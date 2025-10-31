# Mojo Documentation Search Engine - Project Summary

## Project Status: In Progress - Chunking Strategy Upgrade

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
- **New Strategy**: The original chunker (`TechnicalDocChunker`) has been replaced with `LangchainMarkdownChunker`. This new approach is "tokenizer-aware." It uses `langchain`'s `MarkdownHeaderTextSplitter` to preserve semantic structure and `RecursiveCharacterTextSplitter` with the `sentence-transformers/all-mpnet-base-v2` tokenizer to create chunks that do not exceed the model's 384 token limit. This prevents silent truncation of input and is expected to significantly improve embedding quality.
- **Output**: `processed_docs/chunks/`

### 2. Embedding Generation ✅
- **Source**: `embedding/generate_embeddings.py`
- **Function**: Uses a `max serve` instance with `all-mpnet-base-v2` to generate 768-dimensional vector embeddings for each chunk.
- **Output**: `processed_docs/embeddings/`

### 3. Data Consolidation & Quality Filtering (Review Required) ⚠️
- **Source**: `embedding/consolidate_data.py`
- **Function**: Merges chunks, metadata, and embeddings. The previous filtering logic (e.g., `MIN_CHUNK_LENGTH`) may need to be re-evaluated based on the output of the new chunking strategy.
- **Output**: `processed_docs/mojo_manual_embeddings.parquet`

### 4. Versioned Data Lake (DuckLake) ✅
- **Source**: `embedding/load_to_ducklake.py`
- **Function**: Loads the consolidated Parquet file into a versioned DuckLake table (`mojo_docs`). This provides a full history of the data.
- **Output**: `mojo_catalog.ducklake` and its associated data files.

### 5. Indexed Search Database (DuckDB) ✅
- **Source**: `embedding/create_indexes.py`
- **Function**: Implements a "materialized view" pattern. It copies the latest data from the versioned DuckLake table into a native DuckDB table (`mojo_docs_indexed`) and builds high-performance search indexes (HNSW for vectors, FTS for keywords).
- **Output**: `main.db`

### 6. Hybrid Search Application ✅
- **Source**: `search.py`
- **Function**: A command-line tool that performs a hybrid search. It uses Reciprocal Rank Fusion (RRF) to intelligently combine results from vector search (semantic meaning) and full-text search (keywords). The search weights are tunable.

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

The chunking strategy has been upgraded. The next steps are to validate the new pipeline and assess the impact on search quality.

### 1. Run the Full Pipeline

Execute the entire data processing pipeline to regenerate all artifacts using the new chunking logic.

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

### 3. Experiment with Weights

Tune the FTS (keyword) and VSS (semantic) weights to see how they affect the results.

```bash
# Give more weight to keyword search
pixi run search -- -q "How do I declare a variable in Mojo?" --fts-weight 0.7 --vss-weight 0.3

# Give more weight to semantic search
pixi run search -- -q "How do I declare a variable in Mojo?" --fts-weight 0.2 --vss-weight 0.8
```

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

- **Problem**: Search results are still poor.
  - **Solution**: The new `LangchainMarkdownChunker` has tunable parameters (`chunk_size`, `chunk_overlap`) in `preprocessing/config/processing_config.yaml`. Adjust these and re-run the pipeline from `process` onwards.

## Conclusion

The project has successfully evolved from a simple preprocessing script into a complete, end-to-end hybrid search engine. It is currently undergoing a significant enhancement to its chunking logic to improve search relevance by aligning the chunking process with the embedding model's tokenization. The system is robust and ready for validation of the new strategy.

---

**Status**: ⚠️ In Progress
**Next Action**: Validate the new chunking pipeline and assess search quality.
**Estimated Time**: 30 minutes to run the pipeline and review results.
