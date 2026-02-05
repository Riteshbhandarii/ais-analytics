import json
import time
import uuid
import psycopg2
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

from config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# testing
def save_vessel(mmsi, data):
    cur.execute(
        """
        INSERT INTO vessels (mmsi, name, imo, callsign, vessel_type)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (mmsi) DO UPDATE SET
            name = EXCLUDED.name,
            imo = EXCLUDED.imo,
            callsign = EXCLUDED.callsign,
            vessel_type = EXCLUDED.vessel_type,
            updated_at = NOW()
        """,
        (
            mmsi,
            data.get("name"),
            data.get("imo"),
            data.get("callSign"),
            data.get("type")
        )
    )
    conn.commit()

def save_ais_message(mmsi, data):
    ais_time = datetime.fromtimestamp(data["time"], tz=timezone.utc)

    cur.execute(
        """
        INSERT INTO ais_messages
        (ais_time, mmsi, latitude, longitude, sog, cog, heading, nav_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            ais_time,
            mmsi,
            data["lat"],
            data["lon"],
            data.get("sog"),
            data.get("cog"),
            data.get("heading"),
            data.get("navStat")
        )
    )
    conn.commit()
 
def process_location(topic, data):
    try:
        mmsi = int(topic.split("/")[1])
    except Exception:
        return

    if not all(k in data for k in ("lat", "lon", "time")):
        return

    if not (-90 <= data["lat"] <= 90 and -180 <= data["lon"] <= 180):
        return

    ensure_vessel_exists(mmsi)
    save_ais_message(mmsi, data)

    print(f"AIS saved for MMSI {mmsi}")

def process_metadata(topic, data):
    try:
        mmsi = int(topic.split("/")[1])
    except Exception:
        return

    save_vessel(mmsi, data)
    print(f"Metadata saved for MMSI {mmsi}")

def ensure_vessel_exists(mmsi):
    cur.execute(
        """
        INSERT INTO vessels (mmsi)
        VALUES (%s)
        ON CONFLICT (mmsi) DO NOTHING
        """,
        (mmsi,)
    )

conn.autocommit = True




def on_connect(client, userdata, flags, reasonCode, properties):
    print("Connected to Digitraffic MQTT")
    client.subscribe("vessels-v2/+/location")
    client.subscribe("vessels-v2/+/metadata")
    print("Subscribed to location and metadata topics")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))

        if msg.topic.endswith("/location"):
            process_location(msg.topic, data)
        elif msg.topic.endswith("/metadata"):
            process_metadata(msg.topic, data)

    except Exception as e:
        print("Message error:", e)

client = mqtt.Client(
    client_id=f"ais-{uuid.uuid4()}",
    transport="websockets",
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

client.tls_set()
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to Digitraffic MQTT...")
client.connect("meri.digitraffic.fi", 443)
client.loop_forever()
