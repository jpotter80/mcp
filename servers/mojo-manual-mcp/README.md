# Mojo Manual MCP Server

Searchable Mojo documentation via MCP (Model Context Protocol).

## Quick Start

### Option 1: With Python venv (No pixi required)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd runtime
python mojo_manual_mcp_server.py
```

### Option 2: With pixi
```bash
pixi run mojo-build  # Rebuild database if needed
cd runtime
python mojo_manual_mcp_server.py
```

## Configure in VS Code

Add to VS Code settings.json:
```json
{
  "mcp.servers": {
    "mojo-docs": {
      "type": "stdio",
      "command": "python3",
      "args": ["/absolute/path/to/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"],
      "cwd": "/absolute/path/to/mojo-manual-mcp/runtime",
      "env": {
        "MOJO_DB_PATH": "/absolute/path/to/mojo-manual-mcp/runtime/mojo_manual_mcp.db",
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

## Configuration Files

- `config/processing_config.yaml` — Document processing parameters (for rebuilding)
- `config/server_config.yaml` — MCP server runtime parameters

## Rebuilding the Database

If you update documentation sources:
```bash
pixi run mojo-process
pixi run mojo-embed
pixi run mojo-consolidate
pixi run mojo-load
pixi run mojo-index
```

(These tasks are in the root `/pixi.toml`)

## Resources

- `runtime/mojo_manual_mcp_server.py` — MCP server entry point
- `runtime/search.py` — Hybrid search engine
- `runtime/mojo_manual_mcp.db` — Indexed DuckDB database

For more details, see the main project README.
