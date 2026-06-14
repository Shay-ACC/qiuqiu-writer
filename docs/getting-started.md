# 快速开始

## 前置条件

| 工具 | 版本要求 |
|------|----------|
| Node.js | 20+（前端要求 npm ≥ 10） |
| Python | 3.10+ |
| Docker & Docker Compose | 任意最新版 |
| Poetry | 1.8+ |

## 一键启动（推荐）

```bash
# 克隆仓库后，在项目根目录执行
./start.sh
```

该脚本会自动启动基础设施容器、后端服务和前端开发服务器。

---

## 手动逐步启动

### 第一步：启动基础设施

以下命令默认从仓库根目录执行；后端、用户端和管理后台建议分别使用独立终端。

```bash
cp docker/.env.example docker/.env
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox up -d postgres redis mongodb minio
```

等待所有容器健康检查通过（约 10-30 秒）：

```bash
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox ps   # STATUS 列应显示 healthy
```

### 第二步：配置后端环境变量

```bash
cp backend/.env.example backend/.env
```

打开 `backend/.env`，至少填写以下必要配置：

```env
# 环境与安全
ENVIRONMENT=development
SECRET_KEY=example-placeholder-do-not-use
BACKEND_CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174","http://localhost:8889"]'
ALLOWED_HOSTS='["localhost","127.0.0.1","0.0.0.0"]'

# AI 服务（必填）
OPENAI_API_KEY=example-placeholder-do-not-use
OPENAI_API_BASE=https://api.deepseek.com/v1   # 或 OpenAI 官方地址
DEFAULT_AI_MODEL=deepseek-chat

# 数据库（与 docker/.env 保持一致）
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=example-placeholder-do-not-use
POSTGRES_DB=writerai
```

完整配置项说明见 [配置参考](./configuration.md)。

### 第三步：安装后端依赖并启动

```bash
conda activate nspox-py311
cd backend
export PYTHONPATH="$PWD/src"
poetry install  # 首次运行安装依赖
poetry run uvicorn memos.api.ai_api:app --host 0.0.0.0 --port 8000 --reload
```

后端启动成功后，可访问 API 文档：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 第四步：安装前端依赖并启动

```bash
cd frontend
npm ci          # 或 npm install；按 package-lock.json 可复现安装优先使用 npm ci
npm run dev     # 开发服务器，端口 5173
```

前端通过 Vite 代理将 `/api`、`/ai`、`/v1` 请求转发到后端 `http://127.0.0.1:8000`。

### 第五步：启动管理后台（可选）

```bash
cd admin
npm ci          # 或 npm install
npm run dev     # 管理后台，端口 5174
```

---

## 验证安装

打开浏览器访问：

- Backend docs：http://localhost:8000/docs
- Frontend 用户端：http://localhost:5173
- Admin 管理后台：http://localhost:5174

用户端和管理后台是两个独立应用；不要把 `http://localhost:5174` 的管理后台登录页误认为用户端页面。

**首次使用注册账号：** 注册需要邀请码，可通过管理后台生成（见[管理后台功能](./features.md#管理后台)）。

---

## 干净数据库首次启动验证

仅在本地验证初始化流程时使用以下命令；`down -v` 会删除当前 `nspox` Docker volume 中的数据。

```bash
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox down -v
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox up -d postgres redis mongodb minio
```

然后启动后端：

```bash
conda activate nspox-py311
cd backend
export PYTHONPATH="$PWD/src"
poetry run uvicorn memos.api.ai_api:app --host 0.0.0.0 --port 8000 --reload
```

干净初始化 SQL 已预置一批未使用的邀请码，注册测试可使用 `docker/postgres/init/01-init.sql` 中 `COPY public.invitation_codes` 段里的未使用记录。注册用户时不应再出现 `column users.plan does not exist`。

---

## 常见问题

### 数据库连接失败

检查 Docker 容器是否正常运行：

```bash
docker ps
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox logs postgres
```

### 端口冲突

默认端口：
- 前端：5173
- 管理后台：5174
- 后端：8000
- PostgreSQL：5432
- MongoDB：27017
- Redis：6379

如有冲突，修改 `docker-compose.infra.yml` 中的端口映射，并同步更新 `backend/.env`。

### macOS arm64 npm optional dependencies 缺失

如果启动 frontend 或 admin 时报 Rollup、Lightning CSS、Tailwind oxide native binding 缺失，可在对应前端目录下执行：

```bash
ROLLUP_VERSION=$(node -p "require('./node_modules/rollup/package.json').version")
LIGHTNINGCSS_VERSION=$(node -p "require('./node_modules/lightningcss/package.json').version")
TAILWIND_OXIDE_VERSION=$(node -p "require('./node_modules/@tailwindcss/oxide/package.json').version")
npm install --no-save \
  "@rollup/rollup-darwin-arm64@$ROLLUP_VERSION" \
  "lightningcss-darwin-arm64@$LIGHTNINGCSS_VERSION" \
  "@tailwindcss/oxide-darwin-arm64@$TAILWIND_OXIDE_VERSION" \
  --registry=https://registry.npmjs.org/
```

不要把 `npm audit fix --force` 当作本地启动修复手段，它可能改动依赖树并引入非预期升级。

### AI 接口无响应

确认 `.env` 中的 `OPENAI_API_KEY` 和 `OPENAI_API_BASE` 配置正确，可用 `curl` 测试：

```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_API_BASE/models
```
