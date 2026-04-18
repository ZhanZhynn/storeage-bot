from pathlib import Path

from listeners.listener_utils.slack_files import (
    extract_response_image_targets,
    upload_images_from_response,
)


class _FakeSlackClient:
    def __init__(self):
        self.upload_calls = []

    def files_upload_v2(self, channel: str, thread_ts: str, file: str, title: str):
        self.upload_calls.append(
            {
                "channel": channel,
                "thread_ts": thread_ts,
                "file": file,
                "title": title,
            }
        )
        return {"ok": True}


def test_extract_response_image_targets_detects_markdown_url_and_path():
    response = (
        "Saved image to `/tmp/output.png`\n"
        "And preview: ![chart](https://example.com/plot.webp)"
    )

    local_paths, remote_urls = extract_response_image_targets(response)

    assert "/tmp/output.png" in local_paths
    assert "https://example.com/plot.webp" in remote_urls


def test_upload_images_from_response_uploads_local_image(tmp_path: Path):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    client = _FakeSlackClient()
    text = f"Generated file: `{image_path}`"
    uploaded, warnings, temp_paths = upload_images_from_response(
        client=client,
        channel="C123",
        thread_ts="111.222",
        response_text=text,
    )

    assert uploaded == ["sample.png"]
    assert warnings == []
    assert temp_paths == []
    assert len(client.upload_calls) == 1
    assert client.upload_calls[0]["channel"] == "C123"
    assert client.upload_calls[0]["thread_ts"] == "111.222"
    assert client.upload_calls[0]["title"] == "sample.png"


def test_upload_images_from_response_warns_when_local_file_missing():
    client = _FakeSlackClient()
    uploaded, warnings, temp_paths = upload_images_from_response(
        client=client,
        channel="C123",
        thread_ts="111.222",
        response_text="Image path: `/tmp/does-not-exist-12345.png`",
    )

    assert uploaded == []
    assert temp_paths == []
    assert len(warnings) == 1
    assert "local file not found" in warnings[0]


def test_upload_images_from_response_uploads_plain_relative_path(tmp_path: Path, monkeypatch):
    image_path = tmp_path / "outputs" / "chart.png"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    monkeypatch.chdir(tmp_path)
    client = _FakeSlackClient()

    uploaded, warnings, temp_paths = upload_images_from_response(
        client=client,
        channel="C123",
        thread_ts="111.222",
        response_text="Chart saved to outputs/chart.png",
    )

    assert uploaded == ["chart.png"]
    assert warnings == []
    assert temp_paths == []
    assert len(client.upload_calls) == 1
    assert client.upload_calls[0]["title"] == "chart.png"
