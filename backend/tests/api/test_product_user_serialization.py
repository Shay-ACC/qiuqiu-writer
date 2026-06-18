import importlib.util
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[3]
SERIALIZATION_PATH = REPO_ROOT / "backend/src/memos/api/serialization.py"

spec = importlib.util.spec_from_file_location("api_serialization", SERIALIZATION_PATH)
serialization = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(serialization)
serialize_product_user = serialization.serialize_product_user


class UserRole(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


def test_serialize_product_user_from_internal_user_object():
    user = SimpleNamespace(
        user_id="u1",
        user_name="Alice",
        role=UserRole.ADMIN,
        created_at=datetime(2026, 6, 16, 8, 0, tzinfo=timezone.utc),
        updated_at=None,
        is_active=True,
    )

    assert serialize_product_user(user) == {
        "user_id": "u1",
        "user_name": "Alice",
        "role": "ADMIN",
        "created_at": "2026-06-16T08:00:00+00:00",
        "updated_at": None,
        "is_active": True,
    }


def test_serialize_product_user_preserves_dict_shape():
    assert serialize_product_user({"user_id": "u1", "role": UserRole.USER}) == {
        "user_id": "u1",
        "role": "USER",
    }
