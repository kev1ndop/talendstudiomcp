"""component_search — Search components by name or category."""

from __future__ import annotations

from talend_mcp.tools._base import json_response

# Common Talend component categories for reference
COMPONENT_CATEGORIES = {
    "Database": ["tDBInput", "tDBOutput", "tDBConnection", "tDBCommit", "tDBClose", "tDBRow",
                  "tMySQLInput", "tMySQLOutput", "tOracleInput", "tOracleOutput",
                  "tPostgresqlInput", "tPostgresqlOutput", "tMSSqlInput", "tMSSqlOutput"],
    "File": ["tFileInputDelimited", "tFileOutputDelimited", "tFileInputExcel",
             "tFileOutputExcel", "tFileInputJSON", "tFileOutputJSON",
             "tFileInputXML", "tFileOutputXML", "tFileList", "tFileCopy", "tFileDelete"],
    "Processing": ["tMap", "tJoin", "tUnite", "tSortRow", "tAggregateRow",
                    "tFilterRow", "tNormalize", "tDenormalize", "tReplicate",
                    "tUniqRow", "tSampleRow"],
    "Cloud": ["tS3Connection", "tS3Input", "tS3Output", "tAzureStorageInput",
              "tRedshiftInput", "tRedshiftOutput", "tBigQueryInput", "tBigQueryOutput",
              "tSnowflakeInput", "tSnowflakeOutput"],
    "Orchestration": ["tRunJob", "tPreJob", "tPostJob", "tJava", "tJavaRow",
                       "tJavaFlex", "tWarn", "tDie", "tLogRow", "tFlowToIterate"],
    "Messaging": ["tKafkaInput", "tKafkaOutput", "tJMSInput", "tJMSOutput",
                   "tActiveMQInput"],
    "API": ["tRESTClient", "tRESTRequest", "tRESTResponse", "tSOAP"],
    "Logs": ["tLogRow", "tLog4j", "tStatCatcher", "tFlowMeter"],
}


def register(mcp, services):
    @mcp.tool()
    async def component_search(
        query: str,
        include_reference: bool = False,
    ) -> str:
        """Search for Talend components by name or category.

        Searches both components used in the project and the reference library
        of known Talend components.

        Args:
            query: Component name or category to search (e.g. 'tDBInput', 'database', 'file')
            include_reference: Include known components from reference library (not just used ones)
        """
        services.audit.log("component_search", {"query": query})
        q = query.lower()

        # Search in project usage
        usage = await services.index.get_component_usage()
        project_matches = [
            {"name": name, "usage_count": count, "source": "project"}
            for name, count in usage.items()
            if q in name.lower()
        ]

        # Search in reference library
        ref_matches = []
        if include_reference:
            for category, components in COMPONENT_CATEGORIES.items():
                if q in category.lower():
                    for comp in components:
                        ref_matches.append({
                            "name": comp,
                            "category": category,
                            "source": "reference",
                        })
                else:
                    for comp in components:
                        if q in comp.lower():
                            ref_matches.append({
                                "name": comp,
                                "category": category,
                                "source": "reference",
                            })

        return json_response({
            "project_matches": project_matches,
            "reference_matches": ref_matches,
            "total": len(project_matches) + len(ref_matches),
        })
