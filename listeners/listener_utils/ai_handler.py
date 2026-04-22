"""Shared AI response handler.

Extracts the common AI-response flow used by both ``app_mentioned`` and
``app_messaged`` event listeners into a single reusable function so that
logic changes only need to happen in one place.
"""

from __future__ import annotations

from logging import Logger
from typing import Optional

from slack_bolt import Say
from slack_sdk import WebClient

from ai.ai_constants import DEFAULT_SYSTEM_CONTENT
from ai.providers import (
    get_opencode_sent_file_ids,
    get_provider_response,
    mark_opencode_sent_file_ids,
)

from .listener_constants import DEFAULT_LOADING_TEXT
from .parse_conversation import parse_conversation
from .slack_files import (
    cleanup_files,
    download_supported_files,
    upload_images_from_response,
    upload_spreadsheets_from_response,
)
from .slack_message import clamp_slack_text, safe_chat_update
from .slack_reactions import add_working_reaction, remove_working_reaction
from .sqlite_upload_flow import build_sqlite_upload_reply, process_sqlite_upload_message


def handle_ai_response(
    *,
    client: WebClient,
    say: Say,
    logger: Logger,
    user_id: str,
    channel_id: str,
    thread_ts: Optional[str],
    message_ts: str,
    text: Optional[str],
    event_messages: list[dict],
    system_content: str = DEFAULT_SYSTEM_CONTENT,
    in_thread: bool = False,
) -> None:
    """Run the full AI-response lifecycle for a Slack event.

    Parameters
    ----------
    client:
        Slack Web API client.
    say:
        Bolt ``say`` helper (posts messages in the channel/thread).
    logger:
        Logger instance for error reporting.
    user_id:
        Slack user who triggered the event.
    channel_id:
        Channel where the event occurred.
    thread_ts:
        Thread timestamp (``None`` for top-level messages).
    message_ts:
        Timestamp of the triggering message (used for reactions).
    text:
        The user's message text.
    event_messages:
        List of Slack message dicts to scan for file attachments.
    system_content:
        System prompt to prepend on the first message in a session.
    in_thread:
        Whether the event is a reply inside a thread.
    """
    file_paths: list[str] = []
    file_warnings: list[str] = []
    response_file_warnings: list[str] = []
    downloaded_file_ids: list[str] = []
    waiting_message = None
    reaction_set = False

    try:
        reaction_set = add_working_reaction(client, channel_id, message_ts)

        # --- Conversation context ---
        if in_thread and thread_ts:
            conversation = client.conversations_replies(
                channel=channel_id, ts=thread_ts, limit=10
            )["messages"]
            conversation_context = parse_conversation(conversation[:-1])
        else:
            if not thread_ts:
                thread_ts = message_ts
            conversation = []
            conversation_context = []

        conversation_id = f"{channel_id}:{thread_ts}"
        sent_file_ids = get_opencode_sent_file_ids(user_id, conversation_id)

        # --- File downloads ---
        source_messages = conversation if (in_thread and conversation) else event_messages
        file_paths, file_warnings, downloaded_file_ids = download_supported_files(
            source_messages, client.token, exclude_file_ids=sent_file_ids
        )

        # --- SQLite upload flow intercept ---
        if text:
            upload_handled, upload_response = process_sqlite_upload_message(
                user_id=user_id,
                channel_id=channel_id,
                thread_ts=thread_ts,
                text=text,
                file_paths=file_paths,
            )
            if upload_handled:
                reply_payload = build_sqlite_upload_reply(
                    user_id=user_id,
                    channel_id=channel_id,
                    thread_ts=thread_ts,
                    response_text=upload_response or "Upload request handled.",
                )
                say(
                    text=clamp_slack_text(reply_payload["text"]),
                    blocks=reply_payload.get("blocks"),
                    thread_ts=thread_ts,
                )
                return

        # --- AI provider call ---
        if text:
            waiting_message = say(text=DEFAULT_LOADING_TEXT, thread_ts=thread_ts)
            response = get_provider_response(
                user_id,
                text,
                conversation_context,
                system_content,
                conversation_id=conversation_id,
                file_paths=file_paths,
            )
            mark_opencode_sent_file_ids(user_id, conversation_id, downloaded_file_ids)

            # --- Upload generated files back to Slack ---
            upload_thread_ts = thread_ts or waiting_message["ts"]
            generated_images, image_warnings, generated_temp_paths = upload_images_from_response(
                client=client,
                channel=channel_id,
                thread_ts=upload_thread_ts,
                response_text=response,
            )
            file_paths.extend(generated_temp_paths)
            response_file_warnings.extend(image_warnings)

            generated_spreadsheets, spreadsheet_warnings, spreadsheet_temp_paths = (
                upload_spreadsheets_from_response(
                    client=client,
                    channel=channel_id,
                    thread_ts=upload_thread_ts,
                    response_text=response,
                )
            )
            file_paths.extend(spreadsheet_temp_paths)
            response_file_warnings.extend(spreadsheet_warnings)

            # --- Append warnings / upload notices ---
            if file_warnings:
                warning_text = "\n".join([f"- {w}" for w in file_warnings[:5]])
                response = f"{response}\n\nFile warnings:\n{warning_text}"
            if generated_images:
                uploaded_text = "\n".join([f"- {name}" for name in generated_images[:5]])
                response = f"{response}\n\nUploaded images:\n{uploaded_text}"
            if generated_spreadsheets:
                uploaded_text = "\n".join([f"- {name}" for name in generated_spreadsheets[:5]])
                response = f"{response}\n\nUploaded spreadsheets:\n{uploaded_text}"
            if response_file_warnings:
                warning_text = "\n".join([f"- {w}" for w in response_file_warnings[:5]])
                response = f"{response}\n\nFile upload warnings:\n{warning_text}"

            safe_chat_update(
                client=client,
                channel=channel_id,
                ts=waiting_message["ts"],
                user_id=user_id,
                text=response,
            )
        else:
            # No text — just post a nudge (for app_mention without text)
            from .listener_constants import MENTION_WITHOUT_TEXT

            nudge = MENTION_WITHOUT_TEXT
            if file_warnings:
                warning_text = "\n".join([f"- {w}" for w in file_warnings[:5]])
                nudge = f"{nudge}\n\nFile warnings:\n{warning_text}"
            say(text=clamp_slack_text(nudge), thread_ts=thread_ts)

    except Exception as e:
        logger.error(e)
        warning_text = ""
        if file_warnings or response_file_warnings:
            combined_warnings = file_warnings + response_file_warnings
            warning_text = "\n\nFile warnings:\n" + "\n".join(
                [f"- {w}" for w in combined_warnings[:5]]
            )
        if waiting_message:
            safe_chat_update(
                client=client,
                channel=channel_id,
                ts=waiting_message["ts"],
                user_id=user_id,
                text=f"Received an error from Bolty:\n{e}{warning_text}",
            )
        else:
            say(
                text=clamp_slack_text(f"Received an error from Bolty:\n{e}{warning_text}"),
                thread_ts=thread_ts,
            )
    finally:
        if reaction_set:
            remove_working_reaction(client, channel_id, message_ts)
        cleanup_files(file_paths)
