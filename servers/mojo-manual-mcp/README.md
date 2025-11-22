# Mojo Manual MCP Server

Searchable Mojo documentation via MCP (Model Context Protocol). This server is self-contained and ready to use immediately—it includes pre-built indexes for fast hybrid search (vector + keyword).

## Quick Start

### With Pixi (Recommended)

```bash
# Clone the repo and navigate to the server directory
git clone jpotter80/mcp
cd /path/to/mcp/servers/mojo-manual-mcp

# Install dependencies in servers/mojo-manual-mcp
pixi install
```

Add to your VS Code `mcp.json` (User Settings → Settings JSON):

```json
{
  "servers": {
    "mojo-manual": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "serve"],
      "cwd": "/absolute/path/to/mojo-manual-mcp"
    }
  }
}
```

Replace `/absolute/path/to/mojo-manual-mcp` with your actual path.

**Alternative (venv):**
```json
{
  "servers": {
    "mojo-manual": {
      "type": "stdio",
      "command": "python",
      "args": ["runtime/mojo_manual_mcp_server.py"],
      "cwd": "/absolute/path/to/mojo-manual-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/mojo-manual-mcp"
      }
    }
  }
}
```

## Configuration

The server is configured via `config/server_config.yaml`. Override default settings with environment variables:

- `MOJO_DB_PATH`: Path to the DuckDB database (default: `runtime/mojo_manual_mcp.db`)
- `MAX_SERVER_URL`: URL for MAX embeddings server (default: `http://localhost:8000/v1`)
- `EMBED_MODEL_NAME`: Model name (default: `sentence-transformers/all-mpnet-base-v2`)
- `AUTO_START_MAX`: Auto-start MAX server if needed (default: `1`)

## Testing the Server

### Using MCP Inspector

```bash
pixi run mcp-dev
```

Opens an interactive inspector in your browser to test search and explore resources.


## Rebuilding the Database

The database includes all Mojo documentation. If you want to rebuild it (e.g., when Modular releases updates):

From the project root directory:
```bash
pixi run mojo-build
```

This runs the full pipeline:
1. `mojo-process` — Extract and chunk documentation
2. `mojo-generate-embeddings` — Generate vector embeddings
3. `mojo-consolidate` — Combine into Parquet format
4. `mojo-load` — Load into DuckLake
5. `mojo-index` — Create materialized indexes

**Note**: You'll need MAX server running for this: `pixi run max-serve`

## Architecture

- `runtime/mojo_manual_mcp_server.py` — MCP server entry point
- `runtime/search.py` — Hybrid search engine (HNSW + BM25)
- `runtime/mojo_manual_mcp.db` — Indexed DuckDB database
- `config/server_config.yaml` — Configuration template

## Resources

For framework details and creating new servers, see the [main project README](../../README.md).

