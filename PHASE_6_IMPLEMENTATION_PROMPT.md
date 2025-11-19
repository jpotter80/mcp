# Phase 6 Execution Guide: Organize Mojo Server Structure
For Next Session's AI Model

## Quick Phase 5 Recap (Current State)

As of `restructure/05-move-build-infrastructure` (now merged to `main`):

- **All build infrastructure moved to `/shared/`**:
  - Preprocessing: `/shared/preprocessing/` (complete module)
  - Embedding scripts: `/shared/embedding/` (all scripts)
  - Old `/preprocessing/` and `/embedding/` directories removed
- **All pixi.toml tasks updated**: Reference `shared/preprocessing` and `shared/embedding` paths
- **Import paths fixed**: sys.path manipulation for shared module access, relative imports within packages
- **MAX server check added**: `generate_embeddings.py` verifies server availability before running
- **Full pipeline verified**: All steps working (process, embed, consolidate, load, index, search)
- **Search quality confirmed**: Hybrid search returns excellent results

Key accomplishments in Phase 5:
- Consolidated all build-time infrastructure in one location
- Separated build-time code from runtime code
- Added developer experience improvements (MAX server check, clear error messages)
- Updated workflow documentation with critical development rules

## Goal of Phase 6: Organize Mojo Server Structure

Organize the Mojo MCP server to be self-contained and ready for independent distribution:

1. Verify/organize server runtime files in `/servers/mojo-manual-mcp/runtime/`
2. Ensure database and catalog files are in correct server location
3. Update any references to old database/catalog locations
4. Clean up old runtime artifacts at project root
5. Verify MCP server functionality end-to-end

**Important**: This phase prepares the Mojo server for distribution. After Phase 6, the server should be fully self-contained.

## Phase 6 Objectives

1. **Verify server runtime structure**:
   - Confirm all runtime files are in `/servers/mojo-manual-mcp/runtime/`
   - Database: `mojo_manual_mcp.db` (with HNSW + FTS indexes)
   - Catalog: `mojo_catalog.ducklake` (DuckLake versioned storage)
   - Server: `mojo_manual_mcp_server.py` (MCP server script)
   - Search: `search.py` (hybrid search implementation)

2. **Update configuration references**:
   - Verify `servers/mojo-manual-mcp/config/server_config.yaml` points to runtime files
   - Check for any hardcoded paths that reference old locations
   - Ensure all `${SERVER_ROOT}` variables resolve correctly

3. **Clean up root-level artifacts**:
   - Remove/move `search.py` and `server.py` if they exist at root
   - Remove any old database files (`main.db`, `mojo_catalog.ducklake` at root)
   - Keep only shared build infrastructure and server directories

4. **Test MCP server functionality**:
   - Verify server can start and respond to MCP protocol
   - Test search functionality through MCP interface
   - Confirm AUTO_START_MAX behavior in MCP environment

5. **Documentation**:
   - Update server README with usage instructions
   - Document configuration options
   - Add deployment instructions

## Files and Components Involved

### Current Structure (After Phase 5)

```
/home/james/mcp/
├── shared/                         # Build infrastructure (Phase 5 complete)
│   ├── config_loader.py
│   ├── preprocessing/
│   │   └── src/
│   ├── embedding/
│   │   ├── generate_embeddings.py
│   │   ├── consolidate_data.py
│   │   ├── load_to_ducklake.py
│   │   └── create_indexes.py
│   └── build/                      # Ephemeral build artifacts
│       ├── processed_docs/mojo/
│       ├── embeddings/mojo/
│       └── mojo_embeddings.parquet
│
├── servers/
│   └── mojo-manual-mcp/
│       ├── runtime/                # Server runtime files
│       │   ├── mojo_manual_mcp.db  # ✅ Created in Phase 5
│       │   ├── mojo_catalog.ducklake  # ✅ Created in Phase 5
│       │   ├── mojo_manual_mcp_server.py  # ❓ Need to verify exists
│       │   └── search.py           # ❓ Need to verify exists
│       ├── config/
│       │   ├── processing_config.yaml
│       │   └── server_config.yaml
│       └── README.md
│
├── runtime/                        # OLD: May still exist at root
│   ├── search.py                   # ❓ Check if exists
│   ├── server.py                   # ❓ Check if exists
│   └── main.db                     # ❓ Check if exists
│
├── search.py                       # ❓ May exist at root
├── server.py                       # ❓ May exist at root
├── main.db                         # ❓ May exist at root
├── mojo_catalog.ducklake           # ❓ May exist at root
│
└── pixi.toml                       # Root workspace config
```

### Target Structure (After Phase 6)

```
/home/james/mcp/
├── shared/                         # Build infrastructure only
│   ├── config_loader.py
│   ├── preprocessing/
│   ├── embedding/
│   ├── templates/                  # NEW: Template files for reference
│   │   ├── search_template.py     # Generic search implementation
│   │   └── mcp_server_template.py # Generic MCP server template
│   └── build/                      # Ephemeral (gitignored)
│
├── servers/
│   └── mojo-manual-mcp/            # Self-contained Mojo server
│       ├── runtime/
│       │   ├── mojo_manual_mcp_server.py  # MCP server (renamed/verified)
│       │   ├── search.py           # Mojo-specific search
│       │   ├── mojo_manual_mcp.db  # Indexed database
│       │   ├── mojo_catalog.ducklake  # DuckLake catalog
│       │   └── __init__.py
│       ├── config/
│       │   ├── processing_config.yaml
│       │   └── server_config.yaml
│       ├── requirements.txt        # For pip installation
│       ├── pixi.toml               # Server-specific (optional)
│       └── README.md               # Server documentation
│
├── source-documentation/
│   └── mojo/
│       └── manual/                 # Mojo docs source
│
├── docs/                           # Project documentation
├── tools/                          # Utility scripts
└── pixi.toml                       # Root workspace config
```

## Step-by-Step Tasks

### Task 1: Audit Current Server Runtime Structure

**1.1 Check what runtime files exist**

```bash
# Check server runtime directory
ls -la servers/mojo-manual-mcp/runtime/

# Check for old runtime directory at root
ls -la runtime/ 2>/dev/null || echo "No root runtime/ directory"

# Check for old files at root
ls -la main.db search.py server.py mojo_catalog.ducklake 2>/dev/null
```

**1.2 Identify what needs to be moved or verified**

Based on the audit:
- If `server.py` exists at root or in `/runtime/`, it should be renamed to `mojo_manual_mcp_server.py` and placed in `servers/mojo-manual-mcp/runtime/`
- If `search.py` exists at root or in `/runtime/`, copy to `servers/mojo-manual-mcp/runtime/` (server-specific) and to `shared/templates/search_template.py` (template)
- Database files should ONLY exist in `servers/mojo-manual-mcp/runtime/`

### Task 2: Organize Server Runtime Files

**2.1 Move/rename MCP server file**

If `server.py` exists at root or `/runtime/`:
```bash
# Rename and move to server runtime
mv server.py servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
# OR
mv runtime/server.py servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
```

**2.2 Copy search.py to server runtime and templates**

```bash
# Copy to server runtime (instance-specific)
cp search.py servers/mojo-manual-mcp/runtime/search.py

# Copy to shared templates (for future servers)
mkdir -p shared/templates
cp search.py shared/templates/search_template.py
```

**2.3 Verify database files are in correct location**

The Phase 5 verification showed these files were created correctly:
- `servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db` ✅
- `servers/mojo-manual-mcp/runtime/mojo_catalog.ducklake` ✅

If old database files exist at root, remove them:
```bash
rm -f main.db mojo_catalog.ducklake
rm -rf mojo_catalog.ducklake.files/
```

**2.4 Clean up old runtime directory**

If `/runtime/` exists at root:
```bash
rm -rf runtime/
```

### Task 3: Verify Server Configuration

**3.1 Check server_config.yaml paths**

Verify `servers/mojo-manual-mcp/config/server_config.yaml` has correct paths:
```yaml
database:
  db_path: "${SERVER_ROOT}/runtime/mojo_manual_mcp.db"
  table_name: "mojo_docs_indexed"
  ducklake_catalog: "${SERVER_ROOT}/runtime/mojo_catalog.ducklake"

embedding:
  max_server_url: "http://localhost:8000/v1"
  model_name: "sentence-transformers/all-mpnet-base-v2"
  auto_start_max: true
  auto_start_timeout: 30

search:
  top_k: 5
  vector_weight: 0.7
  fts_weight: 0.3
  # ... other search params
```

**3.2 Update MCP server script imports (if needed)**

In `servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py`, ensure imports reference local `search.py`:
```python
from .search import HybridSearcher
# OR
from search import HybridSearcher  # If running as script
```

And config loading:
```python
# Add parent directories to path for config_loader access
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.config_loader import load_config_with_substitution
```

### Task 4: Create Server Documentation

**4.1 Update servers/mojo-manual-mcp/README.md**

Create comprehensive server documentation:
```markdown
# Mojo Manual MCP Server

MCP server providing hybrid search over Mojo documentation.

## Features

- **Hybrid Search**: Combines vector similarity (HNSW) + BM25 full-text search
- **Reciprocal Rank Fusion**: Intelligent result merging
- **Auto-Start MAX**: Automatically starts embedding server in MCP environments
- **Cached Embeddings**: LRU cache for query embeddings

## Installation

### Using pixi (recommended)
\`\`\`bash
pixi install
pixi run serve
\`\`\`

### Using pip
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python runtime/mojo_manual_mcp_server.py
\`\`\`

## Configuration

Edit `config/server_config.yaml` to customize:
- Database paths
- Search parameters (weights, top_k)
- Embedding model settings
- MAX server configuration

## MCP Integration

Add to your MCP client configuration (e.g., VS Code settings.json):
\`\`\`json
{
  "mcpServers": {
    "mojo-docs": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "--manifest-path", "/path/to/mcp/servers/mojo-manual-mcp/pixi.toml", "serve"],
      "cwd": "/path/to/mcp/servers/mojo-manual-mcp",
      "env": {
        "AUTO_START_MAX": "1"
      }
    }
  }
}
\`\`\`

## Usage

### MCP Resources
- `mojo://search/{query}` - Perform hybrid search
- `mojo://chunk/{chunk_id}` - Get specific chunk by ID

### MCP Tools
- `search` - Search Mojo documentation with configurable parameters

## Development

To rebuild the database:
\`\`\`bash
# From project root
pixi run mojo-build
\`\`\`

## Database Schema

The indexed database (`mojo_manual_mcp.db`) contains:
- **Table**: `mojo_docs_indexed` (1125 records)
- **HNSW Index**: Vector similarity search on 768-dim embeddings
- **FTS Index**: Full-text search on title and content (BM25)
- **Columns**: chunk_id, title, content, url, section_hierarchy, embedding

## Architecture

- **Search**: `runtime/search.py` - Hybrid search implementation
- **Server**: `runtime/mojo_manual_mcp_server.py` - MCP protocol handler
- **Config**: `config/server_config.yaml` - Runtime configuration
- **Database**: `runtime/mojo_manual_mcp.db` - Indexed search database
- **Catalog**: `runtime/mojo_catalog.ducklake` - DuckLake versioned storage
\`\`\`

**4.2 Create/update requirements.txt**

Ensure `servers/mojo-manual-mcp/requirements.txt` is complete:
```
duckdb>=1.4.1,<2
openai>=2.3.0,<3
numpy>=2.3.3,<3
requests>=2.32.5,<3
pyyaml>=6.0.3,<7
mcp>=1.20.0,<2
```

### Task 5: Test MCP Server Functionality

**5.1 Test server can start**

```bash
cd servers/mojo-manual-mcp
python runtime/mojo_manual_mcp_server.py
```

Should start without errors and initialize MCP protocol.

**5.2 Test with MCP Inspector (if available)**

```bash
pixi run mcp-dev  # If task exists
```

**5.3 Test search functionality**

From project root, using the existing search.py CLI:
```bash
python servers/mojo-manual-mcp/runtime/search.py -q "ownership" -k 5
```

Should return relevant Mojo documentation results.

**5.4 Verify AUTO_START_MAX behavior**

When running through MCP with `AUTO_START_MAX=1`, the server should:
1. Check if MAX server is running
2. If not, attempt to start it automatically
3. Fall back to FTS-only if MAX unavailable

### Task 6: Clean Up Root Directory

**6.1 Remove old root-level files**

After verifying everything works from server directory:
```bash
# From project root
rm -f server.py search.py main.db
rm -rf mojo_catalog.ducklake mojo_catalog.ducklake.files/
rm -rf runtime/  # If it exists
```

**6.2 Update .gitignore if needed**

Ensure build artifacts are ignored but server databases are tracked:
```gitignore
# Build artifacts (ephemeral)
shared/build/

# Runtime databases (tracked for distribution)
!servers/*/runtime/*.db
!servers/*/runtime/*.ducklake
```

### Task 7: Update Project Documentation

**7.1 Update root README.md**

Add section about server structure:
```markdown
## Servers

Individual MCP servers are located in `/servers/` directory. Each server is self-contained and can be distributed independently.

### Mojo Manual MCP
Location: `servers/mojo-manual-mcp/`
Documentation: See [servers/mojo-manual-mcp/README.md](servers/mojo-manual-mcp/README.md)
```

**7.2 Update RESTRUCTURING_PLAN.md**

Mark Phase 6 as complete and update status.

## Out of Scope for Phase 6

Do not:
- Change search algorithm or scoring logic
- Modify database schema or indexes
- Add new MCP tools or resources
- Create additional servers (DuckDB, etc.) - that's future phases
- Change build pipeline logic

## Success Criteria for Phase 6

Phase 6 is complete when:

1. ✅ All server runtime files in `/servers/mojo-manual-mcp/runtime/`
2. ✅ Server named correctly: `mojo_manual_mcp_server.py`
3. ✅ Database files in correct server location:
   - `mojo_manual_mcp.db` with indexes
   - `mojo_catalog.ducklake` catalog
4. ✅ Old root-level runtime files removed
5. ✅ Server configuration verified and documented
6. ✅ MCP server can start and respond to protocol
7. ✅ Search functionality verified working
8. ✅ Server README complete with:
   - Installation instructions (pixi + pip)
   - Configuration options
   - MCP integration guide
   - Development workflow
9. ✅ `requirements.txt` complete and accurate
10. ✅ Project documentation updated

## Development Workflow Reminder

**CRITICAL**: 
- Make all changes on feature branch `restructure/06-organize-mojo-server`
- **NEVER make code changes on `test/restructure` branch**
- **ALWAYS switch to `test/restructure` for testing/running code**
- Switch back to feature branch for fixes if needed
- Ask user to provide terminal output if not visible

## Notes for the Next Model

1. Phase 5 successfully moved all build infrastructure to `/shared/`
2. Database files were created in correct location during Phase 5 verification
3. Server files may need to be moved from root or `/runtime/` directory
4. This phase is primarily organization and documentation
5. After Phase 6, the Mojo server will be ready for independent distribution
6. Future phases (7-8) will add tooling, automation, and create additional servers
