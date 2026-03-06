"""job_list — Paginated list of jobs with folder/name filters."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def job_list(
        project: str | None = None,
        folder: str | None = None,
        name_filter: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> str:
        """List all jobs in the project with optional filtering and pagination.

        Args:
            project: Project name (uses default if omitted)
            folder: Filter by folder path (e.g. 'ETL/Daily')
            name_filter: Filter by job name (case-insensitive substring match)
            offset: Pagination offset (default 0)
            limit: Items per page (default 50, max 200)
        """
        services.audit.log(
            "job_list",
            {"project": project, "folder": folder, "name_filter": name_filter},
        )
        limit = min(limit, 200)
        try:
            result = await services.workspace.list_jobs(
                project=project,
                offset=offset,
                limit=limit,
                folder=folder,
                name_filter=name_filter,
            )
            return json_response(result)
        except FileNotFoundError as e:
            return error_response(str(e), "NOT_FOUND")
