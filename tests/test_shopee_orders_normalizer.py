import sqlite3
from pathlib import Path

import pandas as pd

from ai.utils.shopee_orders_normalizer import (
    FIELD_SPECS,
    FIELD_SQLITE_TYPES,
    ITEM_FIELD_ALIASES,
    ORDER_FIELD_ALIASES,
    normalize_shopee_orders,
    normalize_shopee_orders_to_sqlite,
)


def test_normalize_shopee_orders_splits_parent_and_child_tables(tmp_path: Path):
    csv_path = tmp_path / "shopee_orders.csv"
    source = pd.DataFrame(
        [
            {
                "Order ID": "ORD-1",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-01 10:00",
                "Order Paid Time": "2026-03-01 10:05",
                "Transaction Fee": "1.20",
                "Buyer Paid Shipping Fee": "5.00",
                "Grand Total": "23.80",
                "Coin Cashback Voucher Amount Spo nsored by Seller": "0.30",
                "SKU Reference No.": "SKU-A",
                "Product Name": "Product A",
                "Variation Name": "Red",
                "Deal Price": "10.00",
                "Quantity": "1",
                "Seller Discount": "0.50",
            },
            {
                "Order ID": "ORD-1",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-01 10:00",
                "Order Paid Time": "2026-03-01 10:05",
                "Transaction Fee": "9.99",
                "Buyer Paid Shipping Fee": "99.00",
                "Grand Total": "999.00",
                "Coin Cashback Voucher Amount Spo nsored by Seller": "0.30",
                "SKU Reference No.": "SKU-B",
                "Product Name": "Product B",
                "Variation Name": "Blue",
                "Deal Price": "8.00",
                "Quantity": "2",
                "Seller Discount": "0.00",
            },
            {
                "Order ID": "ORD-2",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-02 09:30",
                "Order Paid Time": "2026-03-02 09:31",
                "Transaction Fee": "0.80",
                "Buyer Paid Shipping Fee": "3.50",
                "Grand Total": "14.20",
                "Coin Cashback Voucher Amount Spo nsored by Seller": "0.10",
                "SKU Reference No.": "SKU-C",
                "Product Name": "Product C",
                "Variation Name": "Single",
                "Deal Price": "13.40",
                "Quantity": "1",
                "Seller Discount": "0.20",
            },
        ]
    )
    source.to_csv(csv_path, index=False)

    orders, order_items = normalize_shopee_orders(str(csv_path))

    assert orders["order_id"].tolist() == ["ORD-1", "ORD-2"]
    assert order_items.shape[0] == 3
    assert order_items["order_id"].tolist() == ["ORD-1", "ORD-1", "ORD-2"]

    # First-row values must win for order-level repeated fields.
    order_one = orders.loc[orders["order_id"] == "ORD-1"].iloc[0]
    assert order_one["transaction_fee"] == 1.2
    assert order_one["buyer_paid_shipping_fee"] == 5.0
    assert order_one["grand_total"] == 23.8
    assert str(orders["ship_time"].dtype).startswith("datetime64")
    assert str(orders["order_creation_date"].dtype).startswith("datetime64")
    assert str(orders["order_paid_time"].dtype).startswith("datetime64")

    # Order-level fields should not be duplicated into order_items.
    assert "transaction_fee" not in order_items.columns
    assert "buyer_paid_shipping_fee" not in order_items.columns
    assert "order_creation_date" not in order_items.columns
    assert set(order_items.columns) >= {
        "order_id",
        "sku_reference_no",
        "quantity",
        "deal_price",
        "seller_discount",
    }


def test_normalize_shopee_orders_to_sqlite_writes_both_tables(tmp_path: Path):
    csv_path = tmp_path / "shopee_orders.csv"
    db_path = tmp_path / "shopee.db"
    source = pd.DataFrame(
        [
            {
                "Order ID": "ORD-10",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-05 08:00",
                "Order Paid Time": "2026-03-05 08:01",
                "Transaction Fee": "2.10",
                "Buyer Paid Shipping Fee": "6.00",
                "Grand Total": "31.40",
                "SKU Reference No.": "SKU-X",
                "Product Name": "Product X",
                "Variation Name": "XL",
                "Deal Price": "15.00",
                "Quantity": "1",
                "Seller Discount": "0.00",
            },
            {
                "Order ID": "ORD-10",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-05 08:00",
                "Order Paid Time": "2026-03-05 08:01",
                "Transaction Fee": "2.10",
                "Buyer Paid Shipping Fee": "6.00",
                "Grand Total": "31.40",
                "SKU Reference No.": "SKU-Y",
                "Product Name": "Product Y",
                "Variation Name": "M",
                "Deal Price": "10.00",
                "Quantity": "1",
                "Seller Discount": "0.60",
            },
        ]
    )
    source.to_csv(csv_path, index=False)

    result = normalize_shopee_orders_to_sqlite(
        file_path=str(csv_path),
        sqlite_db_path=str(db_path),
        orders_table="orders_shopee",
        order_items_table="order_items_shopee",
    )

    assert result["orders_rows"] == 1
    assert result["order_items_rows"] == 2
    assert result["orders_upserted"] == 1
    assert result["order_items_inserted"] == 2
    assert result["health_check"]["orphaned_orders"]["orphaned_count"] == 0
    assert result["health_check"]["nulls"]["null_grand_total"] == 0
    assert result["health_check"]["nulls"]["null_fees"] == 0
    assert result["health_check"]["date_range"]["min_order_paid_time"] == "2026-03-05 08:01:00"
    assert result["health_check"]["date_range"]["max_order_paid_time"] == "2026-03-05 08:01:00"

    with sqlite3.connect(db_path) as connection:
        table_info = connection.execute("PRAGMA table_info(orders_shopee)").fetchall()
        order_rows = connection.execute(
            "SELECT order_id, transaction_fee, buyer_paid_shipping_fee, grand_total, ship_time, order_creation_date, order_paid_time FROM orders_shopee"
        ).fetchall()
        item_rows = connection.execute(
            "SELECT order_id, sku_reference_no, quantity, deal_price, seller_discount FROM order_items_shopee ORDER BY sku_reference_no"
        ).fetchall()
        item_value_types = connection.execute(
            "SELECT sku_reference_no, typeof(quantity), typeof(deal_price) FROM order_items_shopee ORDER BY sku_reference_no"
        ).fetchall()

    assert order_rows == [
        (
            "ORD-10",
            2.1,
            6.0,
            31.4,
            None,
            "2026-03-05 08:00:00",
            "2026-03-05 08:01:00",
        )
    ]
    assert item_rows == [
        ("ORD-10", "SKU-X", 1, 15.0, 0.0),
        ("ORD-10", "SKU-Y", 1, 10.0, 0.6),
    ]
    assert item_value_types == [
        ("SKU-X", "integer", "real"),
        ("SKU-Y", "integer", "real"),
    ]

    table_columns = {row[1]: row[2] for row in table_info}
    assert table_columns["order_creation_date"] == "DATE"
    assert table_columns["order_paid_time"] == "DATE"


def test_field_definitions_are_derived_from_single_spec():
    assert "order_id" in ORDER_FIELD_ALIASES
    assert "order_id" in ITEM_FIELD_ALIASES
    assert FIELD_SQLITE_TYPES["order_creation_date"] == "DATE"
    assert FIELD_SQLITE_TYPES["seller_discount"] == "REAL"
    assert set(FIELD_SPECS.keys()) == set(FIELD_SQLITE_TYPES.keys())


def test_normalize_shopee_orders_to_sqlite_reimport_replaces_item_rows(tmp_path: Path):
    first_csv_path = tmp_path / "shopee_orders_first.csv"
    second_csv_path = tmp_path / "shopee_orders_second.csv"
    db_path = tmp_path / "shopee.db"

    pd.DataFrame(
        [
            {
                "Order ID": "ORD-20",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-10 09:00",
                "Order Paid Time": "2026-03-10 09:05",
                "Transaction Fee": "1.00",
                "Buyer Paid Shipping Fee": "4.00",
                "Grand Total": "24.00",
                "SKU Reference No.": "SKU-A",
                "Product Name": "Product A",
                "Variation Name": "One",
                "Deal Price": "10.00",
                "Quantity": "1",
                "Seller Discount": "0.00",
            },
            {
                "Order ID": "ORD-20",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-10 09:00",
                "Order Paid Time": "2026-03-10 09:05",
                "Transaction Fee": "1.00",
                "Buyer Paid Shipping Fee": "4.00",
                "Grand Total": "24.00",
                "SKU Reference No.": "SKU-B",
                "Product Name": "Product B",
                "Variation Name": "Two",
                "Deal Price": "14.00",
                "Quantity": "1",
                "Seller Discount": "0.00",
            },
        ]
    ).to_csv(first_csv_path, index=False)

    pd.DataFrame(
        [
            {
                "Order ID": "ORD-20",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-10 09:00",
                "Order Paid Time": "2026-03-10 09:05",
                "Transaction Fee": "2.50",
                "Buyer Paid Shipping Fee": "5.00",
                "Grand Total": "30.00",
                "SKU Reference No.": "SKU-C",
                "Product Name": "Product C",
                "Variation Name": "Three",
                "Deal Price": "30.00",
                "Quantity": "1",
                "Seller Discount": "1.00",
            }
        ]
    ).to_csv(second_csv_path, index=False)

    normalize_shopee_orders_to_sqlite(
        file_path=str(first_csv_path),
        sqlite_db_path=str(db_path),
        orders_table="orders_shopee",
        order_items_table="order_items_shopee",
    )
    normalize_shopee_orders_to_sqlite(
        file_path=str(second_csv_path),
        sqlite_db_path=str(db_path),
        orders_table="orders_shopee",
        order_items_table="order_items_shopee",
    )

    with sqlite3.connect(db_path) as connection:
        order_row = connection.execute(
            "SELECT order_id, transaction_fee, buyer_paid_shipping_fee, grand_total FROM orders_shopee WHERE order_id='ORD-20'"
        ).fetchone()
        item_rows = connection.execute(
            "SELECT order_id, sku_reference_no, quantity, deal_price, seller_discount FROM order_items_shopee WHERE order_id='ORD-20'"
        ).fetchall()

    assert order_row == ("ORD-20", 2.5, 5.0, 30.0)
    assert item_rows == [("ORD-20", "SKU-C", 1, 30.0, 1.0)]
