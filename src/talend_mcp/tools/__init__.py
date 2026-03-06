"""Tool auto-discovery and registration."""

import importlib
import pkgutil
from pathlib import Path


def register_all_tools(mcp, services):
    """Auto-discover and register all tool modules in subdirectories."""
    tools_dir = Path(__file__).parent
    for domain_dir in sorted(tools_dir.iterdir()):
        if domain_dir.is_dir() and not domain_dir.name.startswith("_"):
            pkg = f"talend_mcp.tools.{domain_dir.name}"
            for _importer, modname, _ispkg in pkgutil.iter_modules([str(domain_dir)]):
                module = importlib.import_module(f"{pkg}.{modname}")
                if hasattr(module, "register"):
                    module.register(mcp, services)
