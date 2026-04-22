from slack_sdk import WebClient


WORKING_REACTION_NAME = "hourglass_flowing_sand"


def add_working_reaction(
    client: WebClient,
    channel_id: str | None,
    message_ts: str | None,
) -> bool:
    if not channel_id or not message_ts:
        return False

    try:
        client.reactions_add(
            channel=channel_id,
            timestamp=message_ts,
            name=WORKING_REACTION_NAME,
        )
        return True
    except Exception:
        return False


def remove_working_reaction(
    client: WebClient,
    channel_id: str | None,
    message_ts: str | None,
):
    if not channel_id or not message_ts:
        return

    try:
        client.reactions_remove(
            channel=channel_id,
            timestamp=message_ts,
            name=WORKING_REACTION_NAME,
        )
    except Exception:
        pass
