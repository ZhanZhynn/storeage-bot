from typing import Any

from .client import LazadaClient
from .models import (
    AccountTransactionsResponse,
    LogisticsFeeDetailResponse,
    PayoutStatusResponse,
    TransactionDetailsResponse,
)


def _extract_request_id(payload: Any) -> list[str]:
    if isinstance(payload, dict):
        request_id = payload.get("request_id")
        if request_id:
            return [str(request_id)]
    return []


def _extract_data(payload: Any) -> Any:
    if isinstance(payload, dict):
        return payload.get("data")
    return payload


def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _paginate_by_page_num(
    client: LazadaClient,
    *,
    endpoint: str,
    base_params: dict[str, Any],
    list_keys: tuple[str, ...],
    page_num: int,
    page_size: int,
    max_pages: int,
) -> dict[str, Any]:
    if page_num <= 0:
        raise ValueError("page_num must be > 0")
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    items: list[dict[str, Any]] = []
    request_ids: list[str] = []
    current_page = page_num
    has_more = False

    for _ in range(max_pages):
        params = dict(base_params)
        params["page_num"] = current_page
        params["page_size"] = page_size

        payload = client.post(endpoint, params)
        request_ids.extend(_extract_request_id(payload))
        data = _extract_data(payload)

        page_items: list[dict[str, Any]] = []
        total_records: int | None = None

        if isinstance(data, dict):
            for key in list_keys:
                value = data.get(key)
                if isinstance(value, list):
                    page_items = _as_list_of_dicts(value)
                    break

            total_records_value = data.get("total_records")
            if isinstance(total_records_value, int):
                total_records = total_records_value
        elif isinstance(data, list):
            page_items = _as_list_of_dicts(data)

        items.extend(page_items)

        if len(page_items) < page_size:
            has_more = False
            break

        next_page = current_page + 1
        if isinstance(total_records, int) and (next_page - page_num) * page_size >= total_records:
            has_more = False
            current_page = next_page
            break

        has_more = True
        current_page = next_page

    return {
        "endpoint": endpoint,
        "total_fetched": len(items),
        "pages_fetched": len(request_ids),
        "next_page_num": current_page if has_more else None,
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
) -> PayoutStatusResponse:
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
        params = {
            "created_after": created_after,
            "created_before": created_before,
            "limit": limit,
            "offset": current_offset,
        }
        payload = client.get("/finance/payout/status/get", params)
        request_ids.extend(_extract_request_id(payload))
        data = _extract_data(payload)

        page_items: list[dict[str, Any]] = []
        count_total: int | None = None
        if isinstance(data, dict):
            payout_values = data.get("payouts")
            if not isinstance(payout_values, list):
                payout_values = data.get("payout_statuses")
            if not isinstance(payout_values, list):
                payout_values = data.get("records")
            if not isinstance(payout_values, list):
                payout_values = data.get("items")
            page_items = _as_list_of_dicts(payout_values)

            count_total_value = data.get("countTotal")
            if isinstance(count_total_value, int):
                count_total = count_total_value
        elif isinstance(data, list):
            page_items = _as_list_of_dicts(data)

        items.extend(page_items)

        if len(page_items) < limit:
            has_more = False
            break

        current_offset += limit
        if isinstance(count_total, int) and current_offset >= count_total:
            has_more = False
            break

        has_more = True

    return PayoutStatusResponse(
        endpoint="/finance/payout/status/get",
        total_payouts=len(items),
        pages_fetched=len(request_ids),
        next_offset=current_offset if has_more else None,
        has_more=has_more,
        request_ids=request_ids,
        payouts=items,  # type: ignore[arg-type]
    )


def query_account_transactions(
    client: LazadaClient,
    *,
    transaction_type: str | None,
    sub_transaction_type: str | None,
    transaction_number: str | None,
    start_time: str,
    end_time: str,
    page_num: int = 1,
    page_size: int = 10,
    max_pages: int = 10,
) -> AccountTransactionsResponse:
    base_params: dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
    }
    if transaction_type:
        base_params["transaction_type"] = transaction_type
    if sub_transaction_type:
        base_params["sub_transaction_type"] = sub_transaction_type
    if transaction_number:
        base_params["transaction_number"] = transaction_number

    internal_result = _paginate_by_page_num(
        client,
        endpoint="/finance/transaction/accountTransactions/query",
        base_params=base_params,
        list_keys=("transactions", "account_transactions", "records", "items"),
        page_num=page_num,
        page_size=page_size,
        max_pages=max_pages,
    )

    return AccountTransactionsResponse(
        endpoint="/finance/transaction/accountTransactions/query",
        request_ids=internal_result.get("request_ids", []),
        total_transactions=internal_result.get("total_fetched", 0),
        pages_fetched=internal_result.get("pages_fetched", 0),
        next_page=internal_result.get("next_page_num"),
        has_more=internal_result.get("has_more", False),
        transactions=internal_result.get("items", []),  # type: ignore[arg-type]
    )


def query_logistics_fee_detail(
    client: LazadaClient,
    *,
    seller_id: str | None,
    request_type: str | None,
    trade_order_id: str | None,
    trade_order_line_id: str | None,
    fee_type: str | None,
    biz_flow_type: str | None,
    bill_start_time: str,
    bill_end_time: str,
    page_no: int = 1,
    page_size: int = 10,
    total_records: int | None = None,
    max_pages: int = 10,
) -> LogisticsFeeDetailResponse:
    if page_no <= 0:
        raise ValueError("page_no must be > 0")
    if page_size <= 0:
        raise ValueError("page_size must be > 0")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")

    items: list[dict[str, Any]] = []
    request_ids: list[str] = []
    current_page = page_no
    has_more = False

    for _ in range(max_pages):
        params: dict[str, Any] = {
            "bill_start_time": bill_start_time,
            "bill_end_time": bill_end_time,
            "page_no": current_page,
            "page_size": page_size,
        }
        if seller_id:
            params["seller_id"] = seller_id
        if request_type:
            params["request_type"] = request_type
        if trade_order_id:
            params["trade_order_id"] = trade_order_id
        if trade_order_line_id:
            params["trade_order_line_id"] = trade_order_line_id
        if fee_type:
            params["fee_type"] = fee_type
        if biz_flow_type:
            params["biz_flow_type"] = biz_flow_type
        if total_records is not None:
            params["total_records"] = total_records

        payload = client.post("/lbs/slb/queryLogisticsFeeDetail", params)
        request_ids.extend(_extract_request_id(payload))
        data = _extract_data(payload)

        page_items: list[dict[str, Any]] = []
        inferred_total_records: int | None = None

        if isinstance(data, dict):
            for key in ("logistics_fee_details", "details", "records", "items"):
                value = data.get(key)
                if isinstance(value, list):
                    page_items = _as_list_of_dicts(value)
                    break
            total_value = data.get("total_records")
            if isinstance(total_value, int):
                inferred_total_records = total_value
        elif isinstance(data, list):
            page_items = _as_list_of_dicts(data)

        items.extend(page_items)

        if len(page_items) < page_size:
            has_more = False
            break

        next_page = current_page + 1
        known_total_records = total_records if isinstance(total_records, int) else inferred_total_records
        if isinstance(known_total_records, int) and (next_page - page_no) * page_size >= known_total_records:
            has_more = False
            current_page = next_page
            break

        has_more = True
        current_page = next_page

    return LogisticsFeeDetailResponse(
        endpoint="/lbs/slb/queryLogisticsFeeDetail",
        total_records=len(items),
        pages_fetched=len(request_ids),
        next_page_no=current_page if has_more else None,
        has_more=has_more,
        request_ids=request_ids,
        fees=items,  # type: ignore[arg-type]
    )


def get_transaction_details(
    client: LazadaClient,
    *,
    trade_order_id: str | None,
    trade_order_line_id: str | None,
    trans_type: str | None,
    start_time: str,
    end_time: str,
    offset: int = 0,
    limit: int = 100,
) -> TransactionDetailsResponse:
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if limit <= 0:
        raise ValueError("limit must be > 0")

    params: dict[str, Any] = {
        "start_time": start_time,
        "end_time": end_time,
        "offset": offset,
        "limit": limit,
    }
    if trans_type:
        params["trans_type"] = trans_type
    if trade_order_id:
        params["trade_order_id"] = trade_order_id
    if trade_order_line_id:
        params["trade_order_line_id"] = trade_order_line_id

    payload = client.get("/finance/transaction/details/get", params)
    request_ids = _extract_request_id(payload)
    data = _extract_data(payload)

    details: Any = data
    if isinstance(data, dict):
        details_value = data.get("details")
        if details_value is not None:
            details = details_value

    return TransactionDetailsResponse(
        endpoint="/finance/transaction/details/get",
        request_ids=request_ids,
        total_records=len(details) if isinstance(details, list) else 0,
        details=details,  # type: ignore[arg-type]
    )
