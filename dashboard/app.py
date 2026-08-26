from __future__ import annotations

import csv
from pathlib import Path

from flask import Flask, render_template


app = Flask(__name__)
LOG_PATH = Path("logs/attacks.csv")


def read_alerts(limit: int = 100) -> list[dict]:
    if not LOG_PATH.exists():
        return []
    with LOG_PATH.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return rows[-limit:]


@app.route("/")
def index():
    alerts = read_alerts()
    attack_count = sum(1 for item in alerts if item.get("severity") not in {"None", "", "Unknown"})
    return render_template(
        "index.html",
        alerts=list(reversed(alerts)),
        total=len(alerts),
        attack_count=attack_count,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
