"""Tests for the Talend XML parser."""

from __future__ import annotations

import pytest

from talend_mcp.core.talend.xml_parser import TalendXmlParser


@pytest.fixture
def parser():
    return TalendXmlParser()


@pytest.mark.asyncio
async def test_parse_item_components(parser, sample_item_path):
    """Test that all components are extracted from the sample job."""
    job = await parser.parse_item(sample_item_path)
    assert len(job.components) == 5
    names = [c.component_name for c in job.components]
    assert "tDBInput" in names
    assert "tMap" in names
    assert "tDBOutput" in names
    assert "tLogRow" in names
    assert "tRunJob" in names


@pytest.mark.asyncio
async def test_parse_item_connections(parser, sample_item_path):
    """Test that connections between components are extracted."""
    job = await parser.parse_item(sample_item_path)
    assert len(job.connections) == 4

    flow_conns = [c for c in job.connections if c.connector_name == "FLOW"]
    assert len(flow_conns) == 2

    reject_conns = [c for c in job.connections if c.connector_name == "REJECT"]
    assert len(reject_conns) == 1

    subjob_conns = [c for c in job.connections if c.connector_name == "SUBJOB_OK"]
    assert len(subjob_conns) == 1


@pytest.mark.asyncio
async def test_parse_item_context_parameters(parser, sample_item_path):
    """Test that context parameters are extracted."""
    job = await parser.parse_item(sample_item_path)
    assert len(job.context_parameters) == 3

    names = [p["name"] for p in job.context_parameters]
    assert "db_host" in names
    assert "db_port" in names
    assert "db_password" in names


@pytest.mark.asyncio
async def test_parse_item_subjobs(parser, sample_item_path):
    """Test that tRunJob references are extracted as subjob dependencies."""
    job = await parser.parse_item(sample_item_path)
    assert "NotificationJob" in job.subjobs


@pytest.mark.asyncio
async def test_parse_item_metadata(parser, sample_item_path):
    """Test that component metadata (schemas) are extracted."""
    job = await parser.parse_item(sample_item_path)
    db_input = next(c for c in job.components if c.component_name == "tDBInput")
    assert len(db_input.metadata) == 1
    columns = db_input.metadata[0]["columns"]
    assert len(columns) == 3
    assert columns[0]["label"] == "id"
    assert columns[0]["talendType"] == "id_Integer"


@pytest.mark.asyncio
async def test_parse_item_component_parameters(parser, sample_item_path):
    """Test that component elementParameters are extracted."""
    job = await parser.parse_item(sample_item_path)
    db_input = next(c for c in job.components if c.component_name == "tDBInput")
    assert "QUERY" in db_input.parameters
    assert "SELECT" in db_input.parameters["QUERY"]["value"]


@pytest.mark.asyncio
async def test_parse_raw_xml(parser, sample_item_path):
    """Test reading raw XML content."""
    xml = await parser.parse_raw_xml(sample_item_path)
    assert "ProcessType" in xml
    assert "tDBInput" in xml
