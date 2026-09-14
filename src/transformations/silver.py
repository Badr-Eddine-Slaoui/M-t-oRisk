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

def weather_quality_check(df: pd.DataFrame) -> None:
    
    print("Vérification de la qualité des données météorologiques...")
    
    invalid_precipitation = (df["precipitation_sum"] < 0).sum()
    
    print(f"Nombre de précipitations invalides : {invalid_precipitation}")
    
    invalid_probability = ((df["precipitation_probability_max"] < 0) | (df["precipitation_probability_max"] > 100)).sum()
    
    print(f"Nombre de probabilités invalides : {invalid_probability}")
    
    invalid_windspeed = (df["windspeed_10m_max"] < 0).sum()
    
    print(f"Nombre de vitesses de vent invalides : {invalid_windspeed}")
    
    invalid_windgusts = (df["windgusts_10m_max"] < 0).sum()
    
    print(f"Nombre de rafales de vent invalides : {invalid_windgusts}")
    
    invalid_weathercode = (~df["weathercode"].isin(range(0, 100))).sum()
    
    print(f"Nombre de codes météo invalides : {invalid_weathercode}")
    
    invalid_temperature = (df["temperature_2m_max"] < df["temperature_2m_min"]).sum()
    
    print(f"Nombre de temperatures invalides : {invalid_temperature}")
    
    valid_data = df[
        (
            (df["precipitation_sum"] >= 0) &
            (df["precipitation_probability_max"] >= 0) &
            (df["precipitation_probability_max"] <= 100) &
            (df["windspeed_10m_max"] >= 0) &
            (df["windgusts_10m_max"] >= 0) &
            (df["weathercode"].isin(range(0, 100))) &
            (df["temperature_2m_max"] >= df["temperature_2m_min"])
        )
    ]
    
    print(f"Nombre de données valides : {len(valid_data)}")
    
    print("Vérification terminée.")
    
    return valid_data

def transform_cities_data_types(df: pd.DataFrame) -> pd.DataFrame:
    df["lat"] = pd.to_numeric(df["lat"], downcast="float", errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], downcast="float", errors="coerce")
    return df

def join_cities_weather(cities_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(weather_df, cities_df, on="city", how="left", validate="m:1")

def validate_joined_data(df: pd.DataFrame) -> pd.DataFrame:
    missing_data = (df["lat"].isna() | df["lng"].isna()).sum()
    print(f"Nombre de données manquantes : {missing_data}")
    
    if missing_data > 0:
        print("Données manquantes détectées.")
        df = df.dropna(subset=["lat", "lng"])
        
    return df

def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    desired_order = ["city", "lat", "lng", "date", "temperature_2m_max", "temperature_2m_min",
                    "precipitation_sum", "precipitation_probability_max", "windspeed_10m_max",
                    "windgusts_10m_max", "weathercode"]
    
    return df[desired_order]
