# nspox 系统架构

## 项目概述

nspox 是一个 AI 助力写作平台，支持小说、剧本等多种创作形式，提供实时协同编辑、AI 辅助写作、云端同步等功能。

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        浏览器 / 客户端                        │
│   ┌──────────────────┐          ┌──────────────────────┐     │
│   │   用户端前端       │          │      管理后台          │     │
│   │ React 19 + Vite  │          │  React 18 + Ant Design│     │
│   │    端口 5173      │          │      独立端口          │     │
│   └────────┬─────────┘          └──────────┬───────────┘     │
└────────────┼──────────────────────────────┼─────────────────┘
             │ HTTP / WebSocket              │ HTTP
             ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI 后端 (端口 8001)                    │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  路由层   │  │  服务层   │  │  模型层   │  │  Schema层 │  │
│  │ routers/ │→ │services/ │→ │ models/  │  │ schemas/  │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│                     │                                       │
│                  ┌──┴──┐                                    │
│                  │ LLM │ (ai_service / llms/)               │
│                  └─────┘                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │PostgreSQL│  │  Redis   │  │ MongoDB  │
    │ 主数据库  │  │ 缓存/会话 │  │ShareDB文档│
    └──────────┘  └──────────┘  └──────────┘
```

---

## 前端架构

前端包含两个独立的应用：**用户端前端**和**后台管理前端**。

### 1. 用户端前端 (frontend/)

面向普通用户的创作平台，提供小说编辑、剧本创作、作品管理等核心功能。

#### 技术栈

- **框架**: React 19 + TypeScript
- **构建工具**: Vite
- **路由**: React Router v7（懒加载）
- **编辑器**: TipTap + Yjs（CRDT 协同编辑）
- **状态管理**: React Hooks + Context

#### 目录结构

```
frontend/src/
├── main.tsx              # 应用入口：调用 initTheme() 后渲染 React 应用
├── App.tsx               # 路由定义（React Router v7，懒加载）
├── index.css             # 全局样式（CSS变量主题系统）
├── pages/                # 页面组件
│   ├── HomePage.tsx      # 首页 / 落地页
│   ├── UserWorksPage.tsx # 用户个人作品库
│   ├── NovelEditorPage.tsx   # 小说编辑器
│   ├── DramaEditorPage.tsx   # 剧本编辑器
│   ├── UGCPlaza.tsx      # UGC 内容广场
│   ├── PlansPage.tsx     # 付费方案页面
│   └── TransactionsPage.tsx  # 交易记录页面
├── components/           # UI 组件
│   ├── auth/             # 认证组件（登录弹窗、权限守卫）
│   ├── common/           # 通用组件（加载器、消息弹窗、反馈弹窗）
│   ├── editor/           # 编辑器组件（小说/剧本编辑器、AI助手、角色管理）
│   ├── drama/            # 剧本专用组件（故事板视图、剧集导入）
│   ├── home/             # 首页组件（AI工具广场、案例分享）
│   ├── layout/           # 布局组件（主布局、侧边栏）
│   ├── ugc-plaza/        # UGC广场组件（内容卡片、筛选栏、搜索栏）
│   └── ui/               # 基础UI组件（按钮、输入框、对话框、徽章）
├── hooks/                # 自定义 Hooks
│   ├── useYjsEditor.ts   # Yjs 编辑器状态管理
│   ├── useChapterManagement.ts  # 章节管理
│   ├── useVolumeManagement.ts   # 卷管理
│   └── useFindReplace.ts # 查找替换
├── types/                # TypeScript 类型定义
│   ├── document.ts       # 文档类型
│   ├── novelEditor.ts    # 小说编辑器类型
│   └── sharedb.ts        # ShareDB 类型
├── lib/                  # 工具库
│   └── utils.ts          # 通用工具函数
└── utils/                # API 和工具函数
    ├── baseApiClient.ts  # 基础 HTTP 客户端（axios 封装）
    ├── authApi.ts        # 认证相关 API
    ├── chaptersApi.ts    # 章节 API
    ├── bookAnalysisApi.ts# 书籍分析 API
    ├── chatApi.ts        # AI 聊天 API
    ├── collabAiApi.ts    # 协作 AI API
    ├── dramaApi.ts       # 剧本 API
    ├── theme.ts          # 主题系统
    └── yjsApi.ts         # Yjs 相关 API
```

#### 路由配置

| 路径 | 页面组件 | 是否需要登录 | 说明 |
|------|----------|:---:|------|
| `/` | HomePage | 否 | 首页 / 落地页 |
| `/novel` | WorksPage | 否 | 小说广场 |
| `/ugc-plaza` | UGCPlaza | 否 | UGC 内容广场 |
| `/plans` | PlansPage | 是 | 付费方案 |
| `/transactions` | TransactionsPage | 是 | 交易记录 |
| `/novel/editor` | NovelEditorPage | 是 | 小说编辑器 |
| `/drama/editor` | DramaEditorPage | 是 | 剧本编辑器 |
| `/drama` | WorksPage | 是 | 剧本列表（重定向） |
| `/works` | WorksPage | 是 | 个人作品库（重定向） |

#### 核心特性

- **主题系统**: 通过 `html data-theme` 属性切换明暗主题，所有颜色使用 CSS 变量
- **协同编辑**: Yjs CRDT 算法实现无冲突的实时协作编辑
- **离线支持**: y-indexeddb 实现本地数据持久化
- **代码分割**: React Router 懒加载提升首屏性能

---

### 2. 后台管理前端 (admin/)

面向管理员的后台管理系统，提供用户管理、作品审核、系统配置等管理功能。

#### 技术栈

- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design
- **构建工具**: Vite

#### 目录结构

```
admin/src/
├── main.tsx              # 应用入口
├── App.tsx               # 路由配置
├── index.css             # 全局样式
├── layouts/
│   └── MainLayout.tsx    # 管理后台布局（侧边栏导航、顶部栏）
├── pages/
│   ├── Dashboard/        # 仪表盘（数据概览、关键指标）
│   ├── Users/            # 用户管理（用户列表、权限管理）
│   ├── Works/            # 作品管理（作品审核、内容管理）
│   ├── PromptTemplates/  # 提示词模板管理
│   ├── GlobalPrompts/    # 全局提示词管理
│   ├── LLMConfigs/       # LLM 配置管理
│   ├── InvitationCodes/  # 邀请码管理
│   ├── Feedback/         # 用户反馈管理
│   ├── AuditLogs/        # 审计日志
│   ├── Plans/            # 套餐管理
│   ├── SystemSettings/   # 系统设置
│   ├── Maintenance/      # 维护模式
│   ├── PromptExperiments/# 提示词实验管理
│   ├── PromptRatings/    # 提示词评分管理
│   ├── Cubes/            # 记忆立方管理
│   └── MediaModels/      # 媒体模型管理
├── components/
│   └── ResizableModal/   # 可调整大小的弹窗组件
└── utils/
    └── request.ts        # 请求封装（基于 axios）
```

---

### API 代理（开发环境）

`vite.config.ts` 配置的代理规则：

| 前缀 | 转发目标 |
|------|----------|
| `/api` | `http://127.0.0.1:8000` |
| `/ai` | `http://127.0.0.1:8000` |
| `/v1` | `http://127.0.0.1:8000` |


## 后端架构

### 技术栈

- **框架**: FastAPI
- **Python 版本**: 3.10+
- **依赖管理**: Poetry
- **数据验证**: Pydantic

### 目录结构

```
backend/src/memos/api/
├── server_api.py         # FastAPI 应用入口，注册路由、中间件、异常处理
├── routers/              # HTTP 路由层（薄层，委托给 services）
│   ├── auth_router.py
│   ├── work_router.py
│   ├── chapter_router.py
│   ├── ai_router.py      # ~99KB，AI 功能路由
│   ├── product_router.py # ~89KB，产品级 AI 功能
│   ├── admin_router.py
│   ├── feedback_router.py
│   ├── template_router.py
│   ├── prompt_template_router.py
│   ├── volume_router.py
│   ├── sharedb_router.py
│   └── yjs_router.py
├── services/             # 业务逻辑层
├── models/               # SQLAlchemy ORM 模型（PostgreSQL）
├── schemas/              # Pydantic 请求/响应 Schema
├── llms/                 # AI 模型提供商封装
└── core/
    └── config.py         # Settings 类（从 .env 加载所有配置）
```


### 分层职责

```
┌─────────────────────────────────────────────────────────────────┐
│ 路由层 (routers/)                                               │
│ - 接收 HTTP 请求                                                 │
│ - 参数验证（Pydantic）                                           │
│ - 调用服务层                                                     │
│ - 返回响应                                                       │
├─────────────────────────────────────────────────────────────────┤
│ 服务层 (services/)                                              │
│ - 业务逻辑实现                                                   │
│ - 数据库操作                                                     │
│ - AI 接口调用                                                    │
│ - 事务管理                                                       │
├─────────────────────────────────────────────────────────────────┤
│ 模型层 (models/)                                                │
│ - SQLAlchemy ORM 定义                                            │
│ - 数据库表结构                                                   │
├─────────────────────────────────────────────────────────────────┤
│ Schema 层 (schemas/)                                            │
│ - 请求体验证                                                     │
│ - 响应体序列化                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 数据库设计

### PostgreSQL（主数据库）

| 表名 | 用途 | 核心字段 |
|------|------|----------|
| `users` | 用户账户 | id, username, email, password_hash, role |
| `works` | 作品信息 | id, title, work_type, status, owner_id |
| `chapters` | 章节内容 | id, work_id, chapter_number, content |
| `volumes` | 卷信息 | id, work_id, volume_number, title |
| `prompt_templates` | AI 提示词 | id, name, template_content, version |
| `yjs_documents` | 协同快照 | id, chapter_id, snapshot_data, version |
| `token_usage_log` | Token 使用记录 | id, user_id, tokens_used, operation_type |

### MongoDB（ShareDB 文档存储）

用于实时协同编辑的文档操作存储：

```json
{
  "document_id": "chapter_{chapter_id}",
  "content": { /* 文档内容（JSON 格式） */ },
  "version": 42,
  "metadata": { /* 附加元数据 */ }
}
```

### Redis（缓存与会话）

| Key 模式 | 用途 | 过期时间 |
|----------|------|----------|
| `session:{user_id}` | 用户会话 | 会话超时 |
| `blacklist:{token}` | Token 黑名单 | Token 过期时间 |
| `cache:work:{id}` | 作品缓存 | 5 分钟 |
| `rate_limit:{ip}` | 限流计数 | 1 分钟 |

## 实时协同编辑

### 架构流程

```
浏览器 A          浏览器 B
   │                 │
   │  WebSocket      │  WebSocket
   └────────┬────────┘
            ▼
      Yjs WS Handler
      (yjs_ws_handler.py)
            │
            ▼
      Yjs Service
      (yjs_service.py)
            │
    ┌───────┴───────┐
    ▼               ▼
PostgreSQL        MongoDB
(Yjs 快照)      (ShareDB 文档)
```

### 技术方案

- **CRDT 算法**：Yjs（y-websocket + y-indexeddb + y-webrtc）
- **文档同步**：ShareDB + MongoDB 后端
- **离线支持**：y-indexeddb 本地持久化
- **版本管理**：Yjs 快照 API（可标记、恢复历史版本）

---

## AI 集成

### AI 服务层

```
ai_router.py / product_router.py
         │
         ▼
   ai_service.py
         │
   ┌─────┴──────┐
   ▼            ▼
llms/          book_analysis_service.py
(提供商封装)    (书籍分析)
```

### 支持的 AI 提供商

| 提供商 | 配置方式 |
|--------|---------|
| DeepSeek（默认） | `OPENAI_API_BASE=https://api.deepseek.com/v1` |
| OpenAI | `OPENAI_API_BASE=https://api.openai.com/v1` |
| Ollama（本地） | `OPENAI_API_BASE=http://localhost:11434/v1` |
| 任意 OpenAI 兼容接口 | 修改 `OPENAI_API_BASE` 即可 |

### 可选高级功能

| 功能 | 依赖 | 配置 |
|------|------|------|
| 语义搜索 | Qdrant 向量数据库 | `DISABLE_QDRANT=false` |
| 记忆系统 | Neo4j + MemOS | `DISABLE_NEO4J=false` |
| 偏好记忆 | MemOS | `ENABLE_PREFERENCE_MEMORY=true` |

