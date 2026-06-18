from collections.abc import Mapping
from datetime import date, datetime
from enum import Enum
from typing import Any


PRODUCT_USER_FIELDS = (
    "user_id",
    "user_name",
    "role",
    "created_at",
    "updated_at",
    "is_active",
    "email",
    "display_name",
    "avatar_url",
    "phone",
)


def to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [to_jsonable(item) for item in value]

    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return to_jsonable(model_dump(mode="json"))

    dict_method = getattr(value, "dict", None)
    if callable(dict_method):
        return to_jsonable(dict_method())

    return str(value)


def serialize_product_user(user: Any) -> dict[str, Any]:
    if isinstance(user, Mapping):
        return to_jsonable(user)

    data: dict[str, Any] = {}
    for field in PRODUCT_USER_FIELDS:
        if not hasattr(user, field):
            continue
        try:
            data[field] = to_jsonable(getattr(user, field))
        except Exception:
            continue

    if data:
        return data

    return {"value": to_jsonable(user)}
