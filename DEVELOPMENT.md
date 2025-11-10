# Development & Task Reference

Complete guide to development workflows, tasks, testing, and troubleshooting for the Documentation-to-MCP pipeline.

---

## Overview

This document covers:
- Running the full pipeline locally
- Task reference (pixi commands)
- Testing and validation
- Debugging common issues
- Performance optimization

---

## Full Pipeline Execution

### One-Command Build (Complete Pipeline)

Build everything from documentation source to indexed search database:

```bash
pixi run process && \
pixi run generate-embeddings && \
pixi run consolidate && \
pixi run load && \
pixi run index
```

**Expected time**: ~15 minutes
**Outputs**: `main.db` (indexed search database) + artifacts in `processed_docs/`

### Step-by-Step Execution

Execute each phase individually to inspect outputs:

```bash
# Step 1: Preprocess (1–2 min)
pixi run process
# Output: processed_docs/chunks/, metadata/, raw/

# Step 2: Generate embeddings (5–10 min)
# REQUIRES: MAX server running (pixi run max-serve in another terminal)
pixi run generate-embeddings
# Output: processed_docs/embeddings/

# Step 3: Consolidate data (<1 min)
pixi run consolidate
# Output: processed_docs/{project}_embeddings.parquet

# Step 4: Load to DuckLake (<1 min)
pixi run load
# Output: {project}_catalog.ducklake/ (versioned table)

# Step 5: Create indexes (1–2 min)
pixi run index
# Output: main.db (indexed DuckDB)
```

### Parallel Setup (Two Terminals)

For fastest results, run MAX server while preprocessing:

**Terminal 1** (background embedding server):
```bash
pixi run max-serve
```

**Terminal 2** (preprocessing pipeline):
```bash
pixi run process
# Wait for completion...
pixi run generate-embeddings
pixi run consolidate && pixi run load && pixi run index
```

**Total time**: ~12–15 minutes (vs. 15–20 sequential)

---

## Task Reference

Complete list of available Pixi tasks. Check `pixi.toml` for full definitions.

### Build Pipeline Tasks

| Task | Purpose | Time | Prerequisites |
|------|---------|------|---------------|
| `pixi run process` | Preprocess MDX/MD → chunks | 1–2 min | Markdown files in `manual/` |
| `pixi run generate-embeddings` | Chunks → vectors | 5–10 min | MAX server running, chunks generated |
| `pixi run consolidate` | Merge chunks + embeddings → Parquet | <1 min | Embeddings generated |
| `pixi run load` | Parquet → DuckLake | <1 min | Consolidation complete |
| `pixi run index` | DuckLake → indexed DuckDB | 1–2 min | Data loaded |

### Runtime Tasks

| Task | Purpose | Notes |
|------|---------|-------|
| `pixi run max-serve` | Start local embedding server | Runs on `localhost:8000` |
| `pixi run search` | CLI hybrid search tool | Usage: `pixi run search -- -q "query" -k 5` |
| `pixi run mcp-dev` | MCP Inspector (interactive UI) | Opens browser at `http://localhost:3000` |

### Utility Tasks

| Task | Purpose | Output |
|------|---------|--------|
| `pixi run validate` | Validate preprocessing output | Detailed validation report |
| `pixi run stats` | Show processing statistics | Token distribution, chunk counts |
| `pixi run clean` | Remove `processed_docs/` | Clean slate for reprocessing |

### Full Task List

View all available tasks:

```bash
pixi task list
```

---

## Testing & Validation

### 1. Validate Preprocessing Output

```bash
pixi run validate
```

**Output**:
```
============================================================
📈 Validation Report
============================================================

✅ FILE DISCOVERY
   Total files found: 25
   Status: PASS

✅ CONTENT PRESERVATION
   Original vs. reconstructed tokens: 184230 vs 184230
   Status: PASS

✅ CHUNK SIZE CONSTRAINTS
   Chunks within ±25% of target: 456/487 (93.6%)
   Status: PASS

✅ METADATA COMPLETENESS
   Missing fields: 0
   Status: PASS

✅ CODE BLOCK INTEGRITY
   Preserved: 156/156
   Status: PASS

Summary: ALL CHECKS PASSED ✅
```

### 2. Check Statistics

```bash
pixi run stats
```

**Output**:
```
============================================================
📈 Processing Statistics
============================================================

Documents: 25
Chunks: 487
Total tokens: 184,230
Average tokens per chunk: 378.23

Chunk Size Distribution:
  Min: 102 tokens
  25th percentile: 345 tokens
  Median: 387 tokens
  75th percentile: 410 tokens
  Max: 498 tokens

Chunks with code: 156 (32.0%)
Average processing time per doc: 3.5 seconds

============================================================
```

### 3. Test Search Functionality

**Single search**:

```bash
python search.py -q "How do I declare a variable?" -k 5
```

**Test with different weight distributions**:

```bash
# Keyword-focused
python search.py -q "fn syntax" --fts-weight 0.8 --vss-weight 0.2 -k 5

# Semantic-focused
python search.py -q "how to define a function" --fts-weight 0.2 --vss-weight 0.8 -k 5
```

**Batch test** (multiple queries):

```bash
cat <<EOF | while read q; do
  echo "Query: $q"
  python search.py -q "$q" -k 3
  echo "---"
done
How do I declare a variable?
What is ownership?
How do I write a function?
EOF
```

### 4. Inspect Database

```bash
# Check table exists and has data
duckdb main.db "SELECT COUNT(*) FROM mojo_docs_indexed;"

# List all indexes
duckdb main.db ".indexes"

# Sample a few chunks
duckdb main.db "SELECT chunk_id, title, token_count FROM mojo_docs_indexed LIMIT 5;"

# Check HNSW index
duckdb main.db "SELECT * FROM duckdb_indexes() WHERE index_name LIKE '%vss%';"

# Verify schema
duckdb main.db ".schema mojo_docs_indexed"
```

### 5. Test MCP Server

**Start server**:

```bash
pixi run mcp-dev
```

**In MCP Inspector UI**:
1. Navigate to `http://localhost:3000`
2. Find "search" tool
3. Enter query parameter
4. Verify results are returned

---

## Debugging Common Issues

### Issue: "No files found to process"

**Diagnosis**:
```bash
# Check source directory
ls -la manual/

# Check config
grep "directory:" preprocessing/config/processing_config.yaml

# Count matching files
find manual -name "*.mdx" -o -name "*.md" | wc -l
```

**Solution**:
```bash
# Update config
nano preprocessing/config/processing_config.yaml
# Set correct directory path

# Verify
ls -la <directory>/
```

### Issue: Preprocessing hangs or runs slowly

**Diagnosis**:
```bash
# Check RAM usage
watch free -h

# Check disk space
df -h .

# Monitor process
top -p $(pgrep -f preprocessing)
```

**Solution**:
```bash
# Exclude large directories
nano preprocessing/config/processing_config.yaml
# Add to exclude_patterns:
# - "images/**"
# - "*.backup.mdx"

# Or process subset
find manual -name "basics.mdx" > /tmp/subset.txt
# Manually edit pipeline to process subset
```

### Issue: Embedding generation fails

**Cause**: MAX server not running

**Diagnosis**:
```bash
# Try to reach MAX server
curl http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "test", "model": "sentence-transformers/all-mpnet-base-v2"}'
```

**Solution**:
```bash
# Start MAX server in new terminal
pixi run max-serve

# Wait for server to start
sleep 5

# Retry embedding generation
pixi run generate-embeddings
```

### Issue: "Connection refused" in search

**Cause**: Database path or table name wrong

**Diagnosis**:
```bash
# Check database exists
ls -lh main.db

# Check table exists
duckdb main.db ".tables"

# Check environment
echo $MOJO_DB_PATH
echo $MOJO_TABLE_NAME
```

**Solution**:
```bash
# Set correct environment
export MOJO_DB_PATH=./main.db
export MOJO_TABLE_NAME=mojo_docs_indexed

# Retry search
python search.py -q "test"
```

### Issue: Empty search results

**Diagnosis**:
```bash
# Check row count
duckdb main.db "SELECT COUNT(*) FROM mojo_docs_indexed;"

# Check HNSW index exists
duckdb main.db "SELECT * FROM duckdb_indexes() WHERE index_name LIKE 'idx%';"

# Check sample data
duckdb main.db "SELECT chunk_id, title FROM mojo_docs_indexed LIMIT 3;"
```

**Solution**:
```bash
# If empty, rebuild indexes
pixi run clean
pixi run process && pixi run generate-embeddings && \
  pixi run consolidate && pixi run load && pixi run index

# If HNSW missing, recreate indexes
python -c "
import duckdb
db = duckdb.connect('main.db')
# Recreate indexes (see create_indexes.py)
"
```

### Issue: Slow queries (>1 sec)

**Diagnosis**:
```bash
# Check query plan
duckdb main.db "EXPLAIN SELECT * FROM mojo_docs_indexed 
  ORDER BY array_cosine_distance(embedding, CAST([0.1] AS FLOAT[768])) 
  LIMIT 5;"

# Time a search
time python search.py -q "test" -k 5
```

**Solution** (if HNSW not being used):
```bash
# Recreate index with cosine metric
duckdb main.db "CREATE INDEX idx_embedding ON mojo_docs_indexed 
  USING HNSW (embedding) WITH (metric = 'cosine');"

# Verify
duckdb main.db "SELECT * FROM duckdb_indexes();"

# Retry search
time python search.py -q "test" -k 5
```

---

## Configuration Tuning

### Adjust Chunk Size

For different document types:

```yaml
# Fast documentation (tutorials, guides)
chunking:
  chunk_size: 300
  chunk_overlap: 60

# Dense documentation (technical specs)
chunking:
  chunk_size: 500
  chunk_overlap: 100

# Code-heavy documentation
chunking:
  chunk_size: 400
  chunk_overlap: 80
  preserve_code_blocks: true
```

### Tune Search Weights

Default balanced search:

```bash
python search.py -q "query" -k 5  # fts_weight=0.5, vss_weight=0.5
```

For different query types:

```bash
# Exact term matches (e.g., "fn keyword syntax")
python search.py -q "fn keyword syntax" \
  --fts-weight 0.8 --vss-weight 0.2 -k 5

# Semantic queries (e.g., "how to define a function")
python search.py -q "how to define a function" \
  --fts-weight 0.2 --vss-weight 0.8 -k 5

# API documentation
python search.py -q "ModuleType" \
  --fts-weight 0.7 --vss-weight 0.3 -k 5
```

### Configure Embedding Cache

```bash
# Larger cache for long sessions
export EMBED_CACHE_SIZE=1024
python search.py -q "query1" -k 5
python search.py -q "query2" -k 5  # Fast (cached)

# Smaller cache if RAM constrained
export EMBED_CACHE_SIZE=128
python search.py -q "query" -k 5
```

---

## Performance Profiling

### Benchmark Search Speed

```bash
# Generate 100 random queries
python -c "
import random
queries = ['variable', 'function', 'ownership', 'struct', 'trait'] * 20
for q in queries:
    print(q)
" > /tmp/queries.txt

# Run benchmark
time while read q; do
  python search.py -q "$q" -k 3 > /dev/null
done < /tmp/queries.txt
```

### Profile Embedding Generation

```bash
# Time embedding generation for 100 queries
import time
from search import HybridSearcher

searcher = HybridSearcher()
queries = ["test"] * 100

start = time.time()
for q in queries:
    _ = searcher._get_query_embedding(q)
elapsed = time.time() - start

print(f"Generated {len(queries)} embeddings in {elapsed:.2f}s")
print(f"Average: {elapsed/len(queries)*1000:.1f}ms per embedding")
```

### Memory Usage

```bash
# Monitor memory during search
mprof run search.py -q "test" -k 10
mprof plot mprofile_*.dat
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Documentation Index

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Pixi
        uses: prefix-dev/setup-pixi@v0.8.0
      
      - name: Preprocess
        run: pixi run process
      
      - name: Validate
        run: pixi run validate
      
      - name: Generate embeddings (MAX)
        run: |
          pixi run max-serve &
          sleep 10
          pixi run generate-embeddings
      
      - name: Consolidate
        run: pixi run consolidate && pixi run load && pixi run index
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: main.db
          path: main.db
```

---

## Development Workflow

### Typical Day-to-Day

```bash
# 1. Make changes (to preprocessing config, etc.)
nano preprocessing/config/processing_config.yaml

# 2. Test on small subset
pixi run process  # Only processes configured directory

# 3. Inspect output
head processed_docs/chunks/*.jsonl | jq .

# 4. If good, continue pipeline
pixi run generate-embeddings
pixi run consolidate && pixi run load && pixi run index

# 5. Test search
python search.py -q "test query" -k 5

# 6. Deploy (push to repo or build system)
git add main.db
git commit -m "Update search database"
git push
```

### Adding New Features

1. **New preprocessing step**:
   - Add to `preprocessing/src/pipeline.py`
   - Update configuration in `processing_config.yaml`
   - Test with `pixi run process`

2. **New MCP tool/resource**:
   - Add to `mcp_server/server.py`
   - Test with `pixi run mcp-dev`
   - Update documentation

3. **New search strategy**:
   - Implement in `search.py` (HybridSearcher class)
   - Add CLI flags
   - Test with `python search.py --help`

---

## Next Steps

- **Improve chunking**: See [PREPROCESSING.md](PREPROCESSING.md#Phase-2-Chunking-Strategy)
- **Deploy runtime**: See [RUNTIME.md](RUNTIME.md)
- **Extend capabilities**: Add custom preprocessing, new MCP tools
- **Scale up**: Handle multiple documentation sources simultaneously

