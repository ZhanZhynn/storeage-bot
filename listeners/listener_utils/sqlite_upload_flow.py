import json
import os
import re
import shutil
from pathlib import Path

from ai.utils.spreadsheet_utils import (
    is_spreadsheet_path,
    list_sqlite_tables,
    normalize_dataframe,
    read_spreadsheet_sheets,
    upload_spreadsheet_to_sqlite,
    verify_spreadsheet_against_sqlite_schema,
)


DEFAULT_SQLITE_DB_PATH = "./data/bolty.db"
UPLOAD_SESSION_STORE = Path("./data/sqlite_upload_sessions.json")
UPLOAD_FILE_DIR = Path("./data/sqlite_upload_files")
SQLITE_UPLOAD_QUICK_REPLY_ACTION_ID = "sqlite_upload_quick_reply"
SQLITE_UPLOAD_CREATE_TABLE_ACTION_ID = "sqlite_upload_create_table"
SQLITE_UPLOAD_SHARED_MODE_ACTION_ID = "sqlite_upload_use_shared_mode"
SQLITE_UPLOAD_CONFIRM_ACTION_ID = "sqlite_upload_confirm_upload"
SQLITE_UPLOAD_CANCEL_ACTION_ID = "sqlite_upload_cancel"
SQLITE_UPLOAD_QUICK_REPLY_ACTION_IDS = (
    SQLITE_UPLOAD_CREATE_TABLE_ACTION_ID,
    SQLITE_UPLOAD_SHARED_MODE_ACTION_ID,
    SQLITE_UPLOAD_CONFIRM_ACTION_ID,
    SQLITE_UPLOAD_CANCEL_ACTION_ID,
)


def process_sqlite_upload_message(
    user_id: str,
    channel_id: str,
    thread_ts: str | None,
    text: str | None,
    file_paths: list[str] | None,
) -> tuple[bool, str | None]:
    session_key = _session_key(user_id, channel_id, thread_ts)
    text_value = (text or "").strip()
    sessions = _read_sessions()
    pending = sessions.get(session_key)

    if pending:
        if _is_cancel(text_value):
            _cleanup_session_file(pending)
            sessions.pop(session_key, None)
            _write_sessions(sessions)
            return True, "Cancelled SQLite upload session."

        if not pending.get("file_path"):
            spreadsheet_paths = [path for path in (file_paths or []) if is_spreadsheet_path(path)]
            if spreadsheet_paths:
                pending["file_path"] = _persist_uploaded_file(spreadsheet_paths[0], session_key)
            else:
                sessions[session_key] = pending
                _write_sessions(sessions)
                return (
                    True,
                    "Please attach a CSV/XLSX/XLS file in this thread, then I can verify schema and upload.",
                )

        updated = _update_session_from_user_text(pending, text_value)
        sessions[session_key] = updated
        handled, response = _resolve_pending_session(session_key, updated, sessions)
        return handled, response

    if not _is_upload_intent(text_value):
        return False, None

    spreadsheet_paths = [path for path in (file_paths or []) if is_spreadsheet_path(path)]
    if not spreadsheet_paths:
        return (
            True,
            "To upload into SQLite, attach a CSV/XLSX/XLS file and include target details like "
            "`upload to table sales`.",
        )

    db_path = os.environ.get("BOLTY_SQLITE_DB_PATH", DEFAULT_SQLITE_DB_PATH)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    persisted_path = _persist_uploaded_file(spreadsheet_paths[0], session_key)
    requested_table = _extract_table_name(text_value)
    requested_sheet = _extract_sheet_name(text_value)

    session = {
        "db_path": db_path,
        "file_path": persisted_path,
        "table_name": requested_table,
        "sheet_name": requested_sheet,
        "strict_schema": True,
        "allow_create_table": False,
        "awaiting_confirmation": False,
    }
    session = _update_session_from_user_text(session, text_value)
    sessions[session_key] = session

    handled, response = _resolve_pending_session(session_key, session, sessions)
    return handled, response


def start_sqlite_upload_session(
    user_id: str,
    channel_id: str,
    thread_ts: str | None,
    initial_text: str | None = None,
) -> str:
    session_key = _session_key(user_id, channel_id, thread_ts)
    sessions = _read_sessions()

    db_path = os.environ.get("BOLTY_SQLITE_DB_PATH", DEFAULT_SQLITE_DB_PATH)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    session = {
        "db_path": db_path,
        "file_path": None,
        "table_name": None,
        "sheet_name": None,
        "strict_schema": True,
        "allow_create_table": False,
        "awaiting_confirmation": False,
    }
    if initial_text:
        session = _update_session_from_user_text(session, initial_text)

    sessions[session_key] = session
    _write_sessions(sessions)

    tables = list_sqlite_tables(db_path)
    table_hint = (
        f"Available tables: {', '.join(tables)}"
        if tables
        else "No tables found yet. You can say `create table <name>`."
    )

    selected_table = session.get("table_name")
    table_line = f"Current target table: `{selected_table}`." if selected_table else ""
    return (
        "SQLite upload session started. Reply in this thread with your spreadsheet file "
        "(CSV/XLSX/XLS).\n"
        f"DB path: `{db_path}`.\n"
        f"{table_hint}\n"
        f"{table_line}\n"
        "Optional commands: `table <name>`, `sheet <name>`, `mode shared`, "
        "`mode strict`, `create table <name>`, `confirm upload`, `cancel`."
    ).strip()


def build_sqlite_upload_reply(
    user_id: str,
    channel_id: str,
    thread_ts: str | None,
    response_text: str,
) -> dict:
    sessions = _read_sessions()
    session = sessions.get(_session_key(user_id, channel_id, thread_ts))
    return _build_reply_payload(response_text, session)


def _resolve_pending_session(
    session_key: str, session: dict, sessions: dict
) -> tuple[bool, str]:
    db_path = session["db_path"]
    table_names = list_sqlite_tables(db_path)
    sheet_names = list(read_spreadsheet_sheets(session["file_path"]).keys())

    if not session.get("table_name"):
        _write_sessions(sessions)
        tables = ", ".join(table_names) if table_names else "(none found)"
        return True, f"Which SQLite table should I upload to? Available tables: {tables}"

    table_name = session["table_name"]
    table_exists = table_name in table_names
    if not table_exists and not session.get("allow_create_table", False):
        sessions[session_key] = session
        _write_sessions(sessions)
        return (
            True,
            f"Table `{table_name}` does not exist in `{db_path}`. "
            "Reply with `create table <name>` to create it from spreadsheet headers, "
            "or provide an existing table name.",
        )

    if len(sheet_names) > 1 and not session.get("sheet_name"):
        sessions[session_key] = session
        _write_sessions(sessions)
        return (
            True,
            "Which sheet should I upload? Available sheets: " + ", ".join(sheet_names),
        )

    selected_sheet = session.get("sheet_name") or sheet_names[0]
    if selected_sheet not in sheet_names:
        sessions[session_key] = session
        _write_sessions(sessions)
        return (
            True,
            "I could not find that sheet. Available sheets: " + ", ".join(sheet_names),
        )

    if table_exists:
        frame = normalize_dataframe(read_spreadsheet_sheets(session["file_path"])[selected_sheet])
        verification = verify_spreadsheet_against_sqlite_schema(frame, db_path, table_name)
        if not verification["is_compatible"] and session.get("strict_schema", True):
            sessions[session_key] = session
            _write_sessions(sessions)
            return (
                True,
                "Schema check found mismatches. "
                f"Missing columns: {verification['missing_columns'] or 'none'}. "
                f"Extra columns: {verification['extra_columns'] or 'none'}. "
                f"Type issues: {verification['type_issues'] or 'none'}. "
                "Reply with `mode shared` to upload only shared columns, or fix table/sheet.",
            )

    if session.get("confirmed"):
        session["awaiting_confirmation"] = True
    elif not session.get("awaiting_confirmation"):
        session["awaiting_confirmation"] = True
        sessions[session_key] = session
        _write_sessions(sessions)
        return (
            True,
            "Ready to upload. "
            f"DB: `{db_path}`; table: `{table_name}`; sheet: `{selected_sheet}`; "
            f"mode: {'strict' if session.get('strict_schema', True) else 'shared'}. "
            "Reply `confirm upload` to proceed or `cancel` to stop.",
        )

    if not session.get("confirmed"):
        sessions[session_key] = session
        _write_sessions(sessions)
        return True, "Reply `confirm upload` to proceed, or `cancel` to stop."

    result = upload_spreadsheet_to_sqlite(
        file_path=session["file_path"],
        sqlite_db_path=db_path,
        table_name=table_name,
        sheet_name=selected_sheet,
        strict_schema=session.get("strict_schema", True),
        allow_create_table=session.get("allow_create_table", False),
    )

    _cleanup_session_file(session)
    sessions.pop(session_key, None)
    _write_sessions(sessions)
    verification = result.get("verification", {})
    missing_count = len(verification.get("missing_columns", []))
    extra_count = len(verification.get("extra_columns", []))
    type_issue_count = len(verification.get("type_issues", []))
    mode_text = "strict" if session.get("strict_schema", True) else "shared"
    return (
        True,
        f"Upload complete to `{db_path}` table `{result['table_name']}` from sheet "
        f"`{result['sheet_name']}`. "
        f"Summary: {result['row_count_uploaded']} rows, {result['column_count_uploaded']} columns, "
        f"mode {mode_text}, missing cols {missing_count}, extra cols {extra_count}, "
        f"type issues {type_issue_count}.",
    )


def _build_reply_payload(response_text: str, session: dict | None = None) -> dict:
    payload: dict = {"text": response_text}
    completion_blocks = _build_completion_blocks(response_text)
    if completion_blocks:
        payload["blocks"] = completion_blocks
        return payload

    actions: list[dict] = []

    if (
        "Reply with `create table <name>`" in response_text
        and session
        and session.get("table_name")
    ):
        table_name = session["table_name"]
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_CREATE_TABLE_ACTION_ID,
                "text": {"type": "plain_text", "text": f"Create table {table_name}"},
                "style": "primary",
                "value": f"create table {table_name}",
            }
        )

    if "Schema check found mismatches." in response_text:
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_SHARED_MODE_ACTION_ID,
                "text": {"type": "plain_text", "text": "Use shared mode"},
                "value": "mode shared",
            }
        )

    if "Reply `confirm upload` to proceed" in response_text or response_text.startswith(
        "Ready to upload."
    ):
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_CONFIRM_ACTION_ID,
                "text": {"type": "plain_text", "text": "Confirm upload"},
                "style": "primary",
                "value": "confirm upload",
            }
        )

    if actions:
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_CANCEL_ACTION_ID,
                "text": {"type": "plain_text", "text": "Cancel"},
                "style": "danger",
                "value": "cancel",
            }
        )
        payload["blocks"] = [
            {"type": "section", "text": {"type": "mrkdwn", "text": response_text}},
            {"type": "actions", "elements": actions},
        ]

    return payload


def _build_completion_blocks(response_text: str) -> list[dict] | None:
    match = re.match(
        r"^Upload complete to `([^`]+)` table `([^`]+)` from sheet `([^`]+)`\. "
        r"Summary: (\d+) rows, (\d+) columns, mode (strict|shared), "
        r"missing cols (\d+), extra cols (\d+), type issues (\d+)\.$",
        response_text,
    )
    if not match:
        return None

    (
        db_path,
        table_name,
        sheet_name,
        row_count,
        column_count,
        mode,
        missing_count,
        extra_count,
        type_issue_count,
    ) = match.groups()

    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": ":white_check_mark: *Upload complete*"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*DB*\n`{db_path}`"},
                {"type": "mrkdwn", "text": f"*Table*\n`{table_name}`"},
                {"type": "mrkdwn", "text": f"*Sheet*\n`{sheet_name}`"},
                {"type": "mrkdwn", "text": f"*Mode*\n`{mode}`"},
                {"type": "mrkdwn", "text": f"*Rows uploaded*\n`{row_count}`"},
                {"type": "mrkdwn", "text": f"*Columns uploaded*\n`{column_count}`"},
                {"type": "mrkdwn", "text": f"*Missing cols*\n`{missing_count}`"},
                {"type": "mrkdwn", "text": f"*Extra cols*\n`{extra_count}`"},
                {"type": "mrkdwn", "text": f"*Type issues*\n`{type_issue_count}`"},
            ],
        },
    ]


def _update_session_from_user_text(session: dict, text: str) -> dict:
    if not text:
        return session

    table_name = _extract_table_name(text)
    if table_name:
        session["table_name"] = table_name

    create_table = _extract_create_table_name(text)
    if create_table:
        session["table_name"] = create_table
        session["allow_create_table"] = True

    sheet_name = _extract_sheet_name(text)
    if sheet_name:
        session["sheet_name"] = sheet_name

    lowered = text.lower()
    if "mode shared" in lowered or "shared columns" in lowered:
        session["strict_schema"] = False
    if "mode strict" in lowered:
        session["strict_schema"] = True
    if "confirm upload" in lowered or lowered.strip() in {"confirm", "yes", "y"}:
        session["confirmed"] = True

    return session


def _persist_uploaded_file(file_path: str, session_key: str) -> str:
    UPLOAD_FILE_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file_path).suffix
    destination = UPLOAD_FILE_DIR / f"{_safe_name(session_key)}{suffix}"
    shutil.copyfile(file_path, destination)
    return str(destination)


def _cleanup_session_file(session: dict):
    path = session.get("file_path")
    if not path:
        return
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def _read_sessions() -> dict:
    try:
        if not UPLOAD_SESSION_STORE.exists():
            return {}
        with UPLOAD_SESSION_STORE.open("r") as file:
            return json.load(file)
    except Exception:
        return {}


def _write_sessions(sessions: dict):
    UPLOAD_SESSION_STORE.parent.mkdir(parents=True, exist_ok=True)
    with UPLOAD_SESSION_STORE.open("w") as file:
        json.dump(sessions, file)


def _session_key(user_id: str, channel_id: str, thread_ts: str | None) -> str:
    thread = thread_ts or "root"
    return f"{user_id}:{channel_id}:{thread}"


def _is_upload_intent(text: str) -> bool:
    lowered = text.lower()
    if not lowered:
        return False
    return (
        "sqlite" in lowered
        or "database" in lowered
        or "upload" in lowered
        or "import" in lowered
    )


def _is_cancel(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return lowered in {"cancel", "stop", "never mind", "nevermind"}


def _extract_table_name(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r"(?:to|into|table)\s+([a-zA-Z_][a-zA-Z0-9_]*)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _extract_create_table_name(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r"create\s+table\s+([a-zA-Z_][a-zA-Z0-9_]*)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _extract_sheet_name(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r"sheet\s+([a-zA-Z0-9_\- ]+)", text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", value)
