"""git_diff — View pending changes in the workspace repository."""

from __future__ import annotations

import asyncio

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def git_diff(
        project: str | None = None,
        staged: bool = False,
        file_path: str | None = None,
    ) -> str:
        """Show pending Git changes (diff) in the workspace.

        Args:
            project: Project name (uses default if omitted)
            staged: If true, show staged changes (--cached)
            file_path: Optional specific file to diff
        """
        services.audit.log("git_diff", {"project": project, "staged": staged, "file_path": file_path})
        proj = services.workspace._resolve_project(project)
        proj_path = services.workspace._project_path(proj)

        if not proj_path.is_dir():
            return error_response(f"Project not found: {proj}", "NOT_FOUND")

        cmd = ["git", "diff", "--stat"]
        if staged:
            cmd.append("--cached")
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

            # Also get the actual diff (limited to avoid huge outputs)
            cmd_full = ["git", "diff"]
            if staged:
                cmd_full.append("--cached")
            if file_path:
                cmd_full.extend(["--", file_path])

            proc2 = await asyncio.create_subprocess_exec(
                *cmd_full,
                cwd=str(proj_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout2, _ = await proc2.communicate()
            diff_text = stdout2.decode("utf-8", errors="replace")

            # Truncate if too long
            if len(diff_text) > 10000:
                diff_text = diff_text[:10000] + "\n... (truncated, diff too large)"

            return json_response({
                "summary": stdout.decode("utf-8").strip(),
                "diff": diff_text,
            })
        except FileNotFoundError:
            return error_response("Git not found in PATH", "GIT_NOT_FOUND")
