# Architecture

## Components

1. IoT devices or traffic generator produce LAN/Wi-Fi traffic.
2. Gateway node captures packets using Scapy or tcpdump.
3. Flow generator groups packets into network flows.
4. Feature builder converts flows into the exact ML feature vector.
5. Preprocessing applies scaling and encoding compatible with training.
6. Inference engine loads `model.pkl` and predicts traffic class.
7. Alert engine writes alerts to CSV.
8. Response engine can prepare firewall block commands.
9. Dashboard reads CSV logs and displays recent detections.

## Data Flow

```text
Packet -> Flow -> Feature Vector -> Scaler -> Model -> Alert -> CSV/Dashboard
```

## Engineering Notes

- Keep packet capture, feature generation, inference, response, and logging separate.
- Do not hard-code model feature names in packet sniffer code.
- Use `models/features.json` as the single source of truth for live inference feature order.
- Use CSV logging for simple academic review and reproducibility.
