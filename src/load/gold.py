import pandas as pd
from pathlib import Path
from datetime import datetime
from src.db.models import City, WeatherForecast, WeatherRisk
from src.db.connection import engine
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[2]
current_date = datetime.now().strftime("%Y-%m-%d")

SILVER_FILE = (
    PROJECT_ROOT / "data" / "silver" / f"weather_data_cleaned_{current_date}.csv"
)


def load_silver_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def prepare_cities_data(df: pd.DataFrame) -> pd.DataFrame:
    cities_df = df[["city", "lat", "lng"]].drop_duplicates(subset=["city"])
    cities_df = cities_df.rename(columns={"city": "name", "lat": "latitude", "lng": "longitude"})
    return cities_df
