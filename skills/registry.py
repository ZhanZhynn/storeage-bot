from .sqlite_upload import build_sqlite_upload_reply
from .sqlite_upload import process_sqlite_upload_message
from .query_sqlite import handle_sqlite_query_prompt


def handle_sqlite_upload_interaction(
    user_id: str,
    channel_id: str,
    thread_ts: str | None,
    text: str | None,
    file_paths: list[str] | None,
) -> tuple[bool, dict | None]:
    handled, response_text = process_sqlite_upload_message(
        user_id=user_id,
        channel_id=channel_id,
        thread_ts=thread_ts,
        text=text,
        file_paths=file_paths,
    )
    if not handled:
        return False, None

    payload = build_sqlite_upload_reply(
        user_id=user_id,
        channel_id=channel_id,
        thread_ts=thread_ts,
        response_text=response_text or "Upload request handled.",
    )
    return True, payload


def handle_sqlite_query_interaction(prompt: str | None) -> tuple[bool, dict | None]:
    handled, payload = handle_sqlite_query_prompt(prompt)
    if not handled:
        return False, None
    return True, payload


def route_skill_interaction(
    user_id: str,
    channel_id: str,
    thread_ts: str | None,
    text: str | None,
    file_paths: list[str] | None,
) -> tuple[bool, dict | None, str | None]:
    upload_handled, upload_payload = handle_sqlite_upload_interaction(
        user_id=user_id,
        channel_id=channel_id,
        thread_ts=thread_ts,
        text=text,
        file_paths=file_paths,
    )
    if upload_handled:
        return True, upload_payload, "Using SQLite upload skill"

    query_handled, query_payload = handle_sqlite_query_interaction(text)
    if query_handled:
        return True, query_payload, "Using SQLite query skill"

    return False, None, None
