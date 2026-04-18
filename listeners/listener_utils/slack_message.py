import re

from ai.providers import get_provider_response

from .listener_constants import (
    SLACK_MAX_MESSAGE_CHARS,
    SLACK_SAFE_MESSAGE_CHARS,
    SLACK_SUMMARIZED_FOOTER,
)


def clamp_slack_text(text: str, max_chars: int = SLACK_SAFE_MESSAGE_CHARS) -> str:
    """Clamp message text so it safely fits Slack API limits."""
    if not text:
        return ""

    normalized = text.strip()
    if len(normalized) <= max_chars:
        return normalized

    overflow = len(normalized) - max_chars
    suffix = (
        "\n\n_(Response shortened by Bolty because Slack messages are limited "
        f"to about {SLACK_MAX_MESSAGE_CHARS:,} characters. "
        f"Trimmed {overflow:,} characters.)_"
    )
    allowed_chars = max_chars - len(suffix)
    if allowed_chars <= 0:
        return normalized[:max_chars]

    return f"{normalized[:allowed_chars].rstrip()}{suffix}"


def summarize_for_slack(
    user_id: str, text: str, max_chars: int = SLACK_SAFE_MESSAGE_CHARS
) -> str:
    """Summarize oversized provider responses so they fit Slack limits."""
    if not text:
        return ""

    normalized = text.strip()
    if len(normalized) <= max_chars:
        return normalized

    target_chars = max(1000, max_chars - len(SLACK_SUMMARIZED_FOOTER) - 800)
    summary_prompt = (
        "Summarize this assistant response for a Slack message.\n"
        f"Requirements:\n- Keep it under {target_chars} characters.\n"
        "- Keep key decisions, errors, commands, and file paths.\n"
        "- Use concise bullets when helpful.\n"
        "- Do not include a preamble.\n\n"
        "Response to summarize:\n"
        f"{normalized}"
    )

    try:
        summarized = get_provider_response(user_id, summary_prompt, context=[]).strip()
        summarized = re.sub(r"^\[model:[^\]]+\]\s*", "", summarized)
        summary_with_footer = f"{summarized}{SLACK_SUMMARIZED_FOOTER}"
        if len(summary_with_footer) <= max_chars:
            return summary_with_footer

        trimmed_summary = clamp_slack_text(summarized, max_chars=max_chars).rstrip()
        if len(trimmed_summary) + len(SLACK_SUMMARIZED_FOOTER) <= max_chars:
            return f"{trimmed_summary}{SLACK_SUMMARIZED_FOOTER}"
        return trimmed_summary
    except Exception:
        return clamp_slack_text(normalized, max_chars=max_chars)
