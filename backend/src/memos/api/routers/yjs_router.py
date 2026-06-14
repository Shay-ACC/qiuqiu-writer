"""
Y-WebSocket Router

Provides WebSocket endpoints for Yjs real-time collaborative editing.
Compatible with the y-websocket npm package's WebsocketProvider.

Usage from frontend:
  new WebsocketProvider('ws://server/api/v1/yjs', roomName, ydoc)
  → connects to ws://server/api/v1/yjs/{roomName}
"""

import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketException, status

from memos.api.core.security import verify_token
from memos.api.services.yjs_ws_handler import yjs_ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/yjs", tags=["yjs"])


async def authorize_yjs_room_access(user_id: str, room_name: str) -> bool:
    """
    Pluggable room authorization boundary for Yjs.

    TODO: Parse work-scoped room names and call WorkService.can_access_work once
    the room naming contract is fully normalized across legacy clients.
    """
    return bool(user_id and room_name)


async def authenticate_yjs_connection(token: Optional[str], room_name: str) -> str:
    if not token:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Missing token",
        )

    payload = verify_token(token, token_type="access")
    if not payload:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid or expired token",
        )

    user_id_raw = str(payload.get("sub") or "")
    if not user_id_raw:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token payload",
        )

    try:
        from memos.api.core.id_utils import normalize_legacy_id

        user_id = normalize_legacy_id(user_id_raw) or user_id_raw
    except Exception:
        user_id = user_id_raw

    if not await authorize_yjs_room_access(user_id, room_name):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Room access denied",
        )

    return user_id


@router.post("/{room_name}/sync")
async def force_sync(room_name: str):
    """
    Force a database sync for a room.
    Useful when switching chapters to ensure immediate persistence to MongoDB.
    """
    success = await yjs_ws_manager.force_sync(room_name)
    return {"success": success, "room": room_name}


@router.websocket("/{room_name}")
async def yjs_websocket(
    websocket: WebSocket,
    room_name: str,
    token: Optional[str] = None,
):
    """
    Y-WebSocket endpoint for real-time collaboration.

    Room name format: "work_{workId}" (one WebSocket per work; chapters use
    Y.Doc fragments "chapter_{chapterId}")
    Optional query param: ?token=xxx for authentication

    The endpoint speaks the standard y-websocket binary protocol:
    - Sync messages (type 0): document state synchronization
    - Awareness messages (type 1): cursor position relay
    """
    try:
        user_id = await authenticate_yjs_connection(token, room_name)
    except WebSocketException as exc:
        await websocket.close(code=exc.code, reason=exc.reason or "Unauthorized")
        return

    await websocket.accept()

    logger.info(f"[YjsRouter] New connection for room: {room_name}, user: {user_id}")
    await yjs_ws_manager.handle_connection(websocket, room_name)
