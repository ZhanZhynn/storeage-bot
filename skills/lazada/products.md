# Lazada Products Retrieval

keywords: lazada, products, product, sku, item, inventory, getproducts, listing, seller sku

## Goal
Retrieve Lazada catalog/product information for SKU-level checks, listing health, and stock visibility.

## Common Endpoint Family
- `/products/get`
- `/product/item/get`

## Deterministic Helper Commands (Preferred)
- Product list:
  - `python3 -m lazada_helper.cli products get --filter all --update-after 2026-04-01 --update-before 2026-04-21 --limit 100 --offset 0 --max-pages 10`
- Product item detail:
  - `python3 -m lazada_helper.cli products item-get --item-id <ITEM_ID>`

## Datetime Input Rules
- `create_after`, `create_before`, `update_after`, and `update_before` must use `YYYY-MM-DD`.
- Date-only values use Malaysia timezone (`+08:00`), where `*_after` is start of day and `*_before` is end of day (`23:59:59.999`).

## Endpoint Mapping
- `products get` -> `/products/get`
- `products item-get` -> `/product/item/get`

## Execution Notes
- Execute helper command via `python3 -m lazada_helper.safe_run -- ...` and summarize JSON fields directly.

## Inputs to Clarify
- Scope: all products vs selected SKU(s)
- Status filter: active/inactive/suspended
- Pagination and sort requirements

## Workflow
1. Identify the exact product endpoint available to the connected app scope.
2. Build request with configured app credentials and access token.
3. Request paginated product list and normalize key fields:
   - Product/SKU identifiers
   - Product name
   - Status
   - Price
   - Quantity/stock
4. Aggregate into a concise summary plus optional detailed table when requested.

## Guardrails
- Do not assume a single universal response schema; verify field names in current endpoint response.
- Distinguish product-level vs SKU-level metrics in output.
