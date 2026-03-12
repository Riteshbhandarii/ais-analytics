ALTER TABLE vessels
    ADD CONSTRAINT vessels_mmsi_positive CHECK (mmsi > 0);

ALTER TABLE ais_messages
    ADD COLUMN source_topic TEXT;

UPDATE ais_messages
SET source_topic = CONCAT('vessels-v2/', mmsi, '/location')
WHERE source_topic IS NULL;

ALTER TABLE ais_messages
    ALTER COLUMN source_topic SET NOT NULL;

ALTER TABLE ais_messages
    ADD CONSTRAINT ais_messages_latitude_range CHECK (latitude BETWEEN -90 AND 90),
    ADD CONSTRAINT ais_messages_longitude_range CHECK (longitude BETWEEN -180 AND 180),
    ADD CONSTRAINT ais_messages_sog_range CHECK (sog IS NULL OR sog >= 0),
    ADD CONSTRAINT ais_messages_cog_range CHECK (cog IS NULL OR cog BETWEEN 0 AND 360),
    ADD CONSTRAINT ais_messages_heading_range CHECK (heading IS NULL OR heading BETWEEN 0 AND 511),
    ADD CONSTRAINT ais_messages_nav_status_range CHECK (nav_status IS NULL OR nav_status BETWEEN 0 AND 15);

DELETE FROM ais_messages a
USING ais_messages b
WHERE a.id < b.id
  AND a.mmsi = b.mmsi
  AND a.ais_time = b.ais_time
  AND a.latitude = b.latitude
  AND a.longitude = b.longitude;

ALTER TABLE ais_messages
    ADD CONSTRAINT ais_messages_dedup UNIQUE (mmsi, ais_time, latitude, longitude);
