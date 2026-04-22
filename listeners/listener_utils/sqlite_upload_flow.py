import hashlib
import json
import os
import re
import shutil
import warnings
from pathlib import Path
from uuid import uuid4

import pandas as pd

from ai.providers import get_provider_response
from ai.utils.shopee_orders_normalizer import normalize_shopee_orders_to_sqlite
from ai.utils.spreadsheet_utils import (
    is_spreadsheet_path, list_sqlite_tables, normalize_dataframe,
    read_spreadsheet_sheets, suggest_schema_column_mapping,
    upload_spreadsheet_to_sqlite, verify_spreadsheet_against_sqlite_schema)

DEFAULT_SQLITE_DB_PATH = "./data/bolty.db"
DEFAULT_SHOPEE_ORDERS_TABLE = "shopee_orders"
DEFAULT_SHOPEE_ORDER_ITEMS_TABLE = "shopee_order_items"
SHOPEE_REQUIRED_CANONICAL_HEADERS = {
    "order_id",
    "order_status",
    "order_creation_date",
    "order_paid_time",
    "sku_reference_no",
    "quantity",
}
UPLOAD_SESSION_STORE = Path("./data/sqlite_upload_sessions.json")
UPLOAD_FILE_DIR = Path("./data/sqlite_upload_files")
SQLITE_UPLOAD_QUICK_REPLY_ACTION_ID = "sqlite_upload_quick_reply"
SQLITE_UPLOAD_CREATE_TABLE_ACTION_ID = "sqlite_upload_create_table"
SQLITE_UPLOAD_SHARED_MODE_ACTION_ID = "sqlite_upload_use_shared_mode"
SQLITE_UPLOAD_MAP_MODE_ACTION_ID = "sqlite_upload_use_map_mode"
SQLITE_UPLOAD_LLM_MODE_ACTION_ID = "sqlite_upload_use_llm_mode"
SQLITE_UPLOAD_CAST_ZIP_TEXT_ACTION_ID = "sqlite_upload_cast_zip_text"
SQLITE_UPLOAD_APPROVE_SCHEMA_ACTION_ID = "sqlite_upload_approve_schema"
SQLITE_UPLOAD_SCHEMA_ALL_ACTION_ID = "sqlite_upload_schema_all"
SQLITE_UPLOAD_CONFIRM_ACTION_ID = "sqlite_upload_confirm_upload"
SQLITE_UPLOAD_CANCEL_ACTION_ID = "sqlite_upload_cancel"
SQLITE_UPLOAD_QUICK_REPLY_ACTION_IDS = (
    SQLITE_UPLOAD_CREATE_TABLE_ACTION_ID,
    SQLITE_UPLOAD_SHARED_MODE_ACTION_ID,
    SQLITE_UPLOAD_MAP_MODE_ACTION_ID,
    SQLITE_UPLOAD_LLM_MODE_ACTION_ID,
    SQLITE_UPLOAD_CAST_ZIP_TEXT_ACTION_ID,
    SQLITE_UPLOAD_APPROVE_SCHEMA_ACTION_ID,
    SQLITE_UPLOAD_SCHEMA_ALL_ACTION_ID,
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
            _cleanup_session_files(pending)
            sessions.pop(session_key, None)
            _write_sessions(sessions)
            return True, "Cancelled SQLite upload session."

        spreadsheet_paths = [path for path in (file_paths or []) if is_spreadsheet_path(path)]
        if spreadsheet_paths:
            pending = _append_session_files(session_key, pending, spreadsheet_paths)

        if not _get_session_file_paths(pending):
            sessions[session_key] = pending
            _write_sessions(sessions)
            return (
                True,
                "Please attach one or more CSV/XLSX/XLS files in this thread, then I can verify schema and upload.",
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

    requested_table = _extract_table_name(text_value)
    requested_sheet = _extract_sheet_name(text_value)

    session = {
        "db_path": db_path,
        "file_paths": [],
        "current_file_index": 0,
        "table_name": requested_table,
        "shopee_mode": False,
        "sheet_name": requested_sheet,
        "strict_schema": True,
        "use_llm_resolution": False,
        "allow_create_table": False,
        "schema_review_approved": False,
        "column_mapping": {},
        "type_casts": {},
        "create_table_column_types": {},
        "schema_preview_all": False,
        "schema_preview_page": 0,
        "schema_preview_column": None,
        "seen_file_hashes": [],
        "awaiting_confirmation": False,
    }
    session = _append_session_files(session_key, session, spreadsheet_paths)
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
        "file_paths": [],
        "current_file_index": 0,
        "table_name": None,
        "shopee_mode": False,
        "sheet_name": None,
        "strict_schema": True,
        "use_llm_resolution": False,
        "allow_create_table": False,
        "schema_review_approved": False,
        "column_mapping": {},
        "type_casts": {},
        "create_table_column_types": {},
        "schema_preview_all": False,
        "schema_preview_page": 0,
        "schema_preview_column": None,
        "seen_file_hashes": [],
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
        "`mode map`, `mode llm`, `cast <column> as <type>`, `mode strict`, "
        "`schema all`, `schema page <n>`, `schema col <name>`, `set schema <name> as <type>`, `set schema: col=type, ...`, `reset schema types`, "
        "`create table <name>`, `approve schema`, `confirm upload`, `cancel`."
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
    queued_files = _get_session_file_paths(session)
    if not queued_files:
        sessions[session_key] = session
        _write_sessions(sessions)
        return True, "Please attach a CSV/XLSX/XLS file to continue this upload session."

    current_file_index = int(session.get("current_file_index", 0) or 0)
    if current_file_index < 0:
        current_file_index = 0
    if current_file_index >= len(queued_files):
        current_file_index = len(queued_files) - 1
    session["current_file_index"] = current_file_index
    current_file_path = queued_files[current_file_index]

    table_names = list_sqlite_tables(db_path)
    sheet_names = list(read_spreadsheet_sheets(current_file_path).keys())

    selected_sheet = session.get("sheet_name") or sheet_names[0]
    if selected_sheet not in sheet_names:
        sessions[session_key] = session
        _write_sessions(sessions)
        return (
            True,
            "I could not find that sheet. Available sheets: " + ", ".join(sheet_names),
        )

    if _looks_like_shopee_orders_report(current_file_path, selected_sheet):
        session["shopee_mode"] = True
        session["table_name"] = DEFAULT_SHOPEE_ORDERS_TABLE
    elif not session.get("shopee_mode"):
        session["shopee_mode"] = False

    if not session.get("table_name") and not session.get("shopee_mode"):
        _write_sessions(sessions)
        tables = ", ".join(table_names) if table_names else "(none found)"
        return True, f"Which SQLite table should I upload to? Available tables: {tables}"

    table_name = session["table_name"]
    table_exists = table_name in table_names
    if (
        not session.get("shopee_mode")
        and not table_exists
        and not session.get("allow_create_table", False)
    ):
        sessions[session_key] = session
        _write_sessions(sessions)
        return (
            True,
            f"Table `{table_name}` does not exist in `{db_path}`. "
            "Reply with `create table <name>` to create it from spreadsheet headers, "
            "or provide an existing table name.",
        )

    if len(sheet_names) > 1 and not session.get("sheet_name") and not session.get("shopee_mode"):
        sessions[session_key] = session
        _write_sessions(sessions)
        return (
            True,
            "Which sheet should I upload? Available sheets: " + ", ".join(sheet_names),
        )

    if not session.get("shopee_mode") and not table_exists and session.get("allow_create_table", False):
        frame = normalize_dataframe(read_spreadsheet_sheets(current_file_path)[selected_sheet])
        schema_preview = _infer_schema_preview(frame)
        schema_overrides = _normalize_type_overrides_for_schema(
            session.get("create_table_column_types") or {}
        )
        if not session.get("schema_review_approved", False):
            sessions[session_key] = session
            _write_sessions(sessions)
            return (
                True,
                _format_create_table_schema_review(
                    table_name=table_name,
                    sheet_name=selected_sheet,
                    file_name=Path(current_file_path).name,
                    schema_preview=schema_preview,
                    schema_overrides=schema_overrides,
                    show_all=bool(session.get("schema_preview_all", False)),
                    current_page=max(0, int(session.get("schema_preview_page", 0) or 0)),
                    focus_column=(session.get("schema_preview_column") or "").strip() or None,
                ),
            )

    if not session.get("shopee_mode") and table_exists:
        frame = normalize_dataframe(read_spreadsheet_sheets(current_file_path)[selected_sheet])
        if session.get("column_mapping"):
            frame = frame.rename(
                columns={
                    source: target
                    for target, source in (session.get("column_mapping") or {}).items()
                }
            )
        if session.get("apply_suggested_mapping", False):
            suggested_mapping = suggest_schema_column_mapping(
                sqlite_db_path=db_path,
                table_name=table_name,
                spreadsheet_columns=[str(column) for column in frame.columns],
            )["mapping"]
            if suggested_mapping:
                frame = frame.rename(
                    columns={source: target for target, source in suggested_mapping.items()}
                )

        verification = verify_spreadsheet_against_sqlite_schema(
            frame,
            db_path,
            table_name,
            type_overrides=session.get("type_casts") or {},
        )
        if not verification["is_compatible"] and session.get("strict_schema", True):
            if session.get("use_llm_resolution"):
                llm_resolution = _build_llm_resolution(
                    session_key=session_key,
                    table_name=table_name,
                    verification=verification,
                )
                if llm_resolution:
                    session["column_mapping"] = llm_resolution.get("column_mapping", {})
                    session["type_casts"] = {
                        **(session.get("type_casts") or {}),
                        **(llm_resolution.get("type_casts") or {}),
                    }
                    sessions[session_key] = session
                    _write_sessions(sessions)
                    return (
                        True,
                        _format_llm_resolution_message(
                            column_mapping=session.get("column_mapping") or {},
                            type_casts=session.get("type_casts") or {},
                            reasoning=llm_resolution.get("reasoning") or "",
                        ),
                    )

            sessions[session_key] = session
            _write_sessions(sessions)
            return True, _format_schema_mismatch_message(verification)

    if session.get("confirmed"):
        session["awaiting_confirmation"] = True
    elif not session.get("awaiting_confirmation"):
        session["awaiting_confirmation"] = True
        sessions[session_key] = session
        _write_sessions(sessions)
        file_name = Path(current_file_path).name
        file_position = f"{current_file_index + 1}/{len(queued_files)}"
        if session.get("shopee_mode"):
            return (
                True,
                "Ready to upload. Shopee orders normalization. "
                f"File: `{file_name}` ({file_position}); "
                f"DB: `{db_path}`; tables: `{DEFAULT_SHOPEE_ORDERS_TABLE}` + `{DEFAULT_SHOPEE_ORDER_ITEMS_TABLE}`; "
                f"sheet: `{selected_sheet}`. "
                "Reply `confirm upload` to proceed or `cancel` to stop.",
            )
        return (
            True,
            "Ready to upload. "
            f"File: `{file_name}` ({file_position}); "
            f"DB: `{db_path}`; table: `{table_name}`; sheet: `{selected_sheet}`; "
            f"mode: {'strict' if session.get('strict_schema', True) else 'shared'}. "
            "Reply `confirm upload` to proceed or `cancel` to stop.",
        )

    if not session.get("confirmed"):
        sessions[session_key] = session
        _write_sessions(sessions)
        return True, "Reply `confirm upload` to proceed, or `cancel` to stop."

    if session.get("shopee_mode"):
        result = normalize_shopee_orders_to_sqlite(
            file_path=current_file_path,
            sqlite_db_path=db_path,
            sheet_name=selected_sheet,
            orders_table=DEFAULT_SHOPEE_ORDERS_TABLE,
            order_items_table=DEFAULT_SHOPEE_ORDER_ITEMS_TABLE,
        )
    else:
        result = upload_spreadsheet_to_sqlite(
            file_path=current_file_path,
            sqlite_db_path=db_path,
            table_name=table_name,
            sheet_name=selected_sheet,
            strict_schema=session.get("strict_schema", True),
            allow_create_table=session.get("allow_create_table", False),
            apply_suggested_mapping=session.get("apply_suggested_mapping", False),
            type_casts=session.get("type_casts") or {},
            column_mapping=session.get("column_mapping") or {},
            create_table_column_types=session.get("create_table_column_types") or {},
        )

    _remove_uploaded_session_file(session, current_file_path)
    file_name = Path(current_file_path).name
    if session.get("shopee_mode"):
        health = result.get("health_check") or {}
        orphaned = health.get("orphaned_orders") or {}
        nulls = health.get("nulls") or {}
        date_range = health.get("date_range") or {}
        complete_message = (
            f"Shopee orders upload complete for file `{file_name}` to `{db_path}`. "
            f"Orders table `{result['orders_table']}` upserted `{result['orders_upserted']}` rows; "
            f"order items table `{result['order_items_table']}` inserted `{result['order_items_inserted']}` rows "
            f"from sheet `{selected_sheet}`.\n"
            "Data health check:\n"
            f"- Orphaned orders: `{orphaned.get('orphaned_count', 0)}` "
            f"(total `{orphaned.get('total_orders', 0)}`, with items `{orphaned.get('orders_with_items', 0)}`)\n"
            f"- NULL grand_total: `{nulls.get('null_grand_total', 0)}`\n"
            f"- NULL transaction_fee: `{nulls.get('null_fees', 0)}`\n"
            f"- order_paid_time range: `{date_range.get('min_order_paid_time')}` to `{date_range.get('max_order_paid_time')}`"
        )
    else:
        verification = result.get("verification", {})
        missing_count = len(verification.get("missing_columns", []))
        extra_count = len(verification.get("extra_columns", []))
        type_issue_count = len(verification.get("type_issues", []))
        mode_text = "strict" if session.get("strict_schema", True) else "shared"
        complete_message = (
            f"Upload complete for file `{file_name}` to `{db_path}` table `{result['table_name']}` from sheet "
            f"`{result['sheet_name']}`. "
            f"Summary: {result['row_count_uploaded']} rows, {result['column_count_uploaded']} columns, "
            f"mode {mode_text}, missing cols {missing_count}, extra cols {extra_count}, "
            f"type issues {type_issue_count}."
        )

    remaining_files = _get_session_file_paths(session)
    if not remaining_files:
        sessions.pop(session_key, None)
        _write_sessions(sessions)
        return True, complete_message

    session["confirmed"] = False
    session["awaiting_confirmation"] = False
    sessions[session_key] = session
    _write_sessions(sessions)
    _, next_prompt = _resolve_pending_session(session_key, session, sessions)
    return True, f"{complete_message}\n\nNext file queued. {next_prompt}"


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
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_MAP_MODE_ACTION_ID,
                "text": {"type": "plain_text", "text": "Apply suggested mapping"},
                "value": "mode map",
            }
        )
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_LLM_MODE_ACTION_ID,
                "text": {"type": "plain_text", "text": "Let LLM decide fixes"},
                "value": "mode llm",
            }
        )
        if "Zip_Code" in response_text:
            actions.append(
                {
                    "type": "button",
                    "action_id": SQLITE_UPLOAD_CAST_ZIP_TEXT_ACTION_ID,
                    "text": {"type": "plain_text", "text": "Cast Zip_Code as TEXT"},
                    "value": "cast Zip_Code as TEXT",
                }
            )

    if response_text.startswith("Review proposed schema for new table"):
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_APPROVE_SCHEMA_ACTION_ID,
                "text": {"type": "plain_text", "text": "Approve schema"},
                "style": "primary",
                "value": "approve schema",
            }
        )
        actions.append(
            {
                "type": "button",
                "action_id": SQLITE_UPLOAD_SCHEMA_ALL_ACTION_ID,
                "text": {"type": "plain_text", "text": "Show all columns"},
                "value": "schema all",
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
    else:
        payload["blocks"] = [
            {"type": "section", "text": {"type": "mrkdwn", "text": response_text}}
        ]

    return payload


def _build_completion_blocks(response_text: str) -> list[dict] | None:
    match = re.match(
        r"^Upload complete(?: for file `([^`]+)`)? to `([^`]+)` table `([^`]+)` from sheet `([^`]+)`\. "
        r"Summary: (\d+) rows, (\d+) columns, mode (strict|shared), "
        r"missing cols (\d+), extra cols (\d+), type issues (\d+)\.$",
        response_text,
    )
    if not match:
        return None

    (
        file_name,
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
                {"type": "mrkdwn", "text": f"*File*\n`{file_name or 'n/a'}`"},
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

    previous_table_name = session.get("table_name")

    table_name = _extract_table_name(text)
    if table_name:
        session["table_name"] = table_name
        session["shopee_mode"] = False
        if table_name != previous_table_name:
            session["schema_review_approved"] = False
            session["create_table_column_types"] = {}
            session["schema_preview_all"] = False
            session["schema_preview_page"] = 0
            session["schema_preview_column"] = None

    create_table = _extract_create_table_name(text)
    if create_table:
        session["table_name"] = create_table
        session["shopee_mode"] = False
        session["allow_create_table"] = True
        session["schema_review_approved"] = False
        session["schema_preview_all"] = False
        session["schema_preview_page"] = 0
        session["schema_preview_column"] = None

    sheet_name = _extract_sheet_name(text)
    if sheet_name:
        session["sheet_name"] = sheet_name

    lowered = text.lower()
    if "mode shared" in lowered or "shared columns" in lowered:
        session["strict_schema"] = False
    if "mode map" in lowered or "apply suggested mapping" in lowered:
        session["strict_schema"] = True
        session["use_llm_resolution"] = False
        session["apply_suggested_mapping"] = True
        session["column_mapping"] = {}
    if "mode llm" in lowered:
        session["strict_schema"] = True
        session["use_llm_resolution"] = True
        session["apply_suggested_mapping"] = False
        session["column_mapping"] = {}
    if "mode strict" in lowered:
        session["strict_schema"] = True
        session["use_llm_resolution"] = False
        session["apply_suggested_mapping"] = False
        session["column_mapping"] = {}
    if "confirm upload" in lowered or lowered.strip() in {"confirm", "yes", "y"}:
        session["confirmed"] = True
    if "approve schema" in lowered:
        session["schema_review_approved"] = True
    if "schema all" in lowered:
        session["schema_preview_all"] = True
        session["schema_preview_page"] = 0
        session["schema_preview_column"] = None

    schema_page_match = re.search(r"schema\s+page\s+(\d+)", text, re.IGNORECASE)
    if schema_page_match:
        requested_page = max(1, int(schema_page_match.group(1)))
        session["schema_preview_page"] = requested_page - 1
        session["schema_preview_all"] = False
        session["schema_preview_column"] = None

    schema_column_match = re.search(
        r"schema\s+col(?:umn)?\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        text,
        re.IGNORECASE,
    )
    if schema_column_match:
        session["schema_preview_column"] = schema_column_match.group(1)
        session["schema_preview_all"] = False
        session["schema_preview_page"] = 0

    schema_updates = _extract_schema_type_updates(text)
    if schema_updates:
        session.setdefault("create_table_column_types", {}).update(schema_updates)
        session["schema_review_approved"] = False

    if "reset schema types" in lowered:
        session["create_table_column_types"] = {}
        session["schema_review_approved"] = False

    if "clear casts" in lowered:
        session["type_casts"] = {}

    cast_match = re.search(
        r"cast\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+(text|integer|int|real|float|double|numeric|number|date|datetime|timestamp|time|bool|boolean|string|str)",
        text,
        re.IGNORECASE,
    )
    if cast_match:
        column_name = cast_match.group(1)
        target_type = cast_match.group(2)
        session.setdefault("type_casts", {})[column_name] = target_type

    return session


def _suggest_type_overrides(verification: dict) -> dict[str, str]:
    suggestions: dict[str, str] = {}
    for issue in verification.get("type_issues", []):
        column = str(issue.get("column") or "")
        sqlite_type = str(issue.get("sqlite_type") or "").upper()
        lowered_column = column.lower()
        if "zip" in lowered_column and "INT" in sqlite_type:
            suggestions[column] = "TEXT"
    return suggestions


def _format_schema_mismatch_message(verification: dict) -> str:
    missing = verification.get("missing_columns") or []
    extra = verification.get("extra_columns") or []
    type_issues = verification.get("type_issues") or []
    mapping_suggestions = verification.get("mapping_suggestions") or []
    suggested_types = _suggest_type_overrides(verification)

    lines = ["Schema check found mismatches."]
    lines.append("*Missing columns (required by table):*")
    lines.extend(_format_name_list(missing))
    lines.append("*Extra columns (present in sheet):*")
    lines.extend(_format_name_list(extra))
    lines.append("*Type issues:*")
    lines.extend(_format_type_issues(type_issues))

    if mapping_suggestions:
        lines.append("*Suggested column mappings (table <- sheet):*")
        for item in mapping_suggestions:
            table_column = item.get("table_column")
            sheet_column = item.get("spreadsheet_column")
            confidence = item.get("confidence")
            reason = item.get("reason")
            lines.append(
                f"- `{table_column}` <- `{sheet_column}` (confidence `{confidence}`, {reason})"
            )

    if suggested_types:
        lines.append("*Suggested type casts:*")
        for column_name, target_type in suggested_types.items():
            lines.append(f"- `cast {column_name} as {target_type}`")

    lines.append("*Choose how to proceed:*")
    lines.append("- `mode shared` (upload only shared columns)")
    lines.append("- `mode map` (apply suggested column mapping)")
    lines.append("- `mode llm` (let LLM propose mapping + casts)")
    lines.append("- `cast <column> as <type>` (TEXT/INTEGER/REAL/DATE/BOOLEAN)")
    lines.append("- Fix table/sheet and retry")

    return "\n".join(lines)


def _format_create_table_schema_review(
    table_name: str,
    sheet_name: str,
    file_name: str,
    schema_preview: list[tuple[str, str]],
    schema_overrides: dict[str, str] | None = None,
    show_all: bool = False,
    current_page: int = 0,
    focus_column: str | None = None,
) -> str:
    overrides = _normalize_type_overrides_for_schema(schema_overrides or {})
    applied_preview: list[tuple[str, str]] = []
    for column_name, inferred_type in schema_preview:
        applied_preview.append((column_name, overrides.get(column_name, inferred_type)))

    lines = [
        "Review proposed schema for new table before creation.",
        f"*File:* `{file_name}`",
        f"*Sheet:* `{sheet_name}`",
        f"*New table:* `{table_name}`",
        "*Proposed columns:*",
    ]

    preview_rows = applied_preview
    if focus_column:
        preview_rows = [
            row for row in applied_preview if row[0].lower() == focus_column.lower()
        ]
        if not preview_rows:
            lines.append(f"- No column found named `{focus_column}`")

    page_size = len(preview_rows) if show_all else 30
    start = 0 if show_all else max(0, current_page * page_size)
    stop = min(len(preview_rows), start + page_size)
    for column_name, sqlite_type in preview_rows[start:stop]:
        lines.append(f"- `{column_name}` `{sqlite_type}`")

    if stop < len(preview_rows):
        lines.append(f"- ... `{len(preview_rows) - stop}` more columns")

    if not focus_column:
        total_pages = max(1, (len(preview_rows) + 29) // 30)
        shown_page = 1 if show_all else min(total_pages, current_page + 1)
        if not show_all:
            lines.append(f"*Preview page:* `{shown_page}/{total_pages}`")
    if not show_all and len(preview_rows) > 30:
        lines.append("Use `schema all` to show all columns, or `schema page <n>` to navigate pages.")
    lines.append("Use `schema col <name>` to inspect one column.")

    if overrides:
        lines.append("*Manual schema type overrides:*")
        for column_name, target_type in sorted(overrides.items()):
            lines.append(f"- `{column_name}` -> `{target_type}`")

    lines.append(
        "Use `set schema <column> as <type>` or `set schema: col=type, col2=type` "
        "to override type (TEXT/INTEGER/REAL/DATE/BOOLEAN), "
        "or `reset schema types` to clear overrides."
    )

    lines.append("Reply `approve schema` to proceed with table creation, or `cancel`.")
    return "\n".join(lines)


def _infer_schema_preview(data_frame) -> list[tuple[str, str]]:
    preview: list[tuple[str, str]] = []
    for column in data_frame.columns:
        preview.append((str(column), _infer_sqlite_type_for_new_table(data_frame[column])))
    return preview


def _infer_sqlite_type_for_new_table(series) -> str:
    non_null = series.dropna()
    if non_null.empty:
        return "TEXT"

    text_series = non_null.astype(str).str.strip()
    if text_series.empty:
        return "TEXT"

    lowered = text_series.str.lower()
    if lowered.isin({"1", "0", "true", "false", "t", "f", "yes", "no", "y", "n"}).all():
        return "BOOLEAN"

    cleaned = text_series.str.replace(r"[,\$%]", "", regex=True)
    numeric = pd.to_numeric(cleaned, errors="coerce")
    if numeric.notna().all():
        if text_series.str.match(r"^0\d+").any():
            return "TEXT"
        if (numeric % 1 == 0).all():
            return "INTEGER"
        return "REAL"

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Could not infer format, so each element will be parsed individually",
            category=UserWarning,
        )
        parsed_dates = pd.to_datetime(non_null, errors="coerce")
    if parsed_dates.notna().all():
        return "DATE"

    return "TEXT"


def _normalize_type_overrides_for_schema(raw: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for column_name, type_name in (raw or {}).items():
        canonical = _canonical_schema_type(type_name)
        if canonical:
            normalized[str(column_name)] = canonical
    return normalized


def _canonical_schema_type(type_name: str) -> str | None:
    lowered = (type_name or "").strip().lower()
    if lowered in {"text", "string", "str"}:
        return "TEXT"
    if lowered in {"integer", "int"}:
        return "INTEGER"
    if lowered in {"real", "float", "double", "numeric", "number"}:
        return "REAL"
    if lowered in {"date", "datetime", "timestamp", "time"}:
        return "DATE"
    if lowered in {"bool", "boolean"}:
        return "BOOLEAN"
    return None


def _extract_schema_type_updates(text: str) -> dict[str, str]:
    updates: dict[str, str] = {}
    if not text:
        return updates

    single_matches = re.findall(
        r"set\s+schema\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+([a-zA-Z]+)",
        text,
        flags=re.IGNORECASE,
    )
    for column_name, target_type in single_matches:
        canonical = _canonical_schema_type(target_type)
        if canonical:
            updates[column_name] = canonical

    bulk_match = re.search(r"set\s+schema\s*:\s*(.+)$", text, flags=re.IGNORECASE)
    if not bulk_match:
        return updates

    assignments = re.split(r"[,;\n]", bulk_match.group(1))
    for assignment in assignments:
        if "=" not in assignment:
            continue
        left, right = assignment.split("=", 1)
        column_name = left.strip()
        target_type = right.strip()
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", column_name):
            continue
        canonical = _canonical_schema_type(target_type)
        if canonical:
            updates[column_name] = canonical

    return updates


def _format_llm_resolution_message(
    column_mapping: dict[str, str], type_casts: dict[str, str], reasoning: str
) -> str:
    lines = ["LLM schema suggestion ready."]
    lines.append("*Proposed column mapping (table <- sheet):*")
    if column_mapping:
        for table_column, sheet_column in column_mapping.items():
            lines.append(f"- `{table_column}` <- `{sheet_column}`")
    else:
        lines.append("- none")

    lines.append("*Proposed type casts:*")
    if type_casts:
        for column_name, cast_type in type_casts.items():
            lines.append(f"- `cast {column_name} as {cast_type}`")
    else:
        lines.append("- none")

    if reasoning:
        lines.append(f"*Reasoning:* {reasoning}")

    lines.append("Reply `confirm upload` to proceed, `mode strict` to ignore, or adjust with `cast <column> as <type>`.")
    return "\n".join(lines)


def _format_name_list(values: list[str]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- `{value}`" for value in values]


def _format_type_issues(type_issues: list[dict]) -> list[str]:
    if not type_issues:
        return ["- none"]

    lines: list[str] = []
    for issue in type_issues:
        column_name = issue.get("column")
        sqlite_type = issue.get("sqlite_type")
        reason = issue.get("reason")
        lines.append(f"- `{column_name}` expects `{sqlite_type}` ({reason})")
    return lines


def _build_llm_resolution(
    session_key: str,
    table_name: str,
    verification: dict,
) -> dict | None:
    user_id = _user_id_from_session_key(session_key)
    if not user_id:
        return None

    prompt = (
        "You are helping map spreadsheet headers to SQLite schema for an import. "
        "Return STRICT JSON only with keys: column_mapping, type_casts, reasoning. "
        "column_mapping format: {\"Table_Column\": \"Spreadsheet_Column\"}. "
        "type_casts format: {\"Column\": \"TEXT|INTEGER|REAL|DATE|BOOLEAN\"}. "
        "Keep only high-confidence fixes.\n"
        f"Table: {table_name}\n"
        f"Table columns: {verification.get('table_columns', [])}\n"
        f"Spreadsheet columns: {verification.get('spreadsheet_columns', [])}\n"
        f"Missing columns: {verification.get('missing_columns', [])}\n"
        f"Extra columns: {verification.get('extra_columns', [])}\n"
        f"Type issues: {verification.get('type_issues', [])}\n"
    )

    try:
        response = get_provider_response(
            user_id=user_id,
            prompt=prompt,
            context=[],
            system_content="Return valid JSON only. No markdown.",
            conversation_id=None,
            file_paths=None,
        )
    except Exception:
        return None

    payload = _extract_json_payload(response)
    if not payload:
        return None

    return {
        "column_mapping": _normalize_column_mapping(payload.get("column_mapping")),
        "type_casts": payload.get("type_casts") or {},
        "reasoning": str(payload.get("reasoning") or "").strip(),
    }


def _extract_json_payload(text: str) -> dict | None:
    if not text:
        return None
    stripped = text.strip()
    try:
        loaded = json.loads(stripped)
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", stripped)
    if not match:
        return None
    try:
        loaded = json.loads(match.group(0))
        if isinstance(loaded, dict):
            return loaded
    except Exception:
        return None
    return None


def _normalize_column_mapping(raw_mapping: object) -> dict[str, str]:
    if not isinstance(raw_mapping, dict):
        return {}

    normalized: dict[str, str] = {}
    for target, source in raw_mapping.items():
        target_name = str(target or "").strip()
        source_name = str(source or "").strip()
        if target_name and source_name:
            normalized[target_name] = source_name
    return normalized


def _user_id_from_session_key(session_key: str) -> str | None:
    parts = (session_key or "").split(":")
    if len(parts) < 3:
        return None
    return parts[0]


def _persist_uploaded_file(file_path: str, session_key: str) -> str:
    UPLOAD_FILE_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file_path).suffix
    unique = uuid4().hex[:8]
    destination = UPLOAD_FILE_DIR / f"{_safe_name(session_key)}_{unique}{suffix}"
    shutil.copyfile(file_path, destination)
    return str(destination)


def _cleanup_session_files(session: dict):
    for path in _get_session_file_paths(session):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


def _append_session_files(session_key: str, session: dict, source_paths: list[str]) -> dict:
    existing = _get_session_file_paths(session)
    seen_hashes = set(str(item) for item in (session.get("seen_file_hashes") or []))

    persisted: list[str] = []
    for path in source_paths:
        file_hash = _hash_file(path)
        if not file_hash:
            continue
        if file_hash in seen_hashes:
            continue
        seen_hashes.add(file_hash)
        persisted.append(_persist_uploaded_file(path, session_key))

    session["file_paths"] = existing + persisted
    session["seen_file_hashes"] = sorted(seen_hashes)
    if "file_path" in session:
        session.pop("file_path", None)
    session.setdefault("current_file_index", 0)
    return session


def _hash_file(file_path: str) -> str:
    try:
        digest = hashlib.sha256()
        with open(file_path, "rb") as source:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return ""


def _get_session_file_paths(session: dict) -> list[str]:
    paths = session.get("file_paths")
    if isinstance(paths, list):
        return [str(path) for path in paths if path]

    legacy_single = session.get("file_path")
    if legacy_single:
        return [str(legacy_single)]
    return []


def _remove_uploaded_session_file(session: dict, file_path: str):
    current_paths = _get_session_file_paths(session)
    remaining = [path for path in current_paths if path != file_path]
    session["file_paths"] = remaining
    session["current_file_index"] = 0
    session.pop("file_path", None)

    try:
        os.remove(file_path)
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


def _looks_like_shopee_orders_report(file_path: str, sheet_name: str) -> bool:
    try:
        sheets = read_spreadsheet_sheets(file_path)
        frame = sheets.get(sheet_name)
        if frame is None:
            return False
        normalized = normalize_dataframe(frame)
        canonical_headers = {_canonical_header(str(column)) for column in normalized.columns}
        return SHOPEE_REQUIRED_CANONICAL_HEADERS.issubset(canonical_headers)
    except Exception:
        return False


def _canonical_header(value: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def _is_cancel(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return lowered in {"cancel", "stop", "never mind", "nevermind"}


def _extract_table_name(text: str) -> str | None:
    if not text:
        return None

    explicit_match = re.search(
        r"(?:to|into)\s+table\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        text,
        re.IGNORECASE,
    )
    if explicit_match:
        return explicit_match.group(1)

    table_match = re.search(r"\btable\s+([a-zA-Z_][a-zA-Z0-9_]*)", text, re.IGNORECASE)
    if table_match:
        return table_match.group(1)

    generic_match = re.search(r"(?:to|into)\s+([a-zA-Z_][a-zA-Z0-9_]*)", text, re.IGNORECASE)
    if generic_match:
        candidate = generic_match.group(1)
        if candidate.lower() not in {"sqlite", "database", "db", "sql"}:
            return candidate

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
