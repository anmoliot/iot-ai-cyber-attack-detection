from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.detect import DetectionEngine
from src.flow_generator import FlowGenerator
from src.logger import AlertRecord, CSVAlertLogger
from src.severity import severity_for_prediction


def main() -> None:
    generator = FlowGenerator()
    detector = DetectionEngine()
    logger = CSVAlertLogger(ROOT / "logs" / "attacks.csv")

    packets = [
        {
            "src_ip": "192.168.1.25",
            "dst_ip": "192.168.1.1",
            "src_port": 44444,
            "dst_port": 23,
            "protocol": "TCP",
            "length": 600,
        },
        {
            "src_ip": "192.168.1.25",
            "dst_ip": "192.168.1.1",
            "src_port": 44444,
            "dst_port": 23,
            "protocol": "TCP",
            "length": 720,
        },
    ]

    flow = None
    for packet in packets:
        flow = generator.update(packet)

    if flow is None:
        raise RuntimeError("No flow generated.")

    result = detector.predict_flow(flow)
    prediction = result["prediction"]
    severity_info = severity_for_prediction(prediction)

    logger.write(
        AlertRecord(
            src_ip=flow.key.src_ip,
            dst_ip=flow.key.dst_ip,
            src_port=flow.key.src_port,
            dst_port=flow.key.dst_port,
            protocol=flow.key.protocol,
            prediction=prediction,
            confidence=result["confidence"],
            cve_id=severity_info.cve_id,
            cvss_score=severity_info.cvss_score,
            severity=severity_info.severity,
            action="Logged",
            details=result["details"],
        )
    )
    print(f"Logged detection: {prediction} severity={severity_info.severity}")


if __name__ == "__main__":
    main()
