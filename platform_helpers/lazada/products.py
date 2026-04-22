from typing import Any

from .client import LazadaClient


def get_products(
    client: LazadaClient,
    *,
    filter_expr: str = "all",
    create_before: str | None = None,
    create_after: str | None = None,
    update_before: str | None = None,
    update_after: str | None = None,
    offset: int = 0,
    limit: int = 50,
    options: str = "1",
    max_pages: int = 10,
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
        params: dict[str, Any] = {
            "filter": filter_expr,
            "offset": current_offset,
            "limit": limit,
            "options": options,
        }
        if create_before:
            params["create_before"] = create_before
        if create_after:
            params["create_after"] = create_after
        if update_before:
            params["update_before"] = update_before
        if update_after:
            params["update_after"] = update_after

        payload = client.get("/products/get", params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        data = payload.get("data") or {}
        page_items = data.get("products")
        if not isinstance(page_items, list):
            page_items = data.get("items")
        if not isinstance(page_items, list):
            page_items = []

        items.extend(page_items)

        if len(page_items) < limit:
            has_more = False
            break

        total_products = data.get("total_products")
        current_offset += limit
        if isinstance(total_products, int) and current_offset >= total_products:
            has_more = False
            break

        has_more = True

    return {
        "endpoint": "/products/get",
        "total_fetched": len(items),
        "pages_fetched": len(request_ids),
        "next_offset": current_offset if has_more else None,
        "has_more": has_more,
        "request_ids": request_ids,
        "products": items,
    }


def get_product_item(client: LazadaClient, *, item_id: str) -> dict[str, Any]:
    payload = client.get("/product/item/get", {"item_id": item_id})
    request_id = payload.get("request_id")
    data = payload.get("data") or {}

    item = data.get("item")
    if item is None:
        item = data

    return {
        "endpoint": "/product/item/get",
        "request_ids": [str(request_id)] if request_id else [],
        "item": item,
    }
