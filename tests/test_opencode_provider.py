import json
import subprocess

from ai.providers.opencode import OpenCodeAPI


def test_extract_text_from_events_returns_only_final_stop_step_text():
    provider = OpenCodeAPI()

    events = [
        {"type": "step_start", "part": {"type": "step-start"}},
        {"type": "text", "part": {"text": "internal planning text"}},
        {"type": "step_finish", "part": {"reason": "tool-calls"}},
        {"type": "step_start", "part": {"type": "step-start"}},
        {"type": "text", "part": {"text": "final user answer"}},
        {"type": "step_finish", "part": {"reason": "stop"}},
    ]
    output = "\n".join(json.dumps(event) for event in events)

    extracted = provider._extract_text_from_events(output)
    assert extracted == "final user answer"


def test_extract_text_from_events_falls_back_when_no_step_events_present():
    provider = OpenCodeAPI()

    events = [
        {"type": "text", "part": {"text": "first line"}},
        {"type": "text", "part": {"text": "second line"}},
    ]
    output = "\n".join(json.dumps(event) for event in events)

    extracted = provider._extract_text_from_events(output)
    assert extracted == "first line\nsecond line"


def test_generate_response_retries_when_session_not_found(monkeypatch, tmp_path):
    session_store = tmp_path / "sessions.json"
    monkeypatch.setenv("OPENCODE_SESSION_STORE", str(session_store))
    monkeypatch.setenv("OPENCODE_URL", "http://127.0.0.1:4096")

    provider = OpenCodeAPI()
    provider.opencode_path = "opencode"
    provider.current_model = "opencode/big-pickle"
    provider._set_session_id("C1:123", "old-session")

    first_error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["opencode"],
        stderr="\x1b[91mError:\x1b[0m Session not found",
    )
    retry_stdout = "\n".join(
        [
            json.dumps({"sessionID": "new-session"}),
            json.dumps({"type": "text", "part": {"text": "Recovered answer"}}),
        ]
    )
    second_success = subprocess.CompletedProcess(
        args=["opencode"],
        returncode=0,
        stdout=retry_stdout,
        stderr="",
    )

    calls = []

    def fake_run(command, check, capture_output, text, timeout):
        calls.append(command)
        if len(calls) == 1:
            raise first_error
        return second_success

    monkeypatch.setattr("ai.providers.opencode.subprocess.run", fake_run)

    response = provider.generate_response(
        prompt="hello",
        system_content="system",
        conversation_id="C1:123",
    )

    assert response == "[model: opencode/big-pickle] Recovered answer"
    assert len(calls) == 2
    assert "--session" in calls[0]
    assert "--session" not in calls[1]
    assert provider._get_session_id("C1:123") == "new-session"


def test_get_session_id_ignores_mismatched_attach_url(monkeypatch, tmp_path):
    session_store = tmp_path / "sessions.json"
    monkeypatch.setenv("OPENCODE_SESSION_STORE", str(session_store))
    monkeypatch.setenv("OPENCODE_URL", "http://127.0.0.1:4096")

    provider = OpenCodeAPI()
    provider._set_session_id("C1:123", "s1")

    monkeypatch.setenv("OPENCODE_URL", "http://127.0.0.1:5000")
    provider_with_new_attach = OpenCodeAPI()

    assert provider_with_new_attach._get_session_id("C1:123") is None
