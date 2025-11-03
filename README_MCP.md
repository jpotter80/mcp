# Mojo Docs MCP Server (Runtime)

This folder contains a minimal MCP server that exposes the Mojo manual via hybrid search (FTS + vector) over a DuckDB database.

End-users do NOT need the preprocessing/embedding pipeline. You only need:

- `mcp_server/server.py` – the MCP server
- `search.py` – hybrid search logic (DuckDB + MAX embeddings client)
- `main.db` – DuckDB file with FTS + cosine HNSW indexes (prebuilt)

## Requirements

- Python 3.12+
- Packages (installed via Pixi or pip):
  - `mcp[cli]` – MCP CLI and server runtime
  - `duckdb` – database engine
  - `openai` – used as a client for the local MAX server
- MAX runtime (for query embeddings):
  - Provided by `modular` package (already in Pixi deps)

## Start MAX (local embedding server)

Start the local model server (downloads the model on first run):

```bash
pixi run max-serve
```

This serves a compatible OpenAI-like embeddings API at `http://localhost:8000/v1`.

Environment variables you can override:

- `MAX_SERVER_URL` – default `http://localhost:8000/v1`
- `EMBED_MODEL_NAME` – default `sentence-transformers/all-mpnet-base-v2`
- `EMBED_CACHE_SIZE` – in-memory LRU cache size for query embeddings (default 512)
- `MOJO_DB_PATH` – path to DuckDB database (default `main.db`)
- `MOJO_TABLE_NAME` – name of the indexed table (default `mojo_docs_indexed`)

## Run the MCP server (Inspector)

```bash
pixi run mcp-dev
```

This launches the MCP Inspector bound to `mcp_server/server.py`.

Alternatively, run directly for stdio testing:

```bash
python mcp_server/server.py
```

## VS Code MCP host

Configure your VS Code MCP host/client to run the server with a working directory that contains `main.db`.

- Command: `mcp run mcp_server/server.py`
- Working Directory: project folder with `main.db`
- Environment (optional):
  - `MOJO_DB_PATH=/absolute/or/relative/path/to/main.db`
  - `MAX_SERVER_URL=http://localhost:8000/v1`

## Exposed interface

- Tool: `search(query: str, k: int=5)` → structured list with fields: `chunk_id`, `title`, `url`, `section_hierarchy`, `snippet`
- Resources:
  - `mojo://search/{q}` – returns a markdown list of top results for query `q`
  - `mojo://chunk/{chunk_id}` – returns a single chunk as markdown

## Notes

- The database `main.db` was built with cosine HNSW and FTS indexes and should be read-only in this runtime.
- The server uses an in-memory LRU cache for query embeddings to avoid re-encoding the same phrases during a session.
- To update data monthly, rebuild the DB via the preprocessing/embedding pipeline in this repo, then replace `main.db`.
