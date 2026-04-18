import os
import re
import sqlite3
from typing import Any

import pandas as pd


SPREADSHEET_SUFFIXES = (".csv", ".xlsx", ".xls")
MAX_HEADER_PREVIEW_COLUMNS = 20
MAX_NUMERIC_COLUMNS_IN_PROMPT = 10


def is_spreadsheet_path(file_path: str) -> bool:
    return (file_path or "").lower().endswith(SPREADSHEET_SUFFIXES)


def build_spreadsheet_context(file_paths: list[str] | None) -> str:
    if not file_paths:
        return ""

    analyses = []
    for file_path in file_paths:
        if not is_spreadsheet_path(file_path):
            continue
        try:
            analysis = analyze_spreadsheet(file_path)
            analyses.append(format_analysis(analysis))
        except Exception as error:
            name = os.path.basename(file_path)
            analyses.append(f"- File: {name}\n  - Analysis error: {error}")

    if not analyses:
        return ""

    joined = "\n\n".join(analyses)
    return (
        "Attached spreadsheet quick analysis (auto-generated):\n"
        "Use this to answer user questions and reference headers/metrics when relevant.\n\n"
        f"{joined}"
    )


def analyze_spreadsheet(file_path: str) -> dict[str, Any]:
    sheets = read_spreadsheet_sheets(file_path)
    analyzed_sheets = []

    for sheet_name, data_frame in sheets.items():
        normalized = normalize_dataframe(data_frame)
        numeric_stats = compute_numeric_stats(normalized)
        numeric_stats.sort(key=lambda item: (-item["count"], item["header"]))
        analyzed_sheets.append(
            {
                "sheet_name": sheet_name,
                "row_count": int(normalized.shape[0]),
                "column_count": int(normalized.shape[1]),
                "headers": [str(column) for column in normalized.columns],
                "numeric_stats": numeric_stats,
            }
        )

    return {"file_name": os.path.basename(file_path), "sheets": analyzed_sheets}


def read_spreadsheet_sheets(file_path: str) -> dict[str, pd.DataFrame]:
    lower_path = (file_path or "").lower()
    if lower_path.endswith(".csv"):
        data_frame = pd.read_csv(file_path)
        if _looks_like_unnamed_columns(list(data_frame.columns)):
            data_frame = pd.read_csv(file_path, header=None)
        return {"csv": data_frame}
    if lower_path.endswith(".xlsx"):
        return pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
    if lower_path.endswith(".xls"):
        return pd.read_excel(file_path, sheet_name=None, engine="xlrd")
    raise ValueError("Unsupported spreadsheet type")


def normalize_dataframe(data_frame: pd.DataFrame) -> pd.DataFrame:
    normalized = data_frame.copy()
    normalized.columns = [
        _normalize_column_name(column, index)
        for index, column in enumerate(normalized.columns, start=1)
    ]
    return normalized


def compute_numeric_stats(data_frame: pd.DataFrame) -> list[dict[str, Any]]:
    stats = []
    for column in data_frame.columns:
        parsed = _series_to_numeric(data_frame[column])
        valid = parsed.dropna()
        if valid.empty:
            continue

        stats.append(
            {
                "header": str(column),
                "count": int(valid.shape[0]),
                "sum": float(valid.sum()),
                "avg": float(valid.mean()),
                "min": float(valid.min()),
                "max": float(valid.max()),
            }
        )
    return stats


def suggest_sqlite_upload_questions(
    file_path: str,
    sqlite_db_path: str,
    requested_table: str | None = None,
) -> dict[str, Any]:
    sheets = read_spreadsheet_sheets(file_path)
    table_names = list_sqlite_tables(sqlite_db_path)
    if requested_table and requested_table not in table_names:
        raise ValueError(f"SQLite table '{requested_table}' does not exist")

    questions = []
    if not requested_table:
        questions.append(
            "Which SQLite table should I upload into? "
            f"Available tables: {', '.join(table_names) if table_names else '(none)'}"
        )

    if len(sheets) > 1:
        questions.append(
            "Which spreadsheet sheet should be uploaded? "
            f"Available sheets: {', '.join(list(sheets.keys()))}"
        )

    if requested_table and table_names:
        table_columns = get_sqlite_table_schema(sqlite_db_path, requested_table)
        first_sheet_name = next(iter(sheets.keys()))
        spreadsheet_columns = [str(column) for column in normalize_dataframe(sheets[first_sheet_name]).columns]
        if set(table_columns) != set(spreadsheet_columns):
            questions.append(
                "Spreadsheet columns do not exactly match the table schema. "
                "Should I upload only shared columns, fail on mismatch, or create a new table?"
            )

    return {
        "questions": questions,
        "tables": table_names,
        "sheets": list(sheets.keys()),
    }


def upload_spreadsheet_to_sqlite(
    file_path: str,
    sqlite_db_path: str,
    table_name: str,
    sheet_name: str | None = None,
    if_exists: str = "append",
    strict_schema: bool = True,
    allow_create_table: bool = False,
) -> dict[str, Any]:
    sheets = read_spreadsheet_sheets(file_path)
    selected_sheet = sheet_name or next(iter(sheets.keys()))
    if selected_sheet not in sheets:
        raise ValueError(f"Sheet '{selected_sheet}' not found in spreadsheet")

    frame = normalize_dataframe(sheets[selected_sheet])
    table_names = set(list_sqlite_tables(sqlite_db_path))
    table_exists = table_name in table_names

    if not table_exists and not allow_create_table:
        raise ValueError(f"SQLite table '{table_name}' does not exist")

    if table_exists:
        verification = verify_spreadsheet_against_sqlite_schema(
            data_frame=frame,
            sqlite_db_path=sqlite_db_path,
            table_name=table_name,
        )
    else:
        verification = {
            "is_compatible": True,
            "table_columns": [str(column) for column in frame.columns],
            "spreadsheet_columns": [str(column) for column in frame.columns],
            "missing_columns": [],
            "extra_columns": [],
            "type_issues": [],
        }

    if strict_schema and not verification["is_compatible"]:
        raise ValueError(
            "Spreadsheet data does not match table schema: "
            f"missing columns={verification['missing_columns']}, "
            f"extra columns={verification['extra_columns']}, "
            f"type_issues={verification['type_issues']}"
        )

    write_frame = frame
    if table_exists and not strict_schema:
        shared_columns = [
            column for column in frame.columns if column in verification["table_columns"]
        ]
        if not shared_columns:
            raise ValueError("No shared columns between spreadsheet and SQLite table")
        write_frame = frame[shared_columns]

    with sqlite3.connect(sqlite_db_path) as connection:
        write_frame.to_sql(table_name, connection, if_exists=if_exists, index=False)

    return {
        "table_name": table_name,
        "sheet_name": selected_sheet,
        "row_count_uploaded": int(write_frame.shape[0]),
        "column_count_uploaded": int(write_frame.shape[1]),
        "verification": verification,
    }


def verify_spreadsheet_against_sqlite_schema(
    data_frame: pd.DataFrame,
    sqlite_db_path: str,
    table_name: str,
) -> dict[str, Any]:
    table_columns_info = _get_sqlite_table_columns(sqlite_db_path, table_name)
    table_columns = [column["name"] for column in table_columns_info]
    frame_columns = [str(column) for column in data_frame.columns]

    missing_columns = [column for column in table_columns if column not in frame_columns]
    extra_columns = [column for column in frame_columns if column not in table_columns]

    type_issues = []
    for column in table_columns_info:
        name = column["name"]
        if name not in data_frame.columns:
            continue
        sqlite_type = (column["type"] or "").upper()
        column_series = data_frame[name]
        if not _is_series_compatible_with_sqlite_type(column_series, sqlite_type):
            type_issues.append(
                {
                    "column": name,
                    "sqlite_type": sqlite_type,
                    "reason": "Values appear incompatible with target SQLite type",
                }
            )

    is_compatible = not missing_columns and not type_issues
    return {
        "is_compatible": is_compatible,
        "table_columns": table_columns,
        "spreadsheet_columns": frame_columns,
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "type_issues": type_issues,
    }


def list_sqlite_tables(sqlite_db_path: str) -> list[str]:
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    with sqlite3.connect(sqlite_db_path) as connection:
        rows = connection.execute(query).fetchall()
    return [str(row[0]) for row in rows]


def get_sqlite_table_schema(sqlite_db_path: str, table_name: str) -> list[str]:
    columns = _get_sqlite_table_columns(sqlite_db_path, table_name)
    return [column["name"] for column in columns]


def _get_sqlite_table_columns(sqlite_db_path: str, table_name: str) -> list[dict[str, Any]]:
    query = f"PRAGMA table_info({_quote_identifier(table_name)})"
    with sqlite3.connect(sqlite_db_path) as connection:
        rows = connection.execute(query).fetchall()
    if not rows:
        raise ValueError(f"SQLite table '{table_name}' not found or has no columns")

    columns = []
    for row in rows:
        columns.append(
            {
                "name": str(row[1]),
                "type": str(row[2] or ""),
                "notnull": bool(row[3]),
                "default": row[4],
                "pk": bool(row[5]),
            }
        )
    return columns


def _is_series_compatible_with_sqlite_type(series: pd.Series, sqlite_type: str) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return True

    if "INT" in sqlite_type:
        numeric = _series_to_numeric(non_null)
        if numeric.dropna().shape[0] != non_null.shape[0]:
            return False
        return bool((numeric.dropna() % 1 == 0).all())

    if any(token in sqlite_type for token in ["REAL", "FLOA", "DOUB", "NUM"]):
        numeric = _series_to_numeric(non_null)
        return numeric.dropna().shape[0] == non_null.shape[0]

    if any(token in sqlite_type for token in ["DATE", "TIME"]):
        parsed = pd.to_datetime(non_null, errors="coerce")
        return parsed.dropna().shape[0] == non_null.shape[0]

    return True


def _series_to_numeric(series: pd.Series) -> pd.Series:
    text_series = series.astype(str)
    cleaned = text_series.str.replace(r"[,\$%]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def _normalize_column_name(value: Any, index: int) -> str:
    raw = "" if value is None else str(value).strip()
    if not raw:
        return f"column_{index}"
    collapsed = re.sub(r"\s+", "_", raw)
    return collapsed


def _looks_like_unnamed_columns(columns: list[Any]) -> bool:
    if not columns:
        return False
    unnamed_pattern = re.compile(r"^Unnamed:\s*\d+$")
    for column in columns:
        text = "" if column is None else str(column)
        if unnamed_pattern.match(text) is None:
            return False
    return True


def _quote_identifier(identifier: str) -> str:
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'


def format_analysis(analysis: dict[str, Any]) -> str:
    file_name = analysis.get("file_name", "unknown")
    lines = [f"- File: {file_name}"]
    sheets = analysis.get("sheets", [])
    for sheet in sheets:
        sheet_name = sheet.get("sheet_name")
        row_count = sheet.get("row_count", 0)
        column_count = sheet.get("column_count", 0)
        headers = sheet.get("headers", [])
        numeric_stats = sheet.get("numeric_stats", [])

        header_preview = (
            ", ".join(headers[:MAX_HEADER_PREVIEW_COLUMNS]) if headers else "(none)"
        )

        lines.append(f"  - Sheet: {sheet_name}")
        lines.append(f"    - Rows: {row_count}")
        lines.append(f"    - Columns: {column_count}")
        lines.append(f"    - Headers: {header_preview}")

        if numeric_stats:
            lines.append("    - Numeric column stats:")
            top_numeric_stats = numeric_stats[:MAX_NUMERIC_COLUMNS_IN_PROMPT]
            for stat in top_numeric_stats:
                lines.append(
                    "      - "
                    f"{stat['header']}: count={stat['count']}, "
                    f"sum={stat['sum']:.4f}, avg={stat['avg']:.4f}, "
                    f"min={stat['min']:.4f}, max={stat['max']:.4f}"
                )

            omitted = len(numeric_stats) - len(top_numeric_stats)
            if omitted > 0:
                lines.append(f"      - ... {omitted} more numeric columns omitted")

    return "\n".join(lines)
