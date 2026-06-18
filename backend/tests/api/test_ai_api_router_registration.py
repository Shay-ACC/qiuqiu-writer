from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
AI_API_PATH = REPO_ROOT / "backend/src/memos/api/ai_api.py"


def test_product_router_is_registered_once():
    text = AI_API_PATH.read_text(encoding="utf-8")

    assert text.count("include_router(product_router)") == 1
