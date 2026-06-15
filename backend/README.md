# nspox Backend

`backend/` 是 nspox 的 FastAPI 后端，负责认证、作品管理、章节管理、AI 调用、协同编辑、支付和管理后台 API。

当前推荐入口：

```bash
poetry run uvicorn memos.api.ai_api:app --host 0.0.0.0 --port 8000 --reload
```

API docs：

```text
http://localhost:8000/docs
```

---

## 技术栈

- Python 3.10+，推荐 Python 3.11
- FastAPI + Uvicorn
- Poetry
- SQLAlchemy async + asyncpg
- PostgreSQL
- Redis
- MongoDB
- MinIO
- optional Qdrant / Neo4j

---

## 本地启动

先从仓库根目录启动 Docker infra：

```bash
cp docker/.env.example docker/.env
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox up -d postgres redis mongodb minio
```

准备后端配置：

```bash
cp backend/.env.example backend/.env
```

启动后端：

```bash
cd backend
poetry install --extras all --with dev --with test
export PYTHONPATH="$PWD/src"
poetry run uvicorn memos.api.ai_api:app --host 0.0.0.0 --port 8000 --reload
```

---

## 关键环境变量

本机 backend 连接 Docker infra 时：

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=example-placeholder-do-not-use
POSTGRES_DB=writerai
REDIS_HOST=localhost
REDIS_PORT=6379
MONGODB_HOST=localhost
MONGODB_PORT=27017
MINIO_ENDPOINT=localhost:9000
```

CORS 和 Host 必须使用 JSON 数组：

```env
BACKEND_CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174","http://localhost:8889"]'
ALLOWED_HOSTS='["localhost","127.0.0.1","0.0.0.0"]'
```

生产环境不能使用 `example-placeholder-do-not-use`。

---

## 项目结构

```text
backend/
├── src/memos/api/
│   ├── ai_api.py              # 当前推荐 FastAPI 入口
│   ├── routers/               # HTTP / WebSocket 路由
│   ├── services/              # 业务服务
│   ├── models/                # SQLAlchemy ORM
│   ├── schemas/               # Pydantic schema
│   ├── llms/                  # AI provider 封装
│   └── core/                  # 配置、安全、数据库
├── scripts/                   # 初始化和维护脚本
├── tests/                     # 测试
├── pyproject.toml             # Poetry 项目配置
└── poetry.lock
```

---

## 常用命令

安装依赖：

```bash
cd backend
poetry install --extras all --with dev --with test
```

运行测试：

```bash
cd backend
poetry run pytest tests
```

运行 schema 初始化回归测试：

```bash
cd backend
poetry run pytest tests/api/test_postgres_init_schema.py -q
```

检查配置：

```bash
cd backend
poetry check
```

格式化：

```bash
cd backend
poetry run ruff check --fix
poetry run ruff format
```

---

## Admin 初始化脚本

创建默认管理员前必须设置强密码：

```bash
cd backend
export NSPOX_ADMIN_PASSWORD="<strong-admin-password>"
export PYTHONPATH="$PWD/src"
poetry run python scripts/init_admin_auto.py
```

重置管理员密码：

```bash
cd backend
export DATABASE_URL="postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>"
export NSPOX_ADMIN_PASSWORD="<strong-admin-password>"
export PYTHONPATH="$PWD/src"
poetry run python scripts/reset_admin.py
```

---

## 注册和邀请码

本地注册需要邀请码。初始化 SQL 已预置未使用的邀请码，可查询：

```bash
docker exec -it qiuqiuwriter-postgres psql -U postgres -d writerai -c "SELECT code, used FROM invitation_codes ORDER BY id LIMIT 10;"
```

---

## 相关文档

- [本地开发启动](../docs/getting-started.md)
- [配置参考](../docs/configuration.md)
- [部署指南](../docs/deployment.md)
- [开发指南](../docs/development.md)
