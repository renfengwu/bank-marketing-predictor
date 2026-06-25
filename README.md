# 银行营销预测系统 · bank-marketing-predictor

基于葡萄牙银行营销数据的 **数据分析交互平台** 与 **在线认购预测系统**。

## 功能

- 📊 **数据分析交互页面** — 探索客户特征分布、认购行为影响因素、相关性热力图
- 🤖 **在线预测系统** — 点选表单输入客户特征，实时预测是否会认购定期存款

## 技术栈

Python 3.11 · Streamlit · scikit-learn · LightGBM · plotly · pytest · ruff · Docker

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 训练模型（首次使用前）
python -m app.ml.train

# 启动应用
streamlit run app/main.py
```

访问 http://localhost:8501
