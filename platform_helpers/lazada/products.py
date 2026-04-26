from typing import Any

from .client import LazadaClient
from .models import ProductItemResponse, ProductsResponse


def _normalize_product(product: dict[str, Any]) -> dict[str, Any]:
    skus = product.get("skus", [])
    normalized_skus = []
    for sku in skus:
        normalized_skus.append({
            "SellerSku": sku.get("SellerSku"),
            "ShopSku": sku.get("ShopSku"),
            "price": sku.get("price"),
            "specialPrice": sku.get("special_price"),
            "quantity": sku.get("quantity"),
            "Status": sku.get("Status"),
        })

    attrs = product.get("attributes") or {}
    filtered_attrs = {
        "name": attrs.get("name"),
        "brand": attrs.get("brand"),
        "model": attrs.get("model"),
    }

    return {
        "item_id": product.get("item_id"),
        "attributes": filtered_attrs,
        "status": product.get("status"),
        "skus": normalized_skus,
    }


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
    max_pages: int | None = None,
) -> ProductsResponse:
    if limit <= 0:
        raise ValueError("limit must be > 0")
    if offset < 0:
        raise ValueError("offset must be >= 0")

    items: list[dict[str, Any]] = []
    request_ids: list[str] = []
    current_offset = offset
    has_more = False
    total_products: int | None = None

    while True:
        if max_pages is not None and len(request_ids) >= max_pages:
            break

        params: dict[str, Any] = {
            "filter": filter_expr,
            "offset": current_offset,
            "limit": str(limit),
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

        if total_products is None:
            total_products = data.get("total_products")
            if isinstance(total_products, int):
                has_more = True
            else:
                has_more = False

        if len(page_items) < limit:
            has_more = False
            break

        current_offset += limit
        if isinstance(total_products, int) and current_offset >= total_products:
            has_more = False
            break

    normalized_products = [_normalize_product(p) for p in items]

    return ProductsResponse(
        endpoint="/products/get",
        total_products=len(normalized_products),
        pages_fetched=len(request_ids),
        next_offset=current_offset if has_more else None,
        has_more=has_more,
        request_ids=request_ids,
        products=normalized_products,  # type: ignore[arg-type]
    )


def get_product_item(client: LazadaClient, *, item_id: str) -> ProductItemResponse:
    payload = client.get("/product/item/get", {"item_id": item_id})
    request_id = payload.get("request_id")
    data = payload.get("data") or {}

    item = data.get("item")
    if item is None:
        item = data

    return ProductItemResponse(
        endpoint="/product/item/get",
        request_ids=[str(request_id)] if request_id else [],
        item=item,  # type: ignore[arg-type]
    )
