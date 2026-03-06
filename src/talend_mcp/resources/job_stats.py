"""job://stats/{jobName} — Historical execution statistics."""

from __future__ import annotations

import json


def register(mcp, services):
    @mcp.resource("job://stats/{job_name}")
    async def job_stats(job_name: str) -> str:
        """Execution statistics for a job (from TAC if available)."""
        if services.tac.is_available:
            task_id = await services.tac.get_task_id_by_name(job_name)
            if task_id:
                history = await services.tac.get_task_execution_history(task_id)
                return json.dumps(history, indent=2, default=str)

        return json.dumps({
            "job_name": job_name,
            "message": "Statistics not available. TAC not configured or job not scheduled.",
            "hint": "Connect TAC to view execution history and statistics.",
        })
