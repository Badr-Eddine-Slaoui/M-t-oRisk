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
│   ├── __init__.py
│   └── main.py             # weather_data_pipeline DAG (extract >> transform >> load)
├── uml/
│   └── ClassDiagram.puml   # PlantUML class diagram
├── Dockerfile              # Python / Streamlit image
├── Dockerfile.airflow      # Airflow image
├── docker-compose.yml      # Full stack (Postgres x2, pgAdmin, Python, Streamlit, Airflow)
├── requirements.txt
└── .env.example            # Copy to .env and fill in credentials
```

---

## Pipeline Orchestration (Airflow)

The pipeline is orchestrated with Apache Airflow via the `weather_data_pipeline` DAG (`dags/main.py`), running on a `@daily` schedule:

```
[extract] ──► [transform] ──► [load]
```

- **`extract` task**: Ingests 7-day meteorological forecasts from Open-Meteo for all configured Moroccan cities and stores raw data in `data/bronze/`.
- **`transform` task**: Cleans values, performs quality checks, and calculates weighted delivery disruption scores, saving output in `data/silver/`.
- **`load` task**: Upserts dimensional cities, forecast metrics, and calculated risk levels into the PostgreSQL Gold layer.

### Triggering the Pipeline

- **Via Airflow Web UI**: Navigate to [http://localhost:8080](http://localhost:8080), unpause `weather_data_pipeline`, and click **Trigger DAG**.
- **Via Docker CLI**:
  ```bash
  docker exec -it weather-airflow airflow dags trigger weather_data_pipeline
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

### 3. Initialize the database schema

```bash
docker exec -it weather-python python -m src.db.migrate
```

### 4. Trigger the pipeline

Run via Airflow (recommended):
```bash
docker exec -it weather-airflow airflow dags trigger weather_data_pipeline
```

Or run standalone inside the python container:
```bash
docker exec -it weather-python bash -c "python -m src.extractions.weather && python -m src.transformations.silver && python -m src.load.gold"
```

### 5. Access Dashboards & Tools

- **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)
- **Airflow UI**: [http://localhost:8080](http://localhost:8080)
- **pgAdmin**: [http://localhost:5050](http://localhost:5050)

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
