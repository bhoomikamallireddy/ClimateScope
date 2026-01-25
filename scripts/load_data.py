import pandas as pd


def load_dataset(csv_path):
    """
    PHASE 2: DATA INGESTION (RAW → MEMORY)
    - Load CSV into memory
    - Parse date column
    - Print basic dataset information
    """

    # Step 1: Load CSV and parse date column
    df = pd.read_csv(
        csv_path,
        parse_dates=["last_updated"]  # change column name if needed
    )
    df['last_updated'] = pd.to_datetime(df['last_updated']).dt.normalize()
    # Step 2: Basic dataset info
    print("===== DATASET LOADED SUCCESSFULLY =====")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
  


    # Step 3: Date range (only if date column exists)
    if "last_updated" in df.columns:
        print("Date Range:")
        print(f"Start: {df['last_updated'].min()}")
        print(f"End  : {df['last_updated'].max()}")

    # Step 4: Memory usage
    memory_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
    print(f"Memory Usage: {memory_mb:.2f} MB")

    return df


if __name__ == "__main__":
    DATA_PATH = "../data/GlobalWeatherRepository.csv"
    df = load_dataset(DATA_PATH)
