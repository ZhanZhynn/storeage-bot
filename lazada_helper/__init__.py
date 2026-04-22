"""Backward-compatibility shim.

All Lazada helper modules have been moved to ``platform_helpers.lazada``.
This package re-exports them so that existing ``python -m lazada_helper.cli``
invocations and any direct imports continue to work.
"""

# Re-export everything from the new location so old imports keep working.
from platform_helpers.lazada import *  # noqa: F401,F403

__all__: list[str] = []
