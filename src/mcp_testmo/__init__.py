"""
MCP Testmo - Model Context Protocol Server for Testmo Test Management

This package provides an MCP server that enables AI assistants to interact
with Testmo for test case management, including creating, updating, and
organizing test cases.
"""

__version__ = "1.0.0"
__author__ = "mcp-testmo contributors"

from mcp_testmo.client import TestmoClient, TestmoAPIError

__all__ = ["TestmoClient", "TestmoAPIError", "__version__"]
