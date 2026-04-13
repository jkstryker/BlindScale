# VeilScale

A privacy-focused smart scale system that captures weight data over Bluetooth and stores it locally without displaying the measurement to the user.

## Overview

VeilScale is a hardware + software system designed to reduce anxiety and bias around weight measurement. Instead of showing weight on a display, the system captures readings from a Bluetooth-enabled scale and stores them securely for later review.

This project demonstrates:
- Bluetooth Low Energy (BLE) reverse engineering
- Embedded data collection using a Raspberry Pi
- Real-time data processing and stabilization
- Local persistence using SQLite
- Foundations for healthcare integration (FHIR)

---

## System Architecture

[Smart Scale] → [BLE] → [Raspberry Pi] → [Python Processing] → [SQLite Database]


---

## Features

- Connects to a GE Bluetooth scale ("Fit Plus")
- Decodes raw BLE packets into weight values
- Detects stabilized readings (prevents noisy data)
- Logs one final weight per weigh-in session
- Stores data with timestamps and session tracking
- Designed for future EMR / FHIR integration

---

## Hardware

- Raspberry Pi Zero 2 W  
- GE Smart Scale (Fit Plus)  
- Optional: OLED display (planned)  

---

## Software Stack

- Python 3.13
- Bleak (BLE communication)
- SQLite (local database)
- Linux (Raspberry Pi OS)

---

## Setup

### 1. Clone the repository
git clone https://github.com/jkstryker/BlindScale.git

cd BlindScale

### 2. Create virtual environment
python3 -m venv scale-env
source scale-env/bin/activate


### 3. Install dependencies


pip install bleak


### 4. Run the application


python log_scale.py


---

## Database Schema

Table: `weigh_ins`

| Column        | Type    | Description |
|--------------|--------|------------|
| id           | INTEGER | Primary key |
| weight_kg    | REAL    | Weight in kilograms |
| weight_lb    | REAL    | Weight in pounds |
| raw_value    | INTEGER | Raw BLE value |
| status       | INTEGER | Stability flag |
| recorded_at  | TEXT    | Timestamp |
| session_id   | TEXT    | Unique weigh-in session |
| is_final     | INTEGER | Final stabilized reading |

---

## Example Output


Logged FINAL: 65.20 kg (143.7 lb)


---

## How It Works

1. Connects to the scale via BLE
2. Subscribes to notification characteristic
3. Receives raw byte payloads
4. Decodes weight from byte stream
5. Waits for stabilization (~2 seconds)
6. Logs a single final reading to SQLite

---

## Future Work

- FHIR integration (send data to EMR systems)
- OLED “blind mode” interface
- Web dashboard for clinicians
- Multi-user support
- Cloud sync

---

## Use Case

VeilScale is designed for:

- Patients who prefer not to see their weight
- Clinical environments reducing bias
- Research settings requiring passive measurement

---

## Security & Privacy

- No data is transmitted externally by default
- All data is stored locally on device
- Designed for controlled sharing (FHIR in future)

---

## License


---

## Author

Jackson Stryker  
