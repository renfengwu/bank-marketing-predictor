"""Health / smoke tests for the Streamlit application."""


def test_core_modules_import():
    """Verify all core (non-UI) modules import without error."""
    from app.models.data_loader import load_data, preprocess  # noqa: F401
    from app.models.predictor import Predictor  # noqa: F401
    from app.models.visualizer import data_overview  # noqa: F401

    # Streamlit import is skipped here because Python 3.13 + starlette
    # compatibility is handled by the Docker image (python:3.11-slim).


def test_data_files_exist():
    """Verify the data/ directory contains CSV files (local dev only)."""
    from pathlib import Path

    import pytest

    data_dir = Path(__file__).resolve().parents[1] / "data"
    if not data_dir.is_dir():
        pytest.skip("data/ directory not present (CI or fresh checkout)")
    csvs = list(data_dir.glob("*.csv"))
    assert len(csvs) >= 1, f"No CSV files found in {data_dir}"
