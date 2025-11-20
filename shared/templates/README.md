# MCP Server Templates

This directory contains templates used by the `scaffold_new_mcp.sh` script to create new MCP servers.

## Template Files

### Python Code Templates

- **`search_template.py`** - Hybrid search implementation using DuckDB VSS + FTS
  - Implements `HybridSearcher` class with vector and full-text search
  - Configurable via environment variables
  - LRU cache for query embeddings
  - Graceful fallback when MAX server unavailable

- **`mcp_server_template.py`** - MCP server entry point using FastMCP
  - Exposes search tools and resources
  - Auto-starts MAX server if configured
  - Loads configuration from YAML files
  - Includes health checks and connection probing

### Configuration Templates

- **`processing_config_template.yaml`** - Preprocessing configuration
  - Source documentation paths and formats
  - Chunking parameters
  - Processing options (JSX removal, code block preservation, etc.)
  - Output directory structure

- **`server_config_template.yaml`** - Server runtime configuration
  - Database paths and table names
  - Embedding server settings
  - Search parameters (weights, cache sizes, debug flags)
  - Auto-start options

### Project Files

- **`requirements_template.txt`** - Python dependencies for runtime
  - DuckDB, OpenAI client, NumPy, requests, PyYAML, MCP
  - Version constraints for compatibility

- **`README_template.md`** - Server README with setup instructions
  - Quick start for both pixi and venv
  - VS Code configuration examples
  - Build instructions
  - Environment variable documentation

## Template Placeholders

Templates use the following placeholders that are replaced during scaffolding:

| Placeholder | Example Value | Description |
|-------------|---------------|-------------|
| `{{TOOL_NAME}}` | `mojo` | Tool name (lowercase) |
| `{{DOC_TYPE}}` | `manual` | Documentation type (lowercase) |
| `{{MCP_NAME}}` | `mojo-manual-mcp` | Full MCP server name |
| `{{MCP_NAME_UPPER}}` | `MOJO_MANUAL_MCP` | Uppercase for env vars |
| `{{DOC_TYPE_TITLE}}` | `Mojo Manual` | Title-cased for display |
| `{{FORMAT}}` | `mdx` | Documentation format |
| `{{FORMAT_EXT}}` | `mdx` | File extension |
| `{{URL_BASE}}` | `https://docs.modular.com/mojo/manual` | Base URL |

## Usage

These templates are used automatically by `tools/scaffold_new_mcp.sh`:

```bash
./tools/scaffold_new_mcp.sh --name mojo --doc-type manual
```

This will:
1. Copy all templates to `servers/mojo-manual-mcp/`
2. Replace all placeholders with actual values
3. Rename files appropriately (e.g., `mcp_server_template.py` → `mojo_manual_mcp_server.py`)

## Customizing Templates

To modify the default structure of new MCP servers:

1. Edit the appropriate template file in this directory
2. Add new placeholders if needed (update `scaffold_new_mcp.sh` accordingly)
3. Test by scaffolding a new server
4. Document changes in this README

## Template Maintenance

When updating templates:

- **Keep placeholders consistent** across all files
- **Test with `scaffold_new_mcp.sh`** to ensure proper substitution
- **Update this README** if adding/removing placeholders
- **Maintain linting compliance** (templates should be valid Python/YAML when placeholders are replaced)

## Notes

- Python templates may show import errors in IDEs since `search` module doesn't exist in the templates directory - this is expected and will resolve when copied to a server directory
- Templates are version-controlled - changes affect all future MCP servers created with the scaffold script
- Existing servers are not automatically updated when templates change

## See Also

- Tools documentation: `../tools/README.md`
- Scaffold script: `../tools/scaffold_new_mcp.sh`
- Example server: `../../servers/mojo-manual-mcp/`
