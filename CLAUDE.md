# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Testmo is a Python-based Model Context Protocol (MCP) server that integrates AI assistants with Testmo test case management. It provides 20+ tools for managing test cases, folders, projects, and test runs.

## Development Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run a single test
pytest tests/test_client.py::test_function_name

# Linting
ruff check .

# Type checking
mypy src

# Run the MCP server directly
mcp-testmo
```

## Environment Setup

Required environment variables (create `.env` file):
```bash
TESTMO_URL=https://your-instance.testmo.net
TESTMO_API_KEY=your-api-key-here
```

## Architecture

```
src/mcp_testmo/
├── server.py   # MCP server, tool definitions, tool handlers, field mappings
└── client.py   # Async HTTP client for Testmo REST API
```

**Key patterns:**
- All I/O is async (asyncio + httpx)
- `TestmoClient` uses async context manager (`async with`) for HTTP lifecycle
- Global client instance is lazy-initialized in server
- Tools are defined in `TOOLS` list with JSON Schema input validation
- Field mappings (FIELD_MAPPINGS dict) contain Nanovest-specific Testmo configuration IDs

**Request flow:**
1. MCP server receives tool call via stdio
2. `call_tool()` dispatches to `_execute_tool()`
3. Handler uses `get_client()` context manager to get/create client
4. Client makes async HTTP request to Testmo API
5. Response formatted as JSON and returned via MCP

## Testmo API Client Details

- Base URL: `{TESTMO_URL}/api/v1`
- Auth: Bearer token via `TESTMO_API_KEY`
- Rate limiting: 0.5s delay between paginated requests
- Batch operations: 100 cases max per request, auto-batching available
- Custom exception: `TestmoAPIError` with status code, message, details

## Testing

Tests use pytest-asyncio with `asyncio_mode = "auto"`. Fixtures in `conftest.py` provide mock environment variables and sample data.
