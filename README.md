# IoT AI Cyber Attack Detection & Monitoring

This project is a **Real-Time IoT Network Intrusion Detection System (IDS)** with a machine-learning-powered backend and a React-based Security Operations Center (SOC) dashboard.

**This document serves as a comprehensive context guide for both human developers and AI coding agents.**

---

## 1. System Architecture

The project is strictly divided into two distinct services:

### Backend: Python / FastAPI (`/python-backend`)
- **Framework**: `FastAPI` (for REST and WebSockets), `uvicorn` (server).
- **Network Sniffing**: Uses `scapy` running in a background thread to intercept live network packets on the host machine.
- **Machine Learning Engine (`ml_engine.py`)**:
  - An unsupervised **Autoencoder** built entirely from scratch using `numpy` (no PyTorch/TensorFlow dependencies).
  - Extracts 9 numerical features from packets (e.g., protocol type, payload length, TCP flags).
  - **Grace Period**: Starts in an `UNTRAINED` state. It buffers `min_train_samples` (default: 500) packets before training itself (`TRAINING`) and setting an anomaly threshold (97th percentile of reconstruction errors).
  - **Inference**: Once `READY`, every new packet is scored. If the reconstruction error exceeds the threshold, it triggers an anomaly alert.
- **API & WebSockets (`main.py`)**:
  - `GET /api/status`: Returns ML engine state and uptime.
  - `GET /api/alerts/recent`: Returns the last 200 alerts stored in memory.
  - `WS /ws/alerts`: A raw WebSocket endpoint that broadcasts alerts to clients the moment the ML engine detects them.

### Frontend: React / Vite (`/frontend`)
- **Framework**: React 18, Vite, TypeScript.
- **Design System**: Premium SOC aesthetic, strict dark mode (`#0a0e14` base), glassmorphism. UI tokens are centrally defined in `src/tokens.css`.
- **State & Real-Time Binding**:
  - Uses a custom hook `useAlertStream.ts` to manage the WebSocket connection with exponential backoff for resilience.
  - Uses `api.ts` for standard REST calls.
- **Components**:
  - `DashboardShell.tsx`: The main layout wrapper.
  - `StatusPanel.tsx`: Displays live engine metrics.
  - `AnomalyTrendChart.tsx`: Uses `recharts` to plot the last 50 anomaly scores against the dynamic threshold.
  - `AlertFeed.tsx`: An animated table displaying real-time attacks.

*Note: There is an old `/backend` directory containing Java/Spring Boot scaffolding. This is legacy/deprecated and should be ignored.*

---

## 2. Running the Application Locally

To start the environment, you must run both servers:

**Start Backend**:
```bash
cd python-backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

**Start Frontend**:
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173`. The basic auth lock screen password is `admin123`.

---

## 3. Future Roadmap (For Agents)

If you are an agent tasked with improving this repository, refer to this prioritized roadmap of planned improvements:

1. **Model Persistence**: Update `ml_engine.py` to save the trained Autoencoder weights (`W1`, `b1`, `W2`, `b2`, `threshold`) to disk (e.g., `model.npz`). Load them on startup to avoid retraining on every boot.
2. **Database Integration**: Remove the in-memory `recent_alerts` list in `main.py`. Integrate `SQLAlchemy` with SQLite/PostgreSQL to persist alerts securely, enabling historical querying.
3. **Advanced Analytics**: Add endpoints to aggregate alerts by Protocol (TCP/UDP/ICMP) or Source IP. Update the React frontend to display these as Pie Charts or Bar Charts.
4. **JWT Authentication**: Replace the hardcoded `admin123` lock screen with a real JWT authentication flow via FastAPI. Protect the WebSocket connection.
5. **Dockerization**: Create a `Dockerfile` for the backend, a `Dockerfile` for the frontend, and a `docker-compose.yml` to spin up the entire stack seamlessly.

## 4. Agent Context Constraints
- Do not add React/Vite build steps to the Python backend; keep the two repositories decoupled.
- When styling the frontend, avoid Tailwind classes unless explicitly requested; stick to the vanilla CSS variables defined in `tokens.css`.
- The ML engine must remain lightweight. Do not introduce heavy dependencies like TensorFlow unless absolutely necessary for a new feature.
