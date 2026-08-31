"""
main.py  —  SentinelAI Backend
============================================================
FastAPI application that ties together:
  - Live packet sniffing via Scapy (background thread)
  - ML anomaly detection (ml_engine.py)
  - Attack classification (attack_classifier.py)
  - WebSocket real-time alert broadcasting
  - REST API for dashboard analytics
  - SQLite persistence (database.py)
  - Demo simulation mode (simulator.py)

Environment variables:
  DEMO_MODE=true          — Use alert simulator instead of/alongside live sniffing
  DATABASE_URL            — SQLAlchemy URL (default: sqlite:///./sentinel.db)
  CORS_ORIGINS            — Comma-separated allowed origins (default: localhost)
  LOG_LEVEL               — DEBUG / INFO / WARNING (default: INFO)
"""

import asyncio
import json
import os
import threading

# Load .env file if present (must happen before any os.getenv calls)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional
import time
import logging

from collections import Counter
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml_engine import MLEngine, extract_features
from attack_classifier import classify_attack
from database import init_db, SessionLocal, AlertRecord, TrainingRun, db_ping
from edge_iiot_model import EdgeIIoTModel
from edge_iiot_attack_type_model import EdgeIIoTAttackTypeModel
from kitsune_model import KitsuneModel

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s │ %(levelname)-8s │ %(name)-20s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("sentinel.main")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_PATH  = os.path.join(os.path.dirname(__file__), "model.pkl")
KITSUNE_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "models", "kitsune", "kitsune_random_forest.joblib"
)
EDGE_IIOT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "models", "edge_iiot", "edge_iiot_binary_model.joblib"
)
EDGE_IIOT_ATTACK_TYPE_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "models", "edge_iiot", "edge_iiot_attack_type_model.joblib"
)
EDGE_IIOT_DEMO_SAMPLES_PATH = os.path.join(
    os.path.dirname(__file__), "demo_data", "edge_iiot_demo_samples.json"
)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentinel.db")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")

# ---------------------------------------------------------------------------
# Global State
# ---------------------------------------------------------------------------
engine      = MLEngine(min_train_samples=500)
kitsune_model = KitsuneModel(KITSUNE_MODEL_PATH)
edge_iiot_model = EdgeIIoTModel(EDGE_IIOT_MODEL_PATH)
edge_iiot_attack_type_model = EdgeIIoTAttackTypeModel(EDGE_IIOT_ATTACK_TYPE_MODEL_PATH)
sniffer_thread: threading.Thread | None = None
sniffer_stop_event = threading.Event()
capture_lock = threading.Lock()
loop: asyncio.AbstractEventLoop | None = None

START_TIME   = time.time()
MAX_ALERTS   = 500          # in-memory cap (DB holds everything)
recent_alerts: list[dict] = []
alerts_lock  = threading.Lock()

# ---------------------------------------------------------------------------
# WebSocket Manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WS client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WS client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _protocol_name(ip_protocol_num: float) -> str:
    proto = int(ip_protocol_num)
    return {6: "TCP", 17: "UDP", 1: "ICMP"}.get(proto, "OTHER")


def _severity_from_score(score: float, threshold: float) -> str:
    """Rank an anomaly by its distance above the model's own baseline."""
    if threshold <= 0:
        return "critical"

    ratio = score / threshold
    if ratio >= 4.0:
        return "critical"
    if ratio >= 2.0:
        return "high"
    if ratio >= 1.25:
        return "medium"
    return "low"


def _persist_alert(alert: dict) -> None:
    """Write alert to SQLite in a try/except so it never crashes the sniffer."""
    try:
        db = SessionLocal()
        record = AlertRecord(
            id=alert["id"],
            timestamp=alert["timestamp"],
            src_ip=alert["src_ip"],
            dst_ip=alert["dst_ip"],
            protocol=alert["protocol"],
            anomaly_score=alert["anomaly_score"],
            threshold=alert["threshold"],
            severity=alert["severity"],
            attack_type=alert.get("attack_type"),
            attack_label=alert.get("attack_label"),
            attack_confidence=alert.get("attack_confidence"),
        )
        db.add(record)
        db.commit()
    except Exception as e:
        logger.error(f"DB write failed: {e}")
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Packet Processing (Background Thread)
# ---------------------------------------------------------------------------

def process_packet(packet):
    """Called by scapy.sniff() for every live packet."""
    try:
        from scapy.layers.inet import IP
        from scapy.layers.inet6 import IPv6

        src_ip = dst_ip = "Unknown"
        ip_protocol = 0.0

        if IP in packet:
            src_ip      = packet[IP].src
            dst_ip      = packet[IP].dst
            ip_protocol = float(getattr(packet[IP], "proto", 0) or 0)
        elif IPv6 in packet:
            src_ip      = packet[IPv6].src
            dst_ip      = packet[IPv6].dst
            ip_protocol = float(getattr(packet[IPv6], "nh", 0) or 0)

        features = extract_features(packet, engine.flow_tracker)
        status   = engine.get_status()

        if status == "UNTRAINED":
            engine.train_packet(features)
            if engine.get_status() == "TRAINING":
                logger.info("Grace period complete — fitting autoencoder...")
                engine.finalize_training()
                try:
                    engine.save(MODEL_PATH)
                    logger.info(f"Model saved → {MODEL_PATH}")
                except Exception as e:
                    logger.warning(f"Could not save model: {e}")
                logger.info("Model READY — real-time anomaly detection active.")

        elif status == "READY":
            is_anomaly = engine.predict_packet(features)
            if is_anomaly:
                score      = engine.score_packet(features)
                threshold  = engine.get_threshold() or 0.0
                severity   = _severity_from_score(score, threshold)
                clf        = classify_attack(features)

                alert = {
                    "id":                f"live-{time.time():.6f}",
                    "type":              "cyber_attack_alert",
                    "timestamp":         time.time(),
                    "src_ip":            src_ip,
                    "dst_ip":            dst_ip,
                    "protocol":          _protocol_name(ip_protocol),
                    "anomaly_score":     round(score, 4),
                    "threshold":         round(threshold, 4),
                    "severity":          severity,
                    "attack_type":       clf.attack_type,
                    "attack_label":      clf.attack_label,
                    "attack_confidence": round(clf.attack_confidence, 2),
                }

                with alerts_lock:
                    recent_alerts.append(alert)
                    if len(recent_alerts) > MAX_ALERTS:
                        recent_alerts.pop(0)

                _persist_alert(alert)

                if loop and loop.is_running():
                    asyncio.run_coroutine_threadsafe(manager.broadcast(alert), loop)

    except Exception as e:
        logger.debug(f"Packet processing error: {e}")


def start_sniffer():
    """Background thread: capture packets until the operator stops capture."""
    try:
        from scapy.all import sniff
        logger.info("Scapy capture started.")
        # A bounded call lets Stop work even when no packets arrive.
        while not sniffer_stop_event.is_set():
            sniff(prn=process_packet, store=0, timeout=1)
        logger.info("Scapy capture stopped.")
    except Exception as e:
        logger.error(f"Sniffer crashed: {e}")


def _capture_running() -> bool:
    return sniffer_thread is not None and sniffer_thread.is_alive()


def _start_capture() -> bool:
    """Start packet capture once. Returns False when it is already running."""
    global sniffer_thread
    with capture_lock:
        if _capture_running():
            return False
        sniffer_stop_event.clear()
        sniffer_thread = threading.Thread(target=start_sniffer, daemon=True)
        sniffer_thread.start()
        return True


def _stop_capture() -> bool:
    """Signal packet capture to stop. The bounded sniff loop exits within one second."""
    with capture_lock:
        if not _capture_running():
            return False
        sniffer_stop_event.set()
        return True


# ---------------------------------------------------------------------------
# Application Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global sniffer_thread, loop

    loop = asyncio.get_running_loop()

    # Initialise database
    init_db()
    logger.info("Database initialised.")

    if kitsune_model.load():
        logger.info("Loaded Kitsune supervised classifier.")
    else:
        logger.warning(f"Kitsune classifier unavailable: {kitsune_model.load_error}")

    if edge_iiot_model.load():
        logger.info("Loaded Edge-IIoT supervised classifier.")
    else:
        logger.warning(f"Edge-IIoT classifier unavailable: {edge_iiot_model.load_error}")

    if edge_iiot_attack_type_model.load():
        logger.info("Loaded Edge-IIoT attack-type classifier.")
    else:
        logger.warning(f"Edge-IIoT attack-type classifier unavailable: {edge_iiot_attack_type_model.load_error}")

    # Restore persisted model if available
    if os.path.exists(MODEL_PATH):
        try:
            engine.load(MODEL_PATH)
            logger.info(f"Loaded persisted model — status: {engine.get_status()}")
        except Exception as e:
            logger.warning(f"Could not load model ({e}), starting fresh.")

    logger.info("Packet capture is idle. Start it from the dashboard when ready.")

    yield

    # Shutdown
    logger.info("Shutting down SentinelAI…")
    _stop_capture()
    if sniffer_thread and sniffer_thread.is_alive():
        sniffer_thread.join(timeout=5)


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SentinelAI — IoT IDS Backend",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health Check (unauthenticated — for Docker / load balancers)
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Ops"])
async def health_check():
    return {
        "status":          "healthy",
        "engine_status":   engine.get_status(),
        "uptime_seconds":  int(time.time() - START_TIME),
        "sniffer_alive":   _capture_running(),
        "db_ok":           db_ping(),
        "ws_clients":      len(manager.active_connections),
    }


# ---------------------------------------------------------------------------
# Core Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/status", tags=["Core"])
async def get_status():
    return {
        "engine_status":    engine.get_status(),
        "anomaly_threshold": engine.get_threshold(),
        "model_version":    "2.0",
        "started_at":       START_TIME,
        "uptime_seconds":   int(time.time() - START_TIME),
        "metadata":         engine.get_training_metadata(),
    }


@app.get("/api/capture/status", tags=["Capture"])
async def get_capture_status():
    return {"capturing": _capture_running()}


@app.post("/api/capture/start", tags=["Capture"])
async def start_capture():
    started = _start_capture()
    return {"capturing": True, "status": "started" if started else "already_running"}


@app.post("/api/capture/stop", tags=["Capture"])
async def stop_capture():
    stopped = _stop_capture()
    return {"capturing": False, "status": "stopping" if stopped else "already_stopped"}


class KitsunePredictionRequest(BaseModel):
    features: list[float] = Field(min_length=116, max_length=116)


class EdgeIIoTPredictionRequest(BaseModel):
    features: dict[str, object]


@app.get("/api/kitsune/status", tags=["Kitsune"])
async def get_kitsune_status():
    return {
        "ready": kitsune_model.ready,
        "feature_count": kitsune_model.feature_count,
        "model_path": KITSUNE_MODEL_PATH,
        "error": kitsune_model.load_error,
    }


@app.post("/api/kitsune/predict", tags=["Kitsune"])
async def predict_kitsune_attack(request: KitsunePredictionRequest):
    """Classify one pre-extracted Kitsune feature row as benign or attack."""
    try:
        return kitsune_model.predict(request.features)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/api/edge-iiot/status", tags=["Edge-IIoT"])
async def get_edge_iiot_status():
    return {
        "ready": edge_iiot_model.ready,
        "feature_count": edge_iiot_model.feature_count,
        "feature_names": edge_iiot_model.feature_names,
        "model_path": EDGE_IIOT_MODEL_PATH,
        "error": edge_iiot_model.load_error,
    }


@app.post("/api/edge-iiot/predict", tags=["Edge-IIoT"])
async def predict_edge_iiot_attack(request: EdgeIIoTPredictionRequest):
    """Classify one complete Edge-IIoT feature record as benign or attack."""
    try:
        return edge_iiot_model.predict(request.features)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/api/edge-iiot/attack-type/status", tags=["Edge-IIoT"])
async def get_edge_iiot_attack_type_status():
    return {
        "ready": edge_iiot_attack_type_model.ready,
        "feature_count": edge_iiot_attack_type_model.feature_count,
        "feature_names": edge_iiot_attack_type_model.feature_names,
        "classes": edge_iiot_attack_type_model.classes,
        "model_path": EDGE_IIOT_ATTACK_TYPE_MODEL_PATH,
        "error": edge_iiot_attack_type_model.load_error,
    }


@app.post("/api/edge-iiot/attack-type/predict", tags=["Edge-IIoT"])
async def predict_edge_iiot_attack_type(request: EdgeIIoTPredictionRequest):
    """Classify one Edge-IIoT feature record into a specific attack category."""
    try:
        return edge_iiot_attack_type_model.predict(request.features)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/api/demo/edge-iiot-samples", tags=["Demo"])
async def get_edge_iiot_demo_samples():
    """Return held-out Edge-IIoT records for the supervised-model demonstration."""
    if not os.path.exists(EDGE_IIOT_DEMO_SAMPLES_PATH):
        raise HTTPException(status_code=404, detail="Edge-IIoT demo samples are not installed.")

    try:
        with open(EDGE_IIOT_DEMO_SAMPLES_PATH, encoding="utf-8") as demo_file:
            return json.load(demo_file)
    except json.JSONDecodeError as error:
        raise HTTPException(status_code=500, detail="Edge-IIoT demo samples are invalid.") from error


@app.get("/api/alerts/recent", tags=["Core"])
async def get_recent_alerts(
    limit: int = 50,
    severity: str | None = None,
    protocol: str | None = None,
    since: float | None = Query(default=None, ge=0),
):
    """Return most recent alerts with optional filtering. Uses DB for persistence."""
    try:
        db = SessionLocal()
        query = db.query(AlertRecord).order_by(AlertRecord.timestamp.desc())
        if since is not None:
            query = query.filter(AlertRecord.timestamp >= since)
        if severity:
            query = query.filter(AlertRecord.severity == severity)
        if protocol:
            query = query.filter(AlertRecord.protocol == protocol)
        records = query.limit(limit).all()
        return [r.to_dict() for r in records]
    except Exception:
        # Fallback to in-memory if DB unavailable
        with alerts_lock:
            alerts = list(recent_alerts)
        if since is not None:
            alerts = [a for a in alerts if a["timestamp"] >= since]
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        return list(reversed(alerts[-limit:]))
    finally:
        try:
            db.close()
        except Exception:
            pass


@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """Dashboard connects here for real-time alert push."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ---------------------------------------------------------------------------
# Analytics Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/stats/summary", tags=["Analytics"])
async def get_stats_summary(since: float | None = Query(default=None, ge=0)):
    try:
        from sqlalchemy import func
        db = SessionLocal()
        records = db.query(AlertRecord)
        if since is not None:
            records = records.filter(AlertRecord.timestamp >= since)
        total = records.with_entities(func.count(AlertRecord.id)).scalar() or 0
        severity_map = dict(
            records.with_entities(AlertRecord.severity, func.count(AlertRecord.id))
            .group_by(AlertRecord.severity).all()
        )
        unique_src = records.with_entities(func.count(func.distinct(AlertRecord.src_ip))).scalar() or 0
        unique_dst = records.with_entities(func.count(func.distinct(AlertRecord.dst_ip))).scalar() or 0
        db.close()
        return {
            "total_alerts":  total,
            "critical_count": severity_map.get("critical", 0),
            "high_count":    severity_map.get("high", 0),
            "medium_count":  severity_map.get("medium", 0),
            "low_count":     severity_map.get("low", 0),
            "unique_src_ips": unique_src,
            "unique_dst_ips": unique_dst,
        }
    except Exception:
        # In-memory fallback
        with alerts_lock:
            alerts = list(recent_alerts)
        if since is not None:
            alerts = [a for a in alerts if a["timestamp"] >= since]
        sc = Counter(a["severity"] for a in alerts)
        return {
            "total_alerts":  len(alerts),
            "critical_count": sc.get("critical", 0),
            "high_count":    sc.get("high", 0),
            "medium_count":  sc.get("medium", 0),
            "low_count":     sc.get("low", 0),
            "unique_src_ips": len(set(a["src_ip"] for a in alerts)),
            "unique_dst_ips": len(set(a["dst_ip"] for a in alerts)),
        }


@app.get("/api/stats/top-attackers", tags=["Analytics"])
async def get_top_attackers(limit: int = 10, since: float | None = Query(default=None, ge=0)):
    try:
        from sqlalchemy import func
        db = SessionLocal()
        records = db.query(
                AlertRecord.src_ip,
                func.count(AlertRecord.id).label("count"),
                func.max(AlertRecord.timestamp).label("last_seen"),
            )
        if since is not None:
            records = records.filter(AlertRecord.timestamp >= since)
        rows = (
            records
            .group_by(AlertRecord.src_ip)
            .order_by(func.count(AlertRecord.id).desc())
            .limit(limit)
            .all()
        )
        db.close()
        return [{"ip": r.src_ip, "count": r.count, "last_seen": r.last_seen} for r in rows]
    except Exception:
        with alerts_lock:
            alerts = list(recent_alerts)
        if since is not None:
            alerts = [a for a in alerts if a["timestamp"] >= since]
        ip_counter: Counter = Counter()
        ip_last: dict = {}
        for a in alerts:
            ip = a["src_ip"]
            ip_counter[ip] += 1
            ip_last[ip] = a["timestamp"]
        return [
            {"ip": ip, "count": cnt, "last_seen": ip_last.get(ip, 0)}
            for ip, cnt in ip_counter.most_common(limit)
        ]


@app.get("/api/stats/protocol-distribution", tags=["Analytics"])
async def get_protocol_distribution(since: float | None = Query(default=None, ge=0)):
    try:
        from sqlalchemy import func
        db = SessionLocal()
        records = db.query(AlertRecord.protocol, func.count(AlertRecord.id))
        if since is not None:
            records = records.filter(AlertRecord.timestamp >= since)
        rows = dict(
            records
            .group_by(AlertRecord.protocol).all()
        )
        db.close()
        return {
            "TCP":   rows.get("TCP", 0),
            "UDP":   rows.get("UDP", 0),
            "ICMP":  rows.get("ICMP", 0),
            "OTHER": rows.get("OTHER", 0),
        }
    except Exception:
        with alerts_lock:
            alerts = list(recent_alerts)
        if since is not None:
            alerts = [a for a in alerts if a["timestamp"] >= since]
        pc = Counter(a.get("protocol", "OTHER") for a in alerts)
        return {"TCP": pc.get("TCP", 0), "UDP": pc.get("UDP", 0),
                "ICMP": pc.get("ICMP", 0), "OTHER": pc.get("OTHER", 0)}


@app.get("/api/stats/attack-types", tags=["Analytics"])
async def get_attack_type_distribution(since: float | None = Query(default=None, ge=0)):
    """Distribution of classified attack types — new endpoint for dashboard."""
    try:
        from sqlalchemy import func
        db = SessionLocal()
        records = db.query(AlertRecord.attack_type, func.count(AlertRecord.id))
        if since is not None:
            records = records.filter(AlertRecord.timestamp >= since)
        rows = dict(
            records
            .group_by(AlertRecord.attack_type).all()
        )
        db.close()
        return rows
    except Exception:
        with alerts_lock:
            alerts = list(recent_alerts)
        if since is not None:
            alerts = [a for a in alerts if a["timestamp"] >= since]
        ac = Counter(a.get("attack_type", "unknown") for a in alerts)
        return dict(ac)


@app.get("/api/stats/severity-timeline", tags=["Analytics"])
async def get_severity_timeline(
    bucket_minutes: int = 5,
    since: float | None = Query(default=None, ge=0),
):
    with alerts_lock:
        alerts = list(recent_alerts)

    if since is not None:
        alerts = [a for a in alerts if a["timestamp"] >= since]

    if not alerts:
        # Try DB
        try:
            db = SessionLocal()
            records = db.query(AlertRecord)
            if since is not None:
                records = records.filter(AlertRecord.timestamp >= since)
            db_alerts = (
                records
                .order_by(AlertRecord.timestamp.asc())
                .limit(1000)
                .all()
            )
            db.close()
            alerts = [a.to_dict() for a in db_alerts]
        except Exception:
            return []

    if not alerts:
        return []

    bucket_s = bucket_minutes * 60
    buckets: dict[int, dict] = {}
    for a in alerts:
        ts  = a["timestamp"]
        key = int(ts // bucket_s) * bucket_s
        if key not in buckets:
            buckets[key] = {
                "timestamp": key, "critical": 0, "high": 0,
                "medium": 0, "low": 0, "total": 0,
            }
        buckets[key][a["severity"]] += 1
        buckets[key]["total"]       += 1

    return sorted(buckets.values(), key=lambda b: b["timestamp"])


# ---------------------------------------------------------------------------
# Model Management
# ---------------------------------------------------------------------------

@app.post("/api/model/retrain", tags=["Model"])
async def retrain_model():
    """Force ML engine to reset and retrain from scratch."""
    engine.reset_full()
    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
        logger.info("Deleted persisted model — starting fresh Grace Period.")
    return {"status": "retrain_initiated", "engine_status": engine.get_status()}


# ---------------------------------------------------------------------------
# Dev entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
