"""
database.py
============================================================
SQLAlchemy database setup for SentinelAI.

Uses SQLite by default (zero-config, file-based).
Set DATABASE_URL env var to switch to PostgreSQL:
  DATABASE_URL=postgresql://user:pass@host/db

Tables:
  - alerts       : Persisted anomaly alerts (replaces in-memory list)
  - training_runs: Historical record of each model training session
"""

import os
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Index,
    create_engine, text,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./sentinel.db"
)

# SQLite-specific: allow multi-thread access
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class AlertRecord(Base):
    """Persistent storage for anomaly alerts."""
    __tablename__ = "alerts"

    id             = Column(String(40),  primary_key=True)
    timestamp      = Column(Float,       nullable=False, index=True)
    created_at     = Column(DateTime,    default=datetime.utcnow)
    src_ip         = Column(String(45),  nullable=False, index=True)
    dst_ip         = Column(String(45),  nullable=False)
    protocol       = Column(String(10),  nullable=False, index=True)
    anomaly_score  = Column(Float,       nullable=False)
    threshold      = Column(Float,       nullable=False)
    severity       = Column(String(10),  nullable=False, index=True)
    attack_type    = Column(String(30),  nullable=True)
    attack_label   = Column(String(60),  nullable=True)
    attack_confidence = Column(Float,    nullable=True)

    __table_args__ = (
        Index("ix_alerts_ts_severity", "timestamp", "severity"),
    )

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "type":              "cyber_attack_alert",
            "timestamp":         self.timestamp,
            "src_ip":            self.src_ip,
            "dst_ip":            self.dst_ip,
            "protocol":          self.protocol,
            "anomaly_score":     round(self.anomaly_score, 4),
            "threshold":         round(self.threshold, 4),
            "severity":          self.severity,
            "attack_type":       self.attack_type or "unknown",
            "attack_label":      self.attack_label or "Unknown Anomaly",
            "attack_confidence": round(self.attack_confidence or 0.0, 2),
        }


class TrainingRun(Base):
    """Historical record of each model training session."""
    __tablename__ = "training_runs"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    trained_at          = Column(DateTime, default=datetime.utcnow)
    n_samples           = Column(Integer)
    final_loss          = Column(Float)
    threshold_percentile = Column(Float)
    threshold_value     = Column(Float)
    model_version       = Column(String(20))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Create all tables if they don't exist. Safe to call on every startup."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yields a DB session, always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_ping() -> bool:
    """Health-check: returns True if DB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
