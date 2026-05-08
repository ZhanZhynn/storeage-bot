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

