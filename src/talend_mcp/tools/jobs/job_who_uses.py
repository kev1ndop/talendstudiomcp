"""job_who_uses — What other jobs depend on this job (reverse dependencies)."""

from __future__ import annotations

from talend_mcp.tools._base import json_response


def register(mcp, services):
    @mcp.tool()
    async def job_who_uses(
        job_name: str,
        project: str | None = None,
    ) -> str:
        """Find all jobs that call this job as a subjob (via tRunJob).

        Useful for impact analysis: if you change this job, which parent jobs are affected?

        Args:
            job_name: Name of the job to check dependents for
            project: Project name (uses default if omitted)
        """
        services.audit.log("job_who_uses", {"job_name": job_name, "project": project})

        proj = services.workspace._resolve_project(project)
        index = services.index
        if index._project != proj:
            from talend_mcp.core.search.indexer import ProjectIndex
            index = ProjectIndex(services.workspace.workspace_path, proj)

        dependents = await index.get_job_dependents(job_name)

        return json_response({
            "job_name": job_name,
            "used_by": dependents,
            "dependent_count": len(dependents),
        })
