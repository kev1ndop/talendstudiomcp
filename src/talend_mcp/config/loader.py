"""Configuration loader — loads from JSON file and/or environment variables."""

from __future__ import annotations

import json
import os
from pathlib import Path

from talend_mcp.config.schema import (
    AuditConfig,
    SafetyConfig,
    SecurityConfig,
    StudioConfig,
    TacConfig,
    TalendMcpConfig,
    WorkspaceConfig,
)


def load_config() -> TalendMcpConfig:
    """Load configuration from JSON file (if exists) with environment variable overrides."""
    config_path = os.environ.get("TALEND_MCP_CONFIG")
    base: dict = {}

    if config_path and Path(config_path).is_file():
        with open(config_path) as f:
            base = json.load(f)

    workspace_path = os.environ.get("TALEND_WORKSPACE_PATH", "")
    default_project = os.environ.get("TALEND_DEFAULT_PROJECT", "")

    workspace_cfg = base.get("workspace", {})
    if workspace_path:
        workspace_cfg["path"] = workspace_path
    if default_project:
        workspace_cfg["default_project"] = default_project

    studio_cfg = base.get("studio", {})
    if studio_path := os.environ.get("TALEND_STUDIO_PATH"):
        studio_cfg["path"] = studio_path
    if java_home := os.environ.get("TALEND_JAVA_HOME"):
        studio_cfg["java_home"] = java_home

    tac_cfg = base.get("tac", {})
    if tac_url := os.environ.get("TALEND_TAC_URL"):
        tac_cfg["url"] = tac_url

    security_cfg = base.get("security", {})
    if env := os.environ.get("TALEND_ENVIRONMENT"):
        security_cfg["environment"] = env

    return TalendMcpConfig(
        workspace=WorkspaceConfig(**workspace_cfg),
        studio=StudioConfig(**studio_cfg),
        tac=TacConfig(**tac_cfg),
        security=SecurityConfig(**security_cfg),
        safety=SafetyConfig(**base.get("safety", {})),
        audit=AuditConfig(**base.get("audit", {})),
    )
