"""
Automation run tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_automation_runs",
    description="""List automation runs in a project with optional filters.

Automation runs represent CI/CD test execution results. Filter by:
- source_id: Automation source IDs (comma-separated)
- milestone_id: Milestone IDs (comma-separated)
- status: Run status (2=Success, 3=Failure, 4=Running)
- created_after/before: Date range (ISO8601 format)""",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "source_id": {
                "type": "string",
                "description": "Comma-separated automation source IDs to filter by",
            },
            "milestone_id": {
                "type": "string",
                "description": "Comma-separated milestone IDs to filter by",
            },
            "status": {
                "type": "string",
                "description": "Comma-separated status values (2=Success, 3=Failure, 4=Running)",
            },
            "created_after": {
                "type": "string",
                "description": "Filter runs created after (ISO8601 format)",
            },
            "created_before": {
                "type": "string",
                "description": "Filter runs created before (ISO8601 format)",
            },
            "tags": {
                "type": "string",
                "description": "Comma-separated tags to filter by",
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
async def list_automation_runs(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List automation runs in a project."""
    return await client.list_automation_runs(
        args["project_id"],
        source_id=args.get("source_id"),
        milestone_id=args.get("milestone_id"),
        status=args.get("status"),
        created_after=args.get("created_after"),
        created_before=args.get("created_before"),
        tags=args.get("tags"),
        page=args.get("page", 1),
        per_page=args.get("per_page", 100),
        expands=args.get("expands"),
    )


@register_tool(
    name="testmo_get_automation_run",
    description="Get details of a specific automation run.",
    input_schema={
        "type": "object",
        "properties": {
            "automation_run_id": {
                "type": "integer",
                "description": "The automation run ID",
            },
            "expands": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Related entities to include",
            },
        },
        "required": ["automation_run_id"],
    },
)
async def get_automation_run(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get details of a specific automation run."""
    return await client.get_automation_run(
        args["automation_run_id"],
        expands=args.get("expands"),
    )
