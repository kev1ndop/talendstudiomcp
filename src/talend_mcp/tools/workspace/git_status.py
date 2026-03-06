"""git_status — Git status of the workspace repository."""

from __future__ import annotations

import asyncio

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def git_status(project: str | None = None) -> str:
        """Show the Git status of the workspace/project repository.

        Returns staged, modified, and untracked files.

        Args:
            project: Project name (uses default if omitted)
        """
        services.audit.log("git_status", {"project": project})
        proj = services.workspace._resolve_project(project)
        proj_path = services.workspace._project_path(proj)

        if not proj_path.is_dir():
            return error_response(f"Project not found: {proj}", "NOT_FOUND")

        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain", "-b",
                cwd=str(proj_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                return error_response(
                    f"Git error: {stderr.decode('utf-8', errors='replace')}",
                    "GIT_ERROR",
                )

            lines = stdout.decode("utf-8").strip().splitlines()
            branch = ""
            staged = []
            modified = []
            untracked = []

            for line in lines:
                if line.startswith("## "):
                    branch = line[3:]
                elif line.startswith("A  ") or line.startswith("M  "):
                    staged.append(line[3:])
                elif line.startswith(" M "):
                    modified.append(line[3:])
                elif line.startswith("?? "):
                    untracked.append(line[3:])
                elif line[:2].strip():
                    modified.append(line[3:])

            return json_response({
                "branch": branch,
                "staged": staged,
                "modified": modified,
                "untracked": untracked,
                "clean": len(staged) == 0 and len(modified) == 0 and len(untracked) == 0,
            })
        except FileNotFoundError:
            return error_response("Git not found in PATH", "GIT_NOT_FOUND")
