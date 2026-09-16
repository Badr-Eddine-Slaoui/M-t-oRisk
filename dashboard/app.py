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

st.set_page_config(
    page_title="MétéoRisk Dashboard",
    page_icon=":cloud:",
    layout="wide",
)

st.title(":cloud: MétéoRisk Dashboard")
st.markdown("""
Bienvenue sur le tableau de bord MétéoRisk ! Ce tableau de bord fournit des informations sur les prévisions météorologiques et les risques associés pour différentes villes. Vous pouvez explorer les données, visualiser les tendances et obtenir des informations sur l'impact potentiel des conditions météorologiques sur les livraisons et les activités. Utilisez les filtres et les graphiques interactifs pour analyser les données selon vos besoins. Profitez de votre exploration des risques météorologiques !
""")

#First row of metrics, KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de villes", get_number_of_cities())
city, max_temp = get_maximum_temperature()
col2.metric("Température maximale", f"{max_temp} °C", f"Ville: {city}")
city, max_risk = get_maximum_precipitation()
col3.metric("Précipitation maximale", f"{max_risk} mm", f"Ville: {city}")
city, max_risk_score = get_maximum_risk_score()
col4.metric("Risque météorologique maximal", f"{max_risk_score}", f"Ville: {city}")

st.markdown("---")

st.subheader("Analyse des prévisions météorologiques et des risques par ville")
temperature_per_city = st.columns(1)
with temperature_per_city[0]:
    date_filter = st.date_input("Date", datetime.date.today(), key="date_filter", width=120)    
    st.markdown("### Température maximale par ville")
    max_temp_df = get_max_temperature_per_city()
    
    max_temp_df = max_temp_df[max_temp_df["date"] == date_filter]
    
    fig_max_temp = px.bar(
        max_temp_df,
        x="city",
        y="max_temperature",
        labels={"city": "Ville", "max_temperature": "Température maximale (°C)"},
        title="Température maximale par ville",
    )
    st.plotly_chart(fig_max_temp, use_container_width=True)
    

st.markdown("---")

precipitation_per_city = st.columns(1)

with precipitation_per_city[0]:
    st.markdown("### Précipitation maximale par ville")
    max_precip_df = get_max_precipitation_per_city()
    fig_max_precip = px.bar(
        max_precip_df,
        x="city",
        y="max_precipitation",
        labels={"city": "Ville", "max_precipitation": "Précipitation maximale (mm)"},
        title="Précipitation maximale par ville",
    )
    st.plotly_chart(fig_max_precip, use_container_width=True)
    

st.markdown("---")
