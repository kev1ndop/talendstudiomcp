"""connection_list — List all defined connections (passwords redacted)."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def connection_list(project: str | None = None) -> str:
        """List all repository connections defined in the project.

        Passwords and sensitive credentials are never returned.
        Connections are referenced by name/ID.

        Args:
            project: Project name (uses default if omitted)
        """
        services.audit.log("connection_list", {"project": project})
        try:
            connections = await services.workspace.list_connections(project)
            return json_response({
                "connections": connections,
                "total": len(connections),
            })
        except Exception as e:
            return error_response(str(e))
