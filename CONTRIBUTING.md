# Contributing to MCP Testmo

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/if413019/testmo-mcp.git
   cd mcp-testmo
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Testmo credentials
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mcp_testmo

# Run a specific test
pytest tests/test_client.py::test_function_name
```

## Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Linting
ruff check .

# Auto-fix lint issues
ruff check . --fix

# Type checking
mypy src
```

## Pull Request Process

1. Fork the repository and create a feature branch
2. Make your changes with clear, focused commits
3. Add or update tests as needed
4. Ensure all tests and checks pass
5. Submit a pull request with a clear description

## Adding New Tools

When adding a new Testmo API tool:

1. Add the API method to `src/mcp_testmo/client.py`
2. Add the tool definition to the `TOOLS` list in `src/mcp_testmo/server.py`
3. Add the handler in `_execute_tool()` function
4. Add tests for both client method and tool handler
5. Update README.md with the new tool documentation

## Code Style

- Use type hints for all function parameters and return values
- Follow existing patterns in the codebase
- Keep functions focused and single-purpose
- Use async/await for all I/O operations
