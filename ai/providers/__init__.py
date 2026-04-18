from typing import List, Optional
import re

from state_store.get_user_state import get_user_state
from ai.utils import build_spreadsheet_context
from ai.utils import build_sqlite_context

from ..ai_constants import DEFAULT_SYSTEM_CONTENT
from .anthropic import AnthropicAPI
from .opencode import OpenCodeAPI
from .openai import OpenAI_API
from .vertexai import VertexAPI

"""
New AI providers must be added below.
`get_available_providers()`
This function retrieves available API models from different AI providers.
It combines the available models into a single dictionary.
`_get_provider()`
This function returns an instance of the appropriate API provider based on the given provider name.
`get_provider_response`()
This function retrieves the user's selected API provider and model,
sets the model, and generates a response.
Note that context is an optional parameter because some functionalities,
such as commands, do not allow access to conversation history if the bot
isn't in the channel where the command is run.
"""


def get_available_providers():
    return {
        **AnthropicAPI().get_models(),
        **OpenCodeAPI().get_models(),
        **OpenAI_API().get_models(),
        **VertexAPI().get_models(),
    }


def _get_provider(provider_name: str):
    if provider_name.lower() == "anthropic":
        return AnthropicAPI()
    elif provider_name.lower() == "openai":
        return OpenAI_API()
    elif provider_name.lower() == "opencode":
        return OpenCodeAPI()
    elif provider_name.lower() == "vertexai":
        return VertexAPI()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def get_provider_response(
    user_id: str,
    prompt: str,
    context: Optional[List] = None,
    system_content=DEFAULT_SYSTEM_CONTENT,
    conversation_id: Optional[str] = None,
    file_paths: Optional[List[str]] = None,
):
    if context is None:
        context = []
    try:
        provider_name, model_name = get_user_state(user_id, False)
        provider = _get_provider(provider_name)
        provider.set_model(model_name)

        if provider_name.lower() == "opencode":
            full_prompt = prompt
        else:
            formatted_context = "\n".join(
                [f"{msg['user']}: {msg['text']}" for msg in context]
            )
            full_prompt = f"Prompt: {prompt}\nContext: {formatted_context}"

        spreadsheet_context = build_spreadsheet_context(file_paths)
        sqlite_context = build_sqlite_context() if _should_include_sqlite_context(prompt) else ""
        context_parts = []
        if spreadsheet_context:
            context_parts.append(spreadsheet_context)

        if sqlite_context:
            context_parts.append(sqlite_context)

        if context_parts:
            joined_context = "\n\n".join(context_parts)
            full_prompt = f"{full_prompt}\n\n{joined_context}"

        if spreadsheet_context:
            full_prompt = (
                f"{full_prompt}\n\nIf calculations are requested, use the spreadsheet analysis first "
                "and clearly state assumptions for any missing values."
            )

        response = provider.generate_response(
            full_prompt,
            system_content,
            conversation_id=conversation_id,
            file_paths=file_paths,
        )
        return response
    except Exception as e:
        raise e


def _should_include_sqlite_context(prompt: str) -> bool:
    lowered = (prompt or "").lower()
    sqlite_keywords = (
        "sqlite",
        "database",
        "db",
        "table",
        "schema",
        "query",
        "sql",
        "select ",
        "insert ",
        "update ",
        "delete ",
        "upload",
        "import",
        "csv",
        "xlsx",
        "xls",
    )
    if any(keyword in lowered for keyword in sqlite_keywords):
        return True

    return bool(re.search(r"\bfrom\s+[a-zA-Z_][a-zA-Z0-9_]*\b", lowered))


def get_opencode_sent_file_ids(user_id: str, conversation_id: Optional[str]) -> set[str]:
    provider_name, model_name = get_user_state(user_id, False)
    if provider_name.lower() != "opencode":
        return set()

    provider = OpenCodeAPI()
    provider.set_model(model_name)
    return provider.get_sent_file_ids(conversation_id)


def mark_opencode_sent_file_ids(
    user_id: str, conversation_id: Optional[str], file_ids: List[str]
):
    if not file_ids:
        return

    provider_name, model_name = get_user_state(user_id, False)
    if provider_name.lower() != "opencode":
        return

    provider = OpenCodeAPI()
    provider.set_model(model_name)
    provider.set_sent_file_ids(conversation_id, file_ids)
