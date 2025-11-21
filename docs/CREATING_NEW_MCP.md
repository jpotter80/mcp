# Creating New MCP Servers

Step-by-step guide for developers to create new MCP servers for different documentation sources.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Using the Scaffold Tool](#using-the-scaffold-tool)
- [Manual Setup](#manual-setup)
- [Adding Documentation](#adding-documentation)
- [Configuration](#configuration)
- [Building the Server](#building-the-server)
- [Testing](#testing)
- [Distribution](#distribution)
- [Example: Creating a Python Docs Server](#example-creating-a-python-docs-server)

## Overview

The framework makes it easy to create new MCP servers for any documentation source. Each server is self-contained and can be distributed independently.

### What You'll Create

```
servers/your-docs-mcp/
├── runtime/                    # Distributable server code
│   ├── your_docs_mcp_server.py
│   ├── search.py
│   └── your_docs_mcp.db        # Built by pipeline
├── config/                     # Configuration
│   ├── processing_config.yaml
│   └── server_config.yaml
├── requirements.txt            # Dependencies
└── README.md                   # Server documentation
```

### Architecture Reminder

- **Build-time** (`/shared/`): Processing pipeline (dev only, not distributed)
- **Runtime** (`/servers/*/runtime/`): MCP server + database (distributed)
- **Source** (`/source-documentation/`): Raw documentation (dev only)

## Prerequisites

- **Development environment** setup complete (see [SETUP_PIXI.md](SETUP_PIXI.md) or [SETUP_VENV.md](SETUP_VENV.md))
- **Understanding of MCP** (see [modelcontextprotocol.io](https://modelcontextprotocol.io))
- **Documentation source** to index (Markdown, MDX, or other supported formats)

## Using the Scaffold Tool

The easiest way to create a new server is using the scaffold script.

### Basic Usage

```bash
./tools/scaffold_new_mcp.sh \
  --name <tool-name> \
  --doc-type <doc-type> \
  --format <format>
```

**Parameters**:
- `--name`: Tool/project name (e.g., `python`, `duckdb`, `vscode`)
- `--doc-type`: Documentation type (e.g., `docs`, `manual`, `api`, `guide`)
- `--format`: Source format (`mdx`, `markdown`, `rst`)

### Example: Create DuckDB Docs Server

```bash
./tools/scaffold_new_mcp.sh \
  --name duckdb \
  --doc-type docs \
  --format markdown
```

**What it creates**:
```
servers/duckdb-docs-mcp/
├── runtime/
│   ├── duckdb_docs_mcp_server.py   # MCP server entry point
│   ├── search.py                    # Hybrid search implementation
│   └── README.md                    # Runtime documentation
├── config/
│   ├── processing_config.yaml       # Build configuration
│   └── server_config.yaml           # Server configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # Server overview
```

**Next steps after scaffolding**:
1. Add documentation to `source-documentation/duckdb/docs/`
2. Review and customize configuration files
3. Build the server database
4. Test the server

### Scaffold Tool Options

```bash
./tools/scaffold_new_mcp.sh --help
```

**Options**:
- `--name <name>`: Tool name (required)
- `--doc-type <type>`: Documentation type (required)
- `--format <fmt>`: Source format (required: mdx, markdown, rst)
- `--help`: Show help message

## Manual Setup

If you prefer manual setup or need customization:

### Step 1: Create Directory Structure

```bash
mkdir -p servers/mytool-docs-mcp/{runtime,config}
mkdir -p source-documentation/mytool/docs
```

### Step 2: Copy Templates

```bash
# Copy runtime templates
cp shared/templates/search_template.py \
   servers/mytool-docs-mcp/runtime/search.py

cp shared/templates/mcp_server_template.py \
   servers/mytool-docs-mcp/runtime/mytool_docs_mcp_server.py

# Copy config templates
cp shared/templates/processing_config_template.yaml \
   servers/mytool-docs-mcp/config/processing_config.yaml

cp shared/templates/server_config_template.yaml \
   servers/mytool-docs-mcp/config/server_config.yaml

# Copy requirements
cp shared/templates/requirements_template.txt \
   servers/mytool-docs-mcp/requirements.txt

# Copy README
cp shared/templates/README_template.md \
   servers/mytool-docs-mcp/README.md
```

### Step 3: Replace Placeholders

Edit each file and replace placeholders:

- `{{TOOL_NAME}}` → `mytool`
- `{{DOC_TYPE}}` → `docs`
- `{{MCP_NAME}}` → `mytool-docs-mcp`
- `{{MCP_NAME_UPPER}}` → `MYTOOL_DOCS_MCP`
- `{{MCP_NAME_SNAKE}}` → `mytool_docs_mcp`
- `{{FORMAT}}` → `markdown` (or `mdx`, `rst`)

**Tip**: Use search and replace in your editor for consistency.

## Adding Documentation

### Option 1: Sync from Git Repository

Use the sync script to clone/update from upstream:

```bash
./tools/sync_documentation.sh \
  --source owner/repo \
  --dest source-documentation/mytool/docs \
  --sparse-path path/to/docs
```

**Example**: Sync Python docs
```bash
./tools/sync_documentation.sh \
  --source python/cpython \
  --dest source-documentation/python/docs \
  --sparse-path Doc
```

### Option 2: Manual Copy

Copy documentation files manually:

```bash
cp -r /path/to/docs/* source-documentation/mytool/docs/
```

### Supported Formats

#### Markdown (.md)
- Standard Markdown
- GitHub Flavored Markdown (GFM)
- CommonMark

**Processor**: `MarkdownProcessor` (built-in)

#### MDX (.mdx)
- Markdown with JSX components
- Frontmatter support
- Code blocks preserved

**Processor**: `MDXProcessor` (built-in)

#### reStructuredText (.rst)
- Python documentation standard
- Sphinx-compatible

**Processor**: Needs implementation (see [Contributing](#contributing))

### Documentation Structure Best Practices

Good documentation structure:
```
source-documentation/mytool/docs/
├── index.md                # Overview
├── getting-started/        # Tutorials
│   ├── installation.md
│   └── quickstart.md
├── guides/                 # How-to guides
│   ├── basics.md
│   └── advanced.md
├── reference/              # API reference
│   ├── functions.md
│   └── classes.md
└── examples/               # Code examples
    └── ...
```

**Why this matters**:
- Clear section hierarchy for better chunk organization
- Logical navigation structure
- Better search result context

## Configuration

### Processing Configuration

Edit `servers/mytool-docs-mcp/config/processing_config.yaml`:

```yaml
source:
  directory: "${PROJECT_ROOT}/source-documentation/mytool/docs"
  format: "markdown"          # or "mdx", "rst"
  file_patterns:
    - "*.md"
    - "*.markdown"

output:
  base_directory: "${PROJECT_ROOT}/shared/build/processed_docs/mytool"
  raw_dir: "raw"
  metadata_dir: "metadata"
  chunks_dir: "chunks"

chunking:
  chunk_size: 256             # Tokens per chunk
  chunk_overlap: 50           # Overlap between chunks
  min_chunk_size: 50          # Minimum chunk size
  preserve_code_blocks: true  # Keep code blocks intact
  
  # Tokenizer settings
  tokenizer_model: "sentence-transformers/all-mpnet-base-v2"
  target_chunk_tokens: 350    # Target size
  max_chunk_tokens: 400       # Maximum size
  overlap_tokens: 50          # Overlap size

processing:
  skip_validation: false      # Validate chunks after processing
  log_level: "INFO"           # Logging verbosity
```

**Key parameters**:
- `chunk_size`: Affects granularity (smaller = more precise, larger = more context)
- `chunk_overlap`: Prevents information loss at boundaries
- `preserve_code_blocks`: Important for technical documentation

### Server Configuration

Edit `servers/mytool-docs-mcp/config/server_config.yaml`:

```yaml
server:
  name: "mytool-docs"
  database_path: "${SERVER_ROOT}/runtime/mytool_docs_mcp.db"
  table_name: "mytool_docs_indexed"
  ducklake_catalog: "${SERVER_ROOT}/runtime/mytool_docs_catalog.ducklake"

embedding:
  max_server_url: "http://localhost:8000/v1"
  model_name: "sentence-transformers/all-mpnet-base-v2"
  cache_size: 512             # Query embedding cache size
  
search:
  top_k: 5                    # Number of results
  fts_title_weight: 2.0       # Keyword: title weight
  fts_content_weight: 1.0     # Keyword: content weight
  rrf_k: 60                   # RRF fusion parameter
```

**Tuning guidelines**:
- `top_k`: Start with 5, increase for broader coverage
- `fts_title_weight`: Higher = favor title matches
- `rrf_k`: Lower = more fusion between vector/keyword

## Building the Server

### Using the Build Script

```bash
./tools/build_mcp.sh --mcp-name mytool
```

This runs the full pipeline:
1. Process documentation → chunks
2. Generate embeddings → vectors
3. Consolidate → Parquet dataset
4. Load → DuckLake versioning
5. Create indexes → Final database

### Step-by-Step Build (Manual)

If you need more control:

#### 1. Process Documentation

```bash
pixi run python -m shared.preprocessing.src.pipeline --mcp-name mytool
# or without pixi:
python -m shared.preprocessing.src.pipeline --mcp-name mytool
```

**Output**: `shared/build/processed_docs/mytool/chunks/*.jsonl`

#### 2. Generate Embeddings

Ensure MAX server is running:
```bash
pixi run max-serve  # or: max serve --model sentence-transformers/all-mpnet-base-v2
```

Generate embeddings:
```bash
pixi run python shared/embedding/generate_embeddings.py --mcp-name mytool
```

**Output**: `shared/build/embeddings/mytool/*_embeddings.jsonl`

#### 3. Consolidate Data

```bash
pixi run python shared/embedding/consolidate_data.py --mcp-name mytool
```

**Output**: `shared/build/mytool_embeddings.parquet`

#### 4. Load to DuckLake

```bash
pixi run python shared/embedding/load_to_ducklake.py --mcp-name mytool
```

**Output**: `servers/mytool-docs-mcp/runtime/mytool_docs_catalog.ducklake`

#### 5. Create Indexes

```bash
pixi run python shared/embedding/create_indexes.py --mcp-name mytool
```

**Output**: `servers/mytool-docs-mcp/runtime/mytool_docs_mcp.db`

### Verify the Build

```bash
# Check database exists and has reasonable size
ls -lh servers/mytool-docs-mcp/runtime/mytool_docs_mcp.db

# Expected: 50-200MB depending on documentation size

# Test search
cd servers/mytool-docs-mcp/runtime
python search.py -q "test query" -k 3
```

## Testing

### Test Locally with CLI

```bash
cd servers/mytool-docs-mcp/runtime
python search.py -q "your search query" -k 5
```

Expected output:
- Search results with titles
- Snippets with highlighted terms
- URLs to original documentation
- Relevance scores

### Test with MCP Inspector

```bash
# Start MAX server
pixi run max-serve

# In another terminal, start MCP Inspector
python servers/mytool-docs-mcp/runtime/mytool_docs_mcp_server.py
```

The MCP Inspector should show:
- Tool: `search`
- Resources: `mytool://search/*`, `mytool://chunk/*`

Test a search query in the inspector interface.

### Test in VS Code

Add to VS Code settings:

```json
{
  "servers": {
    "mytool-docs": {
      "command": "python",
      "args": [
        "/absolute/path/to/servers/mytool-docs-mcp/runtime/mytool_docs_mcp_server.py"
      ],
      "env": {
        "MYTOOL_DB_PATH": "/absolute/path/to/servers/mytool-docs-mcp/runtime/mytool_docs_mcp.db",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

Reload VS Code and test:
```
@mytool-docs search for [topic]
```

### Automated Testing

Create a test script `servers/mytool-docs-mcp/test_server.py`:

```python
import subprocess
import json

def test_search():
    # Start server process
    proc = subprocess.Popen(
        ["python", "runtime/mytool_docs_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    
    # Send test query (MCP protocol)
    # ...
    
    # Verify results
    assert results is not None
    assert len(results) > 0

if __name__ == "__main__":
    test_search()
    print("✅ All tests passed")
```
## Example: Creating a Python Docs Server

Let's create a complete example for Python documentation.

### 1. Scaffold the Server

```bash
./tools/scaffold_new_mcp.sh \
  --name python \
  --doc-type stdlib \
  --format rst
```

### 2. Sync Documentation

```bash
./tools/sync_documentation.sh \
  --source python/cpython \
  --dest source-documentation/python/stdlib \
  --sparse-path Doc/library
```

### 3. Customize Configuration

Edit `servers/python-stdlib-mcp/config/processing_config.yaml`:

```yaml
source:
  directory: "${PROJECT_ROOT}/source-documentation/python/stdlib"
  format: "rst"               # reStructuredText
  file_patterns:
    - "*.rst"

chunking:
  chunk_size: 300             # Python docs are dense
  chunk_overlap: 60           # More overlap for API docs
  preserve_code_blocks: true
```

Edit `servers/python-stdlib-mcp/config/server_config.yaml`:

```yaml
search:
  top_k: 7                    # More results for API reference
  fts_title_weight: 3.0       # Function/class names are important
```

### 4. Build the Server

```bash
./tools/build_mcp.sh --mcp-name python
```

### 5. Test

```bash
cd servers/python-stdlib-mcp/runtime
python search.py -q "How to use pathlib?" -k 5
```

### 6. Configure in VS Code mcp.json

```json
{
  "servers": {
    "python-stdlib": {
      "command": "python",
      "args": [
        "/path/to/servers/python-stdlib-mcp/runtime/python_stdlib_mcp_server.py"
      ],
      "env": {
        "PYTHON_DB_PATH": "/path/to/servers/python-stdlib-mcp/runtime/python_stdlib_mcp.db",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

### 7. Use in VS Code

```
@python-stdlib how do I use pathlib?
```

Copilot now has access to Python standard library documentation!

## Troubleshooting

### Scaffold script fails

**Cause**: Missing execute permission

**Solution**:
```bash
chmod +x tools/scaffold_new_mcp.sh
./tools/scaffold_new_mcp.sh --help
```

### Build fails on processing step

**Cause**: Unsupported format or malformed source files

**Solution**:
- Check `format` in processing_config.yaml matches files
- Verify file_patterns include correct extensions
- Check preprocessing logs in `shared/build/logs/`

### Embeddings generation fails

**Cause**: MAX server not running or not accessible

**Solution**:
```bash
# Start MAX server
pixi run max-serve

# Test MAX is accessible
curl http://localhost:8000/v1/models
```

### Search returns no results

**Cause**: Database empty or index not created

**Solution**:
```bash
# Verify database size
ls -lh servers/*/runtime/*.db

# If empty, rebuild
./tools/build_mcp.sh --mcp-name your-tool
```

## Best Practices

### Documentation Source

- **Keep sources updated**: Use `sync_documentation.sh` regularly
- **Version control**: Tag documentation versions in DuckLake
- **Test coverage**: Ensure all major topics are covered

### Configuration

- **Start with defaults**: Use templates as-is first
- **Tune incrementally**: Adjust one parameter at a time
- **Document changes**: Explain why you changed defaults

### Building

- **Automate rebuilds**: Set up CI/CD for doc updates
- **Version databases**: Keep old databases for rollback
- **Monitor quality**: Check search results regularly

### Distribution

- **Include databases**: Pre-built for easy use
- **Document clearly**: README with setup instructions
- **Test on clean env**: Verify fresh installation works
- **Provide examples**: Show common queries

## Next Steps

- **Understand architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Advanced features**: Add custom processors or search ranking

## Additional Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [DuckDB Documentation](https://duckdb.org/docs)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Templates README](../shared/templates/README.md)
- [Tools README](../tools/README.md)

---
