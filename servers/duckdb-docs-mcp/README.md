# Duckdb Docs MCP Server

Searchable Duckdb Docs documentation via MCP (Model Context Protocol).

## Quick Start

### Option 1: With Python venv (No pixi required)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Run the server
mcp dev runtime/duckdb-docs-mcp_mcp_server.py
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
    "duckdb-docs": {
      "command": "python3",
      "args": ["/absolute/path/to/servers/duckdb-docs-mcp/runtime/duckdb-docs-mcp_mcp_server.py"],
      "cwd": "/absolute/path/to/servers/duckdb-docs-mcp/runtime",
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
- `DUCKDB_DOCS_MCP_DB_PATH`: Path to the DuckDB database
- `MAX_SERVER_URL`: URL for the MAX embeddings server
- `EMBED_MODEL_NAME`: Model name for embeddings
- `AUTO_START_MAX`: Set to "1" or "true" to auto-start MAX server

## Rebuilding the Database

If you update documentation sources:
```bash
pixi run duckdb-process
pixi run duckdb-embed
pixi run duckdb-consolidate
pixi run duckdb-load
pixi run duckdb-index
```

(These tasks are in the root `/pixi.toml`)

## Resources

- `runtime/duckdb-docs-mcp_mcp_server.py` — MCP server entry point
- `runtime/search.py` — Hybrid search engine
- `runtime/duckdb-docs-mcp.db` — Indexed DuckDB database

For more details, see the main project README.
