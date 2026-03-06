"""Immutable JSONL audit log for all MCP actions."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AuditLog:
    """Append-only JSONL audit log recording every tool invocation.

    Each entry includes: timestamp, session_id, tool_name, parameters (redacted),
    result status, and duration.
    """

    def __init__(self, log_path: Path | None = None, redact_keys: list[str] | None = None):
        self._log_path = log_path
        self._session_id = str(uuid.uuid4())[:12]
        self._redact_keys = set(redact_keys or [
            "password", "pass", "secret", "token", "auth_pass", "authPass",
        ])
        self._fd: int | None = None

    def set_log_path(self, path: Path):
        """Set or update the log path (and close existing fd)."""
        self._close()
        self._log_path = path

    def _open(self):
        if self._fd is None and self._log_path:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            self._fd = os.open(
                str(self._log_path),
                os.O_WRONLY | os.O_APPEND | os.O_CREAT,
                0o644,
            )

    def _close(self):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None

    def _redact(self, params: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive fields from parameters."""
        redacted = {}
        for k, v in params.items():
            if any(rk in k.lower() for rk in self._redact_keys):
                redacted[k] = "***REDACTED***"
            elif isinstance(v, dict):
                redacted[k] = self._redact(v)
            else:
                redacted[k] = v
        return redacted

    def log(
        self,
        tool_name: str,
        parameters: dict[str, Any] | None = None,
        result_status: str = "ok",
        error: str | None = None,
        duration_ms: float | None = None,
    ):
        """Write an audit entry. Non-blocking, best-effort."""
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "epoch": time.time(),
            "session": self._session_id,
            "tool": tool_name,
            "params": self._redact(parameters or {}),
            "status": result_status,
        }
        if error:
            entry["error"] = error[:500]  # truncate long errors
        if duration_ms is not None:
            entry["duration_ms"] = round(duration_ms, 2)

        try:
            self._open()
            if self._fd is not None:
                line = json.dumps(entry, default=str, ensure_ascii=False) + "\n"
                os.write(self._fd, line.encode("utf-8"))
        except Exception as e:
            logger.warning("Failed to write audit log: %s", e)

    def __del__(self):
        self._close()
