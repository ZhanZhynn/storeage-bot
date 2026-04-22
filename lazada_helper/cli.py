"""Backward-compatibility shim for lazada_helper.cli.

Delegates to platform_helpers.lazada.cli.
"""

from platform_helpers.lazada.cli import main, _build_parser  # noqa: F401

if __name__ == "__main__":
    raise SystemExit(main())
