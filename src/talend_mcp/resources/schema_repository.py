"""schema://repository — All schemas defined in the repository."""

from __future__ import annotations

import json
import os
from pathlib import Path

from lxml import etree


def register(mcp, services):
    @mcp.resource("schema://repository")
    async def schema_repository() -> str:
        """Summary of all schemas in the project repository."""
        proj = services.config.workspace.default_project
        metadata_dir = services.workspace._project_path(proj) / "metadata"

        schemas = []
        if metadata_dir.is_dir():
            for root, _dirs, files in os.walk(metadata_dir):
                for f in files:
                    if not f.endswith(".item"):
                        continue
                    try:
                        item_path = Path(root) / f
                        tree = etree.parse(str(item_path))
                        xml_root = tree.getroot()
                        columns = list(xml_root.iter("column"))
                        if columns:
                            stem = f[:-5]
                            parts = stem.rsplit("_", 1)
                            name = parts[0] if len(parts) == 2 else stem
                            schemas.append({
                                "name": name,
                                "column_count": len(columns),
                                "folder": str(Path(root).relative_to(metadata_dir)),
                            })
                    except Exception:
                        continue

        return json.dumps({
            "schemas": schemas[:100],  # Limit to avoid huge responses
            "total": len(schemas),
            "truncated": len(schemas) > 100,
        }, indent=2)
