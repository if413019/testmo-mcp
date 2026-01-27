"""
Utility tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.config import FIELD_MAPPINGS
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_get_field_mappings",
    description="""Get the field value mappings for Testmo API. Returns mappings for:
- project_id: Project name to ID mapping
- custom_priority: Priority levels (Critical, High, Medium, Low)
- custom_type: Test types (Functional, Acceptance, Security, etc.)
- configurations: Platform IDs (Admin Portal, iOS & Android, Insti Web)
- state_id: Test case states (Draft, Review, Approved, Active, Deprecated)
- result_status_id: Test result statuses (Untested, Passed, Failed, Retest, Blocked, Skipped)
- automation_run_status: Automation run statuses (Success, Failure, Running)
- tags: Tag categories (domain, tier-type, scope, risk)

Use this to understand correct field values before creating/updating test cases.""",
    input_schema={
        "type": "object",
        "properties": {},
    },
    requires_client=False,
)
async def get_field_mappings(args: dict[str, Any]) -> Any:
    """Get field value mappings."""
    return FIELD_MAPPINGS


@register_tool(
    name="testmo_get_web_url",
    description="Generate a web URL for viewing a resource in Testmo.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "resource_type": {
                "type": "string",
                "description": "Type of resource (repositories, runs)",
                "default": "repositories",
            },
            "resource_id": {
                "type": "integer",
                "description": "Resource ID (e.g., folder ID)",
            },
        },
        "required": ["project_id"],
    },
)
async def get_web_url(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Generate a web URL for a Testmo resource."""
    return {
        "url": client.get_web_url(
            args["project_id"],
            args.get("resource_type", "repositories"),
            args.get("resource_id"),
        )
    }
