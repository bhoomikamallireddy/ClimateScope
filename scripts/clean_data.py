import pandas as pd
import os
# -------------------------------
# CONFIG
# -------------------------------
RAW_DATA_PATH = "../data/GlobalWeatherRepository.csv"
OUTPUT_PATH = "../data/processed/cleaned_weather.csv"

MANDATORY_COLUMNS = [
    "date",
    "country",
    "temperature_celsius",
    "humidity",
    "precip_mm",
    "wind_kph"
]

# -------------------------------
# LOAD DATA
# -------------------------------
print("Loading raw dataset...")
df = pd.read_csv(RAW_DATA_PATH)
df['last_updated'] = pd.to_datetime(df['last_updated']).dt.normalize()


print(f"Initial shape: {df.shape}")

# -------------------------------
# STANDARDIZE COLUMN NAMES
# -------------------------------
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Rename known variants → standard names
COLUMN_MAP = {
    "last_updated": "date",
    "datetime": "date",
    "temp_c": "temperature_celsius",
    "temperature": "temperature_celsius",
    "wind_speed_kph": "wind_kph",
    "wind": "wind_kph",
    "precipitation_mm": "precip_mm"
}

df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns}, inplace=True)
df.rename(columns=COLUMN_MAP, inplace=True)

# 4. Handle multiple entries per day
# Since we normalized, we might have multiple rows for (country, date)
# We aggregate them to get one clean row per country per day
df = df.groupby(['country', 'date'], as_index=False).mean(numeric_only=True)

print(f"Shape after daily aggregation: {df.shape}")
# -------------------------------
# CHECK MANDATORY COLUMNS
# -------------------------------
missing_cols = [c for c in MANDATORY_COLUMNS if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing mandatory columns: {missing_cols}")

# -------------------------------
# DATE HANDLING
# -------------------------------
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Drop rows where date is invalid
df = df.dropna(subset=["date"])

# -------------------------------
# NUMERIC CLEANING
# -------------------------------
NUMERIC_COLS = [
    "temperature_celsius",
    "humidity",
    "precip_mm",
    "wind_kph"
]

for col in NUMERIC_COLS:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------------
# REMOVE INVALID WEATHER VALUES
# -------------------------------
df = df[
    (df["humidity"].between(0, 100)) &
    (df["temperature_celsius"].between(-90, 60)) &
    (df["wind_kph"] >= 0) &
    (df["precip_mm"] >= 0)
]

# -------------------------------
# HANDLE MISSING VALUES
# -------------------------------
# Drop rows with missing core metrics
df = df.dropna(subset=NUMERIC_COLS + ["country"])

# -------------------------------
# COUNTRY STANDARDIZATION
# -------------------------------
df["country"] = (
    df["country"]
    .astype(str)
    .str.strip()
    .str.title()
)

# -------------------------------
# FINAL VALIDATION
# -------------------------------
assert df[NUMERIC_COLS].isna().sum().sum() == 0, "NaNs still exist in numeric columns"
assert df["date"].dtype == "datetime64[ns]", "Date column is not datetime"

print("Final shape after cleaning:", df.shape)

# -------------------------------
# SAVE CLEAN DATA
# -------------------------------
os.makedirs("data/processed", exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Cleaned dataset saved to: {OUTPUT_PATH}")
print("PHASE 3 COMPLETED SUCCESSFULLY")
