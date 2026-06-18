# 4A100 Deployment Bug Report

Date: 2026-06-16

Repository commit tested: `4e98e67`

Remote host: `4A100` (`wnds-server`, `/home/duxianghe`)

Deployment path:

```text
/home/duxianghe/nspox-deployments/nspox-4e98e67-codex-deploy
```

Temporary service URLs:

```text
Frontend: http://10.154.22.10:18180/
Admin:    http://10.154.22.10:18189/
Backend:  http://10.154.22.10:18100/docs
```

## Deployment Summary

I deployed the project on `4A100` with an isolated Compose stack named `nspox-codex` to avoid interfering with the existing `qiuqiuwriter-*` containers already running on the server.

Services started:

```text
nspox-codex-postgres   postgres:16-alpine
nspox-codex-redis      redis:7-alpine
nspox-codex-mongodb    mongo:7
nspox-codex-backend    qiuqiuwriter-backend:latest with current backend source mounted
nspox-codex-frontend   nginx:alpine, frontend/dist
nspox-codex-admin      nginx:alpine, admin/dist
```

Frontend and admin builds succeeded with `npm ci && npm run build`.

Smoke checks that passed:

```text
GET /ai/health via backend: 200
GET /ai/health via frontend nginx proxy: 200
GET /docs: 200
Frontend homepage: rendered in browser, no console warnings/errors
Admin login page: rendered in browser
Postgres users table contains new plan/token/media columns
Seeded admin weak-password probe did not match common weak passwords tested
```

## Fix Status

Updated on 2026-06-16:

```text
BUG-1 fixed locally and verified on 4A100.
BUG-2 fixed locally and verified on 4A100.
BUG-3 fixed locally and script syntax verified on 4A100.
```

Fix summary:

- `backend/src/memos/api/routers/product_router.py` now serializes users returned by `mos_product.list_users()` before putting them in `BaseResponse.data`.
- `backend/src/memos/api/ai_api.py` now registers `product_router` once.
- `start.sh`, `Makefile`, and `deploy.sh` now use Docker Compose v2 (`docker compose`) instead of the old `docker-compose` command.

Verification after patching the mounted 4A100 deployment:

```text
GET http://127.0.0.1:18100/api/v1/product/users
HTTP/1.1 200 OK
{"code":200,"message":"Users retrieved successfully","data":[{"user_id":"root","user_name":"root","role":"ROOT",...}]}

GET http://127.0.0.1:18100/openapi.json
HTTP/1.1 200 OK, 204488 bytes

docker logs --since 2m nspox-codex-backend
No duplicate operation ID warnings after requesting /openapi.json.

bash -n start.sh deploy.sh
Passed on 4A100.
```

## Bugs Found

### BUG-1: `GET /api/v1/product/users` returns 400 because response contains non-serializable `User` objects

Severity: High

Evidence from deployed backend:

```text
GET http://127.0.0.1:18100/api/v1/product/users

HTTP/1.1 400 Bad Request
{"code":400,"message":"Unable to serialize unknown type: <class 'memos.mem_user.user_manager.User'>","data":null}
```

The same failure happens through frontend nginx:

```text
GET http://127.0.0.1:18180/api/v1/product/users
HTTP/1.1 400 Bad Request
```

Backend log:

```text
ValueError: Unable to serialize unknown type: <class 'memos.mem_user.user_manager.User'>
```

Likely cause:

```python
# backend/src/memos/api/routers/product_router.py
@router.get("/users", summary="List all users", response_model=BaseResponse[list])
def list_users():
    mos_product = get_mos_product_instance()
    users = mos_product.list_users()
    return BaseResponse(message="Users retrieved successfully", data=users)
```

`mos_product.list_users()` returns MemOS internal `User` objects. They need to be converted to dicts or Pydantic response models before returning.

Additional impact:

The first request to this endpoint took about 36 seconds because it initialized the MOS product/embedder stack before failing. Later requests failed faster after initialization.

Suggested fix:

Serialize each returned user explicitly, for example with `model_dump`, `dict`, dataclass conversion, or a small response DTO. Also consider avoiding heavy MOS/embedder initialization for a simple list-users endpoint.

### BUG-2: `product_router` is registered twice, causing duplicate OpenAPI operation IDs

Severity: Medium

Evidence from backend logs after requesting `/openapi.json`:

```text
UserWarning: Duplicate Operation ID list_users_api_v1_product_users_get for function list_users
UserWarning: Duplicate Operation ID chat_api_v1_product_chat_post for function chat
...
```

Cause:

```python
# backend/src/memos/api/ai_api.py
app.include_router(product_router)  # first registration

# later in the same file
from memos.api.routers.product_router import router as product_router
app.include_router(product_router)  # second registration
```

Impact:

FastAPI registers duplicate routes and emits duplicate OpenAPI operation IDs. This can break generated clients, make docs noisy, and make route behavior harder to reason about.

Suggested fix:

Register `product_router` exactly once in `ai_api.py`.

### BUG-3: Documented Docker start path uses `docker-compose` v1, but compose files require v2 syntax

Severity: High for fresh deployments using `start.sh`

Evidence on `4A100`:

```text
docker-compose -f docker/docker-compose.app.yml config

The Compose file ... is invalid because:
'name' does not match any of the regexes: '^x-'
```

Cause:

`start.sh` invokes `docker-compose`, while the compose files use top-level `name:`, which Docker Compose v1 rejects. The server has both:

```text
docker compose version 2.40.3
docker-compose version 1.29.2
```

So `start.sh --docker ...` can fail even though Docker Compose v2 is available.

Suggested fix:

Update scripts and docs to use `docker compose` v2 consistently, or remove/avoid v2-only fields if v1 support is required.

## Notes

The deployed stack is intentionally isolated from existing services on `4A100` by using ports `18100`, `18180`, and `18189`.

The official default compose files use fixed container names such as `qiuqiuwriter-backend`, `qiuqiuwriter-postgres`, and default/common ports. This is fine for a single deployment, but it prevents parallel deployments on a shared server unless override files are used.

## Verification Commands Used

```bash
curl -s -i http://127.0.0.1:18100/ai/health
curl -s -i http://127.0.0.1:18180/ai/health
curl -s -i http://127.0.0.1:18100/api/v1/product/users
curl -s -i http://127.0.0.1:18180/api/v1/product/users
docker exec nspox-codex-postgres psql -U postgres -d writerai -c "select count(*) from users;"
docker logs --tail 200 nspox-codex-backend
```
