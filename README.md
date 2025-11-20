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

### Option 1: Using Pixi (Recommended)

```bash
# 1. Clone and install dependencies
git clone <your-repo-url>
cd mcp
pixi install

# 2. Start MAX embedding server (if not already running)
pixi run max-serve

# 3. Use the MCP server
pixi run mcp-dev  # Opens MCP Inspector
# or add to VS Code config (see Configuration section below)
```

### Option 2: Using Python venv

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd mcp
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r servers/mojo-manual-mcp/requirements.txt

# 2. Run the MCP server
python servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
```

**Note**: Pre-built databases are included in the repository. No build step required to run the server.

📖 **Detailed guides**: See [`docs/QUICKSTART.md`](docs/QUICKSTART.md) for complete setup instructions.

## ⚙️ VS Code Configuration

Add the Mojo MCP server to your VS Code settings:

```json
{
  "mcpServers": {
    "mojo-docs": {
      "command": "python",
      "args": [
        "/absolute/path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"
      ],
      "env": {
        "MOJO_DB_PATH": "/absolute/path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db",
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

**Environment Variables**:
- `MOJO_DB_PATH`: Path to the indexed database
- `MAX_SERVER_URL`: Embedding server endpoint (automatically started if `AUTO_START_MAX=1`)
- `EMBED_MODEL_NAME`: Sentence transformer model name
- `AUTO_START_MAX`: Set to `1` to auto-start MAX server (recommended)

📖 **More details**: See [`docs/USING_MCP_SERVER.md`](docs/USING_MCP_SERVER.md)

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
- [`docs/SETUP_PIXI.md`](docs/SETUP_PIXI.md) - Full pixi-based development setup
- [`docs/SETUP_VENV.md`](docs/SETUP_VENV.md) - Setup without pixi
- [`docs/CREATING_NEW_MCP.md`](docs/CREATING_NEW_MCP.md) - Create new servers

## 📋 Available Servers

Currently implemented:

| Server | Documentation Source | Format | Status |
|--------|---------------------|--------|--------|
| **mojo-manual-mcp** | [Mojo Manual](https://docs.modular.com/mojo/manual) | MDX | ✅ Production |

Coming soon:
- **duckdb-docs-mcp** - DuckDB documentation
- **python-docs-mcp** - Python standard library
- **vscode-api-mcp** - VS Code extension API

## 📚 Documentation

### For Users

| Document | Purpose |
|----------|---------|
| [QUICKSTART.md](docs/QUICKSTART.md) | Get started in 5 minutes |
| [SETUP_PIXI.md](docs/SETUP_PIXI.md) | Complete setup with pixi |
| [SETUP_VENV.md](docs/SETUP_VENV.md) | Setup without pixi (venv) |
| [USING_MCP_SERVER.md](docs/USING_MCP_SERVER.md) | Using servers in VS Code/IDEs |

### For Developers

| Document | Purpose |
|----------|---------|
| [CREATING_NEW_MCP.md](docs/CREATING_NEW_MCP.md) | Create new MCP servers |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and architecture |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | Contribution guidelines |
| [tools/README.md](tools/README.md) | Automation scripts reference |

## 🛠️ Key Technologies

- **Python 3.10+** — Core language for preprocessing and runtime
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

```
User: "How do I declare a variable in Mojo?"
  ↓
1. Query embedding generated via MAX server
2. Vector search finds semantically similar chunks
3. Keyword search finds chunks with "declare" + "variable"
4. RRF fusion combines results
5. Top 5 chunks returned with snippets + URLs
  ↓
Response: Relevant documentation sections with context
```

## 🤝 Contributing

We welcome contributions! Please see [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for:
- Code of conduct
- Development workflow
- Pull request process
- Adding new MCP servers
- Reporting issues

## 🔗 External Resources

- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- [DuckDB Documentation](https://duckdb.org/docs) - Database engine docs
- [DuckDB VSS Extension](https://duckdb.org/docs/extensions/vss) - Vector similarity search
- [MAX Documentation](https://github.com/modularml/max) - Embedding server
- [Mojo Documentation](https://docs.modular.com/mojo/manual) - Example documentation source

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

Built with inspiration from the Model Context Protocol community and powered by open-source tools.

---

**Last Updated**: November 2025  
**Status**: Production Ready (v2.0 - Multi-Server Architecture)
