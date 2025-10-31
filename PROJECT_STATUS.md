# Mojo Documentation Search Engine - Project Summary

## Project Status: In Progress — Quality Fixes After Audit

This document provides a complete overview of the end-to-end hybrid search engine built for the Mojo manual. The system is currently undergoing a significant upgrade to its core document preprocessing and chunking strategy to improve search result quality.

## System Architecture

The system is a multi-stage pipeline that transforms raw documentation into a queryable search index.

```
┌─────────────────┐   ┌───────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌────────────────┐   ┌───────────────┐
│ 1. Preprocessing│   │ 2. Embeddings   │   │ 3. Consolidation │   │ 4. Data Lake     │   │ 5. Indexing    │   │ 6. Search    │
│ (MDX -> Chunks) │──▶│ (Chunks -> Vectors) │──▶│ (Merge -> Parquet) │──▶│ (Versioning)   │──▶│ (DB Materialize) │──▶│ (Hybrid Query)│
└─────────────────┘   └───────────────────┘   └──────────────────┘   └──────────────────┘   └────────────────┘   └───────────────┘
```

## What Has Been Created

### 1. Preprocessing Pipeline (Under Upgrade) ⚠️
- **Source**: `preprocessing/`
- **Function**: Parses MDX files, cleans content, and splits documents.
- **Current Strategy**: The original chunker was replaced with `LangchainMarkdownChunker`, a tokenizer-aware splitter using `RecursiveCharacterTextSplitter` with the `sentence-transformers/all-mpnet-base-v2` tokenizer and Markdown-aware separators to target the 384-token limit.
- **Planned Upgrade (audit action)**: Move to a two-phase split that first preserves section boundaries with `MarkdownHeaderTextSplitter`, then applies tokenizer-aware `RecursiveCharacterTextSplitter` within sections. Add code-fence–aware splitting and richer, accurate `section_hierarchy` and `section_url` generation using extracted anchors.
- **Output**: `processed_docs/chunks/`

### 2. Embedding Generation ✅
- **Source**: `embedding/generate_embeddings.py`
- **Function**: Uses a `max serve` instance with `all-mpnet-base-v2` to generate 768-dimensional vector embeddings for each chunk.
- **Output**: `processed_docs/embeddings/`

### 3. Data Consolidation & Quality Filtering (Review Required) ⚠️
- **Source**: `embedding/consolidate_data.py`
- **Function**: Merges chunks, metadata, and embeddings.
- **Planned Upgrade (audit action)**: Replace character-length filter with token-based thresholds; retain short but high-signal chunks (headers, definitions, code intros). Persist `token_count`, `has_code`, and `section_depth` for downstream weighting instead of early dropping.
- **Output**: `processed_docs/mojo_manual_embeddings.parquet`

### 4. Versioned Data Lake (DuckLake) ✅
- **Source**: `embedding/load_to_ducklake.py`
- **Function**: Loads the consolidated Parquet file into a versioned DuckLake table (`mojo_docs`). This provides a full history of the data.
- **Planned Upgrade (audit action)**: Fix upsert semantics by deleting by `document_id` (not `chunk_id`) before inserting, to avoid stale rows when chunking changes. Provide an optional full-refresh mode.
- **Output**: `mojo_catalog.ducklake` and its associated data files.

### 5. Indexed Search Database (DuckDB) ✅
- **Source**: `embedding/create_indexes.py`
- **Function**: Implements a "materialized view" pattern. It copies the latest data from the versioned DuckLake table into a native DuckDB table (`mojo_docs_indexed`) and builds high-performance search indexes (HNSW for vectors, FTS for keywords).
- Recent update (doc-driven):
  - HNSW index now uses the cosine metric as per the Vector Similarity Search docs. We leverage `ORDER BY array_cosine_distance(embedding, ?::FLOAT[768]) LIMIT k` to ensure HNSW acceleration.
  - FTS index is built with `chunk_id` as the document identifier and indexes the `title` and `content` columns. Queries use `fts_main_<table>.match_bm25(input_id := chunk_id, query_string := ?[, fields := 'title'|'content'])` with a title/content weighted combination.
  - Persistence: `hnsw_enable_experimental_persistence=true` is enabled to persist the HNSW index in `main.db` (experimental; safe for local dev, not production).
- **Output**: `main.db`

### 6. Hybrid Search Application ✅
- **Source**: `search.py`
- **Function**: A command-line tool that performs a hybrid search. It uses Reciprocal Rank Fusion (RRF) to intelligently combine results from vector search (semantic meaning) and full-text search (keywords). The search weights are tunable.
- Recent update (doc-driven):
  - Vector search now uses `array_cosine_distance` to align with the cosine HNSW index and benefit from index acceleration.
  - FTS calls now pass `chunk_id` as `input_id` to `match_bm25` and compute a weighted score: `2.0 * BM25(title) + 1.0 * BM25(content)` (tunable). A robust LIKE-based fallback remains for environments where FTS macros behave differently.
  - Added optional debug flags to print `EXPLAIN` for VSS (to check for `HNSW_INDEX_SCAN`) and log which FTS path was used.
  - CLI continues to honor `-k`; output includes section hierarchy and snippet.

### 7. Project & Task Management (Pixi) ✅
- **Source**: `pixi.toml`
- **Function**: Manages all dependencies and provides a single interface for running the entire pipeline via `pixi run <task>`.

## Final Project Structure

```
/home/james/mcp/
├── embedding/                      # Scripts for embeddings, consolidation, loading
│   ├── generate_embeddings.py
│   ├── consolidate_data.py
│   ├── load_to_ducklake.py
│   └── create_indexes.py
├── manual/                         # Original Mojo documentation (READ-ONLY)
├── preprocessing/                  # Preprocessing pipeline
├── processed_docs/                 # Intermediate processed files
├── main.db                         # Indexed DuckDB search database
├── mojo_catalog.ducklake           # DuckLake versioning catalog
├── search.py                       # Hybrid search CLI application
└── pixi.toml                       # Project configuration and tasks
```

## Final Workflow Commands

This sequence runs the entire pipeline from start to finish.

```bash
# 1. Process raw MDX files into chunks
pixi run process

# 2. Generate vector embeddings for the chunks
pixi run generate-embeddings

# 3. Consolidate all data and apply quality filters
pixi run consolidate

# 4. Load data into the versioned DuckLake
pixi run load

# 5. Create the materialized, indexed search database
pixi run index
```

## Next Steps: Validation and Quality Assurance

The chunking strategy has been upgraded, and an audit identified several high-impact fixes. The next steps are to implement the fixes below and validate the impact on search quality.

### 1. Apply fixes (summary)

- Preprocessing: two-phase split (headers → recursive), code-fence–aware boundaries, accurate `section_hierarchy` and `section_url`.
- Embeddings: prepend Title/Section context to embedded text; consider vector normalization if using cosine.
- Consolidation: switch to token-based quality filter; keep short but high-signal chunks; persist token/section features.
- DuckLake load: upsert by `document_id` (not `chunk_id`); add optional full-refresh mode.
- Indexing: FTS index on `content,title` only; query with `match_bm25(rowid, ?)`. Use cosine-based vss search that triggers HNSW.
- Search CLI: honor `-k`; richer output (hierarchy, snippet, section URL).

### 2. Run the Full Pipeline (post-fix)

Execute the entire data processing pipeline to regenerate all artifacts with the fixes applied.

```bash
pixi run process && \
pixi run generate-embeddings && \
pixi run consolidate && \
pixi run load && \
pixi run index
```

### 2. Run a Test Search

Execute a search query to see the new, ranked results.

```bash
# Use -- to pass arguments to the script
pixi run search -- -q "How do I declare a variable in Mojo?"
```

### 3. Experiment with Weights and Fusion

Tune the FTS (keyword) and VSS (semantic) weights to see how they affect the results.

```bash
# Give more weight to keyword search
pixi run search -- -q "How do I declare a variable in Mojo?" --fts-weight 0.7 --vss-weight 0.3

# Give more weight to semantic search
pixi run search -- -q "How do I declare a variable in Mojo?" --fts-weight 0.2 --vss-weight 0.8
```

Optionally compare RRF vs. weighted score fusion if exposed in the CLI.

---

## Recent fixes and compatibility findings

These issues were uncovered during end-to-end validation and have been addressed in code. They’re recorded here to keep a durable reference of behavior across environments.

- DuckDB FTS API alignment
  - Observation: The FTS docs specify an identifier column (input_id) and vararg text fields. Our index now uses `chunk_id` as `input_id` and indexes `title` and `content`. At query time we call `match_bm25(input_id := chunk_id, query_string := ?, fields := 'title'|'content')` and combine per-field scores with a title boost.
  - Result: Simpler, spec-compliant FTS usage. We kept a LIKE-based fallback for resilience.

- Materialized DB path mismatch
  - Observation: Indexer wrote to `../main.db` while the search app expected `main.db`.
  - Fix: Unified on `main.db` at the repository root.

- Upsert correctness
  - Observation: Deleting by `chunk_id` left stale rows when chunk IDs changed with a new chunking strategy.
  - Fix: Upsert now deletes by `document_id` before insert.

- Vector similarity and HNSW
  - Observation: To benefit from HNSW acceleration with cosine metric, queries must order by `array_cosine_distance` and limit k.
  - Fix: Use `array_cosine_distance(embedding, ?::FLOAT[768]) ORDER BY ... LIMIT k`. Added optional `EXPLAIN` to verify `HNSW_INDEX_SCAN`.

- Embedding input enrichment
  - Fix: Prepend Title/Section context to chunk text before embedding to improve semantic recall.

- Consolidation filtering
  - Fix: Relaxed minimum content length and preserved short, high-signal chunks (headers, intros). Persisted useful features (token_count, has_code, section data).

---

## Current observations (relevance)

- Query: “How do I declare a variable in Mojo?”
  - Returned results were valid pages but not the most relevant (“Variables” section). Likely causes:
    - Terminology mismatch: docs prefer “let” and “binding” vs. “declare variable”.
    - FTS treats title and content equally; a title-boost would help.
    - Fusion weights may overweight VSS when FTS has exact-title matches.

---

## Planned relevance improvements (scoped, low risk)

1) Title-boosted BM25 (FTS)
   - Compute separate BM25 scores over title-only and content-only, then combine: `score = 2.0 * title + 1.0 * content` (tunable). Use the same robust FTS fallbacks already implemented.

2) Lightweight query expansion (FTS-only)
   - Maintain a small synonym map for common terms (e.g., variable → [let, var, binding, assign]). Apply only to the FTS query string to improve lexical recall; keep VSS input unchanged.

3) Fusion tuning
   - Start with `--fts-weight 0.7 --vss-weight 0.3` for intent-led queries. Optionally add a “weighted fusion” mode (normalize and sum) later if needed.

4) Optional follow-up
   - Implement the two-phase, section-preserving chunker with code-fence awareness for another quality lift.

---

## Audit Findings and Fix Plan

Below is a concise list of identified quality risks and the corresponding mitigations to be implemented next.

- Stale rows in versioned table when chunking changes
  - Cause: Upsert deletes by `chunk_id`, leaving old chunks with changed IDs.
  - Fix: Delete by `document_id` before insert (or enable full-refresh mode).

- FTS returning weak/irrelevant matches
  - Cause: FTS index includes `chunk_id`; query uses `match_bm25(chunk_id, ?)`, which is incorrect for DuckDB.
  - Fix: Index only `content,title`. Query with `match_bm25(rowid, ?)`. Consider stemming/stopwords.

- Vector similarity not optimal
  - Cause: Using L2 distance; HNSW index may not be engaged.
  - Fix: Normalize vectors and use cosine with the vss operator/function that triggers HNSW.

- Over-aggressive consolidation filter
  - Cause: Drops chunks shorter than 200 chars, losing high-signal snippets.
  - Fix: Token-based threshold; keep short but meaningful chunks (headers, definitions, code intros).

- Chunk coherence and anchors
  - Cause: Single splitter sometimes breaks code blocks/sections; hierarchy is coarse.
  - Fix: Two-phase split with header preservation and code-fence awareness; richer `section_hierarchy` and exact `section_url`.

- Embeddings lack contextual headers
  - Cause: Model only sees raw chunk content.
  - Fix: Prepend Title/Section context to the embedding input text.

- CLI usability gaps
  - Cause: `-k` not honored; minimal rendering.
  - Fix: Pass `-k` through; display hierarchy, `section_url`, and a highlighted snippet.

---

## Troubleshooting Guide

- **Problem**: `pixi run search` fails with an argument error.
  - **Solution**: Ensure you are using ` -- ` to separate pixi commands from script arguments: `pixi run search -- -q "your query"`.

- **Problem**: `pixi run load` or `pixi run index` fails with a path or catalog error after a script change.
  - **Solution**: The DuckLake catalog may be inconsistent. Delete the old catalog and data, then re-run the load and index tasks.
    ```bash
    rm -f mojo_catalog.ducklake*
    rm -rf mojo_catalog.ducklake.files
    pixi run load
    pixi run index
    ```

- **Problem**: Row counts look larger than expected after a chunking change (stale results).
  - **Cause**: Upsert deleted by `chunk_id` instead of `document_id`, leaving old chunk rows.
  - **Solution**: Update the loader to delete by `document_id` before insert. For a clean slate, do a full refresh:
    ```bash
    rm -f mojo_catalog.ducklake*
    rm -rf mojo_catalog.ducklake.files
    # Optional: remove main.db if you want to fully rebuild
    rm -f main.db
    pixi run load
    pixi run index
    ```

- **Problem**: Search results are still poor.
  - **Solution**: After applying the fixes above, tune chunking parameters (`chunk_size`, `chunk_overlap`) in `preprocessing/config/processing_config.yaml` and adjust `--fts-weight/--vss-weight`. Verify that FTS uses `rowid` and VSS uses cosine with HNSW.

## Conclusion

The project has successfully evolved from a simple preprocessing script into a complete, end-to-end hybrid search engine. It is currently undergoing a significant enhancement to its chunking logic to improve search relevance by aligning the chunking process with the embedding model's tokenization. The system is robust and ready for validation of the new strategy.

---

**Status**: ⚠️ In Progress
**Next Action**: Implement the fixes in preprocessing, consolidation, loading, indexing, and search CLI; then rerun the full pipeline and evaluate results.
**Estimated Time**: ~45–60 minutes to implement and run, plus 10 minutes to review results.
