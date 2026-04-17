import json
import os
from state_store.user_identity import UserIdentity
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def get_user_state(user_id: str, is_app_home: bool):
    filepath = f"./data/{user_id}"
    if not is_app_home and not os.path.exists(filepath):
        raise FileNotFoundError(
            "No provider selection found. Please navigate to the App Home and make a selection."
        )
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                user_identity: UserIdentity = json.load(file)
                provider = user_identity.get("provider")
                model = user_identity.get("model")

                # Backward compatibility: older parsers could store
                # "model|provider" into both fields.
                if isinstance(provider, str) and "|" in provider:
                    model, provider = provider.split("|", 1)
                elif isinstance(model, str) and "|" in model:
                    model, provider = model.split("|", 1)

                if user_identity.get("provider") != provider or user_identity.get(
                    "model"
                ) != model:
                    with open(filepath, "w") as outfile:
                        outfile.write(
                            json.dumps(
                                {
                                    "user_id": user_identity.get("user_id", user_id),
                                    "provider": provider,
                                    "model": model,
                                }
                            )
                        )

                return provider, model
    except Exception as e:
        logger.error(e)
        raise e
