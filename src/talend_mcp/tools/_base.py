"""Base utilities for tool implementations."""

from __future__ import annotations

import json
from typing import Any


def paginate(items: list[Any], offset: int = 0, limit: int = 50) -> dict:
    """Apply pagination to a list of items and return a standardized response."""
    total = len(items)
    page = items[offset : offset + limit]
    return {
        "items": page,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": offset + limit < total,
    }


def json_response(data: Any) -> str:
    """Serialize data to a JSON string for MCP tool responses."""
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


def error_response(message: str, code: str = "ERROR") -> str:
    """Return a standardized error response."""
    return json.dumps({"error": code, "message": message}, indent=2)
