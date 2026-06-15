import ast
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
USER_MODEL_PATH = REPO_ROOT / "backend/src/memos/api/models/user.py"
INIT_SQL_PATH = REPO_ROOT / "docker/postgres/init/01-init.sql"


def user_model_columns() -> set[str]:
    tree = ast.parse(USER_MODEL_PATH.read_text(encoding="utf-8"))

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "User":
            columns: set[str] = set()
            for stmt in node.body:
                if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
                    continue
                target = stmt.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                value = stmt.value
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "Column":
                    columns.add(target.id)
            return columns

    raise AssertionError("User model class not found")


def init_sql_users_columns() -> set[str]:
    text = INIT_SQL_PATH.read_text(encoding="utf-8")
    match = re.search(r"CREATE TABLE public\.users \(\n(?P<body>.*?)\n\);", text, re.DOTALL)
    assert match is not None, "public.users table definition not found in init SQL"

    columns: set[str] = set()
    for line in match.group("body").splitlines():
        stripped = line.strip().rstrip(",")
        if not stripped:
            continue
        columns.add(stripped.split(maxsplit=1)[0].strip('"'))

    return columns


def test_postgres_init_users_table_matches_user_model_columns():
    missing_columns = sorted(user_model_columns() - init_sql_users_columns())

    assert missing_columns == []
