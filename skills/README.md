# Skills Directory

This folder stores markdown skill playbooks used to guide LLM behavior.

## How it works
- Place one skill per `.md` file in this folder.
- The app auto-loads these files and selects relevant skills based on prompt keyword overlap.
- Selected skills are appended to prompt context as `Skill playbooks (auto-selected)`.

## Selection scoring
- Matches in `keywords:` have the highest weight.
- Matches in `# Title` and filename are medium weight.
- Matches in body text are lower weight.
- Top 3 scored skills are injected into prompt context.

## Recommended format
Use this structure for each skill file:

```md
# Skill Title
keywords: keyword1, keyword2, keyword3

## Goal
...

## Use When
...

## Workflow
1. ...
2. ...

## Guardrails
...
```

## Configuration
- Default folder: `./skills`
- Override with env var: `BOLTY_SKILLS_DIR`
- Inject at most one skill by default: `BOLTY_MAX_SKILLS_IN_PROMPT` (default `1`)
- Minimum score threshold: `BOLTY_MIN_SKILL_SCORE` (default `4`)

## Tips
- Keep `keywords:` short and specific.
- Include tool/database locations directly in the skill content when useful.
- Keep steps operational, not generic.
