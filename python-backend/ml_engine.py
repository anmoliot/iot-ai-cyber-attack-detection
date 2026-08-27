"""
ml_engine.py
============================================================
Real-time packet-level anomaly detection module.

This module is the ML Engineer's deliverable. It is a fully
self-contained, backend-agnostic module. It has NO knowledge of
FastAPI, WebSockets, sockets, sniffing, or networking — the Backend
Engineer owns packet capture and transport, and calls into this
module with already-captured scapy packet objects.

------------------------------------------------------------
PIPELINE
------------------------------------------------------------
    raw scapy packet
        -> extract_features(packet)            [stateless + bounded stateful]
        -> numpy feature vector (fixed length)
        -> MLEngine.train_packet(vec)           [Grace Period]
           MLEngine.predict_packet(vec) -> bool [Execution Period]

------------------------------------------------------------
FEATURE DEFINITIONS
------------------------------------------------------------
See FEATURE_NAMES below for the canonical, ordered feature schema.
Features are drawn ONLY from single-packet header fields plus a
small amount of bounded recent-history state (packet/byte counters,
recent packet sizes, recent inter-arrival gaps, recent destination
port diversity). No raw IP addresses, payload contents, or labels
ever enter the feature vector.

------------------------------------------------------------
TRAINING LIFECYCLE (Grace Period)
------------------------------------------------------------
    UNTRAINED -> (train_packet() called repeatedly, buffering
                  samples) -> once buffer reaches `min_train_samples`
                  the autoencoder is fit -> TRAINING -> READY

  - train_packet() never performs a full retrain on every call.
    Samples are buffered (bounded deque) and the model is fit once,
    or periodically re-fit in controlled batches, never per-packet.
  - The feature scaler is fit ONLY on this Grace Period buffer, and
    is frozen once training completes.
  - The anomaly threshold is derived from the training data's own
    reconstruction-error distribution (a configurable percentile),
    never from attack labels (there are none — this is unsupervised).

------------------------------------------------------------
INFERENCE LIFECYCLE (Execution Period)
------------------------------------------------------------
    predict_packet(vec):
        if engine not READY: return False   (fail-safe default)
        x = frozen_scaler.transform(vec)
        error = ||x - autoencoder(x)||^2 (reconstruction error)
        return error > frozen_threshold

  score_packet(vec) exposes the raw reconstruction error for callers
  who want more than a boolean.

------------------------------------------------------------
THRESHOLD METHODOLOGY
------------------------------------------------------------
  threshold = percentile(training_reconstruction_errors, P)
  P defaults to 97 and is configurable via `threshold_percentile`.
  The threshold is computed once, at the end of training, and frozen.

------------------------------------------------------------
STATE BEHAVIOR
------------------------------------------------------------
  MLEngine holds a small amount of bounded behavioral state per
  logical "flow key" (src_ip, dst_ip, proto) used only to derive
  short-window statistical features (recent packet sizes,
  inter-arrival gaps, destination-port diversity). This state:
    - is bounded (deques with maxlen)
    - is deterministic
    - only ever looks at CURRENT and PAST packets
    - never at future packets
    - is fully clearable via reset_state()
  Raw IP addresses are used internally ONLY as dictionary keys for
  this state tracking. They are never written into the numeric
  feature vector itself.

------------------------------------------------------------
LIMITATIONS (please read before relying on this in production)
------------------------------------------------------------
  - This is a single-packet + short-window statistical detector. It
    is NOT a deep behavioral/flow-level classifier and will not
    reliably distinguish attack families (e.g. Mirai vs. Torii vs.
    generic DDoS). It only flags "this looks statistically unlike
    what I learned during the Grace Period."
  - Quality is entirely dependent on the Grace Period traffic being
    representative of "normal" — if attacks occur during the Grace
    Period, they will be learned as normal.
  - IPv6 packets are supported on a best-effort basis: recognized
    header fields map onto the same schema; unmapped/unavailable
    fields default to 0.0 (see extract_features docstring).
  - This module assumes a single-threaded caller per MLEngine
    instance. If the Backend Engineer calls train_packet /
    predict_packet from multiple threads concurrently against the
    same MLEngine instance, external locking is required.
  - No online/continual re-training after the model reaches READY.
    Concept drift after the Grace Period is out of scope; the
    Backend Engineer would need to instantiate + train a new
    MLEngine and swap it in if periodic recalibration is desired.

------------------------------------------------------------
DEPENDENCIES
------------------------------------------------------------
  numpy, scapy (for type hints / packet field access)
  No PyTorch/TensorFlow — the autoencoder is implemented in plain
  NumPy for a small footprint and fast, dependency-light real-time
  inference.
"""

from __future__ import annotations

import json
import pickle
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Deque, Dict, List, Optional, Tuple

import numpy as np

try:
    from scapy.packet import Packet
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.inet6 import IPv6
except ImportError:  # pragma: no cover - scapy is an expected runtime dep
    Packet = object  # type: ignore
    IP = TCP = UDP = ICMP = IPv6 = None  # type: ignore


# ============================================================
# PART 2 — FEATURE SCHEMA
# ============================================================

FEATURE_NAMES: List[str] = [
    # --- single-packet header features ---
    "packet_length",
    "ip_header_length",
    "ttl",
    "ip_protocol",        # numeric IANA protocol number (6=TCP, 17=UDP, 1=ICMP...)
    "is_ipv6",             # 0.0 / 1.0
    "src_port",
    "dst_port",
    "tcp_flags",           # bitmask as int, 0 if not TCP
    "tcp_window_size",
    "tcp_header_length",
    "udp_length",
    "icmp_type",
    "icmp_code",
    "payload_length",
    # --- bounded short-window behavioral features (stateful) ---
    "flow_packet_count",       # packets seen so far for this flow key (capped)
    "flow_byte_count_avg",     # running mean packet length for this flow key
    "flow_inter_arrival_ms",   # ms since previous packet on this flow key
    "flow_recent_size_std",    # std-dev of last N packet sizes on this flow key
    "flow_recent_port_diversity",  # distinct dst ports in last N packets on this flow key
]

FEATURE_DIM = len(FEATURE_NAMES)

# Bounded-history window sizes (all fixed, all small -> memory-safe)
_RECENT_WINDOW = 20          # last N packets per flow key kept for std/diversity
_MAX_TRACKED_FLOWS = 5000    # cap on number of distinct flow keys tracked


def get_feature_names() -> List[str]:
    """Return the canonical, ordered list of feature names."""
    return list(FEATURE_NAMES)


# ============================================================
# BOUNDED FLOW STATE (used internally by extract_features via MLEngine,
# and standalone via FlowStateTracker for stateless callers/tests)
# ============================================================

@dataclass
class _FlowState:
    packet_count: int = 0
    byte_sum: float = 0.0
    last_seen_ts: Optional[float] = None
    recent_sizes: Deque[float] = field(default_factory=lambda: deque(maxlen=_RECENT_WINDOW))
    recent_ports: Deque[int] = field(default_factory=lambda: deque(maxlen=_RECENT_WINDOW))


class FlowStateTracker:
    """
    Bounded, deterministic behavioral state tracker.

    Keyed internally by (src_ip, dst_ip, protocol) — raw IPs are used
    ONLY as dictionary keys here and never enter the numeric feature
    vector. State is capped at _MAX_TRACKED_FLOWS distinct flows
    (oldest-inserted eviction) to guarantee bounded memory.
    """

    def __init__(self) -> None:
        self._flows: Dict[Tuple[str, str, int], _FlowState] = {}
        self._insertion_order: Deque[Tuple[str, str, int]] = deque()

    def _get_or_create(self, key: Tuple[str, str, int]) -> _FlowState:
        state = self._flows.get(key)
        if state is None:
            if len(self._flows) >= _MAX_TRACKED_FLOWS:
                oldest = self._insertion_order.popleft()
                self._flows.pop(oldest, None)
            state = _FlowState()
            self._flows[key] = state
            self._insertion_order.append(key)
        return state

    def observe(
        self,
        key: Tuple[str, str, int],
        packet_length: float,
        dst_port: int,
        now: Optional[float] = None,
    ) -> Tuple[int, float, float, float, int]:
        """
        Read CURRENT + PAST state, compute behavioral features, THEN
        update state with the current packet (so no future leakage).

        Returns:
            (flow_packet_count, flow_byte_count_avg, flow_inter_arrival_ms,
             flow_recent_size_std, flow_recent_port_diversity)
        """
        now = time.time() if now is None else now
        state = self._get_or_create(key)

        # --- compute features from state BEFORE this packet updates it ---
        prior_count = state.packet_count
        prior_avg = (state.byte_sum / prior_count) if prior_count > 0 else 0.0
        inter_arrival_ms = (
            (now - state.last_seen_ts) * 1000.0 if state.last_seen_ts is not None else 0.0
        )
        recent_size_std = float(np.std(state.recent_sizes)) if len(state.recent_sizes) > 0 else 0.0
        recent_port_diversity = float(len(set(state.recent_ports)))

        features = (
            prior_count,
            prior_avg,
            max(inter_arrival_ms, 0.0),
            recent_size_std,
            recent_port_diversity,
        )

        # --- update state with current packet (post-read, no leakage) ---
        state.packet_count += 1
        state.byte_sum += packet_length
        state.last_seen_ts = now
        state.recent_sizes.append(packet_length)
        state.recent_ports.append(dst_port)

        return features

    def reset(self) -> None:
        self._flows.clear()
        self._insertion_order.clear()


# ============================================================
# PART 1 — FEATURE EXTRACTION
# ============================================================

def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def extract_features(
    packet: "Packet",
    flow_tracker: Optional[FlowStateTracker] = None,
    now: Optional[float] = None,
) -> np.ndarray:
    """
    Convert a single raw scapy packet into a fixed-length numeric
    feature vector matching FEATURE_NAMES / FEATURE_DIM exactly.

    Args:
        packet: a scapy Packet object (from sniff()).
        flow_tracker: optional FlowStateTracker for bounded behavioral
            features. If omitted, a fresh internal tracker is used
            (i.e. no cross-call history) — pass a tracker owned by
            your MLEngine/session for meaningful behavioral features.
        now: optional timestamp override (seconds), mainly for tests.

    Returns:
        np.ndarray of shape (FEATURE_DIM,), dtype float64.

    This function NEVER raises on malformed/missing layers — any
    field that cannot be determined defaults to 0.0. It never writes
    raw IP addresses or payload bytes into the returned vector.
    """
    if flow_tracker is None:
        flow_tracker = FlowStateTracker()

    packet_length = float(len(bytes(packet))) if packet is not None else 0.0

    ip_header_length = 0.0
    ttl = 0.0
    ip_protocol = 0.0
    is_ipv6 = 0.0
    src_ip = "0.0.0.0"
    dst_ip = "0.0.0.0"

    has_ip = IP is not None and packet is not None and packet.haslayer(IP)
    has_ipv6 = IPv6 is not None and packet is not None and packet.haslayer(IPv6)

    if has_ip:
        ip_layer = packet[IP]
        ip_header_length = float(getattr(ip_layer, "ihl", 0) or 0) * 4.0
        ttl = float(getattr(ip_layer, "ttl", 0) or 0)
        ip_protocol = float(getattr(ip_layer, "proto", 0) or 0)
        src_ip = str(getattr(ip_layer, "src", "0.0.0.0"))
        dst_ip = str(getattr(ip_layer, "dst", "0.0.0.0"))
    elif has_ipv6:
        ip6_layer = packet[IPv6]
        is_ipv6 = 1.0
        ttl = float(getattr(ip6_layer, "hlim", 0) or 0)
        ip_protocol = float(getattr(ip6_layer, "nh", 0) or 0)
        ip_header_length = 40.0  # fixed IPv6 base header length
        src_ip = str(getattr(ip6_layer, "src", "::"))
        dst_ip = str(getattr(ip6_layer, "dst", "::"))

    src_port = 0.0
    dst_port = 0.0
    tcp_flags = 0.0
    tcp_window = 0.0
    tcp_header_len = 0.0
    udp_length = 0.0
    icmp_type = 0.0
    icmp_code = 0.0
    payload_length = 0.0
    protocol_id_for_key = 0

    if TCP is not None and packet is not None and packet.haslayer(TCP):
        tcp_layer = packet[TCP]
        src_port = float(getattr(tcp_layer, "sport", 0) or 0)
        dst_port = float(getattr(tcp_layer, "dport", 0) or 0)
        flags_obj = getattr(tcp_layer, "flags", 0)
        tcp_flags = float(int(flags_obj)) if flags_obj is not None else 0.0
        tcp_window = float(getattr(tcp_layer, "window", 0) or 0)
        tcp_header_len = float(getattr(tcp_layer, "dataofs", 0) or 0) * 4.0
        payload_length = float(len(bytes(tcp_layer.payload))) if tcp_layer.payload else 0.0
        protocol_id_for_key = 6

    elif UDP is not None and packet is not None and packet.haslayer(UDP):
        udp_layer = packet[UDP]
        src_port = float(getattr(udp_layer, "sport", 0) or 0)
        dst_port = float(getattr(udp_layer, "dport", 0) or 0)
        # scapy leaves .len as None until the packet is serialized/built,
        # so fall back to computing it from the serialized bytes.
        raw_len = getattr(udp_layer, "len", None)
        udp_length = float(raw_len) if raw_len is not None else float(len(bytes(udp_layer)))
        payload_length = float(len(bytes(udp_layer.payload))) if udp_layer.payload else 0.0
        protocol_id_for_key = 17

    elif ICMP is not None and packet is not None and packet.haslayer(ICMP):
        icmp_layer = packet[ICMP]
        icmp_type = float(getattr(icmp_layer, "type", 0) or 0)
        icmp_code = float(getattr(icmp_layer, "code", 0) or 0)
        payload_length = float(len(bytes(icmp_layer.payload))) if icmp_layer.payload else 0.0
        protocol_id_for_key = 1

    flow_key = (src_ip, dst_ip, protocol_id_for_key)
    (
        flow_packet_count,
        flow_byte_count_avg,
        flow_inter_arrival_ms,
        flow_recent_size_std,
        flow_recent_port_diversity,
    ) = flow_tracker.observe(flow_key, packet_length, _safe_int(dst_port), now=now)

    vector = np.array(
        [
            packet_length,
            ip_header_length,
            ttl,
            ip_protocol,
            is_ipv6,
            src_port,
            dst_port,
            tcp_flags,
            tcp_window,
            tcp_header_len,
            udp_length,
            icmp_type,
            icmp_code,
            payload_length,
            float(flow_packet_count),
            float(flow_byte_count_avg),
            float(flow_inter_arrival_ms),
            float(flow_recent_size_std),
            float(flow_recent_port_diversity),
        ],
        dtype=np.float64,
    )

    # sanitize NaN/Inf deterministically -> 0.0
    vector = np.nan_to_num(vector, nan=0.0, posinf=0.0, neginf=0.0)

    assert vector.shape[0] == FEATURE_DIM, "feature vector length drifted from schema"
    return vector


# ============================================================
# PART 8 — NORMALIZATION (frozen after fit)
# ============================================================

class _FrozenStandardScaler:
    """Minimal, dependency-free standard scaler. Fit once, frozen after."""

    def __init__(self) -> None:
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None
        self._fitted = False

    def fit(self, X: np.ndarray) -> "_FrozenStandardScaler":
        self.mean_ = X.mean(axis=0)
        std = X.std(axis=0)
        std[std < 1e-8] = 1.0  # avoid divide-by-zero on constant features
        self.std_ = std
        self._fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Scaler used before fit().")
        return (X - self.mean_) / self.std_

    def to_dict(self) -> dict:
        return {
            "mean": None if self.mean_ is None else self.mean_.tolist(),
            "std": None if self.std_ is None else self.std_.tolist(),
            "fitted": self._fitted,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "_FrozenStandardScaler":
        obj = cls()
        if d.get("mean") is not None:
            obj.mean_ = np.array(d["mean"], dtype=np.float64)
            obj.std_ = np.array(d["std"], dtype=np.float64)
            obj._fitted = bool(d.get("fitted", True))
        return obj


# ============================================================
# PART 4 — AUTOENCODER (plain NumPy, small & real-time friendly)
# ============================================================

class _NumpyAutoencoder:
    """
    Minimal single-hidden-layer autoencoder (encoder + decoder),
    trained with plain-NumPy mini-batch gradient descent.

    Architecture: input_dim -> hidden_dim (tanh) -> latent_dim (tanh)
                  -> hidden_dim (tanh) -> input_dim (linear)

    Kept intentionally small: this runs per-packet in real time, so
    inference must be a handful of matrix multiplies, not a deep net.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 12,
        latent_dim: int = 6,
        learning_rate: float = 0.01,
        seed: int = 42,
    ) -> None:
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.lr = learning_rate

        rng = np.random.default_rng(seed)
        scale = lambda fan_in: np.sqrt(2.0 / fan_in)

        self.W1 = rng.normal(0, scale(input_dim), (input_dim, hidden_dim))
        self.b1 = np.zeros(hidden_dim)
        self.W2 = rng.normal(0, scale(hidden_dim), (hidden_dim, latent_dim))
        self.b2 = np.zeros(latent_dim)
        self.W3 = rng.normal(0, scale(latent_dim), (latent_dim, hidden_dim))
        self.b3 = np.zeros(hidden_dim)
        self.W4 = rng.normal(0, scale(hidden_dim), (hidden_dim, input_dim))
        self.b4 = np.zeros(input_dim)

    @staticmethod
    def _tanh(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    @staticmethod
    def _tanh_deriv(a: np.ndarray) -> np.ndarray:
        return 1.0 - a ** 2

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, dict]:
        z1 = X @ self.W1 + self.b1
        a1 = self._tanh(z1)
        z2 = a1 @ self.W2 + self.b2
        a2 = self._tanh(z2)  # latent
        z3 = a2 @ self.W3 + self.b3
        a3 = self._tanh(z3)
        z4 = a3 @ self.W4 + self.b4  # reconstruction (linear output)
        cache = {"X": X, "a1": a1, "a2": a2, "a3": a3, "z4": z4}
        return z4, cache

    def reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        recon, _ = self.forward(X)
        return np.mean((X - recon) ** 2, axis=1)

    def train_batch(self, X: np.ndarray) -> float:
        n = X.shape[0]
        recon, cache = self.forward(X)
        error = recon - X
        loss = float(np.mean(error ** 2))

        # backprop
        dZ4 = (2.0 / n) * error  # (n, input_dim)
        dW4 = cache["a3"].T @ dZ4
        db4 = dZ4.sum(axis=0)

        dA3 = dZ4 @ self.W4.T
        dZ3 = dA3 * self._tanh_deriv(cache["a3"])
        dW3 = cache["a2"].T @ dZ3
        db3 = dZ3.sum(axis=0)

        dA2 = dZ3 @ self.W3.T
        dZ2 = dA2 * self._tanh_deriv(cache["a2"])
        dW2 = cache["a1"].T @ dZ2
        db2 = dZ2.sum(axis=0)

        dA1 = dZ2 @ self.W2.T
        dZ1 = dA1 * self._tanh_deriv(cache["a1"])
        dW1 = cache["X"].T @ dZ1
        db1 = dZ1.sum(axis=0)

        self.W4 -= self.lr * dW4
        self.b4 -= self.lr * db4
        self.W3 -= self.lr * dW3
        self.b3 -= self.lr * db3
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

        return loss

    def fit(self, X: np.ndarray, epochs: int = 30, batch_size: int = 32, seed: int = 42) -> List[float]:
        rng = np.random.default_rng(seed)
        n = X.shape[0]
        losses = []
        for _epoch in range(epochs):
            perm = rng.permutation(n)
            X_shuffled = X[perm]
            epoch_losses = []
            for start in range(0, n, batch_size):
                batch = X_shuffled[start:start + batch_size]
                if batch.shape[0] == 0:
                    continue
                epoch_losses.append(self.train_batch(batch))
            losses.append(float(np.mean(epoch_losses)) if epoch_losses else 0.0)
        return losses

    def to_dict(self) -> dict:
        return {
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "latent_dim": self.latent_dim,
            "learning_rate": self.lr,
            "W1": self.W1.tolist(), "b1": self.b1.tolist(),
            "W2": self.W2.tolist(), "b2": self.b2.tolist(),
            "W3": self.W3.tolist(), "b3": self.b3.tolist(),
            "W4": self.W4.tolist(), "b4": self.b4.tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "_NumpyAutoencoder":
        obj = cls(d["input_dim"], d["hidden_dim"], d["latent_dim"], d["learning_rate"])
        obj.W1 = np.array(d["W1"]); obj.b1 = np.array(d["b1"])
        obj.W2 = np.array(d["W2"]); obj.b2 = np.array(d["b2"])
        obj.W3 = np.array(d["W3"]); obj.b3 = np.array(d["b3"])
        obj.W4 = np.array(d["W4"]); obj.b4 = np.array(d["b4"])
        return obj


# ============================================================
# ENGINE STATE MACHINE
# ============================================================

class EngineStatus(str, Enum):
    UNTRAINED = "UNTRAINED"
    TRAINING = "TRAINING"
    READY = "READY"


MODEL_VERSION = "1.0.0"


# ============================================================
# PART 5, 6, 7, 9, 10, 11 — MLEngine
# ============================================================

class MLEngine:
    """
    Unsupervised packet anomaly detector.

    Usage (Backend Engineer side):

        engine = MLEngine(input_dim=FEATURE_DIM)

        # --- Grace Period ---
        for packet in sniff_normal_traffic():
            vec = extract_features(packet, engine.flow_tracker)
            engine.train_packet(vec)
        engine.finalize_training()

        # --- Execution Period ---
        for packet in sniff_live_traffic():
            vec = extract_features(packet, engine.flow_tracker)
            if engine.predict_packet(vec):
                alert(packet)
    """

    def __init__(
        self,
        input_dim: int = FEATURE_DIM,
        hidden_dim: int = 12,
        latent_dim: int = 6,
        learning_rate: float = 0.01,
        min_train_samples: int = 200,
        max_buffer_samples: int = 20000,
        epochs: int = 30,
        batch_size: int = 32,
        threshold_percentile: float = 97.0,
        seed: int = 42,
    ) -> None:
        if input_dim <= 0:
            raise ValueError("input_dim must be positive")

        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.min_train_samples = min_train_samples
        self.epochs = epochs
        self.batch_size = batch_size
        self.threshold_percentile = threshold_percentile
        self.seed = seed

        self.status: EngineStatus = EngineStatus.UNTRAINED
        self._buffer: Deque[np.ndarray] = deque(maxlen=max_buffer_samples)

        self._scaler = _FrozenStandardScaler()
        self._model: Optional[_NumpyAutoencoder] = None
        self._threshold: Optional[float] = None
        self._training_metadata: dict = {}

        # Shared bounded flow-state tracker; the Backend Engineer should
        # reuse the SAME tracker instance across extract_features calls
        # for this engine's session so behavioral features are meaningful.
        self.flow_tracker = FlowStateTracker()

    # -------------------------
    # validation
    # -------------------------
    def _validate_vector(self, feature_vector: np.ndarray) -> np.ndarray:
        vec = np.asarray(feature_vector, dtype=np.float64)
        if vec.ndim != 1 or vec.shape[0] != self.input_dim:
            raise ValueError(
                f"Expected feature vector of shape ({self.input_dim},), "
                f"got {vec.shape}."
            )
        vec = np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)
        return vec

    # -------------------------
    # PART 5 — training API
    # -------------------------
    def train_packet(self, feature_vector: np.ndarray) -> None:
        """
        Call during the Grace Period, once per packet. Buffers samples
        only — does NOT retrain the network on every call. Once the
        buffer reaches `min_train_samples`, call finalize_training()
        to actually fit the model (the Backend Engineer controls when
        the Grace Period ends and calls finalize_training()).
        """
        vec = self._validate_vector(feature_vector)
        self._buffer.append(vec)
        if self.status == EngineStatus.UNTRAINED and len(self._buffer) >= self.min_train_samples:
            self.status = EngineStatus.TRAINING

    def finalize_training(self) -> None:
        """
        End of Grace Period. Fits the scaler + autoencoder on all
        buffered samples, computes and freezes the anomaly threshold.
        Safe to call multiple times (re-fits from current buffer).
        """
        if len(self._buffer) < max(2, self.min_train_samples):
            raise RuntimeError(
                f"Not enough training samples: have {len(self._buffer)}, "
                f"need at least {self.min_train_samples}. Call train_packet() more."
            )

        self.status = EngineStatus.TRAINING
        X = np.stack(list(self._buffer), axis=0)

        self._scaler = _FrozenStandardScaler().fit(X)
        X_scaled = self._scaler.transform(X)

        self._model = _NumpyAutoencoder(
            input_dim=self.input_dim,
            hidden_dim=self.hidden_dim,
            latent_dim=self.latent_dim,
            learning_rate=self.learning_rate,
            seed=self.seed,
        )
        losses = self._model.fit(
            X_scaled, epochs=self.epochs, batch_size=self.batch_size, seed=self.seed
        )

        training_errors = self._model.reconstruction_error(X_scaled)
        self._threshold = float(np.percentile(training_errors, self.threshold_percentile))

        self._training_metadata = {
            "trained_at": time.time(),
            "n_training_samples": int(X.shape[0]),
            "final_loss": losses[-1] if losses else None,
            "threshold_percentile": self.threshold_percentile,
            "threshold": self._threshold,
            "model_version": MODEL_VERSION,
        }
        self.status = EngineStatus.READY

    # -------------------------
    # PART 6 — prediction API
    # -------------------------
    def score_packet(self, feature_vector: np.ndarray) -> float:
        """Return the raw reconstruction-error anomaly score. 0.0 if not READY."""
        if self.status != EngineStatus.READY or self._model is None or self._threshold is None:
            return 0.0
        vec = self._validate_vector(feature_vector)
        x_scaled = self._scaler.transform(vec.reshape(1, -1))
        error = self._model.reconstruction_error(x_scaled)[0]
        return float(error)

    def predict_packet(self, feature_vector: np.ndarray) -> bool:
        """
        Return True if the packet is anomalous relative to the
        learned normal-traffic distribution, False otherwise.
        Fails safe (returns False) if the model is not yet READY.
        """
        if self.status != EngineStatus.READY:
            return False
        score = self.score_packet(feature_vector)
        return score > self._threshold  # type: ignore[operator]

    # -------------------------
    # status helpers
    # -------------------------
    def get_status(self) -> str:
        return self.status.value

    def get_threshold(self) -> Optional[float]:
        return self._threshold

    def get_training_metadata(self) -> dict:
        return dict(self._training_metadata)

    # -------------------------
    # PART 10 — reset
    # -------------------------
    def reset_state(self) -> None:
        """Clear behavioral/flow tracking state. Keeps the trained model."""
        self.flow_tracker.reset()

    def reset_full(self) -> None:
        """Full reset: clears training buffer, trained model, and flow state."""
        self._buffer.clear()
        self._scaler = _FrozenStandardScaler()
        self._model = None
        self._threshold = None
        self._training_metadata = {}
        self.status = EngineStatus.UNTRAINED
        self.flow_tracker.reset()

    # -------------------------
    # PART 9 — serialization
    # -------------------------
    def save(self, path: str) -> None:
        artifact = {
            "model_version": MODEL_VERSION,
            "status": self.status.value,
            "config": {
                "input_dim": self.input_dim,
                "hidden_dim": self.hidden_dim,
                "latent_dim": self.latent_dim,
                "learning_rate": self.learning_rate,
                "min_train_samples": self.min_train_samples,
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "threshold_percentile": self.threshold_percentile,
                "seed": self.seed,
            },
            "feature_names": FEATURE_NAMES,
            "scaler": self._scaler.to_dict(),
            "model": self._model.to_dict() if self._model is not None else None,
            "threshold": self._threshold,
            "training_metadata": self._training_metadata,
        }
        with open(path, "wb") as f:
            pickle.dump(artifact, f)

    def load(self, path: str) -> None:
        with open(path, "rb") as f:
            artifact = pickle.load(f)

        if artifact.get("feature_names") != FEATURE_NAMES:
            raise ValueError(
                "Saved artifact's feature schema does not match the "
                "current FEATURE_NAMES. Refusing to load to avoid "
                "silent feature-dimension mismatches."
            )

        cfg = artifact["config"]
        self.input_dim = cfg["input_dim"]
        self.hidden_dim = cfg["hidden_dim"]
        self.latent_dim = cfg["latent_dim"]
        self.learning_rate = cfg["learning_rate"]
        self.min_train_samples = cfg["min_train_samples"]
        self.epochs = cfg["epochs"]
        self.batch_size = cfg["batch_size"]
        self.threshold_percentile = cfg["threshold_percentile"]
        self.seed = cfg["seed"]

        self._scaler = _FrozenStandardScaler.from_dict(artifact["scaler"])
        self._model = (
            _NumpyAutoencoder.from_dict(artifact["model"])
            if artifact.get("model") is not None
            else None
        )
        self._threshold = artifact.get("threshold")
        self._training_metadata = artifact.get("training_metadata", {})
        self.status = EngineStatus(artifact["status"])


# ============================================================
# SMOKE TEST (synthetic data only — no IoT-23, no downloads)
# ============================================================

if __name__ == "__main__":
    print("MLEngine smoke test (synthetic data)")
    print("Feature schema:", get_feature_names())
    print("Feature dim:", FEATURE_DIM)

    rng = np.random.default_rng(0)
    engine = MLEngine(input_dim=FEATURE_DIM, min_train_samples=100, epochs=15)

    print(f"Status before training: {engine.get_status()}")

    # Simulate Grace Period: "normal" traffic clustered around a mean.
    normal_center = rng.normal(100, 10, size=FEATURE_DIM)
    for _ in range(300):
        sample = normal_center + rng.normal(0, 5, size=FEATURE_DIM)
        sample = np.clip(sample, 0, None)
        engine.train_packet(sample)

    print(f"Status after buffering: {engine.get_status()}")
    engine.finalize_training()
    print(f"Status after finalize_training: {engine.get_status()}")
    print("Training metadata:", engine.get_training_metadata())

    # Simulate Execution Period: mix of normal + anomalous packets.
    normal_sample = normal_center + rng.normal(0, 5, size=FEATURE_DIM)
    normal_sample = np.clip(normal_sample, 0, None)
    anomalous_sample = normal_center + rng.normal(0, 5, size=FEATURE_DIM) + 500  # big shift
    anomalous_sample = np.clip(anomalous_sample, 0, None)

    print("Normal sample -> anomaly:", engine.predict_packet(normal_sample),
          "score:", round(engine.score_packet(normal_sample), 4))
    print("Anomalous sample -> anomaly:", engine.predict_packet(anomalous_sample),
          "score:", round(engine.score_packet(anomalous_sample), 4))

    # Save/load round trip
    engine.save("ml_engine_smoke_test.pkl")
    engine2 = MLEngine(input_dim=FEATURE_DIM)
    engine2.load("ml_engine_smoke_test.pkl")
    print("Reloaded engine status:", engine2.get_status())
    print("Reloaded score matches original:",
          np.isclose(engine.score_packet(normal_sample), engine2.score_packet(normal_sample)))

    print("Smoke test complete.")
