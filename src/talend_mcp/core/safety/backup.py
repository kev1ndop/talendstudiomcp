"""Automatic backup of Talend artifacts before modifications."""

from __future__ import annotations

import shutil
import time
from pathlib import Path


class BackupManager:
    """Create and manage backups of .item files before modifications.

    Backups are stored in {workspace}/.talend-mcp-backups/{timestamp}/
    """

    def __init__(self, workspace_path: Path):
        self._backup_root = workspace_path / ".talend-mcp-backups"
        self._backup_root.mkdir(parents=True, exist_ok=True)

    async def backup_file(self, file_path: Path) -> Path:
        """Create a timestamped backup of a single file. Returns the backup path."""
        ts = time.strftime("%Y%m%d_%H%M%S")
        rel = file_path.name
        backup_dir = self._backup_root / ts
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / rel
        shutil.copy2(str(file_path), str(backup_path))
        return backup_path

    async def backup_job(self, item_path: Path) -> list[Path]:
        """Backup all three files of a job (.item, .properties, .screenshot)."""
        backed_up = []
        base = item_path.parent
        stem = item_path.stem  # e.g. MyJob_0.1

        for ext in [".item", ".properties", ".screenshot"]:
            candidate = base / f"{stem}{ext}"
            if candidate.is_file():
                bp = await self.backup_file(candidate)
                backed_up.append(bp)
        return backed_up

    async def list_backups(self, limit: int = 20) -> list[dict]:
        """List recent backups."""
        if not self._backup_root.is_dir():
            return []
        dirs = sorted(self._backup_root.iterdir(), reverse=True)[:limit]
        result = []
        for d in dirs:
            if d.is_dir():
                files = [f.name for f in d.iterdir() if f.is_file()]
                result.append({
                    "timestamp": d.name,
                    "path": str(d),
                    "files": files,
                })
        return result

    async def restore_file(self, backup_path: Path, target_path: Path) -> None:
        """Restore a file from backup to its original location."""
        shutil.copy2(str(backup_path), str(target_path))
