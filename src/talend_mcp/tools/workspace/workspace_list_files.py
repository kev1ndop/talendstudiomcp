"""workspace_list_files — Paginated listing of all workspace artifacts."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def workspace_list_files(
        project: str | None = None,
        artifact_type: str = "all",
        offset: int = 0,
        limit: int = 50,
    ) -> str:
        """List workspace artifacts with pagination and optional type filter.

        Args:
            project: Project name (uses default if omitted)
            artifact_type: Filter by type: 'all', 'jobs', 'connections', 'schemas', 'contexts', 'routines'
            offset: Pagination offset (default 0)
            limit: Items per page (default 50, max 200)
        """
        services.audit.log(
            "workspace_list_files",
            {"project": project, "type": artifact_type, "offset": offset, "limit": limit},
        )
        limit = min(limit, 200)
        try:
            result = await services.workspace.list_artifacts(
                project=project, artifact_type=artifact_type, offset=offset, limit=limit
            )
            return json_response(result)
        except FileNotFoundError as e:
            return error_response(str(e), "NOT_FOUND")
