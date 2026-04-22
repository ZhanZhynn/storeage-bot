# Lazada Product Reviews Retrieval

keywords: lazada, reviews, review, rating, seller reviews, feedback, moderation

## Goal
Retrieve seller review streams for quality monitoring, sentiment checks, and response workflows.

## Scope
- `/review/seller/history/list`
- `/review/seller/list/v2`
- `/review/seller/reply/add`

## Deterministic Helper Commands (Preferred)
- Seller review history list:
  - `python3 -m lazada_helper.cli reviews seller-history-list --created-after <ISO8601> --created-before <ISO8601> --item-id <ITEM_ID> --current 1 --limit 100 --max-pages 10`
- Seller review list v2:
  - `python3 -m lazada_helper.cli reviews seller-list-v2 --item-id <ITEM_ID> [--id-list <REVIEW_ID_LIST>]`
- Reviews from recent delivered orders:
  - `python3 -m lazada_helper.cli reviews get-item-reviews --days 30 --sort desc`
- Seller reply add:
  - `python3 -m lazada_helper.cli reviews seller-reply-add --id-list <REVIEW_ID_LIST> --content <REPLY_TEXT>`

## Endpoint Mapping
- `reviews seller-history-list` -> `/review/seller/history/list`
- `reviews seller-list-v2` -> `/review/seller/list/v2`
- `reviews seller-reply-add` -> `/review/seller/reply/add`

## Output Requirements
- Include review count, pagination status, date range used, and representative review fields.

## Execution Notes
- Execute helper commands via `python3 -m lazada_helper.safe_run -- ...` and parse JSON from stdout.
