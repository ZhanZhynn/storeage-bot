import json

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
