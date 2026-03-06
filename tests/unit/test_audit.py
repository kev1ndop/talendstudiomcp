"""Tests for the audit log."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from talend_mcp.core.security.audit import AuditLog


def test_audit_log_writes_jsonl():
    """Test that audit log writes valid JSONL entries."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        log_path = Path(f.name)

    audit = AuditLog(log_path=log_path)
    audit.log("test_tool", {"param1": "value1"})
    audit.log("test_tool_2", {"param2": "value2"}, result_status="error", error="Something failed")

    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 2

    entry1 = json.loads(lines[0])
    assert entry1["tool"] == "test_tool"
    assert entry1["params"]["param1"] == "value1"
    assert entry1["status"] == "ok"

    entry2 = json.loads(lines[1])
    assert entry2["tool"] == "test_tool_2"
    assert entry2["status"] == "error"
    assert "Something failed" in entry2["error"]

    log_path.unlink()


def test_audit_log_redacts_passwords():
    """Test that password fields are redacted."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        log_path = Path(f.name)

    audit = AuditLog(log_path=log_path)
    audit.log("connection_create", {
        "name": "my_db",
        "password": "super_secret",
        "auth_pass": "another_secret",
        "host": "localhost",
    })

    lines = log_path.read_text().strip().splitlines()
    entry = json.loads(lines[0])
    assert entry["params"]["password"] == "***REDACTED***"
    assert entry["params"]["auth_pass"] == "***REDACTED***"
    assert entry["params"]["host"] == "localhost"
    assert entry["params"]["name"] == "my_db"

    log_path.unlink()


def test_audit_log_has_session_id():
    """Test that all entries share a session ID."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        log_path = Path(f.name)

    audit = AuditLog(log_path=log_path)
    audit.log("tool1", {})
    audit.log("tool2", {})

    lines = log_path.read_text().strip().splitlines()
    e1 = json.loads(lines[0])
    e2 = json.loads(lines[1])
    assert e1["session"] == e2["session"]
    assert len(e1["session"]) > 0

    log_path.unlink()
