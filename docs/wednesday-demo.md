# Wednesday Demonstration Runbook

## Before presenting

1. Start the backend and confirm `GET /health` returns HTTP 200.
2. Start the frontend and open `http://127.0.0.1:5173`.
3. Confirm the model registry reports `READY` for Kitsune RF, Edge-IIoT Binary, and Edge-IIoT Attack Type.
4. Keep the Kaggle output screenshots or the metrics in [evaluation.md](evaluation.md) available as evidence.

## Live-monitoring demo

1. Explain that Scapy is capturing traffic from the host running the backend.
2. Show the connection state, live anomaly engine status, recent alerts, protocol distribution, and persisted history.
3. State precisely: live alerts are autoencoder anomaly signals with heuristic labels. They are not a supervised attack-type result.

## Supervised-model demo

1. Open **Supervised model verification**.
2. Run a binary sample and state whether it is benign or attack.
3. Run an attack-type sample such as `DDoS_HTTP`, `SQL_injection`, or `Ransomware`.
4. State that the sample is a correctly classified held-out Edge-IIoT test record and is submitted to the saved 60-feature models.

## Claims to use

- The system has a working live anomaly-monitoring path and persistent SOC dashboard.
- The project has trained binary and multi-class Edge-IIoT supervised models, with the recorded hold-out metrics.
- The dashboard provides a repeatable supervised inference demonstration using held-out test rows.

## Claims not to use

- Do not say the Edge-IIoT/Kitsune models classify live Scapy packets.
- Do not say the system blocks attackers or updates firewall rules.
- Do not present the random row-level hold-out scores as real-world deployment accuracy.
