"""component_usage_stats — Component usage statistics across the project."""

from __future__ import annotations

from talend_mcp.tools._base import json_response


def register(mcp, services):
    @mcp.tool()
    async def component_usage_stats(
        project: str | None = None,
        top_n: int = 30,
    ) -> str:
        """Show which components are used most across all jobs in the project.

        Helps understand the project's technology profile and identify
        key components that affect the most jobs.

        Args:
            project: Project name (uses default if omitted)
            top_n: Number of top components to return (default 30)
        """
        services.audit.log("component_usage_stats", {"project": project, "top_n": top_n})

        usage = await services.index.get_component_usage()

        sorted_usage = sorted(usage.items(), key=lambda x: -x[1])
        top = sorted_usage[:top_n]

        # Categorize
        categories = {}
        for name, count in sorted_usage:
            if name.startswith("tDB") or name.startswith("tMySQL") or \
               name.startswith("tOracle") or name.startswith("tPostgre") or \
               name.startswith("tMSSql"):
                cat = "Database"
            elif name.startswith("tFile"):
                cat = "File"
            elif name in ("tMap", "tJoin", "tUnite", "tSortRow", "tAggregateRow",
                          "tFilterRow", "tNormalize", "tDenormalize", "tUniqRow"):
                cat = "Processing"
            elif name.startswith("tS3") or name.startswith("tAzure") or \
                 name.startswith("tRedshift") or name.startswith("tBigQuery") or \
                 name.startswith("tSnowflake"):
                cat = "Cloud"
            elif name in ("tRunJob", "tPreJob", "tPostJob", "tFlowToIterate"):
                cat = "Orchestration"
            elif name.startswith("tJava"):
                cat = "Custom Code"
            elif name.startswith("tLog") or name == "tStatCatcher":
                cat = "Logging"
            else:
                cat = "Other"
            categories.setdefault(cat, 0)
            categories[cat] += count

        return json_response({
            "top_components": [{"name": n, "count": c} for n, c in top],
            "categories": dict(sorted(categories.items(), key=lambda x: -x[1])),
            "total_unique_components": len(usage),
            "total_component_instances": sum(usage.values()),
        })
