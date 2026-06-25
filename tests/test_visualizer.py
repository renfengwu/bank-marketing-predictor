"""Tests for app.models.visualizer."""

import pandas as pd
import plotly.graph_objects as go

from app.models.visualizer import (
    build_boxplot,
    build_category_bar,
    build_correlation_heatmap,
    build_distribution,
    data_overview,
)


def _make_toy_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [30, 45, 28, 52, 38],
            "income": [40000, 80000, 35000, 95000, 60000],
            "job": ["admin.", "technician", "admin.", "management", "technician"],
            "subscribe": ["no", "yes", "no", "yes", "no"],
        }
    )


class TestBuildDistribution:
    def test_returns_figure(self):
        df = _make_toy_df()
        fig = build_distribution(df, "age")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_title_contains_feature_name(self):
        df = _make_toy_df()
        fig = build_distribution(df, "age")
        assert "age" in fig.layout.title.text


class TestBuildBoxplot:
    def test_returns_figure(self):
        df = _make_toy_df()
        fig = build_boxplot(df, "age")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0


class TestBuildCategoryBar:
    def test_returns_figure(self):
        df = _make_toy_df()
        fig = build_category_bar(df, "job")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_bar_has_correct_x_values(self):
        df = _make_toy_df()
        fig = build_category_bar(df, "job")
        x_values = fig.data[0].x
        assert len(x_values) == df["job"].nunique()


class TestBuildCorrelationHeatmap:
    def test_returns_figure(self):
        df = _make_toy_df()
        fig = build_correlation_heatmap(df, ["age", "income"])
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0


class TestDataOverview:
    def test_returns_keys(self):
        df = _make_toy_df()
        overview = data_overview(df)
        assert "total_rows" in overview
        assert overview["total_rows"] == len(df)
        assert "columns" in overview
        assert "dtypes" in overview
        assert "missing" in overview
        assert "nunique" in overview
