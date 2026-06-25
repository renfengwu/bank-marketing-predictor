"""Tests for app.ml.train."""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from app.ml.train import train


def _write_training_csv(path: Path, n: int = 200) -> None:
    """Generate a minimal synthetic training CSV at *path*.

    200 rows ensures a statistically plausible 80/20 split for AUC computation.
    """
    np.random.seed(42)
    data = {
        "age": np.random.randint(18, 70, n),
        "job": np.random.choice(["admin.", "technician", "blue-collar"], n),
        "marital": np.random.choice(["married", "single", "divorced"], n),
        "education": np.random.choice(["high.school", "university.degree", "basic.9y"], n),
        "default": np.random.choice(["no", "yes", "unknown"], n),
        "housing": np.random.choice(["yes", "no"], n),
        "loan": np.random.choice(["no", "yes"], n),
        "contact": np.random.choice(["cellular", "telephone"], n),
        "month": np.random.choice(["may", "jun", "jul", "aug"], n),
        "day_of_week": np.random.choice(["mon", "tue", "wed", "thu", "fri"], n),
        "duration": np.random.randint(0, 5000, n),
        "campaign": np.random.randint(1, 30, n),
        "pdays": np.random.choice([999, 0, 1, 5, 10, 100], n),
        "previous": np.random.randint(0, 5, n),
        "poutcome": np.random.choice(["failure", "nonexistent", "success"], n),
        "emp_var_rate": np.random.uniform(-3, 3, n),
        "cons_price_index": np.random.uniform(90, 100, n),
        "cons_conf_index": np.random.uniform(-50, -30, n),
        "lending_rate3m": np.random.uniform(0, 6, n),
        "nr_employed": np.random.uniform(4900, 5300, n),
        "subscribe": np.random.choice(["yes", "no"], n, p=[0.15, 0.85]),
    }
    pd.DataFrame(data).to_csv(path, index=False)


class TestTrain:
    def test_train_returns_metrics(self, tmp_path):
        csv_path = tmp_path / "train.csv"
        _write_training_csv(csv_path, n=200)
        # Patch MODEL_DIR so artifacts go to tmp_path not the real repo
        with patch("app.ml.train.MODEL_DIR", tmp_path / "model"):
            metrics = train(data_path=str(csv_path), use_lgbm=False)
        assert "auc" in metrics
        assert "accuracy" in metrics
        assert "f1" in metrics
        assert 0.0 <= metrics["auc"] <= 1.0

    def test_saves_model_artifacts(self, tmp_path):
        csv_path = tmp_path / "train.csv"
        _write_training_csv(csv_path, n=200)
        model_dir = tmp_path / "model"
        with patch("app.ml.train.MODEL_DIR", model_dir):
            train(data_path=str(csv_path), use_lgbm=False)
        assert (model_dir / "model.joblib").exists()
        assert (model_dir / "encoders.joblib").exists()
        assert (model_dir / "metrics.json").exists()
        assert (model_dir / "feature_names.json").exists()

    def test_check_auc_fails_on_low_threshold(self, tmp_path):
        csv_path = tmp_path / "train.csv"
        _write_training_csv(csv_path, n=200)
        with patch("app.ml.train.MODEL_DIR", tmp_path / "model"):
            # AUC of random data won't reach 0.99
            with np.testing.assert_raises(SystemExit):
                train(data_path=str(csv_path), use_lgbm=False, check_auc=0.99)

    def test_uses_random_forest_by_default(self, tmp_path):
        csv_path = tmp_path / "train.csv"
        _write_training_csv(csv_path, n=200)
        with patch("app.ml.train.MODEL_DIR", tmp_path / "model"):
            metrics = train(data_path=str(csv_path), use_lgbm=False)
        assert "RandomForest" in metrics["model_type"]
