import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Any

import requests

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_PARTNER_ID = "lazop-sdk-go-20230910"

REGION_BASE_MAP = {
    "SG": "https://api.lazada.sg/rest",
    "MY": "https://api.lazada.com.my/rest",
    "VN": "https://api.lazada.vn/rest",
    "TH": "https://api.lazada.co.th/rest",
    "PH": "https://api.lazada.com.ph/rest",
    "ID": "https://api.lazada.co.id/rest",
}


class LazadaConfigError(Exception):
    pass


class LazadaAPIError(Exception):
    def __init__(self, message: str, code: str | None = None, request_id: str | None = None):
        super().__init__(message)
        self.code = code
        self.request_id = request_id


@dataclass
class LazadaConfig:
    app_key: str
    app_secret: str
    access_token: str
    region: str
    api_base: str
    partner_id: str

    @classmethod
    def from_env(cls) -> "LazadaConfig":
        app_key = os.environ.get("BOLTY_LAZADA_APP_KEY", "").strip()
        app_secret = os.environ.get("BOLTY_LAZADA_APP_SECRET", "").strip()
        access_token = os.environ.get("BOLTY_LAZADA_ACCESS_TOKEN", "").strip()
        region = (os.environ.get("BOLTY_LAZADA_REGION", "MY").strip() or "MY").upper()
        api_base = os.environ.get("BOLTY_LAZADA_API_BASE", "").strip() or REGION_BASE_MAP.get(region, "")
        partner_id = os.environ.get("BOLTY_LAZADA_PARTNER_ID", DEFAULT_PARTNER_ID).strip() or DEFAULT_PARTNER_ID

        missing = []
        if not app_key:
            missing.append("BOLTY_LAZADA_APP_KEY")
        if not app_secret:
            missing.append("BOLTY_LAZADA_APP_SECRET")
        if not access_token:
            missing.append("BOLTY_LAZADA_ACCESS_TOKEN")
        if not api_base:
            missing.append("BOLTY_LAZADA_API_BASE or valid BOLTY_LAZADA_REGION")

        if missing:
            raise LazadaConfigError(f"Missing required Lazada config: {', '.join(missing)}")

        return cls(
            app_key=app_key,
            app_secret=app_secret,
            access_token=access_token,
            region=region,
            api_base=api_base,
            partner_id=partner_id,
        )


def _stringify(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class LazadaClient:
    def __init__(self, config: LazadaConfig, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS):
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def _timestamp_ms(self) -> str:
        return str(int(round(time.time()))) + "000"

    def _base_params(self) -> dict[str, str]:
        return {
            "app_key": self.config.app_key,
            "access_token": self.config.access_token,
            "sign_method": "sha256",
            "timestamp": self._timestamp_ms(),
            "partner_id": self.config.partner_id,
        }

    def _sign(self, api_path: str, params: dict[str, Any]) -> str:
        keys = sorted(params.keys())
        message = [api_path]
        for key in keys:
            message.append(f"{key}{_stringify(params[key])}")
        payload = "".join(message).encode("utf-8")
        digest = hmac.new(
            self.config.app_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return digest.upper()

    def _execute(self, api_path: str, api_params: dict[str, Any], *, method: str) -> dict[str, Any]:
        params: dict[str, Any] = self._base_params()
        params.update(api_params)
        params["sign"] = self._sign(api_path, params)

        api_url = f"{self.config.api_base}{api_path}"
        request_params = {key: _stringify(value) for key, value in params.items()}

        normalized_method = method.upper()
        if normalized_method == "POST":
            response = self.session.post(api_url, data=request_params, timeout=self.timeout_seconds)
        elif normalized_method == "GET":
            response = self.session.get(api_url, params=request_params, timeout=self.timeout_seconds)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        payload = response.json()

        code = payload.get("code")

        if code not in (None, "0", 0):
            raise LazadaAPIError(
                message=payload.get("message") or "Lazada API returned non-zero code",
                code=str(code),
                request_id=payload.get("request_id"),
            )

        return payload

    def get(self, api_path: str, api_params: dict[str, Any]) -> dict[str, Any]:
        return self._execute(api_path, api_params, method="GET")

    def post(self, api_path: str, api_params: dict[str, Any]) -> dict[str, Any]:
        return self._execute(api_path, api_params, method="POST")
