from __future__ import annotations

import csv
from pathlib import Path

from fastapi import APIRouter


router = APIRouter()
LOG_PATH = Path("logs/attacks.csv")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/alerts")
def alerts(limit: int = 50) -> dict:
    if not LOG_PATH.exists():
        return {"alerts": []}

    with LOG_PATH.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    return {"alerts": rows[-limit:]}
