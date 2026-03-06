"""Prompt auto-discovery and registration."""

import importlib
import pkgutil
from pathlib import Path


def register_all_prompts(mcp, services):
    """Auto-discover and register all prompt modules."""
    prompts_dir = Path(__file__).parent
    for _importer, modname, _ispkg in pkgutil.iter_modules([str(prompts_dir)]):
        module = importlib.import_module(f"talend_mcp.prompts.{modname}")
        if hasattr(module, "register"):
            module.register(mcp, services)
