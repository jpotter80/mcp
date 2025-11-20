# Phase 1: Quick Start Guide

## Objective
Create the directory structure, update .gitignore, and establish configuration templates as the foundation for all subsequent phases.

## Estimated Time
30-45 minutes

## Prerequisites
- Git installed and configured
- Text editor or IDE
- Terminal access

---

## Step-by-Step Instructions

### Step 1: Create Feature Branch
```bash
cd /home/james/mcp
git checkout main
git pull origin main
git checkout -b restructure/01-directory-structure-and-config
```

### Step 2: Create Directory Structure
```bash
# Create shared infrastructure directories
mkdir -p shared/preprocessing
mkdir -p shared/preprocessing/src
mkdir -p shared/embedding
mkdir -p shared/templates
mkdir -p shared/build/processed_docs/mojo
mkdir -p shared/build/embeddings/mojo
mkdir -p shared/build/logs

# Create server directories
mkdir -p servers/mojo-manual-mcp/runtime
mkdir -p servers/mojo-manual-mcp/config

# Create other directories
mkdir -p docs
mkdir -p tools
```

Verify structure:
```bash
find shared servers docs tools -type d | head -20
```

### Step 3: Update .gitignore

Replace current `.gitignore` with:
```gitignore
# Build artifacts (ephemeral, generated at dev time)
shared/build/
*.pyc
__pycache__/
*.egg-info/
.pixi/

# Runtime databases (large, generated)
*.db
*.ducklake
*.ducklake.files/

# Environment files
.env
.env.local
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary
*.tmp
*.log

# OS
.DS_Store
.vs/
```

Verify:
```bash
cat .gitignore | head -10
```

### Step 4: Create Configuration Templates

#### Create `servers/mojo-manual-mcp/config/processing_config.yaml`
```yaml
# Processing Configuration for Mojo Manual MCP
# Used during build-time preprocessing and embedding generation
# Variables: ${SERVER_ROOT}, ${PROJECT_ROOT} are substituted at runtime

source:
  # Source documentation directory
  directory: "${SERVER_ROOT}/../../../source-documentation/mojo/manual"
  # Format of source files: mdx, markdown, rst, etc.
  format: "mdx"
  file_patterns:
    - "*.mdx"
    - "*.md"
  exclude_patterns:
    - "*.draft.mdx"
    - "node_modules/**"
    - ".git/**"

output:
  # Temporary build artifacts during preprocessing
  base_directory: "${PROJECT_ROOT}/shared/build/processed_docs/mojo"
  raw_dir: "raw"
  metadata_dir: "metadata"
  chunks_dir: "chunks"
  manifest_file: "manifest.json"

chunking:
  strategy: "recursive"
  chunk_size: 256
  chunk_overlap: 50
  min_chunk_size: 100
  preserve_code_blocks: true
  code_block_threshold: 50

processing:
  remove_jsx_components: true
  remove_imports: true
  preserve_code_blocks: true
  normalize_whitespace: true
  extract_urls: true
  url_base: "https://docs.modular.com/mojo/manual"

metadata:
  extract_frontmatter: true
  generate_section_hierarchy: true
  calculate_content_hash: true
  include_statistics: true

validation:
  check_content_preservation: true
  validate_chunk_sizes: true
  verify_metadata_completeness: true
  generate_report: true
```

#### Create `servers/mojo-manual-mcp/config/server_config.yaml`
```yaml
# MCP Server Runtime Configuration for Mojo Manual
# This file defines database paths, embedding server, and search parameters

server:
  # MCP server identifier and description
  name: "mojo-docs"
  description: "Mojo documentation search via hybrid semantic/keyword search"

database:
  # Path to indexed DuckDB database (relative to runtime directory)
  path: "${SERVER_ROOT}/runtime/mojo_manual_mcp.db"
  table_name: "mojo_docs_indexed"
  # DuckLake catalog for versioning (if using version history)
  ducklake_catalog: "${SERVER_ROOT}/runtime/mojo_manual_catalog.ducklake"

embedding:
  # Embedding server endpoint (MAX or OpenAI-compatible)
  max_server_url: "http://localhost:8000/v1"
  model_name: "sentence-transformers/all-mpnet-base-v2"
  # Auto-start MAX if endpoint unavailable
  auto_start: true
  auto_start_timeout: 30

search:
  # Number of results to return by default
  top_k: 5
  # Full-text search field weights (title boosted)
  fts_title_weight: 2.0
  fts_content_weight: 1.0
  # LRU cache size for query embeddings
  embed_cache_size: 512

  # Debug flags (set to false in production)
  debug_explain_vss: false
  debug_log_fts_path: false
```

### Step 5: Create `requirements.txt`

Create `servers/mojo-manual-mcp/requirements.txt`:
```
duckdb>=1.4.1,<2
openai>=2.3.0,<3
numpy>=2.3.3,<3
requests>=2.32.5,<3
pyyaml>=6.0.3,<7
mcp>=1.20.0,<2
```

### Step 6: Create README Files

#### Create `shared/README.md`
```markdown
# Shared Build Infrastructure

This directory contains reusable, development-time infrastructure used to build MCP servers.
**Note**: These are NOT included in distributed servers.

## Contents

- `preprocessing/` — Document processing pipeline (chunking, metadata extraction)
- `embedding/` — Embedding generation and data consolidation
- `templates/` — Code templates for new MCP servers
- `build/` — Generated artifacts (ephemeral, not committed)

## Usage

This infrastructure is used during development to process documentation and build indexed databases.
Processed databases are then committed to individual server directories in `/servers/`.

## Not Distributed

When distributing individual MCP servers (e.g., as GitHub repositories), 
only the `/servers/{mcp}/runtime/` directory is included, along with minimal configuration.
The shared infrastructure stays in the development repository.
```

#### Create `servers/mojo-manual-mcp/README.md`
```markdown
# Mojo Manual MCP Server

Searchable Mojo documentation via MCP (Model Context Protocol).

## Quick Start

### Option 1: With Python venv (No pixi required)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd runtime
python mojo_manual_mcp_server.py
```

### Option 2: With pixi
```bash
pixi run mojo-build  # Rebuild database if needed
cd runtime
python mojo_manual_mcp_server.py
```

## Configure in VS Code

Add to VS Code settings.json:
```json
{
  "mcp.servers": {
    "mojo-docs": {
      "type": "stdio",
      "command": "python3",
      "args": ["/absolute/path/to/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"],
      "cwd": "/absolute/path/to/mojo-manual-mcp/runtime",
      "env": {
        "MOJO_DB_PATH": "/absolute/path/to/mojo-manual-mcp/runtime/mojo_manual_mcp.db",
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

## Configuration Files

- `config/processing_config.yaml` — Document processing parameters (for rebuilding)
- `config/server_config.yaml` — MCP server runtime parameters

## Rebuilding the Database

If you update documentation sources:
```bash
pixi run mojo-process
pixi run mojo-embed
pixi run mojo-consolidate
pixi run mojo-load
pixi run mojo-index
```

(These tasks are in the root `/pixi.toml`)

## Resources

- `runtime/mojo_manual_mcp_server.py` — MCP server entry point
- `runtime/search.py` — Hybrid search engine
- `runtime/mojo_manual_mcp.db` — Indexed DuckDB database

For more details, see the main project README.
```

### Step 7: Update Root `.memory.md`

The memory file should already be updated. Verify:
```bash
head -20 .github/.memory.md
```

Should show the new multi-server architecture content.

### Step 8: Commit Changes

```bash
# Stage all new files and changes
git add -A

# Verify what's being committed
git status

# Commit with clear message
git commit -m "chore(phase-1): Create directory structure and configuration templates

- Create shared/ directory hierarchy for build infrastructure
- Create servers/mojo-manual-mcp/ for first MCP server
- Add .gitignore to exclude build artifacts and databases
- Create processing_config.yaml template for doc processing
- Create server_config.yaml template for MCP runtime
- Create requirements.txt for pip-based installation
- Add README.md files explaining each directory
- Update .memory.md with multi-server architecture

This establishes the foundation for all subsequent restructuring phases.

Phase: 1/8
Branch: restructure/01-directory-structure-and-config"
```

### Step 9: Verify and Push

```bash
# Verify commit
git log -1 --oneline

# Push branch
git push origin restructure/01-directory-structure-and-config
```

### Step 10: Create Pull Request

On GitHub:
1. Go to your repository
2. Click "Compare & pull request"
3. Set base branch to `main`
4. Add description:
```markdown
## Phase 1: Directory Structure and Configuration Templates

This PR establishes the foundation for the multi-server MCP architecture.

### Changes
- ✅ Directory structure created
- ✅ .gitignore updated  
- ✅ Configuration templates added
- ✅ README files created
- ✅ Architecture memory updated

### Verification
- [ ] New directories created correctly
- [ ] .gitignore excludes build artifacts
- [ ] Config YAML is valid
- [ ] All new files present

### Next Phase
After this merges, Phase 2 adds multi-format document processor support.
```

5. Request review

---

## What's Next?

After Phase 1 is merged:

1. **Phase 2**: Multi-format document processor support (creates pluggable architecture)
2. **Phase 3**: Parameterize build scripts (add --config arguments)
3. ... (See RESTRUCTURING_PLAN.md for phases 4-8)

---

## Checklist

- [ ] Branch created
- [ ] Directories created
- [ ] .gitignore updated
- [ ] Config YAML files created (valid YAML)
- [ ] README.md files created
- [ ] .memory.md verified
- [ ] Changes staged and committed
- [ ] Push to origin
- [ ] PR created
- [ ] PR description complete

---

## Common Issues & Solutions

### Issue: Directory already exists
```bash
# That's fine - the command will work, no error
mkdir -p servers/mojo-manual-mcp/runtime
# (safe, won't fail if exists)
```

### Issue: .gitignore not updated
```bash
# Use your text editor to update it manually:
nano .gitignore
# Or use the content provided in Step 3
```

### Issue: YAML syntax error
```bash
# Validate YAML:
python3 -c "import yaml; yaml.safe_load(open('servers/mojo-manual-mcp/config/processing_config.yaml'))"
# Should output nothing if valid
```

### Issue: Can't push branch
```bash
# Make sure you're on the correct branch:
git branch
# Should show * restructure/01-...

# If not, switch:
git checkout restructure/01-directory-structure-and-config
```

---

## Estimated Output

After Phase 1:
```
✅ 13 new directories
✅ 2 YAML config files
✅ 1 requirements.txt
✅ 2 README.md files  
✅ .gitignore updated
✅ 1 git commit
✅ 1 PR ready for review
```

Total lines added: ~200 (mostly config files)
No code changes yet (templates prepared)

---

**Ready? Start with `git checkout -b restructure/01-directory-structure-and-config`**
