from ai.ai_constants import DM_SYSTEM_CONTENT
from logging import Logger
from slack_bolt import Say
from slack_sdk import WebClient
from ..listener_utils.ai_handler import handle_ai_response

"""
Handles the event when a direct message is sent to the bot, retrieves the conversation context,
and generates an AI response.
"""


def app_messaged_callback(client: WebClient, event: dict, logger: Logger, say: Say):
    if event.get("channel_type") != "im":
        return

    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts")
    message_ts = event.get("ts")
    user_id = event.get("user")
    text = event.get("text")
    in_thread = bool(thread_ts)

    handle_ai_response(
        client=client,
        say=say,
        logger=logger,
        user_id=user_id,
        channel_id=channel_id,
        thread_ts=thread_ts,
        message_ts=message_ts,
        text=text,
        event_messages=[event],
        system_content=DM_SYSTEM_CONTENT,
        in_thread=in_thread,
    )
