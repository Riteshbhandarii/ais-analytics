CREATE TABLE IF NOT EXISTS vessels (
    mmsi BIGINT PRIMARY KEY,
    name TEXT,
    imo BIGINT,
    callsign TEXT,
    vessel_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT vessels_mmsi_positive CHECK (mmsi > 0)
);

CREATE TABLE IF NOT EXISTS ais_messages (
    id BIGSERIAL PRIMARY KEY,
    ais_time TIMESTAMPTZ NOT NULL,
    mmsi BIGINT NOT NULL REFERENCES vessels (mmsi),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    sog DOUBLE PRECISION,
    cog DOUBLE PRECISION,
    heading INTEGER,
    nav_status INTEGER,
    source_topic TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ais_messages_latitude_range CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ais_messages_longitude_range CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT ais_messages_sog_range CHECK (sog IS NULL OR sog >= 0),
    CONSTRAINT ais_messages_cog_range CHECK (cog IS NULL OR cog BETWEEN 0 AND 360),
    CONSTRAINT ais_messages_heading_range CHECK (heading IS NULL OR heading BETWEEN 0 AND 511),
    CONSTRAINT ais_messages_nav_status_range CHECK (nav_status IS NULL OR nav_status BETWEEN 0 AND 15),
    CONSTRAINT ais_messages_dedup UNIQUE (mmsi, ais_time, latitude, longitude)
);

CREATE INDEX IF NOT EXISTS idx_ais_messages_mmsi ON ais_messages (mmsi);
CREATE INDEX IF NOT EXISTS idx_ais_messages_ais_time ON ais_messages (ais_time);
