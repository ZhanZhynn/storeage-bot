from typing import Any

from .client import LazadaClient


def _paginate(
    client: LazadaClient,
    *,
    endpoint: str,
    base_params: dict[str, Any],
    collection_keys: tuple[str, ...],
    limit: int,
    offset: int,
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
        params["limit"] = limit
        params["offset"] = current_offset

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


def get_payout_status(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    limit: int = 100,
    offset: int = 0,
    max_pages: int = 10,
) -> dict[str, Any]:
    result = _paginate(
        client,
        endpoint="/finance/payout/status/get",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
        },
        collection_keys=("payouts", "payout_statuses", "records", "items"),
        limit=limit,
        offset=offset,
        max_pages=max_pages,
    )
    result["payouts"] = result.pop("items")
    return result


def query_account_transactions(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    limit: int = 100,
    offset: int = 0,
    max_pages: int = 10,
) -> dict[str, Any]:
    result = _paginate(
        client,
        endpoint="/finance/transaction/accountTransactions/query",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
        },
        collection_keys=("transactions", "account_transactions", "records", "items"),
        limit=limit,
        offset=offset,
        max_pages=max_pages,
    )
    result["transactions"] = result.pop("items")
    return result


def query_logistics_fee_detail(
    client: LazadaClient,
    *,
    created_after: str,
    created_before: str,
    limit: int = 100,
    offset: int = 0,
    max_pages: int = 10,
) -> dict[str, Any]:
    result = _paginate(
        client,
        endpoint="/lbs/slb/queryLogisticsFeeDetail",
        base_params={
            "created_after": created_after,
            "created_before": created_before,
        },
        collection_keys=("logistics_fee_details", "details", "records", "items"),
        limit=limit,
        offset=offset,
        max_pages=max_pages,
    )
    result["logistics_fee_details"] = result.pop("items")
    return result


def get_transaction_details(
    client: LazadaClient,
    *,
    transaction_number: str,
) -> dict[str, Any]:
    payload = client.get(
        "/finance/transaction/details/get",
        {
            "transaction_number": transaction_number,
        },
    )
    request_id = payload.get("request_id")
    data = payload.get("data") or {}

    details = data.get("details")
    if details is None:
        details = data

    return {
        "endpoint": "/finance/transaction/details/get",
        "request_ids": [str(request_id)] if request_id else [],
        "details": details,
    }
