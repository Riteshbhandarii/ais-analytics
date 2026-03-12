# AIS Analytics

AIS Analytics is a data engineering project for collecting live AIS vessel data from Digitraffic's Marine Traffic MQTT feed and storing it in PostgreSQL for later analysis, visualization, and trajectory prediction.

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


Tables:

- `vessels`: one row per vessel, storing static or slowly changing metadata such as MMSI, vessel name, IMO, callsign, and vessel type
- `ais_messages`: historical AIS movement data with timestamp, vessel MMSI, latitude, longitude, speed over ground, course over ground, heading, and navigation status

## Requirements

- Python 3.12 or compatible Python 3 version
- PostgreSQL running locally on `localhost:5432`
- a PostgreSQL database named `postgres`
- a PostgreSQL user named `postgres`
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

If PostgreSQL is installed with Homebrew and version 14 is in use:

```bash
brew services start postgresql@14
```

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

## Notes

- Internet is required for receiving live AIS data from Digitraffic.
- Internet is not required for writing to the local PostgreSQL database itself.


