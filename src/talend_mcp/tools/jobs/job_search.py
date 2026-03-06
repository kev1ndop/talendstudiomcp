"""job_search — Search jobs by name, component, or connection."""

from __future__ import annotations

from talend_mcp.tools._base import json_response


def register(mcp, services):
    @mcp.tool()
    async def job_search(
        query: str | None = None,
        component: str | None = None,
        connection: str | None = None,
        project: str | None = None,
        limit: int = 50,
    ) -> str:
        """Search for jobs by name, component used, or connection referenced.

        At least one search criterion must be provided. Results are sorted by relevance.

        Args:
            query: Search by job name (case-insensitive substring match)
            component: Search by component name (e.g. 'tDBInput', 'tFileInputDelimited')
            connection: Search by connection ID referenced in the job
            project: Project name (uses default if omitted)
            limit: Maximum results (default 50)
        """
        services.audit.log(
            "job_search",
            {"query": query, "component": component, "connection": connection},
        )

        # Use the project-level index for efficient search
        proj = services.workspace._resolve_project(project)
        index = services.index
        if index._project != proj:
            from talend_mcp.core.search.indexer import ProjectIndex
            index = ProjectIndex(services.workspace.workspace_path, proj)

        results = await index.search_jobs(
            query=query, component=component, connection=connection
        )

        return json_response({
            "results": results[:limit],
            "total": len(results),
            "query": {"name": query, "component": component, "connection": connection},
        })
