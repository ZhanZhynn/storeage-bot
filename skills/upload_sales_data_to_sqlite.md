# Upload Sales Data to SQLite

keywords: upload, import, sqlite, sql, table, csv, xlsx, excel, sales, schema

## Goal
Load spreadsheet sales data into a SQLite table safely and predictably.

## Use When
- The user asks to upload/import a spreadsheet into SQLite.
- The user references table names, schema matching, or SQL data loading.

## Inputs
- File path(s) for spreadsheet attachments.
- SQLite DB path from context hint (`BOLTY_SQLITE_DB_PATH` or default).
- Target table name and optional sheet name.

## Workflow
1. Confirm spreadsheet file type is supported (`.csv`, `.xlsx`, `.xls`).
2. Resolve target SQLite DB location and available table names.
3. Determine target table and sheet (if multiple sheets).
4. Verify spreadsheet columns against table schema.
5. Upload with the requested mode (append/replace) and report rows written.

## Guardrails
- If strict schema mode is enabled, fail on missing required columns or type mismatches.
- If table does not exist, only create it when explicitly allowed.
- Report mismatches and suggest next steps (shared columns, create table, or map columns).

## Output Style
- Confirm DB path, table, sheet, and row count uploaded.
- Include any validation warnings and unresolved risks.
