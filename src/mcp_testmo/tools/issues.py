"""
Issue connection tools for Testmo MCP.

Provides tools for discovering and managing issue integrations (GitHub, Jira, etc.)
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_issue_connections",
    description="""List available issue integrations (GitHub, Jira, etc.).

Discover configured issue tracker integrations before linking external issues to test cases.
Returns integration IDs, names, types, and connection details.

Use this to find the integration_id and connection_project_id needed for linking issues.""",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "Filter by project ID (optional)",
            },
            "integration_type": {
                "type": "string",
                "description": "Filter by integration type (e.g., 'github', 'jira', 'azure_devops')",
            },
            "is_active": {
                "type": "boolean",
                "description": "Filter by active status (optional)",
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
                "description": "Related entities to include",
                "items": {"type": "string"},
            },
        },
        "required": [],
    },
)
async def list_issue_connections(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List available issue integrations."""
    return await client.list_issue_connections(
        args.get("project_id"),
        args.get("integration_type"),
        args.get("is_active"),
        args.get("page", 1),
        args.get("per_page", 100),
        args.get("expands"),
    )


@register_tool(
    name="testmo_get_issue_connection",
    description="""Get details of a specific issue connection.

Returns full configuration details for an issue integration including:
- Integration type (github, jira, azure_devops, etc.)
- Connection settings and credentials status
- Linked projects and repositories""",
    input_schema={
        "type": "object",
        "properties": {
            "connection_id": {
                "type": "integer",
                "description": "The issue connection ID",
            },
            "expands": {
                "type": "array",
                "description": "Related entities to include",
                "items": {"type": "string"},
            },
        },
        "required": ["connection_id"],
    },
)
async def get_issue_connection(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get details of a specific issue connection."""
    return await client.get_issue_connection(
        args["connection_id"],
        args.get("expands"),
    )
