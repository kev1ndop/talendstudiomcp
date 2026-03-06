"""workspace_info — Get project metadata: name, version, paths, artifact counts."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def workspace_info(project: str | None = None) -> str:
        """Get high-level project metadata including name, paths, and artifact counts.

        Returns project name, workspace path, and counts for jobs, connections,
        schemas, contexts, and routines.

        Args:
            project: Project name (uses default if omitted)
        """
        services.audit.log("workspace_info", {"project": project})
        try:
            info = await services.workspace.get_project_info(project)
            return json_response(info.model_dump())
        except FileNotFoundError as e:
            return error_response(str(e), "NOT_FOUND")
