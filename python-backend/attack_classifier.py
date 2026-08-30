"""
attack_classifier.py
============================================================
Rule-based attack type classifier for SentinelAI.

Applied AFTER the autoencoder flags a packet as anomalous.
Uses heuristic rules on the numeric feature vector to enrich
alerts with a human-readable attack category.

This is a lightweight enrichment layer — NOT a replacement for a
proper supervised classifier. It uses domain knowledge from
network security to interpret anomalous packet patterns.
"""

from __future__ import annotations
from typing import NamedTuple

import numpy as np

from ml_engine import FEATURE_NAMES


class Classification(NamedTuple):
    attack_type: str        # machine-readable key
    attack_label: str       # human-readable label for UI
    attack_confidence: float  # 0.0–1.0 confidence estimate


# Attack type catalogue
_CATALOGUE = {
    "syn_flood":   "SYN Flood (DDoS)",
    "udp_flood":   "UDP Flood (DDoS)",
    "icmp_flood":  "ICMP Flood",
    "port_scan":   "Port Scan",
    "brute_force": "Brute Force",
    "data_exfil":  "Data Exfiltration",
    "arp_poison":  "ARP Poisoning",
    "unknown":     "Unknown Anomaly",
}

# Build a lookup index so we never hard-code array positions
_IDX = {name: i for i, name in enumerate(FEATURE_NAMES)}


def _f(features: np.ndarray, name: str, default: float = 0.0) -> float:
    """Safe feature lookup by name."""
    idx = _IDX.get(name)
    if idx is None or idx >= len(features):
        return default
    val = features[idx]
    return float(val) if not (np.isnan(val) or np.isinf(val)) else default


def classify_attack(features: np.ndarray) -> Classification:
    """
    Classify an anomalous packet into a likely attack category.

    Args:
        features: numpy feature vector matching ml_engine.FEATURE_NAMES

    Returns:
        Classification namedtuple with attack_type, attack_label, attack_confidence
    """
    ip_proto       = _f(features, "ip_protocol")
    tcp_flags      = int(_f(features, "tcp_flags"))
    payload_len    = _f(features, "payload_length")
    port_diversity = _f(features, "flow_recent_port_diversity")
    inter_arrival  = _f(features, "flow_inter_arrival_ms")
    pkt_count      = _f(features, "flow_packet_count")
    dst_port       = _f(features, "dst_port")
    src_port       = _f(features, "src_port")
    tcp_window     = _f(features, "tcp_window_size")
    pkt_len        = _f(features, "packet_length")

    # ------------------------------------------------------------------
    # TCP flag masks
    SYN = 0x02
    ACK = 0x10
    FIN = 0x01
    RST = 0x04

    syn_set = bool(tcp_flags & SYN)
    ack_set = bool(tcp_flags & ACK)
    fin_set = bool(tcp_flags & FIN)

    # ------------------------------------------------------------------
    # 1. SYN Flood — many SYN packets, no ACK, tiny/no payload, fast rate
    if (ip_proto == 6 and syn_set and not ack_set
            and payload_len < 20 and inter_arrival < 50):
        conf = 0.88
        if inter_arrival < 5:
            conf = 0.95
        return Classification("syn_flood", _CATALOGUE["syn_flood"], conf)

    # 2. Port Scan — high destination port diversity, small packets
    if port_diversity >= 8 and payload_len < 30:
        conf = 0.80
        if port_diversity >= 20:
            conf = 0.92
        return Classification("port_scan", _CATALOGUE["port_scan"], conf)

    # 3. UDP Flood — UDP protocol, very fast inter-arrival
    if ip_proto == 17 and inter_arrival < 10 and pkt_count > 20:
        conf = 0.82
        if inter_arrival < 2:
            conf = 0.91
        return Classification("udp_flood", _CATALOGUE["udp_flood"], conf)

    # 4. ICMP Flood — ICMP protocol, high packet count, fast rate
    if ip_proto == 1 and inter_arrival < 20 and pkt_count > 15:
        conf = 0.78
        return Classification("icmp_flood", _CATALOGUE["icmp_flood"], conf)

    # 5. Brute Force — repeated TCP to specific auth ports (22/23/3389/21/25)
    AUTH_PORTS = {22, 23, 3389, 21, 25, 445, 5900}
    if ip_proto == 6 and int(dst_port) in AUTH_PORTS and pkt_count > 10:
        conf = 0.73
        if pkt_count > 50:
            conf = 0.87
        return Classification("brute_force", _CATALOGUE["brute_force"], conf)

    # 6. Data Exfiltration — large outbound payload on unusual/high port
    if (payload_len > 800 and dst_port > 9000
            and ip_proto in (6, 17)):
        conf = 0.65
        if payload_len > 1400:
            conf = 0.77
        return Classification("data_exfil", _CATALOGUE["data_exfil"], conf)

    # 7. ARP Poisoning heuristic (non-IP, Ethernet-level anomaly)
    if ip_proto == 0 and pkt_len < 64:
        return Classification("arp_poison", _CATALOGUE["arp_poison"], 0.55)

    # Fallback
    return Classification("unknown", _CATALOGUE["unknown"], 0.35)
