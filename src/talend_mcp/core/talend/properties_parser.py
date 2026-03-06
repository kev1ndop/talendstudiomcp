"""Parse Talend .properties XML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lxml import etree


class JobProperties:
    """Parsed job properties."""

    def __init__(
        self,
        label: str,
        version: str,
        purpose: str = "",
        description: str = "",
        status: str = "",
        author: str = "",
        creation_date: str = "",
        modification_date: str = "",
        item_type: str = "",
        path: str = "",
        additional: dict[str, Any] | None = None,
    ):
        self.label = label
        self.version = version
        self.purpose = purpose
        self.description = description
        self.status = status
        self.author = author
        self.creation_date = creation_date
        self.modification_date = modification_date
        self.item_type = item_type
        self.path = path
        self.additional = additional or {}


class PropertiesParser:
    """Parse Talend .properties files (XML format)."""

    async def parse(self, properties_path: Path) -> JobProperties:
        """Parse a .properties XML file and return structured data."""
        tree = etree.parse(str(properties_path))
        root = tree.getroot()

        # Properties files use TalendProperties namespace
        # The root element is typically <TalendProperties:Property>
        label = root.get("label", "")
        version = root.get("version", "0.1")
        purpose = root.get("purpose", "")
        description = root.get("description", "")
        status = root.get("statusCode", "")

        author_el = root.find("author")
        author = ""
        if author_el is not None:
            author = author_el.get("login", "")

        creation_date = root.get("creationDate", "")
        modification_date = root.get("modificationDate", "")

        item = root.find("item")
        item_type = ""
        path = ""
        if item is not None:
            xsi_type = item.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")
            item_type = xsi_type
            path = item.get("state", {})

        additional: dict[str, Any] = {}
        for prop in root.iter("additionalProperties"):
            key = prop.get("key", "")
            value = prop.get("value", "")
            if key:
                additional[key] = value

        return JobProperties(
            label=label,
            version=version,
            purpose=purpose,
            description=description,
            status=status,
            author=author,
            creation_date=creation_date,
            modification_date=modification_date,
            item_type=item_type,
            path=path,
            additional=additional,
        )
