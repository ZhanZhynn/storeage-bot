import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any

from .client import (LazadaAPIError, LazadaClient, LazadaConfig,
                     LazadaConfigError)
from .finance import (get_payout_status, get_transaction_details,
                      query_account_transactions, query_logistics_fee_detail)
from .orders import build_default_order_window, fetch_orders, get_order_items
from .products import get_product_item, get_products
from .returns_refunds import (get_reverse_orders_for_seller,
                              list_return_detail, list_return_history,
                              list_return_reasons)
from .reviews import (add_seller_review_reply, list_seller_reviews_history,
                      list_seller_reviews_v2)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic Lazada API helper")
    subparsers = parser.add_subparsers(dest="domain", required=True)

    orders = subparsers.add_parser("orders", help="Order domain operations")
    orders_subparsers = orders.add_subparsers(dest="action", required=True)

    orders_get = orders_subparsers.add_parser("get", help="Fetch orders via /orders/get")
    orders_get.add_argument("--created-after", dest="created_after", default=None)
    orders_get.add_argument("--created-before", dest="created_before", default=None)
    orders_get.add_argument("--update-after", dest="update_after", default=None)
    orders_get.add_argument("--update-before", dest="update_before", default=None)
    orders_get.add_argument("--days", type=int, default=30)
    orders_get.add_argument("--status", default="all")
    orders_get.add_argument("--limit", type=int, default=100)
    orders_get.add_argument("--offset", type=int, default=0)
    orders_get.add_argument("--sort-by", dest="sort_by", default="updated_at")
    orders_get.add_argument("--sort-direction", dest="sort_direction", default="DESC")
    orders_get.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    finance = subparsers.add_parser("finance", help="Finance domain operations")
    finance_subparsers = finance.add_subparsers(dest="action", required=True)

    payout_status_cmd = finance_subparsers.add_parser(
        "payout-status-get", help="Fetch payout status via /finance/payout/status/get"
    )
    payout_status_cmd.add_argument("--created-after", required=True)
    payout_status_cmd.add_argument("--created-before", required=True)
    payout_status_cmd.add_argument("--limit", type=int, default=100)
    payout_status_cmd.add_argument("--offset", type=int, default=0)
    payout_status_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    account_tx_cmd = finance_subparsers.add_parser(
        "account-transactions-query",
        help="Query account transactions via /finance/transaction/accountTransactions/query",
    )
    account_tx_cmd.add_argument("--created-after", required=True)
    account_tx_cmd.add_argument("--created-before", required=True)
    account_tx_cmd.add_argument("--limit", type=int, default=100)
    account_tx_cmd.add_argument("--offset", type=int, default=0)
    account_tx_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    logistics_fee_cmd = finance_subparsers.add_parser(
        "logistics-fee-detail",
        help="Query logistics fee detail via /lbs/slb/queryLogisticsFeeDetail",
    )
    logistics_fee_cmd.add_argument("--created-after", required=True)
    logistics_fee_cmd.add_argument("--created-before", required=True)
    logistics_fee_cmd.add_argument("--limit", type=int, default=100)
    logistics_fee_cmd.add_argument("--offset", type=int, default=0)
    logistics_fee_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    tx_details_cmd = finance_subparsers.add_parser(
        "transaction-details-get",
        help="Get transaction details via /finance/transaction/details/get",
    )
    tx_details_cmd.add_argument("--transaction-number", required=True)

    products = subparsers.add_parser("products", help="Product domain operations")
    products_subparsers = products.add_subparsers(dest="action", required=True)

    products_get_cmd = products_subparsers.add_parser("get", help="Fetch products via /products/get")
    products_get_cmd.add_argument("--filter", dest="filter_expr", default="all")
    products_get_cmd.add_argument("--create-before", dest="create_before", default=None)
    products_get_cmd.add_argument("--create-after", dest="create_after", default=None)
    products_get_cmd.add_argument("--update-before", dest="update_before", default=None)
    products_get_cmd.add_argument("--update-after", dest="update_after", default=None)
    products_get_cmd.add_argument("--offset", type=int, default=0)
    products_get_cmd.add_argument("--limit", type=int, default=100)
    products_get_cmd.add_argument("--options", default="1")
    products_get_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

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
    rr_detail_cmd.add_argument("--created-after", required=True)
    rr_detail_cmd.add_argument("--created-before", required=True)
    rr_detail_cmd.add_argument("--offset", type=int, default=0)
    rr_detail_cmd.add_argument("--limit", type=int, default=100)
    rr_detail_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    rr_history_cmd = rr_subparsers.add_parser(
        "return-history-list", help="List return history via /order/reverse/return/history/list"
    )
    rr_history_cmd.add_argument("--created-after", required=True)
    rr_history_cmd.add_argument("--created-before", required=True)
    rr_history_cmd.add_argument("--offset", type=int, default=0)
    rr_history_cmd.add_argument("--limit", type=int, default=100)
    rr_history_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    _rr_reason_cmd = rr_subparsers.add_parser(  # noqa: F841
        "reason-list", help="List return reasons via /order/reverse/reason/list"
    )

    rr_reverse_orders_cmd = rr_subparsers.add_parser(
        "get-reverse-orders-for-seller",
        help="Fetch reverse orders via /reverse/getreverseordersforseller",
    )
    rr_reverse_orders_cmd.add_argument("--created-after", required=True)
    rr_reverse_orders_cmd.add_argument("--created-before", required=True)
    rr_reverse_orders_cmd.add_argument("--offset", type=int, default=0)
    rr_reverse_orders_cmd.add_argument("--limit", type=int, default=100)
    rr_reverse_orders_cmd.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    reviews = subparsers.add_parser("reviews", help="Product review domain operations")
    reviews_subparsers = reviews.add_subparsers(dest="action", required=True)

    review_history_cmd = reviews_subparsers.add_parser(
        "seller-history-list", help="List seller review history via /review/seller/history/list"
    )
    review_history_cmd.add_argument("--created-after", required=True)
    review_history_cmd.add_argument("--created-before", required=True)
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
            **result,
        },
        ok=True,
    )


def _handle_finance_payout_status_get(args: argparse.Namespace) -> int:
    result = get_payout_status(
        _with_client(),
        created_after=args.created_after,
        created_before=args.created_before,
        limit=args.limit,
        offset=args.offset,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "payout-status-get",
            "filters": {
                "created_after": args.created_after,
                "created_before": args.created_before,
                "limit": args.limit,
                "offset": args.offset,
                "max_pages": args.max_pages,
            },
            **result,
        },
        ok=True,
    )


def _handle_finance_account_transactions_query(args: argparse.Namespace) -> int:
    result = query_account_transactions(
        _with_client(),
        created_after=args.created_after,
        created_before=args.created_before,
        limit=args.limit,
        offset=args.offset,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "account-transactions-query",
            "filters": {
                "created_after": args.created_after,
                "created_before": args.created_before,
                "limit": args.limit,
                "offset": args.offset,
                "max_pages": args.max_pages,
            },
            **result,
        },
        ok=True,
    )


def _handle_finance_logistics_fee_detail(args: argparse.Namespace) -> int:
    result = query_logistics_fee_detail(
        _with_client(),
        created_after=args.created_after,
        created_before=args.created_before,
        limit=args.limit,
        offset=args.offset,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "logistics-fee-detail",
            "filters": {
                "created_after": args.created_after,
                "created_before": args.created_before,
                "limit": args.limit,
                "offset": args.offset,
                "max_pages": args.max_pages,
            },
            **result,
        },
        ok=True,
    )


def _handle_finance_transaction_details_get(args: argparse.Namespace) -> int:
    result = get_transaction_details(
        _with_client(),
        transaction_number=args.transaction_number,
    )
    return _emit(
        {
            "domain": "finance",
            "action": "transaction-details-get",
            "filters": {
                "transaction_number": args.transaction_number,
            },
            **result,
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
    return _emit(
        {
            "domain": "products",
            "action": "get",
            "filters": {
                "filter": args.filter_expr,
                "create_before": args.create_before,
                "create_after": args.create_after,
                "update_before": args.update_before,
                "update_after": args.update_after,
                "offset": args.offset,
                "limit": args.limit,
                "options": args.options,
                "max_pages": args.max_pages,
            },
            **result,
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
            **result,
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
            **result,
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
            },
            **result,
        },
        ok=True,
    )


def _handle_returns_refunds_reason_list(_args: argparse.Namespace) -> int:
    result = list_return_reasons(_with_client())
    return _emit(
        {
            "domain": "returns-refunds",
            "action": "reason-list",
            **result,
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
            **result,
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
            **result,
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
            **result,
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
            **result,
        },
        ok=True,
    )


def _handle_reviews_get_item_reviews(args: argparse.Namespace) -> int:
    """
    Fetches reviews for items from completed orders in the last N days.
    """
    client = _with_client()
    created_after, created_before = build_default_order_window(args.days)
    sort_desc = args.sort != "asc"

    # 1. Fetch completed orders
    orders_result = get_order_items(
        client,
        created_after=created_after,
        created_before=created_before,
        status="delivered",
    )

    all_reviews = []
    processed_item_ids = set()
    request_ids = []
    item_breakdown = []

    # 2. Extract item_id and fetch reviews
    for order in orders_result.get("orders", []):
        order_items = order.get("items", [])
        if not isinstance(order_items, list):
            continue

        for item in order_items:
            item_id = item.get("item_id")
            if not item_id or item_id in processed_item_ids:
                continue

            try:
                reviews_result = list_seller_reviews_history(
                    client,
                    created_after=created_after,
                    created_before=created_before,
                    item_id=str(item_id),
                )
                item_reviews = reviews_result.get("reviews", [])
                item_request_ids = reviews_result.get("request_ids", [])
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
            "filters": {"days": args.days, "sort": args.sort},
            "request_ids": request_ids,
            "review_ids": all_review_ids,
            "items_processed": len(processed_item_ids),
            "item_breakdown": item_breakdown,
            "total_fetched": len(all_reviews),
            "reviews": all_reviews,
        },
        ok=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.domain == "orders" and args.action == "get":
            return _handle_orders_get(args)

        # if args.domain == "finance" and args.action == "payout-status-get":
        #     return _handle_finance_payout_status_get(args)
        # if args.domain == "finance" and args.action == "account-transactions-query":
        #     return _handle_finance_account_transactions_query(args)
        # if args.domain == "finance" and args.action == "logistics-fee-detail":
        #     return _handle_finance_logistics_fee_detail(args)
        # if args.domain == "finance" and args.action == "transaction-details-get":
        #     return _handle_finance_transaction_details_get(args)

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
