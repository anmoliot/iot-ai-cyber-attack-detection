# IoT AI Cyber Attack Detection & Monitoring

SentinelAI is a local IoT intrusion-detection demonstration with two deliberately separate paths:

- **Live monitoring:** Scapy captures host traffic and a lightweight NumPy autoencoder flags anomalous packets.
- **Supervised validation:** trained Kitsune and Edge-IIoT classifiers accept feature records matching their training schemas. The dashboard includes a repeatable Edge-IIoT held-out-test demo.

## What is implemented

- FastAPI backend, WebSocket alert stream, SQLite alert history, and React SOC dashboard.
- Live Scapy capture with a grace period, autoencoder training, anomaly scoring, and severity classification.
- Persisted supervised artifacts loaded at startup when installed locally:
  - Kitsune Random Forest: 116-feature binary classifier.
  - Edge-IIoT binary classifier: 60-feature benign/attack decision.
  - Edge-IIoT attack-type classifier: 15-class attribution.
- Edge-IIoT dashboard demo using correctly classified records from the held-out Kaggle test split.
- Docker configuration for local deployment; raw packet capture requires the appropriate host privileges.

## Important scope

The supervised models do **not** yet classify raw packets captured by Scapy. They require the exact 60-feature Edge-IIoT or 116-feature Kitsune extraction schemas. Live traffic currently goes through the autoencoder path. A TShark/Kitsune-compatible feature extractor is the next engineering step for live supervised inference.

There is no automated firewall blocking. The application records and displays alerts; response automation remains intentionally out of scope for the current demonstration.

## Evaluation summary

| Model | Dataset/task | Hold-out result |
| --- | --- | --- |
| Edge-IIoT binary | 49,301 rows, 60 features | Accuracy 1.0000, macro F1 1.0000 |
| Edge-IIoT attack type | 15 classes, 60 features | Accuracy 0.9894, macro F1 0.9760 |

These are random row-level hold-out results. Related rows from the same capture can occur in train and test sets, so they demonstrate the training pipeline but are not cross-capture generalisation estimates. See [docs/evaluation.md](docs/evaluation.md).

## Run locally

### Backend

```powershell
cd python-backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The default local password is `admin123`.

## Demonstration flow

1. Open the dashboard and confirm all three persisted supervised models show `READY`.
2. Run the binary and attack-type classifiers in **Supervised model verification**.
3. Explain that the inputs are held-out Edge-IIoT test records, not live Scapy traffic.
4. Use the live monitor, charts, and alert table separately to demonstrate real host packet capture and anomaly detection.

For preparation and speaking points, see [docs/wednesday-demo.md](docs/wednesday-demo.md).
