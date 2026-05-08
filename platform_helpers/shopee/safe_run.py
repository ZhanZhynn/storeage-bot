import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

from . import cli


def _invoke_cli(command_args: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = cli.main(command_args)
    return exit_code, buffer.getvalue().strip()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safe Shopee helper runner with optional save path"
    )
    parser.add_argument(
        "--save-json",
        dest="save_json",
        default=None,
        help="Optional path to save full JSON payload",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Shopee helper command arguments after --",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    command_args = [part for part in args.command if part != "--"]
    if not command_args:
        sys.stdout.write(
            json.dumps(
                {
                    "ok": False,
                    "status": "wrapper_error",
                    "error": "Missing command arguments. Example: python3 -m platform_helpers.shopee.safe_run -- orders get --days 7",
                },
                ensure_ascii=True,
            )
            + "\n"
        )
        return 1

    exit_code, output = _invoke_cli(command_args)

    try:
        payload = json.loads(output)
    except Exception:
        payload = {
            "ok": False,
            "status": "wrapper_error",
            "error": "Failed to parse platform_helpers.shopee.cli output as JSON",
            "raw_output": output,
        }
        exit_code = 1

    if args.save_json:
        save_path = Path(args.save_json).expanduser().resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
        payload["saved_json_path"] = str(save_path)

    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
