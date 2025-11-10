# MCP Multi-Server Restructuring Plan

## Executive Summary

This plan restructures the project to support multiple MCP servers (Mojo, DuckDB, etc.) while maintaining a clean separation between:
- **Source documentation** (organized by tool/library)
- **Shared build-time infrastructure** (preprocessing & embedding pipeline)
- **Generated artifacts** (processed docs, embeddings, databases)
- **Runtime servers** (one per MCP server, with specific naming and organization)

---

## Current State vs. Target State

### Current Organization

```
/home/james/mcp/
├── preprocessing/              # Build-time pipeline
├── embedding/                  # Embeddings & indexing
├── processed_docs/             # Generated chunks, embeddings, metadata
├── runtime/                    # Runtime package
│   ├── search.py              # Generic search template
│   ├── server.py              # Mojo-specific MCP server
│   ├── mcp_server/
│   └── main.db                # Mojo-specific indexed DB
├── mojo_catalog.ducklake      # Mojo-specific DuckLake catalog
├── source-documentation/mojo/manual/  # Mojo docs
├── search.py                  # CLI search tool (duplicate)
├── main.db                    # Duplicate DB at root
└── pixi.toml                  # Root workspace config
```

**Issues:**
- Multiple `main.db` and `search.py` files (ambiguous)
- Runtime server not clearly named (is it Mojo-specific?)
- Preprocessing hardcoded to single source (Mojo manual)
- No clear naming convention for MCP-specific artifacts
- Shared infrastructure mixed with Mojo-specific code

---

## Target Organization

### Directory Structure

```
/home/james/mcp/
│
├── source-documentation/
│   ├── mojo/
│   │   ├── manual/                     # Mojo docs source (mdx/md files)
│   │   └── README.md                   # Notes about Mojo manual source
│   ├── duckdb/
│   │   ├── docs/                       # DuckDB docs source
│   │   └── README.md
│   └── [other-tools]/
│       ├── [docs-or-guide]/            # Source docs
│       └── README.md
│
├── shared/
│   ├── preprocessing/                  # Moved from /preprocessing
│   │   ├── src/
│   │   │   ├── pipeline.py
│   │   │   ├── mdx_processor.py
│   │   │   ├── chunker.py
│   │   │   ├── metadata_extractor.py
│   │   │   ├── utils.py
│   │   │   └── __init__.py
│   │   ├── config/
│   │   │   └── processing_config.yaml
│   │   ├── README.md
│   │   └── __init__.py
│   │
│   ├── embedding/                      # Moved from /embedding
│   │   ├── generate_embeddings.py
│   │   ├── consolidate_data.py
│   │   ├── load_to_ducklake.py
│   │   ├── create_indexes.py
│   │   ├── README.md
│   │   └── [any shared utilities]
│   │
│   ├── templates/                      # NEW: Reusable code templates
│   │   ├── search_template.py          # Moved from /search.py → template
│   │   ├── mcp_server_template.py      # Template for new MCP servers
│   │   └── README.md
│   │
│   └── build/                          # NEW: Generated/ephemeral artifacts
│       ├── logs/
│       ├── processed_docs/             # Moved from /processed_docs
│       │   ├── mojo/
│       │   │   ├── raw/
│       │   │   ├── metadata/
│       │   │   ├── chunks/
│       │   │   └── manifest.json
│       │   ├── duckdb/
│       │   │   ├── raw/
│       │   │   ├── metadata/
│       │   │   ├── chunks/
│       │   │   └── manifest.json
│       │   └── [other-tools]/
│       │
│       └── embeddings/                 # By-product of build
│           ├── mojo/
│           │   └── embeddings/
│           ├── duckdb/
│           │   └── embeddings/
│           └── [other-tools]/
│
├── servers/
│   ├── mojo-manual-mcp/
│   │   ├── runtime/                    # Runtime code & built databases
│   │   │   ├── mojo_manual_mcp_server.py
│   │   │   ├── search.py               # Instance-specific search (copy/adapted from template)
│   │   │   ├── mojo_manual_mcp.db      # Indexed database for this server
│   │   │   ├── mojo_manual_catalog.ducklake  # DuckLake catalog for this server
│   │   │   ├── README.md
│   │   │   └── __init__.py
│   │   ├── config/                     # Server-specific config (NEW)
│   │   │   ├── processing_config.yaml  # Override/customization
│   │   │   └── server_config.yaml      # MCP server-specific settings
│   │   ├── pixi.toml                   # Server-specific dependencies (optional)
│   │   └── README.md
│   │
│   ├── duckdb-docs-mcp/
│   │   ├── runtime/
│   │   │   ├── duckdb_docs_mcp_server.py
│   │   │   ├── search.py
│   │   │   ├── duckdb_docs_mcp.db
│   │   │   ├── duckdb_docs_catalog.ducklake
│   │   │   ├── README.md
│   │   │   └── __init__.py
│   │   ├── config/
│   │   │   ├── processing_config.yaml
│   │   │   └── server_config.yaml
│   │   └── README.md
│   │
│   └── [other-mcp-servers]/
│
├── tools/                              # Utilities & reference
│   ├── build_all_servers.sh           # Script to build all MCPs
│   ├── new_mcp_scaffold.sh             # Script to scaffold new MCP
│   └── [other utility scripts]
│
├── docs/                               # Project-level documentation
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── RESTRUCTURING_PLAN.md           # This file
│
├── pixi.toml                           # Root workspace (workspace + build tasks)
├── pixi.lock
├── .gitignore
└── .github/
    └── copilot-instructions.md
```

---

## Phase-by-Phase Migration Plan

### Phase 1: Directory Structure Setup

#### 1.1 Create new directory hierarchy
```bash
mkdir -p shared/{preprocessing,embedding,templates,build/{processed_docs,embeddings,logs}}
mkdir -p servers/mojo-manual-mcp/{runtime,config}
mkdir -p servers/mojo-manual-mcp/runtime
mkdir -p docs
mkdir -p tools
```

#### 1.2 Move documentation files to docs/
```bash
mv ARCHITECTURE.md docs/
mv PREPROCESSING.md docs/
mv RUNTIME.md docs/
mv DEVELOPMENT.md docs/
mv CONSOLIDATION_SUMMARY.md docs/
mv project.md docs/
mv mojo-example.md docs/
# Create new docs/README.md linking to others
```

---

### Phase 2: Consolidate Build-Time Infrastructure

#### 2.1 Move preprocessing to shared/
```bash
mv preprocessing/src shared/preprocessing/
mv preprocessing/config shared/preprocessing/
mv preprocessing/README.md shared/preprocessing/
mv preprocessing/__init__.py shared/preprocessing/
rm -rf preprocessing/
```

**Changes needed in files:**
- `shared/preprocessing/src/pipeline.py`:
  - Update import paths
  - Add support for dynamic source/output path configuration (not hardcoded)
  - Add ability to specify which documentation source to process

#### 2.2 Move embedding to shared/
```bash
mv embedding/generate_embeddings.py shared/embedding/
mv embedding/consolidate_data.py shared/embedding/
mv embedding/load_to_ducklake.py shared/embedding/
mv embedding/create_indexes.py shared/embedding/
mv embedding/README.md shared/embedding/
# Don't move embedding/main.db (it's Mojo-specific)
rm -rf embedding/
```

**Changes needed in files:**
- `shared/embedding/*.py` scripts:
  - Make all path configurations parameterizable (input/output dirs, catalog path, db names)
  - Accept CLI arguments or environment variables to specify:
    - Which MCP this is for (for naming conventions)
    - Input/output directories
    - Database and table names

#### 2.3 Move and rename templates
```bash
mv search.py shared/templates/search_template.py
cp runtime/server.py shared/templates/mcp_server_template.py
```

**Changes needed:**
- `shared/templates/search_template.py`:
  - Replace hardcoded env var defaults with more generic/configurable approach
  - Document template variables to override per MCP server
  - Keep as a reference template (not used directly at runtime)

- `shared/templates/mcp_server_template.py`:
  - Make server name/description generic in docstring
  - Document all points requiring customization
  - Add configuration section for MCP-specific settings

#### 2.4 Move processed docs to shared/build/
```bash
mv processed_docs shared/build/processed_docs/
mkdir -p shared/build/processed_docs/mojo
mv shared/build/processed_docs/*/raw/* shared/build/processed_docs/mojo/raw/ 2>/dev/null || true
mv shared/build/processed_docs/*/metadata/* shared/build/processed_docs/mojo/metadata/ 2>/dev/null || true
mv shared/build/processed_docs/*/chunks/* shared/build/processed_docs/mojo/chunks/ 2>/dev/null || true
mv shared/build/processed_docs/manifest.json shared/build/processed_docs/mojo/ || true
```

#### 2.5 Move logs and embeddings
```bash
mv logs shared/build/
mkdir -p shared/build/embeddings/mojo
mv processed_docs/embeddings/* shared/build/embeddings/mojo/ 2>/dev/null || true
```

---

### Phase 3: Organize Runtime Servers

#### 3.1 Create Mojo MCP runtime directory
```bash
mkdir -p servers/mojo-manual-mcp/runtime
mkdir -p servers/mojo-manual-mcp/config
```

#### 3.2 Move Mojo-specific runtime files
```bash
# Move the old runtime search/server to new location
cp runtime/search.py servers/mojo-manual-mcp/runtime/search.py
cp runtime/server.py servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
cp runtime/mcp_server/ servers/mojo-manual-mcp/runtime/ || true

# Move Mojo-specific databases
mv main.db servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db
mv mojo_catalog.ducklake servers/mojo-manual-mcp/runtime/mojo_manual_catalog.ducklake
mv mojo_catalog.ducklake.files/ servers/mojo-manual-mcp/runtime/mojo_catalog.ducklake.files/
```

#### 3.3 Create server-specific config
Create `servers/mojo-manual-mcp/config/processing_config.yaml`:
```yaml
source:
  directory: "/home/james/mcp/source-documentation/mojo/manual"
  file_patterns:
    - "*.mdx"
    - "*.md"
  exclude_patterns:
    - "*.draft.mdx"
    - "node_modules/**"
    - ".git/**"

output:
  base_directory: "/home/james/mcp/shared/build/processed_docs/mojo"
  raw_dir: "raw"
  metadata_dir: "metadata"
  chunks_dir: "chunks"
  manifest_file: "manifest.json"

# ... rest of config (customized per MCP) ...
```

Create `servers/mojo-manual-mcp/config/server_config.yaml`:
```yaml
# MCP server configuration
server:
  name: "mojo-docs"
  description: "Mojo documentation search via hybrid indexing"
  database:
    path: "runtime/mojo_manual_mcp.db"
    table_name: "mojo_docs_indexed"
  ducklake_catalog: "runtime/mojo_manual_catalog.ducklake"

embedding:
  max_server_url: "http://localhost:8000/v1"
  model_name: "sentence-transformers/all-mpnet-base-v2"
  auto_start: true

search:
  top_k: 5
  fts_title_weight: 2.0
  fts_content_weight: 1.0
  embed_cache_size: 512

# ... other settings ...
```

#### 3.4 Update runtime files
**`servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py`:**
- Update docstring to reference "Mojo documentation MCP server"
- Update path references to use relative paths from runtime directory
- Update search.py import to reference local search.py

**`servers/mojo-manual-mcp/runtime/search.py`:**
- Update default `DB_PATH` from `"main.db"` to `"mojo_manual_mcp.db"`
- Update default `TABLE_NAME` stays as `"mojo_docs_indexed"` (or make it config-driven)
- Update `MOJO_DB_PATH` env var handling to use defaults appropriate for this server

---

### Phase 4: Update Root Configuration & Tasks

#### 4.1 Update root pixi.toml

**Before:**
```toml
[tasks]
process = "python -m preprocessing.src.pipeline"
generate-embeddings = "python embedding/generate_embeddings.py"
consolidate = "python embedding/consolidate_data.py"
load = "python embedding/load_to_ducklake.py"
index = "python embedding/create_indexes.py"
search = "python search.py"
mcp-dev = "mcp dev mcp_server/server.py"
max-serve = "max serve --model sentence-transformers/all-mpnet-base-v2"
```

**After:**
```toml
[tasks]
# Build tasks (for each MCP server, parameterized)
process-mojo = "python -m shared.preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml"
generate-embeddings-mojo = "python shared/embedding/generate_embeddings.py --mcp-name mojo --config servers/mojo-manual-mcp/config/processing_config.yaml"
consolidate-mojo = "python shared/embedding/consolidate_data.py --mcp-name mojo"
load-mojo = "python shared/embedding/load_to_ducklake.py --mcp-name mojo"
index-mojo = "python shared/embedding/create_indexes.py --mcp-name mojo"

# Build all MCPs
build-all = "bash tools/build_all_servers.sh"

# Runtime tasks
search-mojo = "python servers/mojo-manual-mcp/runtime/search.py"
mcp-dev-mojo = "mcp dev servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"
max-serve = "max serve --model sentence-transformers/all-mpnet-base-v2"

# Template/example
show-template = "cat shared/templates/search_template.py"
```

#### 4.2 Update path references in root workspace config

Ensure paths in pixi.toml use the new shared/ structure.

---

### Phase 5: Update All Code Path References

#### 5.1 Files requiring updates:

**`shared/preprocessing/src/pipeline.py`:**
- [ ] Add argparse to accept `--config` argument
- [ ] Update config loading to use passed config path
- [ ] Ensure source_dir and output directories from config are used (no hardcoding)
- [ ] Import paths updated from `preprocessing/` to relative imports

**`shared/preprocessing/src/utils.py`:**
- [ ] Update any hardcoded path references
- [ ] Update `load_config()` to support custom config path

**`shared/embedding/generate_embeddings.py`:**
- [ ] Add argparse to accept `--mcp-name` and `--config`
- [ ] Make `INPUT_DIR`, `OUTPUT_DIR` derived from config or arguments
- [ ] Update path construction to work from shared/ directory

**`shared/embedding/consolidate_data.py`:**
- [ ] Add argparse for `--mcp-name`
- [ ] Make `CHUNKS_DIR`, `EMBEDDINGS_DIR`, `OUTPUT_FILE` configurable
- [ ] Support dynamic output naming (e.g., `{mcp_name}_embeddings.parquet`)

**`shared/embedding/load_to_ducklake.py`:**
- [ ] Add argparse for `--mcp-name`
- [ ] Make `DUCKLAKE_CATALOG_PATH`, `DUCKLAKE_TABLE_NAME` configurable
- [ ] Support paths like `servers/{mcp-name}/runtime/{mcp-name}_catalog.ducklake`

**`shared/embedding/create_indexes.py`:**
- [ ] Add argparse for `--mcp-name`
- [ ] Make `DUCKLAKE_CATALOG_PATH`, `MAIN_DB_PATH`, `INDEXED_TABLE_NAME` configurable
- [ ] Support paths like `servers/{mcp-name}/runtime/{mcp-name}_mcp.db`

**`servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py`:**
- [ ] Update import path: `from shared.search import HybridSearcher`
- [ ] Or copy search.py locally and update paths
- [ ] Update docstring to reference "Mojo" specifically
- [ ] Update default env vars (e.g., `MOJO_DB_PATH` → `mojo_manual_mcp.db`)

**`servers/mojo-manual-mcp/runtime/search.py`:**
- [ ] Update default `DB_PATH` to `"mojo_manual_mcp.db"`
- [ ] Ensure relative paths work from this directory

#### 5.2 Configuration file references

**`shared/preprocessing/config/processing_config.yaml`:**
- This becomes a template/example
- Each MCP gets its own config at `servers/{mcp}/config/processing_config.yaml`

---

### Phase 6: Update Documentation & README Files

#### 6.1 Update docs (moved to docs/)
- [ ] `docs/ARCHITECTURE.md`: Update to reflect new structure, document template locations
- [ ] `docs/PREPROCESSING.md`: Update paths to use `shared/preprocessing/`
- [ ] `docs/RUNTIME.md`: Update to explain per-server setup, point to `servers/mojo-manual-mcp/runtime/`
- [ ] `docs/DEVELOPMENT.md`: Update task references to new pixi.toml tasks

#### 6.2 Create new documentation
- [ ] `shared/README.md`: Document shared infrastructure
- [ ] `shared/preprocessing/README.md`: Explain preprocessing pipeline (moved content)
- [ ] `shared/embedding/README.md`: Explain embedding pipeline (moved content)
- [ ] `shared/templates/README.md`: Explain how to create new MCP servers
- [ ] `servers/mojo-manual-mcp/README.md`: Mojo-specific runtime setup
- [ ] `tools/README.md`: Explain utility scripts
- [ ] Create/update root `docs/README.md` as entry point

#### 6.3 Update root README
- Explain new multi-server architecture
- Point to docs/ folder
- Explain how to build individual MCPs or all
- Show example: "To build Mojo MCP: `pixi run build-mojo`"

---

### Phase 7: Create Helper Scripts

#### 7.1 `tools/build_all_servers.sh`
```bash
#!/bin/bash
# Builds all MCP servers in sequence

echo "Building all MCP servers..."
pixi run process-mojo
pixi run generate-embeddings-mojo
pixi run consolidate-mojo
pixi run load-mojo
pixi run index-mojo

# Add more MCPs as they're created
echo "✓ All servers built successfully!"
```

#### 7.2 `tools/new_mcp_scaffold.sh`
Template script to quickly create a new MCP server structure:
```bash
#!/bin/bash
# Usage: new_mcp_scaffold.sh mcp_name [doc_source_path]
# Example: new_mcp_scaffold.sh duckdb /path/to/duckdb/docs
```

Creates:
- `source-documentation/{mcp_name}/`
- `servers/{mcp_name}-mcp/{runtime,config}`
- Configuration files
- Sample tasks in root pixi.toml

---

## Summary of Key Changes

### File/Directory Moves
| Current | Target | Notes |
|---------|--------|-------|
| `/preprocessing/` | `/shared/preprocessing/` | Shared infrastructure |
| `/embedding/` | `/shared/embedding/` | Shared infrastructure |
| `/processed_docs/` | `/shared/build/processed_docs/` | Generated artifacts |
| `/logs/` | `/shared/build/logs/` | Generated artifacts |
| `/search.py` | `/shared/templates/search_template.py` | Template reference |
| `/runtime/server.py` | `/shared/templates/mcp_server_template.py` | Template reference |
| `/runtime/` (Mojo) | `/servers/mojo-manual-mcp/runtime/` | Server-specific runtime |
| `/main.db` | `/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db` | Server-specific database |
| `/mojo_catalog.ducklake` | `/servers/mojo-manual-mcp/runtime/mojo_manual_catalog.ducklake` | Server-specific catalog |
| `*.md` docs | `/docs/` | Centralized documentation |

### Naming Conventions

**MCP Servers:**
- Directory: `servers/{tool-name}-{doc-type}-mcp/` (e.g., `mojo-manual-mcp`, `duckdb-docs-mcp`)
- Main server file: `{tool}_{doc_type}_mcp_server.py` (e.g., `mojo_manual_mcp_server.py`)
- Database: `{tool}_{doc_type}_mcp.db` (e.g., `mojo_manual_mcp.db`)
- DuckLake catalog: `{tool}_{doc_type}_catalog.ducklake` (e.g., `mojo_manual_catalog.ducklake`)

**Configuration:**
- Per-MCP config: `servers/{mcp-name}/config/`
- Processing config: `processing_config.yaml` (source paths, chunking params)
- Server config: `server_config.yaml` (MCP setup, database paths)

**Source Documentation:**
- Pattern: `source-documentation/{tool}/{doc-type}/` (e.g., `source-documentation/mojo/manual/`)
- Contains original MDX/MD files

### Configuration Parameterization

All build-time scripts need CLI arguments or env vars for:
- **MCP name** (for naming artifacts)
- **Config path** (for tool/doc-specific settings)
- **Source directory** (where docs come from)
- **Output directory** (where to write processed artifacts)
- **Database paths** (where to save indexed DB and catalog)

---

## Implementation Checklist

### Phase 1: Directory Structure
- [ ] Create directory hierarchy
- [ ] Move docs to docs/
- [ ] Move preprocessing to shared/
- [ ] Move embedding to shared/
- [ ] Move processed_docs to shared/build/

### Phase 2: Move Templates
- [ ] Move search.py to shared/templates/
- [ ] Move runtime/server.py to shared/templates/

### Phase 3: Move Mojo Runtime
- [ ] Create servers/mojo-manual-mcp/runtime/
- [ ] Copy runtime files to new location
- [ ] Move main.db and catalog files
- [ ] Create config/ directory

### Phase 4: Update Configuration Files
- [ ] Create servers/mojo-manual-mcp/config/processing_config.yaml
- [ ] Create servers/mojo-manual-mcp/config/server_config.yaml
- [ ] Update root pixi.toml

### Phase 5: Update Python Code
- [ ] Update preprocessing/src/ path imports
- [ ] Parameterize all path configurations in shared/embedding/
- [ ] Parameterize pipeline.py with --config argument
- [ ] Update runtime search.py and server.py path references
- [ ] Update test/example scripts

### Phase 6: Update Documentation
- [ ] Move markdown docs to docs/
- [ ] Create README files in each shared/ subdirectory
- [ ] Create server-specific README
- [ ] Update architecture documentation

### Phase 7: Create Helper Scripts
- [ ] Write build_all_servers.sh
- [ ] Write new_mcp_scaffold.sh

### Phase 8: Testing & Validation
- [ ] Test pixi tasks work
- [ ] Test build pipeline (process → index)
- [ ] Test MCP server runs
- [ ] Test search functionality
- [ ] Verify all paths are correct

---

## Rollback Strategy

If issues arise during migration:

1. **Keep backups** of all original files before moving
2. **Git commits** at each phase boundary for easy rollback
3. **Test in isolated branch** before committing to main
4. **Verify functionality** at each phase before proceeding

---

## Future Extensibility

This structure enables easy addition of new MCPs:

1. **Add documentation source:**
   ```bash
   mkdir -p source-documentation/{tool}/{doc-type}
   # Add .mdx/.md files
   ```

2. **Create server structure:**
   ```bash
   bash tools/new_mcp_scaffold.sh {tool-name} {doc-type}
   ```

3. **Configure:**
   - Update `servers/{tool-name}-{doc-type}-mcp/config/*.yaml`
   - Adjust processing parameters as needed

4. **Build:**
   ```bash
   pixi run process-{tool-name}
   pixi run generate-embeddings-{tool-name}
   pixi run consolidate-{tool-name}
   pixi run load-{tool-name}
   pixi run index-{tool-name}
   ```

5. **Deploy:**
   - Configure MCP client to use `servers/{tool-name}-{doc-type}-mcp/runtime/{server_name}.py`
   - Set `MOJO_DB_PATH` to point to appropriate `.db` file

---

## Open Questions & Decisions

1. **Shared embedding server vs. per-MCP?**
   - Current plan: Single MAX server at `localhost:8000` shared across all MCPs
   - Alternative: Per-MCP embedding server (more isolated but more resources)

2. **Shared search.py vs. per-MCP?**
   - Current plan: Copy search.py to each MCP runtime (isolation)
   - Alternative: Import shared template with config override

3. **Configuration format:**
   - Current plan: YAML files in `servers/{mcp}/config/`
   - Alternative: Env vars only, or JSON, or Python dataclasses

4. **Build artifacts location:**
   - Current plan: `shared/build/` to avoid polluting workspace
   - Alternative: Keep at root or per-server level

5. **Backward compatibility:**
   - Keep old paths for a transition period?
   - Or clean break to avoid confusion?

---

**This plan is ready for iteration. Review, refine, and approve before implementation.**
