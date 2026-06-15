<div align="center">

<img src="frontend/public/logo.svg" width="64" height="64" alt="logo" />

# nspox

### AI 助力人类构筑专属内心世界

**让创作更简单，让故事更精彩**

nspox 是一款开源 AI 写作平台，帮助创作者管理作品、章节、素材与协作编辑流程，并通过 AI 辅助完成分析、续写、润色和创作管理。

[GitHub 仓库](https://github.com/nspox-project/nspox) · [Issues](https://github.com/nspox-project/nspox/issues) · [Discussions](https://github.com/nspox-project/nspox/discussions)

</div>

---

## 项目声明

本仓库源码基于 [MIT 协议](LICENSE) 开源，可用于学习、研究、二次开发以及商业部署。

开源版本不包含任何真实生产密钥。提交代码前请确认没有提交 `.env`、真实 API key、token、密码、内部地址、`node_modules`、`dist`、`.DS_Store`、`.trae` 或 `.venv`。

---

## 技术栈

| 模块 | 技术 | 默认端口 |
|------|------|----------|
| `backend/` | FastAPI + Python 3.10+ + Poetry + SQLAlchemy async | `8000` |
| `frontend/` | React 19 + TypeScript + Vite + TipTap/Yjs | `5173` |
| `admin/` | React 18 + Ant Design + Vite | `5174` |
| `docker/` | PostgreSQL, Redis, MongoDB, MinIO, optional Qdrant/Neo4j | service ports |

当前本地推荐后端入口是：

```bash
poetry run uvicorn memos.api.ai_api:app --host 0.0.0.0 --port 8000 --reload
```

---

## 项目结构

```text
nspox/
├── frontend/        # 用户端前端，Vite dev server: http://localhost:5173
├── admin/           # 管理后台，Vite dev server: http://localhost:5174
├── backend/         # FastAPI 后端，API docs: http://localhost:8000/docs
├── docker/          # Docker Compose、Nginx、PostgreSQL 初始化 SQL
├── deploy/          # 部署辅助文件和历史数据导出
├── docs/            # 项目文档
└── start.sh         # 历史一键启动脚本；推荐命令以 docs/getting-started.md 为准
```

---

## 文档入口

| 目标 | 文档 |
|------|------|
| 新人本地启动 | [docs/getting-started.md](docs/getting-started.md) |
| 环境变量和配置项 | [docs/configuration.md](docs/configuration.md) |
| 服务器部署 | [docs/deployment.md](docs/deployment.md) |
| 开发协作、测试、PR 检查 | [docs/development.md](docs/development.md) |
| 后端单独说明 | [backend/README.md](backend/README.md) |

---

## 快速本地启动

完整步骤见 [快速开始](docs/getting-started.md)。最短路径如下，命令默认从仓库根目录执行。

```bash
cp docker/.env.example docker/.env
cp backend/.env.example backend/.env
```

```bash
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox up -d postgres redis mongodb minio
```

```bash
cd backend
poetry install --extras all --with dev --with test
export PYTHONPATH="$PWD/src"
poetry run uvicorn memos.api.ai_api:app --host 0.0.0.0 --port 8000 --reload
```

```bash
cd frontend
npm ci
npm run dev
```

```bash
cd admin
npm ci
npm run dev
```

访问地址：

| 服务 | 地址 |
|------|------|
| Backend docs | http://localhost:8000/docs |
| Frontend 用户端 | http://localhost:5173 |
| Admin 管理后台 | http://localhost:5174 |

注册需要邀请码。本地初始化 SQL 已包含未使用的邀请码种子，查询方式见 [docs/getting-started.md](docs/getting-started.md#注册和邀请码)。

---

## 部署入口

负责人部署服务器前请先阅读 [docs/deployment.md](docs/deployment.md)。生产环境必须显式设置：

- `ENVIRONMENT=production`
- 强随机 `SECRET_KEY`
- 明确的 `BACKEND_CORS_ORIGINS` JSON 数组
- 明确的 `ALLOWED_HOSTS` JSON 数组
- 数据库、Redis、MongoDB、MinIO、Neo4j 的强凭证
- AI provider key 或本地模型配置

生产环境不能使用 `example-placeholder-do-not-use` 或任何弱口令占位符。

---

## 安全提醒

- `.env` 只在本机或服务器保存，不提交到 Git。
- `backend/.env.example` 和 `docker/.env.example` 只能保留占位符。
- `BACKEND_CORS_ORIGINS` 和 `ALLOWED_HOSTS` 必须使用 JSON 数组格式。
- 如果真实密钥曾进入 Git 历史，需要先在供应商后台轮换，再清理历史记录。

---

## 许可证

[MIT](LICENSE)
