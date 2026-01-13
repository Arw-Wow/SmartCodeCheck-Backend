# 🛡️ SmartCodeCheck - 智能代码审计平台（Backend）

![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat&logo=sqlalchemy)

SmartCodeCheck Backend 是一个基于 **FastAPI** 的高性能 RESTful 服务，负责统一处理代码分析请求、LLM 调用、用户认证以及历史记录管理。

---

## ✨ 核心特性

- **🧠 LLM 聚合与调度**
  - 兼容 OpenAI API 格式（DeepSeek、Moonshot、GPT 等）
  - 支持**本地模型**（Ollama / vLLM），保障数据隐私

- **🔐 安全认证体系**
  - OAuth2 + JWT Token
  - 用户隔离的历史记录管理

- **💾 数据持久化**
  - SQLAlchemy ORM
  - 默认 SQLite，支持 PostgreSQL / MySQL

- **📝 历史记录管理**
  - 自动存储检测与对比记录
  - 默认 LRU 策略（保留最近 10 条）

- **⚡ 异步高并发**
  - 基于 Async OpenAI SDK
  - 支持流式与非流式响应

---

## 🛠️ 技术栈

- **Web 框架**：FastAPI
- **ASGI Server**：Uvicorn
- **ORM**：SQLAlchemy 2.x
- **数据校验**：Pydantic v2
- **LLM SDK**：OpenAI Python SDK（Async）
- **安全组件**：Passlib、Python-JOSE

---

## 📂 项目结构

```bash
app/
├── api/
│   ├── deps.py          # 依赖注入
│   └── endpoints/       # 路由模块
├── core/
│   ├── config.py        # 环境变量与配置
│   ├── database.py     # 数据库初始化
│   ├── models.py       # Pydantic Schema
│   └── security.py     # JWT / 密码哈希
├── models/              # SQLAlchemy 数据模型
├── services/
│   └── llm_analyzer.py  # Prompt 构建与 LLM 调用
└── main.py
````

---

## 🚀 快速开始

### 1. 创建运行环境

```bash
conda create -n SCC-Backend python=3.11
conda activate SCC-Backend
pip install -r requirements.txt
```

---

### 2. 配置环境变量

复制 `.env example` 文件到项目根目录，将文件名改为 `.env`，并按其中要求修改 .env 的内容。

---

### 3. 启动服务（默认端口为 8000）

```bash
uvicorn app.main:app --reload --port 8000
```

---

### 4. 接口文档

* Swagger UI：`http://localhost:8000/docs`
* ReDoc：`http://localhost:8000/redoc`

---

## 🔌 API 概览

| 模块         | 方法   | 路径                      | 描述    |
| ---------- | ---- | ----------------------- | ----- |
| Auth       | POST | `/api/v1/auth/login`    | 用户登录  |
| Auth       | POST | `/api/v1/auth/register` | 用户注册  |
| Analysis   | POST | `/api/v1/analyze`       | 单代码分析 |
| Analysis   | POST | `/api/v1/compare`       | 双代码对比 |
| History    | GET  | `/api/v1/history`       | 查询历史  |
| Dimensions | POST | `/api/v1/dimensions`    | 自定义维度 |

---

## ⚠️ 注意事项

* **本地模型优先级**：若请求中携带 `local_config`，将覆盖 `.env` 配置
* **CORS**：默认允许 `http://localhost:5173`

SmartCodeCheck Backend — Powering Intelligent Code Audits
