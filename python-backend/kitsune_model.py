"""Supervised inference wrapper for the downloaded Kitsune classifier."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import warnings

import joblib
import numpy as np
from sklearn.exceptions import InconsistentVersionWarning


class KitsuneModel:
    """Loads a 116-feature Kitsune Random Forest and performs validated inference."""

    def __init__(self, model_path: str | Path) -> None:
        self.model_path = Path(model_path)
        self.model: Any | None = None
        self.load_error: str | None = None

    def load(self) -> bool:
        if not self.model_path.exists():
            self.load_error = f"Model file not found: {self.model_path}"
            self.model = None
            return False

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", InconsistentVersionWarning)
                self.model = joblib.load(self.model_path)
            # The persisted Kaggle estimator uses all available workers. A web
            # request is a single prediction, so avoid creating a worker pool.
            self.model.n_jobs = 1
            self.load_error = None
            return True
        except Exception as error:
            self.model = None
            self.load_error = str(error)
            return False

    @property
    def ready(self) -> bool:
        return self.model is not None

    @property
    def feature_count(self) -> int | None:
        if self.model is None:
            return None
        return int(getattr(self.model, "n_features_in_", 0)) or None

    def predict(self, features: list[float]) -> dict[str, float | str | int]:
        if self.model is None:
            raise RuntimeError(self.load_error or "Kitsune model is not loaded")

        expected = self.feature_count
        if expected is None or len(features) != expected:
            raise ValueError(f"Expected exactly {expected} Kitsune features, received {len(features)}")

        vector = np.asarray(features, dtype=np.float64)
        if not np.isfinite(vector).all():
            raise ValueError("Features must contain only finite numeric values")

        prediction = int(self.model.predict(vector.reshape(1, -1))[0])
        probabilities = self.model.predict_proba(vector.reshape(1, -1))[0]
        classes = [int(value) for value in self.model.classes_]
        attack_probability = float(probabilities[classes.index(1)])

        return {
            "prediction": "attack" if prediction == 1 else "benign",
            "prediction_code": prediction,
            "attack_probability": attack_probability,
            "confidence": max(attack_probability, 1.0 - attack_probability),
        }
