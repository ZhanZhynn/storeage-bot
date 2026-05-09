# Shopee Orders Summary

keywords: shopee, orders, order, cancel, split, package, shipment, buyer cancellation, package list

## Quick Answer (Use This)

```bash
# Fetch orders (default)
python3 -m platform_helpers.shopee.cli orders get --days 7

# Fetch order items
python3 -m platform_helpers.shopee.cli orders items --order-sn-list <ORDER_SN>
```

Returns: order list or order item list.

<!-- END_QUICK_ANSWER -->

---

# Full Documentation

## Goal
Retrieve Shopee order lists, order items, manage cancellations, split/unsplit orders, and query package lists.

## Common Endpoint Family
- `/api/v2/order/get_order_list`
- `/api/v2/order/get_order_detail`
- `/api/v2/order/cancel_order`
- `/api/v2/order/handle_buyer_cancellation`
- `/api/v2/order/split_order`
- `/api/v2/order/unsplit_order`
- `/api/v2/order/search_package_list`
- `/api/v2/order/get_package_detail`

## Deterministic Helper Commands (Preferred)
- Fetch orders:
  - `python3 -m platform_helpers.shopee.cli orders get --days 7`
  - `python3 -m platform_helpers.shopee.cli orders get --days 14 --page-size 10 --max-pages 1`
  - `python3 -m platform_helpers.shopee.cli orders get --days 1 --page-size 20 --max-pages 5`
- Fetch order items:
  - `python3 -m platform_helpers.shopee.cli orders items --order-sn-list <ORDER_SN>`
  - `python3 -m platform_helpers.shopee.cli orders items --order-sn-list <ORDER_SN1>,<ORDER_SN2>`
- Cancel order:
  - `python3 -m platform_helpers.shopee.cli orders cancel --order-sn <ORDER_SN> --cancel-reason OUT_OF_STOCK --item-list '[{"item_id":1680783,"model_id":327890123}]'`
- Handle buyer cancellation:
  - `python3 -m platform_helpers.shopee.cli orders buyer-cancel --order-sn <ORDER_SN> --operation ACCEPT`
- Split order evenly across max N packages:
  - `python3 -m platform_helpers.shopee.cli orders split-max --order-sn <ORDER_SN> --max-packages 2 --package-number <PKG_NO>`
  - Uses floor division: `items_per_pkg = floor(total_items / max_packages)`, remainder distributed to first packages.
  - Example: 3 items, max 2 → pkg1 gets 2, pkg2 gets 1.
- Unsplit order:
  - `python3 -m platform_helpers.shopee.cli orders unsplit --order-sn <ORDER_SN>`
- Search package list:
  - `python3 -m platform_helpers.shopee.cli orders pkg-search --page-size 50 --filter '{"package_status":2}' --sort '{"sort_type":1,"ascending":false}'`
  - `python3 -m platform_helpers.shopee.cli orders pkg-search --page-size 5 --filter '{"package_status":0}' --max-pages 1`
- Get package detail:
  - `python3 -m platform_helpers.shopee.cli orders pkg-detail --package-number-list <PACKAGE_NO>`
  - `python3 -m platform_helpers.shopee.cli orders pkg-detail --package-number-list <PKG1>,<PKG2>,<PKG3>`

## Pagination
- `orders get`: uses cursor pagination (`--max-pages`)
- `orders pkg-search`: uses cursor pagination inside `pagination.cursor`

## Endpoint Mapping
- `orders get` -> `/api/v2/order/get_order_list`
- `orders items` -> `/api/v2/order/get_order_detail`
- `orders cancel` -> `/api/v2/order/cancel_order`
- `orders buyer-cancel` -> `/api/v2/order/handle_buyer_cancellation`
- `orders split` -> `/api/v2/order/split_order`
- `orders unsplit` -> `/api/v2/order/unsplit_order`
- `orders pkg-search` -> `/api/v2/order/search_package_list`
- `orders pkg-detail` -> `/api/v2/order/get_package_detail`

## Execution Notes
- Execute helper command via `python3 -m platform_helpers.shopee.safe_run -- ...` and summarize JSON fields directly.

## Test Learnings (from smoke tests)

### Order list search
- Shopee only allows a maximum **15-day window** per query. Requesting > 15 days returns `order.order_list_invalid_time`.
- Always use `--days 14` or `--days 15` to stay within the limit.

### Cancel order
- `cancel_reason` must be a valid enum value: `OUT_OF_STOCK`, `CUSTOMER_REQUEST`, `UNDELIVERABLE_AREA` (TW/MY only), `COD_NOT_SUPPORTED`. Invalid reason returns `error_param`.
- For `OUT_OF_STOCK`, `item_list` is required (array of `{item_id, model_id}`). Missing item_list returns `error_param` "no item ids are given".
- Successful cancel returns `{update_time: <timestamp>}`.

### Split order
- `can_split_order` in `pkg-detail` tells whether an order supports splitting.
- **Proper flow to find split-able orders:**
  1. Search packages: `python3 -m platform_helpers.shopee.cli orders pkg-search --page-size 50 --filter '{"package_status":0}' --max-pages 1`
  2. Get package detail for an order: `python3 -m platform_helpers.shopee.cli orders pkg-detail --package-number-list <PKG_NO>`
  3. Check `can_split_order: true` in response — only then proceed with split.
- All items from the order must be included across the packages in a single request.
- Single-item orders (one item with model_quantity == total) cannot be split: returns `error_param` "size of package list is over limit".
- Successful split returns `package_list` with new `package_number` for each package.
- For multi-item orders, separate each item (or group of items) into its own package object.

### Split-max (even split)
- `split-max` command splits an order into at most N packages, distributed evenly using floor division.
- Algorithm: `items_per_pkg = floor(total_items / max_packages)`, remainder items go to first packages.
- Example: 3 items, max 2 → pkg1 has 2, pkg2 has 1. 5 items, max 2 → pkg1 has 3, pkg2 has 2.
- `split-max` fetches item list from the existing package automatically — only needs `--order-sn`, `--max-packages`, `--package-number`.
- Example: `python3 -m platform_helpers.shopee.cli orders split-max --order-sn 26050904HPPJ39 --max-packages 2 --package-number <PKG>`

### Unsplit order
- `can_unsplit_order` in `pkg-detail` tells whether an order supports unsplitting.
- Only works on orders that were previously split. Calling on a non-split order returns `error` "Cannot undo split this order".
- Successful unsplit returns empty `response: {}`.

### Handle buyer cancellation
- Only works when order status is `IN_CANCEL`. Returns `error` "Invalid order_status.The order status should be IN_CANCEL." otherwise.
- Operation values: `ACCEPT` or `REJECT`.

### Package search
- `package_status` filter: 0=All, 1=Pending, 2=ToProcess (default), 3=Processed.
- `fulfillment_type` filter: 0=None, 1=Shopee, 2=Seller (default).
- For JSON `--filter` and `--sort` args, escape double quotes in the shell, e.g., `--filter "{\"package_status\":2}"`.

### Package detail
- Response includes `item_list`, `recipient_address`, `fulfillment_status`, `can_split_order`, `can_unsplit_order`, `is_shipment_arranged`, and more.
- Multiple package numbers can be fetched in a single call (comma-separated).

## Inputs to Clarify
- Order SN(s) to act on
- Cancel reason and item list (required for OUT_OF_STOCK)
- Package split structure (must include all items in order)
- Filters/sort for package search

## Guardrails
- Cancel/handle buyer cancellation only on eligible order statuses.
- Split order requires complete item coverage across all packages in one request.
- Use cursor-based pagination for package search to avoid missing packages.