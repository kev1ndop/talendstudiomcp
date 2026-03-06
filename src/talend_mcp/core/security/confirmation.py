"""Write confirmation middleware for dangerous operations."""

from __future__ import annotations


class ConfirmationRequired(Exception):
    """Raised when an operation requires human confirmation."""

    def __init__(self, operation: str, details: str = ""):
        self.operation = operation
        self.details = details
        msg = f"Operation '{operation}' requires confirmation (pass confirm=true)."
        if details:
            msg += f" Details: {details}"
        super().__init__(msg)


class BatchConfirmationRequired(Exception):
    """Raised when a batch operation exceeds the max_batch_jobs limit."""

    def __init__(self, operation: str, job_count: int, max_allowed: int):
        self.operation = operation
        self.job_count = job_count
        self.max_allowed = max_allowed
        super().__init__(
            f"Batch operation '{operation}' affects {job_count} jobs, "
            f"exceeding the limit of {max_allowed}. "
            "Human confirmation is required."
        )


def check_batch_limit(operation: str, count: int, max_batch: int) -> None:
    """Raise if a batch operation exceeds the configured limit."""
    if count > max_batch:
        raise BatchConfirmationRequired(operation, count, max_batch)
