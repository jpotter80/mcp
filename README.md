# Documentation-to-MCP Pipeline

A general-purpose system for converting technical documentation (Markdown/MDX) into searchable, vectorized MCP servers with hybrid search capabilities.

## 🎯 Project Overview

This framework builds an end-to-end, reusable pipeline that:

1. **Preprocesses** technical documentation (Markdown/MDX → clean, semantic chunks)
2. **Generates** vector embeddings using sentence-transformers
3. **Consolidates** data with quality filtering
4. **Indexes** content using DuckDB with HNSW (vector) + FTS (keyword) search
5. **Exposes** search via MCP for integration with LLM hosts (VS Code, MCP Inspector, etc.)

### Core Value Proposition

- 🔍 **Hybrid Search**: Combines semantic (vector) and keyword (FTS) search via Reciprocal Rank Fusion
- 📦 **MCP Native**: Exposes documentation as resources and tools for AI agents
- 🚀 **Lightweight Runtime**: No heavy preprocessing needed to run the server
- 🎛️ **Tunable Weights**: Adjust FTS/vector search weights for different query profiles
- 💾 **Versioned Data**: DuckLake provides full history of document changes
- 🔄 **Reusable Framework**: Apply to any Markdown/MDX documentation source

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BUILD-TIME PIPELINE (Generic)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. Preprocessing      2. Embeddings       3. Consolidation              │
│  (MDX/MD → Chunks) →   (Chunks → Vectors) →  (Merge → Parquet)          │
│                                                                           │
│       ↓                      ↓                      ↓                     │
│  processed_docs/        embeddings/          {project}_embeddings.parquet
│  chunks/               *.jsonl                                           │
│                                                                           │
│  4. Data Lake          5. Indexing                                       │
│  (Versioning)    →     (DB Materialization)                             │
│       ↓                      ↓                                           │
│  {project}_              main.db                                        │
│  catalog.ducklake        (HNSW + FTS indexes)                           │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    RUNTIME INFRASTRUCTURE (Generic)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Embedding Server       Search Engine        MCP Server                  │
│  (Local LLM/MAX)   ←→   (Hybrid Search)  ←→  (Resource/Tool API)        │
│  localhost:8000         search.py            mcp_server/server.py       │
│  [openai-compat]        [DuckDB + RRF]       [stdio or inspect]         │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

**Example**: The Mojo documentation instantiation uses this same pipeline with `manual/*.mdx` as input.

## 🚀 Quick Start

### Minimal Runtime Setup (No Preprocessing)

If you have a pre-built search database (`main.db`):

```bash
# 1. Start embedding server (MAX or compatible OpenAI-like endpoint)
pixi run max-serve

# 2. In another terminal, run MCP server
pixi run mcp-dev
# or
python mcp_server/server.py
```

See **[RUNTIME.md](RUNTIME.md)** for detailed setup.

### Full Pipeline (Build from Documentation)

Example with Mojo documentation:

```bash
pixi run process                # Step 1: Clean & chunk MDX/MD
pixi run generate-embeddings    # Step 2: Create embeddings
pixi run consolidate            # Step 3: Merge & filter
pixi run load                   # Step 4: Version in DuckLake
pixi run index                  # Step 5: Materialize & index
```

See **[PREPROCESSING.md](PREPROCESSING.md)** for detailed pipeline info and configuration.

## 📋 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | **You are here** — Project overview & quick links |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Deep dive into design, components, data formats, and principles |
| [PREPROCESSING.md](PREPROCESSING.md) | Build-time: chunking strategy, configuration, quality assurance |
| [RUNTIME.md](RUNTIME.md) | Deployment: MCP server setup, MAX embeddings, environment config |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Dev workflows: full task reference, testing, troubleshooting |

## 🛠️ Key Technologies

- **Python 3.12+** — Preprocessing and runtime
- **DuckDB** — Vector similarity search (HNSW) + full-text search (FTS)
- **DuckLake** — Versioned data lake for reproducibility
- **MAX** — Local sentence-transformers embeddings server
- **MCP** — Model Context Protocol for AI agent integration
- **Pixi** — Python package and task management

## 💾 Storage Architecture

```
Runtime Artifacts:
├── main.db                          # DuckDB with HNSW + FTS indexes
├── search.py                        # Hybrid search engine
├── mcp_server/server.py             # MCP resource/tool interface
└── requirements.txt (via pixi)      # Dependencies

Build Artifacts (processed_docs/):
├── chunks/                          # JSONL per document
├── embeddings/                      # Vector embeddings
├── metadata/                        # Document metadata
├── raw/                             # Clean text
└── manifest.json                    # Processing summary

Versioning:
└── {project}_catalog.ducklake       # DuckLake versioned tables
```

**Note**: Each documentation source gets its own `processed_docs/` and DuckLake catalog. The Mojo example uses `mojo_catalog.ducklake`.

## 🎓 Understanding the System

### Data Flow Example (Mojo Documentation)

1. **Input**: `manual/basics.mdx` (MDX with frontmatter, JSX, code blocks)
2. **After Preprocessing**: 12 chunks (~350–400 tokens each) with section hierarchy
3. **After Embeddings**: Each chunk has a 768-dimensional vector
4. **After Indexing**: DuckDB table `mojo_docs_indexed` with HNSW + FTS indexes ready for search
5. **Query Time**: "How do I declare a variable?" → hybrid search → top 5 results with snippets + URLs

### Search Behavior

- **Vector Search**: Finds semantically similar content (e.g., "variable declaration" ≈ "how to define a variable")
- **Keyword Search**: Matches exact phrases and terms (e.g., "declare" + "variable")
- **RRF Fusion**: Combines rankings intelligently; tunable weights favor one or the other
- **Fallback**: If embeddings unavailable, gracefully falls back to keyword-only search

### Generic Adaptation

To use this pipeline with different documentation:

1. Update `preprocessing/config/processing_config.yaml` to point to your source directory
2. Adjust chunking parameters for your documentation style
3. Run the full pipeline (`pixi run process` → `pixi run index`)
4. Create a project-specific `mcp_server/server.py` or adapt the generic one

## 🔄 Workflow Overview

| Phase | Input | Output | Time | Repeatability |
|-------|-------|--------|------|---------------|
| Preprocessing | Markdown/MDX files | `processed_docs/chunks/` | 1–2 min | Always deterministic |
| Embeddings | Chunks | Vector embeddings | 5–10 min | Deterministic (same model) |
| Consolidation | Embeddings + chunks | Parquet dataset | <1 min | Deterministic |
| Data Lake | Parquet | Versioned table | <1 min | Append/upsert |
| Indexing | Versioned table | Indexed DuckDB | 1–2 min | Full refresh each time |
| **Runtime** | **main.db** | **Search results** | **<100ms** | **Stable** |

## 🎛️ Configuration & Tuning

All major components are configurable:

- **Preprocessing**: `preprocessing/config/processing_config.yaml` — chunk size, overlap, JSX handling
- **Embeddings**: `MAX_SERVER_URL`, `EMBED_MODEL_NAME` environment variables
- **Search Weights**: `--fts-weight` and `--vss-weight` CLI flags in `search.py`
- **Runtime**: `MOJO_DB_PATH`, `MOJO_TABLE_NAME` environment variables

See **[DEVELOPMENT.md](DEVELOPMENT.md)** for complete reference.

## ✅ Status & Next Steps

### Current State
- ✅ Generic preprocessing pipeline established and tested (with Mojo as proof-of-concept)
- ✅ Embedding generation with MAX/OpenAI-compatible servers working
- ✅ DuckDB indexing with HNSW + FTS functional
- ✅ MCP server exposing resources and tools
- ✅ Hybrid search with RRF fusion implemented

### Known Improvements (Future)
- 📋 Enhanced code-fence–aware chunking (preserve code blocks better)
- 📋 Richer section hierarchy and URL generation
- 📋 Token-based quality filtering in consolidation
- 📋 Optional full-refresh mode for DuckLake upserts
- 📋 Multi-documentation support (simultaneous MCP servers for different docs)

## 📚 Learning More

- **System deep dive**: Read [ARCHITECTURE.md](ARCHITECTURE.md)
- **Set up build pipeline**: Follow [PREPROCESSING.md](PREPROCESSING.md)
- **Deploy to production**: Follow [RUNTIME.md](RUNTIME.md)
- **Development & debugging**: See [DEVELOPMENT.md](DEVELOPMENT.md)

## 🔗 External Resources

- [DuckDB Documentation](https://duckdb.org/docs)
- [DuckDB Vector Similarity Search (VSS)](https://duckdb.org/docs/extensions/vss)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Mojo Documentation](https://docs.modular.com/mojo/manual)

---

**Last Updated**: November 2025  
**Status**: Stable (build pipeline complete, runtime ready)
