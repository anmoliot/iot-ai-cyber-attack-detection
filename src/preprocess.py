from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np


class Preprocessor:
    def __init__(self, scaler_path: str | Path = "models/scaler.pkl") -> None:
        self.scaler_path = Path(scaler_path)
        self.scaler: Any | None = None
        if self.scaler_path.exists():
            self.scaler = joblib.load(self.scaler_path)

    def transform_one(self, feature_vector: list[float]) -> np.ndarray:
        row = np.array([feature_vector], dtype=float)
        if self.scaler is None:
            return row
        return self.scaler.transform(row)
