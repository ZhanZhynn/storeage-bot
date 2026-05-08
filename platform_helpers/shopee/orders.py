from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .client import ShopeeClient
from .models import OrderItemsResponse, OrdersResponse


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
