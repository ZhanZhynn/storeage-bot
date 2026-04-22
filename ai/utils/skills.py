import os
import re
from pathlib import Path

DEFAULT_SKILLS_DIR = "./skills"
MAX_SKILLS_IN_PROMPT = 1
MIN_SKILL_SCORE = 4


def build_skills_context(prompt: str, max_skills: int = MAX_SKILLS_IN_PROMPT) -> str:
    configured_max = _read_int_env("BOLTY_MAX_SKILLS_IN_PROMPT", max_skills)
    configured_max = max(3, configured_max)

    skills = _load_skills()
    if not skills:
        return ""

    selected = _select_skills(prompt, skills, max_skills=configured_max)
    if not selected:
        return ""

    sections = []
    for skill in selected:
        sections.append(
            "\n".join(
                [
                    f"### Skill: {skill['title']}",
                    f"Source: {skill['path']}",
                    skill["content"],
                ]
            )
        )

    joined = "\n\n".join(sections)
    return (
        "Skill playbooks (auto-selected):\n"
        "Use these playbooks to choose the right steps/tools when they match the user intent.\n"
        "If a playbook conflicts with direct user instructions, follow the user instructions.\n\n"
        f"{joined}"
    )


def _load_skills() -> list[dict[str, str]]:
    skills_dir = Path(os.environ.get("BOLTY_SKILLS_DIR", DEFAULT_SKILLS_DIR)).resolve()
    if not skills_dir.exists() or not skills_dir.is_dir():
        return []

    skills = []
    for file_path in sorted(skills_dir.rglob("*.md")):
        try:
            content = file_path.read_text(encoding="utf-8").strip()
        except Exception:
            continue

        if not content:
            continue

        title = _extract_title(content) or file_path.stem.replace("_", " ").replace("-", " ")
        keywords = _extract_keywords(content)
        title_tokens = _tokenize(title)
        stem_tokens = _tokenize(file_path.stem)
        body_tokens = _tokenize(content)

        skills.append(
            {
                "path": str(file_path),
                "title": title,
                "content": content,
                "keywords": "|".join(sorted(set([k for k in keywords if k]))),
                "title_tokens": "|".join(sorted(set(title_tokens))),
                "stem_tokens": "|".join(sorted(set(stem_tokens))),
                "body_tokens": "|".join(sorted(set(body_tokens))),
            }
        )

    return skills


def _select_skills(prompt: str, skills: list[dict[str, str]], max_skills: int) -> list[dict[str, str]]:
    prompt_tokens = set(_tokenize(prompt))
    if not prompt_tokens:
        return []

    min_score = _read_int_env("BOLTY_MIN_SKILL_SCORE", MIN_SKILL_SCORE)

    scored = []
    for skill in skills:
        keyword_tokens = _to_set(skill.get("keywords", ""))
        title_tokens = _to_set(skill.get("title_tokens", ""))
        stem_tokens = _to_set(skill.get("stem_tokens", ""))
        body_tokens = _to_set(skill.get("body_tokens", ""))

        keyword_overlap = prompt_tokens.intersection(keyword_tokens)
        title_overlap = prompt_tokens.intersection(title_tokens)
        stem_overlap = prompt_tokens.intersection(stem_tokens)
        body_overlap = prompt_tokens.intersection(body_tokens)

        score = (
            (len(keyword_overlap) * 6)
            + (len(title_overlap) * 4)
            + (len(stem_overlap) * 3)
            + (len(body_overlap) * 1)
        )
        has_strong_overlap = bool(keyword_overlap or title_overlap or stem_overlap)
        if not has_strong_overlap:
            continue

        if score < min_score:
            continue

        scored.append((score, skill["title"], skill))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in scored[:max_skills]]


def _extract_title(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def _extract_keywords(content: str) -> list[str]:
    for line in content.splitlines():
        lowered = line.lower().strip()
        if not lowered.startswith("keywords:"):
            continue
        _, raw = line.split(":", 1)
        values = [item.strip().lower() for item in raw.split(",")]
        return [value for value in values if value]
    return []


def _tokenize(text: str) -> list[str]:
    if not text:
        return []
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "into",
        "from",
        "this",
        "that",
        "your",
        "you",
        "use",
        "when",
        "where",
        "how",
        "what",
        "file",
        "data",
    }
    tokens = [token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if len(token) > 1]
    return [token for token in tokens if token not in stopwords]


def _to_set(serialized_tokens: str) -> set[str]:
    if not serialized_tokens:
        return set()
    return set([token for token in serialized_tokens.split("|") if token])


def _read_int_env(name: str, default: int) -> int:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except Exception:
        return default
