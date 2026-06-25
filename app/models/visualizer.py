"""Plotly chart builders for the data analysis page."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_distribution(
    df: pd.DataFrame,
    feature: str,
    target: str = "subscribe",
) -> go.Figure:
    """Histogram of numeric *feature* coloured by *target*."""
    fig = px.histogram(
        df,
        x=feature,
        color=target,
        barmode="overlay",
        opacity=0.7,
        marginal="box",
        title=f"Distribution of {feature} by Subscription",
    )
    return fig


def build_boxplot(
    df: pd.DataFrame,
    feature: str,
    target: str = "subscribe",
) -> go.Figure:
    """Box plot of numeric *feature* grouped by *target*."""
    fig = px.box(
        df,
        x=target,
        y=feature,
        color=target,
        title=f"{feature} by Subscription",
    )
    return fig


def build_category_bar(
    df: pd.DataFrame,
    feature: str,
    target: str = "subscribe",
) -> go.Figure:
    """Bar chart showing proportion of ``yes`` per category of *feature*.

    X-axis: category values.  Y-axis: subscription rate (0–1).
    A horizontal dashed line marks the global average subscription rate.
    """
    rates = (
        df.groupby(feature)[target]
        .apply(lambda s: (s == "yes").mean())
        .sort_values(ascending=False)
    )

    global_rate = (df[target] == "yes").mean()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=rates.index.astype(str),
            y=rates.values,
            marker_color="steelblue",
            name="Subscription Rate",
        )
    )
    fig.add_hline(
        y=global_rate,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Global avg: {global_rate:.1%}",
    )
    fig.update_layout(
        title=f"Subscription Rate by {feature}",
        xaxis_title=feature,
        yaxis_title="Subscription Rate",
        yaxis=dict(tickformat=".0%"),
        showlegend=False,
    )
    return fig


def build_correlation_heatmap(
    df: pd.DataFrame,
    numeric_cols: list[str],
) -> go.Figure:
    """Correlation heatmap of *numeric_cols*."""
    corr = df[numeric_cols].corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Heatmap (Numeric Features)",
    )
    return fig


def data_overview(df: pd.DataFrame) -> dict:
    """Return a dict of summary statistics for the data overview table."""
    total = len(df)
    missing = df.isna().sum().to_dict()
    dtypes = {col: str(dt) for col, dt in df.dtypes.items()}
    nunique = df.nunique().to_dict()
    return {
        "total_rows": total,
        "columns": list(df.columns),
        "dtypes": dtypes,
        "missing": missing,
        "nunique": nunique,
    }
