"""Data loading, preprocessing, and encoding for bank marketing data."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

#: Numeric feature columns in the dataset.
NUMERIC_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

#: Categorical feature columns that require encoding.
CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

#: Target column name.
TARGET_COL = "subscribe"

#: All feature columns (everything except target).
FEATURE_COLS = NUMERIC_COLS + CATEGORICAL_COLS


def load_data(file_path: str | Path) -> pd.DataFrame:
    """Load raw CSV data from *file_path*.

    Returns:
        DataFrame with all columns including ``subscribe``.
    """
    return pd.read_csv(file_path)


def preprocess(
    df: pd.DataFrame,
    encoders: dict[str, LabelEncoder] | None = None,
) -> tuple[pd.DataFrame, pd.Series, dict[str, LabelEncoder]]:
    """Preprocess raw DataFrame into feature matrix X and target y.

    Steps:
    1. Drop rows where target is missing.
    2. Fill missing numeric values with median.
    3. Fill missing categorical values with ``"unknown"``.
    4. Label-encode categorical columns.
    5. Return (X, y, encoders).

    Args:
        df: Raw DataFrame with all columns.
        encoders: Pre-fitted encoders (for test/transform path). If ``None``,
            new encoders are fitted.

    Returns:
        (X, y, encoders) tuple.
    """
    df = df.copy()
    df = df.dropna(subset=[TARGET_COL])

    y = df[TARGET_COL].map({"yes": 1, "no": 0})

    X = df[FEATURE_COLS].copy()

    # Fill missing values
    for col in NUMERIC_COLS:
        if col in X.columns:
            X[col] = X[col].fillna(X[col].median())

    for col in CATEGORICAL_COLS:
        if col in X.columns:
            X[col] = X[col].fillna("unknown")

    # Encode categoricals
    if encoders is None:
        encoders = {}
        for col in CATEGORICAL_COLS:
            if col in X.columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                encoders[col] = le
    else:
        for col, le in encoders.items():
            if col in X.columns:
                # Map unseen values to a sentinel (-1)
                known = set(le.classes_)
                X[col] = (
                    X[col].astype(str).apply(lambda v: le.transform([v])[0] if v in known else -1)
                )

    return X, y, encoders


def save_encoders(encoders: dict[str, LabelEncoder], dir_path: str | Path) -> None:
    """Persist label encoders to *dir_path* as ``encoders.joblib``."""
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    joblib.dump(encoders, dir_path / "encoders.joblib")


def load_encoders(dir_path: str | Path) -> dict[str, LabelEncoder]:
    """Load persisted label encoders from *dir_path*."""
    return joblib.load(Path(dir_path) / "encoders.joblib")
