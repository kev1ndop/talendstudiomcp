"""Environment gating — controls which operations are allowed in each environment."""

from __future__ import annotations

from typing import Literal


class EnvironmentGuard:
    """Enforce environment-based restrictions on operations.

    - DEV: All operations allowed
    - STAGING: Read + limited write, no PROD deployments
    - PROD: Read-only by default, requires explicit confirmation for any write
    """

    def __init__(
        self,
        environment: Literal["DEV", "STAGING", "PROD"] = "DEV",
        allowed_write_envs: list[str] | None = None,
        read_only: bool = True,
    ):
        self.environment = environment
        self.allowed_write_envs = allowed_write_envs or ["DEV"]
        self.read_only = read_only

    def can_write(self) -> bool:
        """Check if write operations are allowed in the current environment."""
        return self.environment in self.allowed_write_envs

    def can_execute(self) -> bool:
        """Check if job execution is allowed."""
        return self.environment in self.allowed_write_envs

    def require_write_permission(self, operation: str) -> None:
        """Raise if write is not allowed."""
        if not self.can_write():
            raise PermissionError(
                f"Write operation '{operation}' not allowed in {self.environment} environment. "
                f"Allowed environments: {self.allowed_write_envs}"
            )

    def require_confirmation(self, operation: str, confirm: bool = False) -> None:
        """Require explicit confirmation for write operations."""
        if self.read_only and not confirm:
            raise PermissionError(
                f"Operation '{operation}' requires explicit confirmation (confirm=true) "
                f"because the server is in read-only mode."
            )

    def check_write_operation(self, operation: str, confirm: bool = False) -> None:
        """Full check: environment + confirmation."""
        self.require_write_permission(operation)
        self.require_confirmation(operation, confirm)

    def is_prod(self) -> bool:
        return self.environment == "PROD"
