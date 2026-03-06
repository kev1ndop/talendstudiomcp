"""templates://library — Library of job templates."""

from __future__ import annotations

import json

# Built-in templates for common ETL patterns
TEMPLATES = [
    {
        "id": "csv_to_db",
        "name": "CSV to Database",
        "description": "Read a CSV file and load into a database table",
        "components": ["tFileInputDelimited", "tMap", "tDBOutput"],
        "pattern": "source_to_target",
    },
    {
        "id": "db_to_db",
        "name": "Database to Database",
        "description": "Extract from one database and load into another",
        "components": ["tDBInput", "tMap", "tDBOutput"],
        "pattern": "source_to_target",
    },
    {
        "id": "scd2",
        "name": "Slowly Changing Dimension Type 2",
        "description": "SCD2 pattern with history tracking",
        "components": ["tDBInput", "tMap", "tDBSCD"],
        "pattern": "dimensional",
    },
    {
        "id": "cdc",
        "name": "Change Data Capture",
        "description": "Capture and process only changed records",
        "components": ["tDBInput", "tMap", "tDBOutput", "tJavaRow"],
        "pattern": "incremental",
    },
    {
        "id": "lookup_enrichment",
        "name": "Lookup Enrichment",
        "description": "Enrich main flow with lookup data from a reference table",
        "components": ["tDBInput", "tMap", "tDBInput", "tDBOutput"],
        "pattern": "enrichment",
    },
    {
        "id": "file_watcher",
        "name": "File Watcher and Processor",
        "description": "Watch a directory for new files and process each one",
        "components": ["tFileList", "tFileInputDelimited", "tMap", "tDBOutput", "tFileCopy"],
        "pattern": "file_processing",
    },
    {
        "id": "api_to_db",
        "name": "REST API to Database",
        "description": "Fetch data from a REST API and store in a database",
        "components": ["tRESTClient", "tExtractJSONFields", "tMap", "tDBOutput"],
        "pattern": "api_integration",
    },
    {
        "id": "data_quality",
        "name": "Data Quality Check",
        "description": "Profile and validate data with reject handling",
        "components": ["tDBInput", "tFilterRow", "tDBOutput", "tFileOutputDelimited", "tLogRow"],
        "pattern": "quality",
    },
    {
        "id": "master_job",
        "name": "Master/Orchestration Job",
        "description": "Parent job that orchestrates multiple child jobs",
        "components": ["tPreJob", "tRunJob", "tRunJob", "tRunJob", "tPostJob"],
        "pattern": "orchestration",
    },
    {
        "id": "parallel_load",
        "name": "Parallel Bulk Load",
        "description": "Load large datasets in parallel threads",
        "components": ["tDBInput", "tFlowToIterate", "tParallelize", "tDBOutput"],
        "pattern": "performance",
    },
]


def register(mcp, services):
    @mcp.resource("templates://library")
    async def template_library() -> str:
        """Library of pre-built job templates for common ETL patterns."""
        return json.dumps({
            "templates": TEMPLATES,
            "total": len(TEMPLATES),
            "note": "Use job_create_from_template tool (Phase 2) to create jobs from templates.",
        }, indent=2)
