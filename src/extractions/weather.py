import dotenv
import os
from datetime import datetime
from pathlib import Path
from itertools import zip_longest

import pandas as pd
import requests

from .cities import extract_cities_from_csv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

dotenv.load_dotenv(PROJECT_ROOT / ".env")

BASE_URL = os.getenv("OPEN_METEO_BASE_URL")

def get_city_weather_data(
    city: str,
    latitude: float,
    longitude: float,
) -> dict:

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "windspeed_10m_max",
            "windgusts_10m_max",
            "weathercode",
        ],
        "timezone": "auto",
        "forecast_days": 7,
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        if "daily" not in data:
            print(f"Réponse invalide pour {city}")
            return {}

        print(
            f"Données météorologiques extraites pour "
            f"{city} (lat: {latitude}, lng: {longitude})"
        )

        return data

    except requests.exceptions.HTTPError as e:
        print(f"Erreur HTTP pour {city}: {e}")

    except requests.exceptions.ConnectionError as e:
        print(f"Erreur de connexion pour {city}: {e}")

    except requests.exceptions.Timeout as e:
        print(f"Timeout pour {city}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête pour {city}: {e}")

    except ValueError as e:
        print(f"JSON invalide pour {city}: {e}")

    return {}


def add_weather_data_to_contents(
    contents: dict,
    city: str,
    weather_data: dict,
) -> None:

    daily_data = weather_data.get("daily", {})

    time = daily_data.get("time", [])

    temperature_2m_max = daily_data.get("temperature_2m_max", [])
    temperature_2m_min = daily_data.get("temperature_2m_min", [])

    precipitation_sum = daily_data.get("precipitation_sum", [])

    precipitation_probability_max = daily_data.get(
        "precipitation_probability_max",
        [],
    )

    windspeed_10m_max = daily_data.get(
        "windspeed_10m_max",
        [],
    )

    windgusts_10m_max = daily_data.get(
        "windgusts_10m_max",
        [],
    )

    weathercode = daily_data.get("weathercode", [])

    for i, date in enumerate(zip_longest(time, temperature_2m_max, temperature_2m_min, precipitation_sum, precipitation_probability_max, windspeed_10m_max, windgusts_10m_max, weathercode, fillvalue=None)):

        contents["city"].append(city)
        contents["time"].append(time[i])

        contents["temperature_2m_max"].append(
            temperature_2m_max[i]
        )

        contents["temperature_2m_min"].append(
            temperature_2m_min[i]
        )

        contents["precipitation_sum"].append(
            precipitation_sum[i]
        )

        contents["precipitation_probability_max"].append(
            precipitation_probability_max[i]
        )

        contents["windspeed_10m_max"].append(
            windspeed_10m_max[i]
        )

        contents["windgusts_10m_max"].append(
            windgusts_10m_max[i]
        )

        contents["weathercode"].append(
            weathercode[i]
        )

