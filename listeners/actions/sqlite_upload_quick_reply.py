from logging import Logger

from slack_bolt import Ack, Respond
from slack_sdk import WebClient

from ..listener_utils.sqlite_upload_flow import (
    build_sqlite_upload_reply,
    process_sqlite_upload_message,
)


def sqlite_upload_quick_reply_callback(
    ack: Ack,
    body: dict,
    respond: Respond,
    client: WebClient,
    logger: Logger,
):
    try:
        ack()

        action = (body.get("actions") or [{}])[0]
        command_text = (action.get("value") or "").strip()
        if not command_text:
            return

        applied_action = _humanize_action(command_text)
        original_text, original_blocks = _without_actions_block(
            body.get("message") or {},
            applied_action,
        )
        respond(
            replace_original=True,
            text=original_text,
            blocks=original_blocks,
        )

        user_id = body.get("user", {}).get("id")
        channel_id = body.get("channel", {}).get("id")
        container = body.get("container", {})
        thread_ts = container.get("thread_ts") or body.get("message", {}).get("thread_ts")

        upload_handled, upload_response = process_sqlite_upload_message(
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
            text=command_text,
            file_paths=None,
        )

        if upload_handled:
            reply_payload = build_sqlite_upload_reply(
                user_id=user_id,
                channel_id=channel_id,
                thread_ts=thread_ts,
                response_text=upload_response or "Upload request handled.",
            )
            message_ts = (body.get("message") or {}).get("ts")
            target_thread_ts = thread_ts or message_ts
            client.chat_postMessage(
                channel=channel_id,
                text=reply_payload["text"],
                blocks=reply_payload.get("blocks"),
                thread_ts=target_thread_ts,
            )
    except Exception as error:
        logger.error(error)


def _without_actions_block(message: dict, applied_action: str) -> tuple[str, list[dict]]:
    text = (message.get("text") or "SQLite upload action received.").strip()
    existing_blocks = message.get("blocks") or []
    blocks = [block for block in existing_blocks if block.get("type") != "actions"]
    if not blocks:
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Action applied: {applied_action}",
                }
            ],
        }
    )
    return text, blocks


def _humanize_action(command_text: str) -> str:
    lowered = command_text.lower()
    if lowered.startswith("create table "):
        return command_text
    if lowered == "confirm upload":
        return "confirm upload"
    if lowered == "mode shared":
        return "use shared mode"
    if lowered == "cancel":
        return "cancel"
    return command_text
