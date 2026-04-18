import os
from pathlib import Path

from .spreadsheet_utils import list_sqlite_tables


DEFAULT_SQLITE_DB_PATH = "./data/bolty.db"


def build_sqlite_context() -> str:
    db_path = os.environ.get("BOLTY_SQLITE_DB_PATH", DEFAULT_SQLITE_DB_PATH)
    db_resolved = Path(db_path).resolve()
    db_exists = db_resolved.exists()

    table_names: list[str] = []
    if db_exists:
        try:
            table_names = list_sqlite_tables(str(db_resolved))
        except Exception:
            table_names = []

    table_hint = ", ".join(table_names) if table_names else "(none found)"
    return (
        "SQLite data location hint (auto-generated):\n"
        f"- Default DB path: `{db_path}`\n"
        f"- Resolved DB path: `{db_resolved}`\n"
        f"- DB exists: `{str(db_exists).lower()}`\n"
        f"- Tables in DB: {table_hint}\n"
        "When users ask about SQLite table data without specifying a path, "
        "inspect this database first."
    )
