"""git_log — Recent commit history."""

from __future__ import annotations

import asyncio

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def git_log(
        project: str | None = None,
        limit: int = 20,
        file_path: str | None = None,
    ) -> str:
        """Show recent Git commit history for the project.

        Args:
            project: Project name (uses default if omitted)
            limit: Number of commits to show (default 20, max 100)
            file_path: Optional file to filter history for
        """
        services.audit.log("git_log", {"project": project, "limit": limit})
        proj = services.workspace._resolve_project(project)
        proj_path = services.workspace._project_path(proj)
        limit = min(limit, 100)

        if not proj_path.is_dir():
            return error_response(f"Project not found: {proj}", "NOT_FOUND")

        cmd = [
            "git", "log",
            f"--max-count={limit}",
            "--format=%H|%h|%an|%ae|%ai|%s",
        ]
        if file_path:
            cmd.extend(["--", file_path])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(proj_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                return error_response(stderr.decode("utf-8", errors="replace"), "GIT_ERROR")

            commits = []
            for line in stdout.decode("utf-8").strip().splitlines():
                parts = line.split("|", 5)
                if len(parts) == 6:
                    commits.append({
                        "hash": parts[0],
                        "short_hash": parts[1],
                        "author": parts[2],
                        "email": parts[3],
                        "date": parts[4],
                        "message": parts[5],
                    })

            return json_response({"commits": commits, "total": len(commits)})
        except FileNotFoundError:
            return error_response("Git not found in PATH", "GIT_NOT_FOUND")
