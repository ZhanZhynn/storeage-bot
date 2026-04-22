from pathlib import Path

from ai.providers import _should_include_lazada_context
from ai.utils.lazada_context import build_lazada_context
from ai.utils.skills import build_skills_context


def test_build_skills_context_loads_nested_skill_files(tmp_path: Path, monkeypatch):
    skills_dir = tmp_path / "skills"
    lazada_dir = skills_dir / "lazada"
    lazada_dir.mkdir(parents=True)

    (lazada_dir / "orders.md").write_text(
        "\n".join(
            [
                "# Lazada Orders",
                "keywords: lazada, orders, getorders",
                "",
                "Use this for Lazada order retrieval.",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("BOLTY_SKILLS_DIR", str(skills_dir))

    context = build_skills_context("help me fetch lazada orders")

    assert "Skill playbooks (auto-selected):" in context
    assert "Lazada Orders" in context
    assert "lazada/orders.md" in context


def test_build_lazada_context_reads_env_flags(monkeypatch):
    monkeypatch.setenv("BOLTY_LAZADA_APP_KEY", "demo-key")
    monkeypatch.setenv("BOLTY_LAZADA_APP_SECRET", "demo-secret")
    monkeypatch.setenv("BOLTY_LAZADA_ACCESS_TOKEN", "demo-token")
    monkeypatch.setenv("BOLTY_LAZADA_REGION", "SG")

    context = build_lazada_context()

    assert "`yes`" in context
    assert "`SG`" in context
    assert "demo-secret" not in context


def test_should_include_lazada_context_matches_lazada_domains():
    assert _should_include_lazada_context("show lazada orders for this month") is True
    assert _should_include_lazada_context("need finance payout details") is True
    assert _should_include_lazada_context("refund cases status") is True
    assert _should_include_lazada_context("hello team") is False
