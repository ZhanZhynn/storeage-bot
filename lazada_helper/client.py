"""Backward-compatibility shim for lazada_helper.client."""

from platform_helpers.lazada.client import (  # noqa: F401
    LazadaAPIError,
    LazadaClient,
    LazadaConfig,
    LazadaConfigError,
)
