# Lazada API Data Retrieval Playbook

keywords: lazada, iop, open platform, app_key, access_token, seller, orders, products, finance, return, refund, review

## Goal
Provide a repeatable workflow for fetching Lazada seller data using the local Go SDK and Lazada Open Platform APIs.

## Use When
- User asks for Lazada store details, especially orders, products, finance, returns, or refunds.
- User needs API-driven data retrieval, not spreadsheet-only analysis.

## Shared Config
- Read Lazada config from auto-injected context first (`BOLTY_LAZADA_*` values).
- Do not ask user to paste app key/secret/token again if they are already configured.
- If any required credential is missing, ask only for the missing value.

## Workflow
1. Confirm request domain (orders/products/finance/return-refund/reviews) and required filters (time range, status, pagination).
2. Choose endpoint and required params based on Lazada docs and this skill folder.
3. Validate response fields:
   - Top-level `code`, `message`, `request_id`
   - Nested `data` payload completeness
4. Return concise business output with key metrics and any API limitations.

## Deterministic Command Preference
- For API execution, prefer deterministic helper commands over raw ad-hoc curl.
- Orders example:
  - `python3 -m lazada_helper.cli orders get --days 7 --status all --limit 100 --max-pages 10`
- Finance examples:
  - `python3 -m lazada_helper.cli finance payout-status-get --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
  - `python3 -m lazada_helper.cli finance account-transactions-query --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
  - `python3 -m lazada_helper.cli finance logistics-fee-detail --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 3`
  - `python3 -m lazada_helper.cli finance transaction-details-get --transaction-number <TRANSACTION_NUMBER>`
- Product examples:
  - `python3 -m lazada_helper.cli products get --filter all --limit 50 --offset 0 --max-pages 5`
  - `python3 -m lazada_helper.cli products item-get --item-id <ITEM_ID>`
- Returns/refunds examples:
  - `python3 -m lazada_helper.cli returns-refunds return-detail-list --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
  - `python3 -m lazada_helper.cli returns-refunds return-history-list --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
  - `python3 -m lazada_helper.cli returns-refunds reason-list`
  - `python3 -m lazada_helper.cli returns-refunds get-reverse-orders-for-seller --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
- Reviews examples:
  - `python3 -m lazada_helper.cli reviews seller-history-list --created-after 1774972800 --created-before 1776614400 --current 1 --limit 100 --max-pages 10`
  - `python3 -m lazada_helper.cli reviews seller-list-v2 --item-id <ITEM_ID> [--id-list <REVIEW_ID_LIST>]`
  - `python3 -m lazada_helper.cli reviews seller-reply-add --id-list <REVIEW_ID_LIST> --content <REPLY_TEXT>`

## Command Execution Rules (Important)
- Use the safe wrapper command for all helper executions and parse JSON from stdout:
  - `python3 -m lazada_helper.safe_run -- <helper args>`
- Do not use shell redirection like `> /tmp/file.json` unless user explicitly asks to save a file.
- If file output is needed, use wrapper flag `--save-json data/<name>.json` instead of shell redirection.
- If command output is truncated by the tool, read the provided `outputPath` file and continue from that file.
- Prefer workspace paths (for example `data/*.json`) over `/tmp/*` when a file must be saved.
- After running a command, always report key fields first: `ok`, `status`, `endpoint`, `total_fetched`, `has_more`, and `request_ids`.

## Guardrails
- Never expose raw app secret in chat output.
- Prefer pagination-safe retrieval for large datasets.
- Explicitly state date/time assumptions and timezone.
