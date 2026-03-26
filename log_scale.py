import asyncio
import sqlite3
import time
import uuid
from datetime import datetime

from bleak import BleakClient

ADDR = "FF:03:00:70:5F:80"

WRITE_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"

INIT_COMMAND = bytes.fromhex("13 09 ff 02 10 b4 24 00 05")
DB_FILE = "weights.db"

last_stable_time = None
logged_this_session = False
current_session = None


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weigh_ins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weight_kg REAL NOT NULL,
            weight_lb REAL NOT NULL,
            raw_value INTEGER NOT NULL,
            status INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            session_id TEXT,
            is_final INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def save_weight(kg, lb, raw, status, session_id, is_final):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO weigh_ins (
            weight_kg,
            weight_lb,
            raw_value,
            status,
            recorded_at,
            session_id,
            is_final
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        kg,
        lb,
        raw,
        status,
        datetime.now().isoformat(),
        session_id,
        is_final
    ))
    conn.commit()
    conn.close()


def decode_weight(data: bytes):
    if len(data) == 11 and data[0] == 0x10 and data[1] == 0x0B and data[2] == 0xFF:
        raw = int.from_bytes(data[3:5], "big")
        kg = raw / 100.0
        lb = kg * 2.2046226218
        status = data[5]
        return kg, lb, raw, status
    return None


async def main():
    global last_stable_time
    global logged_this_session
    global current_session

    init_db()

    print(f"Connecting to {ADDR} ...")

    async with BleakClient(ADDR) as client:
        print("Connected:", client.is_connected)

        def on_notify(_, data: bytearray):
            global last_stable_time
            global logged_this_session
            global current_session

            payload = bytes(data)
            decoded = decode_weight(payload)

            if not decoded:
                return

            kg, lb, raw, status = decoded

            # Treat status 0x01 as a stable reading
            if status == 0x01:
                if current_session is None:
                    current_session = str(uuid.uuid4())

                if last_stable_time is None:
                    last_stable_time = time.time()

                # Only log once after the reading has stayed stable for 2 seconds
                if time.time() - last_stable_time > 2 and not logged_this_session:
                    save_weight(kg, lb, raw, status, current_session, 1)
                    logged_this_session = True
                    print(f"Logged FINAL: {kg:.2f} kg ({lb:.1f} lb)")
            else:
                # Reset when the measurement is no longer stable
                last_stable_time = None
                logged_this_session = False
                current_session = None

        print("Starting notify on FFF1...")
        await client.start_notify(NOTIFY_UUID, on_notify)

        print("Sending init command to FFF2...")
        await client.write_gatt_char(WRITE_UUID, INIT_COMMAND, response=False)

        print("Ready. Step on the scale. Press Ctrl+C to stop.")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")


if __name__ == "__main__":
    asyncio.run(main())
