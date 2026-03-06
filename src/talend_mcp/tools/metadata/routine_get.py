"""routine_get — View source code of a Java routine."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def routine_get(
        routine_name: str,
        project: str | None = None,
    ) -> str:
        """View the Java source code of a routine.

        Args:
            routine_name: Name of the routine (without .java extension)
            project: Project name (uses default if omitted)
        """
        services.audit.log("routine_get", {"routine_name": routine_name, "project": project})
        try:
            source = await services.workspace.get_routine_source(project, routine_name)
            if len(source) > 50000:
                source = source[:50000] + "\n// ... (truncated)"

            return json_response({
                "routine_name": routine_name,
                "source_code": source,
                "length": len(source),
            })
        except FileNotFoundError as e:
            return error_response(str(e), "NOT_FOUND")
