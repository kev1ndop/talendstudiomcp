"""FastMCP server factory and startup for Talend Studio MCP."""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from talend_mcp.config.loader import load_config
from talend_mcp.core.service_container import ServiceContainer
from talend_mcp.prompts import register_all_prompts
from talend_mcp.resources import register_all_resources
from talend_mcp.tools import register_all_tools

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "talend-studio-mcp",
    version="0.1.0",
)

_services: ServiceContainer | None = None


def get_services() -> ServiceContainer:
    """Get the initialized service container. Raises if not yet started."""
    if _services is None:
        raise RuntimeError("Server not started — services not initialized")
    return _services


@mcp.on_event("startup")
async def startup():
    global _services
    logger.info("Starting Talend Studio MCP server...")

    config = load_config()
    _services = await ServiceContainer.create(config)

    register_all_tools(mcp, _services)
    register_all_resources(mcp, _services)
    register_all_prompts(mcp, _services)

    logger.info(
        "Server ready: workspace=%s, project=%s, env=%s",
        config.workspace.path,
        config.workspace.default_project,
        config.security.environment,
    )


@mcp.on_event("shutdown")
async def shutdown():
    global _services
    if _services:
        await _services.close()
        _services = None
    logger.info("Talend Studio MCP server stopped.")
