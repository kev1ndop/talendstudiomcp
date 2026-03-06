"""Circuit breaker pattern for resilient operations."""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Callable


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    """Raised when a circuit is open and calls are rejected."""

    def __init__(self, circuit_name: str, failures: int, retry_after_ms: int):
        self.circuit_name = circuit_name
        self.failures = failures
        self.retry_after_ms = retry_after_ms
        super().__init__(
            f"Circuit '{circuit_name}' is OPEN after {failures} consecutive failures. "
            f"Retry after {retry_after_ms}ms. Human intervention may be needed."
        )


class Circuit:
    """A single circuit breaker instance."""

    def __init__(self, name: str, max_failures: int = 5, reset_ms: int = 60000):
        self.name = name
        self.max_failures = max_failures
        self.reset_ms = reset_ms
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._success_count = 0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            elapsed = (time.time() - self._last_failure_time) * 1000
            if elapsed >= self.reset_ms:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def record_success(self):
        """Record a successful operation."""
        self._failure_count = 0
        self._success_count += 1
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED

    def record_failure(self):
        """Record a failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.max_failures:
            self._state = CircuitState.OPEN

    def check(self):
        """Check if the circuit allows the call. Raises CircuitOpenError if not."""
        state = self.state
        if state == CircuitState.OPEN:
            retry_after = int(self.reset_ms - (time.time() - self._last_failure_time) * 1000)
            raise CircuitOpenError(self.name, self._failure_count, max(retry_after, 0))

    def reset(self):
        """Manually reset the circuit breaker."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "max_failures": self.max_failures,
            "reset_ms": self.reset_ms,
        }


class CircuitBreakerRegistry:
    """Registry of named circuit breakers."""

    def __init__(self, max_failures: int = 5, reset_ms: int = 60000):
        self._default_max = max_failures
        self._default_reset = reset_ms
        self._circuits: dict[str, Circuit] = {}

    def get(self, name: str) -> Circuit:
        """Get or create a named circuit breaker."""
        if name not in self._circuits:
            self._circuits[name] = Circuit(
                name, self._default_max, self._default_reset
            )
        return self._circuits[name]

    def all_states(self) -> list[dict[str, Any]]:
        """Get the state of all registered circuits."""
        return [c.to_dict() for c in self._circuits.values()]

    def reset_all(self):
        """Reset all circuit breakers."""
        for c in self._circuits.values():
            c.reset()
