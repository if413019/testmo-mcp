# MCP Testmo

Model Context Protocol (MCP) server for [Testmo](https://www.testmo.com/) test case management. Enables AI assistants like Claude to manage test cases, folders, and projects in Testmo.

## Features

- **Project Management**: List and view Testmo projects
- **Folder Management**: Create, update, delete, and organize test case folders
- **Test Case CRUD**: Full create, read, update, delete operations for test cases
- **Batch Operations**: Create or delete multiple test cases efficiently
- **Search**: Search test cases by query, folder, tags, or state
- **Field Mappings**: Built-in mappings for priority, type, platform, and other custom fields
- **Test Runs**: View test runs and execution history

## Installation

### Using pip

```bash
pip install mcp-testmo
```

### Using uvx

```bash
uvx mcp-testmo
```

### From Source (Development)

```bash
git clone https://github.com/if413019/testmo-mcp.git
cd mcp-testmo
pip install -e ".[dev]"
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
TESTMO_URL=https://your-instance.testmo.net
TESTMO_API_KEY=your-api-key-here
```

Get your API key from Testmo: **Settings > API Keys**

### Claude Desktop Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "mcp-testmo": {
      "command": "uvx",
      "args": ["mcp-testmo"],
      "env": {
        "TESTMO_URL": "https://your-instance.testmo.net",
        "TESTMO_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Claude Code Configuration

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "mcp-testmo": {
      "command": "uvx",
      "args": ["mcp-testmo", "--env-file", ".env.testmo"]
    }
  }
}
```

## Available Tools

### Projects

| Tool | Description |
|------|-------------|
| `testmo_list_projects` | List all accessible projects |
| `testmo_get_project` | Get project details by ID |

### Folders

| Tool | Description |
|------|-------------|
| `testmo_list_folders` | List all folders with hierarchy |
| `testmo_get_folder` | Get folder details |
| `testmo_create_folder` | Create a new folder |
| `testmo_update_folder` | Update folder name or parent |
| `testmo_delete_folder` | Delete a folder (and its cases) |
| `testmo_find_folder_by_name` | Find folder by name |

### Test Cases

| Tool | Description |
|------|-------------|
| `testmo_list_cases` | List cases (paginated) |
| `testmo_get_all_cases` | Get all cases in folder |
| `testmo_get_case` | Get full case details |
| `testmo_create_case` | Create a single case |
| `testmo_create_cases` | Create multiple cases (max 100) |
| `testmo_batch_create_cases` | Create any number of cases |
| `testmo_update_case` | Update a case |
| `testmo_delete_case` | Delete a case |
| `testmo_batch_delete_cases` | Delete multiple cases |
| `testmo_search_cases` | Search with filters |

### Test Runs

| Tool | Description |
|------|-------------|
| `testmo_list_runs` | List test runs |
| `testmo_get_run` | Get run details |

### Utilities

| Tool | Description |
|------|-------------|
| `testmo_get_field_mappings` | Get field value mappings |
| `testmo_get_web_url` | Generate web URL for resource |

## Field Mappings

The server includes built-in mappings for Nanovest's Testmo configuration:

### Projects
- `nanovest`: 2
- `playground`: 6

### Priority (`custom_priority`)
- `Critical`: 52 (Financial loss, security breach, compliance violation)
- `High`: 1 (Core flow blocked, no workaround)
- `Medium`: 2 (Feature degraded but workaround exists)
- `Low`: 3 (Cosmetic issues or rare edge cases)

### Type (`custom_type`)
- `Functional`: 59
- `Acceptance`: 64
- `Security`: 55
- `Performance`: 57
- `Usability`: 53
- `Compatibility`: 61
- `Other`: 58

### Platforms (`configurations`)
- `Admin Portal`: 4
- `IOS & Android`: 5
- `Insti Web`: 10

### State (`state_id`)
- `Draft`: 1
- `Review`: 2
- `Approved`: 3
- `Active`: 4
- `Deprecated`: 5

### Tags
- **Domain** (required, pick one): `assets-crypto`, `assets-noncrypto`, `services-usergrowth`, `services-platform`, `wealth-hnwi`
- **Tier-Type** (required, pick one): `ui-verification`, `e2e`, `negative`
- **Scope** (optional): `regression`, `smoke`, `sanity`
- **Risk** (optional): `risk-financial`, `risk-security`, `risk-compliance`

## Usage Examples

### List Projects

```
Use testmo_list_projects to see available projects
```

### Create a Test Case

```
Use testmo_create_case with project_id=6 and case_data containing:
- name: "User can login with valid credentials"
- folder_id: 173750
- custom_priority: 1 (High)
- custom_type: 59 (Functional)
- custom_creator: 51 (AI Generated)
- custom_milestone_id: "release/5.2.0"
- custom_references: "IUG-1169"
- custom_issues_tags_and_configurations_added: 66 (Yes)
- custom_confluence_url: "https://nanovest.atlassian.net/wiki/..."
- custom_feature: "<pre><code class='editor-gherkin'>...</code></pre>"
- configurations: [5] (iOS & Android)
- tags: ["services-usergrowth", "e2e", "regression"]
```

### Search for Test Cases

```
Use testmo_search_cases with project_id=2 and:
- query: "login"
- tags: ["regression"]
- state_id: 4 (Active)
```

### Get Field Mappings

```
Use testmo_get_field_mappings to see all available field values
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/if413019/testmo-mcp.git
cd mcp-testmo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
ruff check .
mypy src
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Related Projects

- [mcp-atlassian](https://github.com/sooperset/mcp-atlassian) - MCP server for Jira and Confluence
- [Model Context Protocol](https://modelcontextprotocol.io/) - The MCP specification
