from pathlib import Path
import sqlite3

import pandas as pd

from listeners.listener_utils import sqlite_upload_flow


def test_process_sqlite_upload_message_auto_uses_shopee_normalization(
    tmp_path: Path,
    monkeypatch,
):
    csv_path = tmp_path / "shopee_orders.csv"
    db_path = tmp_path / "bolty.db"
    pd.DataFrame(
        [
            {
                "Order ID": "ORD-1",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-01 10:00",
                "Order Paid Time": "2026-03-01 10:05",
                "SKU Reference No.": "SKU-1",
                "Quantity": "1",
                "Deal Price": "12.00",
                "Seller Discount": "0.50",
                "Transaction Fee": "1.00",
                "Buyer Paid Shipping Fee": "5.00",
                "Grand Total": "20.00",
            },
            {
                "Order ID": "ORD-1",
                "Order Status": "Completed",
                "Order Creation Date": "2026-03-01 10:00",
                "Order Paid Time": "2026-03-01 10:05",
                "SKU Reference No.": "SKU-2",
                "Quantity": "2",
                "Deal Price": "6.00",
                "Seller Discount": "0.00",
                "Transaction Fee": "9.99",
                "Buyer Paid Shipping Fee": "99.00",
                "Grand Total": "999.00",
            },
        ]
    ).to_csv(csv_path, index=False)

    monkeypatch.setenv("BOLTY_SQLITE_DB_PATH", str(db_path))
    monkeypatch.setattr(sqlite_upload_flow, "UPLOAD_SESSION_STORE", tmp_path / "sessions.json")
    monkeypatch.setattr(sqlite_upload_flow, "UPLOAD_FILE_DIR", tmp_path / "uploads")

    handled, first_response = sqlite_upload_flow.process_sqlite_upload_message(
        user_id="U1",
        channel_id="C1",
        thread_ts="T1",
        text="upload to sqlite",
        file_paths=[str(csv_path)],
    )

    assert handled is True
    assert first_response is not None
    assert "Shopee orders normalization" in first_response

    handled, second_response = sqlite_upload_flow.process_sqlite_upload_message(
        user_id="U1",
        channel_id="C1",
        thread_ts="T1",
        text="confirm upload",
        file_paths=None,
    )

    assert handled is True
    assert second_response is not None
    assert "Shopee orders upload complete" in second_response
    assert "`orders`" in second_response
    assert "`order_items`" in second_response
    assert "Data health check:" in second_response
    assert "Orphaned orders:" in second_response
    assert "NULL grand_total:" in second_response
    assert "NULL transaction_fee:" in second_response

    with sqlite3.connect(db_path) as connection:
        orders_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        items_count = connection.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]
        order_values = connection.execute(
            "SELECT order_id, transaction_fee, buyer_paid_shipping_fee, grand_total FROM orders"
        ).fetchall()
        item_values = connection.execute(
            "SELECT order_id, deal_price, seller_discount FROM order_items ORDER BY deal_price DESC"
        ).fetchall()

    assert orders_count == 1
    assert items_count == 2
    assert order_values == [("ORD-1", 1.0, 5.0, 20.0)]
    assert item_values == [
        ("ORD-1", 12.0, 0.5),
        ("ORD-1", 6.0, 0.0),
    ]


def test_process_sqlite_upload_message_non_shopee_keeps_generic_flow(
    tmp_path: Path,
    monkeypatch,
):
    csv_path = tmp_path / "generic.csv"
    pd.DataFrame([{"id": 1, "amount": 10.0}]).to_csv(csv_path, index=False)

    monkeypatch.setenv("BOLTY_SQLITE_DB_PATH", str(tmp_path / "bolty.db"))
    monkeypatch.setattr(sqlite_upload_flow, "UPLOAD_SESSION_STORE", tmp_path / "sessions.json")
    monkeypatch.setattr(sqlite_upload_flow, "UPLOAD_FILE_DIR", tmp_path / "uploads")

    handled, response = sqlite_upload_flow.process_sqlite_upload_message(
        user_id="U2",
        channel_id="C2",
        thread_ts="T2",
        text="upload to sqlite",
        file_paths=[str(csv_path)],
    )

    assert handled is True
    assert response is not None
    assert "Which SQLite table should I upload to?" in response
