import argparse
import json
import random
import sys
import time as time_module
from datetime import datetime, time, timedelta, timezone
from typing import Any

from .client import (LazadaAPIError, LazadaClient, LazadaConfig,
                     LazadaConfigError)
from .finance import (get_payout_status, get_transaction_details,
                      query_account_transactions, query_logistics_fee_detail)
from .orders import (build_default_order_window, fetch_orders,
                     get_multiple_order_items, get_order_items_by_order_id,
                     validate_order_cancel)
from .products import get_product_item, get_products
from .returns_refunds import (get_reverse_orders_for_seller,
                              list_return_detail, list_return_history,
                              list_return_reasons)
from .reviews import (add_seller_review_reply, list_seller_reviews_history,
                      list_seller_reviews_v2)

_MALAYSIA_TZ = timezone(timedelta(hours=8))
_DATETIME_FILTER_FIELDS = (
    "created_after",
    "created_before",
    "update_after",
    "update_before",
    "create_after",
    "create_before",
)
_DATETIME_FILTER_HELP = (
    "Use YYYY-MM-DD. Helper normalizes to Lazada API datetime format in Malaysia timezone (+08:00)."
)
_DATE_ONLY_HELP = "Use YYYY-MM-DD. Helper normalizes to the endpoint's required Lazada format."


def _parse_to_malaysia_date(value: str | None, *, field_name: str) -> datetime.date:
    if value is None:
        raise ValueError(f"{field_name} is required")

    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} is required")

    if len(text) == 10 and "T" not in text:
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError as err:
            raise ValueError(f"{field_name} must use YYYY-MM-DD") from err

    raise ValueError(f"{field_name} must use YYYY-MM-DD")


def _normalize_date_for_api(value: str | None, *, field_name: str) -> str:
    return _parse_to_malaysia_date(value, field_name=field_name).isoformat()


def _normalize_compact_date_for_api(value: str | None, *, field_name: str) -> str:
    parsed = _parse_to_malaysia_date(value, field_name=field_name)
    return parsed.strftime("%Y%m%d")


def _normalize_bill_date_for_api(value: str | None, *, field_name: str, is_end: bool) -> str:
    parsed = _parse_to_malaysia_date(value, field_name=field_name)
    if is_end:
        dt = datetime.combine(parsed, time(23, 59, 59, 999000), _MALAYSIA_TZ)
    else:
        dt = datetime.combine(parsed, time(0, 0, 0), _MALAYSIA_TZ)
    return str(int(dt.timestamp() * 1000))


def _normalize_datetime_filter(value: str | None, *, is_before: bool) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        date_value = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as err:
        raise ValueError("date filters must use YYYY-MM-DD") from err

    if is_before:
        dt = datetime.combine(date_value, time(23, 59, 59, 999000), _MALAYSIA_TZ)
        return dt.isoformat()

    dt = datetime.combine(date_value, time(0, 0, 0), _MALAYSIA_TZ)
    return dt.isoformat()


def _normalize_datetime_filters(args: argparse.Namespace) -> None:
    skip_created_filters = args.domain == "finance" and args.action == "payout-status-get"
    for field in _DATETIME_FILTER_FIELDS:
        if skip_created_filters and field in ("created_after", "created_before"):
            continue
        if not hasattr(args, field):
            continue
        value = getattr(args, field)
        normalized = _normalize_datetime_filter(value, is_before=field.endswith("_before"))
        setattr(args, field, normalized)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic Lazada API helper")
    subparsers = parser.add_subparsers(dest="domain", required=True)

    orders = subparsers.add_parser("orders", help="Order domain operations")
    orders_subparsers = orders.add_subparsers(dest="action", required=True)

    orders_get = orders_subparsers.add_parser("get", help="Fetch orders via /orders/get")
    orders_get.add_argument(
        "--created-after", dest="created_after", default=None, help=_DATETIME_FILTER_HELP
    )
    orders_get.add_argument(
        "--created-before", dest="created_before", default=None, help=_DATETIME_FILTER_HELP
    )
    orders_get.add_argument(
        "--update-after", dest="update_after", default=None, help=_DATETIME_FILTER_HELP
    )
    orders_get.add_argument(
        "--update-before", dest="update_before", default=None, help=_DATETIME_FILTER_HELP
    )
    orders_get.add_argument("--days", type=int, default=30)
    orders_get.add_argument("--status", default="all")
    orders_get.add_argument("--limit", type=int, default=100)
    orders_get.add_argument("--offset", type=int, default=0)
    orders_get.add_argument("--sort-by", dest="sort_by", default="updated_at")
    orders_get.add_argument("--sort-direction", dest="sort_direction", default="DESC")
    orders_get.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    orders_item_get = orders_subparsers.add_parser("item-get", help="Fetch order items via /order/items/get")
    orders_item_get.add_argument("--order-id", dest="order_id", required=True)

    orders_items_multiple = orders_subparsers.add_parser("items-multiple", help="Fetch multiple order items via /orders/items/get")
    orders_items_multiple.add_argument("--order-ids", dest="order_ids", required=True, help="JSON array of order IDs")

    orders_cancel_validate = orders_subparsers.add_parser("cancel-validate", help="Validate order cancel via /order/reverse/cancel/validate")
    orders_cancel_validate.add_argument("--order-id", dest="order_id", required=True)
    orders_cancel_validate.add_argument("--order-item-id-list", dest="order_item_id_list", default=None, help="JSON array of order item IDs")

    orders_summary = orders_subparsers.add_parser(
        "summary", help="Get order summary with status breakdown in one call"
    )
    orders_summary.add_argument("--days", type=int, default=1, help="Number of days to look back")
    orders_summary.add_argument("--date", type=str, default=None, help="Specific date (YYYY-MM-DD), takes precedence over --days")
    orders_summary.add_argument(
        "--short",
        action="store_true",
        help="Return summary only (no order list), faster for Slack/cron",
    )

    finance = subparsers.add_parser("finance", help="Finance domain operations")
    finance_subparsers = finance.add_subparsers(dest="action", required=True)

    payout_status_cmd = finance_subparsers.add_parser(
        "payout-status-get", help="Fetch payout status via /finance/payout/status/get"
    )
    payout_status_cmd.add_argument("--created-after", required=True, help=_DATETIME_FILTER_HELP)
    payout_status_cmd.add_argument("--created-before", required=True, help=_DATETIME_FILTER_HELP)
    payout_status_cmd.add_argument("--limit", type=int, default=100)
    payout_status_cmd.add_argument("--offset", type=int, default=0)
    payout_status_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    account_tx_cmd = finance_subparsers.add_parser(
        "account-transactions-query",
        help="Query account transactions via /finance/transaction/accountTransactions/query",
    )
    account_tx_cmd.add_argument("--transaction-type", default=None)
    account_tx_cmd.add_argument("--sub-transaction-type", default=None)
    account_tx_cmd.add_argument("--transaction-number", default=None)
    account_tx_cmd.add_argument("--start-time", required=True, help=_DATE_ONLY_HELP)
    account_tx_cmd.add_argument("--end-time", required=True, help=_DATE_ONLY_HELP)
    account_tx_cmd.add_argument("--page-num", type=int, default=1)
    account_tx_cmd.add_argument("--page-size", type=int, default=10)
    account_tx_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    logistics_fee_cmd = finance_subparsers.add_parser(
        "logistics-fee-detail",
        help="Query logistics fee detail via /lbs/slb/queryLogisticsFeeDetail",
    )
    logistics_fee_cmd.add_argument("--seller-id", default=None)
    logistics_fee_cmd.add_argument("--request-type", default=None)
    logistics_fee_cmd.add_argument("--trade-order-id", default=None)
    logistics_fee_cmd.add_argument("--trade-order-line-id", default=None)
    logistics_fee_cmd.add_argument("--fee-type", default=None)
    logistics_fee_cmd.add_argument("--biz-flow-type", default=None)
    logistics_fee_cmd.add_argument("--bill-start-time", required=True, help=_DATE_ONLY_HELP)
    logistics_fee_cmd.add_argument("--bill-end-time", required=True, help=_DATE_ONLY_HELP)
    logistics_fee_cmd.add_argument("--page-no", type=int, default=1)
    logistics_fee_cmd.add_argument("--page-size", type=int, default=10)
    logistics_fee_cmd.add_argument("--total-records", type=int, default=None)
    logistics_fee_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    tx_details_cmd = finance_subparsers.add_parser(
        "transaction-details-get",
        help="Get transaction details via /finance/transaction/details/get",
    )
    tx_details_cmd.add_argument("--trade-order-id", default=None)
    tx_details_cmd.add_argument("--trade-order-line-id", default=None)
    tx_details_cmd.add_argument("--trans-type", default=None)
    tx_details_cmd.add_argument("--start-time", required=True, help=_DATE_ONLY_HELP)
    tx_details_cmd.add_argument("--end-time", required=True, help=_DATE_ONLY_HELP)
    tx_details_cmd.add_argument("--offset", type=int, default=0)
    tx_details_cmd.add_argument("--limit", type=int, default=100)

    products = subparsers.add_parser("products", help="Product domain operations")
    products_subparsers = products.add_subparsers(dest="action", required=True)

    products_get_cmd = products_subparsers.add_parser("get", help="Fetch products via /products/get")
    products_get_cmd.add_argument("--filter", dest="filter_expr", default="all")
    products_get_cmd.add_argument(
        "--create-before", dest="create_before", default=None, help=_DATETIME_FILTER_HELP
    )
    products_get_cmd.add_argument(
        "--create-after", dest="create_after", default=None, help=_DATETIME_FILTER_HELP
    )
    products_get_cmd.add_argument(
        "--update-before", dest="update_before", default=None, help=_DATETIME_FILTER_HELP
    )
    products_get_cmd.add_argument(
        "--update-after", dest="update_after", default=None, help=_DATETIME_FILTER_HELP
    )
    products_get_cmd.add_argument("--offset", type=int, default=0)
    products_get_cmd.add_argument("--limit", type=int, default=10)
    products_get_cmd.add_argument("--options", default="1")
    products_get_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=None)

    product_item_get_cmd = products_subparsers.add_parser(
        "item-get", help="Fetch product detail via /product/item/get"
    )
    product_item_get_cmd.add_argument("--item-id", required=True)

    returns_refunds = subparsers.add_parser(
        "returns-refunds", help="Returns and refunds domain operations"
    )
    rr_subparsers = returns_refunds.add_subparsers(dest="action", required=True)

    rr_detail_cmd = rr_subparsers.add_parser(
        "return-detail-list", help="List return details via /order/reverse/return/detail/list"
    )
    rr_detail_cmd.add_argument("--created-after", required=True, help=_DATETIME_FILTER_HELP)
    rr_detail_cmd.add_argument("--created-before", required=True, help=_DATETIME_FILTER_HELP)
    rr_detail_cmd.add_argument("--offset", type=int, default=0)
    rr_detail_cmd.add_argument("--limit", type=int, default=100)
    rr_detail_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)
    rr_detail_cmd.add_argument("--reverse-order-id", dest="reverse_order_id", type=int, required=True)

    rr_history_cmd = rr_subparsers.add_parser(
        "return-history-list", help="List return history via /order/reverse/return/history/list"
    )
    rr_history_cmd.add_argument("--created-after", required=True, help=_DATETIME_FILTER_HELP)
    rr_history_cmd.add_argument("--created-before", required=True, help=_DATETIME_FILTER_HELP)
    rr_history_cmd.add_argument("--offset", type=int, default=0)
    rr_history_cmd.add_argument("--limit", type=int, default=100)
    rr_history_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)
    rr_history_cmd.add_argument("--reverse-order-line-id", dest="reverse_order_line_id", type=int, required=True)

    rr_reason_cmd = rr_subparsers.add_parser(  # noqa: F841
        "reason-list", help="List return reasons via /order/reverse/reason/list"
    )
    rr_reason_cmd.add_argument("--reverse-order-line-id", dest="reverse_order_line_id", type=int, required=True)

    rr_reverse_orders_cmd = rr_subparsers.add_parser(
        "get-reverse-orders-for-seller",
        help="Fetch reverse orders via /reverse/getreverseordersforseller",
    )
    rr_reverse_orders_cmd.add_argument("--created-after", required=True, help=_DATETIME_FILTER_HELP)
    rr_reverse_orders_cmd.add_argument("--created-before", required=True, help=_DATETIME_FILTER_HELP)
    rr_reverse_orders_cmd.add_argument("--offset", type=int, default=0)
    rr_reverse_orders_cmd.add_argument("--limit", type=int, default=100)
    rr_reverse_orders_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    reviews = subparsers.add_parser("reviews", help="Product review domain operations")
    reviews_subparsers = reviews.add_subparsers(dest="action", required=True)

    review_history_cmd = reviews_subparsers.add_parser(
        "seller-history-list", help="List seller review history via /review/seller/history/list"
    )
    review_history_cmd.add_argument("--created-after", required=True, help=_DATETIME_FILTER_HELP)
    review_history_cmd.add_argument("--created-before", required=True, help=_DATETIME_FILTER_HELP)
    review_history_cmd.add_argument("--item-id", default=None)
    review_history_cmd.add_argument("--current", type=int, default=1)
    review_history_cmd.add_argument("--limit", type=int, default=100)
    review_history_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    review_list_v2_cmd = reviews_subparsers.add_parser(
        "seller-list-v2", help="List seller reviews via /review/seller/list/v2"
    )
    review_list_v2_cmd.add_argument("--id-list", required=True)
    review_list_v2_cmd.add_argument("--item-id", default=None)

    review_reply_add_cmd = reviews_subparsers.add_parser(
        "seller-reply-add", help="Add seller review reply via /review/seller/reply/add"
    )
    review_reply_add_cmd.add_argument("--id-list", required=True)
    review_reply_add_cmd.add_argument("--content", required=True)

    review_item_reviews_cmd = reviews_subparsers.add_parser(
        "get-item-reviews", help="Get item reviews from last 30 days completed orders"
    )
    review_item_reviews_cmd.add_argument("--days", type=int, default=30)
    review_item_reviews_cmd.add_argument(
        "--sort",
        choices=("asc", "desc"),
        default="desc",
        help="Sort reviews by review date: asc=oldest first, desc=newest first",
    )
    review_item_reviews_cmd.add_argument(
        "--max-api-calls",
        type=int,
        default=10,
        help="Max API calls to list_seller_reviews_history (rate limit guard)",
    )

    review_recent_orders_cmd = reviews_subparsers.add_parser(
        "get-recent-orders",
        help="Get reviews for most recent N completed orders",
    )
    review_recent_orders_cmd.add_argument("--days", type=int, default=30)
    review_recent_orders_cmd.add_argument(
        "--max-orders",
        type=int,
        default=10,
        help="Max completed orders to fetch reviews for",
    )
    review_recent_orders_cmd.add_argument(
        "--sort",
        choices=("asc", "desc"),
        default="desc",
        help="Sort reviews by review date: asc=oldest first, desc=newest first",
    )
    review_recent_orders_cmd.add_argument(
        "--max-api-calls",
        type=int,
        default=10,
        help="Max API calls to list_seller_reviews_history (rate limit guard)",
    )

    return parser

def _emit(payload: dict[str, Any], ok: bool, status: str = "ok") -> int:
    body = {
        "ok": ok,
        "status": status,
        **payload,
    }
    sys.stdout.write(json.dumps(body, ensure_ascii=True) + "\n")
    return 0 if ok else 1


def _with_client() -> LazadaClient:
    return LazadaClient(LazadaConfig.from_env())


def _review_timestamp_ms(review: dict[str, Any]) -> int:
    candidates = (
        "review_time",
        "create_time",
        "created_time",
        "created_at",
        "submit_time",
        "gmt_create",
        "createTime",
        "createdTime",
    )
    raw = None
    for key in candidates:
        value = review.get(key)
        if value is not None:
            raw = value
            break

    if raw is None:
        return 0

    text = str(raw).strip()
    if text.isdigit():
        parsed = int(text)
        return parsed if len(text) > 10 else parsed * 1000

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return 0

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def _review_id(review: dict[str, Any]) -> str | None:
    value = review.get("review_id")
    if value is None:
        value = review.get("id")
    if value is None:
        return None
    return str(value)


def _handle_orders_get(args: argparse.Namespace) -> int:
    created_after = args.created_after
    created_before = args.created_before
    update_after = args.update_after
    update_before = args.update_before

    if not (created_after or created_before or update_after or update_before):
        created_after, created_before = build_default_order_window(args.days)

    result = fetch_orders(
        _with_client(),
        created_after=created_after,
        created_before=created_before,
        update_after=update_after,
        update_before=update_before,
        status=args.status,
        limit=args.limit,
        offset=args.offset,
        sort_by=args.sort_by,
        sort_direction=args.sort_direction,
        max_pages=args.max_pages,
    )

    return _emit(
        {
            "domain": "orders",
            "action": "get",
            "filters": {
                "created_after": created_after,
                "created_before": created_before,
                "update_after": update_after,
                "update_before": update_before,
                "status": args.status,
                "limit": args.limit,
                "offset": args.offset,
                "sort_by": args.sort_by,
                "sort_direction": args.sort_direction,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_orders_item_get(args: argparse.Namespace) -> int:
    try:
        result = get_order_items_by_order_id(_with_client(), order_id=args.order_id)
    except Exception as err:
        return _emit({"error": str(err)}, ok=False, status="runtime_error")

    return _emit(
        {
            "domain": "orders",
            "action": "item-get",
            "order_id": args.order_id,
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_orders_items_multiple(args: argparse.Namespace) -> int:
    try:
        order_ids = json.loads(args.order_ids)
    except json.JSONDecodeError as err:
        return _emit({"error": f"Invalid JSON for --order-ids: {err}"}, ok=False, status="runtime_error")

    if not isinstance(order_ids, list):
        return _emit({"error": "--order-ids must be a JSON array"}, ok=False, status="runtime_error")

    try:
        result = get_multiple_order_items(_with_client(), order_ids=order_ids)
    except Exception as err:
        return _emit({"error": str(err)}, ok=False, status="runtime_error")

    return _emit(
        {
            "domain": "orders",
            "action": "items-multiple",
            "order_ids": order_ids,
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_orders_cancel_validate(args: argparse.Namespace) -> int:
    order_item_id_list = None
    if args.order_item_id_list:
        try:
            order_item_id_list = json.loads(args.order_item_id_list)
        except json.JSONDecodeError as err:
            return _emit({"error": f"Invalid JSON for --order-item-id-list: {err}"}, ok=False, status="runtime_error")

        if not isinstance(order_item_id_list, list):
            return _emit({"error": "--order-item-id-list must be a JSON array"}, ok=False, status="runtime_error")

    try:
        result = validate_order_cancel(
            _with_client(),
            order_id=args.order_id,
            order_item_id_list=order_item_id_list,
        )
    except Exception as err:
        return _emit({"error": str(err)}, ok=False, status="runtime_error")

    return _emit(
        {
            "domain": "orders",
            "action": "cancel-validate",
            "order_id": args.order_id,
            "order_item_id_list": order_item_id_list,
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_orders_summary(args: argparse.Namespace) -> int:
    """
    Get order summary with status breakdown in one call.
    Fetches all orders and computes status counts and sales totals.
    Use --short for summary-only output (faster for Slack/cron).
    """
    client = _with_client()

    if args.date:
        created_after = f"{args.date}T00:00:00+08:00"
        created_before = f"{args.date}T23:59:59.999+08:00"
    else:
        created_after, created_before = build_default_order_window(args.days)

    result = fetch_orders(
        client,
        created_after=created_after,
        created_before=created_before,
        status="all",
        limit=100,
        max_pages=1,
    )

    orders = result.orders
    date_used = args.date if args.date else datetime.now(_MALAYSIA_TZ).strftime("%Y-%m-%d")

    status_breakdown: dict[str, int] = {}
    total_sales = 0.0

    for order in orders:
        statuses = order.get("statuses", []) if isinstance(order, dict) else (order.statuses or [])
        if not isinstance(statuses, list):
            statuses = [statuses]

        for s in statuses:
            status_breakdown[s] = status_breakdown.get(s, 0) + 1

        price = order.get("price") if isinstance(order, dict) else order.price
        voucher_seller = order.get("voucher_seller") if isinstance(order, dict) else order.voucher_seller
        shipping_fee_discount_seller = order.get("shipping_fee_discount_seller") if isinstance(order, dict) else order.shipping_fee_discount_seller
        price_str = str(price or "0").replace(",", "")
        voucher_seller_str = str(voucher_seller or "0").replace(",", "")
        shipping_fee_discount_seller = str(shipping_fee_discount_seller or "0").replace(",", "")
        try:
            total_sales += float(price_str) + float(voucher_seller_str) + float(shipping_fee_discount_seller)
        except (ValueError, TypeError):
            pass

    output = {
        "domain": "orders",
        "action": "summary",
        "date": date_used,
        "filters": {
            "created_after": created_after,
            "created_before": created_before,
            "days": args.days,
        },
        "total_orders": len(orders),
        "total_sales": total_sales,
        "status_breakdown": status_breakdown,
    }

    if not getattr(args, "short", False):
        output["orders"] = [o.model_dump() if hasattr(o, "model_dump") else o for o in orders]

    return _emit(output, ok=True)


def _handle_finance_payout_status_get(args: argparse.Namespace) -> int:
    created_after = _normalize_date_for_api(args.created_after, field_name="created_after")
    created_before = _normalize_date_for_api(args.created_before, field_name="created_before")
    result = get_payout_status(
        _with_client(),
        created_after=created_after,
        created_before=created_before,
        limit=args.limit,
        offset=args.offset,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "payout-status-get",
            "filters": {
                "created_after": created_after,
                "created_before": created_before,
                "limit": args.limit,
                "offset": args.offset,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_finance_account_transactions_query(args: argparse.Namespace) -> int:
    start_time = _normalize_compact_date_for_api(args.start_time, field_name="start_time")
    end_time = _normalize_compact_date_for_api(args.end_time, field_name="end_time")
    result = query_account_transactions(
        _with_client(),
        transaction_type=args.transaction_type,
        sub_transaction_type=args.sub_transaction_type,
        transaction_number=args.transaction_number,
        start_time=start_time,
        end_time=end_time,
        page_num=args.page_num,
        page_size=args.page_size,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "account-transactions-query",
            "filters": {
                "transaction_type": args.transaction_type,
                "sub_transaction_type": args.sub_transaction_type,
                "transaction_number": args.transaction_number,
                "start_time": start_time,
                "end_time": end_time,
                "page_num": args.page_num,
                "page_size": args.page_size,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_finance_logistics_fee_detail(args: argparse.Namespace) -> int:
    bill_start_time = _normalize_bill_date_for_api(
        args.bill_start_time, field_name="bill_start_time", is_end=False
    )
    bill_end_time = _normalize_bill_date_for_api(
        args.bill_end_time, field_name="bill_end_time", is_end=True
    )
    result = query_logistics_fee_detail(
        _with_client(),
        seller_id=args.seller_id,
        request_type=args.request_type,
        trade_order_id=args.trade_order_id,
        trade_order_line_id=args.trade_order_line_id,
        fee_type=args.fee_type,
        biz_flow_type=args.biz_flow_type,
        bill_start_time=bill_start_time,
        bill_end_time=bill_end_time,
        page_no=args.page_no,
        page_size=args.page_size,
        total_records=args.total_records,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "logistics-fee-detail",
            "filters": {
                "seller_id": args.seller_id,
                "request_type": args.request_type,
                "trade_order_id": args.trade_order_id,
                "trade_order_line_id": args.trade_order_line_id,
                "fee_type": args.fee_type,
                "biz_flow_type": args.biz_flow_type,
                "bill_start_time": bill_start_time,
                "bill_end_time": bill_end_time,
                "page_no": args.page_no,
                "page_size": args.page_size,
                "total_records": args.total_records,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_finance_transaction_details_get(args: argparse.Namespace) -> int:
    start_time = _normalize_date_for_api(args.start_time, field_name="start_time")
    end_time = _normalize_date_for_api(args.end_time, field_name="end_time")
    result = get_transaction_details(
        _with_client(),
        trade_order_id=args.trade_order_id,
        trade_order_line_id=args.trade_order_line_id,
        trans_type=args.trans_type,
        start_time=start_time,
        end_time=end_time,
        offset=args.offset,
        limit=args.limit,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "transaction-details-get",
            "filters": {
                "trade_order_id": args.trade_order_id,
                "trade_order_line_id": args.trade_order_line_id,
                "trans_type": args.trans_type,
                "start_time": start_time,
                "end_time": end_time,
                "offset": args.offset,
                "limit": args.limit,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_products_get(args: argparse.Namespace) -> int:
    result = get_products(
        _with_client(),
        filter_expr=args.filter_expr,
        create_before=args.create_before,
        create_after=args.create_after,
        update_before=args.update_before,
        update_after=args.update_after,
        offset=args.offset,
        limit=args.limit,
        options=args.options,
        max_pages=args.max_pages,
    )
    result_dict = result.model_dump()
    return _emit(
        {
            "products": result_dict["products"],
            "total_products": result_dict["total_products"],
            "has_more": result_dict["has_more"],
            "pages_fetched": result_dict["pages_fetched"],
        },
        ok=True,
    )


def _handle_products_item_get(args: argparse.Namespace) -> int:
    result = get_product_item(_with_client(), item_id=args.item_id)
    return _emit(
        {
            "domain": "products",
            "action": "item-get",
            "filters": {
                "item_id": args.item_id,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_returns_refunds_detail_list(args: argparse.Namespace) -> int:
    result = list_return_detail(
        _with_client(),
        created_after=args.created_after,
        created_before=args.created_before,
        offset=args.offset,
        limit=args.limit,
        max_pages=args.max_pages,
        reverse_order_id=args.reverse_order_id,
    )
    return _emit(
        {
            "domain": "returns-refunds",
            "action": "return-detail-list",
            "filters": {
                "created_after": args.created_after,
                "created_before": args.created_before,
                "offset": args.offset,
                "limit": args.limit,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_returns_refunds_history_list(args: argparse.Namespace) -> int:
    result = list_return_history(
        _with_client(),
        created_after=args.created_after,
        created_before=args.created_before,
        offset=args.offset,
        limit=args.limit,
        max_pages=args.max_pages,
        reverse_order_line_id=args.reverse_order_line_id,
    )
    return _emit(
        {
            "domain": "returns-refunds",
            "action": "return-history-list",
            "filters": {
                "created_after": args.created_after,
                "created_before": args.created_before,
                "offset": args.offset,
                "limit": args.limit,
                "max_pages": args.max_pages,
                "reverse_order_line_id":args.reverse_order_line_id,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_returns_refunds_reason_list(args: argparse.Namespace) -> int:
    result = list_return_reasons(
        _with_client(),
        reverse_order_line_id=args.reverse_order_line_id,
    )
    return _emit(
        {
            "domain": "returns-refunds",
            "action": "reason-list",
            "filters": {
                "reverse_order_line_id":args.reverse_order_line_id,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_returns_refunds_get_reverse_orders_for_seller(args: argparse.Namespace) -> int:
    result = get_reverse_orders_for_seller(
        _with_client(),
        created_after=args.created_after,
        created_before=args.created_before,
        offset=args.offset,
        limit=args.limit,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "returns-refunds",
            "action": "get-reverse-orders-for-seller",
            "filters": {
                "created_after": args.created_after,
                "created_before": args.created_before,
                "offset": args.offset,
                "limit": args.limit,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )



def _handle_reviews_seller_history_list(args: argparse.Namespace) -> int:
    result = list_seller_reviews_history(
        _with_client(),
        created_after=args.created_after,
        created_before=args.created_before,
        item_id=args.item_id,
        current=args.current,
        limit=args.limit,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "reviews",
            "action": "seller-history-list",
            "filters": {
                "created_after": args.created_after,
                "created_before": args.created_before,
                "item_id": args.item_id,
                "current": args.current,
                "limit": args.limit,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_reviews_seller_list_v2(args: argparse.Namespace) -> int:
    result = list_seller_reviews_v2(
        _with_client(),
        id_list=args.id_list,
        item_id=args.item_id,
    )
    return _emit(
        {
            "domain": "reviews",
            "action": "seller-list-v2",
            "filters": {
                "item_id": args.item_id,
                "id_list": args.id_list,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_reviews_seller_reply_add(args: argparse.Namespace) -> int:
    result = add_seller_review_reply(
        _with_client(),
        id_list=args.id_list,
        content=args.content,
    )
    return _emit(
        {
            "domain": "reviews",
            "action": "seller-reply-add",
            "filters": {
                "id_list": args.id_list,
                "content": args.content,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_reviews_get_item_reviews(args: argparse.Namespace) -> int:
    """
    Fetches reviews for items from completed orders in the last N days.
    Uses rate limiting to avoid hitting Lazada API frequency limit.
    """
    client = _with_client()
    created_after, created_before = build_default_order_window(args.days)
    sort_desc = args.sort != "asc"
    max_api_calls = getattr(args, "max_api_calls", 10)

    time_module.sleep(random.uniform(5.0, 8.0))

    max_retries = 3
    for attempt in range(max_retries):
        try:
            orders_result = fetch_orders(
                client,
                created_after=created_after,
                created_before=created_before,
                status="delivered",
                limit=100,
                sort_by="created_at",
                sort_direction="DESC" if sort_desc else "ASC",
                max_pages=1,
            )
            break
        except LazadaAPIError as err:
            if err.code == "SellerCallLimit" and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 3 + random.uniform(1.0, 2.0)
                time_module.sleep(wait_time)
                continue
            raise

    all_reviews = []
    processed_item_ids = set()
    request_ids = []
    item_breakdown = []
    api_call_count = 0
    rate_limit_stopped = False

    orders_list = orders_result.orders
    for order in orders_list:
        order_items = order.get("items", []) if isinstance(order, dict) else (order.items or [])
        if not isinstance(order_items, list):
            continue

        for item in order_items:
            item_id = item.get("item_id") if isinstance(item, dict) else getattr(item, 'item_id', None)
            if not item_id or item_id in processed_item_ids:
                continue

            if api_call_count >= max_api_calls:
                rate_limit_stopped = True
                break

            time_module.sleep(random.uniform(0.3, 0.5))
            api_call_count += 1

            try:
                reviews_result = list_seller_reviews_history(
                    client,
                    created_after=created_after,
                    created_before=created_before,
                    item_id=str(item_id),
                )
                item_reviews = reviews_result.reviews
                item_request_ids = reviews_result.request_ids
                item_reviews = sorted(
                    [review for review in item_reviews if isinstance(review, dict)],
                    key=_review_timestamp_ms,
                    reverse=sort_desc,
                )
                item_review_ids = []
                seen_review_ids = set()
                for review in item_reviews:
                    review_id = _review_id(review)
                    if review_id is None:
                        continue
                    if review_id in seen_review_ids:
                        continue
                    seen_review_ids.add(review_id)
                    item_review_ids.append(review_id)

                all_reviews.extend(item_reviews)
                request_ids.extend(item_request_ids)
                item_breakdown.append(
                    {
                        "item_id": str(item_id),
                        "reviews_fetched": len(item_reviews),
                        "review_ids": item_review_ids,
                        "request_ids": item_request_ids,
                    }
                )
            except LazadaAPIError as err:
                item_breakdown.append(
                    {
                        "item_id": str(item_id),
                        "reviews_fetched": 0,
                        "review_ids": [],
                        "request_ids": [],
                        "status": "api_error",
                        "error": str(err),
                        "api_code": err.code,
                        "api_request_id": err.request_id,
                    }
                )
            except Exception as err:
                item_breakdown.append(
                    {
                        "item_id": str(item_id),
                        "reviews_fetched": 0,
                        "review_ids": [],
                        "request_ids": [],
                        "status": "runtime_error",
                        "error": str(err),
                    }
                )
            processed_item_ids.add(item_id)

        if rate_limit_stopped:
            break

    all_reviews = sorted(
        [review for review in all_reviews if isinstance(review, dict)],
        key=_review_timestamp_ms,
        reverse=sort_desc,
    )
    all_review_ids = []
    seen_all_review_ids = set()
    for review in all_reviews:
        review_id = _review_id(review)
        if review_id is None or review_id in seen_all_review_ids:
            continue
        seen_all_review_ids.add(review_id)
        all_review_ids.append(review_id)

    return _emit(
        {
            "domain": "reviews",
            "action": "get-item-reviews",
            "filters": {"days": args.days, "sort": args.sort, "max_api_calls": max_api_calls},
            "request_ids": request_ids,
            "review_ids": all_review_ids,
            "items_processed": len(processed_item_ids),
            "api_calls_made": api_call_count,
            "rate_limit_stopped": rate_limit_stopped,
            "item_breakdown": item_breakdown,
            "total_fetched": len(all_reviews),
            "reviews": all_reviews,
        },
        ok=True,
    )


def _handle_reviews_get_recent_orders(args: argparse.Namespace) -> int:
    """
    Fetches reviews for the most recent N completed orders.
    Uses rate limiting to avoid hitting Lazada API frequency limit.
    """
    client = _with_client()
    created_after, created_before = build_default_order_window(args.days)
    sort_desc = args.sort != "asc"
    max_orders = getattr(args, "max_orders", 10)
    max_api_calls = getattr(args, "max_api_calls", 10)

    time_module.sleep(random.uniform(5.0, 8.0))

    max_retries = 3
    for attempt in range(max_retries):
        try:
            orders_result = fetch_orders(
                client,
                created_after=created_after,
                created_before=created_before,
                status="delivered",
                limit=max_orders,
                sort_by="created_at",
                sort_direction="DESC" if sort_desc else "ASC",
                max_pages=1,
            )
            break
        except LazadaAPIError as err:
            if err.code == "SellerCallLimit" and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 3 + random.uniform(1.0, 2.0)
                time_module.sleep(wait_time)
                continue
            raise

    orders_list = orders_result.orders[:max_orders]

    all_reviews = []
    processed_item_ids = set()
    request_ids = []
    item_breakdown = []
    api_call_count = 0
    rate_limit_stopped = False

    for order in orders_list:
        order_id = order.get("order_id") if isinstance(order, dict) else getattr(order, 'order_id', None)
        order_items = order.get("items", []) if isinstance(order, dict) else (order.items or [])
        if not isinstance(order_items, list):
            continue

        for item in order_items:
            item_id = item.get("item_id") if isinstance(item, dict) else getattr(item, 'item_id', None)
            if not item_id or item_id in processed_item_ids:
                continue

            if api_call_count >= max_api_calls:
                rate_limit_stopped = True
                break

            time_module.sleep(random.uniform(0.3, 0.5))
            api_call_count += 1

            try:
                reviews_result = list_seller_reviews_history(
                    client,
                    created_after=created_after,
                    created_before=created_before,
                    item_id=str(item_id),
                )
                item_reviews = reviews_result.reviews
                item_request_ids = reviews_result.request_ids
                item_reviews = sorted(
                    [review for review in item_reviews if isinstance(review, dict)],
                    key=_review_timestamp_ms,
                    reverse=sort_desc,
                )
                item_review_ids = []
                seen_review_ids = set()
                for review in item_reviews:
                    review_id = _review_id(review)
                    if review_id is None:
                        continue
                    if review_id in seen_review_ids:
                        continue
                    seen_review_ids.add(review_id)
                    item_review_ids.append(review_id)

                all_reviews.extend(item_reviews)
                request_ids.extend(item_request_ids)
                item_breakdown.append(
                    {
                        "order_id": str(order_id),
                        "item_id": str(item_id),
                        "reviews_fetched": len(item_reviews),
                        "review_ids": item_review_ids,
                        "request_ids": item_request_ids,
                    }
                )
            except LazadaAPIError as err:
                item_breakdown.append(
                    {
                        "order_id": str(order_id),
                        "item_id": str(item_id),
                        "reviews_fetched": 0,
                        "review_ids": [],
                        "request_ids": [],
                        "status": "api_error",
                        "error": str(err),
                        "api_code": err.code,
                        "api_request_id": err.request_id,
                    }
                )
            except Exception as err:
                item_breakdown.append(
                    {
                        "order_id": str(order_id),
                        "item_id": str(item_id),
                        "reviews_fetched": 0,
                        "review_ids": [],
                        "request_ids": [],
                        "status": "runtime_error",
                        "error": str(err),
                    }
                )
            processed_item_ids.add(item_id)

        if rate_limit_stopped:
            break

    all_reviews = sorted(
        [review for review in all_reviews if isinstance(review, dict)],
        key=_review_timestamp_ms,
        reverse=sort_desc,
    )
    all_review_ids = []
    seen_all_review_ids = set()
    for review in all_reviews:
        review_id = _review_id(review)
        if review_id is None or review_id in seen_all_review_ids:
            continue
        seen_all_review_ids.add(review_id)
        all_review_ids.append(review_id)

    return _emit(
        {
            "domain": "reviews",
            "action": "get-recent-orders",
            "filters": {
                "days": args.days,
                "max_orders": max_orders,
                "sort": args.sort,
                "max_api_calls": max_api_calls,
            },
            "request_ids": request_ids,
            "review_ids": all_review_ids,
            "orders_processed": len(orders_list),
            "unique_items": len(processed_item_ids),
            "api_calls_made": api_call_count,
            "rate_limit_stopped": rate_limit_stopped,
            "item_breakdown": item_breakdown,
            "total_fetched": len(all_reviews),
            "reviews": all_reviews,
        },
        ok=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _normalize_datetime_filters(args)

    try:
        if args.domain == "orders" and args.action == "get":
            return _handle_orders_get(args)
        if args.domain == "orders" and args.action == "item-get":
            return _handle_orders_item_get(args)
        if args.domain == "orders" and args.action == "items-multiple":
            return _handle_orders_items_multiple(args)
        if args.domain == "orders" and args.action == "cancel-validate":
            return _handle_orders_cancel_validate(args)
        if args.domain == "orders" and args.action == "summary":
            return _handle_orders_summary(args)

        if args.domain == "finance" and args.action == "payout-status-get":
            return _handle_finance_payout_status_get(args)
        if args.domain == "finance" and args.action == "account-transactions-query":
            return _handle_finance_account_transactions_query(args)
        if args.domain == "finance" and args.action == "logistics-fee-detail":
            return _handle_finance_logistics_fee_detail(args)
        if args.domain == "finance" and args.action == "transaction-details-get":
            return _handle_finance_transaction_details_get(args)

        if args.domain == "products" and args.action == "get":
            return _handle_products_get(args)
        if args.domain == "products" and args.action == "item-get":
            return _handle_products_item_get(args)

        if args.domain == "returns-refunds" and args.action == "return-detail-list":
            return _handle_returns_refunds_detail_list(args)
        if args.domain == "returns-refunds" and args.action == "return-history-list":
            return _handle_returns_refunds_history_list(args)
        if args.domain == "returns-refunds" and args.action == "reason-list":
            return _handle_returns_refunds_reason_list(args)
        if args.domain == "returns-refunds" and args.action == "get-reverse-orders-for-seller":
            return _handle_returns_refunds_get_reverse_orders_for_seller(args)

        if args.domain == "reviews" and args.action == "seller-history-list":
            return _handle_reviews_seller_history_list(args)
        if args.domain == "reviews" and args.action == "seller-list-v2":
            return _handle_reviews_seller_list_v2(args)
        if args.domain == "reviews" and args.action == "seller-reply-add":
            return _handle_reviews_seller_reply_add(args)
        if args.domain == "reviews" and args.action == "get-item-reviews":
            return _handle_reviews_get_item_reviews(args)
        if args.domain == "reviews" and args.action == "get-recent-orders":
            return _handle_reviews_get_recent_orders(args)

        return _emit({"error": "Unsupported command"}, ok=False, status="invalid_command")
    except LazadaConfigError as err:
        return _emit({"error": str(err)}, ok=False, status="config_error")
    except LazadaAPIError as err:
        return _emit(
            {
                "error": str(err),
                "api_code": err.code,
                "request_id": err.request_id,
            },
            ok=False,
            status="api_error",
        )
    except Exception as err:
        return _emit({"error": str(err)}, ok=False, status="runtime_error")


if __name__ == "__main__":
    raise SystemExit(main())
