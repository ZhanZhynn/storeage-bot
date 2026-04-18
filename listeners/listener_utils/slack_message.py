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


def _format_markdown_tables_for_slack(text: str) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    output = []
    index = 0
    while index < len(lines):
        current = lines[index]
        if _is_markdown_table_header(current, lines, index):
            end = index + 2
            while end < len(lines) and _looks_like_table_row(lines[end]):
                end += 1

            table_lines = lines[index:end]
            rendered = _render_markdown_table_as_code_block(table_lines)
            if rendered:
                output.append(rendered)
                index = end
                continue

        output.append(current)
        index += 1

    return "\n".join(output)


def _is_markdown_table_header(line: str, lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False

    if not _looks_like_table_row(line):
        return False

    separator = lines[index + 1].strip()
    return bool(re.match(r"^\|?\s*[:\-]+(?:\s*\|\s*[:\-]+)+\s*\|?$", separator))


def _looks_like_table_row(line: str) -> bool:
    stripped = (line or "").strip()
    return stripped.count("|") >= 2


def _render_markdown_table_as_code_block(table_lines: list[str]) -> str:
    if len(table_lines) < 2:
        return ""

    raw_rows = []
    for line in table_lines:
        row = [cell.strip() for cell in line.strip().strip("|").split("|")]
        raw_rows.append(row)

    if len(raw_rows) < 2:
        return ""

    header = raw_rows[0]
    body = raw_rows[2:]

    column_count = len(header)
    if column_count == 0:
        return ""

    normalized_rows = []
    for row in [header] + body:
        fixed = row[:column_count] + [""] * max(0, column_count - len(row))
        normalized_rows.append([_truncate_cell(cell) for cell in fixed])

    widths = [0] * column_count
    for row in normalized_rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))

    formatted_rows = []
    formatted_rows.append(_format_row(normalized_rows[0], widths))
    formatted_rows.append("-+-".join(["-" * width for width in widths]))
    for row in normalized_rows[1:]:
        formatted_rows.append(_format_row(row, widths))

    return "```\n" + "\n".join(formatted_rows) + "\n```"


def _format_row(row: list[str], widths: list[int]) -> str:
    padded = [value.ljust(widths[idx]) for idx, value in enumerate(row)]
    return " | ".join(padded)


def _truncate_cell(value: str, max_len: int = 40) -> str:
    if len(value) <= max_len:
        return value
    return value[: max_len - 3].rstrip() + "..."


def summarize_for_slack(
    user_id: str, text: str, max_chars: int = SLACK_SAFE_MESSAGE_CHARS
) -> str:
    """Summarize oversized provider responses so they fit Slack limits."""
    if not text:
        return ""

    normalized = text.strip()
    if len(normalized) <= max_chars:
        formatted = _format_markdown_tables_for_slack(normalized)
        return clamp_slack_text(formatted, max_chars=max_chars)

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
        summarized = _format_markdown_tables_for_slack(summarized)
        summary_with_footer = f"{summarized}{SLACK_SUMMARIZED_FOOTER}"
        if len(summary_with_footer) <= max_chars:
            return summary_with_footer

        trimmed_summary = clamp_slack_text(summarized, max_chars=max_chars).rstrip()
        if len(trimmed_summary) + len(SLACK_SUMMARIZED_FOOTER) <= max_chars:
            return f"{trimmed_summary}{SLACK_SUMMARIZED_FOOTER}"
        return trimmed_summary
    except Exception:
        return clamp_slack_text(normalized, max_chars=max_chars)


def _split_for_slack_messages(text: str, max_chars: int = 12000) -> list[str]:
    if not text:
        return [""]

    normalized = text.strip()
    if len(normalized) <= max_chars:
        return [normalized]

    chunks: list[str] = []
    current = ""

    for line in normalized.splitlines(keepends=True):
        line = line or ""
        while len(line) > max_chars:
            head = line[:max_chars]
            line = line[max_chars:]
            if current:
                chunks.append(current.rstrip())
                current = ""
            chunks.append(head.rstrip())

        if not line:
            continue

        if len(current) + len(line) <= max_chars:
            current += line
            continue

        if current:
            chunks.append(current.rstrip())
        current = line

    if current:
        chunks.append(current.rstrip())

    return [chunk for chunk in chunks if chunk]


def _get_slack_error_code(error) -> str:
    response = getattr(error, "response", None)
    if response is None:
        return ""

    try:
        if hasattr(response, "data") and isinstance(response.data, dict):
            return str(response.data.get("error", "") or "")
    except Exception:
        pass

    try:
        return str(response.get("error", "") or "")
    except Exception:
        return ""


def safe_chat_update(client, channel: str, ts: str, user_id: str, text: str):
    """Update a Slack message with retry logic for message length limits."""
    prepared = summarize_for_slack(user_id, text)
    try:
        return client.chat_update(channel=channel, ts=ts, text=prepared)
    except Exception as error:
        error_code = _get_slack_error_code(error)

        if error_code != "msg_too_long":
            raise

        chunk_limit = 3000
        min_chunk_limit = 800

        while True:
            chunks = _split_for_slack_messages(prepared, max_chars=chunk_limit)
            if not chunks:
                chunks = [clamp_slack_text(prepared, max_chars=chunk_limit)]

            first_message = chunks[0]
            if len(chunks) > 1:
                first_message = (
                    f"{first_message}\n\n"
                    f"_(Long response split into {len(chunks)} messages for reliability.)_"
                )
                first_message = clamp_slack_text(first_message, max_chars=chunk_limit)

            try:
                update_response = client.chat_update(channel=channel, ts=ts, text=first_message)
            except Exception as update_error:
                update_error_code = _get_slack_error_code(update_error)
                if update_error_code == "msg_too_long" and chunk_limit > min_chunk_limit:
                    chunk_limit = max(min_chunk_limit, chunk_limit // 2)
                    continue
                raise

            for idx, chunk in enumerate(chunks[1:], start=2):
                prefix = f"*Part {idx}/{len(chunks)}*\n"
                remaining = max(200, chunk_limit - len(prefix))
                safe_chunk = clamp_slack_text(chunk, max_chars=remaining)
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=ts,
                    text=f"{prefix}{safe_chunk}",
                )

            return update_response
