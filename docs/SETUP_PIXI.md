# Complete Setup Guide with Pixi

Comprehensive guide for setting up the MCP documentation search framework using pixi for dependency management.

## Table of Contents

- [Why Pixi?](#why-pixi)
- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Running the Pre-Built Server](#running-the-pre-built-server)
- [Rebuilding from Source](#rebuilding-from-source)
- [Understanding the Build Pipeline](#understanding-the-build-pipeline)
- [Updating Documentation](#updating-documentation)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)

## Why Pixi?

Pixi is a modern package manager for Python that offers several advantages:

- **Fast**: Uses conda-forge for pre-compiled packages
- **Reproducible**: Lock file ensures consistent environments
- **Task Management**: Built-in task runner (like make, but better)
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **No Conflicts**: Isolated environments prevent dependency issues

If you prefer traditional Python venv, see [SETUP_VENV.md](SETUP_VENV.md).

## Installation

### Install Pixi

**macOS/Linux**:
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

**Windows**:
```powershell
iwr -useb https://pixi.sh/install.ps1 | iex
```

**Alternative**: Download from [prefix.dev/docs/pixi/overview](https://prefix.dev/docs/pixi/overview)

Verify installation:
```bash
pixi --version
```

### Install Git (if not already installed)

**macOS**: Comes pre-installed or install via Homebrew: `brew install git`  
**Linux**: `sudo apt-get install git` (Ubuntu/Debian) or `sudo yum install git` (RHEL/CentOS)  
**Windows**: Download from [git-scm.com](https://git-scm.com/)

## Initial Setup

### Clone the Repository

```bash
git clone <your-repo-url>
cd mcp
```

### Install Dependencies

Pixi reads `pixi.toml` and installs all dependencies automatically:

```bash
pixi install
```

This creates an isolated environment with all required packages including:
- Python 3.10+
- DuckDB with VSS extension
- Sentence transformers
- FastMCP
- All other dependencies

**Time**: 2-5 minutes (depending on internet speed)

### Verify Installation

```bash
pixi run python --version
pixi list
```

You should see Python 3.10+ and a list of installed packages.

## Running the Pre-Built Server

The repository includes pre-built databases, so you can run the server immediately without rebuilding.

### Start MAX Embedding Server

In one terminal:
```bash
pixi run max-serve
```

This starts the MAX server at `http://localhost:8000` with the sentence-transformers model. Leave this running.

### Test with MCP Inspector

In another terminal:
```bash
pixi run mcp-dev
```

This opens the MCP Inspector in your browser where you can:
- View available tools: `search`
- View available resources: `mojo://search/*`, `mojo://chunk/*`
- Test queries interactively

### Test with CLI Search

```bash
pixi run search -- -q "How do I declare a variable?" -k 5
```

You should see search results with snippets from the Mojo documentation.

### Configure for VS Code

1. Get your absolute path:
```bash
cd mcp && pwd
```

2. Add to VS Code settings (`.vscode/settings.json` or user settings):
```json
{
  "mcpServers": {
    "mojo-docs": {
      "command": "python",
      "args": [
        "/your/absolute/path/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"
      ],
      "env": {
        "MOJO_DB_PATH": "/your/absolute/path/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db",
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

3. Restart VS Code or reload window

4. Test by asking Copilot: "What is ownership in Mojo?"

## Rebuilding from Source

If you want to rebuild the database from scratch or have updated documentation:

### Full Pipeline (All Steps)

```bash
pixi run mojo-build
```

This runs all 5 steps in sequence (takes ~10-15 minutes):
1. Process documentation
2. Generate embeddings
3. Consolidate data
4. Load to DuckLake
5. Create indexes

### Step-by-Step Pipeline

For more control, run each step individually:

#### Step 1: Process Documentation

```bash
pixi run mojo-process
```

**What it does**:
- Reads MDX files from `source-documentation/mojo/manual/`
- Cleans frontmatter, JSX, code blocks
- Chunks into ~350-400 tokens with 50-80 token overlap
- Outputs to `shared/build/processed_docs/mojo/chunks/`

**Time**: 1-2 minutes  
**Output**: ~1155 chunks from ~45 documents

#### Step 2: Generate Embeddings

```bash
pixi run mojo-generate-embeddings
```

**What it does**:
- Reads chunks from previous step
- Generates 768-dimensional vectors via MAX server
- Outputs to `shared/build/embeddings/mojo/`

**Time**: 5-10 minutes (depends on MAX server performance)  
**Output**: Embeddings for all chunks in JSONL format

**Note**: MAX server must be running (`pixi run max-serve`)

#### Step 3: Consolidate Data

```bash
pixi run mojo-consolidate
```

**What it does**:
- Merges chunks and embeddings
- Applies quality filters
- Creates consolidated Parquet dataset

**Time**: <1 minute  
**Output**: `shared/build/mojo_embeddings.parquet`

#### Step 4: Load to DuckLake

```bash
pixi run mojo-load
```

**What it does**:
- Loads Parquet data into DuckLake catalog
- Creates versioned table `mojo_docs`
- Enables reproducible builds and rollbacks

**Time**: <1 minute  
**Output**: `servers/mojo-manual-mcp/runtime/mojo_manual_catalog.ducklake`

#### Step 5: Create Indexes

```bash
pixi run mojo-index
```

**What it does**:
- Materializes `mojo_docs` table from DuckLake
- Creates HNSW index for vector search
- Creates FTS index for keyword search
- Creates final indexed table `mojo_docs_indexed`

**Time**: 1-2 minutes  
**Output**: `servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db`

### Verify the Build

```bash
# Check database size (should be ~50-100MB)
ls -lh servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db

# Test search
pixi run search -- -q "ownership" -k 3
```

## Understanding the Build Pipeline

### Build Artifacts Location

```
shared/build/                          # Ephemeral build artifacts
├── processed_docs/
│   └── mojo/
│       ├── raw/                       # Cleaned text
│       ├── metadata/                  # Document metadata
│       ├── chunks/                    # Chunked content (JSONL)
│       └── manifest.json              # Processing summary
└── embeddings/
    └── mojo/
        └── *_embeddings.jsonl         # Vector embeddings

servers/mojo-manual-mcp/runtime/       # Distributable runtime
├── mojo_manual_mcp.db                 # Indexed database (FINAL OUTPUT)
├── mojo_manual_catalog.ducklake       # Versioned data lake
├── mojo_manual_mcp_server.py          # MCP server
└── search.py                          # Hybrid search engine
```

### Configuration Files

- **Processing**: `servers/mojo-manual-mcp/config/processing_config.yaml`
  - Source documentation path
  - Chunk size and overlap
  - Output directories

- **Server**: `servers/mojo-manual-mcp/config/server_config.yaml`
  - Database path
  - Embedding server URL
  - Search parameters

### Available Pixi Tasks

View all available tasks:
```bash
pixi task list
```

**Mojo-specific tasks**:
- `mojo-process` - Process documentation
- `mojo-generate-embeddings` - Generate embeddings
- `mojo-consolidate` - Consolidate data
- `mojo-load` - Load to DuckLake
- `mojo-index` - Create indexes
- `mojo-build` - Run full pipeline

**Server tasks**:
- `max-serve` - Start MAX embedding server
- `mcp-dev` - Run MCP Inspector
- `search` - CLI search tool

## Updating Documentation

### Sync from Upstream Source

If the Mojo documentation has been updated:

```bash
./tools/sync_documentation.sh \
  --source modularml/mojo \
  --dest source-documentation/mojo/manual \
  --sparse-path docs/manual
```

This clones or updates the documentation from the upstream repository.

### Rebuild After Sync

```bash
pixi run mojo-build
```

Or use the build script:
```bash
./tools/build_mcp.sh --mcp-name mojo
```

### Automating Updates

You can set up a cron job or CI/CD pipeline to automatically sync and rebuild:

```bash
# Example cron job (runs daily at 2 AM)
0 2 * * * cd /path/to/mcp && ./tools/sync_documentation.sh --source modularml/mojo --dest source-documentation/mojo/manual --sparse-path docs/manual && pixi run mojo-build
```

## Advanced Configuration

### Customizing Chunking

Edit `servers/mojo-manual-mcp/config/processing_config.yaml`:

```yaml
chunking:
  chunk_size: 256           # Tokens per chunk (default: 256)
  chunk_overlap: 50         # Overlap between chunks (default: 50)
  min_chunk_size: 50        # Minimum chunk size
  preserve_code_blocks: true
```

After editing, rebuild:
```bash
pixi run mojo-process
pixi run mojo-generate-embeddings
pixi run mojo-consolidate
pixi run mojo-load
pixi run mojo-index
```

### Tuning Search Weights

Adjust the balance between vector and keyword search:

```bash
# More weight to keyword search (good for exact matches)
pixi run search -- -q "ownership" --fts-weight 0.7 --vss-weight 0.3

# More weight to vector search (good for semantic queries)
pixi run search -- -q "memory management" --fts-weight 0.3 --vss-weight 0.7

# Default is 0.5 / 0.5
```

### Using a Different Embedding Model

Edit `servers/mojo-manual-mcp/config/server_config.yaml`:

```yaml
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"  # Smaller, faster model
  # or
  model_name: "sentence-transformers/all-mpnet-base-v2"  # Default, better quality
```

Restart MAX server with the new model:
```bash
pixi run max-serve  # Automatically uses configured model
# or manually:
max serve --model sentence-transformers/all-MiniLM-L6-v2
```

Then regenerate embeddings:
```bash
pixi run mojo-generate-embeddings
pixi run mojo-consolidate
pixi run mojo-load
pixi run mojo-index
```

## Troubleshooting

### Issue: `pixi install` fails

**Solution**: Clear cache and retry:
```bash
pixi clean
pixi install
```

### Issue: MAX server fails to start

**Cause**: Port 8000 already in use

**Solution**: Check what's using the port:
```bash
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

Kill the process or change the port in configuration.

### Issue: Embedding generation is very slow

**Cause**: MAX server not optimized or CPU-only inference

**Solutions**:
- Ensure MAX is using GPU if available
- Use a smaller/faster model (see Advanced Configuration)
- Increase MAX server workers

### Issue: Search returns no results

**Cause**: Database empty or corrupted

**Solution**: Rebuild the database:
```bash
pixi run mojo-build
```

Check database size:
```bash
ls -lh servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db
# Should be ~50-100MB
```

### Issue: `pixi run` commands fail with "task not found"

**Cause**: Running from wrong directory

**Solution**: Ensure you're in the repository root:
```bash
cd /path/to/mcp
pixi task list  # Verify tasks are available
```

### Issue: VS Code doesn't see the MCP server

**Causes**:
1. Absolute paths not set correctly
2. MAX server not running (if `AUTO_START_MAX=0`)
3. VS Code needs restart

**Solutions**:
```bash
# 1. Verify paths are absolute
cd mcp && pwd
# Use this output in your VS Code config

# 2. Manually start MAX
pixi run max-serve

# 3. Reload VS Code window
# Cmd/Ctrl+Shift+P → "Developer: Reload Window"
```

### Issue: Out of memory during embedding generation

**Cause**: Processing too many chunks at once

**Solution**: Reduce batch size in embedding script or process fewer documents at a time.

## Next Steps

- **Use the server**: See [USING_MCP_SERVER.md](USING_MCP_SERVER.md)
- **Create new servers**: See [CREATING_NEW_MCP.md](CREATING_NEW_MCP.md)
- **Understand architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Reference

### Key Directories

- `source-documentation/` - Raw documentation sources
- `shared/build/` - Ephemeral build artifacts (not committed)
- `servers/*/runtime/` - Distributable runtime files and databases
- `servers/*/config/` - Configuration files
- `tools/` - Automation scripts

### Key Files

- `pixi.toml` - Dependency and task definitions
- `pixi.lock` - Locked dependency versions
- `servers/mojo-manual-mcp/requirements.txt` - For non-pixi users
- `.gitignore` - Excludes build artifacts

### Environment Variables

- `MOJO_DB_PATH` - Path to indexed database
- `MAX_SERVER_URL` - Embedding server endpoint
- `EMBED_MODEL_NAME` - Sentence transformer model
- `AUTO_START_MAX` - Auto-start MAX server (1=yes, 0=no)
- `PROJECT_ROOT` - Resolved automatically in configs

---

**Setup Time**: 5-15 minutes (depending on rebuilding)  
**Difficulty**: Intermediate  
**Recommended For**: Development and customization
