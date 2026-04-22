from typing import Any

from .client import LazadaClient


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
) -> dict[str, Any]:
    result = _paginate(
        client,
        endpoint="/order/reverse/return/detail/list",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
        },
        collection_keys=("return_details", "details", "records", "items"),
        offset=offset,
        limit=limit,
        max_pages=max_pages,
    )
    result["return_details"] = result.pop("items")
    return result


def list_return_history(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    offset: int = 0,
    limit: int = 100,
    max_pages: int = 10,
) -> dict[str, Any]:
    result = _paginate(
        client,
        endpoint="/order/reverse/return/history/list",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
        },
        collection_keys=("return_history", "history", "records", "items"),
        offset=offset,
        limit=limit,
        max_pages=max_pages,
    )
    result["return_history"] = result.pop("items")
    return result


def list_return_reasons(client: LazadaClient) -> dict[str, Any]:
    payload = client.get("/order/reverse/reason/list", {})
    request_id = payload.get("request_id")
    data = payload.get("data") or {}

    reasons = data.get("reasons")
    if not isinstance(reasons, list):
        reasons = data.get("items")
    if not isinstance(reasons, list):
        reasons = []

    return {
        "endpoint": "/order/reverse/reason/list",
        "request_ids": [str(request_id)] if request_id else [],
        "total_fetched": len(reasons),
        "reasons": reasons,
    }


def get_reverse_orders_for_seller(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    offset: int = 0,
    limit: int = 100,
    max_pages: int = 10,
) -> dict[str, Any]:
    result = _paginate(
        client,
        endpoint="/reverse/getreverseordersforseller",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
        },
        collection_keys=("reverse_orders", "orders", "records", "items"),
        offset=offset,
        limit=limit,
        max_pages=max_pages,
    )
    result["reverse_orders"] = result.pop("items")
    return result
