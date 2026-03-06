"""routine_list — List Java routines available in the project."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def routine_list(project: str | None = None) -> str:
        """List all Java routines defined in the project.

        Routines are reusable Java utility classes used across jobs.

        Args:
            project: Project name (uses default if omitted)
        """
        services.audit.log("routine_list", {"project": project})
        try:
            routines = await services.workspace.list_routines(project)
            return json_response({
                "routines": routines,
                "total": len(routines),
            })
        except Exception as e:
            return error_response(str(e))
