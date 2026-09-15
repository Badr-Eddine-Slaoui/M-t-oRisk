from src.db.connection import engine
import streamlit as st
import pandas as pd
import plotly.express as px
from src.db.models import City, WeatherForecast, WeatherRisk
from sqlalchemy.orm import Session
from sqlalchemy import func, case
import datetime

def get_number_of_cities() -> int:
    with Session(engine) as session:
        result = session.query(func.count(City.id)).scalar()
    return result

def get_maximum_temperature() -> float:
    with Session(engine) as session:
        max_temperature = (
            session.query(
                func.max(WeatherForecast.temperature_2m_max).label("max_temperature"),
            )
            .scalar()
        )
        result = (
            session.query(
                City.name.label("city")
            )
            .join(WeatherForecast, City.id == WeatherForecast.city_id)
            .filter(WeatherForecast.temperature_2m_max == max_temperature)
            .first()
        )   

    return result.city, max_temperature

def get_maximum_precipitation() -> float:
    with Session(engine) as session:
        max_precipitation = (
            session.query(
                func.max(WeatherForecast.precipitation_sum).label("max_precipitation"),
            )
            .scalar()
        )
        
        result = (
            session.query(
                City.name.label("city")
            )
            .join(WeatherForecast, City.id == WeatherForecast.city_id)
            .filter(WeatherForecast.precipitation_sum == max_precipitation)
            .first()
        )
    return result.city, max_precipitation

def get_maximum_risk_score() -> float:
    with Session(engine) as session:
        max_risk_score = (
            session.query(
                func.max(WeatherRisk.weather_risk_score).label("max_risk_score"),
            )
            .scalar()
        )
        
        result = (
            session.query(
                City.name.label("city")
            )
            .join(WeatherRisk, City.id == WeatherRisk.city_id)
            .filter(WeatherRisk.weather_risk_score == max_risk_score)
            .first()
        )
    return result.city, max_risk_score

def get_max_temperature_per_city() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                City.name.label("city"),
                WeatherForecast.date,
                WeatherForecast.temperature_2m_max.label("max_temperature"),
            )
            .join(WeatherForecast)
            .group_by(City.name, WeatherForecast.date, WeatherForecast.temperature_2m_max)
            .order_by(WeatherForecast.temperature_2m_max.desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["city", "date", "max_temperature"])
    
    df["max_temperature"] = pd.to_numeric(
        df["max_temperature"],
        downcast="float",
        errors="coerce"
    ).round(2)
    
    return df

def get_max_precipitation_per_city() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                City.name.label("city"),
                WeatherForecast.precipitation_sum.label("max_precipitation"),
            )
            .join(WeatherForecast)
            .group_by(City.name, WeatherForecast.precipitation_sum)
            .order_by(WeatherForecast.precipitation_sum.desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["city", "max_precipitation"])
    return df

def get_average_risk_per_city() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                City.name.label("city"),
                WeatherRisk.date,
                (WeatherRisk.weather_risk_score).label("average_risk"),
            )
            .join(WeatherRisk)
            .group_by(City.name, WeatherRisk.date, WeatherRisk.weather_risk_score)
            .order_by(WeatherRisk.weather_risk_score.desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["city", "date", "average_risk"])
    
    df["average_risk"] = pd.to_numeric(
        df["average_risk"],
        errors="coerce"
    )
    return df

def get_top_20_weather_risks() -> pd.DataFrame:

    with Session(engine) as session:

        result = (
            session.query(
                City.name.label("city"),
                WeatherRisk.date,
                WeatherRisk.weather_risk_score,
                WeatherRisk.weather_risk_category,
                WeatherRisk.delivery_impact,
            )
            .join(WeatherRisk)
            .order_by(
                WeatherRisk.weather_risk_score.desc()
            )
            .limit(20)
            .all()
        )

    df = pd.DataFrame(
        result,
        columns=[
            "city",
            "date",
            "weather_risk_score",
            "weather_risk_category",
            "delivery_impact",
        ],
    )

    df["weather_risk_score"] = pd.to_numeric(
        df["weather_risk_score"],
        errors="coerce"
    )

    return df

def get_highest_risk_per_city() -> pd.DataFrame:
    with Session(engine) as session:
        subquery = (
            session.query(
                WeatherRisk.city_id,
                func.max(WeatherRisk.weather_risk_score).label("max_risk"),
            )
            .group_by(WeatherRisk.city_id)
            .subquery()
        )

        result = (
            session.query(
                City.name.label("city"),
                WeatherRisk.date,
                WeatherRisk.weather_risk_score,
                WeatherRisk.weather_risk_category,
                WeatherRisk.delivery_impact,
            )
            .join(WeatherRisk)
            .join(
                subquery,
                (WeatherRisk.city_id == subquery.c.city_id)
                & (WeatherRisk.weather_risk_score == subquery.c.max_risk),
            )
            .order_by(WeatherRisk.weather_risk_score.desc())
            .all()
        )

    df = pd.DataFrame(
        result,
        columns=[
            "city",
            "date",
            "weather_risk_score",
            "weather_risk_category",
            "delivery_impact",
        ],
    )
    
    df["weather_risk_score"] = pd.to_numeric(
        df["weather_risk_score"],
        errors="coerce"
    )
    
    return df

def get_weather_risk_category_distribution() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                WeatherRisk.weather_risk_category,
                func.count(WeatherRisk.id).label("number_of_forecasts"),
            )
            .group_by(WeatherRisk.weather_risk_category)
            .order_by(func.count(WeatherRisk.id).desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["weather_risk_category", "number_of_forecasts"])
    return df

def get_weekday_disruptions() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                City.name.label("city"),
                func.count(WeatherRisk.id).label("weekday_disruptions"),
            )
            .join(WeatherRisk)
            .filter(
                WeatherRisk.is_weekend == False,
                WeatherRisk.delivery_impact != "Low Impact",
            )
            .group_by(City.name)
            .order_by(func.count(WeatherRisk.id).desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["city", "weekday_disruptions"])
    return df

def get_affected_forecasts_by_period() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                case(
                    (WeatherRisk.is_weekend.is_(True), "Weekend"), else_="Weekday"
                ).label("period"),
                func.count(WeatherRisk.id).label("affected_forecasts"),
            )
            .filter(WeatherRisk.delivery_impact != "Low Impact")
            .group_by(WeatherRisk.is_weekend)
            .order_by(func.count(WeatherRisk.id).desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["period", "affected_forecasts"])
    return df

def get_average_weekday_risk_per_city() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                City.name.label("city"),
                func.round(func.avg(WeatherRisk.weather_risk_score), 2).label(
                    "average_weekday_risk"
                ),
            )
            .join(WeatherRisk)
            .filter(WeatherRisk.is_weekend == False)
            .group_by(City.name)
            .order_by(func.round(func.avg(WeatherRisk.weather_risk_score), 2).desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["city", "average_weekday_risk"])
    return df

def get_delivery_impact_distribution() -> pd.DataFrame:
    with Session(engine) as session:
        result = (
            session.query(
                WeatherRisk.delivery_impact,
                func.count(WeatherRisk.id).label("number_of_periods"),
            )
            .group_by(WeatherRisk.delivery_impact)
            .order_by(func.count(WeatherRisk.id).desc())
            .all()
        )

    df = pd.DataFrame(result, columns=["delivery_impact", "number_of_periods"])
    return df
