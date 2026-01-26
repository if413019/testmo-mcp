"""
Project management tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_projects",
    description="List all accessible Testmo projects. Returns project IDs, names, and metadata.",
    input_schema={
        "type": "object",
        "properties": {},
    },
)
async def list_projects(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List all accessible projects."""
    return await client.list_projects()


@register_tool(
    name="testmo_get_project",
    description="Get details of a specific Testmo project by ID.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
        },
        "required": ["project_id"],
    },
)
async def get_project(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get details of a specific project."""
    return await client.get_project(args["project_id"])
