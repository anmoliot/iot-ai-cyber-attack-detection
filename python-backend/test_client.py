import asyncio
import websockets
import json

async def listen():
    uri = "ws://localhost:8000/ws/alerts"
    print(f"Connecting to live IDS Dashboard at {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Listening for cyber attacks...\n")
            while True:
                message = await websocket.recv()
                alert = json.loads(message)
                print("=== CYBER ATTACK ALERT DETECTED ===")
                print(f"Time: {alert['timestamp']}")
                print(f"Source IP: {alert['src_ip']} -> Dest IP: {alert['dst_ip']}")
                print(f"Anomaly Score: {alert['anomaly_score']} (Threshold: {alert['threshold']})\n")
    except Exception as e:
        print(f"Connection closed: {e}")

if __name__ == "__main__":
    asyncio.run(listen())
