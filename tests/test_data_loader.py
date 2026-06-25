"""Tests for app.models.data_loader."""

import pandas as pd

from app.models.data_loader import (
    CATEGORICAL_COLS,
    NUMERIC_COLS,
    TARGET_COL,
    load_data,
    load_encoders,
    preprocess,
    save_encoders,
)


class TestLoadData:
    def test_loads_csv_correctly(self, tmp_path):
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("a,b\n1,2\n3,4\n")
        df = load_data(str(csv_path))
        assert len(df) == 2
        assert list(df.columns) == ["a", "b"]

    def test_loads_bank_csv_structure(self, tmp_path, sample_data):
        csv_path = tmp_path / "bank.csv"
        sample_data.to_csv(csv_path, index=False)
        df = load_data(str(csv_path))
        assert TARGET_COL in df.columns
        assert len(df) == len(sample_data)


class TestPreprocess:
    def test_returns_X_y_encoders(self, sample_data):
        X, y, encoders = preprocess(sample_data)
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert isinstance(encoders, dict)
        assert len(X) == len(sample_data)
        assert y.dtype in ("int64", "int32")

    def test_target_encodes_yes_to_1_no_to_0(self, sample_data):
        _, y, _ = preprocess(sample_data)
        unique = set(y.unique())
        assert unique <= {0, 1}

    def test_numeric_cols_are_all_present(self, sample_data):
        X, _, _ = preprocess(sample_data)
        for col in NUMERIC_COLS:
            assert col in X.columns

    def test_categorical_cols_are_encoded(self, sample_data):
        X, _, _ = preprocess(sample_data)
        for col in CATEGORICAL_COLS:
            assert col in X.columns
            assert X[col].dtype in ("int64", "int32")

    def test_rows_with_missing_target_are_dropped(self, sample_data):
        df = sample_data.copy()
        df.loc[0, TARGET_COL] = None
        X, _, _ = preprocess(df)
        assert len(X) == len(sample_data) - 1

    def test_missing_numeric_filled_with_median(self):
        df = pd.DataFrame(
            {
                "age": [30, None, 40],
                "job": ["admin.", "blue-collar", "technician"],
                "subscribe": ["yes", "no", "no"],
                **{col: [0] * 3 for col in NUMERIC_COLS if col != "age"},
                **{col: ["unknown"] * 3 for col in CATEGORICAL_COLS if col != "job"},
            }
        )
        X, _, _ = preprocess(df)
        assert not X["age"].isna().any()

    def test_reuse_encoders_on_new_data(self, sample_data):
        X1, _, encoders = preprocess(sample_data)
        X2, _, _ = preprocess(sample_data, encoders=encoders)
        # same data should produce identical encoding
        pd.testing.assert_frame_equal(X1, X2)

    def test_unseen_category_maps_to_neg1(self, sample_data):
        _, _, encoders = preprocess(sample_data)
        new_row = sample_data.iloc[[0]].copy()
        new_row["job"] = "never-seen-before-job"
        X, _, _ = preprocess(new_row, encoders=encoders)
        assert X["job"].iloc[0] == -1


class TestSaveLoadEncoders:
    def test_roundtrip(self, tmp_path, sample_data):
        _, _, encoders = preprocess(sample_data)
        save_encoders(encoders, tmp_path)
        loaded = load_encoders(tmp_path)
        assert set(loaded.keys()) == set(encoders.keys())
        for col in encoders:
            assert list(loaded[col].classes_) == list(encoders[col].classes_)
