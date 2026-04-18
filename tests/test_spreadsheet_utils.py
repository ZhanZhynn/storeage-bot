from pathlib import Path
import sqlite3

import pandas as pd
import pytest

from ai.utils.spreadsheet_utils import (
    MAX_NUMERIC_COLUMNS_IN_PROMPT,
    analyze_spreadsheet,
    build_spreadsheet_context,
    format_analysis,
    suggest_sqlite_upload_questions,
    upload_spreadsheet_to_sqlite,
    verify_spreadsheet_against_sqlite_schema,
)
from listeners.listener_utils.sqlite_upload_flow import start_sqlite_upload_session


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
