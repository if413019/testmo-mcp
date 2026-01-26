"""
Base classes and utilities for tool registration.

This module provides a decorator-based registry pattern for defining MCP tools.
Tools are automatically registered when their module is imported.
"""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from mcp.types import Tool

# Type alias for async tool handlers
ToolHandler = Callable[..., Coroutine[Any, Any, Any]]


@dataclass
class ToolDefinition:
    """Container for a tool's definition and handler."""

    tool: Tool
    handler: ToolHandler
    requires_client: bool = True


# Global registry of all tools
_tool_registry: dict[str, ToolDefinition] = {}


def register_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    requires_client: bool = True,
) -> Callable[[ToolHandler], ToolHandler]:
    """
    Decorator to register a tool handler with its definition.

    Usage:
        @register_tool(
            name="testmo_list_projects",
            description="List all accessible projects.",
            input_schema={"type": "object", "properties": {}},
        )
        async def list_projects(client: TestmoClient, args: dict[str, Any]) -> Any:
            return await client.list_projects()

    Args:
        name: Unique tool name (should start with "testmo_")
        description: Human-readable description of what the tool does
        input_schema: JSON Schema for the tool's input parameters
        requires_client: Whether the handler needs a TestmoClient instance

    Returns:
        Decorator function that registers the handler
    """

    def decorator(func: ToolHandler) -> ToolHandler:
        tool = Tool(
            name=name,
            description=description,
            inputSchema=input_schema,
        )
        _tool_registry[name] = ToolDefinition(
            tool=tool,
            handler=func,
            requires_client=requires_client,
        )
        return func

    return decorator


def get_all_tools() -> list[Tool]:
    """Get all registered tool definitions."""
    return [td.tool for td in _tool_registry.values()]


def get_handler(name: str) -> ToolDefinition | None:
    """Get a tool definition by name."""
    return _tool_registry.get(name)


def get_all_tool_names() -> list[str]:
    """Get names of all registered tools."""
    return list(_tool_registry.keys())
