# Docling Docs MCP Server

Searchable Docling Docs documentation via MCP (Model Context Protocol).

## Quick Start

### With Pixi (Recommended)

```bash
# Clone the repo and navigate to the server directory
git clone https://github.com/jpotter80/mcp
cd /path/to/mcp/servers/docling-docs-mcp

# Install dependencies for this server
pixi install
```

## Configure in VS Code

Add to your VS Code `mcp.json` (User Settings → Settings JSON):

```json
{
  "servers": {
    "docling-docs": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "serve"],
      "cwd": "/path/to/mcp/servers/docling-docs-mcp",
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
- `DOCLING_DOCS_MCP_DB_PATH`: Path to the DuckDB database
- `MAX_SERVER_URL`: URL for the MAX embeddings server
- `EMBED_MODEL_NAME`: Model name for embeddings
- `AUTO_START_MAX`: Set to "1" or "true" to auto-start MAX server

## Rebuilding the Database

If you update documentation sources:
```bash
pixi run docling-process
pixi run docling-generate-embeddings
pixi run docling-consolidate
pixi run docling-load
pixi run docling-index
```

(These tasks are in the root `/pixi.toml`)

## Resources

- `runtime/docling_docs_mcp_server.py` — MCP server entry point
- `runtime/search.py` — Hybrid search engine
- `runtime/docling_docs_mcp.db` — Indexed DuckDB database

For more details, see the main project README.
