# Multi-Server MCP Documentation Search

A framework for building self-contained, searchable MCP servers from technical documentation. Create independent documentation servers with hybrid vector + keyword search, ready to distribute and deploy.

## 🎯 Project Overview

This framework enables you to:

1. **Build** searchable MCP servers from any Markdown/MDX documentation source
2. **Search** with hybrid semantic (vector) + keyword (FTS) search via Reciprocal Rank Fusion
3. **Distribute** self-contained servers as standalone repositories or packages
4. **Deploy** to VS Code, Claude Desktop, or any MCP-compatible host
5. **Scale** to multiple documentation sources with automated tooling

### Core Value Proposition

- 🔍 **Hybrid Search**: Combines semantic similarity (HNSW) and keyword matching (BM25) intelligently
- 📦 **Self-Contained Servers**: Each MCP server is fully standalone and distributable
- 🚀 **Multi-Format Support**: Works with MDX, Markdown, and other documentation formats
- 🎛️ **Config-Driven**: All paths and parameters controlled via YAML configuration
- 💾 **Versioned Data**: DuckLake provides reproducible documentation snapshots
- 🔄 **Automated Tooling**: Scripts for syncing, scaffolding, and building new servers

## 📐 Multi-Server Architecture

This project supports multiple independent MCP servers, each serving different documentation sources:

```
/home/james/mcp/
├── servers/                          # Standalone MCP servers
│   ├── mojo-manual-mcp/              # Mojo documentation server
│   │   ├── runtime/                  # Server code + indexed database
│   │   │   ├── mojo_manual_mcp_server.py
│   │   │   ├── search.py
│   │   │   └── mojo_manual_mcp.db
│   │   ├── config/                   # YAML configuration
│   │   │   ├── processing_config.yaml
│   │   │   └── server_config.yaml
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── [future-servers]/             # DuckDB, Python, etc.
│
├── shared/                           # Build-time infrastructure (dev only)
│   ├── preprocessing/                # Document processing pipeline
│   ├── embedding/                    # Embedding generation scripts
│   ├── templates/                    # Templates for new servers
│   └── build/                        # Ephemeral build artifacts
│
├── source-documentation/             # Documentation sources
│   ├── mojo/manual/                  # Mojo docs (MDX files)
│   └── [other-sources]/
│
└── tools/                            # Automation scripts
    ├── sync_documentation.sh         # Sync from upstream repos
    ├── scaffold_new_mcp.sh           # Create new server structure
    └── build_mcp.sh                  # Build server database
```

**Key Design Principles**:
- Each server in `/servers/{name}/` is completely self-contained and distributable
- Shared build infrastructure in `/shared/` is for development only (not packaged with servers)
- All configuration is YAML-based with variable substitution (no hardcoded paths)
- Multi-format support via pluggable processor architecture
- Works with or without pixi (pip + venv supported)

## 🚀 Quick Start

Get the Mojo documentation MCP server running in 3 steps:

### Using Pixi (Recommended)

# 1. Clone and install dependencies

```bash
git clone jpotter80/mcp
cd mcp/servers/mojo-manual-mcp
pixi install
```

# 2. Configure VS Code

Add the Mojo-Manual MCP server, by adding the config to your VS Code settings via mcp.json for global settings. Replace `/absolute/path/to/mojo-manual-mcp` with your actual server path.

```json
{
  "servers": {
    "mojo-manual": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "serve"],
      "cwd": "/absolute/path/to/mojo-manual-mcp"
    }
  }
}
```

# 3. From the mcp.json file in VS Code, if properly configured, the server will show a start button to launch the server. From then on, VS Code will manage starting/stopping the server as needed.



**Note**: Pre-built databases are included in the repository. No build step required to run the server.

📖 **Detailed guides**: See [`docs/QUICKSTART.md`](docs/QUICKSTART.md) for complete setup instructions.

**Environment Variables**:
- `MOJO_DB_PATH`: Path to the indexed database
- `MAX_SERVER_URL`: Embedding server endpoint (automatically started if `AUTO_START_MAX=1`)
- `EMBED_MODEL_NAME`: Sentence transformer model name
- `AUTO_START_MAX`: Set to `1` to auto-start MAX server (recommended)

## 🏗️ Building from Source

If you want to rebuild the database from scratch or create a new MCP server:

### Rebuild Mojo Server

```bash
# Full pipeline (all steps)
pixi run mojo-build

# Or step-by-step
pixi run mojo-process              # Process documentation
pixi run mojo-generate-embeddings  # Generate vectors
pixi run mojo-consolidate          # Consolidate data
pixi run mojo-load                 # Load to DuckLake
pixi run mojo-index                # Create indexes
```

### Create a New MCP Server

```bash
# 1. Scaffold new server structure
./tools/scaffold_new_mcp.sh --name duckdb --doc-type docs --format markdown

# 2. Add documentation to source-documentation/duckdb/docs/

# 3. Build the server
./tools/build_mcp.sh --mcp-name duckdb

# 4. Test the server
python servers/duckdb-docs-mcp/runtime/duckdb_docs_mcp_server.py
```

📖 **Developer guides**: 
- [`docs/CREATING_NEW_MCP.md`](docs/CREATING_NEW_MCP.md) - Create new servers

## 📋 Available Servers

Currently implemented:

| Server | Documentation Source | Format | Status |
|--------|---------------------|--------|--------|
| **mojo-manual-mcp** | [Mojo Manual](https://docs.modular.com/mojo/manual) | MDX | ✅ Production |

Coming soon:
- **duckdb-docs-mcp** - DuckDB documentation

## 🛠️ Key Technologies

- **Python 3.12+** — Core language for preprocessing and runtime
- **DuckDB** — Vector similarity search (HNSW) + full-text search (BM25)
- **DuckLake** — Versioned data lake for reproducible builds
- **MAX** — Local sentence-transformers embedding server
- **MCP** — Model Context Protocol for AI agent integration
- **Pixi** — Package management and task automation (optional)

## 🎓 How It Works

### Build Pipeline

1. **Preprocessing**: MDX/Markdown → cleaned chunks (~350-400 tokens, preserving structure)
2. **Embeddings**: Chunks → 768-dimensional vectors via sentence-transformers
3. **Consolidation**: Merge chunks + embeddings into consolidated Parquet dataset
4. **Versioning**: Load into DuckLake for version-controlled data lake
5. **Indexing**: Materialize into DuckDB with HNSW (vector) + FTS (keyword) indexes

### Runtime Search

- **Vector Search (HNSW)**: Semantic similarity matching via cosine distance
- **Keyword Search (FTS/BM25)**: Exact phrase and term matching with field weighting
- **Hybrid Fusion (RRF)**: Reciprocal Rank Fusion combines both rankings intelligently
- **Graceful Fallback**: If MAX server unavailable, falls back to keyword-only search

### Example Query Flow


User: "How do I declare a variable in Mojo?"
  ↓
1. Query embedding generated via MAX server
2. Vector search finds semantically similar chunks
3. Keyword search finds chunks with "declare" + "variable"
4. RRF fusion combines results
5. Top 5 chunks returned with snippets + URLs
  ↓
Response: Relevant documentation sections with context


## 🔗 External Resources

- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- [DuckDB Documentation](https://duckdb.org/docs) - Database engine docs
- [DuckDB VSS Extension](https://duckdb.org/docs/extensions/vss) - Vector similarity search
- [MAX Documentation](https://docs.modular.com/max/intro) - Embedding server
- [Mojo Documentation](https://docs.modular.com/mojo/manual) - Example documentation source

## 📄 License

 Copyright 2025 James Potter
 
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

## 🙏 Acknowledgments

Built with inspiration from Modular, DuckDB, and the Model Context Protocol communities - powered by open-source tools.

---
