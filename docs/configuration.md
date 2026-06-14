# 配置参考

所有后端配置通过 `backend/.env` 文件加载，由 `backend/src/memos/api/core/config.py` 中的 `Settings` 类解析。

## 快速配置（最小必要配置）

```env
# 环境与安全
ENVIRONMENT=development
SECRET_KEY=example-placeholder-do-not-use
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ALLOWED_HOSTS=localhost,127.0.0.1

# AI 服务（必填）
OPENAI_API_KEY=example-placeholder-do-not-use
OPENAI_API_BASE=https://api.deepseek.com/v1
DEFAULT_AI_MODEL=deepseek-chat

# 数据库（需与 docker/.env 保持一致）
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=example-placeholder-do-not-use
POSTGRES_DB=writerai

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=writerai_sharedb

REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## AI 服务配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `OPENAI_API_KEY` | — | AI 服务 API Key（必填） |
| `OPENAI_API_BASE` | `https://api.deepseek.com/v1` | API 基础地址，支持任意 OpenAI 兼容接口 |
| `DEFAULT_AI_MODEL` | `deepseek-chat` | 默认使用的模型名称 |
| `LOG_LEVEL` | `INFO` | 日志级别（DEBUG / INFO / WARNING / ERROR） |

### 切换 AI 提供商示例

**使用 OpenAI：**
```env
OPENAI_API_KEY=example-placeholder-do-not-use
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_AI_MODEL=gpt-4o
```

**使用本地 Ollama：**
```env
OPENAI_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
DEFAULT_AI_MODEL=qwen2.5:7b
```

---

## 数据库配置

### PostgreSQL

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `POSTGRES_HOST` | `localhost` | 数据库主机 |
| `POSTGRES_PORT` | `5433` | 端口（Docker 映射为 5433 避免冲突） |
| `POSTGRES_USER` | `postgres` | 用户名 |
| `POSTGRES_PASSWORD` | — | 密码，生产必须设置强随机值 |
| `POSTGRES_DB` | `writerai` | 数据库名 |

### MongoDB

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MONGODB_HOST` | `localhost` | 主机 |
| `MONGODB_PORT` | `27017` | 端口 |
| `MONGODB_DATABASE` | `writerai_sharedb` | 数据库名 |
| `MONGODB_USERNAME` | — | 用户名（可选） |
| `MONGODB_PASSWORD` | — | 密码（可选） |

### Redis

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `REDIS_HOST` | `localhost` | 主机 |
| `REDIS_PORT` | `6379` | 端口 |
| `REDIS_PASSWORD` | — | 密码（可选） |

---

## 向量数据库配置（可选）

Qdrant 用于语义搜索功能，默认禁用。

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DISABLE_QDRANT` | `true` | 设为 `false` 启用 |
| `QDRANT_HOST` | `127.0.0.1` | Qdrant 主机 |
| `QDRANT_PORT` | `6333` | HTTP 端口 |
| `EMBEDDING_DIMENSION` | `768` | 嵌入向量维度 |

启动 Qdrant：

```bash
# docker-compose.infra.yml 中已包含 Qdrant 服务，默认注释
docker compose up -d qdrant
```

---

## 图数据库配置（可选）

Neo4j 用于记忆系统的知识图谱，默认禁用。

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DISABLE_NEO4J` | `true` | 设为 `false` 启用 |
| `NEO4J_URI` | `bolt://localhost:7687` | Bolt 连接地址 |
| `NEO4J_USER` | `neo4j` | 用户名 |
| `NEO4J_PASSWORD` | — | 密码，生产必须设置强随机值 |
| `NEO4J_DB_NAME` | `neo4j` | 数据库名 |

---

## 记忆系统配置（可选）

MemOS 记忆系统让 AI 能够记住用户偏好和历史对话，需配合 Qdrant 和 Neo4j 使用。

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ENABLE_TEXTUAL_MEMORY` | `false` | 启用文本记忆（读写） |
| `ENABLE_PREFERENCE_MEMORY` | `false` | 启用偏好记忆 |
| `ENABLE_ACTIVATION_MEMORY` | `false` | 启用激活记忆 |
| `MOS_USER_ID` | `default_user` | MemOS 用户标识 |
| `MOS_SESSION_ID` | `default_session` | 会话标识 |
| `MOS_TOP_K` | `5` | 记忆召回数量 |
| `MOS_CHAT_MODEL_PROVIDER` | `openai` | 记忆模型提供商 |
| `MOS_CHAT_MODEL` | `deepseek-chat` | 记忆专用模型 |
| `MOS_CHAT_TEMPERATURE` | `0.7` | 生成温度 |
| `MOS_ENABLE_SCHEDULER` | `false` | 启用后台调度器 |
| `MOS_RERANKER_BACKEND` | `cosine_local` | 重排序方式（本地余弦 / API） |
| `MOS_EMBEDDER_BACKEND` | `sentence_transformer` | 嵌入模型后端 |
| `MOS_EMBEDDER_MODEL` | `/app/models/nomic-embed-text-v1.5` | 嵌入模型路径 |
| `MOS_USER_MANAGER_BACKEND` | `postgres` | 用户管理后端（postgres / sqlite） |

### MemReader（记忆提取）

| 配置项 | 说明 |
|--------|------|
| `MEMRADER_API_KEY` | 记忆提取服务 API Key |
| `MEMRADER_API_BASE` | 记忆提取服务地址 |
| `MEMRADER_MODEL` | 记忆提取使用的模型 |

---

## 本地嵌入模型配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HF_LOCAL_FILES_ONLY` | `true` | 仅使用本地模型文件，不联网下载 |
| `MOS_EMBEDDER_MODEL` | `/app/models/nomic-embed-text-v1.5` | 嵌入模型本地路径 |

---

## API 服务器配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `API_HOST` | `0.0.0.0` | 监听地址 |
| `API_PORT` | `8001` | 监听端口 |

---

## 生产环境注意事项

1. **设置 `ENVIRONMENT=production`** — 生产启动会校验安全配置。
2. **使用强 Secret Key** — `SECRET_KEY` 必须是生产专用随机长字符串。
3. **配置强凭证** — `POSTGRES_PASSWORD`、`REDIS_PASSWORD`、`MONGODB_USERNAME`、`MONGODB_PASSWORD`、`MINIO_ACCESS_KEY`、`MINIO_SECRET_KEY` 不得为空或使用默认值。
4. **限制 CORS/Host** — `BACKEND_CORS_ORIGINS` 和 `ALLOWED_HOSTS` 必须是明确白名单，生产不得使用 `*`。
5. **保护 `.env` 文件** — 确保 `.env` 不被提交到版本控制。
6. **轮换已泄露密钥** — 如果密钥曾进入 Git 历史，必须在供应商后台立即吊销并重新生成。

生产环境变量放在 `docker/.env`（参考 `backend/.env.example`）。
