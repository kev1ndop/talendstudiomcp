"""errors://known_patterns — Library of known error patterns and fixes."""

from __future__ import annotations

import json

# Built-in error patterns for common Talend issues
KNOWN_PATTERNS = [
    {
        "id": "conn_refused",
        "pattern": "java.net.ConnectException: Connection refused",
        "cause": "Database or service is not reachable at the configured host:port",
        "fix": "Check that the database/service is running and the connection host/port are correct",
        "category": "connectivity",
    },
    {
        "id": "auth_failed",
        "pattern": "Access denied for user",
        "cause": "Invalid database credentials",
        "fix": "Verify username and password in the connection settings or context variables",
        "category": "authentication",
    },
    {
        "id": "table_not_found",
        "pattern": "Table '.*' doesn't exist",
        "cause": "Referenced table not found in the database",
        "fix": "Check table name, schema qualifier, and database connection target",
        "category": "schema",
    },
    {
        "id": "column_not_found",
        "pattern": "Unknown column '.*' in",
        "cause": "Column referenced in SQL or schema doesn't exist in the table",
        "fix": "Re-sync the schema from the database or update the SQL query",
        "category": "schema",
    },
    {
        "id": "null_pointer",
        "pattern": "java.lang.NullPointerException",
        "cause": "A null value was encountered where non-null was expected",
        "fix": "Add null checks in tMap/tJavaRow or set columns as nullable in the schema",
        "category": "data",
    },
    {
        "id": "out_of_memory",
        "pattern": "java.lang.OutOfMemoryError",
        "cause": "Job exceeded available JVM heap memory",
        "fix": "Increase -Xmx in JVM args, use batch processing, or optimize tMap lookups",
        "category": "performance",
    },
    {
        "id": "file_not_found",
        "pattern": "java.io.FileNotFoundException",
        "cause": "Input file path doesn't exist or is not accessible",
        "fix": "Verify the file path in context variables, check file permissions",
        "category": "file",
    },
    {
        "id": "date_parse",
        "pattern": "Unparseable date",
        "cause": "Date value doesn't match the expected pattern",
        "fix": "Check the date pattern in the schema column and adjust to match input data",
        "category": "data",
    },
    {
        "id": "duplicate_key",
        "pattern": "Duplicate entry .* for key",
        "cause": "Attempting to insert a row with a duplicate primary/unique key",
        "fix": "Use INSERT_OR_UPDATE action, add tUniqRow before output, or handle rejects",
        "category": "data",
    },
    {
        "id": "class_not_found",
        "pattern": "java.lang.ClassNotFoundException",
        "cause": "Required JDBC driver or library not found",
        "fix": "Add the driver JAR to the job or project library, check module settings",
        "category": "configuration",
    },
]


def register(mcp, services):
    @mcp.resource("errors://known_patterns")
    async def error_patterns() -> str:
        """Library of known Talend error patterns with causes and fixes."""
        return json.dumps({
            "patterns": KNOWN_PATTERNS,
            "total": len(KNOWN_PATTERNS),
            "note": "Use error_pattern_learn tool (Phase 4) to add custom patterns.",
        }, indent=2)
