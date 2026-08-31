# Module Responsibilities

## Live monitoring

- `python-backend/main.py`: starts the Scapy capture loop and broadcasts generated alerts.
- `python-backend/ml_engine.py`: learn baseline traffic and score live anomalies.
- `python-backend/attack_classifier.py`: assign an explanatory label after a live anomaly. This is heuristic attribution, not the Edge-IIoT attack-type model.

## Supervised inference

- `python-backend/kitsune_model.py`: 116 ordered Kitsune features.
- `python-backend/edge_iiot_model.py`: 60 named Edge-IIoT features, binary result.
- `python-backend/edge_iiot_attack_type_model.py`: 60 named Edge-IIoT features, 15-class result.
- `python-backend/demo_data/edge_iiot_demo_samples.json`: held-out records used only for a repeatable demonstration.

## User interface and persistence

- `python-backend/database.py`: persistent alerts and training records.
- `frontend/src`: dashboard, charts, alert feed, model registry, and supervised verification controls.

## Out of scope for the current delivery

- Firewall enforcement or automatic packet blocking.
- Live supervised classification without a schema-compatible feature-extraction layer.
- Claims of cross-network or cross-capture generalisation from random row-level validation.
