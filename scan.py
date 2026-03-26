import asyncio
from bleak import BleakScanner

async def main():
    print("Scanning for BLE devices (10s)...")
    devices = await BleakScanner.discover(timeout=10)

    for d in devices:
        # Some bleak versions expose different fields. Keep it robust.
        name = getattr(d, "name", None)
        addr = getattr(d, "address", None)

        details = getattr(d, "details", None)
        rssi = getattr(d, "rssi", None)

        print(f"{addr}  name={name!r}  rssi={rssi}  details={details}")

asyncio.run(main())

