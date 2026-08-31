# Architecture

## Runtime paths

```text
Live host traffic
  -> Scapy packet capture
  -> 19 live packet/flow features
  -> NumPy scaler + autoencoder
  -> anomaly score and threshold
  -> heuristic alert label and calibrated severity
  -> SQLite + WebSocket
  -> React SOC dashboard

Held-out Edge-IIoT test record
  -> exact 60 named dataset features
  -> saved sklearn binary or attack-type pipeline
  -> prediction API
  -> supervised-model verification panel
```

## Services

- `python-backend/main.py`: FastAPI endpoints, lifecycle, WebSocket fan-out, and model loading.
- `python-backend/ml_engine.py`: lightweight live anomaly engine.
- `python-backend/edge_iiot_model.py`: validates and runs the 60-feature binary Edge-IIoT pipeline.
- `python-backend/edge_iiot_attack_type_model.py`: validates and runs the 15-class Edge-IIoT pipeline.
- `python-backend/kitsune_model.py`: validates and runs the 116-feature Kitsune classifier.
- `python-backend/database.py`: SQLite persistence for alert records and training state.
- `frontend`: React/Vite SOC dashboard and supervised demonstration controls.

## Boundary that must be preserved

Scapy's current live feature set is not schema-compatible with the supervised training datasets. The project must not label a live alert as a Kitsune or Edge-IIoT model prediction until a compatible live feature extractor is added and validated.
