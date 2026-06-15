# 开发指南

目标：说明本项目的协作流程、常用测试命令、提交规范和 PR 前检查清单。

---

## 推荐分支命名

```bash
git checkout -b docs/improve-local-startup
git checkout -b fix/register-clean-db
git checkout -b chore/update-ci-config
```

建议前缀：

| 前缀 | 用途 |
|------|------|
| `feat/` | 新功能 |
| `fix/` | bug 修复 |
| `docs/` | 文档 |
| `chore/` | 构建、脚本、配置 |
| `test/` | 测试 |

---

## fork + upstream 协作流程

```bash
git clone git@github.com:<your-user>/nspox.git
cd nspox
git remote add upstream https://github.com/nspox-project/nspox.git
git fetch upstream
git checkout main
git merge upstream/main
git checkout -b docs/example-change
```

推送分支：

```bash
git push -u origin docs/example-change
```

---

## Commit 信息规范

使用 Conventional Commits 风格：

```text
feat: add chapter outline editor
fix: align local database schema initialization
docs: improve deployment and development guides
chore: replace weak example credentials
test: cover postgres init schema
```

---

## 当前推荐启动入口

后端推荐入口：

```bash
cd backend
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

历史提示：`backend/Makefile` 的 `serve` 目标仍指向旧入口，不作为当前推荐启动方式。以本文和 [getting-started.md](./getting-started.md) 为准。

---

## 后端依赖和测试

安装依赖：

```bash
cd backend
poetry install --extras all --with dev --with test
```

运行全部后端测试：

```bash
cd backend
poetry run pytest tests
```

运行单个测试：

```bash
cd backend
poetry run pytest tests/api/test_postgres_init_schema.py -q
```

检查 Poetry 配置：

```bash
cd backend
poetry check
```

格式化和 lint：

```bash
cd backend
poetry run ruff check --fix
poetry run ruff format
```

---

## 前端和管理后台检查

用户端：

```bash
cd frontend
npm ci
npm run lint
npm run build
```

管理后台：

```bash
cd admin
npm ci
npm run build
```

不要用 `npm audit fix --force` 修启动问题，它可能改动依赖树并引入非预期升级。

---

## API 和代理

开发环境代理关系：

| 应用 | 本地端口 | 代理目标 |
|------|----------|----------|
| frontend | `5173` | `http://127.0.0.1:8000` |
| admin | `5174` | `http://localhost:8000` |

后端 API docs：

```text
http://localhost:8000/docs
```

---

## 安全扫描

提交前建议运行：

```bash
rg -n "example-placeholder-do-not-use" backend/.env.example docker/.env.example docs README.md
rg -n "OPENAI_API_KEY|SECRET_KEY|TOKEN|PASSWORD" backend/.env.example docker/.env.example docs README.md
```

如果发现真实密钥、token、密码或内部地址，先移除并轮换，不要提交。

---

## 不要提交的文件

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

检查命令：

```bash
git status --short
git diff --stat
git diff --check
```

暂存文件必须精确指定：

```bash
git add README.md docs/getting-started.md
```

不要使用：

```bash
git add .
```

---

## PR 前检查清单

- [ ] 本地文档命令可以复制执行
- [ ] 没有提交 `.env` 或真实凭证
- [ ] 没有提交 `node_modules`、`dist`、`.DS_Store`、`.trae`、`.venv`
- [ ] 后端相关修改已运行对应 pytest
- [ ] 前端相关修改已运行 lint 或 build
- [ ] `git diff --check` 通过
- [ ] `git status --short` 只包含本次 PR 文件
