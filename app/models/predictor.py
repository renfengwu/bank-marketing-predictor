"""Model loading and single-sample prediction for the online predictor UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.models.data_loader import FEATURE_COLS, NUMERIC_COLS, load_encoders

MODEL_DIR = Path(__file__).resolve().parents[1] / "ml" / "model"


class Predictor:
    """Wraps the trained model, encoders, and feature metadata for inference."""

    def __init__(self, model_dir: str | Path = MODEL_DIR) -> None:
        self._model_dir = Path(model_dir)
        self._model = None
        self._encoders = None
        self._feature_names: list[str] = []
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        """Whether the model has been successfully loaded."""
        return self._loaded

    @property
    def feature_names(self) -> list[str]:
        """Feature column names the model expects."""
        return list(self._feature_names)

    @property
    def categorical_values(self) -> dict[str, list[str]]:
        """Known categories per categorical feature (from encoder classes)."""
        if not self._encoders:
            return {}
        return {col: list(le.classes_) for col, le in self._encoders.items()}

    def load(self) -> None:
        """Load model, encoders, and feature metadata from disk.

        Raises:
            FileNotFoundError: If model artifacts are missing.
        """
        model_path = self._model_dir / "model.joblib"
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Please run the training script first: python -m app.ml.train"
            )

        self._model = joblib.load(model_path)
        self._encoders = load_encoders(self._model_dir)

        features_path = self._model_dir / "feature_names.json"
        if features_path.exists():
            with open(features_path) as f:
                self._feature_names = json.load(f)
        else:
            self._feature_names = list(FEATURE_COLS)

        self._loaded = True

    def predict(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Run prediction on a single sample.

        Args:
            inputs: Raw feature dict keyed by column name.  Numeric values
                may be numbers or strings convertible to float; categorical
                values must be strings matching the training vocabulary.

        Returns:
            Dict with keys ``subscribe`` (``"yes"`` | ``"no"``) and
            ``probability`` (float in [0, 1]).
        """
        if not self._loaded:
            self.load()

        # Build a one-row DataFrame in the expected column order
        row = {}
        for col in self._feature_names:
            if col not in inputs:
                raise ValueError(f"Missing required feature: {col}")
            row[col] = inputs[col]

        df = pd.DataFrame([row])

        # Encode categoricals
        for col, le in self._encoders.items():
            if col in df.columns:
                val = str(df[col].iloc[0])
                known = set(le.classes_)
                df[col] = le.transform([val])[0] if val in known else -1

        # Ensure numeric cols are float
        for col in self._feature_names:
            if col in NUMERIC_COLS and col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        proba = self._model.predict_proba(df[self._feature_names])[:, 1]
        pred = "yes" if proba[0] >= 0.5 else "no"

        return {"subscribe": pred, "probability": round(float(proba[0]), 4)}


def validate_inputs(
    inputs: dict[str, Any],
    predictor: Predictor,
) -> list[str]:
    """Validate user inputs against the predictor's expected schema.

    Returns:
        List of error messages (empty means valid).
    """
    errors = []

    # Check required features
    for col in predictor.feature_names:
        if col not in inputs or inputs[col] is None or str(inputs[col]).strip() == "":
            errors.append(f"'{col}' 为必填项，请填写。")
            continue

        if col in NUMERIC_COLS:
            try:
                val = float(inputs[col])
                if col == "age" and (val < 18 or val > 100):
                    errors.append(f"年龄应在 18-100 之间，当前值: {val}。")
            except (ValueError, TypeError):
                errors.append(f"'{col}' 应为数字，当前值: {inputs[col]}。")

    return errors
