from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALERT_FIELDS = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "protocol",
    "prediction",
    "confidence",
    "cve_id",
    "cvss_score",
    "severity",
    "action",
    "details",
]


@dataclass
class AlertRecord:
    src_ip: str
    dst_ip: str
    src_port: int | str
    dst_port: int | str
    protocol: str | int
    prediction: str
    confidence: float | str = "N/A"
    cve_id: str = "N/A"
    cvss_score: float | str = "N/A"
    severity: str = "Unknown"
    action: str = "Logged"
    details: str = ""
    timestamp: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        if not row["timestamp"]:
            row["timestamp"] = datetime.now(timezone.utc).isoformat()
        return {field: row.get(field, "") for field in ALERT_FIELDS}


class CSVAlertLogger:
    def __init__(self, log_path: str | Path = "logs/attacks.csv") -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_header()

    def _ensure_header(self) -> None:
        if self.log_path.exists() and self.log_path.stat().st_size > 0:
            return
        with self.log_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ALERT_FIELDS)
            writer.writeheader()

    def write(self, record: AlertRecord) -> None:
        with self.log_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=ALERT_FIELDS)
            writer.writerow(record.to_row())
