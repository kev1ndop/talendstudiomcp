"""job://java/{jobName} — Generated Java code of a job."""

from __future__ import annotations


def register(mcp, services):
    @mcp.resource("job://java/{job_name}")
    async def job_java(job_name: str) -> str:
        """Generated Java source code for a Talend job."""
        code = await services.workspace.find_generated_java(None, job_name)
        return code or f"No generated Java found for job '{job_name}'. Build the job first."
