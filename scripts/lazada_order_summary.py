#!/usr/bin/env python3
"""
Lazada Order Summary - Slack Cron Job Script

Fetches Lazada orders and sends summary to Slack channel.
Designed for cron jobs:
- Morning (8:30 AM): Order status counts
- Evening (5:00 PM): Daily orders + sales amount
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

MALAYSIA_TZ = timezone(timedelta(hours=8))

MORNING_STATUSES = [
    ("topack", "To Pack", ":package:"),
    ("toship", "To Ship", ":truck:"),
    ("pending", "Pending", ":hourglass_flowing_sand:"),
    ("ready_to_ship", "Ready to Ship", ":white_check_mark:"),
]

MAX_RETRIES = 3
RETRY_DELAY_BASE = 2


def get_slack_client() -> WebClient:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN environment variable not set")
    return WebClient(token=token)


def fetch_orders_summary(days: int = 1, date: str | None = None) -> dict:
    """Fetch order summary using efficient single CLI call with retry logic."""
    last_error = None

    for attempt in range(MAX_RETRIES):
        cmd = [
            sys.executable,
            "-m",
            "platform_helpers.lazada.cli",
            "orders",
            "summary",
            "--days", str(days),
            "--short",
        ]
        if date:
            cmd.extend(["--date", date])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if data.get("ok", False):
                    return data
                last_error = data.get("error", "Unknown error")
            except json.JSONDecodeError as e:
                last_error = f"JSON parse error: {e}"
        else:
            last_error = result.stderr or f"Exit code: {result.returncode}"

        print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {last_error}", file=sys.stderr)

        if attempt < MAX_RETRIES - 1:
            wait_time = (RETRY_DELAY_BASE ** attempt) + random.uniform(0.5, 1.0)
            print(f"Retrying in {wait_time:.1f}s...", file=sys.stderr)
            time.sleep(wait_time)

    print(f"All {MAX_RETRIES} attempts failed", file=sys.stderr)
    return {"ok": False, "error": last_error}


def format_morning_message(status_breakdown: dict, error: str | None = None) -> str:
    """Format Slack message for morning summary."""
    today = datetime.now(MALAYSIA_TZ).strftime("%Y-%m-%d")

    if error:
        lines = [
            f":warning: *Morning Order Summary Error* :warning:",
            "",
            f"```Error: {error}```",
            "",
            "Please check the logs for details.",
        ]
        return "\n".join(lines)

    lines = [
        f":sunrise: *Good Morning! Here's your Lazada orders summary for {today}* :sunrise:",
        "",
    ]

    total = 0
    for status, label, emoji in MORNING_STATUSES:
        count = status_breakdown.get(status, 0)
        total += count
        lines.append(f"{emoji} *{label}:* {count} orders")

    if total == 0:
        lines.extend(["", ":wave: All caught up! No pending orders."])
    else:
        lines.extend(["", f":muscle: *Total needing attention: {total} orders*"])

    return "\n".join(lines)


def format_evening_message(total_orders: int, total_sales: float, date: str, error: str | None = None) -> str:
    """Format Slack message for evening summary."""
    date_formatted = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")

    if error:
        lines = [
            f":warning: *Evening Order Summary Error* :warning:",
            "",
            f"```Error: {error}```",
            "",
            "Please check the logs for details.",
        ]
        return "\n".join(lines)

    lines = [
        f":city_sunset: *Good Evening! Lazada Daily Summary for {date_formatted}* :city_sunset:",
        "",
        f":shopping_trolley: *Orders created today:* {total_orders} orders",
        f":money_with_wings: *Total sales:* RM {total_sales:,.2f}",
        "",
    ]

    if total_orders == 0:
        lines.append(":zzz: No orders today. Rest up for tomorrow!")
    else:
        lines.append(":rocket: Keep up the great work! :rocket:")

    return "\n".join(lines)


def send_slack_message(client: WebClient, channel: str, text: str) -> None:
    """Send message to Slack channel."""
    try:
        client.chat_postMessage(channel=channel, text=text)
        print(f"Message sent to {channel}")
    except SlackApiError as e:
        print(f"Error sending message: {e}", file=sys.stderr)
        raise


def run_morning(channel: str) -> None:
    """Run morning summary - fetch orders by status."""
    print("Running morning summary with orders summary CLI...")

    result = fetch_orders_summary(days=1)
    error = result.get("error") if not result.get("ok", True) else None
    status_breakdown = result.get("status_breakdown", {})

    for status, _, _ in MORNING_STATUSES:
        print(f"  {status}: {status_breakdown.get(status, 0)} orders")

    message = format_morning_message(status_breakdown, error)
    client = get_slack_client()
    send_slack_message(client, channel, message)
    print("Morning summary complete!")


def run_evening(channel: str) -> None:
    """Run evening summary - fetch daily orders and sales."""
    print("Running evening summary with orders summary CLI...")

    today = datetime.now(MALAYSIA_TZ).strftime("%Y-%m-%d")
    result = fetch_orders_summary(days=1)
    error = result.get("error") if not result.get("ok", True) else None

    total_orders = result.get("total_orders", 0)
    total_sales = result.get("total_sales", 0.0)

    print(f"  Orders today: {total_orders}")
    print(f"  Sales amount: RM {total_sales:,.2f}")

    message = format_evening_message(total_orders, total_sales, today, error)
    client = get_slack_client()
    send_slack_message(client, channel, message)
    print("Evening summary complete!")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lazada Order Summary - Slack Cron Job Script"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["morning", "evening"],
        help="Summary mode: morning or evening",
    )
    parser.add_argument(
        "--channel",
        required=True,
        help="Slack channel ID (e.g., C123456789)",
    )
    parser.add_argument(
        "--date",
        help="Optional date (YYYY-MM-DD), defaults to today",
    )

    args = parser.parse_args()

    try:
        if args.mode == "morning":
            run_morning(args.channel)
        else:
            run_evening(args.channel)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
