# MétéoRisk 🌩️

A weather-risk ETL pipeline and analytics dashboard that ingests 7-day meteorological forecasts for Moroccan cities, scores them by delivery-disruption risk, and visualises the results in an interactive Streamlit dashboard.

---

## Architecture

```
Open-Meteo API
      │
      ▼
[Bronze Layer] ──► CSV  (raw API response)
      │
      ▼
[Silver Layer] ──► CSV  (cleaned, categorised, risk-scored)
      │
      ▼
[Gold Layer]   ──► PostgreSQL  (cities · weather_forecasts · weather_risks)
      │
      ▼
[Dashboard]    ──► Streamlit + Plotly
```

Orchestration is handled by **Apache Airflow** running inside Docker.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 17 |
| Transformation | Pandas 3 |
| Dashboard | Streamlit + Plotly |
| Orchestration | Apache Airflow 3 |
| Containerisation | Docker / docker-compose |
| Weather API | Open-Meteo (free, no key required) |

---

## Project Structure

```
MétéoRisk/
├── data/
│   ├── cities.csv          # Seed list of Moroccan cities with coordinates
│   ├── bronze/             # Raw weather CSVs (one per run date)
│   └── silver/             # Cleaned & enriched CSVs (one per run date)
├── src/
│   ├── db/
│   │   ├── config.py       # DB URL from env vars
│   │   ├── connection.py   # SQLAlchemy engine
│   │   ├── models.py       # ORM models: City, WeatherForecast, WeatherRisk
│   │   ├── migrate.py      # Create all tables
│   │   └── rollback.py     # Drop all tables
│   ├── extractions/
│   │   ├── cities.py       # Load city list from CSV
│   │   └── weather.py      # Fetch 7-day forecast from Open-Meteo
│   ├── transformations/
│   │   └── silver.py       # Clean, QA, categorise, risk-score
│   ├── load/
│   │   └── gold.py         # Upsert into PostgreSQL
│   └── sql/
│       └── analysis.sql    # Ad-hoc analytical queries
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── dags/                   # Airflow DAGs (orchestration)
├── uml/
│   └── ClassDiagram.puml   # PlantUML class diagram
├── Dockerfile              # Python / Streamlit image
├── Dockerfile.airflow      # Airflow image
├── docker-compose.yml      # Full stack (Postgres x2, pgAdmin, Python, Streamlit, Airflow)
├── requirements.txt
└── .env.example            # Copy to .env and fill in credentials
```

---

## Getting Started

### 1. Clone & configure

```bash
git clone <repo-url>
cd MétéoRisk
cp .env.example .env   # edit with your passwords / ports
```

### 2. Start the stack

```bash
docker compose up -d
```

### 3. Run the pipeline manually (inside the python container)

```bash
docker exec -it weather-python bash

# Inside the container:
python -m src.db.migrate                       # create tables
python -m src.extractions.weather              # bronze: fetch API data
python -m src.transformations.silver           # silver: clean & score
python -m src.load.gold                        # gold: load to Postgres
```

### 4. Open the dashboard

Navigate to http://localhost:8501

### 5. Open Airflow

Navigate to http://localhost:8080

---

## Risk Scoring Model

The `weather_risk_score` is a weighted sum of four factor scores (0-100 each):

| Factor | Weight | Inputs |
|--------|--------|--------|
| Temperature | 15% | `temperature_2m_max` |
| Precipitation | 35% | `precipitation_sum` |
| Wind | 30% | `windspeed_10m_max`, `windgusts_10m_max` |
| Weather code | 20% | `weathercode` (WMO standard) |

Risk categories: **Very Low** · **Low** · **Moderate** · **High** · **Extreme**

Delivery impact: **Low Impact** · **Moderate Impact** · **High Impact**

---

## License

MIT
