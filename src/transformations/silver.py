import pandas as pd
from pathlib import Path
from datetime import datetime
from src.extractions.cities import extract_cities_from_csv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
current_date = datetime.now().strftime("%Y-%m-%d")

BRONZE_FILE = PROJECT_ROOT / "data" / "bronze" / f"weather_data_{current_date}.csv"
SILVER_FILE = PROJECT_ROOT / "data" / "silver" / f"weather_data_cleaned_{current_date}.csv"

def load_bronze_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df.rename(columns={"time": "date"}, inplace=True)
    return df
