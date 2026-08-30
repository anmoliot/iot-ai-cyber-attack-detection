"""Supervised inference wrapper for the Edge-IIoT attack-category pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import warnings

import joblib
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning


class EdgeIIoTAttackTypeModel:
    """Loads the named-feature Edge-IIoT multiclass classifier pipeline."""

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

            classifier = getattr(self.model, "named_steps", {}).get("classifier")
            if classifier is not None and hasattr(classifier, "n_jobs"):
                classifier.n_jobs = 1

            if not self.feature_names:
                raise ValueError("Loaded Edge-IIoT model does not expose its feature names")
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
    def feature_names(self) -> list[str]:
        if self.model is None:
            return []
        return [str(name) for name in getattr(self.model, "feature_names_in_", [])]

    @property
    def feature_count(self) -> int:
        return len(self.feature_names)

    @property
    def classes(self) -> list[str]:
        if self.model is None:
            return []
        return [str(value) for value in getattr(self.model, "classes_", [])]

    def predict(self, features: dict[str, Any]) -> dict[str, float | str | bool]:
        if self.model is None:
            raise RuntimeError(self.load_error or "Edge-IIoT attack-type model is not loaded")

        expected = self.feature_names
        missing = [name for name in expected if name not in features]
        if missing:
            raise ValueError(f"Missing {len(missing)} required Edge-IIoT features: {missing}")

        row = pd.DataFrame([{name: features[name] for name in expected}], columns=expected)
        attack_type = str(self.model.predict(row)[0])
        probabilities = self.model.predict_proba(row)[0]
        confidence = float(probabilities[self.classes.index(attack_type)])

        return {
            "prediction": "benign" if attack_type == "Normal" else "attack",
            "attack_type": attack_type,
            "confidence": confidence,
            "is_attack": attack_type != "Normal",
        }
