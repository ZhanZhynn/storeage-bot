from logging import Logger
from slack_sdk import WebClient
from slack_bolt import Say
from ..listener_utils.ai_handler import handle_ai_response

"""
Handles the event when the app is mentioned in a Slack channel, retrieves the conversation context,
and generates an AI response if text is provided, otherwise sends a default response
"""


def app_mentioned_callback(client: WebClient, event: dict, logger: Logger, say: Say):
    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts")
    message_ts = event.get("ts")
    user_id = event.get("user")
    text = event.get("text")
    in_thread = bool(thread_ts)

    # For top-level mentions, set thread_ts to the message ts so replies go in-thread
    if not in_thread:
        thread_ts = message_ts

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
        in_thread=in_thread,
    )
