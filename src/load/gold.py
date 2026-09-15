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
    
def insert_or_upsert_cities(cities_df: pd.DataFrame) -> None:
    with Session(engine) as session:
        for _, row in cities_df.iterrows():
            city = session.query(City).filter_by(name=row["name"]).first()
            if city:
                city.latitude = row["latitude"]
                city.longitude = row["longitude"]
            else:
                new_city = City(
                    name=row["name"],
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                )
                session.add(new_city)
        session.commit()
        
def get_cities_ids() -> dict:
    with Session(engine) as session:
        cities = session.query(City).all()
        return {city.name: city.id for city in cities}
    
def prepare_weather_forecasts_data(df: pd.DataFrame, cities_ids: dict) -> pd.DataFrame:
    df["city_id"] = df["city"].map(cities_ids)
    
    weather_forecasts_df = df[[
        "city_id", "date", "temperature_2m_max", "temperature_2m_min",
        "precipitation_sum", "precipitation_probability_max",
        "windspeed_10m_max", "windgusts_10m_max", "weathercode"
    ]]
    
    return weather_forecasts_df
        
        
def insert_or_upsert_weather_forecasts(weather_forecasts_df: pd.DataFrame) -> None:
    with Session(engine) as session:
        for _, row in weather_forecasts_df.iterrows():
            forecast = session.query(WeatherForecast).filter_by(city_id=row["city_id"], date=row["date"]).first()
            if forecast:
                forecast.temperature_2m_max = row["temperature_2m_max"]
                forecast.temperature_2m_min = row["temperature_2m_min"]
                forecast.precipitation_sum = row["precipitation_sum"]
                forecast.precipitation_probability_max = row["precipitation_probability_max"]
                forecast.windspeed_10m_max = row["windspeed_10m_max"]
                forecast.windgusts_10m_max = row["windgusts_10m_max"]
                forecast.weathercode = row["weathercode"]
            else:
                new_forecast = WeatherForecast(
                    city_id=row["city_id"],
                    date=row["date"],
                    temperature_2m_max=row["temperature_2m_max"],
                    temperature_2m_min=row["temperature_2m_min"],
                    precipitation_sum=row["precipitation_sum"],
                    precipitation_probability_max=row["precipitation_probability_max"],
                    windspeed_10m_max=row["windspeed_10m_max"],
                    windgusts_10m_max=row["windgusts_10m_max"],
                    weathercode=row["weathercode"],
                )
                session.add(new_forecast)
        session.commit()

def prepare_weather_risks_data(df: pd.DataFrame, cities_ids: dict) -> pd.DataFrame:
    df["city_id"] = df["city"].map(cities_ids)
    
    weather_risks_df = df[[
        "city_id", "date", "temperature_category", "precipitation_category",
        "wind_category", "weathercode_category", "weather_risk_score",
        "weather_risk_category", "is_weekend", "delivery_impact"
    ]]
    
    return weather_risks_df

def insert_or_upsert_weather_risks(weather_risks_df: pd.DataFrame) -> None:
    with Session(engine) as session:
        for _, row in weather_risks_df.iterrows():
            risk = session.query(WeatherRisk).filter_by(city_id=row["city_id"], date=row["date"]).first()
            if risk:
                risk.temperature_category = row["temperature_category"]
                risk.precipitation_category = row["precipitation_category"]
                risk.wind_speed_category = row["wind_category"]
                risk.weathercode_category = row["weathercode_category"]
                risk.weather_risk_score = row["weather_risk_score"]
                risk.weather_risk_category = row["weather_risk_category"]
                risk.is_weekend = row["is_weekend"]
                risk.delivery_impact = row["delivery_impact"]
            else:
                new_risk = WeatherRisk(
                    city_id=row["city_id"],
                    date=row["date"],
                    temperature_category=row["temperature_category"],
                    precipitation_category=row["precipitation_category"],
                    wind_speed_category=row["wind_category"],
                    weathercode_category=row["weathercode_category"],
                    weather_risk_score=row["weather_risk_score"],
                    weather_risk_category=row["weather_risk_category"],
                    is_weekend=row["is_weekend"],
                    delivery_impact=row["delivery_impact"],
                )
                session.add(new_risk)
        session.commit()

def gold_load_pipeline() -> None:
    print("Loading silver data...")
    silver_df = load_silver_data(SILVER_FILE)
    
    print("Preparing and inserting/upserting cities data...")
    cities_df = prepare_cities_data(silver_df)
    insert_or_upsert_cities(cities_df)
    
    print("Retrieving cities IDs...")
    cities_ids = get_cities_ids()
    
    print("Preparing and inserting/upserting weather forecasts data...")
    weather_forecasts_df = prepare_weather_forecasts_data(silver_df, cities_ids)
    insert_or_upsert_weather_forecasts(weather_forecasts_df)
    
    print("Preparing and inserting/upserting weather risks data...")
    weather_risks_df = prepare_weather_risks_data(silver_df, cities_ids)
    insert_or_upsert_weather_risks(weather_risks_df)
    
    print("Loading gold data completed.")
    
if __name__ == "__main__":
    gold_load_pipeline()