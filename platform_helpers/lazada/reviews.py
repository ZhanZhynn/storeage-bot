from datetime import datetime
from datetime import timezone
from typing import Any

from .client import LazadaClient


_MAX_HISTORY_SPAN_MS = 3 * 24 * 60 * 60 * 1000


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


def list_seller_reviews_history(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    item_id: str | None = None,
    current: int = 1,
    limit: int = 100,
    max_pages: int = 10,
) -> dict[str, Any]:
    if not item_id:
        raise ValueError("item_id is required for seller-history-list")
    if current <= 0:
        raise ValueError("current must be > 0")
    if limit <= 0:
        raise ValueError("limit must be > 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    start_time = _to_epoch_millis(created_after)
    end_time = _to_epoch_millis(created_before)
    if end_time < start_time:
        raise ValueError("created_before must be >= created_after")

    reviews: list[dict[str, Any]] = []
    request_ids: list[str] = []
    page = current
    has_more = False

    window_start = start_time
    while window_start <= end_time:
        window_end = min(end_time, window_start + _MAX_HISTORY_SPAN_MS - 1)
        page = current if window_start == start_time else 1

        for _ in range(max_pages):
            payload = client.get(
                "/review/seller/history/list",
                {
                    "item_id": item_id,
                    "start_time": window_start,
                    "end_time": window_end,
                    "current": page,
                    "limit": limit,
                },
            )
            request_id = payload.get("request_id")
            if request_id:
                request_ids.append(str(request_id))

            data = payload.get("data") or {}
            page_reviews = data.get("reviews")
            if not isinstance(page_reviews, list):
                page_reviews = data.get("review_list")
            if not isinstance(page_reviews, list):
                page_reviews = data.get("items")
            if not isinstance(page_reviews, list):
                page_reviews = []

            reviews.extend(page_reviews)

            if len(page_reviews) < limit:
                has_more = False
                break

            page += 1
            has_more = True

        window_start = window_end + 1

    return {
        "endpoint": "/review/seller/history/list",
        "total_fetched": len(reviews),
        "pages_fetched": len(request_ids),
        "next_current": page if has_more else None,
        "has_more": has_more,
        "request_ids": request_ids,
        "reviews": reviews,
    }


def list_seller_reviews_v2(
    client: LazadaClient,
    *,
    id_list: str,
    item_id: str | None = None,
) -> dict[str, Any]:
    if not id_list:
        raise ValueError("id_list is required for seller-list-v2")

    params: dict[str, Any] = {
        "id_list": id_list,
    }
    if item_id:
        params["item_id"] = item_id

    payload = client.get("/review/seller/list/v2", params)
    request_id = payload.get("request_id")
    data = payload.get("data") or {}

    review_list = data.get("review_list")
    if not isinstance(review_list, list):
        review_list = data.get("reviews")
    if not isinstance(review_list, list):
        review_list = data.get("items")
    if not isinstance(review_list, list):
        review_list = []

    return {
        "endpoint": "/review/seller/list/v2",
        "request_ids": [str(request_id)] if request_id else [],
        "total_fetched": len(review_list),
        "reviews": review_list,
    }


def add_seller_review_reply(
    client: LazadaClient,
    *,
    id_list: str,
    content: str,
) -> dict[str, Any]:
    payload = client.post(
        "/review/seller/reply/add",
        {
            "id_list": id_list,
            "content": content,
        },
    )
    request_id = payload.get("request_id")
    data = payload.get("data") or {}
    return {
        "endpoint": "/review/seller/reply/add",
        "request_ids": [str(request_id)] if request_id else [],
        "reply_result": data,
    }
