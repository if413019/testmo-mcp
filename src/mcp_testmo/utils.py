"""
Utility functions for the MCP Testmo server.
"""

import json
from typing import Any

from mcp_testmo.client import TestmoAPIError


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
