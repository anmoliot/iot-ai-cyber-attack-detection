# Module Responsibilities

## Network Engineer

- `src/packet_sniffer.py`
- `src/flow_generator.py`
- `src/feature_builder.py`

The network engineer is responsible for producing live feature vectors that match the ML feature schema exactly.

## ML Engineer

- `src/preprocess.py`
- `src/detect.py`
- `models/model.pkl`
- `models/scaler.pkl`
- `models/features.json`

The ML engineer is responsible for training, exporting, and validating the model artifacts.

## Backend / UI Engineer

- `backend/app.py`
- `dashboard/app.py`
- `dashboard/templates/index.html`

The backend/UI engineer is responsible for APIs and visualizing CSV logs.

## Security Response

- `src/response.py`

Firewall blocking must be disabled by default during development and demonstrations.
