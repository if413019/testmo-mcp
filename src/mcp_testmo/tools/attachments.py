"""
Test case attachment tools for Testmo MCP.
"""

from typing import Any

from mcp_testmo.client import TestmoClient
from mcp_testmo.tools.base import register_tool


@register_tool(
    name="testmo_list_case_attachments",
    description="List all attachments for a test case.",
    input_schema={
        "type": "object",
        "properties": {
            "case_id": {
                "type": "integer",
                "description": "The test case ID",
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
        "required": ["case_id"],
    },
)
async def list_case_attachments(client: TestmoClient, args: dict[str, Any]) -> Any:
    """List all attachments for a test case."""
    return await client.list_case_attachments(
        args["case_id"],
        page=args.get("page", 1),
        per_page=args.get("per_page", 100),
        expands=args.get("expands"),
    )


@register_tool(
    name="testmo_upload_case_attachment",
    description="""Upload a single file attachment to a test case.

Provide the file content as base64-encoded string. Common content types:
- image/png, image/jpeg - Screenshots
- application/pdf - Documents
- text/plain - Log files
- application/json - JSON data

Maximum file size depends on your Testmo instance configuration.""",
    input_schema={
        "type": "object",
        "properties": {
            "case_id": {
                "type": "integer",
                "description": "The test case ID",
            },
            "filename": {
                "type": "string",
                "description": "Name of the file (e.g., 'screenshot.png')",
            },
            "content_base64": {
                "type": "string",
                "description": "Base64-encoded file content",
            },
            "content_type": {
                "type": "string",
                "description": "MIME type (default: 'application/octet-stream')",
                "default": "application/octet-stream",
            },
        },
        "required": ["case_id", "filename", "content_base64"],
    },
)
async def upload_case_attachment(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Upload a single file attachment to a test case."""
    return await client.upload_case_attachment(
        args["case_id"],
        args["filename"],
        args["content_base64"],
        args.get("content_type", "application/octet-stream"),
    )


@register_tool(
    name="testmo_delete_case_attachments",
    description="Delete one or more attachments from a test case.",
    input_schema={
        "type": "object",
        "properties": {
            "case_id": {
                "type": "integer",
                "description": "The test case ID",
            },
            "attachment_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Array of attachment IDs to delete",
            },
        },
        "required": ["case_id", "attachment_ids"],
    },
)
async def delete_case_attachments(client: TestmoClient, args: dict[str, Any]) -> Any:
    """Delete one or more attachments from a test case."""
    return await client.delete_case_attachments(
        args["case_id"],
        args["attachment_ids"],
    )
