"""Tests for app.models.predictor."""

import json
from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from app.models.predictor import Predictor, validate_inputs


def _build_minimal_model_dir(path: Path) -> None:
    """Create a minimal trained-model directory for testing."""
    path.mkdir(parents=True, exist_ok=True)

    # Dummy features
    features = ["age", "job"]
    np.random.seed(0)
    X = np.random.randn(100, 2)
    y = np.random.randint(0, 2, 100)

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)

    joblib.dump(model, path / "model.joblib")

    le = LabelEncoder()
    le.fit(["admin.", "technician", "blue-collar"])
    joblib.dump({"job": le}, path / "encoders.joblib")

    with open(path / "feature_names.json", "w") as f:
        json.dump(features, f)


class TestPredictorLoad:
    def test_raises_if_model_missing(self, tmp_path):
        p = Predictor(model_dir=tmp_path / "nope")
        with pytest.raises(FileNotFoundError):
            p.load()

    def test_loads_successfully(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        assert p.is_loaded
        assert len(p.feature_names) > 0

    def test_categorical_values(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        assert "job" in p.categorical_values
        assert "admin." in p.categorical_values["job"]


class TestPredictorPredict:
    def test_predict_returns_subscribe_and_probability(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        result = p.predict({"age": 35, "job": "admin."})
        assert "subscribe" in result
        assert result["subscribe"] in ("yes", "no")
        assert "probability" in result
        assert 0.0 <= result["probability"] <= 1.0

    def test_predict_missing_feature_raises(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        with pytest.raises(ValueError, match="age"):
            p.predict({"job": "admin."})

    def test_predict_unseen_category_does_not_crash(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        result = p.predict({"age": 35, "job": "never-seen-before"})
        assert "subscribe" in result


class TestValidateInputs:
    def test_empty_errors_on_valid(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        errors = validate_inputs({"age": 35, "job": "admin."}, p)
        assert len(errors) == 0

    def test_returns_errors_for_missing_field(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        errors = validate_inputs({"age": 35}, p)
        assert len(errors) > 0

    def test_returns_errors_for_bad_age(self, tmp_path):
        _build_minimal_model_dir(tmp_path)
        p = Predictor(model_dir=tmp_path)
        p.load()
        errors = validate_inputs({"age": -5, "job": "admin."}, p)
        assert len(errors) > 0
