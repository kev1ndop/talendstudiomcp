"""job_get — Get full parsed job definition."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response


def register(mcp, services):
    @mcp.tool()
    async def job_get(
        job_name: str,
        project: str | None = None,
        version: str | None = None,
    ) -> str:
        """Get the full parsed definition of a Talend job.

        Returns components, connections, schemas, and context parameters
        parsed from the job's .item XML file.

        Args:
            job_name: Name of the job to retrieve
            project: Project name (uses default if omitted)
            version: Specific version (e.g. '0.1'). Latest if omitted
        """
        services.audit.log("job_get", {"job_name": job_name, "project": project})
        try:
            job_files = await services.workspace.get_job_files(project, job_name, version)
            job = await services.xml_parser.parse_item(job_files.item_path)

            # Enrich with properties
            try:
                props = await services.properties_parser.parse(job_files.properties_path)
                job.purpose = props.purpose
                job.description = props.description
                job.author = props.author
                job.status = props.status
            except Exception:
                pass  # Properties file may not exist

            return json_response({
                "name": job.name,
                "version": job.version,
                "purpose": job.purpose,
                "description": job.description,
                "author": job.author,
                "status": job.status,
                "folder": job_files.folder,
                "components": [c.model_dump() for c in job.components],
                "connections": [c.model_dump() for c in job.connections],
                "context_parameters": job.context_parameters,
                "subjobs": job.subjobs,
                "component_count": len(job.components),
                "connection_count": len(job.connections),
            })
        except FileNotFoundError as e:
            return error_response(str(e), "NOT_FOUND")
