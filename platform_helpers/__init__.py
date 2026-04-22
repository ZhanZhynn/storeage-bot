"""Platform helpers package.

Each sub-package (lazada, shopee, …) exposes a deterministic CLI for
interacting with marketplace APIs.  The ``registry`` module provides
auto-discovery so the AI layer can inject context for whichever
platforms are configured.
"""

from .registry import get_platform, get_all_platforms, get_matching_platforms

__all__ = ["get_platform", "get_all_platforms", "get_matching_platforms"]
