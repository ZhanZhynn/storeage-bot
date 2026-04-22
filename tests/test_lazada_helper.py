import json

from lazada_helper.cli import main
from lazada_helper.safe_run import main as safe_run_main
from lazada_helper.client import LazadaClient
from lazada_helper.client import LazadaConfig
from lazada_helper.client import LazadaAPIError


def test_cli_reports_missing_config(monkeypatch, capsys):
    monkeypatch.delenv("BOLTY_LAZADA_APP_KEY", raising=False)
    monkeypatch.delenv("BOLTY_LAZADA_APP_SECRET", raising=False)
    monkeypatch.delenv("BOLTY_LAZADA_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("BOLTY_LAZADA_API_BASE", raising=False)
    monkeypatch.delenv("BOLTY_LAZADA_REGION", raising=False)

    exit_code = main(["orders", "get"])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["status"] == "config_error"


def test_lazada_client_sign_matches_known_vector():
    config = LazadaConfig(
        app_key="12345678",
        app_secret="testsecret",
        access_token="token",
        region="MY",
        api_base="https://api.lazada.com.my/rest",
        partner_id="lazop-sdk-go-20230910",
    )
    client = LazadaClient(config)
    params = {
        "app_key": "12345678",
        "access_token": "token",
        "limit": 10,
        "offset": 0,
        "sign_method": "sha256",
        "sort_by": "updated_at",
        "sort_direction": "DESC",
        "status": "all",
        "timestamp": "1776784389420",
    }
    signature = client._sign("/orders/get", params)

    assert isinstance(signature, str)
    assert len(signature) == 64
    assert signature == signature.upper()


def test_cli_orders_get_uses_default_days_window(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-1",
                "data": {
                    "orders": [],
                    "countTotal": 0,
                },
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(["orders", "get", "--days", "7"])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "orders"
    assert payload["action"] == "get"
    assert payload["total_fetched"] == 0
    assert payload["filters"]["created_after"] is not None
    assert payload["filters"]["created_before"] is not None


def test_cli_finance_transaction_details_get(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-FIN-1",
                "data": {
                    "details": {
                        "transaction_number": "TXN-1001",
                        "amount": "12.34",
                    }
                },
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(["finance", "transaction-details-get", "--transaction-number", "TXN-1001"])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "finance"
    assert payload["action"] == "transaction-details-get"
    assert payload["details"]["transaction_number"] == "TXN-1001"


def test_cli_finance_payout_status_get(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-FIN-2",
                "data": {
                    "payouts": [{"payout_id": "P1"}],
                    "countTotal": 1,
                },
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(
        [
            "finance",
            "payout-status-get",
            "--created-after",
            "2026-04-01T00:00:00+00:00",
            "--created-before",
            "2026-04-21T00:00:00+00:00",
            "--limit",
            "50",
        ]
    )
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "finance"
    assert payload["action"] == "payout-status-get"
    assert payload["endpoint"] == "/finance/payout/status/get"
    assert payload["total_fetched"] == 1
    assert payload["payouts"][0]["payout_id"] == "P1"


def test_cli_products_get(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-PROD-1",
                "data": {
                    "products": [{"item_id": "I1"}],
                    "total_products": 1,
                },
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(["products", "get", "--limit", "50"])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "products"
    assert payload["action"] == "get"
    assert payload["endpoint"] == "/products/get"
    assert payload["products"][0]["item_id"] == "I1"


def test_cli_returns_refunds_reason_list(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-RR-1",
                "data": {
                    "reasons": [{"reason_id": "R1"}],
                },
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(["returns-refunds", "reason-list"])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "returns-refunds"
    assert payload["action"] == "reason-list"
    assert payload["endpoint"] == "/order/reverse/reason/list"
    assert payload["reasons"][0]["reason_id"] == "R1"


def test_cli_reviews_seller_list_v2(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-REV-1",
                "data": {
                    "review_list": [{"review_id": "RV1"}],
                },
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(
        [
            "reviews",
            "seller-list-v2",
            "--item-id",
            "123456789",
        ]
    )
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "reviews"
    assert payload["action"] == "seller-list-v2"
    assert payload["endpoint"] == "/review/seller/list/v2"
    assert payload["reviews"][0]["review_id"] == "RV1"


def test_cli_reviews_seller_history_list(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-REV-H1",
                "data": {
                    "reviews": [{"review_id": "RH1"}],
                    "countTotal": 1,
                },
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(
        [
            "reviews",
            "seller-history-list",
            "--created-after",
            "2026-04-01T00:00:00+00:00",
            "--created-before",
            "2026-04-21T00:00:00+00:00",
            "--item-id",
            "123456789",
            "--current",
            "1",
            "--limit",
            "50",
        ]
    )
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "reviews"
    assert payload["action"] == "seller-history-list"
    assert payload["endpoint"] == "/review/seller/history/list"
    assert payload["reviews"][0]["review_id"] == "RH1"


def test_cli_reviews_get_item_reviews_includes_item_breakdown(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeSession:
        def __init__(self):
            self._calls = []

        def get(self, url, _params, timeout):
            assert timeout == 30
            self._calls.append(url)

            if "/orders/get" in url:
                return FakeResponse(
                    {
                        "code": "0",
                        "request_id": "RID-ORD-1",
                        "data": {
                            "orders": [
                                {
                                    "order_id": "O1",
                                    "items": [
                                        {"item_id": "I1"},
                                        {"item_id": "I2"},
                                    ],
                                }
                            ],
                            "countTotal": 1,
                        },
                    }
                )

            if "/review/seller/history/list" in url and "item_id=I1" in url:
                return FakeResponse(
                    {
                        "code": "0",
                        "request_id": "RID-H-I1",
                        "data": {"reviews": [{"review_id": "R-I1-1"}]},
                    }
                )

            if "/review/seller/history/list" in url and "item_id=I2" in url:
                return FakeResponse(
                    {
                        "code": "0",
                        "request_id": "RID-H-I2",
                        "data": {"reviews": []},
                    }
                )

            raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(["reviews", "get-item-reviews", "--days", "7"])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["domain"] == "reviews"
    assert payload["action"] == "get-item-reviews"
    assert payload["items_processed"] == 2
    assert payload["total_fetched"] == 3
    assert payload["request_ids"] == ["RID-H-I1", "RID-H-I2"]
    assert payload["item_breakdown"] == [
        {"item_id": "I1", "reviews_fetched": 1, "request_ids": ["RID-H-I1"]},
        {"item_id": "I2", "reviews_fetched": 0, "request_ids": ["RID-H-I2"]},
    ]


def test_cli_reviews_get_item_reviews_continues_on_item_api_error(monkeypatch, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeSession:
        def get(self, url, _params, timeout):
            assert timeout == 30

            if "/orders/get" in url:
                return FakeResponse(
                    {
                        "code": "0",
                        "request_id": "RID-ORD-2",
                        "data": {
                            "orders": [
                                {"order_id": "O2", "items": [{"item_id": "I1"}, {"item_id": "I2"}]}
                            ],
                            "countTotal": 1,
                        },
                    }
                )

            if "/review/seller/history/list" in url and "item_id=I1" in url:
                raise LazadaAPIError("MissingParameter", code="MissingParameter", request_id="RID-ERR-I1")

            if "/review/seller/history/list" in url and "item_id=I2" in url:
                return FakeResponse(
                    {
                        "code": "0",
                        "request_id": "RID-H-I2",
                        "data": {"reviews": [{"review_id": "R-I2-1"}]},
                    }
                )

            raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    exit_code = main(["reviews", "get-item-reviews", "--days", "7"])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["items_processed"] == 2
    assert payload["total_fetched"] == 3
    assert payload["item_breakdown"] == [
        {
            "item_id": "I1",
            "reviews_fetched": 0,
            "request_ids": [],
            "status": "api_error",
            "error": "MissingParameter",
            "api_code": "MissingParameter",
            "api_request_id": "RID-ERR-I1",
        },
        {"item_id": "I2", "reviews_fetched": 1, "request_ids": ["RID-H-I2"]},
    ]


def test_safe_run_returns_wrapper_error_when_no_command(capsys):
    exit_code = safe_run_main([])
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["status"] == "wrapper_error"


def test_safe_run_supports_save_json(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "k")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "s")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "t")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "MY")

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "code": "0",
                "request_id": "RID-SAFE-1",
                "data": {"orders": [], "countTotal": 0},
            }

    class FakeSession:
        def get(self, _url, _params, timeout):
            assert timeout == 30
            return FakeResponse()

    monkeypatch.setattr("platform_helpers.lazada.client.requests.Session", lambda: FakeSession())

    save_file = tmp_path / "orders.json"
    exit_code = safe_run_main(
        [
            "--save-json",
            str(save_file),
            "--",
            "orders",
            "get",
            "--days",
            "1",
            "--limit",
            "10",
        ]
    )
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["saved_json_path"] == str(save_file.resolve())
    assert save_file.exists()
