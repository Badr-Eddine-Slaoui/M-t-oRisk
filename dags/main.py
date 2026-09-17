from datetime import datetime
from airflow.sdk import DAG, task
from src.extractions.weather import bronze_extraction_pipeline
from src.transformations.silver import silver_transformation_pipeline
from src.load.gold import gold_load_pipeline

with DAG(
    dag_id="weather_data_pipeline",
    start_date=datetime.now(),
    schedule="@daily",
    catchup=False,
) as dag:

    @task
    def extract():
        print("Extracting data...")
        bronze_extraction_pipeline()

    @task
    def transform():
        print("Transforming data...")
        silver_transformation_pipeline()

    @task
    def load():
        print("Loading data...")
        gold_load_pipeline()

    extract() >> transform() >> load()