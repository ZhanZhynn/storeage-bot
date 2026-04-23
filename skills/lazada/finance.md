# Lazada Finance Retrieval

keywords: lazada, finance, transaction, payout, statement, settlement, wallet, fee, income

## Goal
Fetch Lazada financial records needed for payout reconciliation and fee analysis.

## Scope
- Settlement and transaction history endpoints in Lazada finance domain.
- Fee components and net settlement values where available.

## Deterministic Helper Commands (Preferred)
- Payout status:
  - `python3 -m lazada_helper.cli finance payout-status-get --created-after 2026-04-01 --created-before 2026-04-21 --limit 100 --offset 0 --max-pages 10`

- Account transactions:
  - `python3 -m lazada_helper.cli finance account-transactions-query --start-time 2026-04-01 --end-time 2026-04-30 --page-num 1 --page-size 10 --max-pages 10`
  - `python3 -m lazada_helper.cli finance account-transactions-query --transaction-type Deposit --sub-transaction-type Deposit --transaction-number 1001 --start-time 2022-06-01 --end-time 2022-06-02 --page-num 1 --page-size 10 --max-pages 10`

- Logistics fee detail:
  - `python3 -m lazada_helper.cli finance logistics-fee-detail --seller-id 300163725140 --request-type OPEN_API --biz-flow-type LAZADA --bill-start-time 2026-04-01 --bill-end-time 2026-04-30 --page-no 1 --page-size 10 --max-pages 10`
  - `python3 -m lazada_helper.cli finance logistics-fee-detail --seller-id 1002 --request-type OPEN_API --trade-order-id 9432987348 --trade-order-line-id 9432997348 --fee-type COD --biz-flow-type LAZADA --bill-start-time 2022-01-13 --bill-end-time 2022-01-13 --page-no 1 --page-size 10 --total-records 1000 --max-pages 10`

- Transaction details:
  - `python3 -m lazada_helper.cli finance transaction-details-get --start-time 2026-04-01 --end-time 2026-04-30 --offset 0 --limit 100`
  - `python3 -m lazada_helper.cli finance transaction-details-get --trade-order-id 123123213213 --trade-order-line-id 45645674566 --trans-type -1 --start-time 2021-01-01 --end-time 2021-01-05 --offset 0 --limit 100`

## Parameter Specification Tables

### `account-transactions-query`

| Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `transaction_type` | String | No | Primary transaction type. Common values include `Deposit`, `Withdrawal`, `Payment`. |
| `sub_transaction_type` | String | No | Subtype of transaction. Example values: `Settlement`, `Failed Payment`, `Returned Payment`, `Auto Withdrawal`, `Manual Withdrawal`, `Sponsored Solutions Top-up`. |
| `transaction_number` | String | No | Specific transaction identifier to filter by. |
| `start_time` | String (`YYYY-MM-DD`) | Yes | Start date in CLI input. Helper converts to Lazada format `YYYYMMDD`. |
| `end_time` | String (`YYYY-MM-DD`) | Yes | End date in CLI input. Helper converts to Lazada format `YYYYMMDD`. |
| `page_num` | Number | No | Page index. Default is `1`. |
| `page_size` | Number | No | Records per page. Default is `10`. |

### `logistics-fee-detail`

| Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `seller_id` | String | No | Seller identifier. Required by some Lazada regions/scopes. |
| `request_type` | String | No | Request source/type, for example `OPEN_API`. |
| `trade_order_id` | String | No | Trade order identifier. |
| `trade_order_line_id` | String | No | Trade order line identifier. |
| `fee_type` | String | No | Logistics fee category, for example `COD`. |
| `biz_flow_type` | String | No | Settlement scenario, for example `LAZADA` or `LAZADA_3PV`. |
| `bill_start_time` | String (`YYYY-MM-DD`) | Yes | Start date in CLI input. Helper converts to epoch milliseconds (start of day, MY timezone). |
| `bill_end_time` | String (`YYYY-MM-DD`) | Yes | End date in CLI input. Helper converts to epoch milliseconds (end of day, MY timezone). |
| `page_no` | Number | No | Page number. Default is `1`. |
| `page_size` | Number | No | Records per page. Default is `10`. |
| `total_records` | Number | No | Optional total records hint used by some implementations. |

### `transaction-details-get`

| Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `trade_order_id` | String | No | Trade order identifier filter. |
| `trade_order_line_id` | String | No | Trade order line identifier filter. |
| `trans_type` | String | No | Transaction type filter (docs commonly use `-1` for all types). |
| `start_time` | String (`YYYY-MM-DD`) | Yes | Start date in CLI input. Helper sends Lazada date string format. |
| `end_time` | String (`YYYY-MM-DD`) | Yes | End date in CLI input. Helper sends Lazada date string format. |
| `offset` | Number | No | Offset for pagination. Default is `0`. |
| `limit` | Number | No | Max records per request. Default is `100`. |

## Parameter Rules
- `payout-status-get` uses `created_after` and `created_before` (datetime filters).
- `account-transactions-query` uses `start_time` and `end_time` with `page_num` / `page_size`; pass `YYYY-MM-DD`, helper converts to `YYYYMMDD`.
- `logistics-fee-detail` uses `bill_start_time` and `bill_end_time` with `page_no` / `page_size`; pass `YYYY-MM-DD`, helper converts to epoch milliseconds.
- `transaction-details-get` uses `start_time` and `end_time` plus optional order filters.
- For finance time params, always use `YYYY-MM-DD` in CLI input.

## Endpoint Mapping
- `payout-status-get` -> `/finance/payout/status/get`
- `account-transactions-query` -> `/finance/transaction/accountTransactions/query`
- `logistics-fee-detail` -> `/lbs/slb/queryLogisticsFeeDetail`
- `transaction-details-get` -> `/finance/transaction/details/get`

## Workflow
1. Confirm reporting period and timezone with user intent (daily/weekly/monthly/custom).
2. Query relevant finance endpoint(s) with date filters and pagination.
3. Normalize records into consistent finance fields:
   - gross amount
   - fee amount(s)
   - net payout/settlement
   - transaction type
   - transaction date
4. Reconcile totals and call out missing/unknown fields explicitly.

## Output Requirements
- Provide totals for gross, fees, and net.
- Include transaction count and date window used.
- Highlight data caveats (partial pages, unavailable fee fields, or endpoint scope limits).

## Execution Notes
- Run deterministic helper commands through safe wrapper and parse stdout JSON.
- Avoid redirecting output to `/tmp/*`; use `--save-json data/<name>.json` when persistence is needed.
