from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Iterable


@dataclass(frozen=True)
class FlowKey:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str


@dataclass
class FlowRecord:
    key: FlowKey
    first_seen: float = field(default_factory=time)
    last_seen: float = field(default_factory=time)
    packet_count: int = 0
    byte_count: int = 0
    src_bytes: int = 0
    dst_bytes: int = 0
    tcp_count: int = 0
    udp_count: int = 0
    icmp_count: int = 0

    def add_packet(self, length: int, timestamp: float | None = None, direction: str = "src_to_dst") -> None:
        now = timestamp or time()
        self.last_seen = now
        self.packet_count += 1
        self.byte_count += length
        if direction == "src_to_dst":
            self.src_bytes += length
        else:
            self.dst_bytes += length

        protocol = self.key.protocol.upper()
        if protocol == "TCP":
            self.tcp_count += 1
        elif protocol == "UDP":
            self.udp_count += 1
        elif protocol == "ICMP":
            self.icmp_count += 1

    @property
    def duration(self) -> float:
        return max(self.last_seen - self.first_seen, 0.0)

    @property
    def avg_packet_size(self) -> float:
        if self.packet_count == 0:
            return 0.0
        return self.byte_count / self.packet_count


class FlowGenerator:
    def __init__(self) -> None:
        self.flows: dict[FlowKey, FlowRecord] = {}

    def update(self, packet_metadata: dict) -> FlowRecord:
        key = FlowKey(
            src_ip=packet_metadata.get("src_ip", "0.0.0.0"),
            dst_ip=packet_metadata.get("dst_ip", "0.0.0.0"),
            src_port=int(packet_metadata.get("src_port", 0)),
            dst_port=int(packet_metadata.get("dst_port", 0)),
            protocol=str(packet_metadata.get("protocol", "OTHER")),
        )
        flow = self.flows.setdefault(key, FlowRecord(key=key))
        flow.add_packet(
            length=int(packet_metadata.get("length", 0)),
            timestamp=packet_metadata.get("timestamp"),
        )
        return flow

    def all_flows(self) -> Iterable[FlowRecord]:
        return self.flows.values()
