import asyncio
import threading
import time
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ml_engine import MLEngine, extract_features

# =====================================================================
# GLOBAL STATE & ML ENGINE
# =====================================================================
engine = MLEngine(min_train_samples=500)
sniffer_thread = None
loop = None

# =====================================================================
# WEBSOCKET MANAGER
# =====================================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

# =====================================================================
# PACKET PROCESSING (Background Thread)
# =====================================================================
def process_packet(packet):
    """
    Called by scapy.sniff() for every packet received.
    Extracts features and feeds them into the ML Engine.
    """
    try:
        from scapy.layers.inet import IP
        from scapy.layers.inet6 import IPv6
        
        # Safely extract IP for UI purposes
        src_ip = "Unknown"
        dst_ip = "Unknown"
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
        elif IPv6 in packet:
            src_ip = packet[IPv6].src
            dst_ip = packet[IPv6].dst

        # 1. Feature Extraction
        features = extract_features(packet, engine.flow_tracker)
        status = engine.get_status()

        # 2. State Machine Routing
        if status == "UNTRAINED":
            engine.train_packet(features)
            # If the buffer just hit min_train_samples, the status flips to TRAINING.
            if engine.get_status() == "TRAINING":
                print("Grace period complete! Fitting model...")
                engine.finalize_training()
                print("Model is READY. Executing real-time anomaly detection.")

        elif status == "READY":
            is_anomaly = engine.predict_packet(features)
            
            if is_anomaly:
                score = engine.score_packet(features)
                alert = {
                    "type": "cyber_attack_alert",
                    "timestamp": time.time(),
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "anomaly_score": round(score, 4),
                    "threshold": round(engine.get_threshold(), 4)
                }
                # Broadcast alert to all connected UI clients asynchronously
                if loop and loop.is_running():
                    asyncio.run_coroutine_threadsafe(manager.broadcast(alert), loop)

    except Exception as e:
        print(f"Error processing packet: {e}")


def start_sniffer():
    """Background thread to sniff packets continuously."""
    from scapy.all import sniff
    print("Starting Scapy packet sniffer (Grace Period Active)...")
    # Using count=0 for infinite sniffing. store=0 prevents memory leaks.
    sniff(prn=process_packet, store=0)

# =====================================================================
# FASTAPI APP
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global sniffer_thread, loop
    loop = asyncio.get_running_loop()
    
    # Start the packet sniffer in a background thread
    sniffer_thread = threading.Thread(target=start_sniffer, daemon=True)
    sniffer_thread.start()
    
    yield
    
    # Cleanup (if needed) on shutdown
    print("Shutting down backend...")

app = FastAPI(title="IoT IDS Backend", lifespan=lifespan)

@app.get("/api/status")
async def get_status():
    """Return the current status of the ML Engine."""
    return {
        "status": engine.get_status(),
        "threshold": engine.get_threshold(),
        "metadata": engine.get_training_metadata()
    }

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """Dashboard UI connects here to receive real-time anomaly alerts."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
