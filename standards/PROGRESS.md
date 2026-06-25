# PROGRESS · bank-marketing-predictor 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-25 · by Claude)

- **阶段**:`第①步待启动 — 建仓 + 配 Secrets`
- **上一步完成**:① 已读完 standards/README.md + 00~06;② 已理解项目需求与数据;③ `00-project-context.md`、`01-requirements.md` 已填写完成;④ 本文件已初始化 TODO
- **下一步**:第①步 — 建 GitHub 仓库 + 提示用户配 Secrets
- **阻塞项**:等待用户确认文档内容无误

---

## 待办清单 (TODO,按六步流程优先级排列)

### 里程碑:项目初始化
- [x] **读规范闭环** — 已按序读取 standards/README.md → 00/01/PROGRESS → 02~06
- [x] **填写 00-project-context.md** — 项目身份(银行营销预测)、技术栈(Streamlit+sklearn)、目录地图、质量门槛、部署占位符
- [x] **填写 01-requirements.md** — US-1~US-5 用户故事(CI/CD、数据分析页、离线训练、在线预测、Docker),含验收标准
- [x] **初始化 PROGRESS.md** — 第一批 TODO 按六步流程排列

### 第①步:建仓 + 配 Secrets
- [ ] `gh repo create` 创建 `bank-marketing-predictor` 仓库
- [ ] 初始化最小提交(`.gitignore`、占位 `README.md`)
- [ ] ✋ 提示用户配置 GitHub Secrets:`SSH_PRIVATE_KEY`、`SSH_HOST`(47.115.209.104)、`SSH_USER`(root)
- [ ] `gh secret list` 验证 Secrets 已就位

### 第②步:开 feature 分支
- [ ] 从 `main` 切出 `feature/1-project-init`

### 第③步:逐模块开发
- [ ] **模块1:项目骨架** — `pyproject.toml`(ruff 配置)、`.gitignore`、`requirements.txt`、`requirements-dev.txt`
- [ ] **模块2:数据加载模块** — `app/models/data_loader.py` + `tests/test_data_loader.py`
- [ ] **模块3:可视化模块** — `app/models/visualizer.py` + `tests/test_visualizer.py`
- [ ] **模块4:模型训练模块** — `app/ml/train.py` + `tests/test_train.py`
- [ ] **模块5:预测推理模块** — `app/models/predictor.py` + `tests/test_predictor.py`
- [ ] **模块6:Streamlit 入口 + 数据分析页面** — `app/main.py` + `app/pages/01_data_analysis.py`
- [ ] **模块7:在线预测页面** — `app/pages/02_prediction.py`
- [ ] **模块8:CI/CD 配置** — `.github/workflows/ci.yml` + `cd.yml`
- [ ] **模块9:Docker 化** — `Dockerfile`

### 第④步:本地 CI 自检
- [ ] `ruff format --check .` + `ruff check .`
- [ ] `pytest --cov --cov-fail-under=80`
- [ ] (可选) `python -m app.ml.train --check-auc 0.75`
- [ ] 全绿才进入下一步

### 第⑤步:触发 PR
- [ ] `git push` 分支
- [ ] `gh pr create` 发起 PR
- [ ] 报 PR 链接 + CI 状态

### 第⑥步:人工审核 → 合并 → CD
- [ ] ✋ AI 停下,等人工 Review
- [ ] 人工 Merge 后,CD 自动部署
- [ ] 汇报部署结果(端口、健康检查、访问地址)

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-06-25 | Streamlit 端口定为 8501 | Streamlit 默认端口,当前空闲;区间回退至 8510 |
| 2026-06-25 | 默认模型 LightGBM,回退 RandomForest | LightGBM 在表格数据上通常表现最好;RandomForest 作为零依赖兜底 |
| 2026-06-25 | 数据文件不进 Git | `train.csv`+`test.csv` 合计约 3.5MB;CI 测试用程序生成样本数据 |
| 2026-06-25 | 模型产物不进 Git | `app/ml/model/` 加入 `.gitignore`,部署时随 CI 训练或预置 |
| 2026-06-25 | 采用 standards-template 模板体系 | 确保 AI 与人类按统一六步流程协作,可接力 |
| 2026-06-25 | 本地不强制 docker build | 遵循 05 标准;降低本地环境复杂度,docker build 交给 CI 兜底 |

---

## 已知坑 (GOTCHAS)

- (暂无——项目刚初始化,尚未踩坑)

---

> 反臃肿:里程碑超过 15 条时,把更早内容合并成一行摘要,保持本文件可快速阅读。
