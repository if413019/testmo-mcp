"""
Composite tools for efficient recursive operations in Testmo MCP.

These tools handle multi-step operations server-side to reduce
round-trips and token usage in agentic workflows.
"""

import asyncio
from collections import defaultdict
from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


def _collect_subtree(
    all_folders: list[dict[str, Any]], root_id: int
) -> set[int]:
    """Return set of folder IDs in the subtree rooted at root_id (inclusive)."""
    children_map: dict[int, list[int]] = defaultdict(list)
    for f in all_folders:
        pid = f.get("parent_id") or 0
        children_map[pid].append(f["id"])

    result = {root_id}
    stack = [root_id]
    while stack:
        current = stack.pop()
        for child_id in children_map.get(current, []):
            result.add(child_id)
            stack.append(child_id)
    return result


def _build_folder_map(
    all_folders: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    """Build a lookup map of folder ID to folder dict."""
    return {f["id"]: f for f in all_folders}


def _get_folder_path(
    folder_id: int, folder_map: dict[int, dict[str, Any]]
) -> str:
    """Build full path string for a folder by walking up the parent chain."""
    if folder_id not in folder_map:
        return ""
    folder = folder_map[folder_id]
    path_parts = [folder["name"]]
    parent_id = folder.get("parent_id")
    while parent_id and parent_id in folder_map:
        parent = folder_map[parent_id]
        path_parts.insert(0, parent["name"])
        parent_id = parent.get("parent_id")
    return " / ".join(path_parts)


def _build_folder_tree(
    all_folders: list[dict[str, Any]],
    subtree_ids: set[int],
    root_id: int,
    folder_map: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    """Build a nested tree structure from a flat folder list for a subtree."""
    children_map: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for f in all_folders:
        if f["id"] not in subtree_ids:
            continue
        pid = f.get("parent_id") or 0
        children_map[pid].append(f)

    def build_node(folder: dict[str, Any]) -> dict[str, Any]:
        node = {**folder}
        node["full_path"] = _get_folder_path(folder["id"], folder_map)
        node["children"] = [
            build_node(child) for child in children_map.get(folder["id"], [])
        ]
        return node

    if root_id not in folder_map:
        return None
    return build_node(folder_map[root_id])


@register_tool(
    name="testmo_get_folders_recursive",
    description=(
        "Get a folder and all its descendant subfolders as a nested tree. "
        "Returns the complete folder hierarchy under the given folder ID in a "
        "single call, avoiding multiple round-trips."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "folder_id": {
                "type": "integer",
                "description": "The root folder ID to start recursion from",
            },
        },
        "required": ["project_id", "folder_id"],
    },
)
async def get_folders_recursive(
    client: TestmoClient, args: dict[str, Any]
) -> Any:
    """Get a folder and all descendants as a nested tree."""
    project_id = args["project_id"]
    folder_id = args["folder_id"]

    all_folders = await client.get_all_folders(project_id)
    folder_map = _build_folder_map(all_folders)

    if folder_id not in folder_map:
        return {"error": f"Folder {folder_id} not found in project {project_id}"}

    subtree_ids = _collect_subtree(all_folders, folder_id)
    tree = _build_folder_tree(all_folders, subtree_ids, folder_id, folder_map)

    return {
        "total_folders": len(subtree_ids),
        "tree": tree,
    }


@register_tool(
    name="testmo_get_cases_recursive",
    description=(
        "Get all test cases from a folder and all its subfolders in a single call. "
        "Returns a flat list of cases annotated with folder name and path. "
        "Includes per-folder case counts in the summary."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "folder_id": {
                "type": "integer",
                "description": "The root folder ID to collect cases from recursively",
            },
            "include_folder_path": {
                "type": "boolean",
                "description": "Include folder path on each case (default: true)",
                "default": True,
            },
        },
        "required": ["project_id", "folder_id"],
    },
)
async def get_cases_recursive(
    client: TestmoClient, args: dict[str, Any]
) -> Any:
    """Get all test cases from a folder tree."""
    project_id = args["project_id"]
    folder_id = args["folder_id"]
    include_path = args.get("include_folder_path", True)

    all_folders = await client.get_all_folders(project_id)
    folder_map = _build_folder_map(all_folders)

    if folder_id not in folder_map:
        return {"error": f"Folder {folder_id} not found in project {project_id}"}

    subtree_ids = _collect_subtree(all_folders, folder_id)

    all_cases: list[dict[str, Any]] = []
    folder_summary: list[dict[str, Any]] = []

    for fid in sorted(subtree_ids):
        cases = await client.get_all_cases(project_id, folder_id=fid)
        folder_name = folder_map[fid]["name"] if fid in folder_map else str(fid)
        folder_path = _get_folder_path(fid, folder_map) if include_path else None

        if cases:
            folder_summary.append({
                "folder_id": fid,
                "folder_name": folder_name,
                "folder_path": folder_path,
                "case_count": len(cases),
            })

        for case in cases:
            case["_folder_name"] = folder_name
            if include_path:
                case["_folder_path"] = folder_path
            all_cases.append(case)

        if len(subtree_ids) > 1:
            await asyncio.sleep(client.RATE_LIMIT_DELAY)

    return {
        "total_cases": len(all_cases),
        "total_folders_searched": len(subtree_ids),
        "folder_summary": folder_summary,
        "cases": all_cases,
    }


@register_tool(
    name="testmo_search_cases_recursive",
    description=(
        "Search for test cases recursively within a folder and all its subfolders. "
        "Supports API-level filters (query, tags, state_id) plus client-side "
        "custom_filters for matching on any case property (e.g., custom_priority, "
        "custom_type, configurations). Returns matching cases with folder context."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "The project ID",
            },
            "folder_id": {
                "type": "integer",
                "description": "The root folder ID to search recursively within",
            },
            "query": {
                "type": "string",
                "description": "Search query (searches name and description)",
            },
            "tags": {
                "type": "array",
                "description": "Filter by tags",
                "items": {"type": "string"},
            },
            "state_id": {
                "type": "integer",
                "description": (
                    "Filter by state "
                    "(1=Draft, 2=Review, 3=Approved, 4=Active, 5=Deprecated)"
                ),
            },
            "custom_filters": {
                "type": "object",
                "description": (
                    "Key-value pairs to match on case properties. "
                    "Example: {\"custom_priority\": 1, \"custom_type\": 59}"
                ),
            },
        },
        "required": ["project_id", "folder_id"],
    },
)
async def search_cases_recursive(
    client: TestmoClient, args: dict[str, Any]
) -> Any:
    """Search test cases recursively within a folder subtree."""
    project_id = args["project_id"]
    folder_id = args["folder_id"]
    query = args.get("query")
    tags = args.get("tags")
    state_id = args.get("state_id")
    custom_filters: dict[str, Any] | None = args.get("custom_filters")

    all_folders = await client.get_all_folders(project_id)
    folder_map = _build_folder_map(all_folders)

    if folder_id not in folder_map:
        return {"error": f"Folder {folder_id} not found in project {project_id}"}

    subtree_ids = _collect_subtree(all_folders, folder_id)

    all_matches: list[dict[str, Any]] = []
    folder_summary: list[dict[str, Any]] = []

    for fid in sorted(subtree_ids):
        # Auto-paginate search results per folder
        folder_cases: list[dict[str, Any]] = []
        page = 1
        while True:
            result = await client.search_cases(
                project_id,
                query=query,
                folder_id=fid,
                tags=tags,
                state_id=state_id,
                page=page,
                per_page=100,
            )
            cases = result.get("result", [])
            folder_cases.extend(cases)

            if result.get("next_page") is None:
                break
            page += 1
            await asyncio.sleep(client.RATE_LIMIT_DELAY)

        # Apply custom property filters client-side
        if custom_filters:
            folder_cases = [
                c for c in folder_cases
                if all(c.get(k) == v for k, v in custom_filters.items())
            ]

        folder_name = folder_map[fid]["name"] if fid in folder_map else str(fid)
        folder_path = _get_folder_path(fid, folder_map)

        if folder_cases:
            folder_summary.append({
                "folder_id": fid,
                "folder_name": folder_name,
                "folder_path": folder_path,
                "match_count": len(folder_cases),
            })

        for case in folder_cases:
            case["_folder_name"] = folder_name
            case["_folder_path"] = folder_path
            all_matches.append(case)

        if len(subtree_ids) > 1:
            await asyncio.sleep(client.RATE_LIMIT_DELAY)

    return {
        "total_matches": len(all_matches),
        "total_folders_searched": len(subtree_ids),
        "folder_summary": folder_summary,
        "cases": all_matches,
    }
