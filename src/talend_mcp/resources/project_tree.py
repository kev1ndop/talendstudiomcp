"""workspace://project_tree — Project directory structure."""

from __future__ import annotations

import json
import os


def register(mcp, services):
    @mcp.resource("workspace://project_tree")
    async def workspace_project_tree() -> str:
        """Project directory tree with artifact counts per folder."""
        proj = services.config.workspace.default_project
        proj_path = services.workspace._project_path(proj)

        tree = {"project": proj, "folders": {}}

        for subdir in ["process", "metadata", "context", "code", "businessProcess"]:
            dir_path = proj_path / subdir
            if dir_path.is_dir():
                count = sum(1 for _, _, files in os.walk(dir_path) for f in files)
                tree["folders"][subdir] = {"file_count": count, "exists": True}
            else:
                tree["folders"][subdir] = {"file_count": 0, "exists": False}

        return json.dumps(tree, indent=2)
