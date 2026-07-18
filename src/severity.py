from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeverityInfo:
    cve_id: str
    cvss_score: float | str
    severity: str


ATTACK_SEVERITY_MAP: dict[str, SeverityInfo] = {
    "normal": SeverityInfo("N/A", "N/A", "None"),
    "benign": SeverityInfo("N/A", "N/A", "None"),
    "anomaly": SeverityInfo("N/A", "N/A", "Medium"),
    "suspicious": SeverityInfo("N/A", "N/A", "Medium"),
    "dos": SeverityInfo("N/A", 7.5, "High"),
    "ddos": SeverityInfo("N/A", 8.6, "High"),
    "port_scan": SeverityInfo("N/A", 5.3, "Medium"),
    "brute_force": SeverityInfo("N/A", 8.1, "High"),
    "mirai": SeverityInfo("CVE-2017-17215", 8.8, "High"),
}


def cvss_to_severity(score: float | int | str) -> str:
    if score == "N/A":
        return "Unknown"
    value = float(score)
    if value == 0:
        return "None"
    if value < 4.0:
        return "Low"
    if value < 7.0:
        return "Medium"
    if value < 9.0:
        return "High"
    return "Critical"


def severity_for_prediction(prediction: str) -> SeverityInfo:
    key = prediction.strip().lower().replace(" ", "_")
    return ATTACK_SEVERITY_MAP.get(key, SeverityInfo("N/A", "N/A", "Unknown"))
