import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# 1. Configuration & Paths
# =========================================================
INPUT_PATH = Path("../data/processed/cleaned_weather.csv")
OUTPUT_DIR = Path("../data/analytical")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DAILY_OUTPUT = OUTPUT_DIR / "daily_weather_final.csv"
MONTHLY_OUTPUT = OUTPUT_DIR / "monthly_trends.csv"

REQUIRED_COLUMNS = ["date", "country", "temperature_celsius", "humidity", "precip_mm", "wind_kph"]

# =========================================================
# 2. Logic & Domain Helpers
# =========================================================
def validate_schema(df: pd.DataFrame):
    """Ensure data quality before processing."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"CRITICAL: Missing columns {missing}")

def get_season(month: int) -> str:
    """Global seasonal approximation."""
    if month in [12, 1, 2]: return "Winter"
    if month in [3, 4, 5]: return "Summer"
    if month in [6, 7, 8]: return "Monsoon"
    return "Post-Monsoon"

def categorize_rain(mm: float) -> str:
    """Classify rainfall intensity based on mm."""
    if mm == 0: return "None"
    if mm < 5: return "Light"
    if mm < 20: return "Moderate"
    return "Heavy/Extreme"

# =========================================================
# 3. Main Feature Engineering Pipeline
# =========================================================
def main():
    print("🚀 Starting Feature Engineering Pipeline...")
    df = pd.read_csv(INPUT_PATH, parse_dates=["date"])
    # --- INTEGRITY CHECK START ---
    presence_matrix = df.pivot_table(
        index='country', 
        columns='date', 
        values='temperature_celsius', 
        aggfunc='mean'
    ).fillna(0)
    
    presence_matrix_binary = (presence_matrix > 0).astype(int)
    daily_counts = presence_matrix_binary.sum(axis=0)
    blackout_dates = daily_counts[daily_counts < (df["country"].nunique() * 0.8)]

    print(f"📊 RECTIFIED DATA INTEGRITY REPORT")
    print(f"Total Unique Dates: {len(presence_matrix.columns)}")
    print(f"Days with significant data loss: {len(blackout_dates)}")
    # --- INTEGRITY CHECK END ---

    # Proceed with Rolling Averages and Monthly Aggregation
    df.sort_values(["country", "date"], inplace=True)
    validate_schema(df)
    df['date'] = df['date'].dt.normalize()
    # A. Temporal Intelligence
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df["season"] = df["month"].apply(get_season)

    # B. Smoothing (Rolling Averages)
    # Sorting is mandatory for rolling calculations to work correctly!
    df.sort_values(["country", "date"], inplace=True)
    df["temp_7d_avg"] = df.groupby("country")["temperature_celsius"].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )

    # C. Monthly Aggregation (Signal Extraction)
    monthly_df = df.groupby(["country", "year", "month", "year_month"], as_index=False).agg(
        avg_temp=("temperature_celsius", "mean"),
        max_temp=("temperature_celsius", "max"),
        total_precip=("precip_mm", "sum"),
        avg_humidity=("humidity", "mean"),
        obs_count=("temperature_celsius", "count")
    )

    # D. Temperature Anomaly (Current Temp vs. Monthly Average)
    df = df.merge(monthly_df[["country", "year_month", "avg_temp"]], on=["country", "year_month"], how="left")
    df["temp_anomaly"] = df["temperature_celsius"] - df["avg_temp"]

    # E. Extreme Event Detection (Percentile-based)
    # A heatwave is defined as the top 5% of temperatures for THAT specific country
    heat_thresh = df.groupby("country")["temperature_celsius"].quantile(0.95).to_dict()
    df["is_heatwave"] = df.apply(lambda r: r["temperature_celsius"] > heat_thresh.get(r["country"], 99), axis=1)
    
    df["is_heavy_rain"] = df["precip_mm"] >= 50
    df["is_high_wind"] = df["wind_kph"] >= 40

    # F. Human Comfort Index (Heat + Humidity)
    df["comfort_index"] = df["temperature_celsius"] - (0.55 - 0.0055 * df["humidity"]) * (df["temperature_celsius"] - 14.5)

    # G. Save Final Datasets
    df.to_csv(DAILY_OUTPUT, index=False)
    monthly_df.to_csv(MONTHLY_OUTPUT, index=False)
    print(f"✅ SUCCESS: Cleaned and Normalized data saved to {DAILY_OUTPUT}")

if __name__ == "__main__":
    main()