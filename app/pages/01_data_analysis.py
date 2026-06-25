"""Data analysis interactive page for bank marketing data exploration."""

from pathlib import Path

import pandas as pd
import streamlit as st

from app.models.data_loader import CATEGORICAL_COLS, NUMERIC_COLS, load_data
from app.models.visualizer import (
    build_boxplot,
    build_category_bar,
    build_correlation_heatmap,
    build_distribution,
    data_overview,
)

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "train.csv"

st.set_page_config(page_title="数据分析", page_icon="📊", layout="wide")

st.title("📊 数据分析")
st.markdown("交互式探索银行营销数据的特征分布与认购行为影响因素。")


@st.cache_data(ttl=600)
def _load_data(path: str) -> pd.DataFrame:
    return load_data(path)


# Load data
data_file = str(DATA_PATH)
if not Path(data_file).exists():
    st.error(f"数据文件未找到: {data_file}")
    st.stop()

df = _load_data(data_file)
st.sidebar.success(f"已加载 {len(df):,} 条记录")

# ---- Sidebar filters ----
st.sidebar.header("筛选条件")

# Category filters
filtered_df = df.copy()
for col in CATEGORICAL_COLS:
    if col in filtered_df.columns:
        options = sorted(filtered_df[col].dropna().unique().tolist())
        selected = st.sidebar.multiselect(f"{col}", options, default=options)
        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]

st.sidebar.caption(
    f"筛选后: {len(filtered_df):,} / {len(df):,} 条（{len(filtered_df) / len(df) * 100:.1f}%）"
)

# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs(
    ["📋 数据概览", "📈 数值特征分布", "📊 类别特征分析", "🔗 相关性热力图"]
)

with tab1:
    st.subheader("数据概览")

    overview = data_overview(filtered_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("总行数", f"{overview['total_rows']:,}")
    col2.metric("特征列数", len(overview["columns"]) - 1)
    yes_pct = filtered_df["subscribe"].value_counts(normalize=True).get("yes", 0) * 100
    col3.metric("认购率", f"{yes_pct:.1f}%")

    st.markdown("**字段信息**")
    info_rows = []
    for col in overview["columns"]:
        info_rows.append(
            {
                "字段": col,
                "类型": overview["dtypes"].get(col, "?"),
                "缺失值": overview["missing"].get(col, 0),
                "唯一值数": overview["nunique"].get(col, 0),
            }
        )
    st.dataframe(pd.DataFrame(info_rows), use_container_width=True, hide_index=True)

    st.markdown("**数据预览（前 100 行）**")
    st.dataframe(filtered_df.head(100), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("数值特征分布")

    numeric_feature = st.selectbox(
        "选择数值特征",
        NUMERIC_COLS,
        key="dist_num_feature",
    )
    chart_type = st.radio(
        "图表类型",
        ["直方图（按认购分组）", "箱线图（按认购分组）"],
        horizontal=True,
        key="num_chart_type",
    )

    if chart_type.startswith("直方图"):
        fig = build_distribution(filtered_df, numeric_feature)
    else:
        fig = build_boxplot(filtered_df, numeric_feature)
    st.plotly_chart(fig, use_container_width=True)

    # Quick stats
    st.markdown(f"**{numeric_feature} 统计**")
    col1, col2, col3, col4 = st.columns(4)
    s = filtered_df[numeric_feature]
    col1.metric("均值", f"{s.mean():.2f}")
    col2.metric("中位数", f"{s.median():.2f}")
    col3.metric("标准差", f"{s.std():.2f}")
    col4.metric("缺失数", int(s.isna().sum()))

with tab3:
    st.subheader("类别特征分析")

    cat_feature = st.selectbox(
        "选择类别特征",
        CATEGORICAL_COLS,
        key="cat_feature",
    )
    fig = build_category_bar(filtered_df, cat_feature)
    st.plotly_chart(fig, use_container_width=True)

    # Data table
    counts = (
        filtered_df.groupby(cat_feature)["subscribe"]
        .agg(["count", lambda s: (s == "yes").mean()])
        .round(4)
    )
    counts.columns = ["数量", "认购率"]
    st.dataframe(counts, use_container_width=True)

with tab4:
    st.subheader("相关性热力图")

    # Only use numeric cols that exist in the data
    available_num = [c for c in NUMERIC_COLS if c in filtered_df.columns]
    fig = build_correlation_heatmap(filtered_df, available_num)
    st.plotly_chart(fig, use_container_width=True)

    st.caption("颜色越红表示正相关越强，越蓝表示负相关越强。关键观察：与认购行为相关性最强的特征。")
