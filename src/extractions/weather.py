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
