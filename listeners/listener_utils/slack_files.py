import os
import tempfile
import imghdr
import urllib.request
import re
from pathlib import Path
from urllib.parse import urlparse


_SUPPORTED_IMAGE_ENCODINGS = {"jpeg", "png", "gif", "webp"}
_SUPPORTED_IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def _is_supported_file(file_info: dict) -> bool:
    mimetype = (file_info.get("mimetype") or "").lower()
    name = (file_info.get("name") or "").lower()

    supported_mimetypes = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv",
        "application/csv",
    }
    supported_suffixes = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".xlsx", ".xls", ".csv")

    return mimetype in supported_mimetypes or name.endswith(supported_suffixes)


def _looks_like_image_url(value: str) -> bool:
    lowered = (value or "").lower()
    if not lowered.startswith(("http://", "https://")):
        return False

    parsed = urlparse(lowered)
    path = parsed.path or ""
    return path.endswith(_SUPPORTED_IMAGE_SUFFIXES)


def _looks_like_image_path(value: str) -> bool:
    return (value or "").lower().endswith(_SUPPORTED_IMAGE_SUFFIXES)


def _extract_markdown_image_targets(text: str) -> list[str]:
    if not text:
        return []

    matches = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    targets = []
    for match in matches:
        candidate = (match or "").strip()
        if not candidate:
            continue

        if candidate[0] in {'"', "'"} and candidate[-1:] == candidate[0]:
            candidate = candidate[1:-1].strip()

        if " " in candidate:
            candidate = candidate.split(" ", 1)[0].strip()

        if candidate:
            targets.append(candidate)

    return targets


def extract_response_image_targets(response_text: str) -> tuple[list[str], list[str]]:
    local_paths = []
    remote_urls = []
    seen = set()

    candidates = []
    candidates.extend(_extract_markdown_image_targets(response_text))

    inline_code_candidates = re.findall(r"`([^`]+)`", response_text or "")
    candidates.extend([candidate.strip() for candidate in inline_code_candidates])

    url_candidates = re.findall(r"https?://[^\s)\]>\"']+", response_text or "")
    candidates.extend([candidate.strip().rstrip(".,;:!") for candidate in url_candidates])

    abs_path_candidates = re.findall(r"(?<!\w)(/[A-Za-z0-9_./\-]+\.(?:png|jpe?g|gif|webp))(?!\w)", response_text or "", flags=re.IGNORECASE)
    candidates.extend([candidate.strip() for candidate in abs_path_candidates])

    relative_path_candidates = re.findall(
        r"(?<!://)(?<![A-Za-z0-9_./\-])((?:~?/)?(?:[A-Za-z0-9_.\-]+/)+[A-Za-z0-9_.\-]+\.(?:png|jpe?g|gif|webp))(?![A-Za-z0-9_./\-])",
        response_text or "",
        flags=re.IGNORECASE,
    )
    candidates.extend([candidate.strip() for candidate in relative_path_candidates])

    for candidate in candidates:
        normalized = candidate.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)

        if _looks_like_image_url(normalized):
            remote_urls.append(normalized)
            continue

        if _looks_like_image_path(normalized):
            local_paths.append(normalized)

    return local_paths, remote_urls


def _is_supported_image_payload(payload: bytes) -> tuple[bool, str]:
    detected = imghdr.what(None, payload)
    if detected in _SUPPORTED_IMAGE_ENCODINGS:
        return True, detected
    return False, ""


def _normalize_local_path(path_text: str) -> Path:
    expanded = Path(path_text).expanduser()
    if expanded.is_absolute():
        return expanded
    return Path.cwd() / expanded


def _get_slack_error_code(error) -> str:
    response = getattr(error, "response", None)
    if response is None:
        return ""

    try:
        if hasattr(response, "data") and isinstance(response.data, dict):
            return str(response.data.get("error", "") or "")
    except Exception:
        pass

    try:
        return str(response.get("error", "") or "")
    except Exception:
        return ""


def upload_images_from_response(
    client,
    channel: str,
    thread_ts: str,
    response_text: str,
) -> tuple[list[str], list[str], list[str]]:
    local_targets, remote_targets = extract_response_image_targets(response_text)
    if not local_targets and not remote_targets:
        return [], [], []

    uploaded_names = []
    warnings = []
    temp_paths = []
    uploaded_keys = set()

    for local_target in local_targets:
        image_path = _normalize_local_path(local_target)
        path_key = str(image_path.resolve()) if image_path.exists() else str(image_path)
        if path_key in uploaded_keys:
            continue

        if not image_path.exists() or not image_path.is_file():
            warnings.append(f"Skipped image `{local_target}`: local file not found.")
            continue

        try:
            payload = image_path.read_bytes()
        except Exception:
            warnings.append(f"Skipped image `{local_target}`: could not read local file.")
            continue

        is_supported, _ = _is_supported_image_payload(payload)
        if not is_supported:
            warnings.append(
                f"Skipped image `{local_target}`: unsupported image encoding (allowed: png/jpeg/gif/webp)."
            )
            continue

        try:
            client.files_upload_v2(
                channel=channel,
                thread_ts=thread_ts,
                file=str(image_path),
                title=image_path.name,
            )
            uploaded_names.append(image_path.name)
            uploaded_keys.add(path_key)
        except Exception as error:
            error_code = _get_slack_error_code(error)
            if error_code == "missing_scope":
                warnings.append(
                    "Could not upload generated image(s): missing Slack scope `files:write`."
                )
            else:
                warnings.append(f"Could not upload image `{local_target}` to Slack.")

    for url in remote_targets:
        if url in uploaded_keys:
            continue

        try:
            request = urllib.request.Request(url)
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
        except Exception:
            warnings.append(f"Could not download image URL `{url}`.")
            continue

        is_supported, detected = _is_supported_image_payload(payload)
        if not is_supported:
            warnings.append(
                f"Skipped image URL `{url}`: unsupported image encoding (allowed: png/jpeg/gif/webp)."
            )
            continue

        suffix = ".jpeg" if detected == "jpeg" else f".{detected}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(payload)
            temp_path = temp_file.name
            temp_paths.append(temp_path)

        title = Path(urlparse(url).path).name or f"generated-image{suffix}"
        try:
            client.files_upload_v2(
                channel=channel,
                thread_ts=thread_ts,
                file=temp_path,
                title=title,
            )
            uploaded_names.append(title)
            uploaded_keys.add(url)
        except Exception as error:
            error_code = _get_slack_error_code(error)
            if error_code == "missing_scope":
                warnings.append(
                    "Could not upload generated image(s): missing Slack scope `files:write`."
                )
            else:
                warnings.append(f"Could not upload image URL `{url}` to Slack.")

    return uploaded_names, warnings, temp_paths


def _is_image(file_info: dict) -> bool:
    mimetype = (file_info.get("mimetype") or "").lower()
    name = (file_info.get("name") or "").lower()
    return mimetype.startswith("image/") or name.endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".gif")
    )


def _is_spreadsheet(file_info: dict) -> bool:
    mimetype = (file_info.get("mimetype") or "").lower()
    name = (file_info.get("name") or "").lower()
    spreadsheet_mimetypes = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv",
        "application/csv",
    }
    return mimetype in spreadsheet_mimetypes or name.endswith((".xlsx", ".xls", ".csv"))


def download_supported_files(
    messages: list[dict],
    slack_bot_token: str | None,
    exclude_file_ids: set[str] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    if not slack_bot_token:
        return [], ["File processing is disabled because bot token is missing."], []

    if exclude_file_ids is None:
        exclude_file_ids = set()

    files = []
    seen_ids = set()
    for message in messages:
        for file_info in message.get("files", []) or []:
            file_id = file_info.get("id") or file_info.get("url_private")
            if file_id in seen_ids:
                continue
            seen_ids.add(file_id)
            files.append(file_info)

    downloaded_paths = []
    downloaded_file_ids = []
    warnings = []

    for file_info in files:
        display_name = file_info.get("name") or "unnamed file"
        file_id = file_info.get("id") or file_info.get("url_private")
        if file_id in exclude_file_ids:
            continue

        if not _is_supported_file(file_info):
            warnings.append(
                f"Skipped `{display_name}`: unsupported file type."
            )
            continue

        url = file_info.get("url_private_download") or file_info.get("url_private")
        if not url:
            warnings.append(f"Skipped `{display_name}`: missing download URL.")
            continue

        try:
            request = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {slack_bot_token}"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
        except Exception:
            warnings.append(
                f"Could not download `{display_name}`. Check Slack `files:read` scope."
            )
            continue

        suffix = ""
        if _is_image(file_info):
            detected = imghdr.what(None, payload)
            if detected not in {"jpeg", "png", "gif", "webp"}:
                warnings.append(
                    f"Skipped `{display_name}`: unsupported image encoding (allowed: png/jpeg/gif/webp)."
                )
                continue
            suffix = ".jpeg" if detected == "jpeg" else f".{detected}"
        elif _is_spreadsheet(file_info):
            name = file_info.get("name") or "slack-file"
            suffix = os.path.splitext(name)[1] or ".csv"
        else:
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(payload)
            downloaded_paths.append(temp_file.name)
            if file_id:
                downloaded_file_ids.append(str(file_id))

    return downloaded_paths, warnings, downloaded_file_ids


def cleanup_files(file_paths: list[str]):
    for path in file_paths:
        try:
            os.remove(path)
        except FileNotFoundError:
            continue
