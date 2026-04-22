import os

DEFAULT_LAZADA_REGION = "MY"
DEFAULT_LAZADA_API_BASE = "https://api.lazada.com.my/rest"
DEFAULT_LAZADA_SDK_PATH = "/home/hee/Downloads/iop-sdk-go"


def build_lazada_context() -> str:
    app_key = os.environ.get("BOLTY_LAZADA_APP_KEY", "").strip()
    app_secret = os.environ.get("BOLTY_LAZADA_APP_SECRET", "").strip()
    access_token = os.environ.get("BOLTY_LAZADA_ACCESS_TOKEN", "").strip()
    region = os.environ.get("BOLTY_LAZADA_REGION", DEFAULT_LAZADA_REGION).strip() or DEFAULT_LAZADA_REGION
    api_base = os.environ.get("BOLTY_LAZADA_API_BASE", DEFAULT_LAZADA_API_BASE).strip() or DEFAULT_LAZADA_API_BASE
    sdk_path = os.environ.get("BOLTY_LAZADA_SDK_PATH", DEFAULT_LAZADA_SDK_PATH).strip() or DEFAULT_LAZADA_SDK_PATH

    key_ready = "yes" if bool(app_key) else "no"
    secret_ready = "yes" if bool(app_secret) else "no"
    token_ready = "yes" if bool(access_token) else "no"

    return (
        "Lazada API configuration hint (auto-generated):\n"
        "Use these values for Lazada API calls and do not ask the user to repeat credentials unless missing.\n"
        f"- Env var `BOLTY_LAZADA_APP_KEY` configured: `{key_ready}`\n"
        f"- Env var `BOLTY_LAZADA_APP_SECRET` configured: `{secret_ready}`\n"
        f"- Env var `BOLTY_LAZADA_ACCESS_TOKEN` configured: `{token_ready}`\n"
        f"- Region (`BOLTY_LAZADA_REGION`): `{region}`\n"
        f"- API base (`BOLTY_LAZADA_API_BASE`): `{api_base}`\n"
        f"- SDK path (`BOLTY_LAZADA_SDK_PATH`): `{sdk_path}`\n"
        "If required credentials are missing, ask specifically for the missing value(s) only."
    )
