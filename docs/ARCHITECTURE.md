# System Architecture

Complete technical reference for the multi-server MCP documentation search framework, including component interactions, data formats, and design principles.

## Table of Contents

- [Overview](#overview)
- [Multi-Server Architecture](#multi-server-architecture)
- [Build Pipeline](#build-pipeline)
- [Runtime Components](#runtime-components)
- [Data Formats](#data-formats)
- [Search Implementation](#search-implementation)
- [Configuration System](#configuration-system)
- [Design Principles](#design-principles)

## Overview

### System Design Philosophy

The system implements a **build-time pipeline** that generates **self-contained runtime servers** for documentation search:

```
OFFLINE PHASE (Build-Time)          ONLINE PHASE (Runtime)
────────────────────────            ──────────────────────

Documentation Sources                Embedding Server (MAX)
        ↓                                    ↓
1. Preprocess                           Query Embedding
   - Parse MDX/Markdown                      ↓
   - Extract metadata              ┌─────────────────────┐
   - Chunk intelligently           │   Hybrid Search     │
        ↓                          │  (Vector + Keyword) │
2. Generate Embeddings              └─────────────────────┘
   - 768-dim vectors                         ↓
        ↓                                MCP Server
3. Consolidate                           (stdio/http)
   - Merge + filter                          ↓
        ↓                              AI Assistant/Host
4. Load to DuckLake
   - Versioning
        ↓
5. Create Indexes
   - HNSW (vector)
   - FTS (keyword)
        ↓
  [Distributable Server]
```

### Key Characteristics

- **Separation of Concerns**: Build infrastructure (`/shared/`) vs. runtime servers (`/servers/`)
- **Self-Contained Servers**: Each server is fully standalone and distributable
- **Config-Driven**: All paths and parameters controlled via YAML
- **Multi-Format**: Pluggable processors for MDX, Markdown, etc.
- **Hybrid Search**: Vector similarity (HNSW) + keyword matching (FTS/BM25)
- **Versioned Data**: DuckLake provides reproducible builds

## Multi-Server Architecture

### Directory Structure

```
/mcp/
├── servers/                          # Self-contained MCP servers
│   ├── mojo-manual-mcp/              # Mojo documentation server
│   │   ├── runtime/                  # Distributable components
│   │   │   ├── mojo_manual_mcp_server.py
│   │   │   ├── search.py
│   │   │   ├── mojo_manual_mcp.db    # Indexed database
│   │   │   └── mojo_manual_catalog.ducklake
│   │   ├── config/
│   │   │   ├── processing_config.yaml
│   │   │   └── server_config.yaml
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── [other-mcp-servers]/          # Future servers
│
├── shared/                           # Build-time infrastructure (dev only)
│   ├── preprocessing/                # Document processing pipeline
│   │   └── src/
│   │       ├── pipeline.py
│   │       ├── processor_factory.py
│   │       ├── base_processor.py
│   │       ├── mdx_processor.py
│   │       ├── markdown_processor.py
│   │       └── chunker.py
│   ├── embedding/                    # Embedding generation scripts
│   │   ├── generate_embeddings.py
│   │   ├── consolidate_data.py
│   │   ├── load_to_ducklake.py
│   │   └── create_indexes.py
│   ├── templates/                    # Templates for new servers
│   │   ├── search_template.py
│   │   ├── mcp_server_template.py
│   │   └── *_config_template.yaml
│   └── build/                        # Ephemeral build artifacts
│
├── source-documentation/             # Raw documentation sources (dev only)
│   └── mojo/manual/
│
└── tools/                            # Automation scripts
    ├── sync_documentation.sh
    ├── scaffold_new_mcp.sh
    └── build_mcp.sh
```

## Build Pipeline

### Phase 1: Preprocessing

**Location**: `shared/preprocessing/`

**Input**: Raw documentation files (MDX, Markdown, RST, etc.)

**Process**:

1. **Format Detection & Routing**
   - `ProcessorFactory` selects appropriate processor based on config
   - Processors: `MDXProcessor`, `MarkdownProcessor`, extensible for others

2. **Document Processing**
   - Parse frontmatter (YAML metadata)
   - Clean MDX/JSX components
   - Normalize whitespace
   - Extract section hierarchy (h1-h6)
   - Preserve code blocks with language identifiers

3. **Chunking (Tokenizer-Aware)**
   - Uses `LangchainMarkdownChunker` with sentence-transformers tokenizer
   - Target: ~350-400 tokens per chunk (optimal for embedding model)
   - Overlap: ~50-80 tokens for context preservation
   - Strategy: Recursive split respecting Markdown structure
   - Fallback: Sentence/word splits preserve text integrity

**Output**:
```
shared/build/processed_docs/{mcp_name}/
├── raw/              # Cleaned text
├── metadata/         # Document metadata (JSON)
├── chunks/           # Chunked content (JSONL)
└── manifest.json     # Processing summary
```

**Configuration**: `servers/{mcp}/config/processing_config.yaml`

```yaml
source:
  directory: "${PROJECT_ROOT}/source-documentation/mojo/manual"
  format: "mdx"
  file_patterns: ["*.mdx", "*.md"]

output:
  base_directory: "${PROJECT_ROOT}/shared/build/processed_docs/mojo"

chunking:
  chunk_size: 256
  chunk_overlap: 50
  min_chunk_size: 50
  preserve_code_blocks: true
  tokenizer_model: "sentence-transformers/all-mpnet-base-v2"
```

### Phase 2: Embedding Generation

**Location**: `shared/embedding/generate_embeddings.py`

**Input**: Chunks from preprocessing

**Process**:
- Connects to MAX embedding server (OpenAI-compatible API)
- Model: `sentence-transformers/all-mpnet-base-v2` (768 dimensions)
- Batch processing for efficiency
- LRU cache to avoid re-encoding duplicates
- Health check: verifies MAX server accessibility before starting

**Output**: `shared/build/embeddings/{mcp_name}/*_embeddings.jsonl`

**Format**:
```json
{
  "chunk_id": "basics-001",
  "embedding": [0.123, -0.456, ..., 0.789]
}
```

**Environment Variables**:
- `MAX_SERVER_URL`: http://localhost:8000/v1
- `EMBED_MODEL_NAME`: sentence-transformers/all-mpnet-base-v2
- `EMBED_CACHE_SIZE`: 512 (LRU cache size)

### Phase 3: Data Consolidation

**Location**: `shared/embedding/consolidate_data.py`

**Input**: Chunks + embeddings + metadata

**Process**:
1. Merge chunks with their corresponding embeddings
2. Apply quality filters (minimum content length, valid embeddings)
3. Ensure all required fields present
4. Generate comprehensive metadata (URLs, section hierarchy)

**Output**: `shared/build/{mcp_name}_embeddings.parquet`

**Schema**:
```
chunk_id: string           # Unique identifier
document_id: string        # Source document
title: string              # Chunk title/heading
content: string            # Main text content
url: string                # Original documentation URL
section_hierarchy: JSON    # Nested section structure
embedding: float[768]      # Vector representation
token_count: int           # Chunk size in tokens
has_code: bool             # Contains code blocks
```

### Phase 4: Versioned Data Lake

**Location**: `shared/embedding/load_to_ducklake.py`

**Input**: Parquet dataset from consolidation

**Process**:
1. Load Parquet into DuckLake versioned table (`{mcp_name}_docs`)
2. Record version metadata (timestamp, source, filters applied)
3. Maintain full history for reproducibility

**Output**: `servers/{mcp}/runtime/{mcp_name}_catalog.ducklake`

**Benefits of DuckLake**:
- Versioned storage (query historical data)
- Object storage friendly (S3, GCS compatible)
- Native DuckDB integration
- Reproducible builds via version specification
- Rollback capability

### Phase 5: Indexing & Materialization

**Location**: `shared/embedding/create_indexes.py`

**Input**: Versioned DuckLake table

**Process**:

1. **Materialize Latest Version**
   - Copy latest data from DuckLake to native DuckDB table
   - Table name: `{mcp_name}_docs_indexed`

2. **Create Vector Index (HNSW)**
   ```sql
   CREATE INDEX hnsw_idx ON docs_indexed 
   USING HNSW (embedding) 
   WITH (metric='cosine');
   ```
   - Enables fast approximate nearest neighbor search
   - Cosine distance metric for semantic similarity

3. **Create Full-Text Search Index (FTS/BM25)**
   ```sql
   PRAGMA create_fts_index('docs_indexed', 
                          'chunk_id', 
                          'title', 'content', 
                          overwrite=1);
   ```
   - BM25 ranking algorithm
   - Field weights: title × 2.0, content × 1.0

**Output**: `servers/{mcp}/runtime/{mcp_name}_mcp.db` (final indexed database)

**Index Performance**:
- HNSW: O(log N) approximate search
- FTS: Sub-millisecond keyword matching
- Typical query time: <100ms

## Runtime Components

### Component 1: MCP Server

**Location**: `servers/{mcp}/runtime/{mcp}_mcp_server.py`

**Framework**: FastMCP (Python)

**Protocol**: Model Context Protocol (stdio or HTTP)

**Capabilities**:

1. **Tools** (functions AI can call):
   - `search(query, top_k)`: Hybrid search over documentation

2. **Resources** (URI-based content):
   - `{mcp}://search/{query}`: Search results
   - `{mcp}://chunk/{chunk_id}`: Specific chunk

**Startup Behavior**:
- Checks database existence
- Auto-starts MAX server if `AUTO_START_MAX=1` (production)
- Initializes search engine with config

**Environment Variables**:
```bash
{MCP_NAME_UPPER}_DB_PATH=/path/to/db
MAX_SERVER_URL=http://localhost:8000/v1
EMBED_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
AUTO_START_MAX=1  # Auto-start MAX (stdio is isolated)
```

### Component 2: Search Engine

**Location**: `servers/{mcp}/runtime/search.py`

**Class**: `HybridSearcher`

**Search Methods**:

1. **Vector Search (VSS)**
   ```python
   SELECT chunk_id, title, content, url,
          array_cosine_distance(embedding, ?) as distance
   FROM docs_indexed
   ORDER BY distance ASC
   LIMIT ?
   ```
   - Uses HNSW index
   - Cosine distance for similarity
   - Returns semantically similar content

2. **Keyword Search (FTS)**
   ```python
   SELECT chunk_id, fts_main_docs_indexed.match_bm25(
            chunk_id, 'query text', 
            fields := 'title,content',
            weights := '[2.0, 1.0]'
          ) as score
   FROM docs_indexed
   WHERE score IS NOT NULL
   ORDER BY score DESC
   LIMIT ?
   ```
   - BM25 ranking algorithm
   - Weighted field matching
   - Exact phrase and term matching

3. **Reciprocal Rank Fusion (RRF)**
   ```python
   rrf_score = Σ(1 / (k + rank_in_method))
   ```
   - Combines vector and keyword rankings
   - Parameter `k=60` (configurable)
   - Balanced fusion of both approaches

**Fallback Behavior**:
- If MAX server unavailable → keyword-only search
- If FTS unavailable → vector-only search
- Graceful degradation ensures availability

### Component 3: Embedding Server

**Technology**: MAX (Modular Accelerated Xecution)

**Model**: sentence-transformers/all-mpnet-base-v2

**API**: OpenAI-compatible HTTP endpoint

**Startup**:
```bash
max serve --model sentence-transformers/all-mpnet-base-v2
# Listens on http://localhost:8000
```

**Capabilities**:
- Generate embeddings for queries
- 768-dimensional vectors
- Batch processing support

**Alternative**: Any OpenAI-compatible embedding API (OpenAI, Azure OpenAI, etc.)

## Data Formats

### Chunk JSONL Format

```json
{
  "chunk_id": "basics-001",
  "document_id": "basics",
  "title": "Mojo Basics",
  "content": "Variables in Mojo are declared using var or let...",
  "url": "https://docs.modular.com/mojo/manual/basics",
  "section_hierarchy": ["Manual", "Basics", "Variables"],
  "section_url": "https://docs.modular.com/mojo/manual/basics#variables",
  "token_count": 347,
  "has_code": true
}
```

### Embedding JSONL Format

```json
{
  "chunk_id": "basics-001",
  "embedding": [0.0234, -0.0156, 0.0789, ...]  // 768 floats
}
```

### Consolidated Parquet Schema

```
chunk_id: string
document_id: string
title: string
content: string
url: string
section_hierarchy: list<string>
section_url: string
embedding: list<float>
token_count: int64
has_code: boolean
```

### DuckDB Indexed Table Schema

```sql
CREATE TABLE docs_indexed (
  chunk_id VARCHAR PRIMARY KEY,
  document_id VARCHAR,
  title VARCHAR,
  content VARCHAR,
  url VARCHAR,
  section_hierarchy JSON,
  section_url VARCHAR,
  embedding FLOAT[768],
  token_count INTEGER,
  has_code BOOLEAN
);

-- Indexes created automatically
-- HNSW index on embedding column
-- FTS index on title, content columns
```

## Search Implementation

### Query Flow

```
1. User Query
   ↓
2. Generate Query Embedding (via MAX)
   ↓
3. Vector Search (HNSW)
   - Top K candidates by cosine similarity
   ↓
4. Keyword Search (FTS/BM25)
   - Top K candidates by keyword relevance
   ↓
5. Reciprocal Rank Fusion
   - Combine rankings from both methods
   - Score = Σ(1 / (60 + rank))
   ↓
6. Re-rank and Return Top K
   - Includes: title, snippet, URL, scores
```

### RRF Fusion Details

**Formula**:
```
For each document:
  rrf_score = (1 / (k + vector_rank)) + (1 / (k + keyword_rank))

Where k = 60 (default)
```

**Example**:
```
Document A:
  Vector rank: 1, Keyword rank: 3
  RRF = 1/(60+1) + 1/(60+3) ≈ 0.0164 + 0.0159 = 0.0323

Document B:
  Vector rank: 5, Keyword rank: 1
  RRF = 1/(60+5) + 1/(60+1) ≈ 0.0154 + 0.0164 = 0.0318
```

Document A ranks higher despite worse keyword match because vector similarity is stronger.

### Tuning Parameters

**In server_config.yaml**:
```yaml
search:
  top_k: 5                    # Number of results
  fts_title_weight: 2.0       # Title keyword weight
  fts_content_weight: 1.0     # Content keyword weight
  rrf_k: 60                   # RRF parameter
```

**Effects**:
- `top_k`: Higher = more results, slower
- `fts_title_weight`: Higher = favor title matches
- `rrf_k`: Lower = more fusion, higher = preserve individual rankings

## Configuration System

### Variable Substitution

Configuration files support variable substitution:

```yaml
server:
  database_path: "${SERVER_ROOT}/runtime/mojo_manual_mcp.db"
```

**Available Variables**:
- `${PROJECT_ROOT}`: Repository root directory
- `${SERVER_ROOT}`: Server directory (e.g., `/servers/mojo-manual-mcp`)
- `${MCP_NAME}`: MCP name (e.g., `mojo`)

**Resolution**: Variables resolved at runtime by `shared/config_loader.py`

### Configuration Inheritance

1. **Default values** in templates
2. **Server-specific overrides** in `servers/{mcp}/config/`
3. **Environment variable overrides** (highest priority)

### Configuration Files

**processing_config.yaml**: Build-time configuration
- Source directory and format
- Chunking parameters
- Output directories

**server_config.yaml**: Runtime configuration
- Database paths
- Embedding server settings
- Search parameters

## Design Principles

### 1. Separation of Build and Runtime

**Build-time** (`/shared/`):
- Preprocessing pipeline
- Embedding generation
- Data consolidation
- Index creation

**Runtime** (`/servers/*/runtime/`):
- MCP server
- Search engine
- Indexed database

**Benefit**: Servers are self-contained

### 2. Config-Driven Architecture

**No hardcoded paths** in Python code. All paths via:
- YAML configuration files
- Environment variables
- Variable substitution

**Benefit**: Easy customization and deployment

### 3. Pluggable Processors

**ProcessorFactory pattern**:
```python
processor = ProcessorFactory.create_processor(
    format="mdx",  # or "markdown", "md"
    config=config
)
```

**Benefit**: Easy to add new documentation formats

### 4. Graceful Degradation

- If MAX unavailable → keyword-only search
- If FTS unavailable → vector-only search
- If database missing → clear error messages

**Benefit**: Robust operation in various environments

### 5. Reproducible Builds

- DuckLake versioning for data
- Locked dependencies (pixi.lock)
- Deterministic chunking

**Benefit**: Consistent results across environments

### 6. Distribution-First Design

Each server is:
- **Self-contained**: No external dependencies on `/shared/`
- **Documented**: README with setup instructions
- **Configured**: YAML configs included
- **Ready-to-run**: Pre-built databases included

**Benefit**: Easy to distribute and deploy

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Language** | Python 3.12+ | Core implementation |
| **MCP Framework** | FastMCP | Server protocol |
| **Database** | DuckDB | Vector + keyword search |
| **Vector Index** | HNSW (DuckDB VSS) | Approximate NN search |
| **Keyword Index** | FTS/BM25 (DuckDB) | Full-text search |
| **Versioning** | DuckLake | Data lake with versions |
| **Embeddings** | MAX | Local inference |
| **Model** | sentence-transformers | all-mpnet-base-v2 |
| **Packaging** | Pixi (optional) | Dependency management |

## Extension Points

### Adding New Documentation Formats

1. Create processor class inheriting from `BaseDocumentProcessor`
2. Implement `process_file()` method
3. Register in `ProcessorFactory`
4. Update config templates

### Custom Search Ranking

1. Extend `HybridSearcher` class
2. Override `_fusion_rankings()` method
3. Implement custom scoring algorithm

## Troubleshooting

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## Further Reading

- [QUICKSTART.md](QUICKSTART.md) - Get started quickly
- [CREATING_NEW_MCP.md](CREATING_NEW_MCP.md) - Create new servers

---
