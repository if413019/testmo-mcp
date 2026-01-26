"""
Test run management tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_runs",
    description="List test runs in a project.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
            },
            "per_page": {
                "type": "integer",
                "description": "Results per page (default: 100)",
            },
            "is_closed": {
                "type": "boolean",
                "description": "Filter by closed status (optional)",
            },
            "milestone_id": {
                "type": "string",
                "description": "Comma-separated milestone IDs to filter by",
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
async def list_runs(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List test runs in a project."""
    return await client.list_runs(
        args["project_id"],
        args.get("page", 1),
        args.get("per_page", 100),
        is_closed=args.get("is_closed"),
        milestone_id=args.get("milestone_id"),
        expands=args.get("expands"),
    )


@register_tool(
    name="testmo_get_run",
    description="Get details of a specific test run.",
    input_schema={
        "type": "object",
        "properties": {
            "run_id": {
                "type": "integer",
                "description": "The test run ID",
            },
            "expands": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Related entities to include",
            },
        },
        "required": ["run_id"],
    },
)
async def get_run(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get details of a specific test run."""
    return await client.get_run(
        args["run_id"],
        expands=args.get("expands"),
    )
