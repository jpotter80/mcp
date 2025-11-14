# MojoDocs MCP Runtime Package

This folder collects only the runtime artifacts needed to install the Mojo manual MCP server in clients (e.g., VS Code/Copilot, Cursor, Claude Code).

Contents:
- mcp_server/server.py — MCP server exposing tools and resources
- search.py — hybrid search engine (DuckDB + MAX embeddings)
- main.db — DuckDB database with FTS + HNSW indexes
- README.md — these instructions

Note: Keep preprocessing/embedding pipeline out of the runtime package. Rebuild `main.db` offline and replace it here when you update docs.

## Install in VS Code / Copilot (stdio transport)

Create a settings file that registers the server (global or workspace):
- VS Code global: ~/.config/Code/User/settings.json (Linux)
- VS Code OSS forks may use a different path; for GitHub Copilot agent mode refer to its MCP UI or settings JSON.

Add an entry (adjust absolute paths):

{
  "mcp.servers": {
    "mojo-docs": {
      "type": "stdio",
      "command": "/usr/bin/python3",
      "args": ["mcp_server/server.py"],
      "cwd": "/absolute/path/to/runtime",
      "env": {
        "MOJO_DB_PATH": "/absolute/path/to/runtime/main.db",
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
        "AUTO_START_MAX": "1"  
      }
    }
  }
}

- `cwd` must be the runtime folder containing `main.db`.
- With `AUTO_START_MAX=1`, the server attempts to auto-start `max serve` if not reachable. To disable, set `AUTO_START_MAX=0`.
- You can pin an absolute Python path or use your environment’s python.

After saving, restart the MCP-enabled agent in VS Code (e.g., Copilot Chat agent mode) and it will discover:
- Tool: `search(query: str, k: int=5)`
- Resources: `mojo://search/{q}`, `mojo://chunk/{chunk_id}`

## Optional: Test with MCP Inspector

You can test from this folder with the Inspector:
- npx @modelcontextprotocol/inspector -- python mcp_server/server.py
  (or via `pixi run mcp-dev` from project root)

## Updating data

Rebuild the DuckDB (`main.db`) using the pipeline in the project root. Copy the new `main.db` into this `runtime/` folder.
