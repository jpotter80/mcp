# Runtime Deployment

Detailed guide for deploying and running the MCP search server with the pre-built search database.

---

## Overview

The runtime requires three components:

1. **Embedding Server** — Generates query embeddings (MAX or OpenAI-compatible API)
2. **Search Engine** (`search.py`) — Performs hybrid search using DuckDB
3. **MCP Server** (`mcp_server/server.py`) — Exposes search via Model Context Protocol

```
Query from LLM Host
       ↓
MCP Server
       ↓
Embedding Server (cached)
       ↓
Search Engine (DuckDB)
       ↓
Results (chunk_id, title, snippet, url)
```

---

## Prerequisites

- Python 3.12+
- Pre-built `main.db` (DuckDB with indexes)
- Dependencies installed via Pixi
- Internet connection (first time only, for model download)

---

## Component 1: Embedding Server

The embedding server provides a local OpenAI-compatible API for generating query embeddings.

### Starting MAX Server

**Option 1: Using Pixi**

```bash
pixi run max-serve
```

**Option 2: Direct command**

```bash
max serve \
  --model sentence-transformers/all-mpnet-base-v2 \
  --host 0.0.0.0 \
  --port 8000
```

### Output

```
Downloading model: sentence-transformers/all-mpnet-base-v2...
Model loaded successfully.
Starting MAX embedding server...
Server running at http://0.0.0.0:8000/v1
Press Ctrl+C to stop.
```

### Verification

In another terminal:

```bash
curl http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "How do I declare a variable?",
    "model": "sentence-transformers/all-mpnet-base-v2"
  }' | jq .
```

Expected output: JSON with embedding (768-dimensional array)

### Environment Variables

Configure the server location and model:

```bash
export MAX_SERVER_URL=http://localhost:8000/v1
export EMBED_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `MAX_SERVER_URL` | `http://localhost:8000/v1` | Embedding server endpoint |
| `EMBED_MODEL_NAME` | `sentence-transformers/all-mpnet-base-v2` | Model to use |
| `EMBED_CACHE_SIZE` | `512` | Query embedding LRU cache size |

### Alternative Embedding Servers

Any OpenAI-compatible embeddings API works:

```bash
# Azure OpenAI
export MAX_SERVER_URL=https://<resource>.openai.azure.com/v1
export OPENAI_API_KEY=<key>

# Ollama (local models)
ollama pull all-minilm
export MAX_SERVER_URL=http://localhost:11434/api

# OpenAI (remote)
export MAX_SERVER_URL=https://api.openai.com/v1
export OPENAI_API_KEY=sk-...
```

---

## Component 2: Search Engine

The search engine (`search.py`) implements hybrid search using the DuckDB indexes.

### Direct Usage (CLI)

```bash
python search.py -q "How do I declare a variable?" -k 5
```

### Options

```bash
python search.py --help

Options:
  -q, --query TEXT              Search query
  -k, --top-k INTEGER           Number of results (default: 5)
  --fts-weight FLOAT            Weight for keyword search (0.0–1.0, default: 0.5)
  --vss-weight FLOAT            Weight for semantic search (0.0–1.0, default: 0.5)
  --db-path TEXT                Path to main.db (default: main.db)
  --table-name TEXT             Table name (default: mojo_docs_indexed)
```

### Example Queries

**Balanced search** (equal keyword + semantic):

```bash
python search.py -q "ownership and borrowing" -k 5
```

**Keyword-focused** (exact terms matter):

```bash
python search.py -q "fn keyword syntax" \
  --fts-weight 0.8 --vss-weight 0.2 -k 5
```

**Semantic-focused** (meaning matters):

```bash
python search.py -q "how do I manage memory?" \
  --fts-weight 0.2 --vss-weight 0.8 -k 5
```

### Output Format

```
╔════════════════════════════════════════════════════════════╗
║                    SEARCH RESULTS                           ║
╚════════════════════════════════════════════════════════════╝

Query: "How do I declare a variable?"
Top 5 Results:

1. 📄 variables-001
   Title: Variables and Types
   URL: https://docs.modular.com/mojo/manual/variables#declaring-variables
   Section: ["Mojo Language Basics", "Variables", "Declaration"]
   Snippet: "Variables in Mojo are declared using the `var` keyword. The syntax is..."
   Score: 0.94

2. 📄 basics-002
   Title: Mojo Language Basics
   URL: https://docs.modular.com/mojo/manual/basics#hello-world
   Section: ["Mojo Language Basics", "Hello World"]
   Snippet: "In this example, we declare and initialize a variable in one step..."
   Score: 0.87
   
[...]
```

---

## Component 3: MCP Server

The MCP server exposes the search engine via Model Context Protocol, making it accessible to LLM hosts.

### Starting the Server

**Option 1: MCP Inspector (interactive)**

```bash
pixi run mcp-dev
```

Opens the MCP Inspector UI at `http://localhost:3000`

**Option 2: Direct stdio**

```bash
python mcp_server/server.py
```

Communicates via stdin/stdout (for integrations)

**Option 3: VS Code MCP Host**

Configure in VS Code settings (see next section)

### Exposed Interface

#### Tool: `search`

```
Name: search
Description: "Hybrid search over documentation"

Parameters:
  - query (string, required): Search query
  - k (integer, optional, default=5): Number of results
  - fts_weight (number, optional, default=0.5): Keyword search weight
  - vss_weight (number, optional, default=0.5): Semantic search weight

Returns:
  List of SearchResult objects with:
    - chunk_id
    - title
    - url
    - section_hierarchy (array)
    - snippet
```

#### Resources

- **`mojo://search/{q}`** — Markdown formatted results for query `q`
  ```
  mojo://search/How%20do%20I%20declare%20a%20variable
  ```

- **`mojo://chunk/{chunk_id}`** — Full chunk content as Markdown
  ```
  mojo://chunk/variables-001
  ```

### Testing the Server

Using the MCP Inspector:

1. Start server: `pixi run mcp-dev`
2. Open browser: `http://localhost:3000`
3. Call tool `search` with query parameter
4. View results in UI

Using curl (if stdio available):

```bash
# Not directly supported; use MCP Inspector or SDK client
```

---

## Integration: VS Code MCP Host

Configure VS Code to use the MCP server as a content source.

### Setup Steps

1. **Install MCP extension** (if not present)
   - Open VS Code
   - Extensions → Search "MCP"
   - Install official MCP extension

2. **Update settings** (`settings.json`)

```json
{
  "mcp": {
    "servers": {
      "mojo-docs": {
        "command": "python",
        "args": ["/absolute/path/to/mcp_server/server.py"],
        "cwd": "/home/james/mcp",
        "env": {
          "MOJO_DB_PATH": "main.db",
          "MOJO_TABLE_NAME": "mojo_docs_indexed",
          "MAX_SERVER_URL": "http://localhost:8000/v1"
        }
      }
    }
  }
}
```

3. **Reload VS Code** — CMD+Shift+P → Reload Window

4. **Verify connection** — Check MCP panel for "mojo-docs" status

### Usage in VS Code

Once connected, you can:

- Access resources via @mojo://search/... in chat
- Call search tool from Copilot
- Reference chunks via @mojo://chunk/...

---

## Environment Variables

Configure runtime behavior via environment variables:

### Database

```bash
MOJO_DB_PATH=main.db              # Path to DuckDB file
MOJO_TABLE_NAME=mojo_docs_indexed  # Table name in database
```

### Embeddings

```bash
MAX_SERVER_URL=http://localhost:8000/v1           # Server endpoint
EMBED_MODEL_NAME=sentence-transformers/all-mpnet-base-v2  # Model name
EMBED_CACHE_SIZE=512                              # LRU cache size
```

### MCP Server

```bash
MCP_DEBUG=1          # Enable debug logging
LOG_LEVEL=INFO       # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Example `.env` File

```bash
# Database
MOJO_DB_PATH=./main.db
MOJO_TABLE_NAME=mojo_docs_indexed

# Embeddings
MAX_SERVER_URL=http://localhost:8000/v1
EMBED_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
EMBED_CACHE_SIZE=512

# MCP Server
MCP_DEBUG=0
LOG_LEVEL=INFO
```

Load with:

```bash
set -a
source .env
set +a
python mcp_server/server.py
```

---

## Troubleshooting

### Issue: "Connection refused" when contacting MAX server

**Cause**: Embedding server not running

**Solution**:
```bash
# Terminal 1: Start MAX server
pixi run max-serve

# Terminal 2: Run search or MCP server
python search.py -q "test"
```

### Issue: "main.db not found"

**Cause**: Search database missing or wrong path

**Solution**:
```bash
# Check file exists
ls -lh main.db

# Or specify path
MOJO_DB_PATH=/full/path/to/main.db python search.py -q "test"
```

### Issue: Empty search results

**Cause**: Database has no data or wrong table name

**Solution**:
```bash
# Check table exists
duckdb main.db "SELECT COUNT(*) FROM mojo_docs_indexed;"

# Verify table name
duckdb main.db ".tables"

# Correct environment variable if needed
export MOJO_TABLE_NAME=correct_table_name
```

### Issue: Slow queries (>1 second)

**Cause**: 
- HNSW index not being used
- Large number of results (high k)
- Embedding server slow

**Solution**:
```bash
# Verify HNSW index exists
duckdb main.db ".indexes"

# Try lower k value
python search.py -q "test" -k 3

# Check MAX server performance
time curl http://localhost:8000/v1/embeddings ... | jq .

# Reduce embedding cache if RAM constrained
export EMBED_CACHE_SIZE=128
```

### Issue: MCP server crashes on startup

**Cause**: Configuration error or database corruption

**Solution**:
```bash
# Check config
echo $MOJO_DB_PATH
echo $MAX_SERVER_URL

# Verify database integrity
duckdb main.db "PRAGMA database_list;"

# Try with debug logging
MCP_DEBUG=1 python mcp_server/server.py
```

---

## Performance Tuning

### Query Speed Optimization

1. **Reduce k if high**
   ```bash
   # Fast: k=3
   python search.py -q "query" -k 3
   
   # Slow: k=50
   python search.py -q "query" -k 50
   ```

2. **Use appropriate weight balance**
   - FTS-only: Fastest (10–50ms)
   - VSS-only: Medium (100–200ms)
   - Hybrid (RRF): Medium (100–200ms)

3. **Cache query embeddings**
   - Default: 512 queries cached
   - Already optimized for typical usage

### Embedding Server Performance

1. **GPU acceleration** (if available)
   ```bash
   # MAX uses GPU if detected
   # Verify: Look for CUDA/GPU info in startup logs
   ```

2. **Model selection**
   - `all-mpnet-base-v2`: 768-dim, high quality (slower)
   - `all-MiniLM-L6-v2`: 384-dim, faster
   - Ensure model matches index dimensions!

### Database Performance

1. **HNSW index quality**
   - Automatically optimized during creation
   - Cannot be tuned at runtime

2. **Connection pooling**
   - Currently single-threaded
   - Sufficient for interactive queries

---

## Monitoring & Logging

### Enable Debug Logging

```bash
MCP_DEBUG=1 python mcp_server/server.py
```

Output:
```
[DEBUG] MCP Server started
[DEBUG] Connected to main.db
[DEBUG] HNSW index found on embedding column
[DEBUG] Query: "test query"
[DEBUG] Vector search: 23 results in 87ms
[DEBUG] FTS search: 45 results in 12ms
[DEBUG] RRF fusion: 5 results after fusion
```

### Check Index Statistics

```bash
duckdb main.db <<EOF
-- Vector index stats
SELECT COUNT(*) as total_chunks FROM mojo_docs_indexed;

-- Check index exists
SELECT * FROM duckdb_indexes();

-- Sample query time
EXPLAIN SELECT * FROM mojo_docs_indexed 
  ORDER BY array_cosine_distance(embedding, CAST([0.1, ...] AS FLOAT[768])) 
  LIMIT 5;
EOF
```

---

## Next Steps

- **Update data** — Rebuild `main.db` via [PREPROCESSING.md](PREPROCESSING.md) and [DEVELOPMENT.md](DEVELOPMENT.md)
- **Deploy to cloud** — Use DuckDB HTTP proxy or deploy MCP server to cloud
- **Extend capabilities** — Add new tools/resources in `mcp_server/server.py`
- **Monitor usage** — Add request logging and analytics

