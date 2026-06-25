# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备标准工程结构、测试、CI 与 CD,
以便 后续两项核心功能(数据分析、在线预测)在可靠流水线上开发与部署。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: PR 触发 CI,至少包含格式检查(`ruff format --check .`)、静态检查(`ruff check .`)、单元测试(`pytest`)、覆盖率(`pytest --cov --cov-fail-under=80`)、构建检查(`docker build`)。
- AC3: CI 全绿后合并 main。
- AC4: 合并 main 自动触发 CD,部署后健康检查成功(Streamlit 应用可访问,返回 HTTP 200)。
- AC5: 项目目录结构符合 `00-project-context.md` 第 3 节目录地图。
- AC6: `pyproject.toml` 含 ruff 配置;`.gitignore` 排除 `app/ml/model/`、`data/*.csv`、`__pycache__`、`.pytest_cache`。

技术备注:
- 本地不强制 docker build,交给 CI 执行。
- CD 使用 GitHub Actions + SSH 远程部署,Secrets 由人提前配置。
- 数据文件不进 Git,CI 测试使用程序生成的样本数据。

---

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行营销分析师**,
我想要 在 Web 页面上交互式地探索营销数据,
以便 快速了解客户特征分布、识别认购行为的关键影响因素。

验收标准:
- AC1: Given 应用已启动,When 用户访问数据分析页面,Then 页面展示数据概览(总行数、列名、数据类型、缺失值统计)。
- AC2: Given 页面已加载数据,When 用户勾选/切换筛选条件(如按 job、marital、education 过滤),Then 图表与统计指标实时更新。
- AC3: Given 页面已加载数据,When 用户选择数值特征,Then 页面展示该特征的分布直方图/箱线图(按 subscribe 分组对比)。
- AC4: Given 页面已加载数据,When 用户查看类别特征,Then 页面展示该特征的条形图(各取值对应 subscribe=yes 的比例)。
- AC5: Given 页面已加载数据,When 用户查看相关性分析,Then 页面展示数值特征的相关性热力图。
- AC6: 页面加载 `test.csv`(~900KB)时响应时间 ≤ 5 秒;图表交互(筛选/切换)响应时间 ≤ 2 秒。

技术备注:
- 使用 plotly 实现交互式图表(pip 安装 `plotly`)。
- 数据加载复用 `data_loader.py`,缓存用 `@st.cache_data`。
- 页面文件:`app/pages/01_data_analysis.py`。
- 暂不支持上传自定义 CSV,后续可扩展。

---

### US-3 离线模型训练 · 状态: Backlog

作为 **数据科学家**,
我想要 基于 `train.csv` 离线训练一个二分类模型,
以便 产出一个可部署的模型文件,供在线预测系统调用。

验收标准:
- AC1: Given `data/train.csv` 存在,When 运行训练脚本 `python -m app.ml.train`,Then 完成以下步骤:
  - 数据加载、缺失值处理、类别编码、特征工程
  - 训练集/验证集拆分(80/20,分层抽样)
  - 训练至少一个分类模型(默认 LightGBM,若无则回退 RandomForest)
  - 输出验证集评估指标:AUC、Accuracy、Precision、Recall、F1
- AC2: Given 训练完成,Then AUC ≥ 0.75(不满足时记录但允许继续,后续迭代优化)。
- AC3: Given 训练完成,Then 模型文件保存到 `app/ml/model/` 目录(含模型文件 + 特征列名 + 编码器)。
- AC4: Given 训练完成,Then 训练日志和指标打印到控制台,方便 CI 采集。
- AC5: 训练脚本有对应的单元测试(使用极小的样本数据,验证训练流程可跑通)。

技术备注:
- 训练是离线执行的,不嵌入 Streamlit 页面。可在 Streamlit 启动前运行,或通过 CLI 单独触发。
- 模型产物目录 `app/ml/model/` 被 `.gitignore` 排除。
- 训练依赖:`scikit-learn`,可选 `lightgbm`(若安装)。
- 训练耗时预期 < 60 秒(train.csv ~280 万字节,约 4 万行)。

---

### US-4 在线预测系统(点选表单输入) · 状态: Backlog

作为 **银行业务人员**,
我想要 在一个 Web 表单上通过点选(下拉框/单选/滑块)输入客户特征,
以便 即时获取该客户是否会认购定期存款的预测结果及概率。

验收标准:
- AC1: Given 模型已训练并保存至 `app/ml/model/`,When 用户访问预测页面,Then 页面展示一个结构化输入表单,包含所有模型所需特征:
  - 类别特征(job, marital, education, default, housing, loan, contact, month, day_of_week, poutcome):下拉框/单选按钮,选项来源于训练数据去重值
  - 数值特征(age, duration, campaign, pdays, previous, emp_var_rate, cons_price_index, cons_conf_index, lending_rate3m, nr_employed):数值输入框/滑块,标注合理范围
- AC2: Given 表单已填写,When 用户点击"预测"按钮,Then 系统:
  - 对输入做校验(必填项非空、数值在合理范围)
  - 调用预测模型
  - 展示预测结果:"会认购 ✓"(绿色) 或 "不会认购 ✗"(红色)
  - 同时展示认购概率(如 "认购概率:72.3%")
- AC3: Given 用户输入不合法(如年龄填 -5、必填项为空),When 点击预测,Then 页面显示具体错误提示,不崩溃。
- AC4: Given 模型未训练(产物不存在),When 用户访问预测页面,Then 页面友好提示"模型尚未训练,请先运行训练脚本"并禁用预测按钮。
- AC5: 预测接口单次响应时间 ≤ 500ms(不包含页面渲染)。
- AC6: 预测逻辑有对应的单元测试(验证输入校验、预测输出格式、模型缺失时的降级处理)。

技术备注:
- 页面文件:`app/pages/02_prediction.py`。
- 预测逻辑封装在 `app/models/predictor.py`,与 Streamlit UI 解耦,方便测试。
- 表单字段的候选值从训练数据中提取,训练时随模型一并保存。
- 点选控件映射:类别特征用 `st.selectbox`,二值是/否用 `st.radio`,数值用 `st.number_input` 或 `st.slider`。

---

### US-5 Docker 容器化与部署 · 状态: Backlog

作为 **运维人员**,
我想要 应用被打包成 Docker 镜像并自动部署到服务器,
以便 在任何支持 Docker 的环境一键启动银行营销预测系统。

验收标准:
- AC1: `Dockerfile` 存在,基于 `python:3.11-slim`,安装 `requirements.txt`。
- AC2: `docker build` 成功;`docker run` 启动后,Streamlit 应用可通过 `http://<HOST>:8501` 访问。
- AC3: 容器内 Streamlit 启动命令正确(含 `--server.port=8501 --server.address=0.0.0.0`)。
- AC4: CI 中 `docker build` 作为构建检查关卡。
- AC5: CD 合并 main 后自动 SSH 到服务器、构建镜像、启动容器、健康检查通过。
- AC6: 生产镜像只安装 `requirements.txt`,不安装开发依赖。

技术备注:
- Streamlit 容器内默认监听 8501。
- Dockerfile 支持 `PIP_INDEX_URL` 构建参数,方便国内镜像源加速。
- 数据文件通过 Docker volume 或构建时 COPY 进入镜像(训练数据需要随镜像打包,或通过 volume 挂载)。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交。
- **可测试**:核心逻辑(数据加载、预测推理、可视化)必须有单元测试;覆盖率 ≥ 80%。
- **可部署**:部署后必须有健康检查验证(访问 Streamlit 应用根路径,预期 HTTP 200)。
- **性能**:数据分析页面初始加载 ≤ 5 秒;预测单次响应 ≤ 500ms。
- **数据不进 Git**:`data/*.csv` 和 `app/ml/model/` 通过 `.gitignore` 排除。
