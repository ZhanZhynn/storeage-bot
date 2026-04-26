# Lazada Returns & Refunds Summary

keywords: lazada, return, returns, refund, refunds, dispute, reverse logistics, claim

## Quick Answer (Use This)

```bash
# Get return/refund cases in date range:
python3 -m platform_helpers.lazada.cli returns-refunds return-history-list --created-after 2026-04-01 --created-before 2026-04-30

# Get reverse orders for seller (uses timestamps in ms):
python3 -m platform_helpers.lazada.cli returns-refunds get-reverse-orders-for-seller --created-after 2026-04-01 --created-before 2026-04-30
```

Returns: `returns[]` with `order_id`, `reason`, `status`, `refund_amount`

<!-- END_QUICK_ANSWER -->

---

# Full Documentation

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
  - `python3 -m platform_helpers.lazada.cli returns-refunds return-detail-list --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --offset 0 --max-pages 10 --reverse-order-id 699003535083717`
- Return history list:
  - `python3 -m platform_helpers.lazada.cli returns-refunds return-history-list --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --offset 0 --max-pages 10 --reverse-order-line-id 699003535183717`
- Return reason list:
  - `python3 -m platform_helpers.lazada.cli returns-refunds reason-list --reverse-order-line-id 699003535183717`
- Reverse orders for seller:
  - `python3 -m platform_helpers.lazada.cli returns-refunds get-reverse-orders-for-seller --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --max-pages 10`

**Note**: `get-reverse-orders-for-seller` uses timestamps (`TradeOrderLineCreatedTimeRangeStart/End`) in milliseconds, not date strings.

## Datetime Input Rules
- `created_after` and `created_before` must use `YYYY-MM-DD`.
- Date-only values are interpreted in Malaysia timezone (`+08:00`) with end-of-day handling for `*_before` (`23:59:59.999`).

## Endpoint Mapping
- `returns-refunds return-detail-list` -> `/order/reverse/return/detail/list`
- `returns-refunds return-history-list` -> `/order/reverse/return/history/list`
- `returns-refunds reason-list` -> `/order/reverse/reason/list`
- `returns-refunds get-reverse-orders-for-seller` -> `/reverse/getreverseordersforseller`

## Response Fields
- `return-history-list`: `returns[]` contains `return_id`, `order_id`, `order_item_id`, `item_id`, `reason`, `status`, `created_at`
- `get-reverse-orders-for-seller`: `orders[]` contains `reverse_order_id`, `trade_order_id`, `request_type`, `is_rtm`, `reverse_status`, `ofc_status`, `reason_text`, `refund_amount`, `tracking_number`

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
