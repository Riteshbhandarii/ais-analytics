# AIS Analytics

## Structure

- `src/ais_analytics/`: application code
- `sql/`: database schema
- `docs/`: project documentation and diagrams

## Run

1. Start PostgreSQL on `localhost:5432`.
2. Create the tables with `psql -U postgres -d postgres -f sql/schema.sql`.
3. Install dependencies with `python3 -m pip install -r requirements.txt`.
4. Start the ingestor with `PYTHONPATH=src python3 -m ais_analytics`.


