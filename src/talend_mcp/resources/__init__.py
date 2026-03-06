"""Resource auto-discovery and registration."""

import importlib
import pkgutil
from pathlib import Path


def register_all_resources(mcp, services):
    """Auto-discover and register all resource modules."""
    resources_dir = Path(__file__).parent
    for _importer, modname, _ispkg in pkgutil.iter_modules([str(resources_dir)]):
        module = importlib.import_module(f"talend_mcp.resources.{modname}")
        if hasattr(module, "register"):
            module.register(mcp, services)
