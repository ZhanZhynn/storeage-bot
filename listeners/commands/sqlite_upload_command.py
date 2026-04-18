from logging import Logger

from slack_bolt import Ack, BoltContext, Say
from slack_sdk import WebClient

from ..listener_utils.slack_message import clamp_slack_text
from ..listener_utils.sqlite_upload_flow import start_sqlite_upload_session


def sqlite_upload_callback(
    client: WebClient,
    ack: Ack,
    command: dict,
    say: Say,
    logger: Logger,
    context: BoltContext,
):
    try:
        ack()
        user_id = context["user_id"]
        channel_id = context["channel_id"]
        text = (command.get("text") or "").strip()

        parent = say(
            text=(
                "Starting SQLite upload flow. "
                "I will ask follow-up questions in this thread."
            )
        )
        thread_ts = parent.get("ts") if isinstance(parent, dict) else None

        intro = start_sqlite_upload_session(
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
            initial_text=text,
        )
        say(text=clamp_slack_text(intro), thread_ts=thread_ts)
    except Exception as error:
        logger.error(error)
        client.chat_postEphemeral(
            channel=context["channel_id"],
            user=context["user_id"],
            text=clamp_slack_text(f"Failed to start SQLite upload flow:\n{error}"),
        )
