"""
Test run results tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_run_results",
    description="""List test results for a run with optional filters.

Supports filtering by status, assignee, and date range:
- status_id: Filter by result status (1=Untested, 2=Passed, 3=Failed, 4=Retest, 5=Blocked, 6=Skipped)
- assignee_id: Filter by assigned user IDs (comma-separated)
- get_latest_result: If true, return only the latest result per test

Use expands parameter to include related entities like test case details.""",
    input_schema={
        "type": "object",
        "properties": {
            "run_id": {
                "type": "integer",
                "description": "The test run ID",
            },
            "status_id": {
                "type": "string",
                "description": "Comma-separated status IDs (1=Untested, 2=Passed, 3=Failed, 4=Retest, 5=Blocked, 6=Skipped)",
            },
            "assignee_id": {
                "type": "string",
                "description": "Comma-separated assignee IDs to filter by",
            },
            "created_by": {
                "type": "string",
                "description": "Comma-separated user IDs who created results",
            },
            "created_after": {
                "type": "string",
                "description": "Filter results created after (ISO8601 format)",
            },
            "created_before": {
                "type": "string",
                "description": "Filter results created before (ISO8601 format)",
            },
            "get_latest_result": {
                "type": "boolean",
                "description": "If true, return only the latest result per test",
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
        "required": ["run_id"],
    },
)
async def list_run_results(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List test results for a run with filters."""
    return await client.list_run_results(
        args["run_id"],
        status_id=args.get("status_id"),
        assignee_id=args.get("assignee_id"),
        created_by=args.get("created_by"),
        created_after=args.get("created_after"),
        created_before=args.get("created_before"),
        get_latest_result=args.get("get_latest_result"),
        page=args.get("page", 1),
        per_page=args.get("per_page", 100),
        expands=args.get("expands"),
    )
