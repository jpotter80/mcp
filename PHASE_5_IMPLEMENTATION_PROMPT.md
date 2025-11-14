# Phase 5 Execution Guide: Move Build Infrastructure to Shared
For Next Session's AI Model

## Quick Phase 4 Recap (Current State)

As of `restructure/04-config-loader-integration` (now merged to `main`):

- **Config loader working**: `shared/config_loader.py` properly substitutes `${PROJECT_ROOT}` and `${SERVER_ROOT}` variables
- **Preprocessing pipeline updated**: `preprocessing/src/pipeline.py` now uses `load_config_with_substitution()` 
- **Processing config updated**: `servers/mojo-manual-mcp/config/processing_config.yaml` uses `${PROJECT_ROOT}` for both source and output paths
- **Verification passed**: `pixi run mojo-process` successfully processes 45 docs with correct output paths (`/home/james/mcp/shared/build/processed_docs/mojo`)
- **No literal variables**: No `${PROJECT_ROOT}` directories created; all variables properly resolved

Key files changed in Phase 4:
- `shared/config_loader.py` — Moved from `shared/preprocessing/src/` to avoid import conflicts
- `preprocessing/src/pipeline.py` — Imports and uses `load_config_with_substitution()`
- `servers/mojo-manual-mcp/config/processing_config.yaml` — Uses `${PROJECT_ROOT}` for source directory

## Goal of Phase 5: Move Build Infrastructure to Shared

Consolidate all build-time infrastructure into `/shared/` directory to prepare for self-contained server distribution:

1. Move `/embedding/*.py` scripts to `/shared/embedding/`
2. Move `/preprocessing/` directory to `/shared/preprocessing/` (complete the partial migration)
3. Update all import paths and references
4. Update `pixi.toml` task definitions to use new paths
5. Clean up old locations

**Important**: This is purely a reorganization phase. All functionality should remain identical.

## Phase 5 Objectives

1. **Complete the preprocessing migration**:
   - The preprocessing code exists in both root `/preprocessing/` and `/shared/preprocessing/`
   - Move everything from `/preprocessing/` to `/shared/preprocessing/`
   - Remove old `/preprocessing/` directory

2. **Move embedding scripts**:
   - Move all scripts from `/embedding/*.py` to `/shared/embedding/`
   - Scripts are already parameterized from Phase 3
   - Preserve all CLI arguments and functionality

3. **Update imports and paths**:
   - Update any remaining imports that reference old locations
   - Verify no hardcoded paths reference old structure

4. **Update pixi.toml tasks**:
   - Change task commands to reference new script locations
   - Preserve all Phase 3 parameterization

5. **Verification**:
   - Run full build pipeline on `test/restructure` branch
   - Confirm all tasks work: `mojo-process`, `mojo-generate-embeddings`, `mojo-consolidate`, `mojo-load`, `mojo-index`

## Files and Components Involved

### Current Structure (Before Phase 5)

```
/home/james/mcp/
├── preprocessing/                  # OLD: Still exists at root
│   ├── src/
│   │   ├── pipeline.py
│   │   ├── mdx_processor.py
│   │   ├── chunker.py
│   │   ├── metadata_extractor.py
│   │   └── utils.py
│   └── config/
│       └── processing_config.yaml
│
├── embedding/                      # OLD: At root, needs to move
│   ├── generate_embeddings.py
│   ├── consolidate_data.py
│   ├── load_to_ducklake.py
│   ├── create_indexes.py
│   └── README.md
│
├── shared/
│   ├── config_loader.py           # NEW: From Phase 4
│   ├── preprocessing/              # PARTIAL: Some files here
│   │   └── src/
│   │       ├── base_processor.py
│   │       ├── markdown_processor.py
│   │       ├── mdx_processor.py
│   │       └── processor_factory.py
│   └── embedding/                  # Empty, needs scripts
```

### Target Structure (After Phase 5)

```
/home/james/mcp/
├── shared/                         # All build infrastructure here
│   ├── config_loader.py
│   │
│   ├── preprocessing/              # Complete preprocessing module
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py        # Moved from /preprocessing/src/
│   │   │   ├── base_processor.py
│   │   │   ├── mdx_processor.py
│   │   │   ├── markdown_processor.py
│   │   │   ├── processor_factory.py
│   │   │   ├── chunker.py         # Moved from /preprocessing/src/
│   │   │   ├── metadata_extractor.py  # Moved from /preprocessing/src/
│   │   │   └── utils.py           # Moved from /preprocessing/src/
│   │   ├── config/
│   │   │   └── processing_config.yaml  # Default/template config
│   │   └── README.md
│   │
│   ├── embedding/                  # Complete embedding module
│   │   ├── generate_embeddings.py # Moved from /embedding/
│   │   ├── consolidate_data.py    # Moved from /embedding/
│   │   ├── load_to_ducklake.py    # Moved from /embedding/
│   │   ├── create_indexes.py      # Moved from /embedding/
│   │   └── README.md              # Moved from /embedding/
│   │
│   └── build/                      # Generated artifacts (ephemeral)
│       ├── processed_docs/
│       └── embeddings/
│
├── servers/
│   └── mojo-manual-mcp/
│       └── config/
│           └── processing_config.yaml  # Server-specific config
│
└── pixi.toml                       # Updated task paths
```

## Step-by-Step Tasks

### Task 1: Move Preprocessing Module Completely

**1.1 Move remaining preprocessing files**

The files that need to be moved from `/preprocessing/src/` to `/shared/preprocessing/src/`:
- `pipeline.py`
- `chunker.py`
- `metadata_extractor.py`
- `utils.py`
- `__init__.py` (if exists at root preprocessing)

```bash
# On feature branch restructure/05-move-build-infrastructure
cd /home/james/mcp
mv preprocessing/src/pipeline.py shared/preprocessing/src/
mv preprocessing/src/chunker.py shared/preprocessing/src/
mv preprocessing/src/metadata_extractor.py shared/preprocessing/src/
mv preprocessing/src/utils.py shared/preprocessing/src/
```

**1.2 Update imports in moved files**

After moving, update imports that reference relative paths. For example, in `shared/preprocessing/src/pipeline.py`:

Change:
```python
from .utils import (...)
from .chunker import (...)
```

These should remain the same since they're still using relative imports within the same package.

But check for any imports that reference `preprocessing.src.*` and update to just use relative imports.

**1.3 Move config directory**

```bash
mv preprocessing/config shared/preprocessing/
```

**1.4 Remove old preprocessing directory**

```bash
rm -rf preprocessing/
```

### Task 2: Move Embedding Scripts

**2.1 Move all embedding scripts**

```bash
cd /home/james/mcp
mv embedding/generate_embeddings.py shared/embedding/
mv embedding/consolidate_data.py shared/embedding/
mv embedding/load_to_ducklake.py shared/embedding/
mv embedding/create_indexes.py shared/embedding/
mv embedding/README.md shared/embedding/
```

**2.2 Add __init__.py to shared/embedding**

Create `shared/embedding/__init__.py`:
```python
"""
Shared embedding module for generating and managing embeddings.
"""

__all__ = [
    "generate_embeddings",
    "consolidate_data",
    "load_to_ducklake",
    "create_indexes",
]
```

**2.3 Remove old embedding directory**

```bash
rm -rf embedding/
```

### Task 3: Update pixi.toml Task Definitions

Update all task commands in `pixi.toml` to reference new script locations.

**Current tasks** (as of Phase 4):
```toml
[tasks]
mojo-process = "python -m preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-generate-embeddings = "python embedding/generate_embeddings.py --mcp-name mojo"
mojo-consolidate = "python embedding/consolidate_data.py --mcp-name mojo"
mojo-load = "python embedding/load_to_ducklake.py --mcp-name mojo"
mojo-index = "python embedding/create_indexes.py --mcp-name mojo"
```

**Updated tasks** (Phase 5):
```toml
[tasks]
mojo-process = "python -m shared.preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-generate-embeddings = "python shared/embedding/generate_embeddings.py --mcp-name mojo"
mojo-consolidate = "python shared/embedding/consolidate_data.py --mcp-name mojo"
mojo-load = "python shared/embedding/load_to_ducklake.py --mcp-name mojo"
mojo-index = "python shared/embedding/create_indexes.py --mcp-name mojo"
```

### Task 4: Update Any Remaining Import References

**4.1 Search for old import paths**

Search the codebase for any remaining references to old paths:
```bash
grep -r "from preprocessing" --include="*.py"
grep -r "import preprocessing" --include="*.py"
grep -r "from embedding" --include="*.py"
grep -r "import embedding" --include="*.py"
```

**4.2 Update found references**

Update any found references to use new paths:
- `from preprocessing.src.X` → `from shared.preprocessing.src.X`
- `import preprocessing.src.X` → `import shared.preprocessing.src.X`
- `from embedding.X` → `from shared.embedding.X`

### Task 5: Verify on Testing Branch

**5.1 Switch to testing branch and merge**

```bash
git checkout test/restructure
git merge restructure/05-move-build-infrastructure --no-edit
```

**5.2 Run full pipeline verification**

```bash
# Test preprocessing
pixi run mojo-process

# Test embeddings generation
pixi run mojo-generate-embeddings

# Test consolidation
pixi run mojo-consolidate

# Test DuckLake load
pixi run mojo-load

# Test indexing
pixi run mojo-index

# Or run full pipeline
pixi run mojo-build
```

**5.3 Verify outputs**

Check that all outputs are in expected locations:
- Processed docs: `shared/build/processed_docs/mojo/`
- Embeddings: `shared/build/embeddings/mojo/`
- Database: `servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db`
- Catalog: `servers/mojo-manual-mcp/runtime/mojo_catalog.ducklake`

## Out of Scope for Phase 5

Do not:
- Change any script functionality or logic
- Modify CLI arguments (already done in Phase 3)
- Change config file structure or variables
- Move server-specific files
- Modify search.py or server.py (that's Phase 6)

## Success Criteria for Phase 5

Phase 5 is complete when:

1. ✅ All preprocessing code is in `/shared/preprocessing/`
2. ✅ All embedding scripts are in `/shared/embedding/`
3. ✅ Old `/preprocessing/` and `/embedding/` directories removed
4. ✅ All `pixi.toml` tasks updated with new paths
5. ✅ All imports updated to reference new locations
6. ✅ Full pipeline runs successfully on `test/restructure`:
   - `pixi run mojo-process` — 45 docs, 1155 chunks
   - `pixi run mojo-generate-embeddings` — Generates embeddings
   - `pixi run mojo-consolidate` — Creates parquet file
   - `pixi run mojo-load` — Loads to DuckLake
   - `pixi run mojo-index` — Creates indexed database
7. ✅ No behavior regressions or errors

## Development Workflow Reminder

**CRITICAL**: 
- Make all changes on feature branch `restructure/05-move-build-infrastructure`
- **NEVER test on feature branch directly**
- **ALWAYS switch to `test/restructure` for testing**
- Switch back to feature branch for fixes if needed
- Ask user to provide terminal output if not visible

## Notes for the Next Model

1. This is primarily a file reorganization phase — no logic changes
2. The key challenge is updating all import paths consistently
3. Phase 3 already parameterized the scripts, so no CLI changes needed
4. Phase 4 already wired the config loader, so variable substitution works
5. After Phase 5, all build infrastructure will be cleanly separated in `/shared/`
6. This sets up Phase 6 (organize Mojo server structure) to move runtime files
