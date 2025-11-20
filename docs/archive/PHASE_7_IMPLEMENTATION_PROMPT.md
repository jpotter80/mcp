# Phase 7 Execution Guide: Tooling & Automation
For Next Session's AI Model

## Quick Phase 6 Recap (Current State)

As of `feature/phase-6-server-structure` (now merged to `main`):

- **Mojo Server Organized**: All runtime files in `/servers/mojo-manual-mcp/runtime/`
- **Root Cleanup**: Old artifacts (`main.db`, `search.py`, etc.) removed from root
- **Configuration Updated**: Server uses `config_loader` and correct paths
- **Verification**: Search functionality verified with MAX server, linting errors fixed
- **Documentation**: `.memory.md` and `IMPLEMENTATION_SUMMARY.md` updated

Key accomplishments in Phase 6:
- Established the standard server structure
- Cleaned up the project root
- Verified the self-contained nature of the Mojo server

## Goal of Phase 7: Create Tooling & Automation

Create the necessary scripts and tools to manage the multi-server architecture, automate documentation updates, and simplify the creation of new MCP servers.

1. Create `tools/sync_documentation.sh` for upstream doc syncing
2. Create `tools/scaffold_new_mcp.sh` for generating new server structures
3. Create `tools/build_mcp.sh` for building specific MCP servers
4. Document the usage of these tools

**Important**: This phase focuses on developer experience and automation. These tools will make it easy to maintain existing servers and add new ones.

## Phase 7 Objectives

1. **Documentation Sync Tool (`tools/sync_documentation.sh`)**:
   - Script to clone/pull upstream documentation repositories
   - Configurable via arguments or config file
   - Support for sparse checkouts (if needed) to get only relevant docs

2. **Scaffolding Tool (`tools/scaffold_new_mcp.sh`)**:
   - Script to create a new server directory structure in `servers/`
   - Copies templates from `shared/templates/`
   - Generates initial configuration files
   - Sets up `requirements.txt` and `README.md`

3. **Build Tool (`tools/build_mcp.sh`)**:
   - Wrapper script to run the build pipeline for a specific MCP
   - Simplifies running the sequence: process -> embed -> consolidate -> load -> index
   - Handles `pixi run` commands or direct python execution

4. **Documentation**:
   - Create `tools/README.md` explaining how to use these scripts
   - Update main `README.md` with references to these tools

## Files and Components Involved

### Current Structure (After Phase 6)

```
/home/james/mcp/
├── shared/
│   ├── templates/                  # Templates to be used by scaffold script
│   │   ├── search_template.py
│   │   └── mcp_server_template.py
│   └── ...
├── servers/
│   └── mojo-manual-mcp/            # Reference implementation
│       └── ...
├── tools/                          # Target directory for new scripts
│   └── ...
└── ...
```

### Target Structure (After Phase 7)

```
/home/james/mcp/
├── tools/
│   ├── sync_documentation.sh      # NEW
│   ├── scaffold_new_mcp.sh        # NEW
│   ├── build_mcp.sh               # NEW
│   └── README.md                  # NEW
└── ...
```

## Step-by-Step Tasks

### Task 1: Create Documentation Sync Tool

**1.1 Create `tools/sync_documentation.sh`**

- **Functionality**:
  - Accepts arguments: `--source-repo`, `--target-dir`, `--branch`
  - Clones repo if not exists, pulls if it does
  - Optional: Copies specific directories from repo to `source-documentation/`
- **Example Usage**:
  ```bash
  ./tools/sync_documentation.sh --repo https://github.com/modularml/mojo --target source-documentation/mojo/manual --path manual
  ```

### Task 2: Create Scaffolding Tool

**2.1 Create `tools/scaffold_new_mcp.sh`**

- **Functionality**:
  - Accepts arguments: `--name`, `--doc-type`
  - Creates directory `servers/{name}-{doc-type}-mcp/`
  - Creates subdirectories: `runtime/`, `config/`
  - Copies templates:
    - `shared/templates/mcp_server_template.py` -> `runtime/{name}_{doc_type}_mcp_server.py`
    - `shared/templates/search_template.py` -> `runtime/search.py`
  - Generates `config/processing_config.yaml` and `config/server_config.yaml` with placeholders
  - Generates `requirements.txt` and `README.md`
- **Example Usage**:
  ```bash
  ./tools/scaffold_new_mcp.sh --name duckdb --doc-type docs
  ```

### Task 3: Create Build Tool

**3.1 Create `tools/build_mcp.sh`**

- **Functionality**:
  - Accepts arguments: `--mcp-name`
  - Runs the full build pipeline for the specified MCP
  - Checks for `pixi` availability, falls back to python if configured
- **Example Usage**:
  ```bash
  ./tools/build_mcp.sh --mcp-name mojo
  ```

### Task 4: Documentation

**4.1 Create `tools/README.md`**

- Document each script, its arguments, and examples.

**4.2 Update main `README.md`**

- Add a "Developer Tools" section referencing the new scripts.

## Success Criteria for Phase 7

Phase 7 is complete when:

1. ✅ `tools/sync_documentation.sh` exists and works
2. ✅ `tools/scaffold_new_mcp.sh` exists and correctly generates a new server structure
3. ✅ `tools/build_mcp.sh` exists and can trigger the build pipeline
4. ✅ All scripts are executable (`chmod +x`)
5. ✅ `tools/README.md` provides clear usage instructions

## Development Workflow Reminder

**CRITICAL**: 
- Make all changes on feature branch `restructure/07-create-tooling-and-automation`
- **NEVER make code changes on `test/restructure` branch**
- **ALWAYS switch to `test/restructure` for testing/running code**
- Switch back to feature branch for fixes if needed
- Ask user to provide terminal output if not visible
