"""Parse and manipulate Talend .item XML files using lxml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lxml import etree

from talend_mcp.core.talend.item_types import (
    TalendComponent,
    TalendConnection,
    TalendJob,
)

# Common Talend XMI namespaces
TALEND_NS = {
    "xmi": "http://www.omg.org/XMI",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "TalendProperties": "TalendProperties",
}


class TalendXmlParser:
    """Parse Talend .item XML files into structured Python objects."""

    async def parse_item(self, item_path: Path) -> TalendJob:
        """Parse a .item XML file into a TalendJob model."""
        tree = etree.parse(str(item_path))
        root = tree.getroot()

        components = self._parse_components(root)
        connections = self._parse_connections(root)
        context_params = self._parse_context_parameters(root)
        subjobs = self._extract_subjob_references(components)

        return TalendJob(
            name=root.get("name", item_path.stem.rsplit("_", 1)[0]),
            version=root.get("version", "0.1"),
            components=components,
            connections=connections,
            context_parameters=context_params,
            subjobs=subjobs,
        )

    def _parse_components(self, root: etree._Element) -> list[TalendComponent]:
        """Extract all components (nodes) from the job XML."""
        components = []
        for node in root.iter("node"):
            comp = TalendComponent(
                unique_name=self._get_param(node, "UNIQUE_NAME", node.get("componentName", "")),
                component_name=node.get("componentName", ""),
                pos_x=int(node.get("posX", "0")),
                pos_y=int(node.get("posY", "0")),
                parameters=self._parse_element_parameters(node),
                metadata=self._parse_metadata(node),
            )
            components.append(comp)
        return components

    def _parse_connections(self, root: etree._Element) -> list[TalendConnection]:
        """Extract all connections between components."""
        connections = []
        for conn in root.iter("connection"):
            c = TalendConnection(
                connector_name=conn.get("connectorName", ""),
                label=conn.get("label", ""),
                line_style=int(conn.get("lineStyle", "0")),
                source=conn.get("source", ""),
                target=conn.get("target", ""),
                metadata_list=self._parse_metadata(conn),
            )
            connections.append(c)
        return connections

    def _parse_context_parameters(self, root: etree._Element) -> list[dict[str, str]]:
        """Extract context parameters defined in the job."""
        params = []
        for ctx in root.iter("context"):
            for param in ctx.iter("contextParameter"):
                params.append({
                    "name": param.get("name", ""),
                    "type": param.get("type", "id_String"),
                    "value": param.get("value", ""),
                    "prompt": param.get("prompt", ""),
                    "comment": param.get("comment", ""),
                })
        return params

    def _parse_element_parameters(self, element: etree._Element) -> dict[str, Any]:
        """Extract elementParameter children into a dict."""
        params = {}
        for ep in element.iter("elementParameter"):
            field = ep.get("field", "")
            name = ep.get("name", "")
            value = ep.get("value", "")
            if name:
                params[name] = {"value": value, "field": field}
        return params

    def _parse_metadata(self, element: etree._Element) -> list[dict[str, Any]]:
        """Extract metadata (schema) definitions from an element."""
        metadata_list = []
        for md in element.findall("metadata"):
            columns = []
            for col in md.iter("column"):
                columns.append({
                    "label": col.get("label", ""),
                    "talendType": col.get("talendType", ""),
                    "nullable": col.get("nullable", "true") == "true",
                    "length": col.get("length"),
                    "precision": col.get("precision"),
                    "key": col.get("key", "false") == "true",
                    "pattern": col.get("pattern"),
                    "comment": col.get("comment", ""),
                })
            metadata_list.append({
                "name": md.get("name", ""),
                "connector": md.get("connector", "FLOW"),
                "columns": columns,
            })
        return metadata_list

    def _get_param(self, node: etree._Element, param_name: str, default: str = "") -> str:
        """Get a specific elementParameter value from a node."""
        for ep in node.iter("elementParameter"):
            if ep.get("name") == param_name:
                return ep.get("value", default)
        return default

    def _extract_subjob_references(self, components: list[TalendComponent]) -> list[str]:
        """Find tRunJob references to extract subjob dependencies."""
        subjobs = []
        for comp in components:
            if comp.component_name == "tRunJob":
                process_name = comp.parameters.get("PROCESS", {})
                if isinstance(process_name, dict):
                    val = process_name.get("value", "")
                    # tRunJob stores the process ID, extract the readable name
                    if val:
                        subjobs.append(val)
        return subjobs

    async def parse_raw_xml(self, path: Path) -> str:
        """Return the raw XML content of a file as a string."""
        return path.read_text(encoding="utf-8")

    async def get_element_tree(self, path: Path) -> etree._ElementTree:
        """Parse and return the full lxml ElementTree (for advanced operations)."""
        return etree.parse(str(path))
