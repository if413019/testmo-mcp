"""
Automation source tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_automation_sources",
    description="List automation sources in a project (CI/CD integrations).",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "is_retired": {
                "type": "boolean",
                "description": "Filter by retired status (optional)",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "per_page": {
                "type": "integer",
                "description": "Results per page (default: 100, max: 100). Valid values: 25, 50, 100",
                "default": 100,
                "enum": [25, 50, 100],
            },
            "expands": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Related entities to include",
            },
        },
        "required": ["project_id"],
    },
)
async def list_automation_sources(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List automation sources in a project."""
    return await client.list_automation_sources(
        args["project_id"],
        is_retired=args.get("is_retired"),
        page=args.get("page", 1),
        per_page=args.get("per_page", 100),
        expands=args.get("expands"),
    )


@register_tool(
    name="testmo_get_automation_source",
    description="Get details of a specific automation source.",
    input_schema={
        "type": "object",
        "properties": {
            "automation_source_id": {
                "type": "integer",
                "description": "The automation source ID",
            },
            "expands": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Related entities to include",
            },
        },
        "required": ["automation_source_id"],
    },
)
async def get_automation_source(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get details of a specific automation source."""
    return await client.get_automation_source(
        args["automation_source_id"],
        expands=args.get("expands"),
    )
