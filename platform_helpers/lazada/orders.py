import json
from datetime import datetime, timedelta, timezone
from typing import Any

from .client import LazadaClient
from .models import (CancelValidationResponse, OrderItemsResponse,
                     OrderResponse, OrdersResponse)


def _format_dt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def build_default_order_window(days: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    if days == 0:
        earlier = now.replace(day=now.day-1,hour=16, second=0, minute=0, microsecond=0) #2026-04-25 16:00 (UTC) = 2026-04-26 0000 (GMT+8)
    else:
        earlier = now - timedelta(days=days)
    return _format_dt(earlier), _format_dt(now)


def get_order_items(client: LazadaClient, **kwargs: Any) -> OrdersResponse:
    return fetch_orders(client, **kwargs)  # type: ignore[return-value]


def get_order(client: LazadaClient, *, order_id: str) -> OrderResponse:
    payload = client.get("/order/get", {"order_id": order_id})
    request_id = payload.get("request_id")
    data = payload.get("data")

    order: dict[str, Any] = {}
    if isinstance(data, dict):
        order = data

    return OrderResponse(
        endpoint="/order/get",
        request_ids=[str(request_id)] if request_id else [],
        order=order,
    )


def get_order_items_by_order_id(client: LazadaClient, *, order_id: str) -> OrderItemsResponse:
    payload = client.get("/order/items/get", {"order_id": order_id})
    request_id = payload.get("request_id")
    data = payload.get("data")

    items: list[dict[str, Any]] = []
    if isinstance(data, list):
        items = [item for item in data if isinstance(item, dict)]

    return OrderItemsResponse(
        endpoint="/order/items/get",
        request_ids=[str(request_id)] if request_id else [],
        order_id=str(order_id),
        total_fetched=len(items),
        order_items=items,  # type: ignore[arg-type]
    )


def get_multiple_order_items(
    client: LazadaClient,
    *,
    order_ids: list[str] | list[int],
) -> OrderItemsResponse:
    if not order_ids:
        raise ValueError("order_ids must not be empty")

    normalized_order_ids = [str(order_id).strip() for order_id in order_ids if str(order_id).strip()]
    if not normalized_order_ids:
        raise ValueError("order_ids must contain at least one valid order id")

    payload = client.get("/orders/items/get", {"order_ids": json.dumps(normalized_order_ids)})
    request_id = payload.get("request_id")
    data = payload.get("data")

    orders: list[dict[str, Any]] = []
    if isinstance(data, list):
        orders = [item for item in data if isinstance(item, dict)]

    total_items = 0
    for order in orders:
        maybe_items = order.get("order_items")
        if isinstance(maybe_items, list):
            total_items += len([item for item in maybe_items if isinstance(item, dict)])

    return OrderItemsResponse(
        endpoint="/orders/items/get",
        request_ids=[str(request_id)] if request_id else [],
        order_id=str(normalized_order_ids[0]) if normalized_order_ids else "",
        total_fetched=total_items,
        order_items=orders,  # type: ignore[arg-type]
    )


def validate_order_cancel(
    client: LazadaClient,
    *,
    order_id: str,
    order_item_id_list: list[str] | list[int] | None = None,
) -> CancelValidationResponse:
    params: dict[str, Any] = {"order_id": order_id}
    normalized_item_ids: list[str] = []
    if order_item_id_list is not None:
        normalized_item_ids = [
            str(order_item_id).strip()
            for order_item_id in order_item_id_list
            if str(order_item_id).strip()
        ]
    params["order_item_id_list"] = json.dumps(normalized_item_ids)

    payload = client.get("/order/reverse/cancel/validate", params)
    request_id = payload.get("request_id")
    data = payload.get("data")

    validation: dict[str, Any] = {}
    if isinstance(data, dict):
        validation = data

    return CancelValidationResponse(
        endpoint="/order/reverse/cancel/validate",
        request_ids=[str(request_id)] if request_id else [],
        order_id=str(order_id),
        order_item_id_list=normalized_item_ids,
        validation=validation,
    )


def fetch_orders(
    client: LazadaClient,
    *,
    created_after: str | None = None,
    created_before: str | None = None,
    update_after: str | None = None,
    update_before: str | None = None,
    status: str = "all",
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "updated_at",
    sort_direction: str = "DESC",
    max_pages: int = 10,
) -> OrdersResponse:
    if limit <= 0:
        raise ValueError("limit must be > 0")
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    collected_orders: list[dict[str, Any]] = []
    request_ids: list[str] = []
    current_offset = offset
    has_more = False

    for _ in range(max_pages):
        params: dict[str, Any] = {
            "status": status,
            "limit": limit,
            "offset": current_offset,
            "sort_by": sort_by,
            "sort_direction": sort_direction,
        }
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
        if update_after:
            params["update_after"] = update_after
        if update_before:
            params["update_before"] = update_before

        payload = client.get("/orders/get", params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        data = payload.get("data") or {}
        page_orders = data.get("orders") or []
        if not isinstance(page_orders, list):
            page_orders = []

        collected_orders.extend(page_orders)

        if len(page_orders) < limit:
            has_more = False
            break

        count_total = data.get("countTotal")
        current_offset += limit
        if isinstance(count_total, int) and current_offset >= count_total:
            has_more = False
            break

        has_more = True

    return OrdersResponse(
        endpoint="/orders/get",
        total_fetched=len(collected_orders),
        pages_fetched=len(request_ids),
        next_offset=current_offset if has_more else None,
        has_more=has_more,
        request_ids=request_ids,
        orders=collected_orders,  # type: ignore[arg-type]
    )
