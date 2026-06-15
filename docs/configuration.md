# 配置参考

后端配置由 `backend/src/memos/api/core/config.py` 的 `Settings` 类读取。常用配置来自：

- 本机后端：`backend/.env`
- Docker Compose：`docker/.env`
- 示例模板：`backend/.env.example`、`docker/.env.example`

`.env` 文件不要提交到 Git。

---

## 配置文件职责

| 文件 | 用途 |
|------|------|
| `backend/.env.example` | 本机运行 backend 的示例 |
| `backend/.env` | 本机 backend 实际配置，不提交 |
| `docker/.env.example` | Docker infra / Docker Compose 的示例 |
| `docker/.env` | Docker Compose 实际配置，不提交 |

本地开发时，Docker 跑基础设施，本机跑 backend，因此：

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
REDIS_HOST=localhost
MONGODB_HOST=localhost
MINIO_ENDPOINT=localhost:9000
```

Docker 容器内部互联时，host 使用服务名：

```env
POSTGRES_HOST=postgres
REDIS_HOST=redis
MONGODB_HOST=mongodb
MINIO_ENDPOINT=minio:9000
```

---

## 环境与安全

| 变量 | 说明 | 本地示例 |
|------|------|----------|
| `ENVIRONMENT` | `development`、`staging`、`production` | `development` |
| `SECRET_KEY` | JWT 和安全相关密钥 | `example-placeholder-do-not-use` |
| `BACKEND_CORS_ORIGINS` | 允许跨域来源，JSON 数组 | 见下方 |
| `ALLOWED_HOSTS` | 允许 Host，JSON 数组 | 见下方 |
| `API_HOST` | 后端监听地址 | `0.0.0.0` |
| `API_PORT` | 后端监听端口 | `8000` |

`BACKEND_CORS_ORIGINS` 和 `ALLOWED_HOSTS` 必须使用 JSON 数组格式：

```env
BACKEND_CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174","http://localhost:8889"]'
ALLOWED_HOSTS='["localhost","127.0.0.1","0.0.0.0"]'
```

不要写成逗号字符串，否则 Pydantic Settings 会按 `list[str]` 解析失败。

---

## PostgreSQL

| 变量 | 说明 | 本地示例 |
|------|------|----------|
| `POSTGRES_HOST` | 数据库 host | `127.0.0.1` |
| `POSTGRES_PORT` | 本机映射端口 | `5432` |
| `POSTGRES_USER` | 数据库用户 | `postgres` |
| `POSTGRES_PASSWORD` | 数据库密码 | `example-placeholder-do-not-use` |
| `POSTGRES_DB` | 数据库名 | `writerai` |

`backend/.env` 和 `docker/.env` 中的 `POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_DB` 必须一致。

---

## Redis

| 变量 | 说明 |
|------|------|
| `REDIS_HOST` | 本机开发通常为 `localhost`，容器内部为 `redis` |
| `REDIS_PORT` | 默认 `6379` |
| `REDIS_PASSWORD` | 生产环境必须显式设置 |

本地 infra 的 Redis 默认未启用密码。生产 Compose 使用 `REDIS_PASSWORD`。

---

## MongoDB

| 变量 | 说明 |
|------|------|
| `MONGODB_HOST` | 本机开发通常为 `localhost`，容器内部为 `mongodb` |
| `MONGODB_PORT` | 默认 `27017` |
| `MONGODB_DATABASE` | 默认 `writerai_sharedb` |
| `MONGODB_USERNAME` | 生产环境建议设置 |
| `MONGODB_PASSWORD` | 生产环境建议设置 |

MongoDB 用于 ShareDB 协同文档存储。

---

## MinIO

| 变量 | 说明 |
|------|------|
| `MINIO_ENDPOINT` | 本机开发 `localhost:9000`，容器内部 `minio:9000` |
| `MINIO_ACCESS_KEY` | 访问凭证 |
| `MINIO_SECRET_KEY` | 访问密钥 |

`backend/.env` 和 `docker/.env` 中的 MinIO 凭证需要一致。

---

## Qdrant 和 Neo4j

Qdrant 和 Neo4j 是可选服务。

| 变量 | 说明 |
|------|------|
| `DISABLE_QDRANT` | `true` 时不连接 Qdrant |
| `QDRANT_HOST` | 本机开发通常为 `127.0.0.1` |
| `QDRANT_PORT` | 默认 `6333` |
| `DISABLE_NEO4J` | `true` 时不连接 Neo4j |
| `NEO4J_URI` | 本机开发通常为 `bolt://localhost:7687` |
| `NEO4J_USER` | 默认用户 |
| `NEO4J_PASSWORD` | 生产必须显式设置 |
| `NEO4J_DB_NAME` | 默认数据库名 |

启动可选服务：

```bash
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox up -d qdrant neo4j
```

---

## AI provider

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI 兼容接口 key |
| `OPENAI_API_BASE` | OpenAI 兼容接口地址 |
| `DEFAULT_AI_MODEL` | 默认模型 |
| `MEMRADER_API_KEY` | 记忆抽取服务 key |
| `MEMRADER_API_BASE` | 记忆抽取服务地址 |
| `MEMRADER_MODEL` | 记忆抽取模型 |

示例文件只能保留占位符：

```env
OPENAI_API_KEY=example-placeholder-do-not-use
MEMRADER_API_KEY=example-placeholder-do-not-use
```

真实 key 只放在本机 `.env`、服务器密钥管理系统或 CI secret 中。

---

## 支付配置

本地开发可以使用模拟支付：

```env
PAYMENT_MOCK_MODE=true
```

生产环境需要填写真实商户配置或官方测试环境配置。不要把商户私钥、证书序列号或回调内部地址写入示例文件和文档。

---

## Admin 初始化脚本

`backend/scripts/init_admin_auto.py` 会创建默认管理员账号。它不会静默使用弱默认密码，必须显式设置：

```bash
cd backend
export NSPOX_ADMIN_PASSWORD="<strong-admin-password>"
export PYTHONPATH="$PWD/src"
poetry run python scripts/init_admin_auto.py
```

`backend/scripts/reset_admin.py` 需要同时设置数据库连接和管理员密码：

```bash
cd backend
export DATABASE_URL="postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>"
export NSPOX_ADMIN_PASSWORD="<strong-admin-password>"
export PYTHONPATH="$PWD/src"
poetry run python scripts/reset_admin.py
```

---

## development 与 production 差异

| 项目 | development | production |
|------|-------------|------------|
| `ENVIRONMENT` | `development` | `production` |
| `SECRET_KEY` | 可用占位符启动本地 | 必须强随机 |
| CORS/Host | 允许 localhost | 只能是明确域名/IP |
| 数据库密码 | 可使用本地占位符 | 必须强随机 |
| Redis/Mongo/MinIO | 可简化本地配置 | 必须显式强凭证 |
| `.env` 管理 | 本机文件 | 服务器文件或 secret manager |

生产环境不能使用 `example-placeholder-do-not-use`。

---

## 不应提交的文件

不要提交：

```text
.env
backend/.env
docker/.env
node_modules/
dist/
.DS_Store
.trae/
.venv/
```

提交前检查：

```bash
git status --short
```
