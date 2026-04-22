"""Platform-aware context builders for AI prompt injection.

Replaces the old hardcoded ``lazada_context.py`` with a generic approach
that uses the platform registry to build context for any matching platform.
"""

from __future__ import annotations

from platform_helpers.registry import get_matching_platforms


def build_platform_context(prompt: str) -> str:
    """Build combined context for all platforms whose keywords match *prompt*.

    Returns an empty string if no platforms match or none have configured
    credentials.
    """
    matching = get_matching_platforms(prompt)
    if not matching:
        return ""

    parts: list[str] = []
    for platform in matching:
        try:
            ctx = platform.context_builder()
            if ctx:
                parts.append(ctx)
        except Exception:
            continue

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Backward compatibility — keep the old function name working
# ---------------------------------------------------------------------------

def build_lazada_context() -> str:
    """Build Lazada-specific context (backward-compat wrapper)."""
    from platform_helpers.registry import get_platform

    platform = get_platform("lazada")
    if platform is None:
        return ""
    try:
        return platform.context_builder()
    except Exception:
        return ""


def should_include_platform_context(prompt: str) -> bool:
    """Return True if any registered platform's keywords match the prompt."""
    return bool(get_matching_platforms(prompt))
