# MCP Development Tools

This directory contains automation scripts for managing MCP servers in this multi-server architecture.

## Scripts Overview

### 1. `sync_documentation.sh`
Sync documentation from upstream repositories (e.g., GitHub).

**Purpose**: Keep documentation sources up-to-date by pulling from upstream repos.

**Usage**:
```bash
./tools/sync_documentation.sh --repo <url> --target <path> [OPTIONS]
```

**Arguments**:
- `--repo <url>` (required): Git repository URL to sync from
- `--target <path>` (required): Target directory (relative to project root or absolute)
- `--path <subdir>` (optional): Subdirectory within repo to sync
- `--branch <branch>` (optional): Branch to sync from (default: main)

**Examples**:
```bash
# Sync entire Mojo repository
./tools/sync_documentation.sh \
  --repo https://github.com/modularml/mojo \
  --target source-documentation/mojo/manual

# Sync only the docs subdirectory from DuckDB repo
./tools/sync_documentation.sh \
  --repo https://github.com/duckdb/duckdb \
  --target source-documentation/duckdb/docs \
  --path docs

# Sync from a specific branch
./tools/sync_documentation.sh \
  --repo https://github.com/example/docs \
  --target source-documentation/example/docs \
  --branch develop
```

**Features**:
- Clones repository if it doesn't exist
- Updates existing repositories with `git pull`
- Supports sparse checkout for specific subdirectories
- Shows file count summary after sync

---

### 2. `scaffold_new_mcp.sh`
Create a new MCP server structure from templates.

**Purpose**: Quickly scaffold a new MCP server with all necessary files and configuration.

**Usage**:
```bash
./tools/scaffold_new_mcp.sh --name <tool> --doc-type <type> [OPTIONS]
```

**Arguments**:
- `--name <tool>` (required): Tool name (e.g., 'duckdb', 'mojo')
- `--doc-type <type>` (required): Documentation type (e.g., 'manual', 'docs', 'guide')
- `--format <format>` (optional): Documentation format: mdx, markdown, rst (default: mdx)
- `--url-base <url>` (optional): Base URL for documentation links

**Examples**:
```bash
# Create DuckDB docs server
./tools/scaffold_new_mcp.sh \
  --name duckdb \
  --doc-type docs \
  --format markdown \
  --url-base https://duckdb.org/docs

# Create Mojo manual server (MDX format)
./tools/scaffold_new_mcp.sh \
  --name mojo \
  --doc-type manual \
  --url-base https://docs.modular.com/mojo/manual

# Create Python guide server (reStructuredText)
./tools/scaffold_new_mcp.sh \
  --name python \
  --doc-type guide \
  --format rst \
  --url-base https://docs.python.org/3/
```

**What it creates**:
```
servers/{tool}-{doc-type}-mcp/
├── runtime/
│   ├── search.py                      # From template
│   └── {tool}_{doc_type}_mcp_server.py  # From template
├── config/
│   ├── processing_config.yaml         # From template
│   └── server_config.yaml             # From template
├── requirements.txt                   # From template
└── README.md                          # From template
```

**Next steps after scaffolding**:
1. Add documentation source to `source-documentation/{tool}/{doc-type}/`
2. Review and adjust configurations in `config/`
3. Run the build pipeline
4. Test the server

---

### 3. `build_mcp.sh`
Build a specific MCP server database by running the full pipeline.

**Purpose**: Execute all preprocessing, embedding, and indexing steps to build a searchable database.

**Usage**:
```bash
./tools/build_mcp.sh --mcp-name <name> [OPTIONS]
```

**Arguments**:
- `--mcp-name <name>` (required): MCP server name (e.g., 'mojo', 'duckdb')
- `--skip-process` (optional): Skip preprocessing step (use existing processed docs)
- `--skip-embed` (optional): Skip embedding generation (use existing embeddings)
- `--use-python` (optional): Use direct python instead of pixi

**Pipeline Steps**:
1. **Process**: Parse and chunk documentation
2. **Embed**: Generate embeddings using MAX server
3. **Consolidate**: Combine chunks and embeddings into Parquet
4. **Load**: Load Parquet into DuckLake catalog
5. **Index**: Create indexed DuckDB with HNSW + FTS

**Examples**:
```bash
# Full build using pixi
./tools/build_mcp.sh --mcp-name mojo

# Build without pixi (direct python)
./tools/build_mcp.sh --mcp-name mojo --use-python

# Skip preprocessing (reuse existing chunks)
./tools/build_mcp.sh --mcp-name mojo --skip-process

# Skip both preprocessing and embedding (for quick index rebuild)
./tools/build_mcp.sh --mcp-name mojo --skip-process --skip-embed
```

**Requirements**:
- For pixi mode: Corresponding tasks must exist in root `pixi.toml`
- For python mode: Python environment with required packages
- MAX server running for embedding generation (unless `--skip-embed`)

**Output**:
- Database: `servers/{mcp}/runtime/{mcp}.db`
- Catalog: `servers/{mcp}/runtime/{mcp}_catalog.ducklake`

---

## Workflow Examples

### Creating and Building a New MCP Server

Complete workflow from scratch:

```bash
# 1. Sync documentation from upstream
./tools/sync_documentation.sh \
  --repo https://github.com/example/docs \
  --target source-documentation/example/docs \
  --path docs

# 2. Scaffold the server structure
./tools/scaffold_new_mcp.sh \
  --name example \
  --doc-type docs \
  --format markdown \
  --url-base https://example.com/docs

# 3. Review and adjust configurations
# Edit: servers/example-docs-mcp/config/processing_config.yaml
# Edit: servers/example-docs-mcp/config/server_config.yaml

# 4. Build the database
./tools/build_mcp.sh --mcp-name example

# 5. Test the server
mcp dev servers/example-docs-mcp/runtime/example_docs_mcp_server.py
```

### Updating Documentation and Rebuilding

When upstream docs change:

```bash
# 1. Sync latest documentation
./tools/sync_documentation.sh \
  --repo https://github.com/modularml/mojo \
  --target source-documentation/mojo/manual

# 2. Rebuild the database
./tools/build_mcp.sh --mcp-name mojo
```

### Quick Rebuild After Configuration Changes

If you only changed indexing parameters:

```bash
# Skip processing and embedding, just rebuild indexes
./tools/build_mcp.sh --mcp-name mojo --skip-process --skip-embed
```

---

## Templates

Templates are stored in `shared/templates/` and used by `scaffold_new_mcp.sh`:

- `search_template.py` - Hybrid search implementation
- `mcp_server_template.py` - MCP server entry point
- `processing_config_template.yaml` - Preprocessing configuration
- `server_config_template.yaml` - Server runtime configuration
- `requirements_template.txt` - Python dependencies
- `README_template.md` - Server README

**Placeholders** (automatically replaced during scaffolding):
- `{{TOOL_NAME}}` - Tool name (e.g., 'mojo', 'duckdb')
- `{{DOC_TYPE}}` - Documentation type (e.g., 'manual', 'docs')
- `{{MCP_NAME}}` - Full MCP name (e.g., 'mojo-manual-mcp')
- `{{MCP_NAME_UPPER}}` - Uppercase MCP name for env vars (e.g., 'MOJO_MANUAL_MCP')
- `{{DOC_TYPE_TITLE}}` - Title-cased documentation type (e.g., 'Mojo Manual')
- `{{FORMAT}}` - Documentation format (e.g., 'mdx', 'markdown')
- `{{FORMAT_EXT}}` - File extension (e.g., 'mdx', 'md')
- `{{URL_BASE}}` - Base URL for documentation links

---

## Prerequisites

### For All Scripts
- Git installed
- Bash shell
- Project structure as per `RESTRUCTURING_PLAN.md`

### For `build_mcp.sh`
- **Pixi mode**: 
  - Pixi installed and configured
  - Tasks defined in root `pixi.toml`
- **Python mode**:
  - Python 3.10+
  - Required packages installed (see `requirements.txt`)
  - MAX server running at `http://localhost:8000/v1` (for embeddings)

---

## Troubleshooting

### Sync Issues
**Problem**: Clone fails with "permission denied"
- **Solution**: Check SSH keys or use HTTPS URL instead

**Problem**: Sparse checkout doesn't work
- **Solution**: Ensure Git version supports sparse checkout (Git 2.25+)

### Scaffold Issues
**Problem**: Template files not found
- **Solution**: Ensure `shared/templates/` exists with all template files

**Problem**: Server directory already exists
- **Solution**: Delete existing directory or choose a different name

### Build Issues
**Problem**: Pixi task not found
- **Solution**: Add task definitions to root `pixi.toml` or use `--use-python`

**Problem**: MAX server connection fails
- **Solution**: Start MAX server with `pixi run max-serve` or skip embeddings with `--skip-embed`

**Problem**: Import errors in python mode
- **Solution**: Ensure you're in project root and dependencies are installed

---

## Contributing

When adding new scripts:

1. Follow the existing naming convention: `{action}_{target}.sh`
2. Include comprehensive help text with `--help` flag
3. Use color output for better UX (see existing scripts)
4. Handle errors gracefully with clear error messages
5. Update this README with usage examples

---

## See Also

- Main README: `../README.md`
- Restructuring Plan: `../RESTRUCTURING_PLAN.md`
- Implementation Summary: `../IMPLEMENTATION_SUMMARY.md`
- Phase 7 Prompt: `../PHASE_7_IMPLEMENTATION_PROMPT.md`
