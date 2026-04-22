# Lazada Orders Retrieval

keywords: lazada, orders, order, getorders, orders/get, status, created_after, updated_at, pagination

## Goal
Fetch Lazada order-level data accurately for operational tracking and sales reporting.

## Endpoint
- Primary: `/orders/get`

## Required Inputs
- Date window (`created_after`/`created_before` or `update_after`/`update_before`)
- Pagination (`offset`, `limit`)
- Sort (`sort_by`, `sort_direction`)
- `status` (default `all` unless user narrows)

## Execution Pattern (Go SDK)
1. Create client and set access token.
2. Add query params via `AddAPIParam`.
3. Call `Execute("/orders/get", "GET", nil)`.
4. Parse response `data.orders` and pagination metadata.
5. If result count hits `limit`, continue paging until complete or user-defined cap.

## Deterministic Helper (Preferred)
- Prefer the local helper command over raw hand-written curl:
  - `python3 -m lazada_helper.cli orders get --days 7 --status all --limit 100 --max-pages 10`
- Helper reads shared env config (`BOLTY_LAZADA_*`), computes signature internally, and returns JSON.

## Recommended Defaults
- `sort_by=updated_at`
- `sort_direction=DESC`
- `limit=100`
- `offset=0`
- Use most recent 30 days if user gives no time range.

## Output Requirements
- Include order count, statuses breakdown, date range used, and sample order identifiers.
- Note if results are partial due to paging or missing token scope.

## Execution Notes
- Prefer safe wrapper execution without shell redirection:
  - `python3 -m lazada_helper.safe_run -- orders get --days 7 --status all --limit 100 --max-pages 10`
- If user asks to save JSON, use:
  - `python3 -m lazada_helper.safe_run --save-json data/lazada_orders.json -- orders get --days 7 --status all --limit 100 --max-pages 10`
- If output is truncated by tool limits, open the emitted `outputPath` file and continue parsing from there.
