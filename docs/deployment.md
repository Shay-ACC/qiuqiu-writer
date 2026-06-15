# 部署指南

目标：负责人可以按本文完成本地开发部署、Docker Compose staging 部署和生产部署准备。

当前推荐后端入口：

```text
memos.api.ai_api:app
```

当前后端端口：

```text
8000
```

---

## 部署模式总览

| 模式 | 适用场景 | 运行方式 |
|------|----------|----------|
| 本地开发部署 | 开发、调试、联调 | Docker infra + 本机 backend/frontend/admin |
| Docker Compose staging | 内网验收、预发布 | Docker Compose 运行 infra、backend、frontend |
| 生产部署 | 公网服务 | 预构建镜像 + Nginx/HTTPS + 持久化卷 + 备份 |

当前 `docker/docker-compose.prod.yml` 是生产模板，包含 backend 和用户端 frontend。管理后台已有 `docker/nginx/admin.conf`，但模板中没有单独 admin 服务；生产需要管理后台时，建议在部署编排中增加独立 Nginx 服务或由外部 Nginx 托管 `admin/dist`。

---

## 本地开发部署

本地开发请优先使用 [getting-started.md](./getting-started.md) 中的命令。

```bash
cp docker/.env.example docker/.env
cp backend/.env.example backend/.env
docker compose --env-file docker/.env -f docker/docker-compose.infra.yml -p nspox up -d postgres redis mongodb minio
```

后端本机启动：

```bash
cd backend
poetry install --extras all --with dev --with test
export PYTHONPATH="$PWD/src"
poetry run uvicorn memos.api.ai_api:app --host 0.0.0.0 --port 8000 --reload
```

用户端：

```bash
cd frontend
npm ci
npm run dev
```

管理后台：

```bash
cd admin
npm ci
npm run dev
```

---

## Docker Compose staging 部署

staging 可以使用 `docker/docker-compose.prod.yml` 的服务拓扑，但仍建议使用 staging 专用域名、镜像 tag 和 `.env`。

准备环境变量：

```bash
cp docker/.env.example docker/.env
```

编辑 `docker/.env`，至少设置：

```env
ENVIRONMENT=production
SECRET_KEY=<generate-a-strong-random-value>
BACKEND_CORS_ORIGINS='["https://staging.example.com","https://staging-admin.example.com"]'
ALLOWED_HOSTS='["staging.example.com","staging-admin.example.com","staging-api.example.com"]'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-postgres-password>
POSTGRES_DB=writerai
REDIS_PASSWORD=<strong-redis-password>
MONGODB_DATABASE=writerai_sharedb
MONGODB_USERNAME=<strong-mongo-user>
MONGODB_PASSWORD=<strong-mongo-password>
MINIO_ACCESS_KEY=<strong-minio-access-key>
MINIO_SECRET_KEY=<strong-minio-secret-key>
NEO4J_PASSWORD=<strong-neo4j-password>
BACKEND_IMAGE=<registry>/<namespace>/nspox-backend:<tag>
```

构建用户端静态文件：

```bash
cd frontend
npm ci
npm run build
```

如 staging 需要管理后台，也构建 admin：

```bash
cd admin
npm ci
npm run build
```

启动：

```bash
cd docker
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-staging up -d
```

查看状态和日志：

```bash
cd docker
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-staging ps
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-staging logs -f backend
```

---

## 生产部署注意事项

生产环境必须满足：

- `ENVIRONMENT=production`
- `SECRET_KEY` 是强随机长字符串
- `BACKEND_CORS_ORIGINS` 是明确域名白名单 JSON 数组，不能是通配
- `ALLOWED_HOSTS` 是明确域名或 IP 白名单 JSON 数组
- PostgreSQL、Redis、MongoDB、MinIO、Neo4j 密码必须显式设置
- 不使用 `example-placeholder-do-not-use`
- 不使用常见弱口令或示例口令
- `.env` 不提交到 Git

生成 `SECRET_KEY` 示例：

```bash
openssl rand -hex 32
```

生产 `.env` 只放在服务器或密钥管理系统中。不要把真实值写入 `.env.example`、README 或 docs。

---

## Docker 内部服务名

Docker Compose 内部服务互联使用服务名：

| 服务 | Docker 内部 host |
|------|------------------|
| PostgreSQL | `postgres` |
| Redis | `redis` |
| MongoDB | `mongodb` |
| Backend | `backend` |
| MinIO | `minio` |

本机开发连接 Docker infra 时使用 `127.0.0.1` 和映射端口；容器内部互联时使用服务名。

---

## Nginx 反向代理关系

`docker/nginx/frontend.conf`：

- `/` 返回用户端静态文件
- `/api/` 代理到 `http://backend:8000`
- `/ai/` 代理到 `http://backend:8000`
- `/v1/` 代理到 `http://backend:8000`
- `/api/v1/yjs` 和 `/api/v1/collab-ai` 以 WebSocket 方式代理到 `backend:8000`

`docker/nginx/admin.conf`：

- `/` 返回管理后台静态文件
- `/api/` 代理到 `http://backend:8000`

如果生产使用外部 Nginx 或云负载均衡，请保持同样的路径转发关系，并在 HTTPS 终止层正确传递：

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

WebSocket 路径需要：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

## 前端和管理端构建

用户端：

```bash
cd frontend
npm ci
npm run build
```

管理后台：

```bash
cd admin
npm ci
npm run build
```

当前 `docker/docker-compose.prod.yml` 示例将 `../frontend/dist` 挂载到 Nginx。生产更推荐将构建产物固化进镜像，或由 CI 生成制品后发布到服务器。

如果部署管理后台，可使用 `docker/nginx/admin.conf` 托管 `admin/dist`，并为它分配独立域名或端口。不要把管理后台和用户端静态文件混到同一个目录。

---

## 数据卷和备份

需要备份的 Docker volumes：

- `postgres_data`
- `redis_data`
- `mongodb_data`
- `minio_data`
- 如果启用记忆图或向量库，还包括 `neo4j_data`、`qdrant_data`

PostgreSQL 备份：

```bash
docker exec qiuqiuwriter-postgres pg_dump -U postgres writerai > backup_$(date +%Y%m%d).sql
```

PostgreSQL 恢复：

```bash
docker exec -i qiuqiuwriter-postgres psql -U postgres writerai < backup_20260101.sql
```

MongoDB 备份：

```bash
docker exec qiuqiuwriter-mongodb mongodump --db writerai_sharedb --out /tmp/mongodump
docker cp qiuqiuwriter-mongodb:/tmp/mongodump ./mongodump_$(date +%Y%m%d)
```

MinIO 需要按对象存储策略备份 bucket 数据。生产环境建议使用云对象存储或跨机房备份。

---

## 日志查看

```bash
cd docker
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod logs -f backend
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod logs --tail=100 frontend
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod ps
```

生产 Compose 已限制日志大小。外部 Nginx、云负载均衡和系统日志应纳入统一日志平台。

---

## 健康检查

后端启动后检查：

```bash
curl -f http://127.0.0.1:8000/docs
```

容器状态：

```bash
cd docker
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod ps
```

数据库连通性：

```bash
docker exec -it qiuqiuwriter-postgres pg_isready -U postgres -d writerai
docker exec -it qiuqiuwriter-redis redis-cli ping
docker exec -it qiuqiuwriter-mongodb mongosh --eval "db.adminCommand('ping')"
```

---

## 回滚策略

推荐每次部署使用不可变镜像 tag。

发布前记录当前版本：

```bash
cd docker
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod images
```

回滚步骤：

```bash
cd docker
export BACKEND_IMAGE=<registry>/<namespace>/nspox-backend:<previous-tag>
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod up -d backend
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod logs -f backend
```

如果本次发布包含数据库变更，必须先确认回滚兼容性。本仓库当前没有引入大型迁移系统，生产变更应单独制定迁移与回滚方案。

---

## 大 SQL dump 说明

`deploy/writerai.sql` 当前约数十 MB，适合作为历史导出参考，不适合作为长期源码分发方式。后续建议迁移到更合适的分发方式，例如 Git LFS、Release artifact 或对象存储制品。本次文档治理不移除该文件。

---

## 停止和清理

停止容器，保留数据：

```bash
cd docker
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod down
```

停止并删除数据卷，生产环境谨慎使用：

```bash
cd docker
docker compose --env-file .env -f docker-compose.prod.yml -p nspox-prod down -v
```
