# Duckdb Docs MCP Server

Searchable Duckdb Docs documentation via MCP (Model Context Protocol).

## Quick Start

### With Pixi (Recommended)

```bash
# Clone the repo and navigate to the server directory
git clone jpotter80/mcp
cd /path/to/mcp/servers/duckdb-docs-mcp

# Install dependencies in servers/mojo-manual-mcp
pixi install
```

Add to your VS Code `mcp.json` (User Settings → Settings JSON):

```json
{
  "servers": {
    "duckdb-docs": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "serve"],
      "cwd": "/home/james/mcp/servers/duckdb-docs-mcp",
      "env": {
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
		    "AUTO_START_MAX": "1"
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

- `runtime/duckdb_docs_mcp_server.py` — MCP server entry point
- `runtime/search.py` — Hybrid search engine
- `runtime/duckdb_docs_mcp.db` — Indexed DuckDB database

For more details, see the main project README.
