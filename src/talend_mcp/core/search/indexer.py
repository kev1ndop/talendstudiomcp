"""Lazy incremental indexer for Talend project artifacts."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from lxml import etree


class ProjectIndex:
    """In-memory search index for Talend project artifacts.

    Builds lazily on first query, then incrementally updates
    based on file modification times. Designed for projects with 500+ jobs.
    """

    def __init__(self, workspace_path: Path, project: str):
        self._workspace = workspace_path
        self._project = project
        self._project_path = workspace_path / project
        self._jobs: dict[str, dict[str, Any]] = {}
        self._components_usage: dict[str, int] = {}
        self._connections_index: dict[str, list[str]] = {}
        self._last_indexed: float = 0
        self._indexed = False

    async def ensure_indexed(self):
        """Build or refresh the index if needed."""
        if not self._indexed or (time.time() - self._last_indexed) > 30:
            await self._build_index()

    async def _build_index(self):
        """Scan the process directory and build the search index."""
        process_dir = self._project_path / "process"
        if not process_dir.is_dir():
            return

        self._jobs.clear()
        self._components_usage.clear()
        self._connections_index.clear()

        for root, _dirs, files in os.walk(process_dir):
            for f in files:
                if not f.endswith(".item"):
                    continue
                item_path = Path(root) / f
                try:
                    self._index_job(item_path, process_dir)
                except Exception:
                    continue  # Skip unparseable files

        self._last_indexed = time.time()
        self._indexed = True

    def _index_job(self, item_path: Path, process_dir: Path):
        """Index a single job file."""
        tree = etree.parse(str(item_path))
        root = tree.getroot()

        stem = item_path.stem
        parts = stem.rsplit("_", 1)
        name = parts[0] if len(parts) == 2 else stem
        version = parts[1] if len(parts) == 2 else "0.1"
        folder = str(item_path.parent.relative_to(process_dir))
        if folder == ".":
            folder = ""

        components = []
        subjobs = []
        connection_refs = []

        for node in root.iter("node"):
            comp_name = node.get("componentName", "")
            if comp_name:
                components.append(comp_name)
                self._components_usage[comp_name] = (
                    self._components_usage.get(comp_name, 0) + 1
                )

                # Track tRunJob references
                if comp_name == "tRunJob":
                    for ep in node.iter("elementParameter"):
                        if ep.get("name") == "PROCESS":
                            subjobs.append(ep.get("value", ""))

                # Track database connection references
                if comp_name.startswith("tDB") or comp_name.startswith("tMySQL") or \
                   comp_name.startswith("tOracle") or comp_name.startswith("tPostgre"):
                    for ep in node.iter("elementParameter"):
                        if ep.get("name") in ("PROPERTY:REPOSITORY_PROPERTY_TYPE", "CONNECTION"):
                            val = ep.get("value", "")
                            if val:
                                connection_refs.append(val)
                                self._connections_index.setdefault(val, []).append(name)

        self._jobs[name] = {
            "name": name,
            "version": version,
            "folder": folder,
            "path": str(item_path),
            "components": components,
            "subjobs": subjobs,
            "connection_refs": connection_refs,
        }

    async def search_jobs(
        self,
        query: str | None = None,
        component: str | None = None,
        connection: str | None = None,
    ) -> list[dict]:
        """Search indexed jobs by name, component, or connection."""
        await self.ensure_indexed()

        results = list(self._jobs.values())

        if query:
            q = query.lower()
            results = [j for j in results if q in j["name"].lower()]

        if component:
            results = [j for j in results if component in j["components"]]

        if connection:
            results = [j for j in results if connection in j["connection_refs"]]

        return results

    async def get_component_usage(self) -> dict[str, int]:
        """Get component usage statistics across all indexed jobs."""
        await self.ensure_indexed()
        return dict(sorted(self._components_usage.items(), key=lambda x: -x[1]))

    async def get_jobs_using_connection(self, connection_id: str) -> list[str]:
        """Find all jobs that reference a specific connection."""
        await self.ensure_indexed()
        return self._connections_index.get(connection_id, [])

    async def get_job_dependents(self, job_name: str) -> list[str]:
        """Find all jobs that call this job as a subjob (reverse dependency)."""
        await self.ensure_indexed()
        dependents = []
        for name, info in self._jobs.items():
            if job_name in info.get("subjobs", []):
                dependents.append(name)
        return dependents
