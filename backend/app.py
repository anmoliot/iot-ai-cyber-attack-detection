from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from backend.routes import router


app = FastAPI(title="AI Based Cyber Attack Detection API")
app.include_router(router)


@app.get("/")
def root() -> dict:
    return {
        "project": "AI Based Cyber Attack Detection",
        "status": "running",
        "logs": str(Path("logs/attacks.csv")),
    }
