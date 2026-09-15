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

