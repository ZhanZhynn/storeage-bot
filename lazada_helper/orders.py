from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any

from .client import LazadaClient


def _format_dt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def build_default_order_window(days: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(days=days)
    return _format_dt(earlier), _format_dt(now)


def get_order_items(client: LazadaClient, **kwargs: Any) -> dict[str, Any]:
    # Delegate to the existing fetch_orders function
    return fetch_orders(client, **kwargs)


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
) -> dict[str, Any]:
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

    return {
        "endpoint": "/orders/get",
        "total_fetched": len(collected_orders),
        "pages_fetched": len(request_ids),
        "next_offset": current_offset if has_more else None,
        "has_more": has_more,
        "request_ids": request_ids,
        "orders": collected_orders,
    }
