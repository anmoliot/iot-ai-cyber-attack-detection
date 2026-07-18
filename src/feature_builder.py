from __future__ import annotations

import json
from pathlib import Path

from src.flow_generator import FlowRecord


PROTOCOL_ENCODING = {
    "ICMP": 1,
    "TCP": 6,
    "UDP": 17,
}


class FeatureBuilder:
    def __init__(self, features_path: str | Path = "models/features.json") -> None:
        self.features_path = Path(features_path)
        self.feature_names = self._load_feature_names()

    def _load_feature_names(self) -> list[str]:
        with self.features_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
            raise ValueError("features.json must contain a JSON list of feature names.")
        return data

    def build_dict(self, flow: FlowRecord) -> dict[str, float]:
        protocol_name = flow.key.protocol.upper()
        return {
            "duration": flow.duration,
            "protocol": float(PROTOCOL_ENCODING.get(protocol_name, 0)),
            "src_port": float(flow.key.src_port),
            "dst_port": float(flow.key.dst_port),
            "packet_count": float(flow.packet_count),
            "byte_count": float(flow.byte_count),
            "avg_packet_size": float(flow.avg_packet_size),
            "src_bytes": float(flow.src_bytes),
            "dst_bytes": float(flow.dst_bytes),
            "tcp_count": float(flow.tcp_count),
            "udp_count": float(flow.udp_count),
            "icmp_count": float(flow.icmp_count),
        }

    def build_vector(self, flow: FlowRecord) -> list[float]:
        feature_values = self.build_dict(flow)
        return [float(feature_values.get(name, 0.0)) for name in self.feature_names]
