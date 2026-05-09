from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .client import ShopeeClient
from .models import (
    OrderActionResponse,
    OrderItemsResponse,
    OrdersResponse,
    OrderSplitResponse,
    PackageDetailResponse,
    PackageListResponse,
)


def _format_dt(dt: datetime) -> int:
    return int(dt.timestamp())


def build_default_order_window(days: int) -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(days=days)
    return _format_dt(earlier), _format_dt(now)


def fetch_orders(
    client: ShopeeClient,
    *,
    time_from: int | None = None,
    time_to: int | None = None,
    time_range_field: str = "create_time",
    page_size: int = 50,
    cursor: str | None = None,
    order_status: str | None = None,
    response_optional_fields: str | None = None,
    max_pages: int = 10,
) -> OrdersResponse:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")
    if time_range_field not in ("create_time", "update_time"):
        raise ValueError("time_range_field must be create_time or update_time")

    collected_orders: list[dict[str, Any]] = []
    request_ids: list[str] = []
    next_cursor = cursor or ""
    has_more = False

    for _ in range(max_pages):
        params: dict[str, Any] = {
            "time_range_field": time_range_field,
            "page_size": page_size,
        }
        if time_from is not None:
            params["time_from"] = time_from
        if time_to is not None:
            params["time_to"] = time_to
        if order_status:
            params["order_status"] = order_status
        if response_optional_fields:
            params["response_optional_fields"] = response_optional_fields
        if next_cursor:
            params["cursor"] = next_cursor

        payload = client.get("/api/v2/order/get_order_list", params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        response = payload.get("response") or {}
        orders = response.get("order_list") or []
        if not isinstance(orders, list):
            orders = []
        collected_orders.extend([item for item in orders if isinstance(item, dict)])

        has_more = bool(response.get("more"))
        next_cursor = response.get("next_cursor") or ""
        if not has_more:
            break

    return OrdersResponse(
        endpoint="/api/v2/order/get_order_list",
        request_ids=request_ids,
        total_fetched=len(collected_orders),
        pages_fetched=len(request_ids),
        has_more=has_more,
        next_cursor=next_cursor or None,
        orders=collected_orders,
    )


def get_order_items(
    client: ShopeeClient,
    *,
    order_sn_list: list[str],
) -> OrderItemsResponse:
    normalized = [str(sn).strip() for sn in order_sn_list if str(sn).strip()]
    if not normalized:
        raise ValueError("order_sn_list must not be empty")

    payload = client.get(
        "/api/v2/order/get_order_detail",
        {
            "order_sn_list": ",".join(normalized),
            "response_optional_fields": "item_list",
        },
    )
    request_id = payload.get("request_id")
    response = payload.get("response") or {}
    orders = response.get("order_list") or []
    items: list[dict[str, Any]] = []
    for order in orders:
        if not isinstance(order, dict):
            continue
        item_list = order.get("item_list")
        if isinstance(item_list, list):
            items.extend([item for item in item_list if isinstance(item, dict)])

    return OrderItemsResponse(
        endpoint="/api/v2/order/get_order_detail",
        request_ids=[str(request_id)] if request_id else [],
        total_fetched=len(items),
        order_ids=normalized,
        items=items,
    )


def cancel_order(
    client: ShopeeClient,
    *,
    order_sn: str,
    cancel_reason: str,
    item_list: list[dict[str, Any]] | None = None,
) -> OrderActionResponse:
    if not order_sn:
        raise ValueError("order_sn must not be empty")
    if not cancel_reason:
        raise ValueError("cancel_reason must not be empty")
    payload: dict[str, Any] = {
        "order_sn": order_sn,
        "cancel_reason": cancel_reason,
    }
    if item_list:
        payload["item_list"] = item_list

    response = client.post("/api/v2/order/cancel_order", payload)
    request_id = response.get("request_id")
    body = response.get("response") or {}
    if not isinstance(body, dict):
        body = {}
    return OrderActionResponse(
        endpoint="/api/v2/order/cancel_order",
        request_ids=[str(request_id)] if request_id else [],
        response=body,
    )


def handle_buyer_cancellation(
    client: ShopeeClient,
    *,
    order_sn: str,
    operation: str,
) -> OrderActionResponse:
    if not order_sn:
        raise ValueError("order_sn must not be empty")
    if not operation:
        raise ValueError("operation must not be empty")

    response = client.post(
        "/api/v2/order/handle_buyer_cancellation",
        {"order_sn": order_sn, "operation": operation},
    )
    request_id = response.get("request_id")
    body = response.get("response") or {}
    if not isinstance(body, dict):
        body = {}
    return OrderActionResponse(
        endpoint="/api/v2/order/handle_buyer_cancellation",
        request_ids=[str(request_id)] if request_id else [],
        response=body,
    )


def split_order(
    client: ShopeeClient,
    *,
    order_sn: str,
    package_list: list[dict[str, Any]],
) -> OrderSplitResponse:
    if not order_sn:
        raise ValueError("order_sn must not be empty")
    if not package_list:
        raise ValueError("package_list must not be empty")

    response = client.post(
        "/api/v2/order/split_order",
        {"order_sn": order_sn, "package_list": package_list},
    )
    request_id = response.get("request_id")
    body = response.get("response") or {}
    if not isinstance(body, dict):
        body = {}
    packages = body.get("package_list") or []
    if not isinstance(packages, list):
        packages = []
    return OrderSplitResponse(
        endpoint="/api/v2/order/split_order",
        request_ids=[str(request_id)] if request_id else [],
        order_sn=body.get("order_sn") if isinstance(body.get("order_sn"), str) else None,
        package_list=[item for item in packages if isinstance(item, dict)],
    )


def unsplit_order(
    client: ShopeeClient,
    *,
    order_sn: str,
) -> OrderActionResponse:
    if not order_sn:
        raise ValueError("order_sn must not be empty")

    response = client.post("/api/v2/order/unsplit_order", {"order_sn": order_sn})
    request_id = response.get("request_id")
    body = response.get("response") or {}
    if not isinstance(body, dict):
        body = {}
    return OrderActionResponse(
        endpoint="/api/v2/order/unsplit_order",
        request_ids=[str(request_id)] if request_id else [],
        response=body,
    )


def search_package_list(
    client: ShopeeClient,
    *,
    page_size: int = 50,
    cursor: str | None = None,
    filter_payload: dict[str, Any] | None = None,
    sort_payload: dict[str, Any] | None = None,
    max_pages: int = 10,
) -> PackageListResponse:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    collected: list[dict[str, Any]] = []
    request_ids: list[str] = []
    next_cursor = cursor or ""
    has_more = False
    total_count: int | None = None

    for _ in range(max_pages):
        payload: dict[str, Any] = {
            "pagination": {
                "page_size": page_size,
                "cursor": next_cursor,
            }
        }
        if filter_payload:
            payload["filter"] = filter_payload
        if sort_payload:
            payload["sort"] = sort_payload

        response = client.post("/api/v2/order/search_package_list", payload)
        request_id = response.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        body = response.get("response") or {}
        if not isinstance(body, dict):
            body = {}
        packages = body.get("packages_list") or []
        if not isinstance(packages, list):
            packages = []
        collected.extend([item for item in packages if isinstance(item, dict)])

        pagination = body.get("pagination") or {}
        if isinstance(pagination, dict):
            if total_count is None and isinstance(pagination.get("total_count"), int):
                total_count = pagination.get("total_count")
            next_cursor = pagination.get("next_cursor") or ""
            has_more = bool(pagination.get("more"))
        else:
            next_cursor = ""
            has_more = False

        if not has_more:
            break

    return PackageListResponse(
        endpoint="/api/v2/order/search_package_list",
        request_ids=request_ids,
        total_fetched=len(collected),
        pages_fetched=len(request_ids),
        has_more=has_more,
        next_cursor=next_cursor or None,
        total_count=total_count,
        packages=collected,
    )


def split_order_max(
    client: ShopeeClient,
    *,
    order_sn: str,
    max_packages: int,
    item_list: list[dict[str, Any]],
) -> OrderSplitResponse:
    if not order_sn:
        raise ValueError("order_sn must not be empty")
    if max_packages <= 0:
        raise ValueError("max_packages must be > 0")
    if not item_list:
        raise ValueError("item_list must not be empty")

    total_items = len(item_list)
    items_per_package = total_items // max_packages
    remainder = total_items % max_packages

    package_list: list[dict[str, Any]] = []
    idx = 0
    for pkg_idx in range(max_packages):
        count = items_per_package + (1 if pkg_idx < remainder else 0)
        package_items = item_list[idx : idx + count]
        idx += count
        package_list.append({"item_list": package_items})
        if idx >= total_items:
            break

    return split_order(client, order_sn=order_sn, package_list=package_list)


def get_package_detail(
    client: ShopeeClient,
    *,
    package_number_list: list[str],
) -> PackageDetailResponse:
    normalized = [str(value).strip() for value in package_number_list if str(value).strip()]
    if not normalized:
        raise ValueError("package_number_list must not be empty")

    response = client.get(
        "/api/v2/order/get_package_detail",
        {"package_number_list": ",".join(normalized)},
    )
    request_id = response.get("request_id")
    body = response.get("response") or {}
    if not isinstance(body, dict):
        body = {}
    packages = body.get("package_list") or []
    if not isinstance(packages, list):
        packages = []
    return PackageDetailResponse(
        endpoint="/api/v2/order/get_package_detail",
        request_ids=[str(request_id)] if request_id else [],
        packages=[item for item in packages if isinstance(item, dict)],
    )
