"""connection_get — Get connection configuration (passwords redacted)."""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from talend_mcp.tools._base import error_response, json_response

# Fields that should always be redacted
REDACT_FIELDS = {"Password", "password", "PASS", "pass", "secret", "Secret", "token", "Token"}


def register(mcp, services):
    @mcp.tool()
    async def connection_get(
        connection_name: str,
        project: str | None = None,
    ) -> str:
        """Get the configuration of a specific repository connection.

        Passwords and sensitive fields are automatically redacted.
        The connection is identified by name.

        Args:
            connection_name: Name of the connection
            project: Project name (uses default if omitted)
        """
        services.audit.log("connection_get", {"connection_name": connection_name, "project": project})

        proj = services.workspace._resolve_project(project)
        conn_dir = services.workspace._project_path(proj) / "metadata" / "connections"

        if not conn_dir.is_dir():
            return error_response("No connections directory found", "NOT_FOUND")

        # Search for the connection .item file
        import os
        for root, _dirs, files in os.walk(conn_dir):
            for f in files:
                if f.endswith(".item"):
                    item_path = Path(root) / f
                    try:
                        tree = etree.parse(str(item_path))
                        xml_root = tree.getroot()
                        label = xml_root.get("label", xml_root.get("name", ""))
                        if label == connection_name or connection_name in f:
                            properties = {}
                            for attr_name, attr_val in xml_root.attrib.items():
                                if any(rk in attr_name for rk in REDACT_FIELDS):
                                    properties[attr_name] = "***REDACTED***"
                                else:
                                    properties[attr_name] = attr_val

                            conn_type = xml_root.get(
                                "{http://www.w3.org/2001/XMLSchema-instance}type", "unknown"
                            )

                            return json_response({
                                "name": label,
                                "type": conn_type,
                                "file": f,
                                "properties": properties,
                            })
                    except Exception:
                        continue

        return error_response(f"Connection not found: {connection_name}", "NOT_FOUND")
