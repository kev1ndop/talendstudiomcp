"""job_dependencies — What subjobs/routines does a job use."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def job_dependencies(
        job_name: str,
        project: str | None = None,
        version: str | None = None,
    ) -> str:
        """Show all dependencies of a job: subjobs called via tRunJob and routines used.

        Args:
            job_name: Name of the job
            project: Project name (uses default if omitted)
            version: Specific version (optional)
        """
        services.audit.log("job_dependencies", {"job_name": job_name, "project": project})
        try:
            job_files = await services.workspace.get_job_files(project, job_name, version)
            job = await services.xml_parser.parse_item(job_files.item_path)

            # Extract routine references from tJava/tJavaRow components
            routine_refs = set()
            for comp in job.components:
                if comp.component_name in ("tJava", "tJavaRow", "tJavaFlex"):
                    code_param = comp.parameters.get("CODE", {})
                    if isinstance(code_param, dict):
                        code = code_param.get("value", "")
                        # Simple heuristic: look for routine. references
                        import re
                        refs = re.findall(r"routines\.(\w+)\.", code)
                        routine_refs.update(refs)

            # Extract connection references
            connection_refs = set()
            for comp in job.components:
                repo_type = comp.parameters.get("PROPERTY:REPOSITORY_PROPERTY_TYPE", {})
                if isinstance(repo_type, dict) and repo_type.get("value"):
                    connection_refs.add(repo_type["value"])

            return json_response({
                "job_name": job_name,
                "subjobs": job.subjobs,
                "routines": sorted(routine_refs),
                "connections": sorted(connection_refs),
                "component_types": sorted(set(c.component_name for c in job.components)),
            })
        except FileNotFoundError as e:
            return error_response(str(e), "NOT_FOUND")
