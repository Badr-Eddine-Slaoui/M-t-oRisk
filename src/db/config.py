from dotenv import load_dotenv
import os
load_dotenv()

POSTGRES_DB = str(os.getenv("POSTGRES_DB"))
POSTGRES_USER = str(os.getenv("POSTGRES_USER"))
POSTGRES_PASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
POSTGRES_PORT = str(os.getenv("POSTGRES_PORT"))

DB_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"