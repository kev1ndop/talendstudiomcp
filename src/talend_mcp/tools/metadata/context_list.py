"""context_list — List context groups."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def context_list(project: str | None = None) -> str:
        """List all context groups defined in the project.

        Context groups contain environment-specific variables (e.g., DEV, STAGING, PROD).

        Args:
            project: Project name (uses default if omitted)
        """
        services.audit.log("context_list", {"project": project})
        try:
            contexts = await services.workspace.list_contexts(project)
            return json_response({
                "contexts": contexts,
                "total": len(contexts),
            })
        except Exception as e:
            return error_response(str(e))
