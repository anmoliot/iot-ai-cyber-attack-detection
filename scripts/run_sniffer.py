from __future__ import annotations

from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.detect import DetectionEngine
from src.flow_generator import FlowGenerator
from src.logger import AlertRecord, CSVAlertLogger
from src.packet_sniffer import PacketSniffer
from src.severity import severity_for_prediction


def main() -> None:
    parser = argparse.ArgumentParser(description="Run live packet sniffer and IDS inference.")
    parser.add_argument("--interface", default=None, help="Network interface name. Leave empty for Scapy default.")
    parser.add_argument("--count", type=int, default=0, help="Number of packets to capture. 0 means unlimited.")
    args = parser.parse_args()

    flows = FlowGenerator()
    detector = DetectionEngine()
    logger = CSVAlertLogger(ROOT / "logs" / "attacks.csv")

    def handle_packet(metadata: dict) -> None:
        flow = flows.update(metadata)
        result = detector.predict_flow(flow)
        prediction = result["prediction"]
        severity_info = severity_for_prediction(prediction)

        if severity_info.severity == "None":
            return

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

    PacketSniffer(interface=args.interface).start(handle_packet, packet_count=args.count)


if __name__ == "__main__":
    main()
