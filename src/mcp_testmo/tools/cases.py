"""
Test case management tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_cases",
    description="List test cases in a project or folder. Supports pagination.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "folder_id": {
                "type": "integer",
                "description": "Filter by folder ID (optional)",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1,
            },
            "per_page": {
                "type": "integer",
                "description": "Results per page (default: 100, max: 100)",
                "default": 100,
            },
        },
        "required": ["project_id"],
    },
)
async def list_cases(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List test cases in a project or folder."""
    return await client.list_cases(
        args["project_id"],
        args.get("folder_id"),
        args.get("page", 1),
        args.get("per_page", 100),
    )


@register_tool(
    name="testmo_get_all_cases",
    description="Get all test cases in a folder (handles pagination automatically). Use for discovering existing test cases.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "folder_id": {
                "type": "integer",
                "description": "Folder ID to get cases from (optional)",
            },
        },
        "required": ["project_id"],
    },
)
async def get_all_cases(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get all test cases with auto-pagination."""
    cases = await client.get_all_cases(
        args["project_id"],
        args.get("folder_id"),
    )
    return {
        "total": len(cases),
        "cases": cases,
    }


@register_tool(
    name="testmo_get_case",
    description="Get full details of a specific test case, including custom fields and Gherkin scenarios.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "case_id": {
                "type": "integer",
                "description": "The test case ID",
            },
        },
        "required": ["project_id", "case_id"],
    },
)
async def get_case(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Get full details of a specific test case."""
    return await client.get_case(args["project_id"], args["case_id"])


@register_tool(
    name="testmo_create_case",
    description="""Create a single test case in Testmo.

Required fields:
- name: Test case title
- folder_id: Target folder ID (0 for root)
- custom_priority: Priority ID (52=Critical, 1=High, 2=Medium, 3=Low)
- custom_type: Type ID (59=Functional, 64=Acceptance, 55=Security)
- custom_creator: Creator ID (51=AI Generated)
- custom_milestone_id: Milestone string (e.g., "release/5.2.0")
- custom_references: Jira key (e.g., "IUG-1169")
- custom_issues_tags_and_configurations_added: 66=Yes, 67=No
- custom_confluence_url: Confluence URL
- custom_feature: Rich HTML with Gherkin scenario
- configurations: Platform IDs array (4=Admin Portal, 5=iOS & Android, 10=Insti Web)

Optional fields:
- template_id: 4=BDD/Gherkin (default), 1=Steps Table
- state_id: 1=Draft (default), 2=Review, 3=Approved, 4=Active, 5=Deprecated
- tags: Array of strings (domain, tier-type, scope tags)""",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "case_data": {
                "type": "object",
                "description": "Test case data object with all required fields",
            },
        },
        "required": ["project_id", "case_data"],
    },
)
async def create_case(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Create a single test case."""
    return await client.create_case(args["project_id"], args["case_data"])


@register_tool(
    name="testmo_create_cases",
    description="Create multiple test cases in a batch (max 100 per call).",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "cases": {
                "type": "array",
                "description": "Array of test case objects (max 100)",
                "items": {"type": "object"},
            },
        },
        "required": ["project_id", "cases"],
    },
)
async def create_cases(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Create multiple test cases in a batch."""
    return await client.create_cases(args["project_id"], args["cases"])


@register_tool(
    name="testmo_batch_create_cases",
    description="Create any number of test cases, automatically handling batching (100 per request).",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "cases": {
                "type": "array",
                "description": "Array of test case objects",
                "items": {"type": "object"},
            },
        },
        "required": ["project_id", "cases"],
    },
)
async def batch_create_cases(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Create test cases with auto-batching."""
    return await client.batch_create_cases(args["project_id"], args["cases"])


@register_tool(
    name="testmo_update_case",
    description="Update an existing test case. Only include fields you want to change.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "case_id": {
                "type": "integer",
                "description": "The test case ID to update",
            },
            "data": {
                "type": "object",
                "description": "Fields to update",
            },
        },
        "required": ["project_id", "case_id", "data"],
    },
)
async def update_case(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Update an existing test case."""
    return await client.update_case(
        args["project_id"],
        args["case_id"],
        args["data"],
    )


@register_tool(
    name="testmo_delete_case",
    description="Delete a test case.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "case_id": {
                "type": "integer",
                "description": "The test case ID to delete",
            },
        },
        "required": ["project_id", "case_id"],
    },
)
async def delete_case(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Delete a test case."""
    return await client.delete_case(args["project_id"], args["case_id"])


@register_tool(
    name="testmo_batch_delete_cases",
    description="Delete multiple test cases.",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "case_ids": {
                "type": "array",
                "description": "Array of test case IDs to delete",
                "items": {"type": "integer"},
            },
        },
        "required": ["project_id", "case_ids"],
    },
)
async def batch_delete_cases(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Delete multiple test cases."""
    return await client.batch_delete_cases(
        args["project_id"],
        args["case_ids"],
    )


@register_tool(
    name="testmo_search_cases",
    description="Search for test cases with filters (query, folder, tags, state).",
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "query": {
                "type": "string",
                "description": "Search query (searches name and description)",
            },
            "folder_id": {
                "type": "integer",
                "description": "Filter by folder ID",
            },
            "tags": {
                "type": "array",
                "description": "Filter by tags",
                "items": {"type": "string"},
            },
            "state_id": {
                "type": "integer",
                "description": "Filter by state (1=Draft, 2=Review, 3=Approved, 4=Active, 5=Deprecated)",
            },
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
            },
            "per_page": {
                "type": "integer",
                "description": "Results per page (default: 100)",
            },
        },
        "required": ["project_id"],
    },
)
async def search_cases(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Search for test cases with filters."""
    return await client.search_cases(
        args["project_id"],
        args.get("query"),
        args.get("folder_id"),
        args.get("tags"),
        args.get("state_id"),
        args.get("page", 1),
        args.get("per_page", 100),
    )
