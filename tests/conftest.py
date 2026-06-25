"""Shared pytest fixtures for the bank marketing predictor project."""

import pandas as pd
import pytest


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Small synthetic dataset matching the bank marketing schema."""
    return pd.DataFrame(
        {
            "age": [51, 50, 48, 26, 35],
            "job": ["admin.", "services", "blue-collar", "entrepreneur", "technician"],
            "marital": ["divorced", "married", "divorced", "single", "married"],
            "education": [
                "professional.course",
                "high.school",
                "basic.9y",
                "high.school",
                "university.degree",
            ],
            "default": ["no", "unknown", "no", "yes", "no"],
            "housing": ["yes", "yes", "no", "yes", "no"],
            "loan": ["yes", "no", "no", "yes", "no"],
            "contact": ["cellular", "cellular", "cellular", "cellular", "telephone"],
            "month": ["aug", "may", "apr", "aug", "jun"],
            "day_of_week": ["mon", "mon", "wed", "fri", "tue"],
            "duration": [4621, 4715, 171, 359, 1200],
            "campaign": [1, 1, 0, 26, 3],
            "pdays": [112, 412, 1027, 998, 999],
            "previous": [2, 2, 1, 0, 0],
            "poutcome": ["failure", "nonexistent", "failure", "nonexistent", "success"],
            "emp_var_rate": [1.4, -1.8, -1.8, 1.4, -0.1],
            "cons_price_index": [90.81, 96.33, 96.33, 97.08, 93.20],
            "cons_conf_index": [-35.53, -40.58, -44.74, -35.55, -42.0],
            "lending_rate3m": [0.69, 4.05, 1.50, 5.11, 3.20],
            "nr_employed": [5219.74, 4974.79, 5022.61, 5222.87, 5090.0],
            "subscribe": ["no", "yes", "no", "yes", "no"],
        }
    )
