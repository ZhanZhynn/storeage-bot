from __future__ import annotations

from typing import Any

from .client import ShopeeClient
from .models import (
    CommentsResponse,
    ModelListResponse,
    ProductCreateResponse,
    ProductExtraInfoResponse,
    ProductItemResponse,
    ProductPromotionResponse,
    ProductsResponse,
    ReplyCommentsResponse,
)


def get_products(
    client: ShopeeClient,
    *,
    page_size: int = 50,
    offset: int = 0,
    item_status: str | list[str] | None = None,
    update_time_from: int | None = None,
    update_time_to: int | None = None,
    max_pages: int = 10,
) -> ProductsResponse:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    collected: list[dict[str, Any]] = []
    request_ids: list[str] = []
    current_offset = offset
    has_more = False

    status_list: list[str] = []
    if item_status is None:
        status_list = ["NORMAL"]
    elif isinstance(item_status, str):
        status_list = [item_status]
    else:
        status_list = [status for status in item_status if status]

    for _ in range(max_pages):
        params: dict[str, Any] = {
            "page_size": page_size,
            "offset": current_offset,
        }
        if status_list:
            params["item_status"] = status_list
        if update_time_from is not None:
            params["update_time_from"] = update_time_from
        if update_time_to is not None:
            params["update_time_to"] = update_time_to

        payload = client.get("/api/v2/product/get_item_list", params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        response = payload.get("response") or {}
        items = response.get("item") or []
        if not isinstance(items, list):
            items = []

        collected.extend([item for item in items if isinstance(item, dict)])
        has_more = bool(response.get("has_next_page"))
        if not has_more:
            break
        current_offset = int(response.get("next_offset") or (current_offset + page_size))

    return ProductsResponse(
        endpoint="/api/v2/product/get_item_list",
        request_ids=request_ids,
        total_fetched=len(collected),
        pages_fetched=len(request_ids),
        has_more=has_more,
        next_offset=current_offset if has_more else None,
        items=collected,
    )


def search_products(
    client: ShopeeClient,
    *,
    page_size: int = 50,
    offset: str | None = None,
    item_name: str | None = None,
    item_sku: str | None = None,
    attribute_status: int | None = None,
    item_status: str | list[str] | None = None,
    deboost_only: bool | None = None,
    max_pages: int = 10,
) -> ProductsResponse:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if not item_name and attribute_status is None:
        raise ValueError("item_name or attribute_status is required")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    collected: list[dict[str, Any]] = []
    request_ids: list[str] = []
    current_offset = offset or ""
    status_list: list[str] = []
    if isinstance(item_status, str):
        status_list = [item_status]
    elif item_status:
        status_list = [status for status in item_status if status]
    has_more = False

    for _ in range(max_pages):
        params: dict[str, Any] = {"page_size": page_size}
        if current_offset:
            params["offset"] = current_offset
        if item_name:
            params["item_name"] = item_name
        if item_sku:
            params["item_sku"] = item_sku
        if attribute_status is not None:
            params["attribute_status"] = attribute_status
        if status_list:
            params["item_status"] = status_list
        if deboost_only is not None:
            params["deboost_only"] = deboost_only

        payload = client.get("/api/v2/product/search_item", params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        response = payload.get("response") or {}
        item_ids = response.get("item_id_list") or []
        if not isinstance(item_ids, list):
            item_ids = []

        collected.extend(
            [{"item_id": item_id} for item_id in item_ids if isinstance(item_id, int)]
        )
        next_offset = response.get("next_offset") or ""
        has_more = bool(next_offset)
        if not has_more:
            break
        current_offset = str(next_offset)

    return ProductsResponse(
        endpoint="/api/v2/product/search_item",
        request_ids=request_ids,
        total_fetched=len(collected),
        pages_fetched=len(request_ids),
        has_more=has_more,
        next_offset=current_offset if has_more else None,
        items=collected,
    )


def get_product(client: ShopeeClient, *, item_id: int) -> ProductItemResponse:
    payload = client.get("/api/v2/product/get_item_base_info", {"item_id_list": [item_id]})
    request_id = payload.get("request_id")
    response = payload.get("response") or {}
    items = response.get("item_list") or []
    if not isinstance(items, list):
        items = []

    item = {}
    if items:
        first = items[0]
        if isinstance(first, dict):
            item = first

    has_model = bool(item.get("has_model"))
    models: list[dict[str, Any]] = []
    if has_model:
        models_payload = client.get("/api/v2/product/get_model_list", {"item_id": item_id})
        model_response = models_payload.get("response") or {}
        model_list = model_response.get("model") or model_response.get("model_list") or []
        if isinstance(model_list, list):
            models = [model for model in model_list if isinstance(model, dict)]

    return ProductItemResponse(
        endpoint="/api/v2/product/get_item_base_info",
        request_ids=[str(request_id)] if request_id else [],
        item_id=item_id,
        has_model=has_model,
        item_base_info=item,
        models=models,
    )


def get_model_list(client: ShopeeClient, *, item_id: int) -> ModelListResponse:
    payload = client.get("/api/v2/product/get_model_list", {"item_id": item_id})
    request_id = payload.get("request_id")
    response = payload.get("response") or {}
    models = response.get("model") or response.get("model_list") or []
    if not isinstance(models, list):
        models = []
    return ModelListResponse(
        endpoint="/api/v2/product/get_model_list",
        request_ids=[str(request_id)] if request_id else [],
        item_id=item_id,
        models=[model for model in models if isinstance(model, dict)],
    )


def get_product_extra_info(client: ShopeeClient, *, item_id: int) -> ProductExtraInfoResponse:
    payload = client.get("/api/v2/product/get_item_extra_info", {"item_id_list": [item_id]})
    request_id = payload.get("request_id")
    response = payload.get("response") or {}
    items = response.get("item_list") or []
    if not isinstance(items, list):
        items = []

    extra_info: dict[str, Any] = {}
    if items:
        first = items[0]
        if isinstance(first, dict):
            extra_info = first

    return ProductExtraInfoResponse(
        endpoint="/api/v2/product/get_item_extra_info",
        request_ids=[str(request_id)] if request_id else [],
        item_id=item_id,
        extra_info=extra_info,
    )


def get_product_promotion(client: ShopeeClient, *, item_id: int) -> ProductPromotionResponse:
    payload = client.get("/api/v2/product/get_item_promotion", {"item_id_list": [item_id]})
    request_id = payload.get("request_id")
    response = payload.get("response") or {}
    promotions: list[Any] = []
    success_list = response.get("success_list") or []
    if isinstance(success_list, list):
        for entry in success_list:
            if isinstance(entry, dict) and entry.get("item_id") == item_id:
                promotions = entry.get("promotion") or []
                break
    if not promotions:
        promotions = response.get("promotion_list") or []
    if not isinstance(promotions, list):
        promotions = []
    return ProductPromotionResponse(
        endpoint="/api/v2/product/get_item_promotion",
        request_ids=[str(request_id)] if request_id else [],
        item_id=item_id,
        promotions=[promo for promo in promotions if isinstance(promo, dict)],
    )


def update_product(client: ShopeeClient, *, item_id: int, update_payload: dict[str, Any]) -> dict[str, Any]:
    payload = client.post("/api/v2/product/update_item", {"item_id": item_id, **update_payload})
    return payload


def unlist_product(client: ShopeeClient, *, item_id: int, unlist: bool = True) -> dict[str, Any]:
    payload = client.post("/api/v2/product/unlist_item", {"item_id": item_id, "unlist": unlist})
    return payload


def delete_product(client: ShopeeClient, *, item_id: int) -> dict[str, Any]:
    payload = client.post("/api/v2/product/delete_item", {"item_id": item_id})
    return payload


def init_tier_variation(
    client: ShopeeClient,
    *,
    item_id: int,
    tier_variation: list[dict[str, Any]],
    model_list: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = client.post(
        "/api/v2/product/init_tier_variation",
        {"item_id": item_id, "tier_variation": tier_variation, "model": model_list},
    )
    return payload


def update_tier_variation(
    client: ShopeeClient,
    *,
    item_id: int,
    tier_variation: list[dict[str, Any]],
    model_list: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"item_id": item_id, "tier_variation": tier_variation}
    if model_list is not None:
        body["model_list"] = model_list
    payload = client.post("/api/v2/product/update_tier_variation", body)
    return payload


def add_model(
    client: ShopeeClient,
    *,
    item_id: int,
    model_list: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = client.post("/api/v2/product/add_model", {"item_id": item_id, "model_list": model_list})
    return payload


def update_model(
    client: ShopeeClient,
    *,
    item_id: int,
    model_list: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = client.post(
        "/api/v2/product/update_model",
        {"item_id": item_id, "model_list": model_list},
    )
    return payload


def delete_model(
    client: ShopeeClient,
    *,
    item_id: int,
    model_id_list: list[int],
) -> dict[str, Any]:
    payload = client.post(
        "/api/v2/product/delete_model",
        {"item_id": item_id, "model_id_list": model_id_list},
    )
    return payload


def get_item_limit(client: ShopeeClient, *, item_id: int) -> dict[str, Any]:
    payload = client.get("/api/v2/product/get_item_limit", {"item_id": item_id})
    return payload


def get_product_price(client: ShopeeClient, *, item_id: int, has_model: bool) -> dict[str, Any]:
    if has_model:
        payload = client.get("/api/v2/product/get_model_list", {"item_id": item_id})
    else:
        payload = client.get("/api/v2/product/get_item_base_info", {"item_id_list": [item_id]})
    return payload


def get_product_stock(client: ShopeeClient, *, item_id: int, has_model: bool) -> dict[str, Any]:
    if has_model:
        payload = client.get("/api/v2/product/get_model_list", {"item_id": item_id})
    else:
        payload = client.get("/api/v2/product/get_item_base_info", {"item_id_list": [item_id]})
    return payload


def update_product_price(
    client: ShopeeClient,
    *,
    item_id: int,
    price_list: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = client.post(
        "/api/v2/product/update_price",
        {"item_id": item_id, "price_list": price_list},
    )
    return payload


def update_product_stock(
    client: ShopeeClient,
    *,
    item_id: int,
    stock_list: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = client.post(
        "/api/v2/product/update_stock",
        {"item_id": item_id, "stock_list": stock_list},
    )
    return payload


def add_product(client: ShopeeClient, *, payload: dict[str, Any]) -> ProductCreateResponse:
    if not payload:
        raise ValueError("payload must not be empty")
    response = client.post("/api/v2/product/add_item", payload)
    request_id = response.get("request_id")
    body = response.get("response") or {}
    item_id = body.get("item_id")
    if not isinstance(item_id, int):
        item_id = None
    return ProductCreateResponse(
        endpoint="/api/v2/product/add_item",
        request_ids=[str(request_id)] if request_id else [],
        item_id=item_id,
        response=body if isinstance(body, dict) else {},
    )


def get_comments(
    client: ShopeeClient,
    *,
    page_size: int = 50,
    cursor: str = "",
    item_id: int | None = None,
    comment_id: int | None = None,
    max_pages: int = 10,
) -> CommentsResponse:
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    collected: list[dict[str, Any]] = []
    request_ids: list[str] = []
    next_cursor = cursor or ""
    has_more = False

    for _ in range(max_pages):
        params: dict[str, Any] = {
            "page_size": page_size,
            "cursor": next_cursor,
        }
        if item_id is not None:
            params["item_id"] = item_id
        if comment_id is not None:
            params["comment_id"] = comment_id

        payload = client.get("/api/v2/product/get_comment", params)
        request_id = payload.get("request_id")
        if request_id:
            request_ids.append(str(request_id))

        response = payload.get("response") or {}
        items = response.get("item_comment_list") or []
        if not isinstance(items, list):
            items = []

        collected.extend([item for item in items if isinstance(item, dict)])
        has_more = bool(response.get("more"))
        next_cursor = response.get("next_cursor") or ""
        if not has_more:
            break

    return CommentsResponse(
        endpoint="/api/v2/product/get_comment",
        request_ids=request_ids,
        total_fetched=len(collected),
        pages_fetched=len(request_ids),
        has_more=has_more,
        next_cursor=next_cursor or None,
        comments=collected,
    )


def reply_comments(
    client: ShopeeClient,
    *,
    comment_list: list[dict[str, Any]],
) -> ReplyCommentsResponse:
    if not comment_list:
        raise ValueError("comment_list must not be empty")
    payload = client.post("/api/v2/product/reply_comment", {"comment_list": comment_list})
    request_id = payload.get("request_id")
    response = payload.get("response") or {}
    result_list = response.get("result_list") or []
    if not isinstance(result_list, list):
        result_list = []
    warning = response.get("warning")
    if warning is not None and not isinstance(warning, list):
        warning = None
    return ReplyCommentsResponse(
        endpoint="/api/v2/product/reply_comment",
        request_ids=[str(request_id)] if request_id else [],
        result_list=[item for item in result_list if isinstance(item, dict)],
        warning=warning,
    )
