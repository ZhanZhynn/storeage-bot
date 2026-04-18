# Analyze Sales Data

keywords: analyze, sales, revenue, trend, kpi, dashboard, sql, sqlite, table, query, top product, sku, time, monthly, weekly, excel, csv

## Goal
Turn sales data into concise, decision-ready insights with fast and accurate SQL-first analysis.

## Use When
- The user asks for sales analysis, trends, comparisons, top products, SKU performance, or KPI summaries.
- The user asks for time-based drivers (day/week/month/seasonality).
- A spreadsheet file (`.csv`, `.xlsx`, `.xls`) is attached.

## Inputs
- User question and requested time scope.
- SQLite data location hint and table list from prompt context.
- Attached spreadsheet context (headers, row counts, numeric stats), if present.

## Fast Path (Prefer This)
1. If a SQLite location hint exists, use that DB path first.
2. Use existing SQLite helper functions first to inspect schema quickly:
   - `list_sqlite_tables(sqlite_db_path)`
   - `get_sqlite_table_schema(sqlite_db_path, table_name)`
3. Run direct SQL aggregation for requested KPIs (avoid loading full tables to pandas unless needed for edge cases).
4. Return top-N results with requested fields (for example SKU), then add time-slice analysis.

## Query Workflow
1. Identify metric definitions explicitly (for example revenue = `Deal_Price * Quantity` unless user specifies another definition).
2. Verify target table and exact column names from schema before writing final query.
3. Quote unusual identifiers in SQLite (for example columns with spaces, `/`, `.`, `*`, or parentheses).
4. Filter by relevant order status where appropriate (for example completed/paid sales only) and state assumption.
5. Use grouped SQL for speed:
   - Top SKU by revenue/units
   - Revenue by month/week/day for the same SKU set
   - Promo/discount split if columns exist (voucher, discount, bundle indicators)
6. If `sqlite3` CLI is unavailable, use Python `sqlite3` immediately (do not stop analysis).

## Analysis Expectations
- Explain why top products win using time and commercial drivers:
  - volume vs price mix
  - discount/promo intensity
  - concentration in specific periods (month/week/day)
  - operational factors when available (shipping method, region, channel)
- Call out data limits (date coverage, missing fields, non-standard statuses, nulls).

## Output Style
- Keep response concise and decision-focused.
- Use markdown tables for ranked/tabular outputs.
- Include assumptions in one short bullet block.
- End with 2-3 practical recommendations tied to findings.

## Guardrails
- Prefer SQLite over spreadsheet summaries when both are available for the same question.
- Do not guess table/column names; verify first.
- Avoid broad `SELECT *` for analysis queries; select only required columns.
- When time analysis is requested, always include a time-bucket breakdown (at least monthly).
