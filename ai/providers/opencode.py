import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

from .base_provider import BaseAPIProvider

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class OpenCodeAPI(BaseAPIProvider):
    PROVIDER_NAME = "OpenCode"

    def __init__(self):
        self.server_url = os.environ.get("OPENCODE_URL", "http://127.0.0.1:4096")
        self.server_password = os.environ.get("OPENCODE_SERVER_PASSWORD")
        self.opencode_path = shutil.which("opencode")
        self.models = self._load_models()
        self.session_store_path = Path(
            os.environ.get("OPENCODE_SESSION_STORE", "./data/opencode_sessions.json")
        )
        self.session_files_store_path = Path(
            os.environ.get("OPENCODE_SESSION_FILES_STORE", "./data/opencode_session_files.json")
        )

    def set_model(self, model_name: str):
        if model_name not in self.models.keys():
            raise ValueError("Invalid model")
        self.current_model = model_name

    def get_models(self) -> dict:
        if self.opencode_path is not None:
            return self.models
        else:
            return {}

    def generate_response(
        self,
        prompt: str,
        system_content: str,
        conversation_id: str | None = None,
        file_paths: list[str] | None = None,
    ) -> str:
        if self.opencode_path is None:
            raise RuntimeError("opencode CLI is not installed or not in PATH")

        session_id = self._get_session_id(conversation_id)
        if session_id:
            message = prompt
        else:
            message = f"{system_content}\n\n{prompt}"
        command = [
            self.opencode_path,
            "run",
            message,
            "--attach",
            self.server_url,
            "--model",
            self.current_model,
            "--format",
            "json",
        ]
        if session_id:
            command.extend(["--session", session_id])

        for file_path in file_paths or []:
            command.extend(["--file", file_path])

        if self.server_password:
            command.extend(["--password", self.server_password])

        try:
            response = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired as e:
            logger.error("OpenCode request timed out")
            raise RuntimeError("OpenCode request timed out") from e
        except subprocess.CalledProcessError as e:
            stderr_text = (e.stderr or "").strip()
            stdout_error = self._extract_error_from_events(e.stdout or "")
            details = stderr_text or stdout_error or "Unknown OpenCode error"
            logger.error(f"OpenCode CLI call failed: {details}")
            raise RuntimeError(f"OpenCode CLI call failed: {details}") from e

        new_session_id = self._extract_session_id(response.stdout)
        if conversation_id and new_session_id:
            self._set_session_id(conversation_id, new_session_id)

        content = self._extract_text_from_events(response.stdout)
        if not content:
            raise RuntimeError("OpenCode returned an empty response")
        return f"[model: {self.current_model}] {content}"

    def _get_session_id(self, conversation_id: str | None) -> str | None:
        if not conversation_id:
            return None
        sessions = self._read_session_store()
        return sessions.get(conversation_id)

    def _set_session_id(self, conversation_id: str, session_id: str):
        sessions = self._read_session_store()
        sessions[conversation_id] = session_id
        self._write_session_store(sessions)

    def _read_session_store(self) -> dict:
        try:
            if not self.session_store_path.exists():
                return {}
            with self.session_store_path.open("r") as file:
                return json.load(file)
        except Exception:
            return {}

    def _write_session_store(self, sessions: dict):
        self.session_store_path.parent.mkdir(parents=True, exist_ok=True)
        with self.session_store_path.open("w") as file:
            json.dump(sessions, file)

    def _extract_session_id(self, output: str) -> str | None:
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and event.get("sessionID"):
                return event["sessionID"]
        return None

    def get_sent_file_ids(self, conversation_id: str | None) -> set[str]:
        return self._get_sent_file_ids(conversation_id)

    def set_sent_file_ids(self, conversation_id: str | None, file_ids: list[str]):
        if not conversation_id:
            return
        existing = self._get_sent_file_ids(conversation_id)
        existing.update([str(file_id) for file_id in file_ids if file_id])
        self._set_sent_file_ids(conversation_id, existing)

    def _get_sent_file_ids(self, conversation_id: str | None) -> set[str]:
        if not conversation_id:
            return set()
        store = self._read_session_files_store()
        return set(store.get(conversation_id, []))

    def _set_sent_file_ids(self, conversation_id: str, file_ids: set[str]):
        store = self._read_session_files_store()
        store[conversation_id] = sorted(list(file_ids))
        self._write_session_files_store(store)

    def _read_session_files_store(self) -> dict:
        try:
            if not self.session_files_store_path.exists():
                return {}
            with self.session_files_store_path.open("r") as file:
                return json.load(file)
        except Exception:
            return {}

    def _write_session_files_store(self, store: dict):
        self.session_files_store_path.parent.mkdir(parents=True, exist_ok=True)
        with self.session_files_store_path.open("w") as file:
            json.dump(store, file)

    def _load_models(self) -> dict:
        model_ids = []

        models_from_env = os.environ.get("OPENCODE_MODELS", "").strip()
        if models_from_env:
            model_ids = [m.strip() for m in models_from_env.split(",") if m.strip()]
        elif os.environ.get("OPENCODE_MODEL", "").strip():
            model_ids = [os.environ.get("OPENCODE_MODEL", "").strip()]
        elif self.opencode_path is not None:
            try:
                listed = subprocess.run(
                    [self.opencode_path, "models"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                model_ids = [
                    line.strip()
                    for line in listed.stdout.splitlines()
                    if line.strip() and "/" in line
                ]
            except Exception:
                model_ids = []

        if not model_ids:
            model_ids = ["opencode/big-pickle"]

        models = {}
        for model_id in model_ids:
            models[model_id] = {
                "name": model_id,
                "provider": self.PROVIDER_NAME,
                "max_tokens": 10000,
            }
        return models

    def _extract_text_from_events(self, output: str) -> str:
        chunks = []
        current_step_chunks = []
        final_step_chunks = []

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(event, dict):
                continue

            event_type = str(event.get("type") or "")
            part = event.get("part", {}) if isinstance(event.get("part"), dict) else {}
            normalized_type = event_type.replace("-", "_")

            if normalized_type in {"step_start"}:
                current_step_chunks = []
                continue

            if normalized_type in {"step_finish"}:
                reason = str(part.get("reason") or event.get("reason") or "").strip().lower()
                if reason == "stop":
                    final_step_chunks = list(current_step_chunks)
                continue

            if normalized_type != "text":
                continue
            text = ""
            if isinstance(part, dict):
                text = part.get("text", "")
            if not text:
                text = self._extract_text(event)
            if text:
                chunks.append(text)
                current_step_chunks.append(text)

        if final_step_chunks:
            return "\n".join(final_step_chunks).strip()

        return "\n".join(chunks).strip()

    def _extract_error_from_events(self, output: str) -> str:
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(event, dict):
                continue

            if event.get("type") == "error":
                message = self._extract_text(event)
                if message:
                    return message

            part = event.get("part")
            if isinstance(part, dict) and part.get("type") == "error":
                message = self._extract_text(part)
                if message:
                    return message

        return ""

    def _extract_text(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            collected = [self._extract_text(item) for item in value]
            return "\n".join([item for item in collected if item])
        if isinstance(value, dict):
            for key in ("text", "content", "message", "output", "delta"):
                if key in value:
                    extracted = self._extract_text(value[key])
                    if extracted:
                        return extracted
            for nested_key, nested_value in value.items():
                if nested_key in ("type", "id", "sessionID", "messageID", "timestamp"):
                    continue
                extracted = self._extract_text(nested_value)
                if extracted:
                    return extracted
        return ""
