"""Workspace discovery and navigation for Talend projects."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from talend_mcp.core.talend.item_types import JobFiles, ProjectInfo


class WorkspaceService:
    """Discover and navigate Talend workspace artifacts with lazy loading and caching."""

    def __init__(self, workspace_path: Path, default_project: str = ""):
        self.workspace_path = workspace_path
        self.default_project = default_project
        self._cache: dict[str, Any] = {}
        self._cache_mtime: dict[str, float] = {}
        self._cache_ttl = 5.0  # seconds

    def _resolve_project(self, project: str | None) -> str:
        """Resolve project name, falling back to default."""
        return project or self.default_project

    def _project_path(self, project: str) -> Path:
        """Get the root path of a project within the workspace."""
        return self.workspace_path / project

    def _is_cache_valid(self, key: str) -> bool:
        return key in self._cache and (time.time() - self._cache_mtime.get(key, 0)) < self._cache_ttl

    async def get_project_info(self, project: str | None = None) -> ProjectInfo:
        """Get high-level project metadata with artifact counts."""
        proj = self._resolve_project(project)
        proj_path = self._project_path(proj)

        if not proj_path.is_dir():
            raise FileNotFoundError(f"Project directory not found: {proj_path}")

        return ProjectInfo(
            project_name=proj,
            workspace_path=str(self.workspace_path),
            technical_name=proj,
            job_count=self._count_items(proj_path / "process", ".item"),
            connection_count=self._count_items(proj_path / "metadata" / "connections", ".item"),
            schema_count=self._count_items(proj_path / "metadata", ".item"),
            context_count=self._count_items(proj_path / "context", ".item"),
            routine_count=self._count_files(proj_path / "code" / "routines", ".java"),
        )

    async def list_jobs(
        self,
        project: str | None = None,
        offset: int = 0,
        limit: int = 50,
        folder: str | None = None,
        name_filter: str | None = None,
    ) -> dict:
        """List jobs with pagination and optional filtering."""
        proj = self._resolve_project(project)
        process_dir = self._project_path(proj) / "process"

        if not process_dir.is_dir():
            return {"items": [], "total": 0, "offset": offset, "limit": limit, "has_more": False}

        cache_key = f"jobs:{proj}"
        if not self._is_cache_valid(cache_key):
            jobs = self._scan_items(process_dir, ".item")
            self._cache[cache_key] = jobs
            self._cache_mtime[cache_key] = time.time()

        jobs = self._cache[cache_key]

        if folder:
            jobs = [j for j in jobs if j["folder"].startswith(folder)]
        if name_filter:
            name_lower = name_filter.lower()
            jobs = [j for j in jobs if name_lower in j["name"].lower()]

        total = len(jobs)
        page = jobs[offset : offset + limit]
        return {
            "items": page,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total,
        }

    async def get_job_files(
        self, project: str | None, job_name: str, version: str | None = None
    ) -> JobFiles:
        """Find the .item, .properties, and .screenshot files for a job."""
        proj = self._resolve_project(project)
        process_dir = self._project_path(proj) / "process"

        # Search for the job by name (may be in a subfolder)
        for root, _dirs, files in os.walk(process_dir):
            for f in files:
                if f.endswith(".item"):
                    # Filename format: JobName_VERSION.item
                    stem = f[:-5]  # remove .item
                    parts = stem.rsplit("_", 1)
                    if len(parts) == 2:
                        name, ver = parts
                    else:
                        name, ver = stem, "0.1"

                    if name == job_name and (version is None or ver == version):
                        root_path = Path(root)
                        rel_folder = str(root_path.relative_to(process_dir))
                        return JobFiles(
                            item_path=root_path / f,
                            properties_path=root_path / f.replace(".item", ".properties"),
                            screenshot_path=root_path / f.replace(".item", ".screenshot"),
                            job_name=name,
                            version=ver,
                            folder=rel_folder if rel_folder != "." else "",
                        )

        raise FileNotFoundError(f"Job not found: {job_name} (version={version}) in project {proj}")

    async def list_artifacts(
        self,
        project: str | None = None,
        artifact_type: str = "all",
        offset: int = 0,
        limit: int = 100,
    ) -> dict:
        """List workspace artifacts by type (jobs, connections, schemas, contexts, routines)."""
        proj = self._resolve_project(project)
        proj_path = self._project_path(proj)

        artifacts = []
        type_dirs = {
            "jobs": ("process", ".item"),
            "connections": ("metadata/connections", ".item"),
            "schemas": ("metadata", ".item"),
            "contexts": ("context", ".item"),
            "routines": ("code/routines", ".java"),
        }

        if artifact_type == "all":
            for atype, (subdir, ext) in type_dirs.items():
                items = self._scan_items(proj_path / subdir, ext)
                for item in items:
                    item["type"] = atype
                artifacts.extend(items)
        elif artifact_type in type_dirs:
            subdir, ext = type_dirs[artifact_type]
            artifacts = self._scan_items(proj_path / subdir, ext)
            for item in artifacts:
                item["type"] = artifact_type

        total = len(artifacts)
        page = artifacts[offset : offset + limit]
        return {
            "items": page,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total,
        }

    async def list_connections(self, project: str | None = None) -> list[dict]:
        """List connection metadata items."""
        proj = self._resolve_project(project)
        conn_dir = self._project_path(proj) / "metadata" / "connections"
        if not conn_dir.is_dir():
            return []
        return self._scan_items(conn_dir, ".item")

    async def list_contexts(self, project: str | None = None) -> list[dict]:
        """List context group items."""
        proj = self._resolve_project(project)
        ctx_dir = self._project_path(proj) / "context"
        if not ctx_dir.is_dir():
            return []
        return self._scan_items(ctx_dir, ".item")

    async def list_routines(self, project: str | None = None) -> list[dict]:
        """List Java routine files."""
        proj = self._resolve_project(project)
        routines_dir = self._project_path(proj) / "code" / "routines"
        if not routines_dir.is_dir():
            return []
        return self._scan_items(routines_dir, ".java")

    async def get_routine_source(self, project: str | None, routine_name: str) -> str:
        """Read the source code of a Java routine."""
        proj = self._resolve_project(project)
        routines_dir = self._project_path(proj) / "code" / "routines"

        for root, _dirs, files in os.walk(routines_dir):
            for f in files:
                if f.endswith(".java") and f[:-5] == routine_name:
                    return (Path(root) / f).read_text(encoding="utf-8")

        raise FileNotFoundError(f"Routine not found: {routine_name}")

    async def find_generated_java(self, project: str | None, job_name: str) -> str | None:
        """Find and return generated Java code for a job (if it exists in poms/jobs)."""
        proj = self._resolve_project(project)
        proj_path = self._project_path(proj)

        # Talend 8.x generates Java under poms/jobs/process/
        poms_dir = proj_path / "poms" / "jobs" / "process"
        if not poms_dir.is_dir():
            return None

        for root, _dirs, files in os.walk(poms_dir):
            for f in files:
                if f.endswith(".java") and job_name.lower() in f.lower():
                    return (Path(root) / f).read_text(encoding="utf-8")
        return None

    def _scan_items(self, directory: Path, extension: str) -> list[dict]:
        """Recursively scan a directory for files with the given extension."""
        if not directory.is_dir():
            return []

        items = []
        for root, _dirs, files in os.walk(directory):
            for f in sorted(files):
                if f.endswith(extension):
                    rel = Path(root).relative_to(directory)
                    stem = f[: -len(extension)]
                    # Parse name_version pattern
                    parts = stem.rsplit("_", 1)
                    if len(parts) == 2 and parts[1].replace(".", "").isdigit():
                        name, version = parts
                    else:
                        name, version = stem, ""

                    items.append({
                        "name": name,
                        "version": version,
                        "file": f,
                        "folder": str(rel) if str(rel) != "." else "",
                        "path": str(Path(root) / f),
                    })
        return items

    def _count_items(self, directory: Path, extension: str) -> int:
        """Count files with the given extension recursively."""
        if not directory.is_dir():
            return 0
        count = 0
        for _root, _dirs, files in os.walk(directory):
            count += sum(1 for f in files if f.endswith(extension))
        return count

    def _count_files(self, directory: Path, extension: str) -> int:
        """Alias for _count_items."""
        return self._count_items(directory, extension)
