"""job://source/{jobName} — Raw XML source of a job."""

from __future__ import annotations


def register(mcp, services):
    @mcp.resource("job://source/{job_name}")
    async def job_source(job_name: str) -> str:
        """Raw XML content of a Talend job's .item file."""
        job_files = await services.workspace.get_job_files(None, job_name)
        return job_files.item_path.read_text(encoding="utf-8")
