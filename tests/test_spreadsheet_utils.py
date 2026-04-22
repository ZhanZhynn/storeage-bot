from pathlib import Path
import sqlite3

import pandas as pd
import pytest

from ai.utils.spreadsheet_utils import (
    MAX_NUMERIC_COLUMNS_IN_PROMPT,
    analyze_spreadsheet,
    build_spreadsheet_context,
    format_analysis,
    suggest_schema_column_mapping,
    suggest_sqlite_upload_questions,
    upload_spreadsheet_to_sqlite,
    verify_spreadsheet_against_sqlite_schema,
)
from listeners.listener_utils.sqlite_upload_flow import (
    _append_session_files,
    _extract_schema_type_updates,
    _get_session_file_paths,
    _update_session_from_user_text,
    start_sqlite_upload_session,
)


def test_analyze_csv_extracts_headers_and_numeric_stats(tmp_path: Path):
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text(
        "region,revenue,units\n"
        "us,$1,2\n"
        "eu,$3,4\n",
        encoding="utf-8",
    )

    analysis = analyze_spreadsheet(str(csv_path))

    assert analysis["file_name"] == "sales.csv"
    assert len(analysis["sheets"]) == 1
    sheet = analysis["sheets"][0]
    assert sheet["sheet_name"] == "csv"
    assert sheet["headers"] == ["region", "revenue", "units"]
    assert sheet["row_count"] == 2
    assert sheet["column_count"] == 3

    stats = {item["header"]: item for item in sheet["numeric_stats"]}
    assert stats["revenue"]["sum"] == pytest.approx(4.0)
    assert stats["units"]["avg"] == pytest.approx(3.0)


def test_analyze_csv_generates_default_headers_when_missing(tmp_path: Path):
    csv_path = tmp_path / "no_header.csv"
    csv_path.write_text(
        ",,\n"
        "10,20,30\n"
        "40,50,60\n",
        encoding="utf-8",
    )

    analysis = analyze_spreadsheet(str(csv_path))
    sheet = analysis["sheets"][0]

    assert sheet["headers"] == ["column_1", "column_2", "column_3"]
    assert sheet["row_count"] == 3


def test_format_analysis_limits_numeric_columns(tmp_path: Path):
    headers = ["name"] + [f"metric_{i}" for i in range(MAX_NUMERIC_COLUMNS_IN_PROMPT + 3)]
    rows = []
    for row_index in range(3):
        rows.append([f"item_{row_index}"] + [str(row_index + col) for col in range(len(headers) - 1)])

    csv_path = tmp_path / "wide.csv"
    csv_lines = [",".join(headers)] + [",".join(row) for row in rows]
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    analysis = analyze_spreadsheet(str(csv_path))
    rendered = format_analysis(analysis)

    assert "numeric columns omitted" in rendered


def test_build_spreadsheet_context_only_includes_spreadsheets(tmp_path: Path):
    csv_path = tmp_path / "sheet.csv"
    txt_path = tmp_path / "notes.txt"
    csv_path.write_text("a,b\n1,2\n", encoding="utf-8")
    txt_path.write_text("hello", encoding="utf-8")

    context = build_spreadsheet_context([str(txt_path), str(csv_path)])

    assert "Attached spreadsheet quick analysis" in context
    assert "sheet.csv" in context
    assert "notes.txt" not in context


def test_analyze_xlsx_reads_multiple_sheets(tmp_path: Path):
    openpyxl = pytest.importorskip("openpyxl")

    workbook = openpyxl.Workbook()
    sheet1 = workbook.active
    sheet1.title = "Summary"
    sheet1.append(["month", "amount"])
    sheet1.append(["jan", 10])
    sheet2 = workbook.create_sheet(title="Detail")
    sheet2.append(["id", "qty"])
    sheet2.append(["a", 3])
    path = tmp_path / "book.xlsx"
    workbook.save(path)

    analysis = analyze_spreadsheet(str(path))
    sheet_names = [sheet["sheet_name"] for sheet in analysis["sheets"]]

    assert "Summary" in sheet_names
    assert "Detail" in sheet_names


def test_suggest_sqlite_upload_questions_requests_table_when_missing(tmp_path: Path):
    csv_path = tmp_path / "sheet.csv"
    csv_path.write_text("id,amount\n1,10\n", encoding="utf-8")

    db_path = tmp_path / "example.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE metrics (id INTEGER, amount REAL)")

    suggestion = suggest_sqlite_upload_questions(str(csv_path), str(db_path))

    assert suggestion["tables"] == ["metrics"]
    assert any("Which SQLite table" in question for question in suggestion["questions"])


def test_verify_spreadsheet_against_sqlite_schema_reports_type_issues(tmp_path: Path):
    db_path = tmp_path / "example.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE metrics (id INTEGER, amount REAL)")

    frame = pd.DataFrame({"id": ["one"], "amount": [10]})
    verification = verify_spreadsheet_against_sqlite_schema(
        data_frame=frame,
        sqlite_db_path=str(db_path),
        table_name="metrics",
    )

    assert verification["is_compatible"] is False
    assert verification["type_issues"][0]["column"] == "id"


def test_upload_spreadsheet_to_sqlite_non_strict_uploads_shared_columns(tmp_path: Path):
    csv_path = tmp_path / "sheet.csv"
    csv_path.write_text("id,amount,extra\n1,10,foo\n2,12,bar\n", encoding="utf-8")

    db_path = tmp_path / "example.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE metrics (id INTEGER, amount REAL)")

    result = upload_spreadsheet_to_sqlite(
        file_path=str(csv_path),
        sqlite_db_path=str(db_path),
        table_name="metrics",
        strict_schema=False,
    )

    assert result["row_count_uploaded"] == 2
    assert result["column_count_uploaded"] == 2

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("SELECT id, amount FROM metrics ORDER BY id").fetchall()
    assert rows == [(1, 10.0), (2, 12.0)]


def test_upload_spreadsheet_to_sqlite_can_create_table(tmp_path: Path):
    csv_path = tmp_path / "new_table.csv"
    csv_path.write_text("id,amount\n1,10\n", encoding="utf-8")

    db_path = tmp_path / "example.db"
    result = upload_spreadsheet_to_sqlite(
        file_path=str(csv_path),
        sqlite_db_path=str(db_path),
        table_name="created_from_csv",
        strict_schema=True,
        allow_create_table=True,
    )

    assert result["row_count_uploaded"] == 1
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("SELECT id, amount FROM created_from_csv").fetchall()
    assert rows == [(1, 10)]


def test_suggest_schema_column_mapping_handles_punctuation_variants(tmp_path: Path):
    db_path = tmp_path / "example.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE sales (Return_Refund_Status TEXT, Tracking_Number TEXT, Username_Buyer TEXT)"
        )

    mapping = suggest_schema_column_mapping(
        sqlite_db_path=str(db_path),
        table_name="sales",
        spreadsheet_columns=["Return_/_Refund_Status", "Tracking_Number*", "Username_(Buyer)"],
    )

    assert mapping["mapping"] == {
        "Return_Refund_Status": "Return_/_Refund_Status",
        "Tracking_Number": "Tracking_Number*",
        "Username_Buyer": "Username_(Buyer)",
    }


def test_upload_spreadsheet_to_sqlite_can_apply_mapping_and_text_cast(tmp_path: Path):
    csv_path = tmp_path / "sheet.csv"
    csv_path.write_text("Zip_Code,Username_(Buyer)\n02115,user1\n10001,user2\n", encoding="utf-8")

    db_path = tmp_path / "example.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE customers (Zip_Code INTEGER, Username_Buyer TEXT)")

    result = upload_spreadsheet_to_sqlite(
        file_path=str(csv_path),
        sqlite_db_path=str(db_path),
        table_name="customers",
        strict_schema=True,
        apply_suggested_mapping=True,
        type_casts={"Zip_Code": "TEXT"},
    )

    assert result["row_count_uploaded"] == 2
    assert result["verification"]["mapping_applied"]["Username_Buyer"] == "Username_(Buyer)"

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("SELECT Zip_Code, Username_Buyer FROM customers ORDER BY rowid").fetchall()
    assert rows == [(2115, "user1"), (10001, "user2")]


def test_update_session_from_user_text_parses_mode_map_and_cast():
    session = {
        "strict_schema": True,
        "apply_suggested_mapping": False,
        "type_casts": {},
    }

    updated = _update_session_from_user_text(session, "mode map")
    assert updated["apply_suggested_mapping"] is True

    updated = _update_session_from_user_text(updated, "cast Zip_Code as TEXT")
    assert updated["type_casts"]["Zip_Code"] == "TEXT"


def test_update_session_from_user_text_parses_mode_llm():
    session = {
        "strict_schema": True,
        "use_llm_resolution": False,
        "apply_suggested_mapping": True,
        "column_mapping": {"Username_Buyer": "Username_(Buyer)"},
    }

    updated = _update_session_from_user_text(session, "mode llm")
    assert updated["use_llm_resolution"] is True
    assert updated["apply_suggested_mapping"] is False
    assert updated["column_mapping"] == {}


def test_update_session_from_user_text_parses_approve_schema():
    session = {
        "table_name": "new_table",
        "schema_review_approved": False,
    }

    updated = _update_session_from_user_text(session, "approve schema")
    assert updated["schema_review_approved"] is True


def test_start_sqlite_upload_session_uses_repo_db_path(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BOLTY_SQLITE_DB_PATH", str(tmp_path / "repo.db"))

    message = start_sqlite_upload_session(
        user_id="U123",
        channel_id="C123",
        thread_ts="111.222",
        initial_text="table sales",
    )

    assert "repo.db" in message
    assert "sales" in message
    assert "mode map" in message
    assert "approve schema" in message


def test_append_session_files_deduplicates_same_file_content(tmp_path: Path):
    csv_a = tmp_path / "a.csv"
    csv_b = tmp_path / "b.csv"
    csv_a.write_text("id,val\n1,10\n", encoding="utf-8")
    csv_b.write_text("id,val\n1,10\n", encoding="utf-8")

    session = {
        "file_paths": [],
        "seen_file_hashes": [],
    }

    session = _append_session_files("U1:C1:T1", session, [str(csv_a), str(csv_b)])

    assert len(_get_session_file_paths(session)) == 1
    assert len(session["seen_file_hashes"]) == 1


def test_extract_schema_type_updates_supports_bulk_assignments():
    updates = _extract_schema_type_updates(
        "set schema: Zip_Code=text, Shopee_Rebate=INTEGER; Order_Creation_Date=date"
    )

    assert updates == {
        "Zip_Code": "TEXT",
        "Shopee_Rebate": "INTEGER",
        "Order_Creation_Date": "DATE",
    }
