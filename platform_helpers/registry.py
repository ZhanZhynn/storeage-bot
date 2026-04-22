"""Platform helper registry.

Provides a simple registry of marketplace platform helpers so that the
AI context layer and skill matcher can dynamically support any registered
platform without hard-coding each one.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass(frozen=True)
class PlatformHelper:
    """Descriptor for a marketplace platform helper."""

    name: str
    display_name: str
    cli_module: str          # e.g. "platform_helpers.lazada.cli"
    safe_run_module: str     # e.g. "platform_helpers.lazada.safe_run"
    context_builder: Callable[[], str]
    keywords: tuple[str, ...]
    env_prefix: str          # e.g. "BOLTY_LAZADA_"
    required_env_vars: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Built-in platform context builders
# ---------------------------------------------------------------------------

def _build_lazada_context() -> str:
    """Build Lazada API configuration hint from environment."""
    from .lazada.client import REGION_BASE_MAP

    prefix = "BOLTY_LAZADA_"
    app_key = os.environ.get(f"{prefix}APP_KEY", "").strip()
    app_secret = os.environ.get(f"{prefix}APP_SECRET", "").strip()
    access_token = os.environ.get(f"{prefix}ACCESS_TOKEN", "").strip()
    region = (os.environ.get(f"{prefix}REGION", "MY").strip() or "MY").upper()
    api_base = (
        os.environ.get(f"{prefix}API_BASE", "").strip()
        or REGION_BASE_MAP.get(region, "")
    )

    key_ready = "yes" if app_key else "no"
    secret_ready = "yes" if app_secret else "no"
    token_ready = "yes" if access_token else "no"

    return (
        "Lazada API configuration hint (auto-generated):\n"
        "Use these values for Lazada API calls and do not ask the user to repeat credentials unless missing.\n"
        f"- Env var `{prefix}APP_KEY` configured: `{key_ready}`\n"
        f"- Env var `{prefix}APP_SECRET` configured: `{secret_ready}`\n"
        f"- Env var `{prefix}ACCESS_TOKEN` configured: `{token_ready}`\n"
        f"- Region (`{prefix}REGION`): `{region}`\n"
        f"- API base (`{prefix}API_BASE`): `{api_base}`\n"
        "If required credentials are missing, ask specifically for the missing value(s) only.\n"
        "Use `python3 -m platform_helpers.lazada.cli` for deterministic Lazada API calls.\n"
        "Use `python3 -m platform_helpers.lazada.safe_run` for bot/tool-safe execution."
    )


def _build_shopee_context() -> str:
    """Build Shopee API configuration hint from environment (placeholder)."""
    prefix = "BOLTY_SHOPEE_"
    partner_id = os.environ.get(f"{prefix}PARTNER_ID", "").strip()
    partner_key = os.environ.get(f"{prefix}PARTNER_KEY", "").strip()
    shop_id = os.environ.get(f"{prefix}SHOP_ID", "").strip()
    access_token = os.environ.get(f"{prefix}ACCESS_TOKEN", "").strip()

    pid_ready = "yes" if partner_id else "no"
    key_ready = "yes" if partner_key else "no"
    shop_ready = "yes" if shop_id else "no"
    token_ready = "yes" if access_token else "no"

    return (
        "Shopee API configuration hint (auto-generated):\n"
        "Use these values for Shopee API calls and do not ask the user to repeat credentials unless missing.\n"
        f"- Env var `{prefix}PARTNER_ID` configured: `{pid_ready}`\n"
        f"- Env var `{prefix}PARTNER_KEY` configured: `{key_ready}`\n"
        f"- Env var `{prefix}SHOP_ID` configured: `{shop_ready}`\n"
        f"- Env var `{prefix}ACCESS_TOKEN` configured: `{token_ready}`\n"
        "If required credentials are missing, ask specifically for the missing value(s) only."
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_PLATFORMS: dict[str, PlatformHelper] = {}


def _register_builtin_platforms() -> None:
    """Register all built-in platform helpers."""
    _PLATFORMS["lazada"] = PlatformHelper(
        name="lazada",
        display_name="Lazada",
        cli_module="platform_helpers.lazada.cli",
        safe_run_module="platform_helpers.lazada.safe_run",
        context_builder=_build_lazada_context,
        keywords=(
            "lazada",
            "orders",
            "order",
            "products",
            "product",
            "finance",
            "returns",
            "return",
            "refunds",
            "refund",
            "review",
            "reviews",
            "reverse",
            "returns-refunds",
            "seller",
            "getorders",
            "getproducts",
        ),
        env_prefix="BOLTY_LAZADA_",
        required_env_vars=(
            "BOLTY_LAZADA_APP_KEY",
            "BOLTY_LAZADA_APP_SECRET",
            "BOLTY_LAZADA_ACCESS_TOKEN",
        ),
    )

    _PLATFORMS["shopee"] = PlatformHelper(
        name="shopee",
        display_name="Shopee",
        cli_module="platform_helpers.shopee.cli",
        safe_run_module="platform_helpers.shopee.safe_run",
        context_builder=_build_shopee_context,
        keywords=(
            "shopee",
            "shopee orders",
            "shopee products",
            "shopee finance",
            "shopee returns",
        ),
        env_prefix="BOLTY_SHOPEE_",
        required_env_vars=(
            "BOLTY_SHOPEE_PARTNER_ID",
            "BOLTY_SHOPEE_PARTNER_KEY",
            "BOLTY_SHOPEE_SHOP_ID",
            "BOLTY_SHOPEE_ACCESS_TOKEN",
        ),
    )


def get_platform(name: str) -> Optional[PlatformHelper]:
    """Get a platform helper by name."""
    if not _PLATFORMS:
        _register_builtin_platforms()
    return _PLATFORMS.get(name.lower())


def get_all_platforms() -> dict[str, PlatformHelper]:
    """Get all registered platform helpers."""
    if not _PLATFORMS:
        _register_builtin_platforms()
    return dict(_PLATFORMS)


def get_matching_platforms(prompt: str) -> list[PlatformHelper]:
    """Return platforms whose keywords match the given prompt."""
    if not _PLATFORMS:
        _register_builtin_platforms()

    lowered = (prompt or "").lower()
    matches = []
    for platform in _PLATFORMS.values():
        if any(keyword in lowered for keyword in platform.keywords):
            matches.append(platform)
    return matches
