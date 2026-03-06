"""Pydantic configuration models for the Talend Studio MCP server."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class WorkspaceConfig(BaseModel):
    path: Path = Field(description="Path to the Talend workspace directory")
    default_project: str = Field(default="", description="Default project name within the workspace")


class StudioConfig(BaseModel):
    path: Path | None = Field(default=None, description="Path to Talend Studio installation")
    java_home: Path | None = Field(default=None, description="Java home for Talend Studio")


class TacConfig(BaseModel):
    url: str | None = Field(default=None, description="TAC MetaServlet base URL")
    timeout_ms: int = Field(default=30000, description="HTTP timeout for TAC API calls")


class SecurityConfig(BaseModel):
    environment: Literal["DEV", "STAGING", "PROD"] = Field(
        default="DEV", description="Current environment"
    )
    allowed_write_envs: list[str] = Field(
        default_factory=lambda: ["DEV"],
        description="Environments where write operations are allowed",
    )
    read_only: bool = Field(
        default=True, description="If true, all write tools require confirm=true"
    )
    vault_provider: Literal["env", "file"] = Field(
        default="env", description="How credentials are stored"
    )


class SafetyConfig(BaseModel):
    circuit_breaker_max_failures: int = Field(
        default=5, description="Max consecutive failures before circuit opens"
    )
    circuit_breaker_reset_ms: int = Field(
        default=60000, description="Time before circuit breaker resets from OPEN to HALF_OPEN"
    )
    max_retries_per_heal_cycle: int = Field(
        default=3, description="Max retry attempts in a self-healing cycle"
    )
    execution_timeout_ms: int = Field(
        default=600000, description="Max execution time for a job run"
    )
    max_batch_jobs: int = Field(
        default=5,
        description="Max jobs that can be modified in a single batch without human confirmation",
    )


class AuditConfig(BaseModel):
    log_path: Path | None = Field(
        default=None,
        description="Audit log path. Defaults to {workspace}/.talend-mcp-audit.jsonl",
    )
    redact_passwords: bool = Field(default=True, description="Redact password fields in logs")


class TalendMcpConfig(BaseModel):
    workspace: WorkspaceConfig
    studio: StudioConfig = Field(default_factory=StudioConfig)
    tac: TacConfig = Field(default_factory=TacConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)
