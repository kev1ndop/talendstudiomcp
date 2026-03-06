"""context_get — Get context variables for a context group."""

from __future__ import annotations

import os
from pathlib import Path

from lxml import etree

from talend_mcp.tools._base import error_response, json_response

# Fields to redact in context variables
SENSITIVE_NAMES = {"password", "pass", "secret", "token", "key", "credential"}


def register(mcp, services):
    @mcp.tool()
    async def context_get(
        context_name: str,
        project: str | None = None,
    ) -> str:
        """Get all variables in a context group.

        Password/secret values are automatically redacted.

        Args:
            context_name: Name of the context group
            project: Project name (uses default if omitted)
        """
        services.audit.log("context_get", {"context_name": context_name, "project": project})

        proj = services.workspace._resolve_project(project)
        ctx_dir = services.workspace._project_path(proj) / "context"

        if not ctx_dir.is_dir():
            return error_response("Context directory not found", "NOT_FOUND")

        for root, _dirs, files in os.walk(ctx_dir):
            for f in files:
                if not f.endswith(".item"):
                    continue
                if context_name not in f:
                    continue

                item_path = Path(root) / f
                try:
                    tree = etree.parse(str(item_path))
                    xml_root = tree.getroot()

                    variables = []
                    for param in xml_root.iter("contextParameter"):
                        name = param.get("name", "")
                        value = param.get("value", "")

                        # Redact sensitive values
                        if any(s in name.lower() for s in SENSITIVE_NAMES):
                            value = "***REDACTED***"

                        variables.append({
                            "name": name,
                            "type": param.get("type", "id_String"),
                            "value": value,
                            "prompt": param.get("prompt", ""),
                            "comment": param.get("comment", ""),
                        })

                    if variables:
                        return json_response({
                            "context_name": context_name,
                            "file": f,
                            "variables": variables,
                            "variable_count": len(variables),
                        })
                except Exception:
                    continue

        return error_response(f"Context not found: {context_name}", "NOT_FOUND")
