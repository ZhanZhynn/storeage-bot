import os
import tempfile
import imghdr
import urllib.request


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
