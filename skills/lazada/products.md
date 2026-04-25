# Lazada Products Summary

keywords: lazada, products, product, sku, item, inventory, getproducts, listing, seller sku

## Quick Answer (Use This)

```bash
# Fetch all products (default behavior)
python3 -m lazada_helper.cli products get --filter all

# Fetch specific number
python3 -m lazada_helper.cli products get --filter all --limit 10
```

Returns: product list with `item_id`, `attributes` (name, brand, model), `status`, `skus` (SellerSku, ShopSku, price, quantity, Status)

<!-- END_QUICK_ANSWER -->

---

# Full Documentation

## Goal
Retrieve Lazada catalog/product information for SKU-level checks, listing health, and stock visibility.

## Common Endpoint Family
- `/products/get`
- `/product/item/get`

## Deterministic Helper Commands (Preferred)
- Fetch all products (default):
  - `python3 -m lazada_helper.cli products get --filter all`
- Fetch specific count:
  - `python3 -m lazada_helper.cli products get --filter all --limit 10`
  - `python3 -m lazada_helper.cli products get --filter all --limit 10 --max-pages 5` (50 products)
- Product item detail:
  - `python3 -m lazada_helper.cli products item-get --item-id <ITEM_ID>`

## Pagination
- `--limit`: Items per page (max 50, default 50)
- `--max-pages`: Number of pages to fetch (optional, defaults to unlimited when omitted)
- No limit specified → fetches all products

## Date Filtering
Not supported for products endpoint. Use `--filter` only (e.g., `--filter all`, `--filter live`, `--filter inactive`).

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
