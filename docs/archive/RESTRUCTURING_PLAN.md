# MCP Multi-Server Restructuring Plan

**Status: PHASES 1-7 COMPLETE ✅ | Phase 8 Ready for Execution**

## Executive Summary

This plan restructures the project to support multiple independently-deployable MCP servers (Mojo, DuckDB, etc.) that can be:
- **Packaged as standalone modules** for distribution via GitHub
- **Self-contained** with all dependencies included (no shared resources assumed)
- **Easily updatable** with automated documentation refresh workflows
- **Compatible with non-Pixi environments** (fallback to pip/venv)

Key design principles:
- Each MCP server is **completely self-contained** in `/servers/{mcp-name}/`
- All configuration is **YAML-based and centralized** in config files
- Build-time infrastructure is **shared during development** but **not packaged** in distributed servers
- Documentation sources support **multiple formats** (MDX, MD, other)
- **Automation scripts** exist for documentation sync from upstream sources

### Current Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ COMPLETE & VERIFIED | Directory structure, `.gitignore`, config templates, `requirements.txt` |
| **Phase 2** | ✅ COMPLETE & VERIFIED | `ProcessorFactory`, `BaseDocumentProcessor`, multi-format support, config loading |
| **Phase 3** | ✅ COMPLETE & VERIFIED | Parameterized embedding scripts, updated pixi.toml, integrated config loader |
| **Phase 4** | ✅ COMPLETE & VERIFIED | Config loader integration, variable substitution working |
| **Phase 5** | ✅ COMPLETE & VERIFIED | All build infrastructure moved to `/shared/`, MAX server health check |
| **Phase 6** | ✅ COMPLETE & VERIFIED | Mojo server organized in `/servers/mojo-manual-mcp/`, root cleanup |
| **Phase 7** | ✅ COMPLETE & VERIFIED | Templates created, automation scripts (sync, scaffold, build) working |
| **Phase 8** | ⏳ NEXT | Final documentation updates, cleanup, and validation |

### Alignment Confirmed ✅

The project architecture and vision are **fully cohesive and well-organized**. Phases 1-2 have been properly executed with no corruption detected. All foundational elements are correctly in place.

---

## 📋 Key Reference Documents

For next session, refer to these companion documents:

1. **`PHASE_3_IMPLEMENTATION_PROMPT.md`** — Step-by-step Phase 3 implementation guide
   - Detailed checklist for parameterizing embedding scripts
   - Expected outcomes and success criteria
   - Debugging tips if issues arise

2. **`PHASE_1_2_VERIFICATION.md`** — Comprehensive integrity check results
   - Detailed verification of all Phase 1-2 components
   - Confirmation that architecture is sound
   - No corruption detected - safe to proceed
   - Testing & validation results

3. **`RESTRUCTURING_PLAN.md`** (this file) — Overall restructuring plan with 8 phases

---

---

## Actual Current State (After Phase 2)

### ✅ What Has Been Successfully Implemented

```
/home/james/mcp/
│
├── shared/                                 # NEW: Build-time infrastructure
│   ├── preprocessing/                      # Moved from /preprocessing
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── base_processor.py          # NEW: Abstract base class (Phase 2)
│   │   │   ├── mdx_processor.py           # Inherited from BaseDocumentProcessor
│   │   │   ├── markdown_processor.py      # NEW: Markdown format support (Phase 2)
│   │   │   ├── processor_factory.py       # NEW: Pluggable processor selection (Phase 2)
│   │   │   ├── config_loader.py           # NEW: Variable substitution (Phase 3 prep)
│   │   │   ├── chunker.py
│   │   │   ├── metadata_extractor.py
│   │   │   ├── utils.py
│   │   │   └── pipeline.py                # Supports --config CLI argument (Phase 3 prep)
│   │   ├── config/
│   │   │   └── processing_config.yaml
│   │   └── README.md
│   │
│   ├── embedding/                          # Location prepared (scripts still at root)
│   │
│   ├── templates/                          # NEW: Reusable code templates
│   │   ├── search_template.py              # Moved from /search.py
│   │   ├── mcp_server_template.py          # Future reference
│   │   └── README.md
│   │
│   └── build/                              # NEW: Generated/ephemeral artifacts
│       ├── logs/
│       ├── processed_docs/
│       └── embeddings/
│
├── servers/
│   └── mojo-manual-mcp/                    # NEW: Mojo MCP server (self-contained)
│       ├── runtime/
│       │   ├── search.py                   # Local copy of search implementation
│       │   ├── mojo_manual_mcp_server.py   # MCP server (renamed from server.py)
│       │   └── [database files when built]
│       ├── config/
│       │   ├── processing_config.yaml      # ✅ Complete, parameterized
│       │   └── server_config.yaml          # ✅ Complete, with ${VAR} substitution
│       ├── requirements.txt                # ✅ For pip installation
│       └── README.md
│
├── source-documentation/
│   ├── mojo/
│   │   └── manual/                         # Original docs source (MDX files)
│   └── [room for other doc sources]
│
├── preprocessing/                          # OLD: Still exists (Phase 4 will move)
│   ├── src/
│   └── config/
│
├── embedding/                              # OLD: Still exists (scripts, not yet parameterized)
│   ├── generate_embeddings.py              # 🔄 Needs --mcp-name and --config args
│   ├── consolidate_data.py                 # 🔄 Needs --mcp-name arg
│   ├── load_to_ducklake.py                 # 🔄 Needs --mcp-name arg
│   ├── create_indexes.py                   # 🔄 Needs --mcp-name arg
│   └── README.md
│
├── processed_docs/                         # Generated artifacts (will move to shared/build/ in Phase 4)
├── runtime/                                # OLD: Still exists with original structure
├── server.py                               # ROOT: Working MCP server (will be organized in Phase 5)
├── search.py                               # ROOT: Hybrid search implementation
├── pixi.toml                               # Root workspace config
│
└── [other files]
```

### 🔄 What's in Progress (Phase 3 Preparation)

1. **config_loader.py** — ✅ Exists and working with `${SERVER_ROOT}` and `${PROJECT_ROOT}` substitution
2. **Processing config** — ✅ Exists with all necessary parameters for Mojo server
3. **Server config** — ✅ Exists with database paths, embedding settings, search params
4. **processor_factory.py** — ✅ Supports dynamic processor selection (mdx, markdown, etc.)
5. **Embedding scripts** — 🔄 Still at root `/embedding/`, need parameterization

### ❌ What Still Needs to Happen

**Phase 3 (Next)**: Parameterize embedding scripts
- Move scripts from `/embedding/` to `/shared/embedding/`
- Add `--mcp-name` argument to all scripts
- Add `--config` argument for config file path
- Update scripts to use config_loader for path resolution
- Update root `pixi.toml` with parameterized task definitions

**Phase 4**: Move build infrastructure
- Finalize migration of embedding scripts to `/shared/embedding/`
- Move `/preprocessing/` completely (currently in both places)
- Organize `/processed_docs/` artifacts to `/shared/build/`

**Phase 5**: Create Mojo MCP server structure
- This will be mostly moving/renaming existing files
- Database files move to server runtime directory

**Phases 6-8**: Tooling, docs, cleanup

---

## Current State vs. Target State (Original Plan)

### Current Organization (Before Phase 1)

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

## Key Design Decisions (Refined)

### 1. Self-Contained Server Packaging

**Each MCP server in `/servers/{mcp-name}/` must be completely standalone:**
- Includes its own copy of runtime code (not shared)
- Bundled with all required dependencies
- Can be distributed as a GitHub repository module or submodule
- No assumptions about shared infrastructure being available

**Implication:**
- `search.py` is copied (not symlinked) to each server's runtime
- Configuration files are per-server (not shared templates)
- Each server has a `requirements.txt` or can be used with pixi

### 2. Multi-Format Documentation Support

**Processing pipeline must support multiple doc formats:**
- `.mdx` files → use `MDXProcessor` (Mojo manual)
- `.md` files → use `MarkdownProcessor` (most common)
- Other formats → need format-specific processor or pass-through

**Implication:**
- Create configuration option `processing.input_format` to specify processor type
- Build processors as pluggable classes (not hardcoded)
- Update pipeline to check file extension and route to appropriate processor
- Support mixed formats in same source directory

### 3. YAML Configuration Standard

**All configuration centralized in YAML files:**
- No hardcoded paths in Python code
- Configuration lives in `/servers/{mcp}/config/`
- Two config files per server:
  - `processing_config.yaml` — Source docs, chunking, output paths
  - `server_config.yaml` — MCP runtime settings, database paths, embeddings

**Example structure:**
```yaml
# servers/mojo-manual-mcp/config/processing_config.yaml
source:
  directory: "${MCP_ROOT}/source-documentation/mojo/manual"
  format: "mdx"  # or "markdown", "rst", etc.
  file_patterns:
    - "*.mdx"
    - "*.md"

output:
  base_directory: "${PROJECT_ROOT}/shared/build/processed_docs/mojo"
  raw_dir: "raw"
  chunks_dir: "chunks"
  
# servers/mojo-manual-mcp/config/server_config.yaml
server:
  name: "mojo-docs"
  database_path: "${SERVER_ROOT}/runtime/mojo_manual_mcp.db"
  ducklake_catalog: "${SERVER_ROOT}/runtime/mojo_manual_catalog.ducklake"
```

### 4. Documentation Update Automation

**Automated sync workflow for upstream docs:**
- Create `tools/sync_documentation.sh` script
  - Clones/pulls upstream repo
  - Copies source docs to `source-documentation/{tool}/`
  - Optionally commits changes with timestamp
  - Logs sync activity

- Example usage:
  ```bash
  tools/sync_documentation.sh mojo \
    https://github.com/modularml/mojo.git \
    docs/manual \
    source-documentation/mojo/manual
  ```

- Should integrate into CI/CD pipeline (GitHub Actions)

### 5. Non-Pixi Compatibility

**Support users without pixi installed:**
- Provide `requirements.txt` in each server (for pip)
- Provide `setup.py` or `pyproject.toml` (for pip install)
- Document virtual environment setup with venv
- Maintain `pixi.toml` for pixi users (optional optimization)

**Each server structure includes:**
```
servers/mojo-manual-mcp/
├── requirements.txt           # For pip install
├── pyproject.toml             # For pip install / packaging
├── pixi.toml                  # Optional for pixi users
└── runtime/
    └── ...
```

---

---

## Phased Implementation with Git Branches

Each phase corresponds to a single git branch that can be reviewed and merged independently. This allows for safe, incremental restructuring.

### Git Branch Naming Convention
```
restructure/{phase}-{short-description}
```

Examples: `restructure/01-directory-setup`, `restructure/02-move-preprocessing`, etc.

---

### Phase 1: Foundation & Configuration
**Branch: `restructure/01-directory-structure-and-config`**

#### 1.1 Create new directory hierarchy
```bash
mkdir -p shared/{preprocessing,embedding,templates,build/{processed_docs,embeddings,logs}}
mkdir -p servers/mojo-manual-mcp/{runtime,config}
mkdir -p docs
mkdir -p tools
mkdir -p source-documentation/mojo
```

#### 1.2 Update .gitignore
Add proper patterns to exclude build artifacts:
```gitignore
# Build artifacts (ephemeral, generated at dev time)
shared/build/
*.pyc
__pycache__/
*.egg-info/
.pixi/
pixi.lock

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

# Temporary
*.tmp
*.log
logs/

# OS
.DS_Store
.vs/
```

#### 1.3 Create config templates in `/servers/mojo-manual-mcp/config/`

**`servers/mojo-manual-mcp/config/processing_config.yaml`** — Template with absolute and relative paths:
```yaml
# Processing Configuration for Mojo Manual MCP
# Used during build-time preprocessing and embedding generation

source:
  # Can use ${SERVER_ROOT} or absolute path
  directory: "${SERVER_ROOT}/../../../source-documentation/mojo/manual"
  format: "mdx"  # Format of source files: mdx, markdown, rst, etc.
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

processing:
  remove_jsx_components: true
  remove_imports: true
  preserve_code_blocks: true
  normalize_whitespace: true

metadata:
  extract_frontmatter: true
  generate_section_hierarchy: true
  calculate_content_hash: true
```

**`servers/mojo-manual-mcp/config/server_config.yaml`** — Runtime config:
```yaml
# MCP Server Configuration for Mojo Manual

server:
  name: "mojo-docs"
  description: "Mojo documentation search via hybrid semantic/keyword search"
  
database:
  # Relative to runtime/ directory where server.py runs
  path: "${SERVER_ROOT}/runtime/mojo_manual_mcp.db"
  table_name: "mojo_docs_indexed"
  ducklake_catalog: "${SERVER_ROOT}/runtime/mojo_manual_catalog.ducklake"

embedding:
  # MAX server endpoint (can be auto-started)
  max_server_url: "http://localhost:8000/v1"
  model_name: "sentence-transformers/all-mpnet-base-v2"
  auto_start: true
  auto_start_timeout: 30

search:
  top_k: 5
  fts_title_weight: 2.0
  fts_content_weight: 1.0
  embed_cache_size: 512
  
  # Debug flags
  debug_explain_vss: false
  debug_log_fts_path: false
```

#### 1.4 Create `requirements.txt` for each server
**`servers/mojo-manual-mcp/requirements.txt`:**
```
duckdb>=1.4.1,<2
openai>=2.3.0,<3
numpy>=2.3.3,<3
requests>=2.32.5,<3
pyyaml>=6.0.3,<7
mcp>=1.20.0,<2
```

#### 1.5 Create setup documentation
**`.github/.memory.md`** — Updated project memory:
```markdown
## MCP Multi-Server Architecture

### Project Goal
Build self-contained MCP resource servers for various documentation sources (Mojo, DuckDB, etc.) 
that can be distributed independently via GitHub.

### Key Design Decisions
- Each server is completely self-contained in `/servers/{mcp-name}/`
- Build-time infrastructure in `/shared/` is for development only (not distributed)
- All configuration is YAML-based in `/servers/{mcp-name}/config/`
- Documentation sources in `/source-documentation/{tool}/{doc-type}/`
- Runtime artifacts (DBs, catalogs) are per-server and included in distributions

### Documentation Update Strategy
- Scripts in `/tools/` handle syncing upstream docs
- GitHub Actions can automate periodic updates
- Each server maintains its own `sync_config.yaml` for automation

### Supported Doc Formats
- MDX files (Mojo manual)
- Markdown files (most common)
- Other formats via pluggable processors

### Deployment
- Standalone: Clone server repo, install requirements, run server
- Integrated: Add as git submodule in consuming projects
```

#### 1.6 Commit changes
```bash
git checkout -b restructure/01-directory-structure-and-config
git add -A
git commit -m "chore: Create directory structure, config templates, and .gitignore

- Create shared/ directory for build-time infrastructure
- Create servers/mojo-manual-mcp/ as first MCP server
- Add YAML-based configuration templates (processing_config.yaml, server_config.yaml)
- Create requirements.txt for pip-based installation
- Update .gitignore to exclude build artifacts and databases
- Update .memory.md to document multi-server architecture"
```

---

### Phase 2: Support Multi-Format Processing
**Branch: `restructure/02-multi-format-doc-support`**

#### 2.1 Create pluggable processor architecture

**`shared/preprocessing/src/processor_factory.py`** (NEW):
```python
"""Factory for creating document processors based on file format."""

from pathlib import Path
from typing import Dict
from .mdx_processor import MDXProcessor
from .markdown_processor import MarkdownProcessor  # NEW - create this

class ProcessorFactory:
    """Factory to get appropriate processor for file format."""
    
    PROCESSORS = {
        "mdx": MDXProcessor,
        "md": MarkdownProcessor,
        "markdown": MarkdownProcessor,
    }
    
    @classmethod
    def get_processor(cls, config: Dict, format_type: str):
        """Get processor instance for given format."""
        processor_class = cls.PROCESSORS.get(format_type.lower())
        if not processor_class:
            raise ValueError(f"Unsupported format: {format_type}. "
                           f"Supported: {list(cls.PROCESSORS.keys())}")
        return processor_class(config)
```

#### 2.2 Create base processor class
**`shared/preprocessing/src/base_processor.py`** (NEW):
```python
"""Base class for document processors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

class BaseDocumentProcessor(ABC):
    """Abstract base for document processors."""
    
    def __init__(self, config: Dict):
        self.config = config
    
    @abstractmethod
    def process_file(self, file_path: Path) -> Dict:
        """Process a document file and extract content + metadata."""
        pass
```

#### 2.3 Create MarkdownProcessor
**`shared/preprocessing/src/markdown_processor.py`** (NEW):
- Similar to MDXProcessor but for `.md` files
- Handles YAML frontmatter
- Simpler regex patterns (no JSX)
- Inherits from BaseDocumentProcessor

#### 2.4 Update MDXProcessor
**`shared/preprocessing/src/mdx_processor.py`**:
- Inherit from BaseDocumentProcessor
- No other changes needed

#### 2.5 Update pipeline.py
**`shared/preprocessing/src/pipeline.py`**:
```python
# Add to init:
from .processor_factory import ProcessorFactory

# In process_all_documents():
format_type = self.config["source"].get("format", "mdx")
processor = ProcessorFactory.get_processor(self.config, format_type)

# Then use processor instead of hardcoded MDXProcessor
```

#### 2.6 Update processing_config.yaml template
Add `format` field to specify processor type.

#### 2.7 Commit changes
```bash
git checkout -b restructure/02-multi-format-doc-support
git add -A
git commit -m "feat: Add pluggable multi-format document processor support

- Create ProcessorFactory for format-based processor selection
- Create BaseDocumentProcessor abstract class
- Create MarkdownProcessor for .md files
- Update MDXProcessor to inherit from base class
- Update pipeline.py to use factory pattern
- Configuration now supports 'format' field (mdx, markdown, etc.)
- Supports mixed formats in same documentation source"
```

---

### Phase 3: Parameterize Build Pipeline
**Branch: `restructure/03-parameterize-build-scripts`**

#### 3.1 Update preprocessing pipeline
**`shared/preprocessing/src/pipeline.py`**:
- Add `--config` CLI argument
- Load config from YAML (not hardcoded)
- Support `${SERVER_ROOT}` and `${PROJECT_ROOT}` variable substitution

#### 3.2 Update embedding scripts
Update all scripts in `shared/embedding/`:
- `generate_embeddings.py`: Add `--mcp-name` and `--config` args
- `consolidate_data.py`: Add `--mcp-name` arg for output naming
- `load_to_ducklake.py`: Add `--mcp-name` arg for catalog naming
- `create_indexes.py`: Add `--mcp-name` arg for DB and table naming

#### 3.3 Create config loader utility
**`shared/preprocessing/src/config_loader.py`** (NEW):
```python
"""YAML configuration loader with variable substitution."""

import yaml
from pathlib import Path

def load_config_with_substitution(config_path: str, server_root: Path = None) -> Dict:
    """Load YAML config and substitute variables like ${SERVER_ROOT}."""
    # Implementation with variable substitution
```

#### 3.4 Update root pixi.toml
```toml
[tasks]
# Mojo build pipeline (example)
mojo-process = "python -m shared.preprocessing.src.pipeline --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-embed = "python shared/embedding/generate_embeddings.py --mcp-name mojo --config servers/mojo-manual-mcp/config/processing_config.yaml"
mojo-consolidate = "python shared/embedding/consolidate_data.py --mcp-name mojo"
mojo-load = "python shared/embedding/load_to_ducklake.py --mcp-name mojo"
mojo-index = "python shared/embedding/create_indexes.py --mcp-name mojo"
mojo-build = "bash tools/build_mcp.sh mojo"  # Convenience wrapper
```

#### 3.5 Commit changes
```bash
git checkout -b restructure/03-parameterize-build-scripts
git add -A
git commit -m "refactor: Parameterize all build pipeline scripts

- Add --config argument to preprocessing pipeline
- Add --mcp-name argument to all embedding scripts
- Support ${SERVER_ROOT} and ${PROJECT_ROOT} in YAML configs
- Create config_loader.py for variable substitution
- Update root pixi.toml with new parameterized tasks
- Build pipeline now supports arbitrary MCP servers"
```

---

### Phase 4: Move & Restructure Build Infrastructure
**Branch: `restructure/04-move-build-infrastructure`**

#### 4.1 Move directories
```bash
mv preprocessing/src shared/preprocessing/
mv preprocessing/config shared/preprocessing/
mv preprocessing/README.md shared/preprocessing/
mv preprocessing/__init__.py shared/preprocessing/
rm -rf preprocessing/

mv embedding/*.py shared/embedding/
mv embedding/README.md shared/embedding/
# Keep main.db and .ducklake files (will move later with Mojo server)
```

#### 4.2 Move processed artifacts
```bash
mkdir -p shared/build/processed_docs/mojo
mv processed_docs/raw/* shared/build/processed_docs/mojo/raw/ 2>/dev/null || true
mv processed_docs/metadata/* shared/build/processed_docs/mojo/metadata/ 2>/dev/null || true
mv processed_docs/chunks/* shared/build/processed_docs/mojo/chunks/ 2>/dev/null || true
mv processed_docs/manifest.json shared/build/processed_docs/mojo/ || true
rm -rf processed_docs/

mkdir -p shared/build/logs
mv logs/* shared/build/logs/ || true
rm -rf logs/
```

#### 4.3 Move templates
```bash
mv search.py shared/templates/search_template.py
cp runtime/server.py shared/templates/mcp_server_template.py
```

#### 4.4 Create shared/README.md
Document the shared build infrastructure.

#### 4.5 Commit changes
```bash
git checkout -b restructure/04-move-build-infrastructure
git add -A
git commit -m "refactor: Move build infrastructure to shared/

- Move preprocessing/ to shared/preprocessing/
- Move embedding/ scripts to shared/embedding/
- Move processed_docs/ to shared/build/processed_docs/
- Move logs/ to shared/build/logs/
- Move search.py to shared/templates/search_template.py
- Create shared/README.md for documentation
- Update all relative imports to work from new location"
```

---

### Phase 5: Create Mojo MCP Server Structure
**Branch: `restructure/05-organize-mojo-server`**

#### 5.1 Create server directories and move files
```bash
mkdir -p servers/mojo-manual-mcp/runtime

# Copy runtime files (not move - keep originals for safety initially)
cp runtime/server.py servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
cp runtime/search.py servers/mojo-manual-mcp/runtime/search.py

# Move databases
mv main.db servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db
mv mojo_catalog.ducklake servers/mojo-manual-mcp/runtime/mojo_manual_catalog.ducklake
mv mojo_catalog.ducklake.files/ servers/mojo-manual-mcp/runtime/
```

#### 5.2 Update server runtime code
**`servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py`**:
- Update imports to reference local `search.py`
- Update docstring to be Mojo-specific
- Load `server_config.yaml` from parent directory
- Update path handling to be relative

**`servers/mojo-manual-mcp/runtime/search.py`**:
- Update `DB_PATH` default from `"main.db"` to `"mojo_manual_mcp.db"`
- Add YAML config loading for database/table paths
- Remove hardcoded environment defaults (use config)

#### 5.3 Create server README
**`servers/mojo-manual-mcp/README.md`**:
- Installation instructions (with pixi and without)
- Configuration options
- How to run locally
- How to configure in VS Code/Cursor

#### 5.4 Copy mojo docs if not already there
```bash
# Move/ensure mojo manual is in correct location
# Source docs should already be in source-documentation/mojo/manual/
```

#### 5.5 Commit changes
```bash
git checkout -b restructure/05-organize-mojo-server
git add -A
git commit -m "refactor: Organize Mojo MCP server as standalone module

- Create servers/mojo-manual-mcp/runtime/ directory
- Move/copy runtime files with MCP-specific naming
- Rename main.db to mojo_manual_mcp.db
- Update server.py to mojo_manual_mcp_server.py
- Update all path references to be relative and config-based
- Create server-specific README with installation and usage
- Mojo server now fully self-contained and distributable"
```

---

### Phase 6: Create Tooling & Automation
**Branch: `restructure/06-create-tooling-and-automation`**

#### 6.1 Create build wrapper script
**`tools/build_mcp.sh`** (NEW):
```bash
#!/bin/bash
# Build a single MCP server (preprocessing + embedding + indexing)
# Usage: build_mcp.sh mcp_name
```

#### 6.2 Create build all script
**`tools/build_all_mcp.sh`** (NEW):
```bash
#!/bin/bash
# Build all MCP servers defined in pixi.toml
```

#### 6.3 Create new MCP scaffold script
**`tools/scaffold_new_mcp.sh`** (NEW):
```bash
#!/bin/bash
# Scaffold a new MCP server structure
# Usage: scaffold_new_mcp.sh tool_name doc_type
# Example: scaffold_new_mcp.sh duckdb docs
```

#### 6.4 Create documentation sync script
**`tools/sync_documentation.sh`** (NEW):
```bash
#!/bin/bash
# Sync documentation from upstream source
# Usage: sync_documentation.sh mcp_name repo_url source_path dest_path
# Example: sync_documentation.sh mojo https://github.com/modularml/mojo.git docs/manual source-documentation/mojo/manual
```

#### 6.5 Create setup script for users
**`setup.sh`** (NEW) at project root:
```bash
#!/bin/bash
# Setup script for users who don't have pixi
# Guides through venv setup and pip installation
```

#### 6.6 Commit changes
```bash
git checkout -b restructure/06-create-tooling-and-automation
git add -A
git commit -m "feat: Create tooling and automation scripts

- Create build_mcp.sh for building individual servers
- Create build_all_mcp.sh for building all servers
- Create scaffold_new_mcp.sh for generating new server templates
- Create sync_documentation.sh for syncing upstream docs
- Create setup.sh for non-pixi users
- All scripts documented with usage examples"
```

---

### Phase 7: Update Documentation
**Branch: `restructure/07-update-documentation`**

#### 7.1 Move docs
```bash
mv ARCHITECTURE.md docs/
mv PREPROCESSING.md docs/
mv RUNTIME.md docs/
mv DEVELOPMENT.md docs/
mv CONSOLIDATION_SUMMARY.md docs/ (if still needed)
mv project.md docs/
mv mojo-example.md docs/
```

#### 7.2 Create new docs
- `docs/README.md` — Entry point to all docs
- `docs/QUICKSTART.md` — For new users
- `docs/SETUP_PIXI.md` — Setup for pixi users
- `docs/SETUP_VENV.md` — Setup without pixi
- `docs/CREATING_NEW_MCP.md` — How to add a new MCP server
- `docs/CONFIGURATION.md` — Detailed config options

#### 7.3 Create server-specific docs
- `servers/mojo-manual-mcp/README.md` — Already created in Phase 5
- `servers/mojo-manual-mcp/CONFIGURATION.md` — Config options
- `servers/mojo-manual-mcp/DEVELOPMENT.md` — Rebuilding the DB

#### 7.4 Update root README.md
- Explain new multi-server architecture
- Point to docs/
- Show quick examples for both pixi and non-pixi users

#### 7.5 Update .memory.md
Final comprehensive memory document for future work.

#### 7.6 Commit changes
```bash
git checkout -b restructure/07-update-documentation
git add -A
git commit -m "docs: Reorganize and expand documentation

- Move existing docs to docs/ directory
- Create comprehensive README structure
- Add QUICKSTART for new users
- Add setup guides for pixi and venv
- Add guide for creating new MCP servers
- Add detailed configuration documentation
- Update root README with new architecture overview
- Update .memory.md with current state and decisions"
```

---

### Phase 8: Final Cleanup & Testing
**Branch: `restructure/08-final-cleanup-and-validation`**

#### 8.1 Clean up old directories
```bash
rm -rf runtime/  # Old runtime, now in servers/mojo-manual-mcp/runtime/
```

#### 8.2 Verify all imports work
- Test that `shared/preprocessing/` can be imported as module
- Test that all pixi tasks work
- Test build pipeline end-to-end

#### 8.3 Test server setup
- Test running Mojo server from `servers/mojo-manual-mcp/`
- Test searches work
- Verify config loading works

#### 8.4 Test for non-pixi users
- Create fresh venv
- Install from `requirements.txt`
- Test that server still runs

#### 8.5 Final .gitignore audit
Ensure no unnecessary files are tracked.

#### 8.6 Commit changes
```bash
git checkout -b restructure/08-final-cleanup-and-validation
git add -A
git commit -m "chore: Final cleanup and validation

- Remove obsolete old runtime/ directory
- Verify all imports and relative paths
- Validate pixi tasks complete successfully
- Test MCP server runs from new location
- Confirm pip/venv setup works for non-pixi users
- Final gitignore audit
- Project structure complete and working"
```

---

## Summary of Git Workflow

```bash
# Create main feature branch
git checkout -b restructure/main

# Work through each phase (can do in parallel or sequence)
git checkout -b restructure/01-directory-structure-and-config
# ... make changes ...
git commit
git push

# Create PR for review
# After approval, merge to main

# Continue with next phase
git checkout main
git pull
git checkout -b restructure/02-multi-format-doc-support
# ... make changes ...
```

**Total phases: 8**
**Estimated time: 2-3 hours per phase for implementation + review**

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

## Summary of Git Workflow

```bash
# Create main feature branch
git checkout -b restructure/main

# Work through each phase (can do in parallel or sequence)
git checkout -b restructure/01-directory-structure-and-config
# ... make changes ...
git commit
git push

# Create PR for review
# After approval, merge to main

# Continue with next phase
git checkout main
git pull
git checkout -b restructure/02-multi-format-doc-support
# ... make changes ...
```

**Total phases: 8**
**Estimated time: 2-3 hours per phase for implementation + review**

---

## Final Implementation Checklist

### Overall Validation
- [ ] All phases merged to main
- [ ] No broken imports or missing modules
- [ ] pixi tasks all work correctly
- [ ] Non-pixi (venv) setup works
- [ ] Mojo server builds and runs
- [ ] Search functionality works end-to-end
- [ ] Database files are properly named and located
- [ ] Config loading works correctly
- [ ] Documentation is complete and accurate

### Pre-Merge Checks for Each Phase
- [ ] Branch builds without errors
- [ ] All tests pass (if applicable)
- [ ] Imports resolve correctly
- [ ] No files in .gitignore accidentally committed
- [ ] Config examples are valid YAML
- [ ] Scripts have executable bit set (`chmod +x`)
- [ ] Documentation reflects changes

---

## Key Files to Create/Modify Summary

### New Files
- `shared/preprocessing/src/processor_factory.py`
- `shared/preprocessing/src/base_processor.py`
- `shared/preprocessing/src/markdown_processor.py`
- `shared/preprocessing/src/config_loader.py`
- `servers/mojo-manual-mcp/config/processing_config.yaml`
- `servers/mojo-manual-mcp/config/server_config.yaml`
- `servers/mojo-manual-mcp/requirements.txt`
- `servers/mojo-manual-mcp/README.md`
- `tools/build_mcp.sh`
- `tools/build_all_mcp.sh`
- `tools/scaffold_new_mcp.sh`
- `tools/sync_documentation.sh`
- `setup.sh`
- `docs/README.md`
- `docs/QUICKSTART.md`
- `docs/SETUP_PIXI.md`
- `docs/SETUP_VENV.md`
- `docs/CREATING_NEW_MCP.md`
- `docs/CONFIGURATION.md`

### Modified Files
- `.gitignore` — Add exclusions for build artifacts
- `.github/.memory.md` — Document new architecture
- `shared/preprocessing/src/pipeline.py` — Add config support
- `shared/preprocessing/src/mdx_processor.py` — Inherit from base class
- `shared/embedding/generate_embeddings.py` — Add CLI args
- `shared/embedding/consolidate_data.py` — Add CLI args
- `shared/embedding/load_to_ducklake.py` — Add CLI args
- `shared/embedding/create_indexes.py` — Add CLI args
- `servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py` — Update paths
- `servers/mojo-manual-mcp/runtime/search.py` — Update config loading
- `pixi.toml` — Update tasks with new paths
- Root `README.md` — Explain new structure

### Moved Files
- `preprocessing/` → `shared/preprocessing/`
- `embedding/` → `shared/embedding/`
- `search.py` → `shared/templates/search_template.py`
- `runtime/server.py` → `shared/templates/mcp_server_template.py` + `servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py`
- `processed_docs/` → `shared/build/processed_docs/`
- `logs/` → `shared/build/logs/`
- `main.db` → `servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db`
- `mojo_catalog.ducklake` → `servers/mojo-manual-mcp/runtime/`
- `*.md` docs → `docs/`

### Deleted Directories
- `preprocessing/` (contents moved to shared/)
- `embedding/` (contents moved to shared/)
- `runtime/` (contents moved to servers/mojo-manual-mcp/)
- `processed_docs/` (contents moved to shared/build/)
- `logs/` (contents moved to shared/build/)

---

## Environment Variable Reference

### Configuration Loading
Scripts will use these environment variable conventions:

```bash
# During development/building:
SERVER_ROOT=/path/to/servers/mojo-manual-mcp
PROJECT_ROOT=/path/to/mcp

# In configs, use:
# ${SERVER_ROOT}/... = absolute path to server
# ${PROJECT_ROOT}/... = absolute path to project root

# At runtime (when server.py runs):
MOJO_DB_PATH=servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db
MAX_SERVER_URL=http://localhost:8000/v1
EMBED_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
AUTO_START_MAX=1
```

---

## Testing Strategy

### Unit Tests (if added)
- Test ProcessorFactory with different formats
- Test YAML config loading with variable substitution
- Test path resolution for different scenarios

### Integration Tests
- Build Mojo MCP from scratch
- Run searches and verify results
- Test config override mechanisms

### End-to-End Tests
- Clone servers/mojo-manual-mcp/ as standalone repo
- Install from requirements.txt
- Run server without accessing parent project

---

## Notes on Non-Pixi Support

### For Users Without Pixi

1. **Clone the server repo** (or submodule):
   ```bash
   git clone https://github.com/yourusername/mojo-manual-mcp.git
   cd mojo-manual-mcp
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start MAX server** (if not running):
   ```bash
   pip install modular
   max serve --model sentence-transformers/all-mpnet-base-v2
   ```

5. **Run MCP server** (in another terminal):
   ```bash
   cd runtime
   python mojo_manual_mcp_server.py
   ```

6. **Configure in VS Code**:
   - Add entry to settings.json with absolute paths

### For Development (with Pixi)

```bash
cd /path/to/mcp
pixi run mojo-build
pixi run mojo-embed
pixi run mojo-index
```

---

## Documentation Update Workflow

### Sync Upstream Documentation
```bash
# For Mojo manual from Modular repo
bash tools/sync_documentation.sh mojo \
  https://github.com/modularml/mojo.git \
  docs/manual \
  source-documentation/mojo/manual

# This will:
# 1. Clone/pull the repo
# 2. Copy docs to correct location
# 3. Optionally commit with timestamp
# 4. Log the sync activity
```

### Automated Updates with GitHub Actions
Create `.github/workflows/sync_docs.yml`:
- Run on schedule (e.g., weekly)
- Sync upstream documentation
- Run build pipeline if docs changed
- Create pull request with updated databases

### Manual Rebuild
```bash
# After docs are updated, rebuild:
pixi run mojo-process
pixi run mojo-embed
pixi run mojo-consolidate
pixi run mojo-load
pixi run mojo-index

# Commit the rebuilt database files
git add servers/mojo-manual-mcp/runtime/*.db
git commit -m "chore: Rebuild Mojo MCP database with latest docs"
```

---

## Rollback Strategy

If issues arise during any phase:

1. **Before starting phase**:
   ```bash
   git checkout main
   git pull
   ```

2. **During phase (if major issue)**:
   ```bash
   git reset --hard main  # Discard all changes in current branch
   git checkout -b restructure/[phase]-retry
   # Start over more carefully
   ```

3. **After merge (if discovered issue)**:
   ```bash
   git revert <commit-hash>  # Reverts the problematic merge commit
   # Fix issues in new branch
   git checkout -b restructure/[phase]-fix
   # Re-apply corrections
   ```

---

## Success Criteria

✅ **Phase complete when:**
1. All files in correct locations with correct names
2. All imports resolve correctly
3. All pixi tasks work
4. All scripts run without errors
5. Documentation updated and accurate
6. Git branch clean and ready for merge

✅ **Project complete when:**
1. All 8 phases merged
2. Full test suite passes
3. Can create new MCP server with scaffold script
4. Can distribute individual servers as standalone repos
5. Documentation is comprehensive
6. Both pixi and non-pixi workflows work

---

## Summary

This plan provides a **safe, incremental restructuring** that:
- ✅ Maintains git history (easy rollback)
- ✅ Breaks work into manageable phases
- ✅ Allows parallel review processes
- ✅ Supports both pixi and pip-based workflows
- ✅ Enables easy distribution of servers
- ✅ Provides automation for doc updates
- ✅ Creates completely self-contained servers

**Start with Phase 1, merge to main, then proceed incrementally.**
