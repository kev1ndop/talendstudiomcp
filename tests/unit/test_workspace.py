"""Tests for the workspace service."""

from __future__ import annotations

import pytest

from talend_mcp.core.talend.workspace import WorkspaceService


@pytest.fixture
def ws(workspace_path, project_name):
    return WorkspaceService(workspace_path, project_name)


@pytest.mark.asyncio
async def test_get_project_info(ws):
    """Test that project info returns correct counts."""
    info = await ws.get_project_info()
    assert info.project_name == "TEST_PROJECT"
    assert info.job_count == 1
    assert info.connection_count >= 1
    assert info.routine_count >= 1


@pytest.mark.asyncio
async def test_list_jobs(ws):
    """Test listing jobs with pagination."""
    result = await ws.list_jobs()
    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["name"] == "SampleJob"
    assert result["items"][0]["version"] == "0.1"


@pytest.mark.asyncio
async def test_list_jobs_with_filter(ws):
    """Test filtering jobs by name."""
    result = await ws.list_jobs(name_filter="Sample")
    assert result["total"] == 1

    result = await ws.list_jobs(name_filter="NonExistent")
    assert result["total"] == 0


@pytest.mark.asyncio
async def test_get_job_files(ws):
    """Test locating job files."""
    files = await ws.get_job_files(None, "SampleJob")
    assert files.job_name == "SampleJob"
    assert files.version == "0.1"
    assert files.item_path.is_file()
    assert files.properties_path.is_file()


@pytest.mark.asyncio
async def test_get_job_files_not_found(ws):
    """Test that missing job raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        await ws.get_job_files(None, "NonExistentJob")


@pytest.mark.asyncio
async def test_list_connections(ws):
    """Test listing connections."""
    connections = await ws.list_connections()
    assert len(connections) >= 1
    assert any("postgres_main" in c["name"] for c in connections)


@pytest.mark.asyncio
async def test_list_contexts(ws):
    """Test listing context groups."""
    contexts = await ws.list_contexts()
    assert len(contexts) >= 1


@pytest.mark.asyncio
async def test_list_routines(ws):
    """Test listing Java routines."""
    routines = await ws.list_routines()
    assert len(routines) >= 1
    assert any("DataUtils" in r["name"] for r in routines)


@pytest.mark.asyncio
async def test_get_routine_source(ws):
    """Test reading routine source code."""
    source = await ws.get_routine_source(None, "DataUtils")
    assert "public class DataUtils" in source
    assert "normalize" in source


@pytest.mark.asyncio
async def test_get_routine_not_found(ws):
    """Test that missing routine raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        await ws.get_routine_source(None, "NonExistentRoutine")


@pytest.mark.asyncio
async def test_list_artifacts_all(ws):
    """Test listing all artifact types."""
    result = await ws.list_artifacts(artifact_type="all")
    assert result["total"] >= 3  # job + connection + routine at minimum


@pytest.mark.asyncio
async def test_list_artifacts_by_type(ws):
    """Test listing artifacts filtered by type."""
    result = await ws.list_artifacts(artifact_type="jobs")
    assert result["total"] == 1

    result = await ws.list_artifacts(artifact_type="routines")
    assert result["total"] >= 1
