## Copilot instructions for this repo

Short version: this project builds a searchable Mojo manual and exposes it via an MCP server. The data is prepared offline into a DuckDB file with FTS + HNSW indexes; the runtime server performs hybrid search (vector + BM25) and returns snippets and resource views.

### Architecture (what lives where)
- Preprocessing (offline) — `preprocessing/src/*`
  - `pipeline.py` reads `manual/**.mdx`, cleans MDX, extracts metadata, and produces `processed_docs/{raw,metadata,chunks,manifest.json}`.
  - Chunking is tokenizer-aware for `sentence-transformers/all-mpnet-base-v2` (target ~350–400 tokens, 50–80 overlap) via `LangchainMarkdownChunker`.
- Embeddings + Lake → DB (offline) — `embedding/*`
  - `generate_embeddings.py` → `processed_docs/embeddings/*_embeddings.jsonl` via MAX server (OpenAI-compatible API).
  - `consolidate_data.py` → `processed_docs/mojo_manual_embeddings.parquet` (joins chunks + embeddings).
  - `load_to_ducklake.py` → versioned DuckLake table `mojo_docs` in `mojo_catalog.ducklake`.
  - `create_indexes.py` materializes `mojo_docs_indexed` into `main.db` and builds:
    - HNSW index on `embedding` (FLOAT[768], metric='cosine'), and
    - FTS index on `title`, `content` (BM25).
- Runtime (online) — `runtime/`
  - `runtime/search.py` implements `HybridSearcher` using DuckDB VSS + FTS with RRF fusion.
  - `runtime/mcp_server/server.py` exposes MCP tool/resource APIs and reuses `HybridSearcher`.

### Dev workflows (use these tasks/commands)
- Pixi tasks (see `pixi.toml`):
  - `pixi run process` → preprocess docs (creates `processed_docs/`).
  - `pixi run generate-embeddings` → write embeddings JSONL via MAX.
  - `pixi run consolidate` → build Parquet combined dataset.
  - `pixi run load` → load Parquet into DuckLake catalog.
  - `pixi run index` → create `main.db` with HNSW + FTS indexes.
  - `pixi run search` → CLI hybrid search using `search.py`.
  - `pixi run max-serve` → start MAX embeddings server.
  - `pixi run mcp-dev` → run MCP Inspector with `mcp_server/server.py`.

### Runtime config (key env vars and defaults)
- `MOJO_DB_PATH=main.db`, `MOJO_TABLE_NAME=mojo_docs_indexed`.
- `MAX_SERVER_URL=http://localhost:8000/v1`, `EMBED_MODEL_NAME=sentence-transformers/all-mpnet-base-v2`.
- `EMBED_CACHE_SIZE=512` (LRU for query embeddings).
- In `mcp_server/server.py`, `AUTO_START_MAX=1` attempts to `max serve` if the endpoint isn’t reachable (stdio is isolated; stdio streams are suppressed).

### Search behavior and conventions (important when editing)
- Vector search uses `array_cosine_distance(embedding, CAST(? AS FLOAT[768]))` to trigger HNSW acceleration; expect 768-dim vectors.
- FTS uses BM25 with field weighting: title weight = 2.0, content weight = 1.0. There’s a LIKE-based fallback for older DuckDB/FTS.
- Hybrid scoring is Reciprocal Rank Fusion (RRF) over VSS and FTS rankings.
- If embeddings fail (MAX down), the system gracefully falls back to FTS-only.
- Data shape relied on at runtime: columns `chunk_id`, `title`, `content`, `url`, `section_hierarchy` (JSON array) in `mojo_docs_indexed`.

### Adding/changing features (what to update together)
- Schema tweaks: update both the materialization (`embedding/create_indexes.py`) and any runtime selectors in `runtime/search.py` and `runtime/mcp_server/server.py`.
- New metadata fields: thread them through `consolidate_data.py` → `load_to_ducklake.py` → `create_indexes.py`; runtime currently renders title/section/url/snippet only.
- New tools/resources: add `@mcp.tool()`/`@mcp.resource()` in `runtime/mcp_server/server.py`; prefer small Pydantic models for stable outputs.

### Examples (useful entry points)
- CLI search: `pixi run search` (or `python search.py -q "ownership" -k 5`).
- MCP resources: `mojo://search/{q}`, `mojo://chunk/{chunk_id}` (see `runtime/README.md`).
- VS Code/Copilot MCP: point a server entry to `runtime/mcp_server/server.py` with `cwd` containing `main.db`.

### Debugging tips (non-obvious)
- Set `DEBUG_EXPLAIN_VSS=True` or `DEBUG_LOG_FTS_PATH=True` in `runtime/search.py` while iterating to confirm HNSW and FTS paths.
- If HNSW isn’t used, verify embedding type is `FLOAT[768]`, metric='cosine', and index exists (`CREATE INDEX ... USING HNSW`).
- If results look empty, confirm `main.db` exists and table `mojo_docs_indexed` has rows; re-run `pixi run index` after upstream changes.
