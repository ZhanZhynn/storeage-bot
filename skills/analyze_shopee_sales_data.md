# Shopee Sales Analysis Skills

**keywords**: shopee, analyze, sales, revenue, trend, kpi, dashboard, sql, sqlite, table, query, p&l, profit, margin, aggregation

**tables**: shopee_orders, shopee_order_items

## Goal
Turn raw e-commerce data into high-integrity, decision-ready insights. Prioritize data validation and performance through SQL-first aggregation while ensuring no double-deduction of fees/shipping.

## Use When
- Analyzing sales performance, profitability, SKU or product trends, or fee leakage.
- Comparing time-based growth (MoM/WoW) or promotional efficiency.
- Handling SQLite databases or normalized spreadsheet exports.

## Setup & Optimization
- **Environment**: Always set `PRAGMA cache_size = 10000;` and `PRAGMA foreign_keys = ON;`.
- **Performance**: If queries are slow, ensure these indexes exist:
    - `CREATE INDEX IF NOT EXISTS idx_shopee_orders_paid_time ON shopee_orders(order_paid_time);`
    - `CREATE INDEX IF NOT EXISTS idx_shopee_order_items_order_id ON shopee_order_items(order_id);`
- **Verification**: Use `EXPLAIN QUERY PLAN` to ensure indexes are utilized for date filters and joins.

## Data Health Check (Pre-Analysis)
Before reporting results, run a "Health Check" to identify data gaps:
1. **Orphaned Rows**: Compare `COUNT(DISTINCT order_id)` between the orders and items tables. Flag discrepancies (e.g., thousands of orders but only a few item rows).
2. **Missing Metadata**: Check for NULLs in critical fields (`grand_total`, `total_amount`, `order_paid_time`).
3. **Status Check**: Verify if the data includes "Cancelled" or "Returned" orders and state the assumption in the report.

## Query Workflow
1. **Aggregate Items First**: Use a CTE to aggregate item-level data (Price * Qty, Seller Discounts) per `order_id` *before* joining to the main orders table.
1a. **Product trend**: When asked to analyze sales trend of a product, user might just give the approximate product name such as Raya paper bags and not give the exact SKU Reference No. , you'll have use infer which product the user is asking about. You can shortlist the items after running sql ilike function, the product name must at least contain the case-insensitive keywords mentioned, once you have a list of the products, double check the product name to further shortlist the relevant items based on how relevant is the keyword to the product names, then only query the data by the sku reference no. if unsure, ask the user for further clarification.
2. **Handle NULLs**: Wrap all monetary math in `COALESCE(field, 0)` to prevent NULL propagation.
3. **Join Strategy**: Use `LEFT JOIN` on `order_id` to ensure no orders are dropped from the topline summary.
4. **Time Bucketing**: Use `STRFTIME('%Y-%m', order_paid_time)` for monthly or `%Y-%W` for weekly grouping.

## Canonical Column Source of Truth

### `shopee_orders` (one row per order)
- Keys and time: `order_id`, `order_paid_time`, `order_creation_date`, `order_complete_time`.
- Order-level payout and fee fields:
  - `total_amount`
  - `grand_total`
  - `buyer_paid_shipping_fee`
  - `shipping_rebate_estimate`
  - `reverse_shipping_fee`
  - `transaction_fee`
  - `commission_fee`
  - `service_fee`
  - `seller_bundle_discount`
  - `shopee_bundle_discount`

### `shopee_order_items` (many rows per order)
- Keys and SKU metadata: `order_id`, `sku_reference_no`, `product_name`, `variation_name`.
- Item-level sales and discount fields:
  - `deal_price`
  - `quantity`
  - `returned_quantity`
  - `total_buyer_payment`
  - `seller_discount`
  - `seller_rebate`
  - `shopee_rebate`

### Source Rules
- Use `shopee_orders.grand_total` as the primary payout KPI.
- Use `shopee_order_items.seller_discount` for seller-funded discount analysis (it does not exist in `shopee_orders`).
- Never sum item-level fields directly after joining to raw order rows; always aggregate `shopee_order_items` to order-level first.

## Data Type Guard (Critical)
- SQLite column declaration is not strict storage typing. A column declared `INTEGER` can still store BLOB values.
- Before item-level math, validate type integrity:
  - `SELECT typeof(quantity), COUNT(*) FROM shopee_order_items GROUP BY 1;`
  - `SELECT typeof(deal_price), COUNT(*) FROM shopee_order_items GROUP BY 1;`
- Required state for reliable item math:
  - `quantity` should be `integer`
  - `deal_price` should be `real` or `integer`
- If `quantity` is `blob`, flag results as invalid for item GMV/units and request data re-normalization before final reporting.

## Metric Definitions & Reconciliation Logic
Based on row-level reconciliation (e.g., Image_987498.png), follow these precise definitions to avoid double-deductions or missed inflows:

### 1. The Payout Base
- **Total Buyer Payment**: What the customer paid. (Reflects customer's cost, not seller's base).
- **Total Amount**: The gross base for payout calculation.
    - *Logic*: `(Deal Price * Quantity) + Buyer Paid Shipping Fee`.

### 2. The "Grand Total" (Payout) Formula
The `Grand Total` column is the final settlement. To reconcile it from the `Total Amount`, use:
> **Grand Total** = `Total Amount` + `Shipping Rebate Estimate` + `Seller Rebate` - (`Buyer Paid Shipping Fee` + `Transaction Fee` + `Commission Fee` + `Service Fee` + `Reverse Shipping Fee` + `Seller Discount` + `Shopee Bundle Discount`)

### 3. Key Guards
- **No Double-Deduction**: If the analysis uses `Grand Total` as the starting point for profit, do NOT subtract fees again; they are already deducted.
- **Seller vs. Shopee Funding**: 
    - Deduct `Seller Discount` and `Seller Bundle Discount` as they come out of the seller's pocket.
    - `Shopee Rebate` and `Voucher Sponsored by Shopee` are typically neutral to the final payout.

## Accurate Calculation Patterns

### A) Net Payout (Topline)
Use this when the business asks "how much money was settled to seller":

```sql
SELECT
  STRFTIME('%Y-%m', o.order_paid_time) AS month,
  COUNT(DISTINCT o.order_id) AS orders,
  ROUND(SUM(COALESCE(o.grand_total, 0)), 2) AS net_payout
FROM shopee_orders o
GROUP BY 1
ORDER BY 1;
```

### B) Item Metrics Without Double Counting
Always aggregate items by `order_id` first, then join:

```sql
WITH item_agg AS (
  SELECT
    i.order_id,
    SUM(COALESCE(i.quantity, 0)) AS units,
    SUM(COALESCE(i.deal_price, 0) * COALESCE(i.quantity, 0)) AS item_gmv,
    SUM(COALESCE(i.seller_discount, 0)) AS seller_discount,
    SUM(COALESCE(i.seller_rebate, 0)) AS seller_rebate
  FROM shopee_order_items i
  GROUP BY i.order_id
),
orders_filtered AS (
  SELECT *
  FROM shopee_orders
  WHERE STRFTIME('%Y-%m', order_paid_time) = '2026-01'
)
SELECT
  COUNT(DISTINCT o.order_id) AS orders,
  ROUND(SUM(COALESCE(o.grand_total, 0)), 2) AS net_payout,
  ROUND(SUM(COALESCE(a.units, 0)), 2) AS units,
  ROUND(SUM(COALESCE(a.item_gmv, 0)), 2) AS item_gmv,
  ROUND(SUM(COALESCE(a.seller_discount, 0)), 2) AS seller_discount,
  ROUND(SUM(COALESCE(a.seller_rebate, 0)), 2) AS seller_rebate
FROM orders_filtered o
LEFT JOIN item_agg a ON a.order_id = o.order_id;
```

### C) Reconciliation Check
Validate payout logic and data integrity before publishing:

```sql
SELECT
  COUNT(DISTINCT o.order_id) AS total_orders,
  COUNT(DISTINCT i.order_id) AS orders_with_items,
  COUNT(DISTINCT o.order_id) - COUNT(DISTINCT i.order_id) AS orphaned_orders,
  SUM(CASE WHEN o.grand_total IS NULL THEN 1 ELSE 0 END) AS null_grand_total,
  SUM(CASE WHEN o.order_paid_time IS NULL THEN 1 ELSE 0 END) AS null_order_paid_time,
  MIN(o.order_paid_time) AS min_order_paid_time,
  MAX(o.order_paid_time) AS max_order_paid_time
FROM shopee_orders o
LEFT JOIN shopee_order_items i ON i.order_id = o.order_id;
```

## Profit Semantics (Do Not Mislabel)
- `SUM(grand_total)` is net settlement payout, not full accounting profit.
- True profit requires COGS (and optionally ads/ops overhead) from external tables.
- Recommended naming in outputs:
  - `net_payout` for `SUM(grand_total)`
  - `estimated_gross_margin` only after joining reliable COGS

## Analysis Expectations
- **Drivers**: Explain revenue changes via Price Mix (AOV) vs. Volume (Units/Order).
- **Efficiency**: Call out "Fee Leakage" (Total Fees / Gross Sales) and identify high-cost categories.
- **Data Limits**: Explicitly mention floating-point rounding if using `REAL` types; suggest `ROUND(val, 2)` or integer cents for final summaries.
- **Recommendations**: End with 2-3 practical actions (e.g., "Optimize bundle deals for SKU X to offset high service fees").

## Output Style
- **Concise**: Decision-focused summaries first.
- **Tables**: Use markdown tables for Numbers/SKU/Date rankings.
- **Assumptions**: Include a short block detailing whether calculations start from `Total Amount` or `Grand Total`.
