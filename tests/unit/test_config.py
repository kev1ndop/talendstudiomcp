"""Tests for configuration loading."""

from __future__ import annotations

import os

import pytest

from talend_mcp.config.schema import TalendMcpConfig, WorkspaceConfig


def test_config_defaults():
    """Test that config has sensible defaults."""
    config = TalendMcpConfig(
        workspace=WorkspaceConfig(path="/tmp/test-workspace")
    )
    assert config.security.environment == "DEV"
    assert config.security.read_only is True
    assert config.safety.circuit_breaker_max_failures == 5
    assert config.safety.max_retries_per_heal_cycle == 3
    assert config.tac.timeout_ms == 30000


def test_config_env_override(monkeypatch):
    """Test that environment variables override defaults."""
    monkeypatch.setenv("TALEND_WORKSPACE_PATH", "/custom/workspace")
    monkeypatch.setenv("TALEND_DEFAULT_PROJECT", "MY_PROJ")
    monkeypatch.setenv("TALEND_ENVIRONMENT", "PROD")

    from talend_mcp.config.loader import load_config
    config = load_config()
    assert str(config.workspace.path) == "/custom/workspace"
    assert config.workspace.default_project == "MY_PROJ"
    assert config.security.environment == "PROD"


def test_config_security_model():
    """Test security config validation."""
    config = TalendMcpConfig(
        workspace=WorkspaceConfig(path="/tmp/test"),
    )
    assert "DEV" in config.security.allowed_write_envs
    assert config.security.vault_provider == "env"
