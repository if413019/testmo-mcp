# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP Testmo is a Python-based Model Context Protocol (MCP) server that integrates AI assistants with Testmo test case management. It provides 30+ tools for managing test cases, folders, projects, test runs, automation, and issues.

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
├── server.py       # MCP server entry point, tool dispatch via registry
├── client.py       # Async HTTP client for Testmo REST API (httpx)
├── config.py       # FIELD_MAPPINGS dict (instance-specific IDs for priorities, types, tags, etc.)
├── utils.py        # Response formatters (format_result, format_error)
└── tools/          # Tool definitions organized by domain
    ├── base.py     # @register_tool decorator and global tool registry
    ├── cases.py    # Test case CRUD, batch ops, search
    ├── folders.py  # Folder management
    ├── projects.py # Project listing
    ├── runs.py     # Test runs
    ├── run_results.py
    ├── issues.py   # Issue connections
    ├── milestones.py
    ├── attachments.py
    ├── automation_runs.py
    ├── automation_sources.py
    └── utility.py  # Field mappings, web URL tools
```

**Key patterns:**
- All I/O is async (asyncio + httpx)
- `TestmoClient` uses async context manager (`async with`) for HTTP lifecycle
- Global client instance is lazy-initialized in `server.py`
- Tools use a **decorator-based registry**: `@register_tool(name, description, input_schema)` in each domain module. Importing `tools/__init__.py` triggers registration of all tools.
- Tool handlers have signature `async def handler(client: TestmoClient, args: dict) -> Any` (or just `args` if `requires_client=False`)
- `FIELD_MAPPINGS` in `config.py` contains example Testmo instance IDs — customize for your instance

**Adding a new tool:**
1. Add the handler in the appropriate `tools/*.py` module using `@register_tool`
2. If creating a new domain module, import it in `tools/__init__.py`
3. Add corresponding client method in `client.py` if needed

**Request flow:**
1. MCP server receives tool call via stdio
2. `call_tool()` looks up handler from registry via `get_handler(name)`
3. Handler receives client + args, calls `TestmoClient` methods
4. Client makes async HTTP request to Testmo API
5. Response formatted as JSON and returned via MCP

## Testmo API Client Details

- Base URL: `{TESTMO_URL}/api/v1`
- Auth: Bearer token via `TESTMO_API_KEY`
- Rate limiting: 0.5s delay between paginated requests
- Batch operations: 100 cases max per request, auto-batching available
- Custom exception: `TestmoAPIError` with status code, message, details

## Testing

Tests use pytest-asyncio with `asyncio_mode = "auto"`. Fixtures in `conftest.py` provide mock environment variables and sample data. Test files: `test_client.py` and `test_server.py`.

## Linting/Formatting

- Ruff: line-length 100, target Python 3.10, rules E/F/I/N/W/UP (E501 ignored)
- mypy: strict (`disallow_untyped_defs`, `warn_return_any`)
