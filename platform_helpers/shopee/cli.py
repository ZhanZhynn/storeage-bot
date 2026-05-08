import argparse
import json
import sys
from typing import Any

from .client import ShopeeAPIError, ShopeeClient, ShopeeConfig, ShopeeConfigError
from .orders import build_default_order_window, fetch_orders, get_order_items
from .products import get_products
from .returns_refunds import get_return_list


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic Shopee API helper")
    subparsers = parser.add_subparsers(dest="domain", required=True)

    orders = subparsers.add_parser("orders", help="Order domain operations")
    orders_subparsers = orders.add_subparsers(dest="action", required=True)

    orders_get = orders_subparsers.add_parser("get", help="Fetch orders via /api/v2/order/get_order_list")
    orders_get.add_argument("--days", type=int, default=7)
    orders_get.add_argument("--time-from", dest="time_from", type=int, default=None)
    orders_get.add_argument("--time-to", dest="time_to", type=int, default=None)
    orders_get.add_argument(
        "--time-range-field",
        dest="time_range_field",
        choices=("create_time", "update_time"),
        default="create_time",
    )
    orders_get.add_argument("--page-size", dest="page_size", type=int, default=50)
    orders_get.add_argument("--cursor", default=None)
    orders_get.add_argument("--order-status", dest="order_status", default=None)
    orders_get.add_argument("--response-optional-fields", dest="response_optional_fields", default=None)
    orders_get.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    orders_items = orders_subparsers.add_parser(
        "items", help="Fetch order items via /api/v2/order/get_order_detail"
    )
    orders_items.add_argument("--order-sn-list", dest="order_sn_list", required=True)

    products = subparsers.add_parser("products", help="Product domain operations")
    products_subparsers = products.add_subparsers(dest="action", required=True)

    products_get = products_subparsers.add_parser("get", help="Fetch items via /api/v2/product/get_item_list")
    products_get.add_argument("--page-size", dest="page_size", type=int, default=50)
    products_get.add_argument("--offset", type=int, default=0)
    products_get.add_argument("--item-status", dest="item_status", default=None)
    products_get.add_argument("--update-time-from", dest="update_time_from", type=int, default=None)
    products_get.add_argument("--update-time-to", dest="update_time_to", type=int, default=None)
    products_get.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    returns_refunds = subparsers.add_parser(
        "returns-refunds", help="Returns/refunds domain operations"
    )
    rr_subparsers = returns_refunds.add_subparsers(dest="action", required=True)

    rr_list = rr_subparsers.add_parser("list", help="Fetch returns via /api/v2/returns/get_return_list")
    rr_list.add_argument("--page-size", dest="page_size", type=int, default=50)
    rr_list.add_argument("--cursor", default=None)
    rr_list.add_argument("--create-time-from", dest="create_time_from", type=int, default=None)
    rr_list.add_argument("--create-time-to", dest="create_time_to", type=int, default=None)
    rr_list.add_argument("--update-time-from", dest="update_time_from", type=int, default=None)
    rr_list.add_argument("--update-time-to", dest="update_time_to", type=int, default=None)
    rr_list.add_argument("--status", default=None)
    rr_list.add_argument("--max-pages", dest="max_pages", type=int, default=10)

    auth = subparsers.add_parser("auth", help="Authorization helpers")
    auth_subparsers = auth.add_subparsers(dest="action", required=True)

    auth_url = auth_subparsers.add_parser("url", help="Build authorization URL")
    auth_url.add_argument("--redirect", required=True)

    token_get = auth_subparsers.add_parser("token-get", help="Exchange code for tokens")
    token_get.add_argument("--code", required=True)
    token_get.add_argument("--shop-id", dest="shop_id", default=None)
    token_get.add_argument("--main-account-id", dest="main_account_id", default=None)

    token_refresh = auth_subparsers.add_parser("token-refresh", help="Refresh access token")
    token_refresh.add_argument("--refresh-token", dest="refresh_token", required=True)
    token_refresh.add_argument("--shop-id", dest="shop_id", default=None)
    token_refresh.add_argument("--merchant-id", dest="merchant_id", default=None)

    return parser


def _emit(payload: dict[str, Any], ok: bool, status: str = "ok") -> int:
    body = {
        "ok": ok,
        "status": status,
        **payload,
    }
    sys.stdout.write(json.dumps(body, ensure_ascii=True) + "\n")
    return 0 if ok else 1


def _with_client() -> ShopeeClient:
    return ShopeeClient(ShopeeConfig.from_env())


def _handle_orders_get(args: argparse.Namespace) -> int:
    time_from = args.time_from
    time_to = args.time_to
    if time_from is None or time_to is None:
        time_from, time_to = build_default_order_window(args.days)

    result = fetch_orders(
        _with_client(),
        time_from=time_from,
        time_to=time_to,
        time_range_field=args.time_range_field,
        page_size=args.page_size,
        cursor=args.cursor,
        order_status=args.order_status,
        response_optional_fields=args.response_optional_fields,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "orders",
            "action": "get",
            "filters": {
                "time_from": time_from,
                "time_to": time_to,
                "time_range_field": args.time_range_field,
                "page_size": args.page_size,
                "cursor": args.cursor,
                "order_status": args.order_status,
                "response_optional_fields": args.response_optional_fields,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_orders_items(args: argparse.Namespace) -> int:
    order_sn_list = [sn.strip() for sn in args.order_sn_list.split(",") if sn.strip()]
    result = get_order_items(_with_client(), order_sn_list=order_sn_list)
    return _emit(
        {
            "domain": "orders",
            "action": "items",
            "order_sn_list": order_sn_list,
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_products_get(args: argparse.Namespace) -> int:
    result = get_products(
        _with_client(),
        page_size=args.page_size,
        offset=args.offset,
        item_status=args.item_status,
        update_time_from=args.update_time_from,
        update_time_to=args.update_time_to,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "products",
            "action": "get",
            "filters": {
                "page_size": args.page_size,
                "offset": args.offset,
                "item_status": args.item_status,
                "update_time_from": args.update_time_from,
                "update_time_to": args.update_time_to,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_returns_list(args: argparse.Namespace) -> int:
    result = get_return_list(
        _with_client(),
        page_size=args.page_size,
        cursor=args.cursor,
        create_time_from=args.create_time_from,
        create_time_to=args.create_time_to,
        update_time_from=args.update_time_from,
        update_time_to=args.update_time_to,
        status=args.status,
        max_pages=args.max_pages,
    )
    return _emit(
        {
            "domain": "returns-refunds",
            "action": "list",
            "filters": {
                "page_size": args.page_size,
                "cursor": args.cursor,
                "create_time_from": args.create_time_from,
                "create_time_to": args.create_time_to,
                "update_time_from": args.update_time_from,
                "update_time_to": args.update_time_to,
                "status": args.status,
                "max_pages": args.max_pages,
            },
            **result.model_dump(),
        },
        ok=True,
    )


def _handle_auth_url(args: argparse.Namespace) -> int:
    url = _with_client().build_auth_url(args.redirect)
    return _emit({"auth_url": url}, ok=True)


def _handle_token_get(args: argparse.Namespace) -> int:
    result = _with_client().get_access_token(
        args.code,
        shop_id=args.shop_id,
        main_account_id=args.main_account_id,
    )
    return _emit({"response": result}, ok=True)


def _handle_token_refresh(args: argparse.Namespace) -> int:
    result = _with_client().refresh_access_token(
        args.refresh_token,
        shop_id=args.shop_id,
        merchant_id=args.merchant_id,
    )
    return _emit({"response": result}, ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.domain == "orders" and args.action == "get":
            return _handle_orders_get(args)
        if args.domain == "orders" and args.action == "items":
            return _handle_orders_items(args)
        if args.domain == "products" and args.action == "get":
            return _handle_products_get(args)
        if args.domain == "returns-refunds" and args.action == "list":
            return _handle_returns_list(args)
        if args.domain == "auth" and args.action == "url":
            return _handle_auth_url(args)
        if args.domain == "auth" and args.action == "token-get":
            return _handle_token_get(args)
        if args.domain == "auth" and args.action == "token-refresh":
            return _handle_token_refresh(args)
        return _emit({"error": "Unsupported command"}, ok=False, status="invalid_command")
    except ShopeeConfigError as err:
        return _emit({"error": str(err)}, ok=False, status="config_error")
    except ShopeeAPIError as err:
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
