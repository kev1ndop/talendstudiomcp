"""Rollback mechanism for reverting failed modifications."""

from __future__ import annotations

from pathlib import Path

from talend_mcp.core.safety.backup import BackupManager


class RollbackManager:
    """Manage rollback operations using backup files."""

    def __init__(self, backup_manager: BackupManager):
        self._backup = backup_manager

    async def rollback_file(self, backup_path: Path, target_path: Path) -> None:
        """Restore a single file from its backup."""
        await self._backup.restore_file(backup_path, target_path)

    async def rollback_job(self, backup_paths: list[Path], target_dir: Path) -> list[str]:
        """Restore all files of a job from backup.

        Args:
            backup_paths: List of backup file paths (from backup_job result)
            target_dir: The directory where the job files should be restored
        """
        restored = []
        for bp in backup_paths:
            target = target_dir / bp.name
            await self._backup.restore_file(bp, target)
            restored.append(str(target))
        return restored
