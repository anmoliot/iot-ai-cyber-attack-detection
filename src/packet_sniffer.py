from __future__ import annotations

from time import time
from typing import Callable

try:
    from scapy.all import ICMP, IP, TCP, UDP, sniff
except ImportError:  # Allows docs/tests to import without Scapy installed.
    ICMP = IP = TCP = UDP = None
    sniff = None


PacketHandler = Callable[[dict], None]


def packet_to_metadata(packet) -> dict | None:
    if IP is None or IP not in packet:
        return None

    protocol = "OTHER"
    src_port = 0
    dst_port = 0

    if TCP in packet:
        protocol = "TCP"
        src_port = int(packet[TCP].sport)
        dst_port = int(packet[TCP].dport)
    elif UDP in packet:
        protocol = "UDP"
        src_port = int(packet[UDP].sport)
        dst_port = int(packet[UDP].dport)
    elif ICMP in packet:
        protocol = "ICMP"

    return {
        "timestamp": time(),
        "src_ip": packet[IP].src,
        "dst_ip": packet[IP].dst,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "length": len(packet),
    }


class PacketSniffer:
    def __init__(self, interface: str | None = None) -> None:
        self.interface = interface

    def start(self, handler: PacketHandler, packet_count: int = 0) -> None:
        if sniff is None:
            raise RuntimeError("Scapy is not installed. Run: pip install -r requirements.txt")

        def _handle(packet) -> None:
            metadata = packet_to_metadata(packet)
            if metadata is not None:
                handler(metadata)

        sniff(iface=self.interface, prn=_handle, store=False, count=packet_count)
