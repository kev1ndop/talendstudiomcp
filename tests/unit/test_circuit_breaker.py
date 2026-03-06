"""Tests for the circuit breaker pattern."""

from __future__ import annotations

import pytest

from talend_mcp.core.safety.circuit_breaker import (
    Circuit,
    CircuitBreakerRegistry,
    CircuitOpenError,
    CircuitState,
)


def test_circuit_starts_closed():
    """Circuit starts in CLOSED state."""
    c = Circuit("test", max_failures=3)
    assert c.state == CircuitState.CLOSED


def test_circuit_opens_after_max_failures():
    """Circuit opens after N consecutive failures."""
    c = Circuit("test", max_failures=3)
    c.record_failure()
    c.record_failure()
    assert c.state == CircuitState.CLOSED
    c.record_failure()
    assert c.state == CircuitState.OPEN


def test_circuit_rejects_when_open():
    """Open circuit raises CircuitOpenError."""
    c = Circuit("test", max_failures=2)
    c.record_failure()
    c.record_failure()
    with pytest.raises(CircuitOpenError) as exc_info:
        c.check()
    assert "test" in str(exc_info.value)
    assert exc_info.value.failures == 2


def test_circuit_resets_on_success():
    """Success resets the failure counter."""
    c = Circuit("test", max_failures=3)
    c.record_failure()
    c.record_failure()
    c.record_success()
    assert c._failure_count == 0
    assert c.state == CircuitState.CLOSED


def test_circuit_half_open_after_timeout():
    """Circuit transitions to HALF_OPEN after reset timeout."""
    c = Circuit("test", max_failures=2, reset_ms=10)  # 10ms timeout
    c.record_failure()
    c.record_failure()
    # Internally OPEN, but state property auto-transitions if timeout elapsed
    assert c._state == CircuitState.OPEN
    import time
    time.sleep(0.02)  # Wait for timeout to expire
    assert c.state == CircuitState.HALF_OPEN


def test_circuit_closes_from_half_open_on_success():
    """Circuit closes from HALF_OPEN on success."""
    c = Circuit("test", max_failures=2, reset_ms=0)
    c.record_failure()
    c.record_failure()
    import time
    time.sleep(0.01)
    assert c.state == CircuitState.HALF_OPEN
    c.record_success()
    assert c.state == CircuitState.CLOSED


def test_circuit_manual_reset():
    """Manual reset returns circuit to CLOSED."""
    c = Circuit("test", max_failures=2)
    c.record_failure()
    c.record_failure()
    assert c.state == CircuitState.OPEN
    c.reset()
    assert c.state == CircuitState.CLOSED
    assert c._failure_count == 0


def test_registry_creates_circuits():
    """Registry creates and retrieves named circuits."""
    reg = CircuitBreakerRegistry(max_failures=5)
    c1 = reg.get("tac_api")
    c2 = reg.get("xml_modifications")
    assert c1 is not c2
    assert reg.get("tac_api") is c1  # Same instance


def test_registry_all_states():
    """Registry reports states of all circuits."""
    reg = CircuitBreakerRegistry()
    reg.get("a")
    reg.get("b")
    states = reg.all_states()
    assert len(states) == 2
    assert all(s["state"] == "CLOSED" for s in states)
