"""
MCP Tools for Testmo.

This package contains all tool definitions organized by domain.
Import this module to register all tools with the registry.
"""

# Import all tool modules to trigger registration
from mcp_testmo.tools import (
    attachments,
    automation_runs,
    automation_sources,
    cases,
    composite,
    folders,
    issues,
    milestones,
    projects,
    run_results,
    runs,
    utility,
)

# Re-export registry functions for convenience
from mcp_testmo.tools.base import get_all_tool_names, get_all_tools, get_handler

__all__ = [
    "get_all_tools",
    "get_handler",
    "get_all_tool_names",
    # Tool modules
    "composite",
    "projects",
    "folders",
    "milestones",
    "cases",
    "issues",
    "runs",
    "run_results",
    "attachments",
    "automation_sources",
    "automation_runs",
    "utility",
]
