"""Credential vault — provides secrets without exposing them to the LLM."""

from __future__ import annotations

import os
from typing import Literal


class Vault:
    """Simple credential vault that reads from environment variables or a config.

    In production, this should be replaced with a proper secrets manager
    (HashiCorp Vault, AWS Secrets Manager, etc.).
    """

    def __init__(self, provider: Literal["env", "file"] = "env"):
        self._provider = provider
        self._file_secrets: dict[str, str] = {}

    def load_from_file(self, path: str):
        """Load secrets from a file (key=value format, one per line)."""
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    self._file_secrets[key.strip()] = value.strip()

    async def get_secret(self, key: str) -> str | None:
        """Retrieve a secret by key. Never returns the value in logs or tool responses."""
        if self._provider == "env":
            return os.environ.get(key)
        elif self._provider == "file":
            return self._file_secrets.get(key)
        return None

    async def has_secret(self, key: str) -> bool:
        """Check if a secret exists without retrieving it."""
        val = await self.get_secret(key)
        return val is not None and val != ""

    def redact(self, text: str, keys: list[str] | None = None) -> str:
        """Redact known secret values from a text string."""
        result = text
        check_keys = keys or ["TAC_AUTH_PASS", "DB_PASSWORD"]
        for key in check_keys:
            if self._provider == "env":
                val = os.environ.get(key, "")
            else:
                val = self._file_secrets.get(key, "")
            if val and val in result:
                result = result.replace(val, "***REDACTED***")
        return result
