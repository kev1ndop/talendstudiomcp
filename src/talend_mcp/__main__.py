"""Entry point for running the Talend Studio MCP server."""

import sys

from talend_mcp.server import mcp


def main():
    """Run the MCP server with stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
