import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DB_PASSWORD = os.getenv("AIS_DB_PASSWORD")
if not DB_PASSWORD:
    raise RuntimeError("Missing database credentials.")

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": DB_PASSWORD,
    "host": "localhost",
    "port": 5432,
}
