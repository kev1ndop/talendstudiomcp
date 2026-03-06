"""Rate limiting and timeout enforcement for operations."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Coroutine


class TimeoutError(Exception):
    """Raised when an operation exceeds its timeout."""

    def __init__(self, operation: str, timeout_ms: int):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_ms}ms"
        )


class RetryExhaustedError(Exception):
    """Raised when max retries are exhausted."""

    def __init__(self, operation: str, attempts: int, last_error: str):
        self.attempts = attempts
        super().__init__(
            f"Operation '{operation}' failed after {attempts} attempts. "
            f"Last error: {last_error}"
        )


async def with_timeout(
    coro: Coroutine, timeout_ms: int, operation: str = "operation"
) -> Any:
    """Execute a coroutine with a timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_ms / 1000)
    except asyncio.TimeoutError:
        raise TimeoutError(operation, timeout_ms)


async def with_retry(
    fn,
    max_retries: int = 3,
    operation: str = "operation",
    backoff_base_ms: int = 1000,
) -> Any:
    """Execute an async function with retry and exponential backoff."""
    last_error = ""
    for attempt in range(1, max_retries + 1):
        try:
            return await fn()
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries:
                delay = (backoff_base_ms * (2 ** (attempt - 1))) / 1000
                await asyncio.sleep(delay)

    raise RetryExhaustedError(operation, max_retries, last_error)
