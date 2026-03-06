"""Shared test fixtures for Talend Studio MCP tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_WORKSPACE = FIXTURES_DIR / "sample_workspace"
TEST_PROJECT = "TEST_PROJECT"


@pytest.fixture
def workspace_path() -> Path:
    return SAMPLE_WORKSPACE


@pytest.fixture
def project_name() -> str:
    return TEST_PROJECT


@pytest.fixture
def sample_item_path() -> Path:
    return SAMPLE_WORKSPACE / TEST_PROJECT / "process" / "SampleJob" / "SampleJob_0.1.item"


@pytest.fixture
def sample_properties_path() -> Path:
    return SAMPLE_WORKSPACE / TEST_PROJECT / "process" / "SampleJob" / "SampleJob_0.1.properties"


@pytest.fixture
def sample_connection_path() -> Path:
    return SAMPLE_WORKSPACE / TEST_PROJECT / "metadata" / "connections" / "postgres_main_0.1.item"


@pytest.fixture
def sample_context_path() -> Path:
    return SAMPLE_WORKSPACE / TEST_PROJECT / "context" / "Default_0.1.item"


@pytest.fixture
def sample_routine_path() -> Path:
    return SAMPLE_WORKSPACE / TEST_PROJECT / "code" / "routines" / "DataUtils.java"
