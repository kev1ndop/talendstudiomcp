"""component_list — List components used in the project."""

from __future__ import annotations

from talend_mcp.tools._base import json_response


def register(mcp, services):
    @mcp.tool()
    async def component_list(
        project: str | None = None,
        category: str | None = None,
    ) -> str:
        """List all Talend component types used across jobs in the project.

        Optionally filter by category prefix (e.g. 'tDB', 'tFile', 'tMap').

        Args:
            project: Project name (uses default if omitted)
            category: Filter components by prefix (e.g. 'tDB' for all database components)
        """
        services.audit.log("component_list", {"project": project, "category": category})

        usage = await services.index.get_component_usage()

        if category:
            usage = {k: v for k, v in usage.items() if k.startswith(category)}

        components = [
            {"name": name, "usage_count": count}
            for name, count in sorted(usage.items(), key=lambda x: -x[1])
        ]

        return json_response({
            "components": components,
            "total": len(components),
        })
