"""schema_list — List repository schemas."""

from __future__ import annotations

import os
from pathlib import Path

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def schema_list(
        project: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> str:
        """List all schemas defined in the project repository.

        Schemas define the structure (columns, types) of data flowing
        through Talend components.

        Args:
            project: Project name (uses default if omitted)
            offset: Pagination offset
            limit: Items per page (max 200)
        """
        services.audit.log("schema_list", {"project": project})
        limit = min(limit, 200)

        proj = services.workspace._resolve_project(project)
        metadata_dir = services.workspace._project_path(proj) / "metadata"

        schemas = []
        if metadata_dir.is_dir():
            for root, _dirs, files in os.walk(metadata_dir):
                for f in files:
                    if f.endswith(".item") and "schema" in root.lower():
                        stem = f[:-5]
                        parts = stem.rsplit("_", 1)
                        name = parts[0] if len(parts) == 2 else stem
                        rel = str(Path(root).relative_to(metadata_dir))
                        schemas.append({
                            "name": name,
                            "file": f,
                            "folder": rel if rel != "." else "",
                            "path": str(Path(root) / f),
                        })

        total = len(schemas)
        page = schemas[offset : offset + limit]
        return json_response({
            "schemas": page,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total,
        })
