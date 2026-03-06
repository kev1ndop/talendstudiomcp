"""workspace://current_state — Running jobs, errors, uncommitted changes."""

from __future__ import annotations

import asyncio
import json


def register(mcp, services):
    @mcp.resource("workspace://current_state")
    async def workspace_current_state() -> str:
        """Current workspace state: uncommitted changes, circuit breaker status."""
        state = {
            "project": services.config.workspace.default_project,
            "environment": services.config.security.environment,
            "read_only": services.config.security.read_only,
            "circuit_breakers": services.circuit_breakers.all_states(),
        }

        # Try to get git status
        proj_path = services.workspace._project_path(
            services.config.workspace.default_project
        )
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain",
                cwd=str(proj_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            changes = stdout.decode("utf-8").strip().splitlines()
            state["uncommitted_changes"] = len(changes)
            state["has_changes"] = len(changes) > 0
        except Exception:
            state["uncommitted_changes"] = "unknown"

        return json.dumps(state, indent=2, default=str)
