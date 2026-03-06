"""Wrapper for the Talend Studio CommandLine tool."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CommandLineWrapper:
    """Async wrapper around Talend Studio's CommandLine tool.

    Supports headless job building, export, and other CLI operations.
    Used in Phase 3+ for execution tools.
    """

    def __init__(self, studio_path: Path | None = None, java_home: Path | None = None):
        self.studio_path = studio_path
        self.java_home = java_home
        self._cmd = self._resolve_commandline()

    def _resolve_commandline(self) -> str | None:
        """Find the commandline executable."""
        if not self.studio_path:
            return None
        # Linux
        sh = self.studio_path / "commandline.sh"
        if sh.is_file():
            return str(sh)
        # Windows
        bat = self.studio_path / "commandline.bat"
        if bat.is_file():
            return str(bat)
        return None

    @property
    def is_available(self) -> bool:
        return self._cmd is not None

    async def build_job(
        self,
        project_name: str,
        job_name: str,
        version: str = "Latest",
        output_dir: str = "/tmp/talend-builds",
        timeout_ms: int = 300000,
    ) -> dict:
        """Build a job into a deployable archive using CommandLine.

        Phase 3 implementation — returns structured result.
        """
        if not self.is_available:
            return {"error": "CommandLine tool not configured", "available": False}

        args = [
            self._cmd,
            "buildJob",
            job_name,
            "-dd", output_dir,
            "-af", f"{job_name}_{version}",
            "-jv", version,
        ]

        return await self._run(args, timeout_ms=timeout_ms)

    async def export_job(
        self,
        project_name: str,
        job_name: str,
        output_file: str,
        timeout_ms: int = 300000,
    ) -> dict:
        """Export a job to a ZIP file."""
        if not self.is_available:
            return {"error": "CommandLine tool not configured", "available": False}

        args = [
            self._cmd,
            "exportJob",
            job_name,
            "-dd", str(Path(output_file).parent),
            "-af", str(Path(output_file).stem),
        ]

        return await self._run(args, timeout_ms=timeout_ms)

    async def _run(self, args: list[str], timeout_ms: int = 120000) -> dict:
        """Execute a command and return structured result."""
        env = {}
        if self.java_home:
            env["JAVA_HOME"] = str(self.java_home)

        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env if env else None,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_ms / 1000
            )
            return {
                "returncode": proc.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "success": proc.returncode == 0,
            }
        except asyncio.TimeoutError:
            logger.error("CommandLine execution timed out after %dms", timeout_ms)
            return {"error": "Timeout", "timeout_ms": timeout_ms, "success": False}
        except Exception as e:
            logger.error("CommandLine execution failed: %s", e)
            return {"error": str(e), "success": False}
