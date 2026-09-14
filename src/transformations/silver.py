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

def transform_data_types(df: pd.DataFrame) -> pd.DataFrame:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["temperature_2m_max"] = pd.to_numeric(df["temperature_2m_max"], downcast="float", errors="coerce")
    df["temperature_2m_min"] = pd.to_numeric(df["temperature_2m_min"], downcast="float", errors="coerce")
    df["precipitation_sum"] = pd.to_numeric(df["precipitation_sum"], downcast="float", errors="coerce")
    df["precipitation_probability_max"] = pd.to_numeric(df["precipitation_probability_max"], downcast="float", errors="coerce")
    df["windspeed_10m_max"] = pd.to_numeric(df["windspeed_10m_max"], downcast="float", errors="coerce")
    df["windgusts_10m_max"] = pd.to_numeric(df["windgusts_10m_max"], downcast="float", errors="coerce")
    df["weathercode"] = pd.to_numeric(df["weathercode"], downcast="integer", errors="coerce")
    return df

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    
    count = df.duplicated(subset=["city", "date"]).sum()
    
    print(f"Nombre de doublons trouvés : {count}")
    
    if count > 0:
        print("Suppression des doublons...")
        return df.drop_duplicates(subset=["city", "date"], keep="last")
    
    return df

def remove_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    
    count = df[["city", "date"]].isna().sum()
    
    print(f"Nombre de valeurs manquantes trouvées : {count}")
    
    if count.any() > 0:
        print("Suppression des valeurs manquantes...")
        df = df.dropna(subset=["city", "date"])
    
    return df
