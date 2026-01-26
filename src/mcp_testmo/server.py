"""
MCP Testmo Server

Model Context Protocol server for Testmo test case management.
Provides tools for AI assistants to manage test cases, folders, and projects.
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_testmo.client import TestmoClient
from mcp_testmo.config import FIELD_MAPPINGS
from mcp_testmo.tools import get_all_tools, get_handler
from mcp_testmo.utils import format_error, format_result

# Load environment variables
load_dotenv()

# Initialize MCP server
server = Server("mcp-testmo")

# Global client instance (lazy initialized)
_client: TestmoClient | None = None


@asynccontextmanager
async def get_client():
    """Get or create a Testmo client."""
    global _client
    if _client is None:
        _client = TestmoClient()
    async with _client as client:
        yield client


# =============================================================================
# Tool Handlers
# =============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return get_all_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls by dispatching to registered handlers."""
    try:
        tool_def = get_handler(name)
        if tool_def is None:
            raise ValueError(f"Unknown tool: {name}")

        if tool_def.requires_client:
            async with get_client() as client:
                result = await tool_def.handler(client, arguments)
        else:
            result = await tool_def.handler(arguments)

        return [TextContent(type="text", text=format_result(result))]
    except Exception as e:
        return [TextContent(type="text", text=format_error(e))]


# =============================================================================
# Legacy exports for backward compatibility
# =============================================================================

# Re-export FIELD_MAPPINGS and formatters for tests and other modules
__all__ = ["FIELD_MAPPINGS", "format_error", "format_result", "server", "main"]

# Build TOOLS list from registry for backward compatibility with tests
TOOLS = get_all_tools()


# =============================================================================
# Server Entry Point
# =============================================================================


def main() -> None:
    """Main entry point for the MCP server."""
    # Check for required environment variables
    if not os.environ.get("TESTMO_URL"):
        print(
            "Error: TESTMO_URL environment variable not set",
            file=sys.stderr,
        )
        print(
            "Set it to your Testmo instance URL (e.g., https://your-instance.testmo.net)",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.environ.get("TESTMO_API_KEY"):
        print(
            "Error: TESTMO_API_KEY environment variable not set",
            file=sys.stderr,
        )
        print(
            "Get your API key from Testmo: Settings > API Keys",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run the server
    asyncio.run(_run_server())


async def _run_server() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    main()
