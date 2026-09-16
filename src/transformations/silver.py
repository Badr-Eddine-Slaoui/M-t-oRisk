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

def categorize_temperature(row: pd.Series) -> str:
    if row["temperature_2m_max"] >= 30:
        return "Hot"
    elif 20 <= row["temperature_2m_max"] < 30:
        return "Warm"
    elif 10 <= row["temperature_2m_max"] < 20:
        return "Mild"
    else:
        return "Cold"

def categorize_precipitation(row: pd.Series) -> str:
    if row["precipitation_sum"] > 30:
        return "Very Heavy Rain"
    elif 10 < row["precipitation_sum"] <= 30:
        return "Heavy Rain"
    elif 2 < row["precipitation_sum"] <= 10:
        return "Moderate Rain"
    elif 0 < row["precipitation_sum"] <= 2:
        return "Light Rain"
    else:
        return "No Rain"

def categorize_wind(row: pd.Series) -> str:
    wind_value = max(row["windspeed_10m_max"], row["windgusts_10m_max"])
    if wind_value >= 80:
        return "Extreme Wind"
    elif 60 <= wind_value < 80:
        return "Very Strong Wind"
    elif 40 <= wind_value < 60:
        return "Strong Wind"
    elif 20 <= wind_value < 40:
        return "Moderate Wind"
    elif 10 <= wind_value < 20:
        return "Light Wind"
    else:
        return "Calm"

def categorieze_weather_code(row: pd.Series) -> str:
    if 95 <= row["weathercode"] <= 99:
        return "Thunderstorm"
    elif 85 <= row["weathercode"] <= 86:
        return "Snow Showers"
    elif 80 <= row["weathercode"] <= 82:
        return "Rain Showers"
    elif 71 <= row["weathercode"] <= 77:
        return "Snow"
    elif 61 <= row["weathercode"] <= 67:
        return "Rain"
    elif 51 <= row["weathercode"] <= 57:
        return "Drizzle"
    elif 45 <= row["weathercode"] <= 48:
        return "Fog"
    elif 1 <= row["weathercode"] <= 3:
        return "Cloudy"
    elif row["weathercode"] == 0:
        return "Clear"
    else:
        return "Unknown"

def categoriez_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    df["temperature_category"] = df.apply(categorize_temperature, axis=1)
    df["precipitation_category"] = df.apply(categorize_precipitation, axis=1)
    df["wind_category"] = df.apply(categorize_wind, axis=1)
    df["weathercode_category"] = df.apply(categorieze_weather_code, axis=1)
    return df

def calculate_temperature_risk(df: pd.Series) -> int:
    if df["temperature_category"] == "Hot":
        return 75
    elif df["temperature_category"] == "Warm":
        return 50
    elif df["temperature_category"] == "Mild":
        return 20
    else:
        return 0

def calculate_precipitation_risk(df: pd.Series) -> int:
    if df["precipitation_category"] == "No Rain":
        return 0
    elif df["precipitation_category"] == "Light Rain":
        return 20
    elif df["precipitation_category"] == "Moderate Rain":
        return 45
    elif df["precipitation_category"] == "Heavy Rain":
        return 75
    else:
        return 100
    
def calculate_wind_risk(df: pd.Series) -> int:
    if df["wind_category"] == "Calm":
        return 0
    elif df["wind_category"] == "Light Wind":
        return 15
    elif df["wind_category"] == "Moderate Wind":
        return 30
    elif df["wind_category"] == "Strong Wind":
        return 60
    elif df["wind_category"] == "Very Strong Wind":
        return 85
    else:
        return 100
    
def calculate_weathercode_risk(df: pd.Series) -> int:
    if df["weathercode_category"] == "Clear":
        return 0
    elif df["weathercode_category"] == "Cloudy":
        return 5
    elif df["weathercode_category"] == "Fog":
        return 30
    elif df["weathercode_category"] == "Drizzle":
        return 25
    elif df["weathercode_category"] == "Rain":
        return 50
    elif df["weathercode_category"] == "Snow":
        return 70
    elif df["weathercode_category"] == "Rain Showers":
        return 55
    elif df["weathercode_category"] == "Snow Showers":
        return 75
    else:
        return 100
    
def calculate_overall_risk(df: pd.DataFrame) -> pd.DataFrame:
    df["weather_risk_score"] = df.apply(
        lambda row: (
            calculate_temperature_risk(row) * 0.15 +
            calculate_precipitation_risk(row) * 0.35 +
            calculate_wind_risk(row) * 0.30 +
            calculate_weathercode_risk(row) * 0.20
        ),
        axis=1
    )
    return df

def categorize_weather_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    df["weather_risk_category"] = df["weather_risk_score"].apply(
        lambda score: (
            "Very Low Risk" if score < 20 else
            "Low Risk" if 20 <= score < 40 else
            "Moderate Risk" if 40 <= score < 60 else
            "High Risk" if 60 <= score < 80 else
            "Extreme Risk"
        )
    )
    return df

def check_is_weekend(df: pd.DataFrame) -> pd.DataFrame:
    df["is_weekend"] = df["date"].dt.dayofweek >= 5
    return df
    
def delivery_impact(row: pd.Series) -> str:
    if row["weather_risk_category"] in ["High Risk", "Extreme Risk"]:
        return "High Impact"
    elif row["weather_risk_category"] == "Moderate Risk":
        return "Moderate Impact"
    else:
        return "Low Impact"
    
def add_delivery_impact(df: pd.DataFrame) -> pd.DataFrame:
    df["delivery_impact"] = df.apply(delivery_impact, axis=1)
    return df

def save_to_csv(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path, index=False)
    print(f"Données sauvegardées dans : {file_path}")

def silver_transformation_pipeline() -> None:
    
    bronze_df = load_bronze_data(BRONZE_FILE)
    
    bronze_df = standardize_column_names(bronze_df)
    
    bronze_df = transform_data_types(bronze_df)
    
    bronze_df = remove_duplicates(bronze_df)
    
    bronze_df = remove_missing_values(bronze_df)
    
    valid_weather_data = weather_quality_check(bronze_df)
    
    cities_df = extract_cities_from_csv()
    
    cities_df = transform_cities_data_types(cities_df)
    
    joined_df = join_cities_weather(cities_df, valid_weather_data)
    
    final_df = validate_joined_data(joined_df)
    
    final_df = reorder_columns(final_df)
    
    final_df = categoriez_weather_data(final_df)
    
    final_df = calculate_overall_risk(final_df)
    
    final_df = categorize_weather_risk_score(final_df)
    
    final_df = check_is_weekend(final_df)
    
    final_df = add_delivery_impact(final_df)
    
    save_to_csv(final_df, SILVER_FILE)
    
    print("Transformation des données terminée.")