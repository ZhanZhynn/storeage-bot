"""Backward-compatibility shim for lazada_helper.safe_run.

Delegates to platform_helpers.lazada.safe_run.
"""

from platform_helpers.lazada.safe_run import main  # noqa: F401

if __name__ == "__main__":
    raise SystemExit(main())
