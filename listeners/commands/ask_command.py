from slack_bolt import Ack, Say, BoltContext
from logging import Logger
from ai.providers import get_provider_response
from slack_sdk import WebClient
from ..listener_utils.slack_message import clamp_slack_text, summarize_for_slack
from ..listener_utils.slack_reactions import add_working_reaction, remove_working_reaction

"""
Callback for handling the 'ask-bolty' command. It acknowledges the command, retrieves the user's ID and prompt,
checks if the prompt is empty, and responds with either an error message or the provider's response.
"""


def ask_callback(
    client: WebClient, ack: Ack, command, say: Say, logger: Logger, context: BoltContext
):
    try:
        ack()
        user_id = context["user_id"]
        channel_id = context["channel_id"]
        prompt = command["text"]
        command_ts = command.get("message_ts")
        reaction_set = add_working_reaction(client, channel_id, command_ts)

        try:
            if prompt == "":
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="Looks like you didn't provide a prompt. Try again.",
                )
            else:
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    blocks=[
                        {
                            "type": "rich_text",
                            "elements": [
                                {
                                    "type": "rich_text_quote",
                                    "elements": [{"type": "text", "text": prompt}],
                                },
                                {
                                    "type": "rich_text_section",
                                    "elements": [
                                        {
                                            "type": "text",
                                            "text": summarize_for_slack(
                                                user_id,
                                                get_provider_response(user_id, prompt)
                                            ),
                                        }
                                    ],
                                },
                            ],
                        }
                    ],
                )
        finally:
            if reaction_set:
                remove_working_reaction(client, channel_id, command_ts)
    except Exception as e:
        logger.error(e)
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=clamp_slack_text(f"Received an error from Bolty:\n{e}"),
        )
