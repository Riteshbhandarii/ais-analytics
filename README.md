# AIS Analytics

AIS Analytics is a course project for collecting live AIS vessel data from Digitraffic's Marine Traffic MQTT feed and storing it in PostgreSQL for later analysis, visualization, and trajectory prediction.

## Current Scope

The repository currently contains the ingestion and storage layer of the project:

- connects to Digitraffic Marine Traffic MQTT over secure websockets
- subscribes to live vessel location and metadata topics
- stores vessel metadata in PostgreSQL
- stores historical AIS position messages in PostgreSQL

This is the data collection foundation for the later project stages such as map visualization, prediction, and API access.

## Repository Structure

- `src/ais_analytics/`: Python application code
- `sql/`: SQL schema files
- `docs/`: project documentation and architecture files
- `requirements.txt`: Python dependencies

## Data Model

The database schema is defined in `sql/schema.sql`.

- `vessels`: vessel metadata such as MMSI, name, IMO, callsign, and vessel type
- `ais_messages`: historical AIS movement data such as time, position, speed, course, heading, and navigation status

## Requirements

- Python 3
- PostgreSQL running locally on `localhost:5432`
- internet access for the Digitraffic MQTT feed

## Environment Configuration

Database credentials are loaded from the `AIS_DB_PASSWORD` environment variable. The project supports loading this from a local `.env` file.

Example `.env`:

```env
AIS_DB_PASSWORD=your_database_password
```

## Setup

1. Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Start PostgreSQL.
3. Create the database tables:

```bash
psql -U postgres -d postgres -f sql/schema.sql
```

## Run The Ingestor

Start the live AIS ingestor with:

```bash
PYTHONPATH=src python3 -m ais_analytics
```

When the application is running correctly, it should print messages similar to:

```text
Connecting to Digitraffic MQTT...
Connected to Digitraffic MQTT
Subscribed to location and metadata topics
AIS saved for MMSI ...
Metadata saved for MMSI ...
```
