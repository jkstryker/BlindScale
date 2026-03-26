import asyncio
from bleak import BleakClient

ADDR = "FF:03:00:70:5F:80"

WRITE_UUID  = "0000fff2-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"

INIT_COMMAND = bytes.fromhex("13 09 ff 02 10 b4 24 00 05")

last_weight = None

def decode_weight(data: bytes):
    if len(data) == 11 and data[0] == 0x10 and data[1] == 0x0B and data[2] == 0xFF:
        raw = int.from_bytes(data[3:5], "big")
        kg = raw / 100.0
        lb = kg * 2.2046226218
        status = data[5]
        return kg, lb, raw, status
    return None

async def main():
    global last_weight

    print(f"Connecting to {ADDR} ...")
    async with BleakClient(ADDR) as client:
        print("Connected:", client.is_connected)

        def on_notify(_, data: bytearray):
            global last_weight
            payload = bytes(data)
            decoded = decode_weight(payload)

            if decoded:
                kg, lb, raw, status = decoded

                if status == 0x01 and kg != last_weight:
                    last_weight = kg
                    print(f"Stable Weight: {kg:.2f} kg ({lb:.1f} lb)")

        print("Starting notify on FFF1...")
        await client.start_notify(NOTIFY_UUID, on_notify)

        print("Sending init command to FFF2...")
        await client.write_gatt_char(WRITE_UUID, INIT_COMMAND, response=False)

        print("Ready. Step on the scale. (Ctrl+C to stop)")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    asyncio.run(main())
