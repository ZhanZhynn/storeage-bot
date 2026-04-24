# Lazada Orders Retrieval

keywords: lazada, orders, order, getorders, orders/get, orders/item-get, orders/items-multiple, order/cancel-validate, status, created_after, updated_at, pagination, order_id

## Goal
Fetch Lazada order-level data accurately for operational tracking and sales reporting.

## Endpoints
- List orders: `/orders/get`
- Get single order: `/order/get`
- Get order items: `/order/items/get`
- Get multiple order items: `/orders/items/get`
- Validate cancel: `/order/reverse/cancel/validate`

## Required Inputs
- Date window (`created_after`/`created_before` or `update_after`/`update_before`)
- Pagination (`offset`, `limit`)
- Sort (`sort_by`, `sort_direction`)
- `status` (default `all` unless user narrows)

| Endpoint | Method | Required Params | Optional Params |
|----------|--------|-----------------|------------------|
| `/orders/get` | GET | status, limit, offset, sort_by, sort_direction | created_after, created_before, update_after, update_before |
| `/order/get` | GET | order_id | - |
| `/order/items/get` | GET | order_id | - |
| `/orders/items/get` | GET | order_ids (JSON array) | - |
| `/order/reverse/cancel/validate` | GET | order_id | order_item_id_list (JSON array) |

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
- Datetime filter inputs (`created_*`, `update_*`) must use `YYYY-MM-DD`.
- `YYYY-MM-DD` uses Malaysia timezone (`+08:00`): `*_after` maps to `00:00:00`, `*_before` maps to `23:59:59.999`.

## Order Sub-API Commands

### Get order items for single order
```
python3 -m lazada_helper.cli orders item-get --order-id 123456789
```
- Calls `/order/items/get`
- Returns order items array
- Normalized input: order_id as string

### Get multiple order items
```
python3 -m lazada_helper.cli orders items-multiple --order-ids '["123456789","987654321"]'
```
- Calls `/orders/items/get`
- accepts JSON array of order IDs
- Returns orders with items grouped

### Validate order cancel
```
python3 -m lazada_helper.cli orders cancel-validate --order-id 123456789 --order-item-id-list '["111111","222222"]'
```
- Calls `/order/reverse/cancel/validate`
- order_item_id_list optional if canceling entire order
- Returns validation result

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
