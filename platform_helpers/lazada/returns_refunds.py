from datetime import datetime, timezone
from typing import Any

from .client import LazadaClient
from .models import (ReasonListResponse, ReturnDetailListResponse,
                     ReturnHistoryListResponse, ReverseOrdersResponse)


def _paginate(
    client: LazadaClient,
    *,
    endpoint: str,
    base_params: dict[str, Any],
    collection_keys: tuple[str, ...],
    offset: int,
    limit: int,
    max_pages: int,
) -> dict[str, Any]:
    if limit <= 0:
        raise ValueError("limit must be > 0")
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    items: list[dict[str, Any]] = []
    request_ids: list[str] = []
    current_offset = offset
    has_more = False

    for _ in range(max_pages):
        params = dict(base_params)
        params["offset"] = current_offset
        params["limit"] = limit

        payload = client.get(endpoint, params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        data = payload.get("data") or {}
        page_items: list[dict[str, Any]] = []
        for key in collection_keys:
            value = data.get(key)
            if isinstance(value, list):
                page_items = value
                break

        items.extend(page_items)

        if len(page_items) < limit:
            has_more = False
            break

        count_total = data.get("countTotal")
        current_offset += limit
        if isinstance(count_total, int) and current_offset >= count_total:
            has_more = False
            break

        has_more = True

    return {
        "endpoint": endpoint,
        "total_fetched": len(items),
        "pages_fetched": len(request_ids),
        "next_offset": current_offset if has_more else None,
        "has_more": has_more,
        "request_ids": request_ids,
        "items": items,
    }


def list_return_detail(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    offset: int = 0,
    limit: int = 100,
    max_pages: int = 10,
    reverse_order_id: int,
) -> ReturnDetailListResponse:
    internal_result = _paginate(
        client,
        endpoint="/order/reverse/return/detail/list",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
            "reverse_order_id": reverse_order_id,
        },
        collection_keys=("reverse_order_id", "reverseOrderLineDTOList"),
        offset=offset,
        limit=limit,
        max_pages=max_pages,
    )

    return ReturnDetailListResponse(
        endpoint="/order/reverse/return/detail/list",
        request_ids=internal_result.get("request_ids", []),
        total_returns=internal_result.get("total_fetched", 0),
        pages_fetched=internal_result.get("pages_fetched", 0),
        next_offset=internal_result.get("next_offset"),
        has_more=internal_result.get("has_more", False),
        returns=internal_result.get("items", []),  # type: ignore[arg-type]
    )


def list_return_history(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    offset: int = 0,
    limit: int = 100,
    max_pages: int = 10,
    reverse_order_line_id: int,
) -> ReturnHistoryListResponse:
    internal_result = _paginate(
        client,
        endpoint="/order/reverse/return/history/list",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
            "reverse_order_line_id": reverse_order_line_id,
        },
        collection_keys=("page_info", "list"),
        offset=offset,
        limit=limit,
        max_pages=max_pages,
    )

    return ReturnHistoryListResponse(
        endpoint="/order/reverse/return/history/list",
        request_ids=internal_result.get("request_ids", []),
        total_returns=internal_result.get("total_fetched", 0),
        pages_fetched=internal_result.get("pages_fetched", 0),
        next_offset=internal_result.get("next_offset"),
        has_more=internal_result.get("has_more", False),
        returns=internal_result.get("items", []),  # type: ignore[arg-type]
    )


def list_return_reasons(
    client: LazadaClient,
    reverse_order_line_id: int,
    offset: int = 0,
    limit: int = 100,
    max_pages: int = 1,
) -> ReasonListResponse:
    # payload = client.get("/order/reverse/reason/list", {})
    internal_result = _paginate(
        client,
        endpoint="/order/reverse/return/history/list",
        base_params={
            "reverse_order_line_id": reverse_order_line_id,
        },
        collection_keys=("page_info", "list"),
        offset=offset,
        limit=limit,
        max_pages=max_pages,
    )
    return ReasonListResponse(
        endpoint="/order/reverse/reason/list",
        request_ids=internal_result.get("request_ids", []),
        reasons=internal_result.get("items"),  # type: ignore[arg-type]
    )


def _to_epoch_millis(value: str) -> int:
    text = str(value).strip()
    if text.isdigit():
        parsed = int(text)
        return parsed * 1000 if len(text) <= 10 else parsed

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def get_reverse_orders_for_seller(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    offset: int = 0,
    limit: int = 100,
    max_pages: int = 100,
) -> ReverseOrdersResponse:
    start_time = _to_epoch_millis(created_after)
    end_time = _to_epoch_millis(created_before)

    page_size = limit
    current_page = 0
    reverse_orders: list[dict[str, Any]] = []
    request_ids: list[str] = []
    total = 0

    for current_page in range(max_pages):
        params = {
            "page_size": page_size,
            "page_no": current_page,
            "TradeOrderLineCreatedTimeRangeStart": start_time,
            "TradeOrderLineCreatedTimeRangeEnd": end_time,
        }

        payload = client.get("/reverse/getreverseordersforseller", params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        data = payload.get("result") or {}
        result = data.get("result", {})
        if not result:
            result = data

        items = result.get("items", [])
        if not items:
            continue

        for item in items:
            reverse_order_id = item.get("reverse_order_id")
            trade_order_id = item.get("trade_order_id")
            request_type = item.get("request_type")
            is_rtm = item.get("is_rtm")
            shipping_type = item.get("shipping_type")
            reverse_order_lines = item.get("reverse_order_lines", [])

            for line in reverse_order_lines:
                reverse_orders.append({
                    "reverse_order_id": reverse_order_id,
                    "trade_order_id": trade_order_id,
                    "request_type": request_type,
                    "is_rtm": is_rtm,
                    "shipping_type": shipping_type,
                    **line,
                })

        total_str = result.get("total", "0")
        try:
            total = int(total_str)
        except (ValueError, TypeError):
            total = len(items)

        if len(items) < page_size:
            break

    return ReverseOrdersResponse(
        endpoint="/reverse/getreverseordersforseller",
        request_ids=request_ids,
        total_returns=total,
        pages_fetched=len(request_ids),
        next_offset=None,
        has_more=False,
        orders=reverse_orders,
    )
