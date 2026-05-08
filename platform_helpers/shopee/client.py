import hashlib
import hmac
import os
import time
from typing import Any

import requests
from pydantic import BaseModel, ConfigDict


DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_REFRESH_WINDOW_SECONDS = 600

REGION_BASE_MAP: dict[tuple[str, str], str] = {
    ("production", "global"): "https://partner.shopeemobile.com",
    ("production", "china"): "https://openplatform.shopee.cn",
    ("production", "us"): "https://openplatform.shopee.com.br",
    ("sandbox", "global"): "https://openplatform.sandbox.test-stable.shopee.sg",
    ("sandbox", "china"): "https://openplatform.sandbox.test-stable.shopee.cn",
}


class ShopeeConfigError(Exception):
    pass


class ShopeeAPIError(Exception):
    def __init__(self, message: str, code: str | None = None, request_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.request_id = request_id


class ShopeeConfig(BaseModel):
    """Shopee API configuration from environment variables."""

    partner_id: str = ""
    partner_key: str = ""
    shop_id: str = ""
    merchant_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    access_token_expires_at: int | None = None
    environment: str = "production"
    region: str = "global"
    api_base: str = ""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
    )

    @classmethod
    def from_env(cls) -> "ShopeeConfig":
        prefix = "BOLTY_SHOPEE_"
        partner_id = os.environ.get(f"{prefix}PARTNER_ID", "").strip()
        partner_key = os.environ.get(f"{prefix}PARTNER_KEY", "").strip()
        shop_id = os.environ.get(f"{prefix}SHOP_ID", "").strip()
        merchant_id = os.environ.get(f"{prefix}MERCHANT_ID", "").strip()
        access_token = os.environ.get(f"{prefix}ACCESS_TOKEN", "").strip()
        refresh_token = os.environ.get(f"{prefix}REFRESH_TOKEN", "").strip()
        environment = (os.environ.get(f"{prefix}ENVIRONMENT", "production").strip() or "production").lower()
        region = (os.environ.get(f"{prefix}REGION", "global").strip() or "global").lower()
        api_base = os.environ.get(f"{prefix}API_BASE", "").strip()

        if not api_base:
            api_base = REGION_BASE_MAP.get((environment, region), "")

        missing = []
        if not partner_id:
            missing.append(f"{prefix}PARTNER_ID")
        elif not partner_id.isdigit():
            raise ShopeeConfigError(
                f"{prefix}PARTNER_ID must be numeric (got '{partner_id}')"
            )
        if shop_id and not shop_id.isdigit():
            raise ShopeeConfigError(
                f"{prefix}SHOP_ID must be numeric (got '{shop_id}')"
            )
        if merchant_id and not merchant_id.isdigit():
            raise ShopeeConfigError(
                f"{prefix}MERCHANT_ID must be numeric (got '{merchant_id}')"
            )
        if not partner_key:
            missing.append(f"{prefix}PARTNER_KEY")
        if not api_base:
            missing.append(f"{prefix}API_BASE or valid {prefix}ENVIRONMENT/{prefix}REGION")

        if missing:
            raise ShopeeConfigError(f"Missing required Shopee config: {', '.join(missing)}")

        return cls(
            partner_id=partner_id,
            partner_key=partner_key,
            shop_id=shop_id,
            merchant_id=merchant_id,
            access_token=access_token,
            refresh_token=refresh_token,
            environment=environment,
            region=region,
            api_base=api_base,
        )

    @property
    def partner_id_int(self) -> int:
        return int(self.partner_id)

    @property
    def shop_id_int(self) -> int | None:
        if not self.shop_id:
            return None
        return int(self.shop_id)

    @property
    def merchant_id_int(self) -> int | None:
        if not self.merchant_id:
            return None
        return int(self.merchant_id)


def _stringify(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class ShopeeClient:
    def __init__(self, config: ShopeeConfig, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS):
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self._access_token_expires_at = config.access_token_expires_at

    def _timestamp(self) -> int:
        return int(time.time())

    def _set_token_state(self, access_token: str | None, refresh_token: str | None, expire_in: int | None) -> None:
        if access_token:
            self.config.access_token = access_token
        if refresh_token:
            self.config.refresh_token = refresh_token
        if expire_in is not None:
            self._access_token_expires_at = self._timestamp() + int(expire_in)

    def _should_refresh(self) -> bool:
        if not self.config.refresh_token:
            return False
        if not self.config.access_token:
            return True
        if self._access_token_expires_at is None:
            return True
        return (self._access_token_expires_at - self._timestamp()) <= DEFAULT_REFRESH_WINDOW_SECONDS

    def _ensure_token(self, *, shop_id: str | None, merchant_id: str | None) -> None:
        if not self._should_refresh():
            return
        if not (shop_id or merchant_id):
            raise ShopeeConfigError("shop_id or merchant_id is required to refresh access token")
        payload = self.refresh_access_token(
            self.config.refresh_token,
            shop_id=shop_id,
            merchant_id=merchant_id,
        )
        response = payload.get("response") or payload
        access_token = response.get("access_token")
        refresh_token = response.get("refresh_token")
        expire_in = response.get("expire_in")
        self._set_token_state(access_token, refresh_token, expire_in)

    def _sign_base_string(
        self,
        api_path: str,
        timestamp: int,
        *,
        access_token: str | None = None,
        shop_id: str | None = None,
        merchant_id: str | None = None,
    ) -> str:
        partner_id = str(self.config.partner_id_int)
        if merchant_id:
            return f"{partner_id}{api_path}{timestamp}{access_token or ''}{int(merchant_id)}"
        if access_token and shop_id:
            return f"{partner_id}{api_path}{timestamp}{access_token}{int(shop_id)}"
        return f"{partner_id}{api_path}{timestamp}"

    def _sign(
        self,
        api_path: str,
        timestamp: int,
        *,
        access_token: str | None = None,
        shop_id: str | None = None,
        merchant_id: str | None = None,
    ) -> str:
        base = self._sign_base_string(
            api_path,
            timestamp,
            access_token=access_token,
            shop_id=shop_id,
            merchant_id=merchant_id,
        )
        digest = hmac.new(
            self.config.partner_key.encode("utf-8"),
            base.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return digest

    def _common_params(
        self,
        api_path: str,
        *,
        access_token: str | None = None,
        shop_id: str | None = None,
        merchant_id: str | None = None,
        timestamp: int | None = None,
    ) -> dict[str, Any]:
        ts = timestamp or self._timestamp()
        token = access_token if access_token is not None else (self.config.access_token or None)
        shop = shop_id if shop_id is not None else (self.config.shop_id_int)
        merchant = merchant_id if merchant_id is not None else (self.config.merchant_id_int)
        params: dict[str, Any] = {
            "partner_id": self.config.partner_id_int,
            "timestamp": ts,
        }

        if merchant is not None:
            params["merchant_id"] = merchant
        elif shop is not None:
            params["shop_id"] = shop

        if token and (merchant is not None or shop is not None):
            params["access_token"] = token

        params["sign"] = self._sign(
            api_path,
            ts,
            access_token=token,
            shop_id=shop,
            merchant_id=merchant,
        )
        return params

    def request(
        self,
        method: str,
        api_path: str,
        params: dict[str, Any] | None = None,
        *,
        access_token: str | None = None,
        shop_id: str | None = None,
        merchant_id: str | None = None,
        timestamp: int | None = None,
    ) -> dict[str, Any]:
        token_shop = shop_id if shop_id is not None else (self.config.shop_id_int)
        token_merchant = merchant_id if merchant_id is not None else (self.config.merchant_id_int)
        if token_shop or token_merchant:
            self._ensure_token(shop_id=token_shop, merchant_id=token_merchant)
        common = self._common_params(
            api_path,
            access_token=access_token,
            shop_id=shop_id,
            merchant_id=merchant_id,
            timestamp=timestamp,
        )
        api_url = f"{self.config.api_base}{api_path}"
        request_params = {key: _stringify(value) for key, value in common.items()}

        normalized_method = method.upper()
        if normalized_method == "GET":
            response = self.session.get(
                api_url,
                params={**request_params, **(params or {})},
                timeout=self.timeout_seconds,
            )
        elif normalized_method == "POST":
            response = self.session.post(
                api_url,
                params=request_params,
                json=params or {},
                timeout=self.timeout_seconds,
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        payload = response.json()

        error = payload.get("error")
        message = payload.get("message")
        request_id = payload.get("request_id")

        if error not in (None, "", 0, "0"):
            raise ShopeeAPIError(
                message=message or "Shopee API returned error",
                code=str(error),
                request_id=str(request_id) if request_id else None,
            )

        return payload

    def get(self, api_path: str, params: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.request("GET", api_path, params=params, **kwargs)

    def post(self, api_path: str, params: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        return self.request("POST", api_path, params=params, **kwargs)

    def build_auth_url(self, redirect_url: str, *, timestamp: int | None = None) -> str:
        api_path = "/api/v2/shop/auth_partner"
        ts = timestamp or self._timestamp()
        sign = self._sign(api_path, ts)
        return (
            f"{self.config.api_base}{api_path}?partner_id={self.config.partner_id_int}"
            f"&timestamp={ts}&sign={sign}&redirect={redirect_url}"
        )

    def get_access_token(
        self,
        code: str,
        *,
        shop_id: str | None = None,
        main_account_id: str | None = None,
        timestamp: int | None = None,
    ) -> dict[str, Any]:
        if not (shop_id or main_account_id):
            raise ValueError("shop_id or main_account_id is required")

        api_path = "/api/v2/auth/token/get"
        ts = timestamp or self._timestamp()
        sign = self._sign(api_path, ts)
        api_url = f"{self.config.api_base}{api_path}"
        params = {
            "partner_id": self.config.partner_id_int,
            "timestamp": ts,
            "sign": sign,
        }
        body: dict[str, Any] = {
            "code": code,
            "partner_id": self.config.partner_id_int,
        }
        if shop_id:
            body["shop_id"] = shop_id
        if main_account_id:
            body["main_account_id"] = main_account_id

        response = self.session.post(api_url, params=params, json=body, timeout=self.timeout_seconds)
        response.raise_for_status()
        payload = response.json()

        error = payload.get("error")
        if error not in (None, "", 0, "0"):
            raise ShopeeAPIError(
                message=payload.get("message") or "Shopee API returned error",
                code=str(error),
                request_id=str(payload.get("request_id")) if payload.get("request_id") else None,
            )
        response = payload.get("response") or payload
        self._set_token_state(
            response.get("access_token"),
            response.get("refresh_token"),
            response.get("expire_in"),
        )
        return payload

    def refresh_access_token(
        self,
        refresh_token: str,
        *,
        shop_id: str | None = None,
        merchant_id: str | None = None,
        timestamp: int | None = None,
    ) -> dict[str, Any]:
        if not (shop_id or merchant_id):
            raise ValueError("shop_id or merchant_id is required")

        api_path = "/api/v2/auth/access_token/get"
        ts = timestamp or self._timestamp()
        sign = self._sign(api_path, ts)
        api_url = f"{self.config.api_base}{api_path}"
        params = {
            "partner_id": self.config.partner_id_int,
            "timestamp": ts,
            "sign": sign,
        }
        body: dict[str, Any] = {
            "partner_id": self.config.partner_id_int,
            "refresh_token": refresh_token,
        }
        if shop_id:
            body["shop_id"] = shop_id
        if merchant_id:
            body["merchant_id"] = merchant_id

        response = self.session.post(api_url, params=params, json=body, timeout=self.timeout_seconds)
        response.raise_for_status()
        payload = response.json()

        error = payload.get("error")
        if error not in (None, "", 0, "0"):
            raise ShopeeAPIError(
                message=payload.get("message") or "Shopee API returned error",
                code=str(error),
                request_id=str(payload.get("request_id")) if payload.get("request_id") else None,
            )
        response = payload.get("response") or payload
        self._set_token_state(
            response.get("access_token"),
            response.get("refresh_token"),
            response.get("expire_in"),
        )
        return payload
