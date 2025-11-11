# Phase 3 Implementation Prompt for Next Session

## Context
The MCP project restructuring is proceeding with Phase 3. Phase 2 (pluggable multi-format document processor architecture) has been completed and merged to main. Phase 3 implements parameterized build scripts that support multiple MCP servers with dynamic configuration.

## Current State
- Main branch has Phase 1 and Phase 2 changes merged
- Multi-format processor architecture in place
- Build scripts still use hardcoded paths
- Ready to parameterize build pipeline

## Task: Execute Phase 3

### Objective
Parameterize all build pipeline scripts to support arbitrary MCP servers. Replace hardcoded paths with configuration-driven approach. Enable `--config` and `--mcp-name` arguments for all build stages.

### Branch
`restructure/03-parameterize-build-scripts`

### Instructions to Follow
1. Reference: `/home/james/mcp/RESTRUCTURING_PLAN.md` (lines 563-620, "Phase 3: Parameterize Build Pipeline" section)
2. Execute all steps in sequence:
   - Create feature branch
   - Create config_loader.py utility for variable substitution
   - Update preprocessing pipeline to accept --config argument
   - Update all embedding scripts with --mcp-name argument
   - Update root pixi.toml with new parameterized tasks
   - Verify all scripts accept arguments correctly
   - Commit with clear Phase 3 message
   - Merge to main

### Key Files to Create
- `shared/preprocessing/src/config_loader.py` — YAML config loader with variable substitution

### Key Files to Modify
- `shared/preprocessing/src/pipeline.py` — Add --config CLI argument
- `shared/embedding/generate_embeddings.py` — Add --mcp-name and --config arguments
- `shared/embedding/consolidate_data.py` — Add --mcp-name argument
- `shared/embedding/load_to_ducklake.py` — Add --mcp-name argument
- `shared/embedding/create_indexes.py` — Add --mcp-name argument
- `/home/james/mcp/pixi.toml` — Add parameterized task definitions

### Implementation Details

#### Step 1: Create Feature Branch
```bash
cd /home/james/mcp
git checkout main
git pull
git checkout -b restructure/03-parameterize-build-scripts
```

#### Step 2: Create config_loader.py
Location: `shared/preprocessing/src/config_loader.py`

Create utility with:
- `load_config_with_substitution(config_path: str, server_root: Path = None) -> Dict`
- Support `${SERVER_ROOT}` and `${PROJECT_ROOT}` variable substitution in config values
- Handle missing environment variables gracefully
- Return fully resolved configuration dictionary

Features:
- Parse YAML config file
- Recursively walk config dict for ${VAR} patterns
- Replace with environment variables or defaults
- Validate paths exist after substitution

Example substitutions:
```yaml
output:
  base_directory: "${SERVER_ROOT}/processed_docs"
  # Becomes: /home/james/mcp/servers/mojo-manual-mcp/processed_docs
```

#### Step 3: Update preprocessing pipeline
Location: `shared/preprocessing/src/pipeline.py`

Changes:
- Add argparse support with `--config` argument
- Load config using config_loader (instead of hardcoded path)
- Make `config_path` parameter optional (use CLI arg if provided)
- Example: `python -m shared.preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml`
- Default to `preprocessing/config/processing_config.yaml` if --config not provided (backward compatibility)

#### Step 4: Update embedding scripts
Update all scripts in `shared/embedding/`:

**generate_embeddings.py**:
- Add `--mcp-name` argument (e.g., "mojo")
- Add `--config` argument (path to config file)
- Use config to find embeddings output directory
- Store embeddings in `processed_docs/embeddings/{mcp_name}_embeddings.jsonl`

**consolidate_data.py**:
- Add `--mcp-name` argument
- Use for output parquet naming: `processed_docs/{mcp_name}_embeddings.parquet`
- Load embeddings from correct source based on mcp_name

**load_to_ducklake.py**:
- Add `--mcp-name` argument
- Use for catalog and table naming: `{mcp_name}_docs` table in catalog
- Create versioned DuckLake table

**create_indexes.py**:
- Add `--mcp-name` argument
- Generate database name: `{mcp_name}_docs.db`
- Create indexed table: `{mcp_name}_docs_indexed`

#### Step 5: Verify CLI Arguments
All scripts should support:
```bash
# Preprocessing
python -m shared.preprocessing.src.pipeline --config <config_path>

# Embeddings
python shared/embedding/generate_embeddings.py --mcp-name <name> --config <config_path>
python shared/embedding/consolidate_data.py --mcp-name <name>
python shared/embedding/load_to_ducklake.py --mcp-name <name>
python shared/embedding/create_indexes.py --mcp-name <name>
```

#### Step 6: Update root pixi.toml
Add to `[tasks]` section:
```toml
# Mojo build pipeline (example)
mojo-process = "python -m shared.preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-embed = "python shared/embedding/generate_embeddings.py --mcp-name mojo --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-consolidate = "python shared/embedding/consolidate_data.py --mcp-name mojo"
mojo-load = "python shared/embedding/load_to_ducklake.py --mcp-name mojo"
mojo-index = "python shared/embedding/create_indexes.py --mcp-name mojo"
```

Keep existing tasks for backward compatibility, but mark as deprecated.

#### Step 7: Test & Verification
Run basic argument parsing tests:
```bash
pixi run python -m shared.preprocessing.src.pipeline --help
pixi run python shared/embedding/generate_embeddings.py --help
pixi run python shared/embedding/consolidate_data.py --help
pixi run python shared/embedding/load_to_ducklake.py --help
pixi run python shared/embedding/create_indexes.py --help
```

Verify:
- All scripts accept --help and show usage
- --config argument works with valid config file
- --mcp-name argument affects output paths/names
- Script fails gracefully with missing arguments

#### Step 8: Commit Changes
```bash
git add -A
git commit -m "refactor: Parameterize all build pipeline scripts

- Create config_loader.py with variable substitution support
- Add --config argument to preprocessing pipeline
- Add --mcp-name argument to all embedding scripts
- Support \${SERVER_ROOT} and \${PROJECT_ROOT} in YAML configs
- Update root pixi.toml with new parameterized task definitions
- Build pipeline now supports arbitrary MCP servers
- All paths now config-driven instead of hardcoded

Variable substitution enables portable configurations that work
across different installation directories and server setups.

Phase: 3/8
Branch: restructure/03-parameterize-build-scripts"
```

#### Step 9: Merge to Main
```bash
git checkout main
git merge restructure/03-parameterize-build-scripts -m "Merge Phase 3: Parameterized build pipeline scripts"
```

### Verification Checklist
- [ ] config_loader.py created with variable substitution
- [ ] config_loader supports ${SERVER_ROOT} and ${PROJECT_ROOT}
- [ ] pipeline.py accepts --config argument
- [ ] All embedding scripts accept --mcp-name argument
- [ ] generate_embeddings.py accepts --config argument
- [ ] All scripts have --help support
- [ ] pixi.toml has new mojo-* task definitions
- [ ] Test: `python -m shared.preprocessing.src.pipeline --help` works
- [ ] Test: `python shared/embedding/generate_embeddings.py --help` works
- [ ] Test: All scripts fail gracefully with missing required args
- [ ] Git branch is clean and ready to merge
- [ ] All changes committed locally
- [ ] Merged successfully to main branch

### Success Criteria
- config_loader.py implemented and working
- All build scripts accept required CLI arguments
- Variable substitution in configs working correctly
- New pixi tasks added and functional
- No breaking changes to existing functionality
- Single logical commit with clear message
- Changes merged to main

### Key Design Patterns
- **Configuration-Driven**: All paths and settings from YAML, not hardcoded
- **Variable Substitution**: Support for ${VAR} patterns in config values
- **CLI Arguments**: Flexible argument passing for different scenarios
- **Backward Compatibility**: Old hardcoded paths still work as defaults

### Important Implementation Notes
- Use argparse module for CLI argument parsing
- config_loader should be imported by all scripts
- Support both relative and absolute paths in configs
- Environment variable fallback for ${VAR} substitution
- Graceful error handling for missing config files

### Resources
- RESTRUCTURING_PLAN.md (lines 563-620) — Detailed Phase 3 specification
- Existing embedding scripts in `shared/embedding/`
- Phase 2 implementation for reference patterns

### If Issues Arise
- **argparse errors**: Ensure all args use standard conventions
- **Config not found**: Add helpful error messages with expected paths
- **Variable substitution fails**: Check ${VAR} format and provide clear errors
- **Task definition syntax**: Verify pixi.toml toml syntax (quotes, escapes)

### Architecture Note
This phase prepares configuration-driven builds for multiple documentation sources. Each server will have its own config file with variable substitution, enabling portable builds. Phase 4 will move build infrastructure to shared/ location, and Phase 5 will organize individual MCP servers.

---

**Start with**: `git checkout -b restructure/03-parameterize-build-scripts`

**Follow**: Implementation steps 1-9 above in order

**Complete when**: All changes merged to main branch and all --help commands work
