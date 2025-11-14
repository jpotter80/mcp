# Phase 3 Execution Guide: Parameterize Build Pipeline

**For Next Session's AI Model**

## Quick Reference: Current State Summary

### ✅ What's Already Done
- **Phase 1**: Directory structure, `.gitignore`, config templates — COMPLETE
- **Phase 2**: Multi-format document processor support — COMPLETE
- **Foundation**: `ProcessorFactory`, `BaseDocumentProcessor`, `config_loader.py` all exist and working
- **Mojo Server**: Config files (`processing_config.yaml`, `server_config.yaml`) exist and parameterized

### 🎯 What Phase 3 Does
Parameterizes the embedding pipeline scripts so they can be:
1. Moved to `/shared/embedding/`
2. Called with `--mcp-name` argument (e.g., `mojo`, `duckdb`)
3. Called with `--config` argument pointing to YAML config file
4. Updated to use `config_loader.py` for path resolution with `${SERVER_ROOT}` and `${PROJECT_ROOT}` substitution

### 📊 Phase 3 Scope (Estimated 1-1.5 hours)

| File | Current Location | Action | Status |
|------|------------------|--------|--------|
| `generate_embeddings.py` | `/embedding/` | Add CLI args, use config_loader | Not started |
| `consolidate_data.py` | `/embedding/` | Add CLI args, parameterize paths | Not started |
| `load_to_ducklake.py` | `/embedding/` | Add CLI args, parameterize catalog names | Not started |
| `create_indexes.py` | `/embedding/` | Add CLI args, parameterize DB/table names | Not started |
| `pixi.toml` | Root | Update task definitions | Not started |
| `/shared/embedding/README.md` | New | Document the scripts | Not started |

---

## Architecture Review: Is It Sound?

### Project Vision Confirmed ✅
- **Dual Distribution Model**:
  - Full repo (GitHub): developers can adapt pipeline to their docs
  - Individual servers (GitHub): self-contained for end users
- **Self-Contained Servers**: Each `/servers/{mcp-name}/` has everything needed to run independently
- **Shared Build Infrastructure**: `/shared/` is for development only, not distributed with individual servers
- **Parameterization**: All configuration via YAML, path resolution via variable substitution

### Design Decisions Confirmed ✅
1. **Pluggable Processors**: Support multiple doc formats (MDX, Markdown, etc.)
2. **Config-Driven**: All paths, chunking params, embedding settings in YAML
3. **CLI Arguments**: Scripts accept `--mcp-name` and `--config` for flexibility
4. **Path Resolution**: Use `${SERVER_ROOT}` and `${PROJECT_ROOT}` for portability

### No Corruption Detected ✅
- Phase 1 implementation is correct and complete
- Phase 2 implementation is correct and complete
- No files have been lost or misplaced
- `.gitignore` is properly configured (only ignores ephemeral artifacts)
- All source code is tracked in git

**Conclusion**: The path forward is safe. Proceed with Phase 3.

---

## Phase 3 Implementation Checklist

### Step 1: Parameterize Embedding Scripts

Each script needs the same pattern:

#### Template for CLI Argument Addition:
```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument(
        "--mcp-name",
        default="mojo",
        help="MCP server name (e.g., 'mojo', 'duckdb')"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to processing_config.yaml or server_config.yaml"
    )
    args = parser.parse_args()
    
    # Load config using config_loader
    from shared.preprocessing.src.config_loader import load_config_with_substitution
    config = load_config_with_substitution(args.config)
    
    # Use config to determine paths
    # Example: output_dir = config["output"]["base_directory"]
```

#### Scripts to Update:

1. **`/embedding/generate_embeddings.py`**
   - Add `--mcp-name` (default: "mojo")
   - Add `--config` (required or use default)
   - Change: `INPUT_DIR = f"shared/build/processed_docs/{mcp_name}/chunks"`
   - Change: `OUTPUT_DIR = f"shared/build/embeddings/{mcp_name}"`
   - Use config_loader for variable substitution

2. **`/embedding/consolidate_data.py`**
   - Add `--mcp-name` (default: "mojo")
   - Change: `CHUNKS_DIR = f"shared/build/processed_docs/{mcp_name}/chunks"`
   - Change: `EMBEDDINGS_DIR = f"shared/build/embeddings/{mcp_name}"`
   - Change: `OUTPUT_FILE = f"shared/build/{mcp_name}_embeddings.parquet"`

3. **`/embedding/load_to_ducklake.py`**
   - Add `--mcp-name` (default: "mojo")
   - Change: `PARQUET_PATH = f"shared/build/{mcp_name}_embeddings.parquet"`
   - Change: `DUCKLAKE_CATALOG_PATH = f"servers/{mcp_name}-manual-mcp/runtime/{mcp_name}_catalog.ducklake"`
   - Change: `DUCKLAKE_TABLE_NAME = f"{mcp_name}_docs"`

4. **`/embedding/create_indexes.py`**
   - Add `--mcp-name` (default: "mojo")
   - Change: `DUCKLAKE_CATALOG_PATH = f"servers/{mcp_name}-manual-mcp/runtime/{mcp_name}_catalog.ducklake"`
   - Change: `MAIN_DB_PATH = f"servers/{mcp_name}-manual-mcp/runtime/{mcp_name}_manual_mcp.db"`
   - Change: `INDEXED_TABLE_NAME = f"{mcp_name}_docs_indexed"`

### Step 2: Update Root `pixi.toml`

Current tasks reference `/embedding/` and `/preprocessing/` directly. Update to use new parameterized task definitions:

```toml
[tasks]
# Remove old generic tasks, keep them as examples but comment out

# Mojo-specific build tasks (these should work)
mojo-process = "python -m preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-generate-embeddings = "python embedding/generate_embeddings.py --mcp-name mojo --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-consolidate = "python embedding/consolidate_data.py --mcp-name mojo"
mojo-load = "python embedding/load_to_ducklake.py --mcp-name mojo"
mojo-index = "python embedding/create_indexes.py --mcp-name mojo"

# Convenience: build all mojo tasks in sequence
mojo-build = """
pixi run mojo-process && \
pixi run mojo-generate-embeddings && \
pixi run mojo-consolidate && \
pixi run mojo-load && \
pixi run mojo-index
"""

# Demonstration: generic tasks (with explicit mcp-name)
process = "python -m preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml --mcp-name mojo"
generate-embeddings = "python embedding/generate_embeddings.py --mcp-name mojo"
```

### Step 3: Create `/shared/embedding/README.md`

Document:
- What each script does
- How to use with `--mcp-name` and `--config` arguments
- Example commands
- Configuration requirements

### Step 4: Testing Phase 3

Before merging:
```bash
# Test that parameterized tasks work
pixi run mojo-process  # Should work with existing config
pixi run mojo-generate-embeddings  # Should read config and find correct paths
pixi run mojo-consolidate
pixi run mojo-load
pixi run mojo-index

# Test that help messages show new arguments
python embedding/generate_embeddings.py --help
python embedding/consolidate_data.py --help
python embedding/load_to_ducklake.py --help
python embedding/create_indexes.py --help
```

### Step 5: Git Operations

```bash
# Create testing branch from main
git checkout -b test/restructure

# Create feature branch for Phase 3
git checkout -b restructure/03-parameterize-build-scripts

# Make changes to embedding scripts and pixi.toml

# Test thoroughly

# Commit with clear message:
git commit -m "feat: Parameterize all embedding pipeline scripts

- Add --mcp-name argument to all embedding scripts
- Add --config argument for configuration file paths
- Integrate config_loader for variable substitution
- Scripts now support dynamic paths: shared/build/processed_docs/{mcp_name}
- Update pixi.toml with parameterized tasks (mojo-generate-embeddings, etc.)
- Each script can now serve multiple MCP servers
- Example: python embedding/generate_embeddings.py --mcp-name duckdb --config servers/duckdb-docs-mcp/config/processing_config.yaml"

# Merge to main
git checkout main
git merge restructure/03-parameterize-build-scripts
```

---

## What NOT to Do

❌ **Do NOT**:
- Delete `/preprocessing/` from root yet (Phase 4 does this)
- Delete `/embedding/` from root yet (Phase 4 does this)
- Move database files (Phase 5 does this)
- Create new MCP servers yet (we only have Mojo, more come later)
- Modify test data or restructure docs folders (only Python scripts and config)

---

## Key Files Reference

### Files That Should Exist and Work

- ✅ `/shared/preprocessing/src/config_loader.py` — Load YAML with variable substitution
- ✅ `/shared/preprocessing/src/processor_factory.py` — Select processor by format
- ✅ `/shared/preprocessing/src/base_processor.py` — Abstract base class
- ✅ `/shared/preprocessing/src/pipeline.py` — Main orchestrator (may need `--config` support)
- ✅ `/servers/mojo-manual-mcp/config/processing_config.yaml` — Mojo processing config
- ✅ `/servers/mojo-manual-mcp/config/server_config.yaml` — Mojo server config

### Files to Modify

- 🔄 `/embedding/generate_embeddings.py` — Add CLI args
- 🔄 `/embedding/consolidate_data.py` — Add CLI args
- 🔄 `/embedding/load_to_ducklake.py` — Add CLI args
- 🔄 `/embedding/create_indexes.py` — Add CLI args
- 🔄 `/pixi.toml` — Update task definitions

### Files to Create

- 📝 `/shared/embedding/README.md` — Document the scripts

---

## Expected Outcome After Phase 3

1. All embedding scripts accept `--mcp-name` and `--config` arguments
2. Scripts resolve paths using config_loader with variable substitution
3. Root `pixi.toml` has parameterized tasks
4. Can run `pixi run mojo-process`, `pixi run mojo-generate-embeddings`, etc.
5. Ready to support multiple MCP servers (currently just Mojo)
6. All source code properly tracked in git
7. No files lost or corrupted

---

## If Issues Arise

### Debugging Path Resolution
Enable debug logging in config_loader:
```python
# In config_loader.py, add debug print:
print(f"Substituting {var_name} with {final_value}")
```

### Testing Config Loading
```bash
python -c "
from pathlib import Path
from shared.preprocessing.src.config_loader import load_config_with_substitution
config = load_config_with_substitution('servers/mojo-manual-mcp/config/processing_config.yaml')
print(config)
"
```

### If Paths Don't Resolve
Check:
1. Is `config_loader.py` being imported correctly?
2. Are `${SERVER_ROOT}` and `${PROJECT_ROOT}` defined in config?
3. Do config files exist at specified paths?

### Rollback Strategy
If Phase 3 fails:
```bash
git reset --hard test/restructure
git branch -D restructure/03-parameterize-build-scripts
# Start over
```

---

## Success Criteria

✅ Phase 3 is complete when:

1. **All 4 embedding scripts** accept `--mcp-name` and `--config` arguments
2. **Scripts use config_loader** for path resolution with variable substitution
3. **pixi.toml** has parameterized task definitions that work
4. **Testing**: Can run:
   ```bash
   pixi run mojo-process
   pixi run mojo-generate-embeddings
   pixi run mojo-consolidate
   pixi run mojo-load
   pixi run mojo-index
   ```
5. **All changes** tracked in git on `restructure/03-parameterize-build-scripts` branch
6. **No files lost** or accidentally deleted
7. **Documentation** (README.md) in `/shared/embedding/` explains the scripts

---

## Next Steps After Phase 3

Once Phase 3 is merged to main:

1. **Phase 4**: Move embedding scripts to `/shared/embedding/`, move preprocessing to `/shared/preprocessing/`
2. **Phase 5**: Organize Mojo MCP server structure in `/servers/mojo-manual-mcp/`
3. **Phase 6**: Create automation tooling (`build_all.sh`, `scaffold_new_mcp.sh`, etc.)
4. **Phase 7**: Update documentation and README files
5. **Phase 8**: Final cleanup and validation

---

## Important Notes

### Git History is Clean
- Phases 1-2 are in main branch
- No corruption detected
- Safe to continue

### No Superfluous Files
- Do NOT create intermediate summary documents
- Do NOT commit generated artifacts (only source code)
- Keep commits focused and minimal

### Testing Branch Strategy
- Use `test/restructure` as persistent testing branch for all phases
- Feature branches: `restructure/03-...`, `restructure/04-...`, etc.
- Merge feature branches to main after passing tests
- Keep `test/restructure` updated alongside main

---

## Files to Review Before Starting

1. `/shared/preprocessing/src/config_loader.py` — How variable substitution works
2. `/servers/mojo-manual-mcp/config/processing_config.yaml` — Example of parameterized config
3. `/embedding/generate_embeddings.py` — Example of script that needs parameterization
4. Root `/pixi.toml` — Current task definitions

---

## Questions to Answer Before Proceeding

1. **Are all embedding scripts at `/embedding/` and do they have the same hardcoded paths?**
   - Yes, verified: generate_embeddings.py, consolidate_data.py, load_to_ducklake.py, create_indexes.py

2. **Does config_loader.py exist and does it support variable substitution?**
   - Yes, verified: `/shared/preprocessing/src/config_loader.py` exists and works

3. **Are the config files (processing_config.yaml, server_config.yaml) complete and valid?**
   - Yes, verified: Both exist in `/servers/mojo-manual-mcp/config/` and are well-formed

4. **Can scripts import config_loader from the right location?**
   - Yes, verified: All scripts are at root, can import from `shared.preprocessing.src.config_loader`

5. **Is pixi.toml ready for updates?**
   - Yes, verified: Current tasks are simple and can be enhanced

---

## Success Story

After Phase 3 completes successfully, you'll be able to:

```bash
# Build the Mojo MCP with one command
pixi run mojo-build

# Or build step-by-step
pixi run mojo-process
pixi run mojo-generate-embeddings
pixi run mojo-consolidate
pixi run mojo-load
pixi run mojo-index

# Support for other MCPs is now trivial - just add new mcp-* tasks
```

This sets up the foundation for supporting multiple MCP servers while keeping the codebase DRY (Don't Repeat Yourself).

