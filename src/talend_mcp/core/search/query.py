"""Text search utilities for workspace content."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


async def search_in_files(
    directory: Path,
    pattern: str,
    extensions: list[str] | None = None,
    max_results: int = 50,
) -> list[dict[str, Any]]:
    """Search for a text pattern in files within a directory.

    Args:
        directory: Root directory to search
        pattern: Text to search for (case-insensitive)
        extensions: File extensions to include (e.g. ['.item', '.java'])
        max_results: Maximum number of results to return
    """
    exts = set(extensions or [".item", ".properties", ".java"])
    results = []
    pattern_lower = pattern.lower()

    for root, _dirs, files in os.walk(directory):
        for f in files:
            if not any(f.endswith(ext) for ext in exts):
                continue

            file_path = Path(root) / f
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if pattern_lower in content.lower():
                    # Find the matching line(s)
                    lines = content.splitlines()
                    matches = []
                    for i, line in enumerate(lines, 1):
                        if pattern_lower in line.lower():
                            matches.append({"line": i, "text": line.strip()[:200]})
                            if len(matches) >= 3:
                                break

                    results.append({
                        "file": str(file_path),
                        "name": f,
                        "matches": matches,
                    })

                    if len(results) >= max_results:
                        return results
            except Exception:
                continue

    return results
