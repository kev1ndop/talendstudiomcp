"""schema_get — Get schema definition with columns."""

from __future__ import annotations

import os
from pathlib import Path

from lxml import etree

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def schema_get(
        schema_name: str,
        project: str | None = None,
    ) -> str:
        """Get the full definition of a repository schema including all columns.

        Returns column names, types, nullable flags, lengths, and other metadata.

        Args:
            schema_name: Name of the schema
            project: Project name (uses default if omitted)
        """
        services.audit.log("schema_get", {"schema_name": schema_name, "project": project})

        proj = services.workspace._resolve_project(project)
        metadata_dir = services.workspace._project_path(proj) / "metadata"

        if not metadata_dir.is_dir():
            return error_response("Metadata directory not found", "NOT_FOUND")

        for root, _dirs, files in os.walk(metadata_dir):
            for f in files:
                if not f.endswith(".item"):
                    continue
                if schema_name not in f and schema_name.lower() not in f.lower():
                    continue

                item_path = Path(root) / f
                try:
                    tree = etree.parse(str(item_path))
                    xml_root = tree.getroot()

                    columns = []
                    for col in xml_root.iter("column"):
                        columns.append({
                            "label": col.get("label", ""),
                            "talendType": col.get("talendType", ""),
                            "nullable": col.get("nullable", "true") == "true",
                            "length": col.get("length"),
                            "precision": col.get("precision"),
                            "key": col.get("key", "false") == "true",
                            "pattern": col.get("pattern"),
                            "default": col.get("default"),
                            "comment": col.get("comment", ""),
                        })

                    if columns:
                        return json_response({
                            "name": schema_name,
                            "file": f,
                            "columns": columns,
                            "column_count": len(columns),
                        })
                except Exception:
                    continue

        return error_response(f"Schema not found: {schema_name}", "NOT_FOUND")
