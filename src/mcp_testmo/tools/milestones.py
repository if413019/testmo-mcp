"""
Milestone management tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_milestones",
    description="List all milestones in a project (e.g., release/5.2.0).",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "is_completed": {
                "type": "boolean",
                "description": "Filter by completion status (optional)",
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
async def list_milestones(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List all milestones in a project."""
    return await client.list_milestones(
        args["project_id"],
        is_completed=args.get("is_completed"),
        page=args.get("page", 1),
        per_page=args.get("per_page", 100),
        expands=args.get("expands"),
    )


@register_tool(
    name="testmo_get_milestone",
    description="Get details of a specific milestone by ID.",
    input_schema={
        "type": "object",
        "properties": {
            "milestone_id": {
                "type": "integer",
                "description": "The milestone ID",
            },
            "expands": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Related entities to include",
            },
        },
        "required": ["milestone_id"],
    },
)
async def get_milestone(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get details of a specific milestone."""
    return await client.get_milestone(
        args["milestone_id"],
        expands=args.get("expands"),
    )
