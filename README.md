# AI Based Cyber Attack Detection

Final-year project scaffold for an IoT network intrusion detection system.

The system captures IoT network traffic, converts packets into flow features, aligns those features with the trained ML model schema, runs inference, records alerts in a standard CSV file, and optionally prepares firewall response actions.

## Pipeline

```text
IoT Devices / Traffic Generator
        |
   Wi-Fi / LAN
        |
Gateway / Sniffer
        |
Packet Capture / Live Sniffing
        |
Flow Generator
        |
Feature Builder
        |
Preprocessing / Scaling
        |
ML Inference
        |
Alert + CSV Logger + Optional Firewall Response
        |
Flask Dashboard
```

## Important Design Rule

The network feature generator must match `models/features.json` exactly.

The ML model expects:

- Same feature names
- Same feature order
- Same numeric encoding
- Same preprocessing behavior used during training

If the live feature vector differs from the training feature vector, prediction quality will be unreliable.

## Folder Structure

```text
AI Based Cyber Attack Detection/
├── README.md
├── requirements.txt
├── .env.example
├── docs/
├── dataset/
├── models/
├── src/
├── backend/
├── dashboard/
├── logs/
└── scripts/
```

## CSV Alert Format

Alerts are stored in `logs/attacks.csv`.

The logger is intentionally standard CSV so it can be opened in Excel, Python, or any report tool.

Columns include:

- timestamp
- src_ip
- dst_ip
- src_port
- dst_port
- protocol
- prediction
- confidence
- cve_id
- cvss_score
- severity
- action
- details

`cve_id` and `cvss_score` may be `N/A` when the model detects a generic anomaly that is not mapped to a known CVE.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Windows, install Npcap before live packet sniffing:

```text
https://npcap.com/
```

## Run Demo Detection

```powershell
python scripts\simulate_traffic.py
```

## Run Dashboard

```powershell
python dashboard\app.py
```

Then open:

```text
http://127.0.0.1:5000
```

