from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CITIES_FILE = PROJECT_ROOT / "data" / "cities.csv"


def extract_cities_from_csv() -> pd.DataFrame:
    return pd.read_csv(CITIES_FILE)