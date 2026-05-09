from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ShopeeBaseResponse(BaseModel):
    endpoint: str
    request_ids: list[str]

    model_config = ConfigDict(extra="allow")


class OrdersResponse(ShopeeBaseResponse):
    total_fetched: int
    pages_fetched: int
    has_more: bool
    next_cursor: str | None
    orders: list[dict[str, Any]]


class OrderItemsResponse(ShopeeBaseResponse):
    total_fetched: int
    order_ids: list[str]
    items: list[dict[str, Any]]


class OrderActionResponse(ShopeeBaseResponse):
    response: dict[str, Any]


class OrderSplitResponse(ShopeeBaseResponse):
    order_sn: str | None
    package_list: list[dict[str, Any]]


class PackageListResponse(ShopeeBaseResponse):
    total_fetched: int
    pages_fetched: int
    has_more: bool
    next_cursor: str | None
    total_count: int | None
    packages: list[dict[str, Any]]


class PackageDetailResponse(ShopeeBaseResponse):
    packages: list[dict[str, Any]]


class ProductsResponse(ShopeeBaseResponse):
    total_fetched: int
    pages_fetched: int
    has_more: bool
    next_offset: int | None
    items: list[dict[str, Any]]


class ProductItemResponse(ShopeeBaseResponse):
    item_id: int
    has_model: bool
    item_base_info: dict[str, Any]
    models: list[dict[str, Any]]


class ModelListResponse(ShopeeBaseResponse):
    item_id: int
    models: list[dict[str, Any]]


class ProductExtraInfoResponse(ShopeeBaseResponse):
    item_id: int
    extra_info: dict[str, Any]


class ProductPromotionResponse(ShopeeBaseResponse):
    item_id: int
    promotions: list[dict[str, Any]]


class ProductCreateResponse(ShopeeBaseResponse):
    item_id: int | None
    response: dict[str, Any]


class CommentsResponse(ShopeeBaseResponse):
    total_fetched: int
    pages_fetched: int
    has_more: bool
    next_cursor: str | None
    comments: list[dict[str, Any]]


class ReplyCommentsResponse(ShopeeBaseResponse):
    result_list: list[dict[str, Any]]
    warning: list[str] | None
