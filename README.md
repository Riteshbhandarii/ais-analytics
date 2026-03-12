# AIS Analytics

## Run

The ingestor script is `ais_ingestor.py`.

1. Start PostgreSQL on `localhost:5432`.
2. Create the tables with `psql -U postgres -d postgres -f schema.sql`.
3. Install dependencies with `python3 -m pip install -r requirements.txt`.
4. Start the ingestor with `python3 ais_ingestor.py`.

Internet is required for the MQTT feed from `meri.digitraffic.fi`. Internet is not required for writes to your local PostgreSQL database itself.
