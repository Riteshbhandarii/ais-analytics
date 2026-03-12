CREATE TABLE IF NOT EXISTS vessels (
    mmsi BIGINT PRIMARY KEY,
    name TEXT,
    imo BIGINT,
    callsign TEXT,
    vessel_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
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
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ais_messages_mmsi ON ais_messages (mmsi);
CREATE INDEX IF NOT EXISTS idx_ais_messages_ais_time ON ais_messages (ais_time);
