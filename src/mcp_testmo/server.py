"""
MCP Testmo Server

Model Context Protocol server for Testmo test case management.
Provides tools for AI assistants to manage test cases, folders, and projects.
"""

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_testmo.client import TestmoAPIError, TestmoClient

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


def format_error(e: Exception) -> str:
    """Format an exception as a JSON error response."""
    if isinstance(e, TestmoAPIError):
        return json.dumps(
            {
                "error": True,
                "status_code": e.status_code,
                "message": e.message,
                "details": e.details,
            },
            indent=2,
        )
    return json.dumps({"error": True, "message": str(e)}, indent=2)


def format_result(data: Any) -> str:
    """Format a result as JSON."""
    return json.dumps(data, indent=2, default=str)


# =============================================================================
# Tool Definitions
# =============================================================================

TOOLS = [
    # Projects
    Tool(
        name="testmo_list_projects",
        description="List all accessible Testmo projects. Returns project IDs, names, and metadata.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="testmo_get_project",
        description="Get details of a specific Testmo project by ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
            },
            "required": ["project_id"],
        },
    ),
    # Folders
    Tool(
        name="testmo_list_folders",
        description="List all folders in a Testmo project. Returns folder hierarchy with IDs, names, and parent relationships.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
            },
            "required": ["project_id"],
        },
    ),
    Tool(
        name="testmo_get_folder",
        description="Get details of a specific folder.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
                "folder_id": {
                    "type": "integer",
                    "description": "The folder ID",
                },
            },
            "required": ["project_id", "folder_id"],
        },
    ),
    Tool(
        name="testmo_create_folder",
        description="Create a new folder in a Testmo project.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
                "name": {
                    "type": "string",
                    "description": "Folder name",
                },
                "parent_id": {
                    "type": "integer",
                    "description": "Parent folder ID (optional, omit for root level)",
                },
            },
            "required": ["project_id", "name"],
        },
    ),
    Tool(
        name="testmo_update_folder",
        description="Update a folder's name or parent.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
                "folder_id": {
                    "type": "integer",
                    "description": "The folder ID to update",
                },
                "name": {
                    "type": "string",
                    "description": "New folder name (optional)",
                },
                "parent_id": {
                    "type": "integer",
                    "description": "New parent folder ID (optional)",
                },
            },
            "required": ["project_id", "folder_id"],
        },
    ),
    Tool(
        name="testmo_delete_folder",
        description="Delete a folder from a project. WARNING: This will also delete all test cases in the folder.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
                "folder_id": {
                    "type": "integer",
                    "description": "The folder ID to delete",
                },
            },
            "required": ["project_id", "folder_id"],
        },
    ),
    Tool(
        name="testmo_find_folder_by_name",
        description="Find a folder by its name within a project.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
                "name": {
                    "type": "string",
                    "description": "Folder name to search for",
                },
                "parent_id": {
                    "type": "integer",
                    "description": "Parent folder ID to search within (optional, omit for root level)",
                },
            },
            "required": ["project_id", "name"],
        },
    ),
    # Milestones
    Tool(
        name="testmo_list_milestones",
        description="List all milestones in a project (e.g., release/5.2.0).",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
            },
            "required": ["project_id"],
        },
    ),
    # Test Cases
    Tool(
        name="testmo_list_cases",
        description="List test cases in a project or folder. Supports pagination.",
        inputSchema={
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
    ),
    Tool(
        name="testmo_get_all_cases",
        description="Get all test cases in a folder (handles pagination automatically). Use for discovering existing test cases.",
        inputSchema={
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
    ),
    Tool(
        name="testmo_get_case",
        description="Get full details of a specific test case, including custom fields and Gherkin scenarios.",
        inputSchema={
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
    ),
    Tool(
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
        inputSchema={
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
    ),
    Tool(
        name="testmo_create_cases",
        description="Create multiple test cases in a batch (max 100 per call).",
        inputSchema={
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
    ),
    Tool(
        name="testmo_batch_create_cases",
        description="Create any number of test cases, automatically handling batching (100 per request).",
        inputSchema={
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
    ),
    Tool(
        name="testmo_update_case",
        description="Update an existing test case. Only include fields you want to change.",
        inputSchema={
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
    ),
    Tool(
        name="testmo_delete_case",
        description="Delete a test case.",
        inputSchema={
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
    ),
    Tool(
        name="testmo_batch_delete_cases",
        description="Delete multiple test cases.",
        inputSchema={
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
    ),
    Tool(
        name="testmo_search_cases",
        description="Search for test cases with filters (query, folder, tags, state).",
        inputSchema={
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
    ),
    # Test Runs
    Tool(
        name="testmo_list_runs",
        description="List test runs in a project.",
        inputSchema={
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
            },
            "required": ["project_id"],
        },
    ),
    Tool(
        name="testmo_get_run",
        description="Get details of a specific test run.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
                "run_id": {
                    "type": "integer",
                    "description": "The test run ID",
                },
            },
            "required": ["project_id", "run_id"],
        },
    ),
    # Utility
    Tool(
        name="testmo_get_field_mappings",
        description="""Get the field value mappings for Testmo API. Returns mappings for:
- project_id: Project name to ID mapping
- custom_priority: Priority levels (Critical, High, Medium, Low)
- custom_type: Test types (Functional, Acceptance, Security, etc.)
- configurations: Platform IDs (Admin Portal, iOS & Android, Insti Web)
- state_id: Test case states (Draft, Review, Approved, Active, Deprecated)
- tags: Tag categories (domain, tier-type, scope, risk)

Use this to understand correct field values before creating/updating test cases.""",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="testmo_get_web_url",
        description="Generate a web URL for viewing a resource in Testmo.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "The project ID",
                },
                "resource_type": {
                    "type": "string",
                    "description": "Type of resource (repository, runs)",
                    "default": "repository",
                },
                "resource_id": {
                    "type": "integer",
                    "description": "Resource ID (e.g., folder ID)",
                },
            },
            "required": ["project_id"],
        },
    ),
]


# =============================================================================
# Field Mappings (embedded for quick access)
# =============================================================================

FIELD_MAPPINGS = {
    "project_id": {
        "example-project": 2,
        "playground": 6,
    },
    "custom_priority": {
        "Critical": 52,
        "High": 1,
        "Medium": 2,
        "Low": 3,
    },
    "custom_type": {
        "Performance": 57,
        "Functional": 59,
        "Usability": 53,
        "Acceptance": 64,
        "Compatibility": 61,
        "Security": 55,
        "Other": 58,
    },
    "custom_creator": {
        "AI Generated": 51,
    },
    "configurations": {
        "Admin Portal": 4,
        "IOS & Android": 5,
        "Insti Web": 10,
    },
    "template_id": {
        "BDD/Gherkin": 4,
        "Steps Table": 1,
    },
    "state_id": {
        "Draft": 1,
        "Review": 2,
        "Approved": 3,
        "Active": 4,
        "Deprecated": 5,
    },
    "status_id": {
        "Incomplete": 1,
        "Complete": 2,
    },
    "custom_issues_tags_and_configurations_added": {
        "Yes": 66,
        "No": 67,
    },
    "tags": {
        "domain": ["assets-crypto", "assets-noncrypto", "services-usergrowth", "services-platform", "wealth-hnwi"],
        "tier-type": ["ui-verification", "e2e", "negative"],
        "scope": ["regression", "smoke", "sanity"],
        "risk": ["risk-financial", "risk-security", "risk-compliance"],
    },
    "defaults": {
        "template_id": 4,
        "state_id": 1,
        "status_id": 2,
        "custom_priority": 2,
        "custom_type": 59,
        "custom_creator": 51,
        "custom_issues_tags_and_configurations_added": 66,
    },
}


# =============================================================================
# Tool Handlers
# =============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        result = await _execute_tool(name, arguments)
        return [TextContent(type="text", text=format_result(result))]
    except Exception as e:
        return [TextContent(type="text", text=format_error(e))]


async def _execute_tool(name: str, args: dict[str, Any]) -> Any:
    """Execute a tool and return the result."""

    # Utility tools (no API call needed)
    if name == "testmo_get_field_mappings":
        return FIELD_MAPPINGS

    if name == "testmo_get_web_url":
        async with get_client() as client:
            return {
                "url": client.get_web_url(
                    args["project_id"],
                    args.get("resource_type", "repository"),
                    args.get("resource_id"),
                )
            }

    # API-based tools
    async with get_client() as client:
        # Projects
        if name == "testmo_list_projects":
            return await client.list_projects()

        if name == "testmo_get_project":
            return await client.get_project(args["project_id"])

        # Folders
        if name == "testmo_list_folders":
            folders = await client.get_all_folders(args["project_id"])
            # Build folder paths for easier reading
            folder_map = {f["id"]: f for f in folders}
            for folder in folders:
                path_parts = [folder["name"]]
                parent_id = folder.get("parent_id")
                while parent_id and parent_id in folder_map:
                    parent = folder_map[parent_id]
                    path_parts.insert(0, parent["name"])
                    parent_id = parent.get("parent_id")
                folder["full_path"] = " / ".join(path_parts)
            return folders

        if name == "testmo_get_folder":
            return await client.get_folder(args["project_id"], args["folder_id"])

        if name == "testmo_create_folder":
            return await client.create_folder(
                args["project_id"],
                args["name"],
                args.get("parent_id"),
            )

        if name == "testmo_update_folder":
            return await client.update_folder(
                args["project_id"],
                args["folder_id"],
                args.get("name"),
                args.get("parent_id"),
            )

        if name == "testmo_delete_folder":
            return await client.delete_folder(args["project_id"], args["folder_id"])

        if name == "testmo_find_folder_by_name":
            result = await client.find_folder_by_name(
                args["project_id"],
                args["name"],
                args.get("parent_id"),
            )
            if result:
                return result
            return {"found": False, "message": f"Folder '{args['name']}' not found"}

        # Milestones
        if name == "testmo_list_milestones":
            return await client.list_milestones(args["project_id"])

        # Test Cases
        if name == "testmo_list_cases":
            return await client.list_cases(
                args["project_id"],
                args.get("folder_id"),
                args.get("page", 1),
                args.get("per_page", 100),
            )

        if name == "testmo_get_all_cases":
            cases = await client.get_all_cases(
                args["project_id"],
                args.get("folder_id"),
            )
            return {
                "total": len(cases),
                "cases": cases,
            }

        if name == "testmo_get_case":
            return await client.get_case(args["project_id"], args["case_id"])

        if name == "testmo_create_case":
            return await client.create_case(args["project_id"], args["case_data"])

        if name == "testmo_create_cases":
            return await client.create_cases(args["project_id"], args["cases"])

        if name == "testmo_batch_create_cases":
            return await client.batch_create_cases(args["project_id"], args["cases"])

        if name == "testmo_update_case":
            return await client.update_case(
                args["project_id"],
                args["case_id"],
                args["data"],
            )

        if name == "testmo_delete_case":
            return await client.delete_case(args["project_id"], args["case_id"])

        if name == "testmo_batch_delete_cases":
            return await client.batch_delete_cases(
                args["project_id"],
                args["case_ids"],
            )

        if name == "testmo_search_cases":
            return await client.search_cases(
                args["project_id"],
                args.get("query"),
                args.get("folder_id"),
                args.get("tags"),
                args.get("state_id"),
                args.get("page", 1),
                args.get("per_page", 100),
            )

        # Test Runs
        if name == "testmo_list_runs":
            return await client.list_runs(
                args["project_id"],
                args.get("page", 1),
                args.get("per_page", 100),
            )

        if name == "testmo_get_run":
            return await client.get_run(args["project_id"], args["run_id"])

    raise ValueError(f"Unknown tool: {name}")


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
