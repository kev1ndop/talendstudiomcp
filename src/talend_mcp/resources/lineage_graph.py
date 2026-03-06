"""lineage://graph — Lineage graph of the project (stub for Phase 1)."""

from __future__ import annotations

import json


def register(mcp, services):
    @mcp.resource("lineage://graph")
    async def lineage_graph() -> str:
        """Project lineage graph (Phase 1: basic component-level dependencies).

        Full table-level lineage is planned for Phase 4.
        """
        # In Phase 1, provide basic dependency info from the index
        await services.index.ensure_indexed()

        edges = []
        for job_name, info in services.index._jobs.items():
            for subjob in info.get("subjobs", []):
                edges.append({"from": job_name, "to": subjob, "type": "subjob"})

        return json.dumps({
            "edges": edges[:200],
            "total_edges": len(edges),
            "total_jobs": len(services.index._jobs),
            "note": "Phase 1 lineage: subjob dependencies only. Full table lineage in Phase 4.",
        }, indent=2)
