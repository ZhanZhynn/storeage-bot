from ai.ai_constants import DM_SYSTEM_CONTENT
from ai.providers import (
    get_opencode_sent_file_ids,
    get_provider_response,
    mark_opencode_sent_file_ids,
)
from logging import Logger
from slack_bolt import Say
from slack_sdk import WebClient
from ..listener_utils.listener_constants import DEFAULT_LOADING_TEXT
from ..listener_utils.parse_conversation import parse_conversation
from ..listener_utils.slack_files import cleanup_files, download_supported_files

"""
Handles the event when a direct message is sent to the bot, retrieves the conversation context,
and generates an AI response.
"""


def app_messaged_callback(client: WebClient, event: dict, logger: Logger, say: Say):
    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts")
    user_id = event.get("user")
    text = event.get("text")
    file_paths = []
    file_warnings = []
    waiting_message = None

    try:
        if event.get("channel_type") == "im":
            conversation_context = ""
            conversation_id = f"{channel_id}:{thread_ts or event.get('ts')}"

            if thread_ts:  # Retrieves context to continue the conversation in a thread.
                conversation = client.conversations_replies(
                    channel=channel_id, limit=10, ts=thread_ts
                )["messages"]
                conversation_context = parse_conversation(conversation[:-1])
                sent_file_ids = get_opencode_sent_file_ids(user_id, conversation_id)
                file_paths, file_warnings, downloaded_file_ids = download_supported_files(
                    conversation, client.token, exclude_file_ids=sent_file_ids
                )
            else:
                sent_file_ids = get_opencode_sent_file_ids(user_id, conversation_id)
                file_paths, file_warnings, downloaded_file_ids = download_supported_files(
                    [event], client.token, exclude_file_ids=sent_file_ids
                )

            waiting_message = say(text=DEFAULT_LOADING_TEXT, thread_ts=thread_ts)
            response = get_provider_response(
                user_id,
                text,
                conversation_context,
                DM_SYSTEM_CONTENT,
                conversation_id=conversation_id,
                file_paths=file_paths,
            )
            mark_opencode_sent_file_ids(user_id, conversation_id, downloaded_file_ids)
            if file_warnings:
                warning_text = "\n".join([f"- {w}" for w in file_warnings[:5]])
                response = f"{response}\n\nFile warnings:\n{warning_text}"
            client.chat_update(
                channel=channel_id, ts=waiting_message["ts"], text=response
            )
    except Exception as e:
        logger.error(e)
        warning_text = ""
        if file_warnings:
            warning_text = "\n\nFile warnings:\n" + "\n".join(
                [f"- {w}" for w in file_warnings[:5]]
            )
        if waiting_message:
            client.chat_update(
                channel=channel_id,
                ts=waiting_message["ts"],
                text=f"Received an error from Bolty:\n{e}{warning_text}",
            )
        else:
            say(text=f"Received an error from Bolty:\n{e}{warning_text}", thread_ts=thread_ts)
    finally:
        cleanup_files(file_paths)
