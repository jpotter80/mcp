# System Architecture

Complete technical reference for the Documentation-to-MCP pipeline, including component interactions, data formats, and design principles.

## 🏗️ Overall Design

### Multi-Phase Pipeline

The system implements a **build-time pipeline** that generates a **lightweight runtime** for queries:

```
OFFLINE PHASE (Build)              ONLINE PHASE (Runtime)
─────────────────────              ──────────────────────

1. Preprocess                       → Embedding Server (cached)
   - Parse MDX/Markdown            ↓
   - Extract metadata              Search Engine
   - Clean content                 ↓
   - Chunk intelligently           MCP Server
                                   ↓
2. Generate Embeddings             Query Results
   - Vector embeddings (768-dim)
   
3. Consolidate Data
   - Merge chunks + embeddings
   - Quality filtering
   - Parquet output
   
4. Load to DuckLake
   - Versioned storage
   - Reproducibility
   
5. Create Indexes
   - HNSW vector index
   - FTS keyword index
   - Materialized view
```

### Why This Architecture?

- **Separation of Concerns**: Build-time is deterministic and reproducible; runtime is fast and lightweight
- **Versioning**: DuckLake provides complete history of data changes
- **Scalability**: Indexes enable sub-100ms queries over large corpora
- **Flexibility**: Supports any Markdown/MDX documentation source with configuration

---

## 📊 Build-Time Pipeline

### Phase 1: Preprocessing (`preprocessing/`)

**Input**: Markdown/MDX files with optional frontmatter, JSX components, code blocks

**Processing Steps**:

1. **MDX Parsing**
   - Extract YAML frontmatter (metadata)
   - Parse document structure
   - Identify code blocks and preserve them

2. **Content Cleaning**
   - Remove JSX imports and components
   - Normalize whitespace
   - Preserve code blocks with language identifiers
   - Clean markdown artifacts

3. **Chunking (Tokenizer-Aware)**
   - Uses `LangchainMarkdownChunker` with `sentence-transformers/all-mpnet-base-v2` tokenizer
   - Target: ~350–400 tokens per chunk (optimal for embedding model)
   - Overlap: ~80 tokens (20% for context preservation)
   - Strategy: Recursive split respecting Markdown headers
   - Fallback: Sentence and word splits preserve text integrity

4. **Metadata Extraction**
   - Document ID and file path
   - Section hierarchy (h1 → h6 mapping)
   - URLs and anchors
   - Code block presence/count

**Output**: 
- `processed_docs/raw/` — clean text
- `processed_docs/metadata/` — document metadata (JSON)
- `processed_docs/chunks/` — chunked content (JSONL, one chunk per line)
- `processed_docs/manifest.json` — processing summary

**Configuration**: `preprocessing/config/processing_config.yaml`

```yaml
source:
  directory: "/path/to/docs"
  file_patterns: ["*.mdx", "*.md"]

chunking:
  strategy: "recursive"
  chunk_size: 400           # tokens
  chunk_overlap: 80         # tokens
  min_chunk_size: 100       # tokens
  preserve_code_blocks: true

processing:
  remove_jsx_components: true
  normalize_whitespace: true
```

---

### Phase 2: Embedding Generation (`embedding/generate_embeddings.py`)

**Input**: Chunks from preprocessing

**Process**:
- Uses local embedding server (MAX or OpenAI-compatible endpoint)
- Model: `sentence-transformers/all-mpnet-base-v2` (768 dimensions)
- Batch processing for efficiency
- In-memory LRU cache to avoid re-encoding duplicates

**Output**: `processed_docs/embeddings/` — JSONL files with vectors

```json
{
  "chunk_id": "basics-001",
  "embedding": [0.123, -0.456, ..., 0.789]  // 768-dim float array
}
```

**Environment Variables**:
- `MAX_SERVER_URL=http://localhost:8000/v1`
- `EMBED_MODEL_NAME=sentence-transformers/all-mpnet-base-v2`
- `EMBED_CACHE_SIZE=512` (LRU cache size)

---

### Phase 3: Data Consolidation (`embedding/consolidate_data.py`)

**Input**: Chunks + embeddings + metadata

**Process**:
1. Merge chunks with their embeddings
2. Apply quality filters (minimum content length)
3. Ensure all required fields present
4. Generate comprehensive metadata

**Output**: `processed_docs/{project}_embeddings.parquet`

**Schema**:
```
chunk_id: string           # unique identifier
document_id: string        # source document
title: string             # chunk title/heading
content: string           # main text content
url: string               # original documentation URL
section_hierarchy: JSON   # nested section structure
section_url: string       # direct link to section
embedding: float[768]     # vector representation
token_count: int          # chunk size in tokens
has_code: bool            # contains code blocks
```

---

### Phase 4: Versioned Data Lake (`embedding/load_to_ducklake.py`)

**Input**: Parquet dataset from consolidation

**Process**:
1. Load Parquet into DuckLake versioned table (`{project}_docs`)
2. Record version metadata (timestamp, source, filters applied)
3. Maintain full history for reproducibility

**Output**: DuckLake catalog (`.ducklake/` directory)

**Why DuckLake?**
- Versioned storage (query historical data)
- Object storage friendly (S3, GCS compatible)
- Native integration with DuckDB
- Reproducible builds via version specification

---

### Phase 5: Indexing & Materialization (`embedding/create_indexes.py`)

**Input**: Versioned DuckLake table

**Process**:

1. **Materialize Latest Version**
   - Copy latest data from DuckLake to native DuckDB table (`{project}_docs_indexed`)
   - This table is the runtime search target

2. **Create Vector Index (HNSW)**
   - Index on `embedding` column (768-dimensional float array)
   - Metric: `cosine` (angle-based similarity)
   - Enables fast approximate nearest neighbor search
   - Persisted in `main.db` (experimental but stable for local dev)

3. **Create Full-Text Search Index (FTS)**
   - BM25 index on `title` and `content` columns
   - Weight: title × 2.0, content × 1.0
   - Enables keyword-based ranking

**Output**: `main.db` (DuckDB file with all indexes)

**Index Details**:

```sql
-- Vector Index (HNSW)
CREATE INDEX idx_embedding ON {project}_docs_indexed 
  USING HNSW (embedding) 
  WITH (metric = 'cosine');

-- FTS Index (BM25)
CREATE INDEX idx_fts ON {project}_docs_indexed 
  USING FTS (title, content);
```

---

## 🔍 Runtime Search

### Hybrid Search Architecture (`search.py`)

The runtime uses **Reciprocal Rank Fusion (RRF)** to combine two search methods:

#### 1. **Vector Search (Semantic)**

Finds chunks semantically similar to the query:

```python
# 1. Encode query to 768-dim vector
query_vector = embedding_model.encode(query)

# 2. Find nearest neighbors using HNSW index
results_vss = db.execute("""
  SELECT chunk_id, content, 
    array_cosine_distance(embedding, CAST(? AS FLOAT[768])) AS distance
  FROM {project}_docs_indexed
  ORDER BY distance
  LIMIT k
""", [query_vector])
```

**Advantages**: Understands meaning, synonyms, context
**Example**: Query "How do I declare a variable?" matches content about "defining variables"

#### 2. **Full-Text Search (Keyword)**

Finds chunks matching query terms exactly:

```python
# 1. Match BM25 relevance
results_fts = db.execute("""
  SELECT chunk_id, content, bm25_score
  FROM {project}_docs_indexed
  WHERE match_bm25(rowid, ?)
  ORDER BY bm25_score DESC
  LIMIT k
""", [query])
```

**Advantages**: Precise, exact matches, fast
**Example**: Query "declare variable" matches content with those exact words

#### 3. **RRF Fusion**

Combines both rankings intelligently:

```python
# Score = 1/rank_vss + 1/rank_fts (with optional weights)
# Default: equal weighting (0.5 each)
# Tunable: --fts-weight and --vss-weight flags
```

**Why RRF?**
- Avoids score scale mismatches (vector scores vs. BM25 scores)
- Robust combination method proven in IR research
- Both methods have complementary strengths

---

### MCP Server Interface (`mcp_server/server.py`)

Exposes the search engine via Model Context Protocol:

#### **Tool: `search`**

```python
@mcp.tool()
def search(
    query: str,
    k: int = 5,
    fts_weight: float = 0.5,
    vss_weight: float = 0.5
) -> List[SearchResult]:
    """
    Hybrid search over documentation.
    
    Args:
        query: Search query (natural language or keywords)
        k: Number of results to return
        fts_weight: Weight for keyword search (0.0–1.0)
        vss_weight: Weight for semantic search (0.0–1.0)
    
    Returns:
        List of SearchResult with chunk_id, title, url, section_hierarchy, snippet
    """
```

#### **Resources**

- `mojo://search/{q}` — Markdown formatted results for query `q`
- `mojo://chunk/{chunk_id}` — Single chunk as Markdown

---

## 📐 Data Formats

### Chunk Format (JSONL)

Each line in `processed_docs/chunks/*.jsonl`:

```json
{
  "chunk_id": "basics-001",
  "document_id": "basics",
  "position": 0,
  "title": "Hello World",
  "content": "# Hello World\n\nThis page shows...",
  "token_count": 387,
  "has_code": true,
  "section_hierarchy": [
    "Mojo language basics",
    "Hello world"
  ],
  "metadata": {
    "file_path": "manual/basics.mdx",
    "url": "https://docs.modular.com/mojo/manual/basics",
    "section_url": "https://docs.modular.com/mojo/manual/basics#hello-world"
  }
}
```

### Search Result Format

Returned by `search()` tool:

```python
SearchResult(
    chunk_id="basics-001",
    title="Hello World",
    url="https://docs.modular.com/mojo/manual/basics#hello-world",
    section_hierarchy=["Mojo language basics", "Hello world"],
    snippet="This page shows how to write your first Mojo program..."
)
```

### Manifest Format

`processed_docs/manifest.json`:

```json
{
  "processing_date": "2025-11-07T12:00:00Z",
  "source_directory": "/home/james/mcp/manual",
  "total_documents": 25,
  "total_chunks": 487,
  "configuration": {
    "chunk_size": 400,
    "chunk_overlap": 80,
    "preserve_code_blocks": true
  },
  "documents": [
    {
      "id": "basics",
      "file_path": "manual/basics.mdx",
      "title": "Mojo Language Basics",
      "chunks": 12,
      "tokens": 4632
    }
  ]
}
```

---

## 🎯 Design Principles

### 1. **Determinism & Reproducibility**

- All preprocessing is deterministic (same inputs → same outputs)
- Tokenizer-aware chunking ensures consistent chunk boundaries
- DuckLake versioning tracks all data transformations
- Enables bit-for-bit reproducible builds

### 2. **Performance**

- HNSW index: ~O(log N) query time (vs. O(N) for brute force)
- FTS index: ~O(log N) with early termination
- RRF: O(k) after combining top-k from each method
- In-memory LRU cache for query embeddings (avoid redundant encoding)

### 3. **Graceful Degradation**

- If embedding server unavailable → fall back to FTS-only search
- If FTS unavailable → vector search only (less ideal but functional)
- Short queries with no embeddings → keyword search
- Robust error handling at each pipeline phase

### 4. **Extensibility**

- Generic preprocessing pipeline works with any Markdown/MDX
- Configurable chunking parameters
- Pluggable embedding models (any OpenAI-compatible endpoint)
- Custom MCP server implementations per documentation source

### 5. **Data Integrity**

- Schema validation at each pipeline phase
- Quality filtering in consolidation (remove < 100-token chunks by default)
- Checksums and metadata tracking
- DuckLake versioning as audit trail

---

## 🔄 Workflow Sequence

### Building a New Documentation MCP

```
1. Configure source
   └─ Update preprocessing/config/processing_config.yaml
      └─ Set source directory, chunk sizes, etc.

2. Run preprocessing
   └─ pixi run process
   └─ Outputs: processed_docs/chunks/

3. Generate embeddings
   └─ pixi run generate-embeddings
   └─ Requires: MAX server running
   └─ Outputs: processed_docs/embeddings/

4. Consolidate
   └─ pixi run consolidate
   └─ Outputs: {project}_embeddings.parquet

5. Load to DuckLake
   └─ pixi run load
   └─ Outputs: {project}_catalog.ducklake/

6. Create indexes
   └─ pixi run index
   └─ Outputs: main.db (with HNSW + FTS)

7. Deploy runtime
   └─ pixi run max-serve (in terminal 1)
   └─ pixi run mcp-dev (in terminal 2)
   └─ OR configure VS Code MCP host
```

---

## 🛠️ Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   PREPROCESSING                              │
├──────────────────────────────────────────────────────────────┤
│  pipeline.py                                                 │
│  ├─ mdx_processor.py → clean content                         │
│  ├─ metadata_extractor.py → extract hierarchy               │
│  └─ chunker.py (LangchainMarkdownChunker) → split           │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                   EMBEDDINGS & STORAGE                        │
├──────────────────────────────────────────────────────────────┤
│  generate_embeddings.py → MAX server (localhost:8000)        │
│  consolidate_data.py → merge chunks + embeddings            │
│  load_to_ducklake.py → DuckLake versioning                  │
│  create_indexes.py → HNSW + FTS indexes                     │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                     RUNTIME                                  │
├──────────────────────────────────────────────────────────────┤
│  search.py (HybridSearcher)                                 │
│  ├─ VSS (HNSW) path                                         │
│  ├─ FTS (BM25) path                                         │
│  └─ RRF fusion                                              │
│       ↑                   ↓                                  │
│  MAX Server          mcp_server/server.py                   │
│  (embeddings)        (resources & tools)                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 📈 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Preprocess 25 docs | 1–2 min | Sequential file processing |
| Generate embeddings | 5–10 min | Depends on chunk count and MAX speed |
| Consolidate | <1 min | Parquet creation |
| Load to DuckLake | <1 min | Metadata operations |
| Create indexes | 1–2 min | HNSW + FTS materialization |
| **Search query** | **<100ms** | With warm indexes and server |
| **Embed query** | **200–500ms** | MAX server latency (first time) |

---

## 🔐 Security & Limitations

### Current Limitations

- **Local dev only**: DuckLake persistence is experimental; not recommended for production
- **Single-threaded search**: No concurrent query handling (by design)
- **In-memory embedding cache**: Limited to `EMBED_CACHE_SIZE` (default 512)

### Future Hardening

- Replace DuckLake persistence with prod-grade versioning
- Add query concurrency (connection pooling)
- Implement distributed embedding cache
- Add authentication/authorization for MCP server

---

## 📚 Reference

- **Vector Similarity**: [DuckDB VSS Extension](https://duckdb.org/docs/extensions/vss)
- **Full-Text Search**: [DuckDB FTS](https://duckdb.org/docs/extensions/fts)
- **Reciprocal Rank Fusion**: [RRF Algorithm (Cormack et al.)](https://dl.acm.org/doi/10.1145/1571941.1572114)
- **Transformer Embeddings**: [all-mpnet-base-v2 Model](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)

