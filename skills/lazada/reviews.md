# Lazada Product Reviews Summary

keywords: lazada, reviews, review, rating, seller reviews, feedback, moderation

## Quick Answer (Use This)

```bash
# Get recent reviews for a product:
python3 -m lazada_helper.cli reviews seller-history-list --created-after 2026-04-01 --created-before 2026-04-30 --item-id <ITEM_ID>
```

Returns: `reviews[]` with `rating`, `content`, `author`, `created_at`

<!-- END_QUICK_ANSWER -->

---

# Full Documentation

## Goal
Retrieve seller review streams for quality monitoring, sentiment checks, and response workflows.

## Scope
- `/review/seller/history/list`
- `/review/seller/list/v2`
- `/review/seller/reply/add`

## Deterministic Helper Commands (Preferred)
- Seller review history list:
  - `python3 -m lazada_helper.cli reviews seller-history-list --created-after 2026-04-01 --created-before 2026-04-21 --item-id <ITEM_ID> --current 1 --limit 100 --max-pages 10`
- Seller review list v2:
  - `python3 -m lazada_helper.cli reviews seller-list-v2 --item-id <ITEM_ID> [--id-list <REVIEW_ID_LIST>]`
- Reviews from items in delivered orders:
  - `python3 -m lazada_helper.cli reviews get-item-reviews --days 30 --sort desc --max-api-calls 10`
- Reviews for recent N delivered orders:
  - `python3 -m lazada_helper.cli reviews get-recent-orders --days 30 --max-orders 10 --sort desc --max-api-calls 10`
- Seller reply add:
  - `python3 -m lazada_helper.cli reviews seller-reply-add --id-list <REVIEW_ID_LIST> --content <REPLY_TEXT>`

## Endpoint Mapping
- `reviews seller-history-list` -> `/review/seller/history/list`
- `reviews seller-list-v2` -> `/review/seller/list/v2`
- `reviews seller-reply-add` -> `/review/seller/reply/add`
- `reviews get-item-reviews` -> `/orders/get` + `/review/seller/history/list` (per item)
- `reviews get-recent-orders` -> `/orders/get` + `/review/seller/history/list` (per item, sorted by most recent orders)

## Rate Limiting (Always On)
Both `get-item-reviews` and `get-recent-orders` use rate limiting to avoid hitting Lazada's API frequency limit.

| Flag | Type | Default | Description |
|------|------|--------|------------|
| `--max-api-calls` | int | 10 | Max calls to `list_seller_reviews_history` API |
| `--max-orders` | int | 10 | Max delivered orders to fetch (only `get-recent-orders`) |

- Initial delay: 5-8 seconds before first API call
- Per-item delay: 0.3-0.5 seconds between API calls
- Exponential backoff retry: if rate limited, wait 3-9 seconds before retry

## Output Requirements
- Include review count, pagination status, date range used, and representative review fields.
- Include `api_calls_made`, `rate_limit_stopped`, and `unique_items` in output.

## Execution Notes
- Execute helper commands via `python3 -m lazada_helper.safe_run -- ...` and parse JSON from stdout.
- For `seller-history-list`, `created_after` and `created_before` must use `YYYY-MM-DD`.
- `YYYY-MM-DD` uses Malaysia timezone (`+08:00`), where `created_after` is start of day and `created_before` is end of day (`23:59:59.999`).
