"""
Pydantic models for Lazada API self-documentation.

These models document the data structures for API responses, CLI inputs,
config, and state stores. Used primarily for type hints and schema generation.
"""
from typing import Any

from pydantic import BaseModel, ConfigDict


class LazadaConfig(BaseModel):
    """Lazada API configuration."""

    app_key: str = ""
    app_secret: str = ""
    access_token: str = ""
    region: str = "MY"
    api_base: str = "https://api.lazada.com.my/rest"
    partner_id: str = ""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
    )


class Order(BaseModel):
    """Single order from Lazada API."""

    order_id: int | str | None = None
    order_number: int | str | None = None
    status: str | None = None
    statuses: list[str] | None = None
    price: str | None = None
    price_formated: str | None = None
    currency: str | None = None
    buyer_id: str | None = None
    buyer_email: str | None = None
    estimated_delivery_time: int | str | None = None
    created_at: str | int | None = None
    updated_at: str | int | None = None
    delivery_type: str | None = None
    payment_method: str | None = None
    items: list[dict[str, Any]] | None = None
    remark: str | None = None
    warehouse_code: str | None = None
    order_items: list[dict[str, Any]] | None = None

    model_config = ConfigDict(extra="allow")


class OrderItem(BaseModel):
    """Single order item from Lazada API."""

    order_item_id: int | str | None = None
    order_id: int | str | None = None
    item_id: int | str | None = None
    name: str | None = None
    sku: str | None = None
    seller_sku: str | None = None
    shop_sku: str | None = None
    price: str | None = None
    discount: str | None = None
    quantity: int | None = None
    status: str | None = None
    created_at: str | int | None = None

    model_config = ConfigDict(extra="allow")


class OrderItemsResponse(BaseModel):
    """Response from /order/items/get or /orders/items/get."""

    endpoint: str = ""
    request_ids: list[str] = []
    order_id: str | None = None
    total_fetched: int = 0
    order_items: list[OrderItem] = []

    model_config = ConfigDict(extra="allow")


class OrdersResponse(BaseModel):
    """Response from /orders/get (paginated)."""

    endpoint: str = ""
    total_fetched: int = 0
    pages_fetched: int = 0
    next_offset: int | None = None
    has_more: bool = False
    request_ids: list[str] = []
    orders: list[Order] = []

    model_config = ConfigDict(extra="allow")


class OrderResponse(BaseModel):
    """Response from /order/get."""

    endpoint: str = ""
    request_ids: list[str] = []
    order: Order | dict[str, Any] = {}

    model_config = ConfigDict(extra="allow")


class CancelValidationResponse(BaseModel):
    """Response from /order/reverse/cancel/validate."""

    endpoint: str = ""
    request_ids: list[str] = []
    order_id: int | str = ""
    order_item_id_list: list[int | str] = []
    validation: dict[str, Any] = {}

    model_config = ConfigDict(extra="allow")


class Product(BaseModel):
    """Single product from Lazada API."""

    item_id: int | str | None = None
    sku: str | None = None
    name: str | None = None
    brand: str | None = None
    model: str | None = None
    category_id: int | str | None = None
    status: str | None = None
    price: str | None = None
    special_price: str | None = None
    special_from: str | None = None
    special_to: str | None = None
    quantity: int | None = None
    created_at: str | int | None = None
    updated_at: str | int | None = None
    skus: list[dict[str, Any]] | None = None
    attributes: dict[str, Any] | None = None
    images: list[str] | None = None

    model_config = ConfigDict(extra="allow")


class ProductsResponse(BaseModel):
    """Response from /products/get (paginated)."""

    endpoint: str = ""
    total_products: int = 0
    pages_fetched: int = 0
    next_offset: int | None = None
    has_more: bool = False
    request_ids: list[str] = []
    products: list[Product] = []

    model_config = ConfigDict(extra="allow")


class ProductItemResponse(BaseModel):
    """Response from /product/item/get."""

    endpoint: str = ""
    request_ids: list[str] = []
    item: Product | dict[str, Any] = {}

    model_config = ConfigDict(extra="allow")


class PayoutStatus(BaseModel):
    """Payout status entry."""

    payout_id: int | str | None = None
    order_id: int | str | None = None
    status: str | None = None
    amount: str | None = None
    currency: str | None = None
    created_at: str | int | None = None

    model_config = ConfigDict(extra="allow")


class PayoutStatusResponse(BaseModel):
    """Response from /finance/payout/status/get."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_payouts: int = 0
    pages_fetched: int = 0
    next_offset: int | None = None
    has_more: bool = False
    payouts: list[PayoutStatus] = []

    model_config = ConfigDict(extra="allow")


class Transaction(BaseModel):
    """Account transaction entry."""

    transaction_id: int | str | None = None
    transaction_type: str | None = None
    sub_transaction_type: str | None = None
    transaction_number: str | None = None
    amount: str | None = None
    currency: str | None = None
    status: str | None = None
    created_at: str | int | None = None
    order_id: int | str | None = None

    model_config = ConfigDict(extra="allow")


class AccountTransactionsResponse(BaseModel):
    """Response from /finance/transaction/accountTransactions/query."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_transactions: int = 0
    pages_fetched: int = 0
    next_page: int | None = None
    has_more: bool = False
    transactions: list[Transaction] = []

    model_config = ConfigDict(extra="allow")


class LogisticsFeeDetail(BaseModel):
    """Logistics fee detail entry."""

    id: int | str | None = None
    seller_id: int | str | None = None
    request_type: str | None = None
    trade_order_id: int | str | None = None
    fee: str | None = None
    fee_type: str | None = None
    created_at: str | int | None = None

    model_config = ConfigDict(extra="allow")


class LogisticsFeeDetailResponse(BaseModel):
    """Response from /lbs/slb/queryLogisticsFeeDetail."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_records: int = 0
    pages_fetched: int = 0
    next_page: int | None = None
    has_more: bool = False
    fees: list[LogisticsFeeDetail] = []

    model_config = ConfigDict(extra="allow")


class TransactionDetail(BaseModel):
    """Transaction detail entry."""

    trade_order_id: int | str | None = None
    trade_order_line_id: int | str | None = None
    trans_type: str | None = None
    amount: str | None = None
    currency: str | None = None
    created_at: str | int | None = None

    model_config = ConfigDict(extra="allow")


class TransactionDetailsResponse(BaseModel):
    """Response from /finance/transaction/details/get."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_records: int = 0
    details: list[TransactionDetail] = []

    model_config = ConfigDict(extra="allow")


class ReturnDetail(BaseModel):
    """Return detail entry."""

    return_id: int | str | None = None
    order_id: int | str | None = None
    order_item_id: int | str | None = None
    item_id: int | str | None = None
    reason: str | None = None
    status: str | None = None
    created_at: str | int | None = None

    model_config = ConfigDict(extra="allow")


class ReturnDetailListResponse(BaseModel):
    """Response from /order/reverse/return/detail/list."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_returns: int = 0
    pages_fetched: int = 0
    next_offset: int | None = None
    has_more: bool = False
    returns: list[ReturnDetail] = []

    model_config = ConfigDict(extra="allow")


class ReturnHistory(BaseModel):
    """Return history entry."""

    return_id: int | str | None = None
    order_id: int | str | None = None
    status: str | None = None
    resolution: str | None = None
    created_at: str | int | None = None
    updated_at: str | int | None = None

    model_config = ConfigDict(extra="allow")


class ReturnHistoryListResponse(BaseModel):
    """Response from /order/reverse/return/history/list."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_returns: int = 0
    pages_fetched: int = 0
    next_offset: int | None = None
    has_more: bool = False
    returns: list[ReturnHistory] = []

    model_config = ConfigDict(extra="allow")


class ReturnReason(BaseModel):
    """Return reason entry."""

    reason_id: str | None = None
    reason: str | None = None
    reason_type: str | None = None

    model_config = ConfigDict(extra="allow")


class ReasonListResponse(BaseModel):
    """Response from /order/reverse/reason/list."""

    endpoint: str = ""
    request_ids: list[str] = []
    reasons: list[ReturnReason] = []

    model_config = ConfigDict(extra="allow")


class ReverseOrder(BaseModel):
    """Reverse order entry from /reverse/getreverseordersforseller."""

    order_id: int | str | None = None
    return_id: int | str | None = None
    reverse_order_id: int | str | None = None
    trade_order_id: int | str | None = None
    request_type: str | None = None
    is_rtm: bool | str | None = None
    shipping_type: str | None = None
    status: str | None = None
    reverse_status: str | None = None
    ofc_status: str | None = None
    created_at: str | int | None = None

    model_config = ConfigDict(extra="allow")


class ReverseOrdersResponse(BaseModel):
    """Response from /reverse/getreverseordersforseller."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_returns: int = 0
    pages_fetched: int = 0
    next_offset: int | None = None
    has_more: bool = False
    orders: list[ReverseOrder] = []

    model_config = ConfigDict(extra="allow")


class Review(BaseModel):
    """Product review entry."""

    review_id: int | str | None = None
    item_id: int | str | None = None
    order_id: int | str | None = None
    rating: int | None = None
    comment: str | None = None
    created_at: str | int | None = None
    updated_at: str | int | None = None
    buyer_name: str | None = None
    images: list[str] | None = None

    model_config = ConfigDict(extra="allow")


class SellerReviewsHistoryResponse(BaseModel):
    """Response from /review/seller/history/list."""

    endpoint: str = ""
    request_ids: list[str] = []
    total_reviews: int = 0
    pages_fetched: int = 0
    next_offset: int | None = None
    has_more: bool = False
    reviews: list[str] = []

    model_config = ConfigDict(extra="allow")


class SellerReviewsV2Response(BaseModel):
    """Response from /review/seller/list/v2."""

    endpoint: str = ""
    request_ids: list[str] = []
    reviews: list[Review] = []

    model_config = ConfigDict(extra="allow")


class SellerReviewReplyResponse(BaseModel):
    """Response from /review/seller/reply/add."""

    endpoint: str = ""
    request_ids: list[str] = []
    reply_id: str | None = None
    review_id: str | None = None

    model_config = ConfigDict(extra="allow")


class ItemReviewsResponse(BaseModel):
    """Response wrapper for get-item-reviews flow."""

    domain: str = "reviews"
    action: str = "get-item-reviews"
    filters: dict[str, Any] = {}
    request_ids: list[str] = []
    review_ids: list[str] = []
    items_processed: int = 0
    api_calls_made: int = 0
    rate_limit_stopped: bool = False
    item_breakdown: list[dict[str, Any]] = []
    total_fetched: int = 0
    reviews: list[Review] = []

    model_config = ConfigDict(extra="allow")


class RecentOrdersReviewsResponse(BaseModel):
    """Response wrapper for get-recent-orders flow."""

    domain: str = "reviews"
    action: str = "get-recent-orders"
    filters: dict[str, Any] = {}
    request_ids: list[str] = []
    review_ids: list[str] = []
    orders_processed: int = 0
    unique_items: int = 0
    api_calls_made: int = 0
    rate_limit_stopped: bool = False
    item_breakdown: list[dict[str, Any]] = []
    total_fetched: int = 0
    reviews: list[Review] = []

    model_config = ConfigDict(extra="allow")


class ErrorResponse(BaseModel):
    """API error response."""

    error: str
    api_code: str | None = None
    request_id: str | None = None

    model_config = ConfigDict(extra="allow")
