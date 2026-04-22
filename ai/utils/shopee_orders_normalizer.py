import re
import sqlite3
from numbers import Integral, Real
from pathlib import Path
from typing import Any

import pandas as pd

from .spreadsheet_utils import normalize_dataframe, read_spreadsheet_sheets

FIELD_SPECS: dict[str, dict[str, Any]] = {
    "order_id": {"aliases": ["Order ID"], "level": "both", "sqlite_type": "TEXT"},
    "order_status": {"aliases": ["Order Status"], "level": "order", "sqlite_type": "TEXT"},
    "hot_listing": {"aliases": ["Hot Listing"], "level": "order", "sqlite_type": "BOOLEAN"},
    "return_refund_status": {
        "aliases": ["Return / Refund Status"],
        "level": "order",
        "sqlite_type": "TEXT",
    },
    "tracking_number": {
        "aliases": ["Tracking Number*", "Tracking Number"],
        "level": "order",
        "sqlite_type": "TEXT",
    },
    "shipping_option": {"aliases": ["Shipping Option"], "level": "order", "sqlite_type": "TEXT"},
    "shipment_method": {"aliases": ["Shipment Method"], "level": "order", "sqlite_type": "TEXT"},
    "estimated_ship_out_date": {
        "aliases": ["Estimated Ship Out Date"],
        "level": "order",
        "sqlite_type": "DATE",
    },
    "ship_time": {"aliases": ["Ship Time"], "level": "order", "sqlite_type": "DATE"},
    "order_creation_date": {
        "aliases": ["Order Creation Date"],
        "level": "order",
        "sqlite_type": "DATE",
    },
    "order_paid_time": {"aliases": ["Order Paid Time"], "level": "order", "sqlite_type": "DATE"},
    "no_of_product_in_order": {
        "aliases": ["No of product in order"],
        "level": "order",
        "sqlite_type": "INTEGER",
    },
    "order_total_weight": {
        "aliases": ["Order Total Weight"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "voucher_code": {"aliases": ["Voucher Code"], "level": "order", "sqlite_type": "TEXT"},
    "discount_voucher_amount_sponsored_by_seller": {
        "aliases": ["Discount Voucher Amount Sponsored by Seller"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "coin_cashback_voucher_amount_sponsored_by_seller": {
        "aliases": [
            "Coin Cashback Voucher Amount Sponsored by Seller",
            "Coin Cashback Voucher Amount Spo nsored by Seller",
        ],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "discount_voucher_amount_sponsored_by_shopee": {
        "aliases": ["Discount Voucher Amount Sponsored by Shopee"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "bundle_deal_indicator": {
        "aliases": ["Bundle Deal Indicator"],
        "level": "order",
        "sqlite_type": "BOOLEAN",
    },
    "shopee_bundle_discount": {
        "aliases": ["Shopee Bundle Discount"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "seller_bundle_discount": {
        "aliases": ["Seller Bundle Discount"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "coin_cashback_voucher_amount_sponsored_by_shopee": {
        "aliases": ["Coin Cashback Voucher Amount Sponsored by Shopee"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "credit_card_discount_total": {
        "aliases": ["Credit Card Discount Total"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "total_amount": {"aliases": ["Total Amount"], "level": "order", "sqlite_type": "REAL"},
    "buyer_paid_shipping_fee": {
        "aliases": ["Buyer Paid Shipping Fee"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "shipping_rebate_estimate": {
        "aliases": ["Shipping Rebate Estimate"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "reverse_shipping_fee": {
        "aliases": ["Reverse Shipping Fee"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "transaction_fee": {"aliases": ["Transaction Fee"], "level": "order", "sqlite_type": "REAL"},
    "commission_fee": {"aliases": ["Commission Fee"], "level": "order", "sqlite_type": "REAL"},
    "service_fee": {"aliases": ["Service Fee"], "level": "order", "sqlite_type": "REAL"},
    "grand_total": {"aliases": ["Grand Total"], "level": "order", "sqlite_type": "REAL"},
    "estimated_shipping_fee": {
        "aliases": ["Estimated Shipping Fee"],
        "level": "order",
        "sqlite_type": "REAL",
    },
    "username_buyer": {"aliases": ["Username (Buyer)"], "level": "order", "sqlite_type": "TEXT"},
    "receiver_name": {"aliases": ["Receiver Name"], "level": "order", "sqlite_type": "TEXT"},
    "phone_number": {"aliases": ["Phone Number"], "level": "order", "sqlite_type": "TEXT"},
    "delivery_address": {"aliases": ["Delivery Address"], "level": "order", "sqlite_type": "TEXT"},
    "town": {"aliases": ["Town"], "level": "order", "sqlite_type": "TEXT"},
    "district": {"aliases": ["District"], "level": "order", "sqlite_type": "TEXT"},
    "city": {"aliases": ["City"], "level": "order", "sqlite_type": "TEXT"},
    "province": {"aliases": ["Province"], "level": "order", "sqlite_type": "TEXT"},
    "country": {"aliases": ["Country"], "level": "order", "sqlite_type": "TEXT"},
    "zip_code": {"aliases": ["Zip Code"], "level": "order", "sqlite_type": "TEXT"},
    "remark_from_buyer": {
        "aliases": ["Remark from buyer"],
        "level": "order",
        "sqlite_type": "TEXT",
    },
    "order_complete_time": {
        "aliases": ["Order Complete Time"],
        "level": "order",
        "sqlite_type": "DATE",
    },
    "note": {"aliases": ["Note"], "level": "order", "sqlite_type": "TEXT"},
    "sku_reference_no": {"aliases": ["SKU Reference No."], "level": "item", "sqlite_type": "TEXT"},
    "parent_sku_reference_no": {
        "aliases": ["Parent SKU Reference No."],
        "level": "item",
        "sqlite_type": "TEXT",
    },
    "product_name": {"aliases": ["Product Name"], "level": "item", "sqlite_type": "TEXT"},
    "variation_name": {"aliases": ["Variation Name"], "level": "item", "sqlite_type": "TEXT"},
    "original_price": {"aliases": ["Original Price"], "level": "item", "sqlite_type": "REAL"},
    "deal_price": {"aliases": ["Deal Price"], "level": "item", "sqlite_type": "REAL"},
    "quantity": {"aliases": ["Quantity"], "level": "item", "sqlite_type": "INTEGER"},
    "returned_quantity": {"aliases": ["Returned quantity"], "level": "item", "sqlite_type": "INTEGER"},
    "total_buyer_payment": {
        "aliases": ["Total Buyer Payment"],
        "level": "item",
        "sqlite_type": "REAL",
    },
    "seller_rebate": {"aliases": ["Seller Rebate"], "level": "item", "sqlite_type": "REAL"},
    "seller_discount": {"aliases": ["Seller Discount"], "level": "item", "sqlite_type": "REAL"},
    "shopee_rebate": {"aliases": ["Shopee Rebate"], "level": "item", "sqlite_type": "REAL"},
    "sku_total_weight": {"aliases": ["SKU Total Weight"], "level": "item", "sqlite_type": "REAL"},
}


def _collect_field_aliases(levels: set[str]) -> dict[str, list[str]]:
    return {
        name: list(spec["aliases"])
        for name, spec in FIELD_SPECS.items()
        if str(spec["level"]) in levels
    }


ORDER_FIELD_ALIASES = _collect_field_aliases({"order", "both"})
ITEM_FIELD_ALIASES = _collect_field_aliases({"item", "both"})
FIELD_SQLITE_TYPES: dict[str, str] = {
    name: str(spec["sqlite_type"]) for name, spec in FIELD_SPECS.items()
}
DATE_FIELDS = {name for name, sqlite_type in FIELD_SQLITE_TYPES.items() if sqlite_type == "DATE"}
BOOLEAN_FIELDS = {name for name, sqlite_type in FIELD_SQLITE_TYPES.items() if sqlite_type == "BOOLEAN"}
INTEGER_FIELDS = {name for name, sqlite_type in FIELD_SQLITE_TYPES.items() if sqlite_type == "INTEGER"}
REAL_FIELDS = {name for name, sqlite_type in FIELD_SQLITE_TYPES.items() if sqlite_type == "REAL"}
ORDER_NUMERIC_FIELDS = {
    name
    for name, spec in FIELD_SPECS.items()
    if str(spec["level"]) in {"order", "both"} and str(spec["sqlite_type"]) in {"REAL", "INTEGER"}
}
ITEM_NUMERIC_FIELDS = {
    name
    for name, spec in FIELD_SPECS.items()
    if str(spec["level"]) in {"item", "both"} and str(spec["sqlite_type"]) in {"REAL", "INTEGER"}
}


def normalize_shopee_orders(
    file_path: str,
    sheet_name: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    sheets = read_spreadsheet_sheets(file_path)
    selected_sheet = sheet_name or next(iter(sheets.keys()))
    if selected_sheet not in sheets:
        raise ValueError(f"Sheet '{selected_sheet}' not found in spreadsheet")

    frame = normalize_dataframe(sheets[selected_sheet])
    frame["_row_order"] = range(len(frame))
    resolved_columns = _resolve_columns(frame)

    order_id_column = resolved_columns["order_id"]
    if not order_id_column:
        raise ValueError("Shopee report must contain 'Order ID'")

    parent_rows = (
        frame.sort_values("_row_order")
        .drop_duplicates(subset=[order_id_column], keep="first")
        .copy()
    )

    orders = _build_table(parent_rows, resolved_columns, ORDER_FIELD_ALIASES, ORDER_NUMERIC_FIELDS)
    order_items = _build_table(frame, resolved_columns, ITEM_FIELD_ALIASES, ITEM_NUMERIC_FIELDS)

    orders = orders.dropna(subset=["order_id"])
    order_items = order_items.dropna(subset=["order_id"])
    return orders, order_items


def write_shopee_orders_to_sqlite(
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
    sqlite_db_path: str,
    orders_table: str = "orders",
    order_items_table: str = "order_items",
) -> dict[str, Any]:
    _validate_identifier(orders_table)
    _validate_identifier(order_items_table)

    Path(sqlite_db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(sqlite_db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        _ensure_orders_table(connection, orders_table, orders)
        _ensure_order_items_table(connection, order_items_table, orders_table, order_items)
        inserted_orders = _upsert_orders(connection, orders_table, orders)
        inserted_items = _replace_order_items(connection, order_items_table, order_items)
        health_check = _run_data_health_check(connection, orders_table, order_items_table)

    return {
        "orders_table": orders_table,
        "order_items_table": order_items_table,
        "orders_upserted": inserted_orders,
        "order_items_inserted": inserted_items,
        "health_check": health_check,
    }


def normalize_shopee_orders_to_sqlite(
    file_path: str,
    sqlite_db_path: str,
    sheet_name: str | None = None,
    orders_table: str = "orders",
    order_items_table: str = "order_items",
) -> dict[str, Any]:
    orders, order_items = normalize_shopee_orders(file_path=file_path, sheet_name=sheet_name)
    write_result = write_shopee_orders_to_sqlite(
        orders=orders,
        order_items=order_items,
        sqlite_db_path=sqlite_db_path,
        orders_table=orders_table,
        order_items_table=order_items_table,
    )
    return {
        **write_result,
        "orders_rows": int(orders.shape[0]),
        "order_items_rows": int(order_items.shape[0]),
    }


def _resolve_columns(frame: pd.DataFrame) -> dict[str, str | None]:
    lookup: dict[str, str] = {}
    for column in frame.columns:
        canonical = _canonical(str(column))
        lookup.setdefault(canonical, str(column))

    resolved: dict[str, str | None] = {}
    for output_name, aliases in {**ORDER_FIELD_ALIASES, **ITEM_FIELD_ALIASES}.items():
        resolved[output_name] = None
        for alias in aliases:
            actual = lookup.get(_canonical(alias))
            if actual:
                resolved[output_name] = actual
                break
    return resolved


def _build_table(
    source: pd.DataFrame,
    resolved_columns: dict[str, str | None],
    aliases: dict[str, list[str]],
    numeric_fields: set[str],
) -> pd.DataFrame:
    built: dict[str, pd.Series] = {}
    for output_name in aliases:
        source_column = resolved_columns.get(output_name)
        if source_column and source_column in source.columns:
            series = source[source_column]
        else:
            series = pd.Series([pd.NA] * len(source), index=source.index)

        if output_name in BOOLEAN_FIELDS:
            built[output_name] = _to_boolean(series)
        elif output_name in DATE_FIELDS:
            built[output_name] = _to_datetime(series)
        elif output_name in INTEGER_FIELDS:
            built[output_name] = _to_numeric(series).round().astype("Int64")
        elif output_name in numeric_fields or output_name in REAL_FIELDS:
            built[output_name] = _to_numeric(series)
        else:
            built[output_name] = series

    return pd.DataFrame(built)


def _to_numeric(series: pd.Series) -> pd.Series:
    text_series = series.astype(str)
    cleaned = text_series.str.replace(r"[,\$%]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def _to_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def _to_boolean(series: pd.Series) -> pd.Series:
    def parse_bool(value: Any) -> Any:
        if pd.isna(value):
            return pd.NA
        lowered = str(value).strip().lower()
        if lowered in {"1", "true", "t", "yes", "y"}:
            return True
        if lowered in {"0", "false", "f", "no", "n"}:
            return False
        return pd.NA

    return series.apply(parse_bool).astype("boolean")


def _canonical(value: str) -> str:
    text = (value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def _validate_identifier(name: str):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"Invalid SQLite identifier: {name}")


def _ensure_orders_table(connection: sqlite3.Connection, table_name: str, data_frame: pd.DataFrame):
    column_defs = ["order_id TEXT PRIMARY KEY"]
    for column in data_frame.columns:
        if column == "order_id":
            continue
        column_defs.append(f"{_quote_identifier(column)} {_sqlite_type(column, data_frame[column])}")
    query = f"CREATE TABLE IF NOT EXISTS {_quote_identifier(table_name)} ({', '.join(column_defs)})"
    connection.execute(query)
    expected = {
        column: _sqlite_type(column, data_frame[column])
        for column in data_frame.columns
        if column != "order_id"
    }
    _ensure_columns_exist(connection, table_name, expected)


def _ensure_order_items_table(
    connection: sqlite3.Connection,
    table_name: str,
    orders_table: str,
    data_frame: pd.DataFrame,
):
    column_defs = []
    for column in data_frame.columns:
        nullable = "NOT NULL" if column == "order_id" else ""
        spacing = " " if nullable else ""
        column_defs.append(
            f"{_quote_identifier(column)} {_sqlite_type(column, data_frame[column])}{spacing}{nullable}".strip()
        )
    column_defs.append(
        f"FOREIGN KEY(order_id) REFERENCES {_quote_identifier(orders_table)}(order_id)"
    )
    query = f"CREATE TABLE IF NOT EXISTS {_quote_identifier(table_name)} ({', '.join(column_defs)})"
    connection.execute(query)
    expected = {column: _sqlite_type(column, data_frame[column]) for column in data_frame.columns}
    _ensure_columns_exist(connection, table_name, expected)


def _ensure_columns_exist(
    connection: sqlite3.Connection,
    table_name: str,
    expected_columns: dict[str, str],
):
    existing = {
        str(row[1])
        for row in connection.execute(
            f"PRAGMA table_info({_quote_identifier(table_name)})"
        ).fetchall()
    }
    for column, sqlite_type in expected_columns.items():
        if column in existing:
            continue
        query = (
            f"ALTER TABLE {_quote_identifier(table_name)} "
            f"ADD COLUMN {_quote_identifier(column)} {sqlite_type}"
        )
        connection.execute(query)


def _upsert_orders(connection: sqlite3.Connection, table_name: str, data_frame: pd.DataFrame) -> int:
    if data_frame.empty:
        return 0

    columns = list(data_frame.columns)
    placeholders = ", ".join(["?"] * len(columns))
    quoted_columns = ", ".join(_quote_identifier(column) for column in columns)
    updates = ", ".join(
        f"{_quote_identifier(column)}=excluded.{_quote_identifier(column)}"
        for column in columns
        if column != "order_id"
    )
    if updates:
        query = (
            f"INSERT INTO {_quote_identifier(table_name)} ({quoted_columns}) VALUES ({placeholders}) "
            f"ON CONFLICT(order_id) DO UPDATE SET {updates}"
        )
    else:
        query = (
            f"INSERT INTO {_quote_identifier(table_name)} ({quoted_columns}) VALUES ({placeholders}) "
            "ON CONFLICT(order_id) DO NOTHING"
        )
    records = [tuple(_coerce_sql_value(value) for value in row) for row in data_frame.itertuples(index=False)]
    connection.executemany(query, records)
    return len(records)


def _replace_order_items(connection: sqlite3.Connection, table_name: str, data_frame: pd.DataFrame) -> int:
    if data_frame.empty:
        return 0

    if "order_id" in data_frame.columns:
        order_ids = [
            str(order_id)
            for order_id in data_frame["order_id"].dropna().unique().tolist()
            if str(order_id).strip()
        ]
        if order_ids:
            placeholders = ", ".join(["?"] * len(order_ids))
            delete_query = (
                f"DELETE FROM {_quote_identifier(table_name)} "
                f"WHERE order_id IN ({placeholders})"
            )
            connection.execute(delete_query, tuple(order_ids))

    columns = list(data_frame.columns)
    placeholders = ", ".join(["?"] * len(columns))
    quoted_columns = ", ".join(_quote_identifier(column) for column in columns)
    query = f"INSERT INTO {_quote_identifier(table_name)} ({quoted_columns}) VALUES ({placeholders})"
    records = [tuple(_coerce_sql_value(value) for value in row) for row in data_frame.itertuples(index=False)]
    connection.executemany(query, records)
    return len(records)


def _sqlite_type(column_name: str, series: pd.Series) -> str:
    declared = FIELD_SQLITE_TYPES.get(column_name)
    if declared:
        return declared
    if pd.api.types.is_integer_dtype(series.dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series.dtype):
        return "REAL"
    if pd.api.types.is_datetime64_any_dtype(series.dtype):
        return "DATE"
    if pd.api.types.is_bool_dtype(series.dtype):
        return "BOOLEAN"
    return "TEXT"


def _quote_identifier(identifier: str) -> str:
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'


def _coerce_sql_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item") and not isinstance(value, (str, bytes, bytearray)):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        return float(value)
    return value


def _run_data_health_check(
    connection: sqlite3.Connection,
    orders_table: str,
    order_items_table: str,
) -> dict[str, Any]:
    orders_identifier = _quote_identifier(orders_table)
    items_identifier = _quote_identifier(order_items_table)

    orphan_row = connection.execute(
        (
            "SELECT "
            "COUNT(DISTINCT o.order_id) AS total_orders, "
            "COUNT(DISTINCT i.order_id) AS orders_with_items, "
            "COUNT(DISTINCT o.order_id) - COUNT(DISTINCT i.order_id) AS orphaned_count "
            f"FROM {orders_identifier} o "
            f"LEFT JOIN {items_identifier} i ON o.order_id = i.order_id"
        )
    ).fetchone()

    null_row = connection.execute(
        (
            "SELECT "
            "SUM(CASE WHEN grand_total IS NULL THEN 1 ELSE 0 END) AS null_grand_total, "
            "SUM(CASE WHEN transaction_fee IS NULL THEN 1 ELSE 0 END) AS null_fees "
            f"FROM {orders_identifier}"
        )
    ).fetchone()

    date_row = connection.execute(
        f"SELECT MIN(order_paid_time), MAX(order_paid_time) FROM {orders_identifier}"
    ).fetchone()

    return {
        "orphaned_orders": {
            "total_orders": int(orphan_row[0] or 0),
            "orders_with_items": int(orphan_row[1] or 0),
            "orphaned_count": int(orphan_row[2] or 0),
        },
        "nulls": {
            "null_grand_total": int(null_row[0] or 0),
            "null_fees": int(null_row[1] or 0),
        },
        "date_range": {
            "min_order_paid_time": date_row[0],
            "max_order_paid_time": date_row[1],
        },
    }
