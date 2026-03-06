"""component_get_schema — View properties/parameters of a component type."""

from __future__ import annotations

from talend_mcp.tools._base import error_response, json_response

# Common component property schemas (reference data)
COMPONENT_SCHEMAS = {
    "tDBInput": {
        "description": "Read data from a database table or SQL query",
        "properties": {
            "CONNECTION": "Repository connection reference",
            "DBTABLE": "Table name to query",
            "QUERY": "SQL SELECT query",
            "TRIM_ALL_COLUMN": "Trim whitespace from all columns",
        },
        "inputs": [],
        "outputs": ["FLOW", "REJECT"],
    },
    "tDBOutput": {
        "description": "Write data to a database table",
        "properties": {
            "CONNECTION": "Repository connection reference",
            "DBTABLE": "Target table name",
            "DATA_ACTION": "INSERT, UPDATE, INSERT_OR_UPDATE, DELETE",
            "COMMIT_EVERY": "Commit interval",
        },
        "inputs": ["FLOW"],
        "outputs": ["FLOW", "REJECT"],
    },
    "tMap": {
        "description": "Transform and route data with visual mapping",
        "properties": {
            "MAPPING": "Visual mapping configuration",
            "INNER_JOIN": "Enable inner join filtering",
            "LOOKUP_MODEL": "LOAD_ONCE, RELOAD, NO_LOAD",
        },
        "inputs": ["main", "lookup1", "lookup2"],
        "outputs": ["out1", "out2", "reject"],
    },
    "tFileInputDelimited": {
        "description": "Read delimited text files (CSV, TSV, etc.)",
        "properties": {
            "FILENAME": "Input file path",
            "ROWSEPARATOR": "Row delimiter",
            "FIELDSEPARATOR": "Field delimiter",
            "HEADER": "Number of header rows to skip",
            "ENCODING": "File encoding",
        },
        "inputs": [],
        "outputs": ["FLOW", "REJECT"],
    },
    "tFileOutputDelimited": {
        "description": "Write data to delimited text files",
        "properties": {
            "FILENAME": "Output file path",
            "ROWSEPARATOR": "Row delimiter",
            "FIELDSEPARATOR": "Field delimiter",
            "INCLUDE_HEADER": "Write column headers",
            "APPEND": "Append to existing file",
        },
        "inputs": ["FLOW"],
        "outputs": [],
    },
    "tRunJob": {
        "description": "Call another Talend job as a child process",
        "properties": {
            "PROCESS": "Child job ID/name",
            "CONTEXT": "Context group to pass",
            "USE_DYNAMIC_JOB": "Load job dynamically",
            "TRANSMIT_WHOLE_CONTEXT": "Pass all context variables",
        },
        "inputs": [],
        "outputs": ["FLOW"],
    },
    "tLogRow": {
        "description": "Log/print row data for debugging",
        "properties": {
            "BASIC_MODE": "Simple log format",
            "TABLE_PRINT": "Print as formatted table",
            "VERTICAL": "Print vertically",
        },
        "inputs": ["FLOW"],
        "outputs": ["FLOW"],
    },
    "tFilterRow": {
        "description": "Filter rows based on conditions",
        "properties": {
            "CONDITIONS": "Filter conditions list",
            "LOGICAL_OP": "AND/OR between conditions",
        },
        "inputs": ["FLOW"],
        "outputs": ["FILTER", "REJECT"],
    },
    "tSortRow": {
        "description": "Sort rows by one or more columns",
        "properties": {
            "CRITERIA": "Sort criteria (columns, order)",
        },
        "inputs": ["FLOW"],
        "outputs": ["FLOW"],
    },
    "tAggregateRow": {
        "description": "Aggregate data with group by and aggregation functions",
        "properties": {
            "GROUP_BY": "Group by columns",
            "OPERATIONS": "Aggregation operations (sum, count, avg, etc.)",
        },
        "inputs": ["FLOW"],
        "outputs": ["FLOW"],
    },
    "tJava": {
        "description": "Custom Java code component (standalone)",
        "properties": {
            "CODE": "Java code to execute",
        },
        "inputs": [],
        "outputs": [],
    },
    "tJavaRow": {
        "description": "Custom Java code that processes each row",
        "properties": {
            "CODE": "Java code to execute per row",
        },
        "inputs": ["FLOW"],
        "outputs": ["FLOW"],
    },
}


def register(mcp, services):
    @mcp.tool()
    async def component_get_schema(component_name: str) -> str:
        """Get the property schema, description, and I/O connectors for a component type.

        Provides reference information about what properties a component accepts
        and what input/output connections it supports.

        Args:
            component_name: Component type name (e.g. 'tDBInput', 'tMap', 'tFileInputDelimited')
        """
        services.audit.log("component_get_schema", {"component_name": component_name})

        schema = COMPONENT_SCHEMAS.get(component_name)
        if schema:
            return json_response({
                "component": component_name,
                **schema,
                "source": "reference",
            })

        # Try partial match
        matches = [
            (name, data)
            for name, data in COMPONENT_SCHEMAS.items()
            if component_name.lower() in name.lower()
        ]
        if matches:
            return json_response({
                "component": component_name,
                "exact_match": False,
                "similar": [
                    {"name": name, "description": data["description"]}
                    for name, data in matches
                ],
            })

        return error_response(
            f"Component '{component_name}' not found in reference library. "
            "This component may be a custom or Marketplace component.",
            "NOT_FOUND",
        )
