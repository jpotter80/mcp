# Phase 4 Implementation Prompt for Next Session

## Context
The MCP project restructuring has successfully completed Phases 1, 2, and 3. Phase 3 (parameterized build scripts) has been merged to main. Phase 4 will move the build infrastructure into a shared directory structure, consolidating all dev-time tools while preparing runtime code to be distributed independently.

## Current State
- Main branch has Phases 1, 2, and 3 changes merged
- Build scripts are parameterized with `--config` and `--mcp-name` arguments
- config_loader.py utility implemented for variable substitution
- Ready to reorganize directory structure for better separation of concerns
- Persistent testing branch `test/restructure` is in place with all dependencies installed

## Task: Execute Phase 4

### Objective
Restructure the repository to separate build-time infrastructure (in `/shared/`) from runtime code that will be distributed (in `/servers/*/runtime/`). This phase moves all development/build tools to a shared location while keeping server-specific code self-contained.

### Branch Strategy
**Feature Branch**: `restructure/04-move-build-infrastructure`
**Testing Branch**: `test/restructure` (persistent, do NOT delete)

#### Branch Workflow
1. Create new feature branch from main:
   ```bash
   git checkout main
   git pull
   git checkout -b restructure/04-move-build-infrastructure
   ```

2. Make all changes on feature branch

3. Test by merging into persistent testing branch:
   ```bash
   # On feature branch, commit changes
   git add -A
   git commit -m "..."
   
   # Switch to testing branch and merge
   git checkout test/restructure
   git merge restructure/04-move-build-infrastructure
   pixi install  # Ensure dependencies available (usually already cached)
   # Run verification tests here
   ```

4. If tests pass, merge to main:
   ```bash
   git checkout main
   git merge restructure/04-move-build-infrastructure
   ```

### Key Files to Move/Create

#### MOVE: `preprocessing/` → `shared/preprocessing/`
Move entire directory:
```bash
mv preprocessing/src shared/preprocessing/
mv preprocessing/config shared/preprocessing/
mv preprocessing/README.md shared/preprocessing/
mv preprocessing/__init__.py shared/preprocessing/
rm -rf preprocessing/
```

#### MOVE: `embedding/` → `shared/embedding/`
Move all Python scripts (keep databases for now):
```bash
mkdir -p shared/embedding
mv embedding/generate_embeddings.py shared/embedding/
mv embedding/consolidate_data.py shared/embedding/
mv embedding/load_to_ducklake.py shared/embedding/
mv embedding/create_indexes.py shared/embedding/
mv embedding/README.md shared/embedding/
# Keep main.db and *.ducklake in root for now (will move with server in Phase 5)
rm -rf embedding/  # Or keep as empty dir temporarily
```

#### MOVE: `processed_docs/` → `shared/build/processed_docs/`
Build artifacts move to shared/build:
```bash
mkdir -p shared/build/processed_docs/mojo
mv processed_docs/raw/* shared/build/processed_docs/mojo/raw/ 2>/dev/null || true
mv processed_docs/metadata/* shared/build/processed_docs/mojo/metadata/ 2>/dev/null || true
mv processed_docs/chunks/* shared/build/processed_docs/mojo/chunks/ 2>/dev/null || true
mv processed_docs/manifest.json shared/build/processed_docs/mojo/ || true
rm -rf processed_docs/
```

#### MOVE: `logs/` → `shared/build/logs/`
Build logs move to shared/build:
```bash
mkdir -p shared/build/logs
mv logs/* shared/build/logs/ 2>/dev/null || true
rm -rf logs/
```

#### MOVE: Templates to `shared/templates/`
Template files for reuse:
```bash
mkdir -p shared/templates
mv search.py shared/templates/search_template.py
cp runtime/server.py shared/templates/mcp_server_template.py
```

#### CREATE: `shared/README.md`
New documentation for shared build infrastructure (see "Implementation Details" below).

### Implementation Details

#### Step 1: Create Feature Branch
```bash
cd /home/james/mcp
git checkout main
git pull
git checkout -b restructure/04-move-build-infrastructure
```

#### Step 2: Move Preprocessing Directory
```bash
# Ensure target directory exists
mkdir -p shared/preprocessing

# Move all components
mv preprocessing/src shared/preprocessing/
mv preprocessing/config shared/preprocessing/
mv preprocessing/README.md shared/preprocessing/
mv preprocessing/__init__.py shared/preprocessing/
rm -rf preprocessing/
```

**Important**: This creates:
- `shared/preprocessing/src/pipeline.py`
- `shared/preprocessing/src/chunker.py`
- `shared/preprocessing/src/mdx_processor.py`
- `shared/preprocessing/src/metadata_extractor.py`
- `shared/preprocessing/src/processor_factory.py`
- `shared/preprocessing/src/utils.py`
- `shared/preprocessing/config/processing_config.yaml`

#### Step 3: Move Embedding Scripts
```bash
# Ensure target directory exists
mkdir -p shared/embedding

# Move scripts (keep databases for now)
mv embedding/generate_embeddings.py shared/embedding/
mv embedding/consolidate_data.py shared/embedding/
mv embedding/load_to_ducklake.py shared/embedding/
mv embedding/create_indexes.py shared/embedding/
mv embedding/README.md shared/embedding/

# Clean up old directory
rm -rf embedding/
```

**Note about .db files**: Leave `main.db` and `mojo_catalog.ducklake*` in root for now. They'll move to server-specific locations in Phase 5.

#### Step 4: Move Build Artifacts
```bash
# Create shared build structure
mkdir -p shared/build/processed_docs/mojo/raw
mkdir -p shared/build/processed_docs/mojo/metadata
mkdir -p shared/build/processed_docs/mojo/chunks
mkdir -p shared/build/logs

# Move processed docs (if they exist)
if [ -d "processed_docs/raw" ]; then
    mv processed_docs/raw/* shared/build/processed_docs/mojo/raw/
fi
if [ -d "processed_docs/metadata" ]; then
    mv processed_docs/metadata/* shared/build/processed_docs/mojo/metadata/
fi
if [ -d "processed_docs/chunks" ]; then
    mv processed_docs/chunks/* shared/build/processed_docs/mojo/chunks/
fi
if [ -f "processed_docs/manifest.json" ]; then
    mv processed_docs/manifest.json shared/build/processed_docs/mojo/
fi

# Move logs (if they exist)
if [ -d "logs" ]; then
    mv logs/* shared/build/logs/ 2>/dev/null || true
fi

# Remove old directories
rm -rf processed_docs/ logs/
```

#### Step 5: Move Template Files
```bash
# Create templates directory
mkdir -p shared/templates

# Move search template
mv search.py shared/templates/search_template.py

# Copy server template (don't delete original - Phase 5 will update)
cp runtime/server.py shared/templates/mcp_server_template.py
```

#### Step 6: Create `shared/README.md`

Create new file with content explaining the shared build infrastructure structure:

```markdown
# Shared Build Infrastructure

This directory contains dev-time build tools and templates for the MCP project. These are used during documentation processing but are NOT included in distributed server packages.

## Structure

### `/preprocessing/`
**Purpose**: Document processing pipeline (MDX/MD → semantic chunks)

- `src/pipeline.py` — Main pipeline orchestrator
- `src/chunker.py` — LangChain-based chunking for various doc formats
- `src/mdx_processor.py` — MDX-specific processing logic
- `src/metadata_extractor.py` — Extract metadata from documents
- `src/processor_factory.py` — Factory pattern for pluggable processors
- `src/utils.py` — Shared utilities
- `config/processing_config.yaml` — Configuration template

**Usage**:
```bash
pixi run python -m shared.preprocessing.src.pipeline --config <path_to_config>
```

**Status**: Accepts `--config` argument for parameterized runs per server.

### `/embedding/`
**Purpose**: Embedding generation and consolidation (chunks → vectors → index)

- `generate_embeddings.py` — Create embeddings via embedding service (MAX/OpenAI)
- `consolidate_data.py` — Merge chunks + embeddings into Parquet files
- `load_to_ducklake.py` — Load Parquet data into versioned DuckLake catalog
- `create_indexes.py` — Create HNSW + FTS indexes in DuckDB
- `README.md` — Detailed embedding pipeline documentation

**Usage**:
```bash
# Generate embeddings for a specific server
pixi run python shared/embedding/generate_embeddings.py \
  --mcp-name <name> \
  --config <path_to_config>

# Consolidate data
pixi run python shared/embedding/consolidate_data.py --mcp-name <name>

# Load to DuckLake
pixi run python shared/embedding/load_to_ducklake.py --mcp-name <name>

# Create indexes
pixi run python shared/embedding/create_indexes.py --mcp-name <name>
```

**Status**: All scripts parameterized with `--mcp-name` argument.

### `/build/`
**Purpose**: Build artifacts (ephemeral, not distributed)

- `processed_docs/` — Intermediate processing outputs
- `logs/` — Build logs and processing history

**Lifecycle**: Regenerated each build cycle; not shipped with servers.

### `/templates/`
**Purpose**: Reusable templates for server-specific implementations

- `search_template.py` — Generic hybrid search implementation (reference for customization)
- `mcp_server_template.py` — Generic MCP server implementation (basis for server-specific servers)

**Usage**: Copy and customize for each new MCP server type.

## Integration with `/servers/`

Each MCP server in `/servers/{mcp-name}/` uses this shared infrastructure:

1. **Build Phase** (using shared tools):
   ```
   shared/preprocessing/ → shared/build/processed_docs/{mcp-name}/
   shared/embedding/ → {mcp-name}_embeddings.parquet
   ```

2. **Package Phase**:
   - Copy indexes to `servers/{mcp-name}/runtime/`
   - Copy/customize templates to `servers/{mcp-name}/runtime/`
   - Distribute complete server directory (no shared/ dependency)

3. **Runtime Phase** (distributed):
   - Server runs with only files in `servers/{mcp-name}/runtime/`
   - No dependency on shared/ directory

## Configuration

All build steps are driven by per-server configuration files:

```
servers/{mcp-name}/config/
  ├── processing_config.yaml    — Document processing parameters
  └── server_config.yaml        — Runtime server configuration
```

Example `processing_config.yaml`:
```yaml
server_root: "${SERVER_ROOT}"
project_root: "${PROJECT_ROOT}"
format: mdx
input_directory: "${SERVER_ROOT}/docs/manual"
output:
  base_directory: "${SERVER_ROOT}/processed_docs"
chunking:
  chunk_size: 350
  overlap: 75
```

Variable substitution:
- `${SERVER_ROOT}` → Server-specific directory (e.g., `servers/mojo-manual-mcp`)
- `${PROJECT_ROOT}` → Project root (`/home/james/mcp`)
- Environment variables via `${VAR_NAME}`

## Pixi Tasks

Root `pixi.toml` defines parameterized build tasks using this infrastructure:

```toml
# Mojo build pipeline (example)
mojo-process = "python -m shared.preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-embed = "python shared/embedding/generate_embeddings.py --mcp-name mojo --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-consolidate = "python shared/embedding/consolidate_data.py --mcp-name mojo"
mojo-load = "python shared/embedding/load_to_ducklake.py --mcp-name mojo"
mojo-index = "python shared/embedding/create_indexes.py --mcp-name mojo"
```

Add similar task definitions for each new MCP server.

## Development Workflow

To build a new documentation index:

```bash
# 1. Process documents
pixi run mojo-process

# 2. Generate embeddings
pixi run mojo-embed

# 3. Consolidate
pixi run mojo-consolidate

# 4. Load to DuckLake
pixi run mojo-load

# 5. Create indexes
pixi run mojo-index

# Result: indexes ready in servers/mojo-manual-mcp/runtime/
```

## Not Included in Distributed Servers

This shared infrastructure is development-only. Distributed servers (in `/servers/*/`) do NOT include:
- Source document files
- Processing configuration
- Embedding pipeline scripts
- Build artifacts

Servers only include:
- Pre-built indexes (`.db`, `.ducklake`)
- Runtime search implementation
- MCP server code
- Documentation

This keeps server packages small and focused on runtime functionality.
```

#### Step 7: Update File References

After moving files, update import paths in code that references them:

**Check `pixi.toml` references**:
```bash
# Current (after Phase 3):
# mojo-process = "python -m preprocessing.src.pipeline ..."
# Should become:
# mojo-process = "python -m shared.preprocessing.src.pipeline ..."

# Update all references from:
# - preprocessing/ → shared/preprocessing/
# - embedding/ → shared/embedding/
# - search.py → shared/templates/search_template.py
```

**Update any Python imports** (check for any files that import from old locations):
```bash
grep -r "from preprocessing" . 2>/dev/null | grep -v ".git"
grep -r "from embedding" . 2>/dev/null | grep -v ".git"
grep -r "import embedding" . 2>/dev/null | grep -v ".git"
```

**Common updates needed in root `pixi.toml`**:
```toml
# Old (Phase 3)
mojo-process = "python -m preprocessing.src.pipeline --config ..."
mojo-embed = "python embedding/generate_embeddings.py --mcp-name mojo ..."

# New (Phase 4)
mojo-process = "python -m shared.preprocessing.src.pipeline --config ..."
mojo-embed = "python shared/embedding/generate_embeddings.py --mcp-name mojo ..."
```

#### Step 8: Update `.gitignore`

Verify `.gitignore` entries for new structure:

```gitignore
# Build artifacts (ephemeral - not distributed)
shared/build/

# Cache and environment
__pycache__/
*.pyc
.pixi/
venv/
*.egg-info/

# Database files ARE tracked (essential)
# (DO NOT ignore *.db or *.ducklake)

# IDE and temp files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
```

**Note**: Database files (`.db`, `.ducklake`) should already be tracked from Phase 3 gitignore corrections. Leave them unignored.

#### Step 9: Verify Directory Structure

After all moves, directory structure should look like:

```
/home/james/mcp/
├── shared/
│   ├── preprocessing/
│   │   ├── src/
│   │   │   ├── pipeline.py
│   │   │   ├── chunker.py
│   │   │   ├── mdx_processor.py
│   │   │   ├── metadata_extractor.py
│   │   │   ├── processor_factory.py
│   │   │   └── utils.py
│   │   ├── config/
│   │   │   └── processing_config.yaml
│   │   └── README.md
│   ├── embedding/
│   │   ├── generate_embeddings.py
│   │   ├── consolidate_data.py
│   │   ├── load_to_ducklake.py
│   │   ├── create_indexes.py
│   │   └── README.md
│   ├── build/
│   │   ├── processed_docs/
│   │   │   └── mojo/
│   │   │       ├── raw/
│   │   │       ├── metadata/
│   │   │       └── chunks/
│   │   └── logs/
│   ├── templates/
│   │   ├── search_template.py
│   │   └── mcp_server_template.py
│   └── README.md
├── runtime/
│   ├── server.py          (Phase 5 will copy to servers/)
│   └── search.py          (Phase 5 will archive)
├── servers/
│   └── mojo-manual-mcp/
│       ├── config/
│       ├── runtime/       (Phase 5)
│       └── README.md      (Phase 5)
├── pixi.toml              (updated import paths)
└── [other project files]
```

#### Step 10: Test Before Committing

On feature branch, run verification tests to ensure structure is valid:

```bash
# 1. Check imports in new location
pixi run python -c "from shared.preprocessing.src.pipeline import main; print('✓ preprocessing imports OK')"
pixi run python -c "from shared.embedding.generate_embeddings import main; print('✓ embedding imports OK')"

# 2. Verify help commands work
pixi run python -m shared.preprocessing.src.pipeline --help
pixi run python shared/embedding/generate_embeddings.py --help
pixi run python shared/embedding/consolidate_data.py --help
pixi run python shared/embedding/load_to_ducklake.py --help
pixi run python shared/embedding/create_indexes.py --help

# 3. Verify pixi tasks reference new paths
pixi run mojo-process --help
pixi run mojo-embed --help
pixi run mojo-consolidate --help
pixi run mojo-load --help
pixi run mojo-index --help
```

#### Step 11: Commit Changes

Once all moves are complete and tests pass:

```bash
git add -A
git commit -m "refactor: Move build infrastructure to shared/ directory

- Move preprocessing/ to shared/preprocessing/
- Move embedding/ scripts to shared/embedding/
- Move processed_docs/ to shared/build/processed_docs/
- Move logs/ to shared/build/logs/
- Move search.py to shared/templates/search_template.py
- Copy server.py to shared/templates/mcp_server_template.py
- Create comprehensive shared/README.md documentation
- Update pixi.toml tasks to reference new shared/ paths
- Update import paths from preprocessing.* to shared.preprocessing.*
- Maintain .db and .ducklake files in root (distribute in Phase 5)

Benefits of this restructuring:
- Clear separation: dev tools in shared/, runtime in servers/
- Easier to add new MCP servers (copy templates, run build pipeline)
- Prepared for Phase 5 (server-specific organization)
- Build artifacts properly isolated in shared/build/

Phase: 4/8
Branch: restructure/04-move-build-infrastructure"
```

#### Step 12: Test on Persistent Testing Branch

After committing to feature branch:

```bash
# Verify changes locally
git log -1 --stat

# Switch to testing branch
git checkout test/restructure

# Merge feature branch into test branch
git merge restructure/04-move-build-infrastructure

# Ensure dependencies available (may already be cached)
pixi install

# Run full verification suite
pixi run python -m shared.preprocessing.src.pipeline --help
pixi run python shared/embedding/generate_embeddings.py --help
pixi run mojo-process --help
pixi run mojo-embed --help

# If all pass, merge to main
git checkout main
git merge restructure/04-move-build-infrastructure
```

#### Step 13: Merge to Main

```bash
git checkout main
git merge restructure/04-move-build-infrastructure -m "Merge Phase 4: Move build infrastructure to shared/"

# Verify clean merge
git log --oneline -3
```

### Verification Checklist

- [ ] Feature branch created: `restructure/04-move-build-infrastructure`
- [ ] `preprocessing/` moved to `shared/preprocessing/`
- [ ] `embedding/` scripts moved to `shared/embedding/`
- [ ] `processed_docs/` moved to `shared/build/processed_docs/`
- [ ] `logs/` moved to `shared/build/logs/`
- [ ] `search.py` moved to `shared/templates/search_template.py`
- [ ] `runtime/server.py` copied to `shared/templates/mcp_server_template.py`
- [ ] `shared/README.md` created with comprehensive documentation
- [ ] All import paths updated in Python files
- [ ] `pixi.toml` updated with new path references
  - [ ] `mojo-process` task updated to use `shared.preprocessing.src.pipeline`
  - [ ] `mojo-embed` task updated to use `shared/embedding/generate_embeddings.py`
  - [ ] `mojo-consolidate` task updated
  - [ ] `mojo-load` task updated
  - [ ] `mojo-index` task updated
- [ ] Directory structure matches expected layout (see "Verify Directory Structure" step)
- [ ] Test: `pixi run python -m shared.preprocessing.src.pipeline --help` works
- [ ] Test: `pixi run python shared/embedding/generate_embeddings.py --help` works
- [ ] Test: All embedding scripts have `--help` working
- [ ] Test: All pixi mojo-* tasks have `--help` working
- [ ] Test passes on persistent testing branch `test/restructure`
- [ ] Changes committed on feature branch with clear message
- [ ] Feature branch merged to main without conflicts
- [ ] Git history clean: `git log --oneline -3` shows merge commit

### Success Criteria

- Build infrastructure consolidated in `/shared/`
- All import paths updated and verified working
- Pixi tasks reference new locations correctly
- All `--help` commands work across pipeline
- Persistent testing branch `test/restructure` used for verification
- Feature branch successfully merged to main
- Directory structure ready for Phase 5 server organization

### Important Notes

#### About Database Files
- `main.db` and `mojo_catalog.ducklake*` stay in project root during Phase 4
- They will move to `servers/mojo-manual-mcp/runtime/` in Phase 5
- Do NOT ignore these files in `.gitignore` (they are essential)

#### About `test/restructure` Branch
- This is a **persistent** testing branch created in Phase 3
- Do **NOT** delete it
- Use it for testing ALL remaining phases (4-8)
- It has all dependencies pre-installed from Phase 3
- Reuse by merging feature branches into it for verification

#### Backward Compatibility
- Old import paths (`from preprocessing.src import ...`) will no longer work
- This is intentional - Phase 4 is a breaking restructuring
- All references updated in this phase
- Next phases build on this new structure

#### Performance Note
- Directory moves are fast (no data processing)
- All previous build artifacts can be regenerated
- If something breaks, can always reset with: `git reset --hard HEAD~1`

### Architecture After Phase 4

```
Project Root (/home/james/mcp/)
│
├── shared/                     ← Dev-time build infrastructure
│   ├── preprocessing/          ← Doc processing tools
│   ├── embedding/              ← Embedding generation
│   ├── build/                  ← Build artifacts (ephemeral)
│   └── templates/              ← Reusable templates
│
├── servers/                    ← Distributable server packages
│   └── mojo-manual-mcp/        ← Individual MCP servers
│       ├── config/
│       └── runtime/            ← Runtime code (Phase 5)
│
├── runtime/                    ← Legacy (kept for reference, will deprecate Phase 5)
├── pixi.toml                   ← Build task definitions
├── main.db                     ← Searchable index (Phase 5 moves this)
└── [other files]
```

---

## Next Phase

**Phase 5**: Organize Mojo MCP Server as Standalone Module
- Move indexes to `servers/mojo-manual-mcp/runtime/`
- Create server-specific README and configuration
- Update imports to be relative to server directory
- Prepare for non-pixi deployment (Phase 5 also introduces pip + venv setup)

---

## Git Workflow Summary for Next Session

**Key Commands**:
```bash
# Start
git checkout main && git pull
git checkout -b restructure/04-move-build-infrastructure

# Work (move files, update paths)
git add -A
git commit -m "refactor: Move build infrastructure to shared/ directory"

# Test
git checkout test/restructure
git merge restructure/04-move-build-infrastructure
pixi run <verification_commands>

# Merge to production
git checkout main
git merge restructure/04-move-build-infrastructure
```

**Remember**: 
- `test/restructure` is persistent (do NOT delete)
- All `pixi run` commands require pixi environment
- Database files (`.db`, `.ducklake`) are tracked and important
- If tests fail, reset with `git reset --hard HEAD~1` and investigate
