from ai.providers import (
    get_opencode_sent_file_ids,
    get_provider_response,
    mark_opencode_sent_file_ids,
)
from logging import Logger
from slack_sdk import WebClient
from slack_bolt import Say
from ..listener_utils.listener_constants import (
    DEFAULT_LOADING_TEXT,
    MENTION_WITHOUT_TEXT,
)
from ..listener_utils.parse_conversation import parse_conversation
from ..listener_utils.sqlite_upload_flow import process_sqlite_upload_message
from ..listener_utils.sqlite_upload_flow import build_sqlite_upload_reply
from ..listener_utils.slack_message import clamp_slack_text, safe_chat_update
from ..listener_utils.slack_reactions import add_working_reaction, remove_working_reaction
from ..listener_utils.slack_files import (
    cleanup_files,
    download_supported_files,
    upload_images_from_response,
    upload_spreadsheets_from_response,
)

"""
Handles the event when the app is mentioned in a Slack channel, retrieves the conversation context,
and generates an AI response if text is provided, otherwise sends a default response
"""


def app_mentioned_callback(client: WebClient, event: dict, logger: Logger, say: Say):
    file_paths = []
    file_warnings = []
    response_file_warnings = []
    downloaded_file_ids = []
    waiting_message = None
    reaction_set = False
    try:
        channel_id = event.get("channel")
        thread_ts = event.get("thread_ts")
        message_ts = event.get("ts")
        in_thread = bool(thread_ts)
        user_id = event.get("user")
        text = event.get("text")
        reaction_set = add_working_reaction(client, channel_id, message_ts)

        if in_thread:
            conversation = client.conversations_replies(
                channel=channel_id, ts=thread_ts, limit=10
            )["messages"]
            conversation_context = parse_conversation(conversation[:-1])
        else:
            thread_ts = event["ts"]
            conversation_context = []

        conversation_id = f"{channel_id}:{thread_ts}"
        sent_file_ids = get_opencode_sent_file_ids(user_id, conversation_id)

        if in_thread:
            file_paths, file_warnings, downloaded_file_ids = download_supported_files(
                conversation, client.token, exclude_file_ids=sent_file_ids
            )
        else:
            file_paths, file_warnings, downloaded_file_ids = download_supported_files(
                [event], client.token, exclude_file_ids=sent_file_ids
            )

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

            waiting_message = say(text=DEFAULT_LOADING_TEXT, thread_ts=thread_ts)
            response = get_provider_response(
                user_id,
                text,
                conversation_context,
                conversation_id=conversation_id,
                file_paths=file_paths,
            )
            mark_opencode_sent_file_ids(user_id, conversation_id, downloaded_file_ids)

            upload_thread_ts = thread_ts or waiting_message["ts"]
            generated_images, image_warnings, generated_temp_paths = upload_images_from_response(
                client=client,
                channel=channel_id,
                thread_ts=upload_thread_ts,
                response_text=response,
            )
            file_paths.extend(generated_temp_paths)
            response_file_warnings.extend(image_warnings)

            generated_spreadsheets, spreadsheet_warnings, spreadsheet_temp_paths = upload_spreadsheets_from_response(
                client=client,
                channel=channel_id,
                thread_ts=upload_thread_ts,
                response_text=response,
            )
            file_paths.extend(spreadsheet_temp_paths)
            response_file_warnings.extend(spreadsheet_warnings)

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
            response = MENTION_WITHOUT_TEXT
            if file_warnings:
                warning_text = "\n".join([f"- {w}" for w in file_warnings[:5]])
                response = f"{response}\n\nFile warnings:\n{warning_text}"
            say(text=clamp_slack_text(response), thread_ts=thread_ts)

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
