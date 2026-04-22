# Lazada Returns and Refunds Retrieval

keywords: lazada, return, returns, refund, refunds, dispute, reverse logistics, claim

## Goal
Track return/refund cases and quantify impact on order outcomes and cash flow.

## Scope
- Return/refund/dispute endpoints available to seller app permissions.
- `/order/reverse/return/detail/list`
- `/order/reverse/return/history/list`
- `/order/reverse/reason/list`
- `/reverse/getreverseordersforseller`

## Deterministic Helper Commands (Preferred)
- Return detail list:
  - `python3 -m lazada_helper.cli returns-refunds return-detail-list --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
- Return history list:
  - `python3 -m lazada_helper.cli returns-refunds return-history-list --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
- Return reason list:
  - `python3 -m lazada_helper.cli returns-refunds reason-list`
- Reverse orders for seller:
  - `python3 -m lazada_helper.cli returns-refunds get-reverse-orders-for-seller --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`

## Endpoint Mapping
- `returns-refunds return-detail-list` -> `/order/reverse/return/detail/list`
- `returns-refunds return-history-list` -> `/order/reverse/return/history/list`
- `returns-refunds reason-list` -> `/order/reverse/reason/list`
- `returns-refunds get-reverse-orders-for-seller` -> `/reverse/getreverseordersforseller`

## Execution Notes
- Run commands via `python3 -m lazada_helper.safe_run -- ...` and parse stdout JSON.
- If output exceeds tool limits, use the provided output file path from the tool metadata.

## Inputs
- Date window
- Case status (open/closed/approved/rejected, if supported)
- Optional order id or SKU filters

## Workflow
1. Identify return/refund endpoint and required parameters from Lazada docs.
2. Execute paginated retrieval using configured Lazada credentials.
3. Normalize case-level fields:
   - case id
   - order id
   - status
   - refund amount
   - created/updated timestamps
4. Summarize volume and amounts by status and time period.

## Output Requirements
- Return case count, refund total, and status distribution.
- Flag unresolved/pending cases and any partial retrieval limits.
