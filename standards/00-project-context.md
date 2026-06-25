# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`bank-marketing-predictor`
- **一句话目标**:基于葡萄牙银行营销数据,提供数据可视化交互分析与在线认购预测的 Streamlit Web 应用。
- **使用者/受益者**:银行营销人员(通过交互页面理解数据特征)、业务决策者(通过预测模型判断客户认购概率)。
- **核心功能**:
  - **数据分析交互页面**:上传/加载营销数据后,提供筛选、聚合、可视化图表(分布图、相关性热力图、目标变量对比等),支持交互探索。
  - **离线训练 + 在线预测**:基于 `train.csv` 离线训练分类模型(默认使用 LightGBM/随机森林),保存模型产物;在预测页面通过点选表单输入客户特征,实时返回"是否会认购"的预测结果及概率。
- **输入/数据**:`data/train.csv`(训练集,含目标列 `subscribe`)、`data/test.csv`(测试/演示集,含目标列);数据源为 UCI Bank Marketing 数据集变体,共 21 个特征 + 1 个目标变量。
  - 特征:age, job, marital, education, default, housing, loan, contact, month, day_of_week, duration, campaign, pdays, previous, poutcome, emp_var_rate, cons_price_index, cons_conf_index, lending_rate3m, nr_employed
  - 目标:subscribe (yes/no,二分类)

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 用户指定,生态成熟 |
| Web/UI 框架 | Streamlit | 纯 Python 快速构建数据应用,适合分析与表单场景 |
| 机器学习 | scikit-learn / LightGBM | 分类模型训练、评估、概率预测 |
| 数据分析/可视化 | pandas + plotly | 高效数据处理 + 交互式图表 |
| 测试 | pytest + pytest-cov | 社区标准,fixture 丰富 |
| 格式/静态检查 | ruff (format + check) | 单工具覆盖格式与 lint,速度快 |
| 打包/运行 | Docker | 一次构建随处部署,CI/CD 标准 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
bank-marketing-predictor/
├── standards/                  # AI 项目记忆与通用规范
├── data/
│   ├── train.csv               # 训练数据(含目标列 subscribe)
│   └── test.csv                # 测试/演示数据(含目标列 subscribe)
├── app/
│   ├── __init__.py
│   ├── main.py                 # Streamlit 入口,页面路由
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── 01_data_analysis.py # 数据分析交互页面
│   │   └── 02_prediction.py    # 在线预测页面(表单输入→预测)
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── train.py            # 离线训练脚本
│   │   └── model/              # 训练产物目录(被 .gitignore)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_loader.py      # 数据加载与预处理
│   │   ├── predictor.py        # 模型加载与预测推理
│   │   └── visualizer.py       # 可视化图表封装
│   └── utils/
│       ├── __init__.py
│       └── (工具函数)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures(样本数据、mock 模型)
│   ├── test_data_loader.py
│   ├── test_train.py
│   ├── test_predictor.py
│   ├── test_visualizer.py
│   └── test_health.py          # Streamlit 健康/存活检查
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖
├── Dockerfile                  # 容器镜像构建
├── pyproject.toml              # ruff 配置
├── .github/workflows/
│   ├── ci.yml                  # PR 触发:ruff + pytest + coverage + docker build
│   └── cd.yml                  # 合并 main 触发:SSH 部署 + 健康检查
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `pytest --cov --cov-fail-under=80` |
| 构建 | `docker build` 成功(CI 执行,本地不强制) |
| 业务/模型指标 | 模型 AUC ≥ 0.75(训练后检查,作为 CI 可选门禁) |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集、模型产物不进 Git(通过 `.gitignore` 排除 `app/ml/model/`)。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- **数据文件 `data/*.csv` 不入 Git**(约 3.5MB),通过 `.gitignore` 排除。本地开发直接从 `data/` 加载,CI 中使用样本造数。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `bank-marketing-predictor` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/bank-marketing-predictor` | 服务器部署目录 |
| `<PORT>` | `8501` | Streamlit 默认端口,当前空闲 |
| `<PORT_MAX>` | `8510` | 回退端口区间上限 |
| `<CONTAINER_PORT>` | `8501` | 容器内 Streamlit 监听端口 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/health` 或 `/_stcore/health` | Streamlit 健康检查地址 |
| `<SSH_USER>` | 待定(沿用 `root`) | 部署用户 |
| `<SSH_HOST>` | 待定(沿用 `47.115.209.104`) | 服务器公网 IP |
