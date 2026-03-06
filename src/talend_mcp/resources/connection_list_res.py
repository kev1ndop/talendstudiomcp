"""connection://list — All connections (passwords redacted)."""

from __future__ import annotations

import json


def register(mcp, services):
    @mcp.resource("connection://list")
    async def connection_list_resource() -> str:
        """All repository connections (passwords and secrets redacted)."""
        connections = await services.workspace.list_connections()
        return json.dumps({
            "connections": connections,
            "total": len(connections),
            "note": "Passwords are never exposed. Use connection_get tool for details.",
        }, indent=2)
