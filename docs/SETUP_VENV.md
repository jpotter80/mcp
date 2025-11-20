# Setup Guide Without Pixi (Python venv)

Complete guide for setting up the MCP documentation search framework using standard Python virtual environments.

## Table of Contents

- [When to Use This Guide](#when-to-use-this-guide)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Running the Pre-Built Server](#running-the-pre-built-server)
- [Rebuilding from Source](#rebuilding-from-source)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## When to Use This Guide

Use this guide if you:
- Don't want to install pixi
- Prefer standard Python tools (pip, venv)
- Need minimal dependencies
- Are familiar with Python virtual environments

**Note**: Pixi is recommended for easier dependency management and task automation. See [SETUP_PIXI.md](SETUP_PIXI.md) if you're interested.

## Prerequisites

### Python 3.10+

Check your Python version:
```bash
python3 --version
```

If you need to install or upgrade Python:

**macOS**:
```bash
brew install python@3.10
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**Windows**:
Download from [python.org](https://www.python.org/downloads/)

### Git

**macOS**: Pre-installed or `brew install git`  
**Linux**: `sudo apt-get install git` or `sudo yum install git`  
**Windows**: Download from [git-scm.com](https://git-scm.com/)

### MAX CLI (for embeddings)

MAX is needed for generating embeddings (if rebuilding from source):

```bash
pip install max-cli
```

Or follow instructions at [modular.com/max](https://www.modular.com/max)

## Initial Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd mcp
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

This creates a `venv/` directory with an isolated Python environment.

### 3. Activate Virtual Environment

**macOS/Linux**:
```bash
source venv/bin/activate
```

**Windows**:
```powershell
venv\Scripts\activate
```

Your prompt should now show `(venv)` indicating the environment is active.

### 4. Install Server Dependencies

```bash
pip install -r servers/mojo-manual-mcp/requirements.txt
```

This installs:
- FastMCP (MCP server framework)
- DuckDB with VSS extension
- Python dependencies for the runtime

**Time**: 2-5 minutes

### 5. Install Build Dependencies (Optional)

Only needed if rebuilding from source:

```bash
# If requirements files exist in shared directory
pip install -r shared/preprocessing/requirements.txt
pip install -r shared/embedding/requirements.txt

# Or install individual packages
pip install python-frontmatter markdown beautifulsoup4 lxml
pip install duckdb pyarrow pandas numpy
pip install transformers sentence-transformers
```

### 6. Verify Installation

```bash
python --version
pip list | grep -i duckdb
```

You should see DuckDB and other installed packages.

## Running the Pre-Built Server

The repository includes pre-built databases, so you can run the server immediately.

### 1. Start MAX Embedding Server

In one terminal (with venv activated):

```bash
max serve --model sentence-transformers/all-mpnet-base-v2
```

**Port**: Runs on `http://localhost:8000`  
**Keep this terminal running**

Alternative: Use a different port if 8000 is busy:
```bash
max serve --model sentence-transformers/all-mpnet-base-v2 --port 8001
# Update MAX_SERVER_URL environment variable accordingly
```

### 2. Test the MCP Server

In another terminal:

```bash
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Navigate to repository
cd mcp

# Run the server
python servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
```

The server starts in stdio mode, ready for MCP connections.

### 3. Test with CLI Search

With venv activated:

```bash
cd servers/mojo-manual-mcp/runtime
python search.py -q "How do I declare a variable?" -k 5
```

You should see search results with snippets from Mojo documentation.

### 4. Configure for VS Code

1. Get absolute paths:

```bash
cd mcp
echo "$(pwd)/servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"
echo "$(pwd)/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db"
```

2. Get Python interpreter path from your venv:

```bash
# With venv activated
which python  # macOS/Linux
where python  # Windows
```

3. Add to VS Code settings (`.vscode/settings.json` or user settings):

```json
{
  "mcpServers": {
    "mojo-docs": {
      "command": "/absolute/path/to/mcp/venv/bin/python",
      "args": [
        "/absolute/path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"
      ],
      "env": {
        "MOJO_DB_PATH": "/absolute/path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db",
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
        "AUTO_START_MAX": "0"
      }
    }
  }
}
```

**Important**: 
- Use **absolute paths** for everything
- Use the Python from your venv (not system Python)
- Set `AUTO_START_MAX=0` since you'll start MAX manually

4. Start MAX server manually:

```bash
source venv/bin/activate
max serve --model sentence-transformers/all-mpnet-base-v2
```

5. Restart VS Code or reload window

6. Test: Ask Copilot "What is ownership in Mojo?"

## Rebuilding from Source

If you want to rebuild the database from scratch or have updated documentation.

### Prerequisites

Ensure you have:
- Build dependencies installed (see step 5 in Initial Setup)
- MAX server running
- Sufficient disk space (~500MB for build artifacts)

### Step 1: Process Documentation

```bash
source venv/bin/activate  # Activate venv
cd mcp

python -m shared.preprocessing.src.pipeline --mcp-name mojo
```

**What it does**: Reads MDX files, cleans them, chunks into ~350-400 tokens  
**Output**: `shared/build/processed_docs/mojo/chunks/*.jsonl`  
**Time**: 1-2 minutes

### Step 2: Generate Embeddings

Ensure MAX server is running on port 8000.

```bash
python shared/embedding/generate_embeddings.py --mcp-name mojo
```

**What it does**: Generates 768-dim vectors for each chunk via MAX  
**Output**: `shared/build/embeddings/mojo/*_embeddings.jsonl`  
**Time**: 5-10 minutes

**Troubleshooting**: If you get "MAX server not running" error:
```bash
# In another terminal
source venv/bin/activate
max serve --model sentence-transformers/all-mpnet-base-v2
```

### Step 3: Consolidate Data

```bash
python shared/embedding/consolidate_data.py --mcp-name mojo
```

**What it does**: Merges chunks + embeddings, applies quality filters  
**Output**: `shared/build/mojo_embeddings.parquet`  
**Time**: <1 minute

### Step 4: Load to DuckLake

```bash
python shared/embedding/load_to_ducklake.py --mcp-name mojo
```

**What it does**: Creates versioned data lake  
**Output**: `servers/mojo-manual-mcp/runtime/mojo_manual_catalog.ducklake`  
**Time**: <1 minute

### Step 5: Create Indexes

```bash
python shared/embedding/create_indexes.py --mcp-name mojo
```

**What it does**: Creates HNSW (vector) + FTS (keyword) indexes  
**Output**: `servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db`  
**Time**: 1-2 minutes

### Verify the Build

```bash
# Check database size (should be ~50-100MB)
ls -lh servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db

# Test search
cd servers/mojo-manual-mcp/runtime
python search.py -q "ownership" -k 3
```

### Automated Build Script

Use the build script for convenience:

```bash
./tools/build_mcp.sh --mcp-name mojo --use-python
```

**Note**: The script detects if pixi is available, otherwise uses python directly.

## Configuration

### Environment Variables

Set before running the server:

```bash
export MOJO_DB_PATH="/absolute/path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db"
export MAX_SERVER_URL="http://localhost:8000/v1"
export EMBED_MODEL_NAME="sentence-transformers/all-mpnet-base-v2"
export AUTO_START_MAX="0"  # Manual MAX server management

python servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
```

### Configuration Files

Edit these YAML files to customize behavior:

**Processing config**: `servers/mojo-manual-mcp/config/processing_config.yaml`
```yaml
chunking:
  chunk_size: 256           # Tokens per chunk
  chunk_overlap: 50         # Overlap between chunks
  min_chunk_size: 50
  preserve_code_blocks: true
```

**Server config**: `servers/mojo-manual-mcp/config/server_config.yaml`
```yaml
server:
  name: "mojo-docs"
  database_path: "${SERVER_ROOT}/runtime/mojo_manual_mcp.db"

embedding:
  max_server_url: "http://localhost:8000/v1"
  model_name: "sentence-transformers/all-mpnet-base-v2"

search:
  top_k: 5
  fts_title_weight: 2.0
  fts_content_weight: 1.0
```

After editing, rebuild the database (see Rebuilding from Source).

## Troubleshooting

### Issue: `python -m venv venv` fails

**Cause**: venv module not installed

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3.10-venv

# Or use virtualenv instead
pip install virtualenv
virtualenv venv
```

### Issue: pip install fails with permission errors

**Solution**: Ensure venv is activated:
```bash
source venv/bin/activate  # Should see (venv) in prompt
pip install -r servers/mojo-manual-mcp/requirements.txt
```

### Issue: ModuleNotFoundError when running scripts

**Cause**: Not in the correct directory or venv not activated

**Solution**:
```bash
# Activate venv
source venv/bin/activate

# Ensure you're in the repository root
cd /path/to/mcp

# Check Python is from venv
which python  # Should show path/to/mcp/venv/bin/python
```

### Issue: MAX server command not found

**Cause**: max-cli not installed in venv

**Solution**:
```bash
source venv/bin/activate
pip install max-cli
max --version
```

### Issue: DuckDB extension errors

**Cause**: VSS extension not available

**Solution**: DuckDB auto-installs extensions on first use. Ensure internet connection and retry.

### Issue: Search returns no results

**Cause**: Database empty or corrupted

**Solution**: Rebuild database (see Rebuilding from Source)

### Issue: VS Code doesn't recognize the MCP server

**Causes**:
1. Wrong Python path (not using venv Python)
2. Absolute paths not set correctly
3. MAX server not running

**Solutions**:
```bash
# 1. Verify venv Python path
source venv/bin/activate
which python  # Use this in VS Code config

# 2. Verify absolute paths
cd mcp && pwd
# Use this + relative paths in VS Code config

# 3. Start MAX manually
max serve --model sentence-transformers/all-mpnet-base-v2
```

### Issue: Out of memory during build

**Cause**: Processing large documentation or limited RAM

**Solution**: Process in smaller batches or use a machine with more memory

## Maintenance

### Updating the Virtual Environment

When dependencies change:

```bash
source venv/bin/activate
pip install --upgrade -r servers/mojo-manual-mcp/requirements.txt
```

### Keeping Documentation Up-to-Date

Sync documentation from upstream:

```bash
./tools/sync_documentation.sh \
  --source modularml/mojo \
  --dest source-documentation/mojo/manual \
  --sparse-path docs/manual
```

Then rebuild:
```bash
# Run each build step manually (see Rebuilding from Source)
# or use the build script
./tools/build_mcp.sh --mcp-name mojo
```

### Deactivating Virtual Environment

When done working:

```bash
deactivate
```

Your prompt returns to normal (no `(venv)` prefix).

## Next Steps

- **Use the server**: See [USING_MCP_SERVER.md](USING_MCP_SERVER.md)
- **Create new servers**: See [CREATING_NEW_MCP.md](CREATING_NEW_MCP.md)
- **Understand architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Consider pixi**: See [SETUP_PIXI.md](SETUP_PIXI.md) for easier workflow

## Comparison: venv vs. Pixi

| Feature | venv (this guide) | Pixi |
|---------|-------------------|------|
| Setup complexity | Moderate | Simple |
| Dependency management | Manual (pip) | Automatic |
| Task automation | Manual commands | Built-in tasks |
| Reproducibility | requirements.txt | Lock file |
| Cross-platform | Good | Excellent |
| Speed | Standard | Fast (conda-forge) |

**Recommendation**: If you frequently rebuild or work on multiple projects, consider trying pixi. For simple server usage, venv is perfectly fine.

---

**Setup Time**: 5-10 minutes  
**Difficulty**: Intermediate  
**Recommended For**: Users without pixi or preferring standard Python tools
