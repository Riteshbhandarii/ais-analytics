import json
import uuid
import asyncio
import psycopg2
import paho.mqtt.client as mqtt
from paho.mqtt.client import Client, MQTTMessage
from datetime import datetime, timezone
from typing import Any, Optional

from config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

event_loop: Optional[asyncio.AbstractEventLoop] = None


async def save_vessel(mmsi: int, data: dict) -> None:
    await asyncio.to_thread(
        cur.execute,
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
    await asyncio.to_thread(conn.commit)


async def save_ais_message(mmsi: int, data: dict) -> None:
    ais_time = datetime.fromtimestamp(data["time"], tz=timezone.utc)
    await asyncio.to_thread(
        cur.execute,
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
    await asyncio.to_thread(conn.commit)


async def process_location(topic: str, data: dict) -> None:
    try:
        mmsi = int(topic.split("/")[1])
    except Exception:
        return
    
    if not all(k in data for k in ("lat", "lon", "time")):
        return
    
    if not (-90 <= data["lat"] <= 90 and -180 <= data["lon"] <= 180):
        return
    
    await ensure_vessel_exists(mmsi)
    await save_ais_message(mmsi, data)
    print(f"AIS saved for MMSI {mmsi}")


async def process_metadata(topic: str, data: dict) -> None:
    try:
        mmsi = int(topic.split("/")[1])
    except Exception:
        return
    
    await save_vessel(mmsi, data)
    print(f"Metadata saved for MMSI {mmsi}")


async def ensure_vessel_exists(mmsi: int) -> None:
    await asyncio.to_thread(
        cur.execute,
        """
        INSERT INTO vessels (mmsi)
        VALUES (%s)
        ON CONFLICT (mmsi) DO NOTHING
        """,
        (mmsi,)
    )
    await asyncio.to_thread(conn.commit)


def on_connect(client: Any, userdata: Any, flags: Any, reasonCode: Any, properties: Any) -> None:
    print("Connected to Digitraffic MQTT")
    client.subscribe("vessels-v2/+/location")
    client.subscribe("vessels-v2/+/metadata")
    print("Subscribed to location and metadata topics")


def on_message(client: Client, userdata: Any, msg: MQTTMessage) -> None:
    """Синхронный callback - запускаем async задачу через event loop"""
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        
        # Создаём задачу в event loop
        if msg.topic.endswith("/location"):
            asyncio.run_coroutine_threadsafe(
                process_location(msg.topic, data), 
                event_loop
            )
        elif msg.topic.endswith("/metadata"):
            asyncio.run_coroutine_threadsafe(
                process_metadata(msg.topic, data), 
                event_loop
            )
    except Exception as e:
        print("Message error:", e)


async def mqtt_loop(client: Client) -> None:
    """Запуск MQTT loop в отдельном потоке"""
    loop = asyncio.get_event_loop()
    
    def mqtt_work():
        client.loop_forever()
    
    await loop.run_in_executor(None, mqtt_work)


async def main() -> None:
    global event_loop
    event_loop = asyncio.get_running_loop()
    
    client = mqtt.Client(  # type: ignore[call-arg]
        client_id=f"ais-{uuid.uuid4()}",
        transport="websockets",
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2  # type: ignore[attr-defined]
    )
    
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    
    print("Connecting to Digitraffic MQTT...")
    client.connect("meri.digitraffic.fi", 443)
    
    try:
        await mqtt_loop(client)
    except KeyboardInterrupt:
        print("\nShutting down...")
        client.disconnect()
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(main())
