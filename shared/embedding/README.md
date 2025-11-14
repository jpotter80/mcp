# Shared Embedding Pipeline

This directory contains shared, parameterized scripts for building embedding datasets
and DuckDB/DuckLake indexes for MCP documentation servers.

## Scripts

All scripts live in the root `embedding/` directory and are intended for development-time
usage via pixi tasks or direct `python` invocations.

- `embedding/generate_embeddings.py`
  - Reads chunked documents and writes embedding JSONL files.
  - Uses the MAX server (OpenAI-compatible) to generate embeddings.
  - Respects:
    - `--mcp-name` (default: `mojo`)
    - `--config` (optional path to `processing_config.yaml`)
  - Input directory (for a given `--mcp-name`):
    - `shared/build/processed_docs/{mcp_name}/chunks`
  - Output directory:
    - `shared/build/embeddings/{mcp_name}`

- `embedding/consolidate_data.py`
  - Joins chunks, metadata, and embeddings into a single Parquet file.
  - Respects:
    - `--mcp-name` (default: `mojo`)
    - `--config` (optional; used for variable substitution only)
  - Reads from:
    - `shared/build/processed_docs/{mcp_name}/chunks`
    - `shared/build/embeddings/{mcp_name}`
  - Writes:
    - `shared/build/{mcp_name}_embeddings.parquet`

- `embedding/load_to_ducklake.py`
  - Loads the consolidated Parquet embeddings into a DuckLake catalog.
  - Respects:
    - `--mcp-name` (default: `mojo`)
  - Paths for a given `mcp_name`:
    - Catalog: `servers/{mcp_name}-manual-mcp/runtime/{mcp_name}_catalog.ducklake`
    - Parquet: `shared/build/{mcp_name}_embeddings.parquet`
    - Table: `{mcp_name}_docs`

- `embedding/create_indexes.py`
  - Materializes a native DuckDB table and builds HNSW + FTS indexes for search.
  - Respects:
    - `--mcp-name` (default: `mojo`)
  - Paths for a given `mcp_name`:
    - Catalog: `servers/{mcp_name}-manual-mcp/runtime/{mcp_name}_catalog.ducklake`
    - Source table: `{mcp_name}_docs`
    - Indexed table: `{mcp_name}_docs_indexed`
    - Main DB: `servers/{mcp_name}-manual-mcp/runtime/{mcp_name}_manual_mcp.db`

## Typical Mojo Workflow

From the project root:

1. Preprocess documentation:
   - `pixi run mojo-process`
2. Generate embeddings:
   - `pixi run mojo-generate-embeddings`
3. Consolidate into Parquet:
   - `pixi run mojo-consolidate`
4. Load into DuckLake catalog:
   - `pixi run mojo-load`
5. Create HNSW + FTS indexes:
   - `pixi run mojo-index`

Or run the full build:

- `pixi run mojo-build`

## Notes

- All scripts are designed to be reusable for future MCP servers by changing `--mcp-name`
  and pointing `--config` to the appropriate server configuration.
- The `config_loader` (`shared.preprocessing.src.config_loader`) is used for
  variable substitution but does not currently drive the `shared/build` layout; that
  layout is convention-based for Phase 3.
