"""Offline training pipeline for the bank marketing subscription model.

Usage::

    python -m app.ml.train          # default: RandomForest
    python -m app.ml.train --lgbm   # try LightGBM if installed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedShuffleSplit

# Allow running this module from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.models.data_loader import FEATURE_COLS, load_data, preprocess, save_encoders

MODEL_DIR = Path(__file__).resolve().parent / "model"


def _get_model(use_lgbm: bool = False):
    """Return a classifier instance.

    Prefers LightGBM when *use_lgbm* is True and the library is installed;
    otherwise falls back to RandomForest.
    """
    if use_lgbm:
        try:
            import lightgbm as lgb  # noqa: F811

            return lgb.LGBMClassifier(
                n_estimators=200,
                max_depth=8,
                random_state=42,
                verbose=-1,
            )
        except ImportError:
            print("[WARN] LightGBM not installed, falling back to RandomForest.")
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )


def train(
    data_path: str | Path = "data/train.csv",
    use_lgbm: bool = False,
    check_auc: float | None = None,
) -> dict[str, Any]:
    """Run the full training pipeline and return an evaluation dict.

    Args:
        data_path: Path to the training CSV.
        use_lgbm: If True, attempt to use LightGBM.
        check_auc: If set, assert that validation AUC >= this value.
            Used as a CI quality gate.

    Returns:
        Dict with keys: ``model_type``, ``auc``, ``accuracy``, ``precision``,
        ``recall``, ``f1``, ``train_samples``, ``val_samples``.
    """
    print(f"Loading data from {data_path} ...")
    df = load_data(data_path)
    print(f"  loaded {len(df)} rows")

    X, y, encoders = preprocess(df)

    # Train / validation split (stratified, single split)
    splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, val_idx = next(splitter.split(X, y))
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    print(f"  train: {len(X_train)}, val: {len(X_val)}")

    # Fit
    model = _get_model(use_lgbm)
    model_type = type(model).__name__
    print(f"Training {model_type} ...")
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]

    metrics = {
        "model_type": model_type,
        "auc": round(roc_auc_score(y_val, y_proba), 4),
        "accuracy": round(accuracy_score(y_val, y_pred), 4),
        "precision": round(precision_score(y_val, y_pred), 4),
        "recall": round(recall_score(y_val, y_pred), 4),
        "f1": round(f1_score(y_val, y_pred), 4),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
    }

    print("\nEvaluation:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    # Save artifacts
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_DIR / "model.joblib")
    save_encoders(encoders, MODEL_DIR)
    with open(MODEL_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    with open(MODEL_DIR / "feature_names.json", "w") as f:
        json.dump(FEATURE_COLS, f, indent=2)

    print(f"\nModel artifacts saved to {MODEL_DIR}")

    # Optional CI gate
    if check_auc is not None and metrics["auc"] < check_auc:
        raise SystemExit(f"AUC {metrics['auc']} < required {check_auc}. Failing CI gate.")

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train bank marketing model.")
    parser.add_argument("--data", default="data/train.csv", help="Path to training CSV")
    parser.add_argument("--lgbm", action="store_true", help="Use LightGBM")
    parser.add_argument(
        "--check-auc", type=float, default=None, help="Fail if validation AUC < this value"
    )
    args = parser.parse_args()
    train(data_path=args.data, use_lgbm=args.lgbm, check_auc=args.check_auc)


if __name__ == "__main__":
    main()
