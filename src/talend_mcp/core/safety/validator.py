"""XML validation for Talend .item files."""

from __future__ import annotations

from pathlib import Path

from lxml import etree


class XmlValidator:
    """Validate Talend job XML files before saving modifications."""

    async def validate_item(self, item_path: Path) -> dict:
        """Validate that a .item file is well-formed XML with expected structure.

        Returns a dict with 'valid' bool and 'errors' list.
        """
        errors = []

        # Check file exists
        if not item_path.is_file():
            return {"valid": False, "errors": [f"File not found: {item_path}"]}

        # Check well-formed XML
        try:
            tree = etree.parse(str(item_path))
            root = tree.getroot()
        except etree.XMLSyntaxError as e:
            return {"valid": False, "errors": [f"XML syntax error: {e}"]}

        # Check basic Talend job structure
        tag = root.tag
        if "ProcessType" not in tag and "Process" not in tag:
            # Root should be talendfile:ProcessType or similar
            errors.append(f"Unexpected root element: {tag}")

        # Check that nodes have componentName attributes
        nodes = list(root.iter("node"))
        for node in nodes:
            if not node.get("componentName"):
                errors.append(
                    f"Node missing componentName at position "
                    f"({node.get('posX', '?')}, {node.get('posY', '?')})"
                )

        # Check that connections reference valid sources/targets
        node_names = set()
        for node in nodes:
            for ep in node.iter("elementParameter"):
                if ep.get("name") == "UNIQUE_NAME":
                    node_names.add(ep.get("value", ""))

        for conn in root.iter("connection"):
            src = conn.get("source", "")
            tgt = conn.get("target", "")
            if src and src not in node_names:
                errors.append(f"Connection references unknown source: {src}")
            if tgt and tgt not in node_names:
                errors.append(f"Connection references unknown target: {tgt}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "node_count": len(nodes),
            "connection_count": len(list(root.iter("connection"))),
        }

    async def validate_xml_string(self, xml_content: str) -> dict:
        """Validate an XML string without writing to disk."""
        try:
            root = etree.fromstring(xml_content.encode("utf-8"))
            return {"valid": True, "errors": [], "root_tag": root.tag}
        except etree.XMLSyntaxError as e:
            return {"valid": False, "errors": [f"XML syntax error: {e}"]}
