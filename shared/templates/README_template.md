# {{DOC_TYPE_TITLE}} MCP Server

Searchable {{DOC_TYPE_TITLE}} documentation via MCP (Model Context Protocol).

## Quick Start

### Option 1: With Python venv (No pixi required)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Run the server
mcp dev runtime/{{MCP_NAME}}_mcp_server.py
```

### Option 2: With pixi
```bash
pixi run mcp-dev
```

## Configure in VS Code

Add to VS Code settings.json:
```json
{
  "mcp.servers": {
    "{{TOOL_NAME}}-docs": {
      "command": "python3",
      "args": ["/absolute/path/to/servers/{{MCP_NAME}}/runtime/{{MCP_NAME}}_mcp_server.py"],
      "cwd": "/absolute/path/to/servers/{{MCP_NAME}}/runtime",
      "env": {
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2"
      }
    }
  }
}
```

## Configuration

The server is configured via `config/server_config.yaml`.
You can override settings using environment variables:
- `{{MCP_NAME_UPPER}}_DB_PATH`: Path to the DuckDB database
- `MAX_SERVER_URL`: URL for the MAX embeddings server
- `EMBED_MODEL_NAME`: Model name for embeddings
- `AUTO_START_MAX`: Set to "1" or "true" to auto-start MAX server

## Rebuilding the Database

If you update documentation sources:
```bash
pixi run {{TOOL_NAME}}-process
pixi run {{TOOL_NAME}}-embed
pixi run {{TOOL_NAME}}-consolidate
pixi run {{TOOL_NAME}}-load
pixi run {{TOOL_NAME}}-index
```

(These tasks are in the root `/pixi.toml`)

## Resources

- `runtime/{{MCP_NAME}}_mcp_server.py` — MCP server entry point
- `runtime/search.py` — Hybrid search engine
- `runtime/{{MCP_NAME}}.db` — Indexed DuckDB database

For more details, see the main project README.
