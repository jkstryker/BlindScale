import asyncio
from bleak import BleakClient

ADDR = "FF:03:00:70:5F:80"

AE_WRITE  = "0000ae01-0000-1000-8000-00805f9b34fb"
AE_NOTIFY = "0000ae02-0000-1000-8000-00805f9b34fb"

FFF_WRITE  = "0000fff2-0000-1000-8000-00805f9b34fb"
FFF_NOTIFY = "0000fff1-0000-1000-8000-00805f9b34fb"

INIT = bytes.fromhex("13 09 ff 02 10 b4 24 00 05")

def decode_weight(data: bytes):
    # Candidate frame: 21 04 <lo> <hi> <status>
    if len(data) >= 5 and data[0] == 0x21 and data[1] == 0x04:
        raw = int.from_bytes(data[2:4], "little")
        kg = raw / 10.0
        lb = kg * 2.2046226218
        return kg, lb, raw
    return None

async def main():
    async with BleakClient(ADDR) as client:
        print("Connected:", client.is_connected)

        def make_cb(tag):
            def cb(_, data: bytearray):
                d = bytes(data)
                w = decode_weight(d)
                if w:
                    kg, lb, raw = w
                    print(f"[{tag}] Weight {kg:.1f} kg ({lb:.1f} lb) raw={raw} payload={d.hex()}")
                else:
                    print(f"[{tag}] {d.hex()}")
            return cb

        # Subscribe to both
        print("Subscribing AE02 + FFF1...")
        await client.start_notify(AE_NOTIFY, make_cb("AE02"))
        await client.start_notify(FFF_NOTIFY, make_cb("FFF1"))

        # Try init on AE01 first
        print("Writing INIT to AE01...")
        await client.write_gatt_char(AE_WRITE, INIT, response=False)

        # Also try init on FFF2 (some firmwares use this instead)
        print("Writing INIT to FFF2...")
        await client.write_gatt_char(FFF_WRITE, INIT, response=False)

        print("Step on the scale now. Listening for 60s...")
        await asyncio.sleep(60)

        await client.stop_notify(AE_NOTIFY)
        await client.stop_notify(FFF_NOTIFY)

if __name__ == "__main__":
    asyncio.run(main())
