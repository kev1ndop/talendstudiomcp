"""job://last_log/{jobName} — Last execution log of a job."""

from __future__ import annotations

import json
import os
from pathlib import Path


def register(mcp, services):
    @mcp.resource("job://last_log/{job_name}")
    async def job_last_log(job_name: str) -> str:
        """Last execution log for a Talend job (if available locally)."""
        proj = services.config.workspace.default_project
        proj_path = services.workspace._project_path(proj)

        # Common log locations in Talend workspace
        log_dirs = [
            proj_path / "logs",
            proj_path / ".logs",
            proj_path / "temp" / "logs",
        ]

        for log_dir in log_dirs:
            if not log_dir.is_dir():
                continue
            for root, _dirs, files in os.walk(log_dir):
                for f in sorted(files, reverse=True):
                    if job_name.lower() in f.lower() and f.endswith(".log"):
                        log_path = Path(root) / f
                        content = log_path.read_text(encoding="utf-8", errors="replace")
                        if len(content) > 20000:
                            content = content[-20000:]
                            content = "... (truncated, showing last 20000 chars)\n" + content
                        return content

        return json.dumps({
            "message": f"No log file found for job '{job_name}'",
            "hint": "Logs may be available through TAC for remote executions",
        })
