"""Online prediction page — point-and-click form for subscription prediction."""

import streamlit as st

from app.models.predictor import Predictor, validate_inputs

st.set_page_config(page_title="在线预测", page_icon="🤖", layout="wide")

st.title("🤖 在线预测")
st.markdown("通过点选表单输入客户特征，实时预测该客户是否会认购定期存款。")


# ---- Load model ----
@st.cache_resource
def _get_predictor() -> Predictor | None:
    p = Predictor()
    try:
        p.load()
        return p
    except FileNotFoundError:
        return None


predictor = _get_predictor()

if predictor is None:
    st.warning("⚠️ 模型尚未训练，预测功能不可用。请先运行训练脚本：`python -m app.ml.train`")
    st.stop()

st.success(f"模型已加载（{predictor.feature_names.__len__()} 个特征）")

# ---- Input form ----
st.subheader("客户特征输入")

with st.form("prediction_form"):
    inputs: dict = {}

    # Numeric features
    st.markdown("**数值特征**")
    cols = st.columns(4)
    numeric_defaults = {
        "age": (18, 100, 40),
        "duration": (0, 5000, 300),
        "campaign": (0, 50, 2),
        "pdays": (0, 999, 999),
        "previous": (0, 10, 0),
        "emp_var_rate": (-5, 5, 0),
        "cons_price_index": (85, 100, 93),
        "cons_conf_index": (-60, -20, -40),
        "lending_rate3m": (0, 10, 3),
        "nr_employed": (4500, 5500, 5100),
    }
    for i, col_name in enumerate([c for c in predictor.feature_names if c in numeric_defaults]):
        mn, mx, default = numeric_defaults.get(col_name, (0, 100, 0))
        with cols[i % 4]:
            inputs[col_name] = st.number_input(
                col_name,
                min_value=float(mn),
                max_value=float(mx),
                value=float(default),
                step=0.1 if isinstance(default, float) else 1.0,
                format="%.1f" if isinstance(default, float) else "%d",
            )

    # Categorical features
    st.markdown("**类别特征**")
    cats = predictor.categorical_values
    cols = st.columns(4)
    for i, col_name in enumerate([c for c in predictor.feature_names if c in cats]):
        options = cats[col_name]
        with cols[i % 4]:
            short_label = col_name if len(col_name) <= 15 else f"{col_name[:12]}..."
            inputs[col_name] = st.selectbox(
                short_label,
                options,
                help=f"字段: {col_name}",
            )

    submitted = st.form_submit_button("🔮 预测", type="primary", use_container_width=True)

# ---- Results ----
if submitted:
    errors = validate_inputs(inputs, predictor)
    if errors:
        st.error("输入校验失败，请修正以下问题：")
        for e in errors:
            st.warning(f"• {e}")
    else:
        result = predictor.predict(inputs)
        is_yes = result["subscribe"] == "yes"
        proba = result["probability"]

        st.markdown("---")
        st.subheader("预测结果")

        col1, col2 = st.columns(2)

        with col1:
            if is_yes:
                st.success(f"### ✅ 会认购（概率: {proba:.1%}）")
            else:
                st.error(f"### ❌ 不会认购（概率: {proba:.1%}）")

        with col2:
            st.metric("认购概率", f"{proba:.1%}")
            st.progress(proba)

        st.caption(
            f"预测依据: 模型根据 {predictor.feature_names.__len__()} 个特征综合判断。"
            f"概率 ≥ 50% 判定为「会认购」。"
        )

        # Show input summary
        with st.expander("查看本次输入详情"):
            st.json(inputs)
