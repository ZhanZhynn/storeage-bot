# Lazada API Data Retrieval Playbook

keywords: lazada, iop, open platform, app_key, access_token, seller, orders, products, finance, return, refund, review

## Quick Cheat Sheet (Common Questions)

| Question | CLI Command (Use This for Fast Results) |
| :--- | :--- |
| "How many orders?" | `python3 -m platform_helpers.lazada.cli orders summary --days 1 --short` |
| "How much sales?" | Same command → check `total_sales` in output |
| "Any returns?" | `python3 -m platform_helpers.lazada.cli returns-refunds return-history-list` |
| "Product reviews?" | `python3 -m platform_helpers.lazada.cli reviews seller-history-list --item-id <ITEM_ID>` |
| "Payout status?" | `python3 -m platform_helpers.lazada.cli finance payout-status-get --created-after 2026-04-01 --created-before 2026-04-30` |

<!-- END_QUICK_ANSWER -->

---

# Full Documentation

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
  - `python3 -m platform_helpers.lazada.cli orders summary --days 7 --short`
- Date filter format for `created_*`, `update_*`, and `create_*`:
  - Use `YYYY-MM-DD` only.
  - Helper normalizes `YYYY-MM-DD` to endpoint-specific Lazada API formats.
  - `YYYY-MM-DD` is interpreted in Malaysia timezone (`+08:00`).
  - For date-only input: `*_after` uses `00:00:00`, `*_before` uses `23:59:59.999`.
- Finance examples:
  - `python3 -m lazada_helper.cli finance payout-status-get --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --offset 0 --max-pages 10`
  - `python3 -m lazada_helper.cli finance account-transactions-query --transaction-type Deposit --sub-transaction-type Deposit --transaction-number 1001 --start-time 2022-06-01 --end-time 2022-06-02 --page-num 1 --page-size 10 --max-pages 10`
  - `python3 -m lazada_helper.cli finance logistics-fee-detail --seller-id 1002 --request-type OPEN_API --trade-order-id 9432987348 --trade-order-line-id 9432997348 --fee-type COD --biz-flow-type LAZADA --bill-start-time 2022-01-13 --bill-end-time 2022-01-13 --page-no 1 --page-size 10 --total-records 1000 --max-pages 3`
  - `python3 -m lazada_helper.cli finance transaction-details-get --trade-order-id 123123213213 --trade-order-line-id 45645674566 --trans-type -1 --start-time 2021-01-01 --end-time 2021-01-05 --offset 0 --limit 100`
- Product examples:
  - `python3 -m lazada_helper.cli products get --filter all --limit 50 --offset 0 --max-pages 5`
  - `python3 -m lazada_helper.cli products item-get --item-id <ITEM_ID>`
- Returns/refunds examples:
  - `python3 -m lazada_helper.cli returns-refunds return-detail-list --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --offset 0 --max-pages 10`
  - `python3 -m lazada_helper.cli returns-refunds return-history-list --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --offset 0 --max-pages 10`
  - `python3 -m lazada_helper.cli returns-refunds reason-list`
  - `python3 -m lazada_helper.cli returns-refunds get-reverse-orders-for-seller --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --offset 0 --max-pages 10`
- Reviews examples:
  - `python3 -m lazada_helper.cli reviews seller-history-list --created-after 2026-04-01 --created-before 2026-04-21 --item-id <ITEM_ID> --current 1 --limit 100 --max-pages 10`
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
