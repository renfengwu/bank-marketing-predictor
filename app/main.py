"""Streamlit entry point for the Bank Marketing Predictor app."""

import streamlit as st

st.set_page_config(
    page_title="银行营销预测系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 银行营销预测系统")
st.markdown("### Bank Marketing Predictor")

st.markdown(
    """
本系统基于葡萄牙银行营销数据，提供两大核心功能：

| 功能 | 说明 |
|------|------|
| 📊 **数据分析** | 交互式探索客户特征分布、认购行为影响因素、特征相关性 |
| 🤖 **在线预测** | 通过点选表单输入客户特征，实时预测是否会认购定期存款 |

---

### 快速开始

1. **数据分析** → 点击左侧 `01_data_analysis` 页面
2. **在线预测** → 点击左侧 `02_prediction` 页面（需先训练模型）

---

### 模型训练

首次使用预测功能前，请先运行训练脚本：

```bash
python -m app.ml.train
```
"""
)
