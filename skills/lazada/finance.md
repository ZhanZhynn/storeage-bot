# Lazada Finance Retrieval

keywords: lazada, finance, transaction, payout, statement, settlement, wallet, fee, income

## Goal
Fetch Lazada financial records needed for payout reconciliation and fee analysis.

## Scope
- Settlement and transaction history endpoints in Lazada finance domain.
- Fee components and net settlement values where available.

## Deterministic Helper Commands (Preferred)
- Payout status:
  - `python3 -m lazada_helper.cli finance payout-status-get --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
- Account transactions:
  - `python3 -m lazada_helper.cli finance account-transactions-query --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
- Logistics fee detail:
  - `python3 -m lazada_helper.cli finance logistics-fee-detail --created-after <ISO8601> --created-before <ISO8601> --limit 100 --offset 0 --max-pages 10`
- Transaction details:
  - `python3 -m lazada_helper.cli finance transaction-details-get --transaction-number <TRANSACTION_NUMBER>`

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
