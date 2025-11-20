# Using the MCP Server

Complete guide for using the MCP documentation search server in VS Code, Claude Desktop, and other MCP-compatible clients.

## Table of Contents

- [Overview](#overview)
- [VS Code Setup](#vs-code-setup)
- [Claude Desktop Setup](#claude-desktop-setup)
- [Available Tools and Resources](#available-tools-and-resources)
- [Example Queries](#example-queries)
- [Understanding Search Results](#understanding-search-results)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Overview

The MCP server provides AI assistants with searchable access to documentation through:

- **Tools**: Functions the AI can call (e.g., `search`)
- **Resources**: URIs the AI can access (e.g., `mojo://search/*`, `mojo://chunk/*`)

### What Can the AI Do?

With the MCP server configured:
- Answer questions about Mojo programming
- Provide code examples from documentation
- Explain concepts with direct documentation references
- Search for specific topics or terms
- Navigate documentation structure

## VS Code Setup

### Prerequisites

- VS Code with GitHub Copilot extension installed
- MCP server setup complete (see [QUICKSTART.md](QUICKSTART.md))
- MAX embedding server running (or `AUTO_START_MAX=1` set)

### Configuration

1. **Get your absolute paths**:

```bash
cd /path/to/mcp
echo "Python: $(which python)"  # If using venv, use venv python
echo "Server: $(pwd)/servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"
echo "Database: $(pwd)/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db"
```

2. **Add to VS Code settings**:

Open settings: `Cmd/Ctrl+Shift+P` → "Preferences: Open User Settings (JSON)"

Add this configuration:

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

**Key Configuration Options**:

- `command`: Python executable (use venv python if applicable)
- `args`: Absolute path to the MCP server script
- `MOJO_DB_PATH`: Absolute path to the indexed database
- `MAX_SERVER_URL`: Embedding server endpoint (default: `http://localhost:8000/v1`)
- `EMBED_MODEL_NAME`: Sentence transformer model name
- `AUTO_START_MAX`: 
  - `"1"` = Auto-start MAX server (recommended for VS Code)
  - `"0"` = Manually start MAX server

3. **Reload VS Code**:

`Cmd/Ctrl+Shift+P` → "Developer: Reload Window"

### Verification

Open Copilot chat and ask:
```
@mojo-docs What is ownership in Mojo?
```

Or simply:
```
Explain Mojo's memory management
```

Copilot should use the MCP server to fetch relevant documentation.

### Workspace-Specific Configuration

For project-specific settings, create `.vscode/settings.json` in your project:

```json
{
  "mcpServers": {
    "mojo-docs": {
      "command": "/path/to/mcp/venv/bin/python",
      "args": ["/path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"],
      "env": {
        "MOJO_DB_PATH": "/path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

## Claude Desktop Setup

### Prerequisites

- Claude Desktop app with MCP support
- MCP server setup complete
- MAX embedding server running manually (Claude Desktop doesn't support `AUTO_START_MAX`)

### Configuration

1. **Locate Claude Desktop config file**:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add server configuration**:

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
        "AUTO_START_MAX": "0"
      }
    }
  }
}
```

**Note**: Set `AUTO_START_MAX=0` and start MAX server manually:

```bash
# With pixi:
pixi run max-serve

# With venv:
source venv/bin/activate
max serve --model sentence-transformers/all-mpnet-base-v2
```

3. **Restart Claude Desktop**

### Verification

Ask Claude:
```
Search the Mojo documentation for information about ownership
```

Claude should use the MCP server to access documentation.

## Available Tools and Resources

### Tools

The MCP server exposes these tools that AI assistants can call:

#### `search` Tool

Performs hybrid search (vector + keyword) on documentation.

**Parameters**:
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of results (default: 5)

**Example usage by AI**:
```
User: "How do I use decorators in Mojo?"
AI: [Calls search tool with query="Mojo decorators usage"]
AI: Based on the documentation...
```

### Resources

Resources are URI-based content that can be accessed:

#### `mojo://search/{query}`

Performs a search and returns results.

**Example**: `mojo://search/ownership%20in%20mojo`

#### `mojo://chunk/{chunk_id}`

Retrieves a specific documentation chunk by ID.

**Example**: `mojo://chunk/basics-001`

### How AI Assistants Use These

When you ask a question:

1. **AI decides** to use documentation
2. **AI calls** the `search` tool with your query
3. **Server searches** using hybrid (vector + keyword) search
4. **AI receives** relevant chunks with snippets and URLs
5. **AI formulates** response with documentation context

## Example Queries

### Basic Questions

```
What is ownership in Mojo?
```

Expected: AI searches documentation and explains ownership concept with examples.

```
How do I declare a variable?
```

Expected: AI finds variable declaration syntax and examples.

### Code Examples

```
Show me an example of using decorators in Mojo
```

Expected: AI retrieves decorator documentation and provides code samples.

```
What's the difference between var and let?
```

Expected: AI explains variable vs. constant with documentation references.

### Conceptual Questions

```
Explain Mojo's memory management system
```

Expected: AI searches for memory management topics and provides comprehensive explanation.

```
How does Mojo handle GPU computation?
```

Expected: AI finds GPU-related documentation and explains the concepts.

### Specific Topics

```
What are the available Mojo decorators?
```

Expected: AI searches decorator documentation and lists them.

```
How do I use pointers in Mojo?
```

Expected: AI retrieves pointer documentation with usage examples.

## Understanding Search Results

### Result Structure

Each search result includes:

- **Title**: Document or section title
- **Content Snippet**: Relevant excerpt (with query terms highlighted)
- **URL**: Link to original documentation
- **Section Hierarchy**: Document structure path
- **Relevance Score**: Hybrid search score

### Hybrid Search Explained

The server uses two search methods:

1. **Vector Search (Semantic)**:
   - Finds conceptually similar content
   - Example: "variable declaration" matches "how to define a variable"
   - Uses 768-dimensional embeddings via sentence-transformers

2. **Keyword Search (BM25)**:
   - Matches exact terms and phrases
   - Example: "decorator" finds documents containing "decorator"
   - Weighted by field (title has 2x weight vs content)

3. **Reciprocal Rank Fusion (RRF)**:
   - Combines both rankings intelligently
   - Balances semantic similarity with keyword relevance

### Quality Indicators

Good results have:
- High relevance score (both vector and keyword)
- Clear context in snippet
- Relevant section hierarchy
- Direct URL to documentation

## Customization

### Adjusting Search Behavior

Edit `servers/mojo-manual-mcp/config/server_config.yaml`:

```yaml
search:
  top_k: 5                    # Number of results (1-20)
  fts_title_weight: 2.0       # Keyword search: title weight
  fts_content_weight: 1.0     # Keyword search: content weight
  rrf_k: 60                   # RRF parameter (lower = more fusion)
```

**After editing**: Restart the MCP server (reload VS Code or restart Claude).

### Using Different Embedding Models

Edit `servers/mojo-manual-mcp/config/server_config.yaml`:

```yaml
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"  # Faster, smaller
  # or
  model_name: "sentence-transformers/all-mpnet-base-v2"  # Default, better quality
```

**After editing**: 
1. Restart MAX server with new model
2. Restart MCP server

**Trade-offs**:
- `all-MiniLM-L6-v2`: Faster queries, lower quality embeddings
- `all-mpnet-base-v2`: Slower queries, higher quality embeddings

### Changing MAX Server Port

If port 8000 is unavailable:

1. Start MAX on different port:
```bash
max serve --model sentence-transformers/all-mpnet-base-v2 --port 8001
```

2. Update `MAX_SERVER_URL` in VS Code/Claude config:
```json
"env": {
  "MAX_SERVER_URL": "http://localhost:8001/v1",
  ...
}
```

## Troubleshooting

### AI Doesn't Use Documentation

**Symptoms**: AI answers questions without referencing MCP server

**Causes**:
1. MCP server not configured correctly
2. Server not running
3. AI doesn't recognize when to use it

**Solutions**:
```
# 1. Verify server is in settings
Check VS Code settings or Claude Desktop config

# 2. Check server logs
Look for startup messages or errors

# 3. Explicitly mention the server
Ask: "@mojo-docs what is ownership?"
Or: "Search the Mojo documentation for..."
```

### "Server Connection Failed" Error

**Causes**:
1. Wrong paths in configuration
2. Python not found
3. Dependencies missing

**Solutions**:
```bash
# Verify Python path
which python  # Should point to correct Python

# Verify server file exists
ls -l /path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py

# Test server manually
python /path/to/server.py
# Should start without errors
```

### "MAX Server Not Running" Error

**Cause**: Embedding server not accessible

**Solutions**:
```bash
# Check if MAX is running
curl http://localhost:8000/v1/models
# Should return model information

# Start MAX server
pixi run max-serve
# or
max serve --model sentence-transformers/all-mpnet-base-v2

# Or set AUTO_START_MAX=1 in VS Code config
```

### Slow Search Responses

**Causes**:
1. MAX server on CPU (not GPU)
2. Large result set
3. Network latency

**Solutions**:
- Use GPU for MAX if available
- Reduce `top_k` in config (fewer results = faster)
- Use smaller embedding model (all-MiniLM-L6-v2)

### Search Returns Irrelevant Results

**Causes**:
1. Query too vague
2. Documentation doesn't cover topic
3. Search weights need tuning

**Solutions**:
- Be more specific in queries
- Check if topic exists in documentation
- Adjust search weights in server_config.yaml:
  ```yaml
  # For more keyword matching
  fts_title_weight: 3.0
  fts_content_weight: 2.0
  
  # For more semantic matching
  # (keep weights lower, increase RRF fusion)
  ```

### "Database Not Found" Error

**Cause**: Database path incorrect or file missing

**Solutions**:
```bash
# Verify database exists
ls -lh /path/to/mcp/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db

# Check size (should be ~50-100MB)
# If missing or empty, rebuild:
pixi run mojo-build
# or follow manual build steps
```

## Advanced Usage

### Multiple Documentation Servers

You can configure multiple MCP servers for different documentation sources:

```json
{
  "mcpServers": {
    "mojo-docs": {
      "command": "python",
      "args": ["/path/to/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py"],
      ...
    },
    "duckdb-docs": {
      "command": "python",
      "args": ["/path/to/duckdb-docs-mcp/runtime/duckdb_docs_mcp_server.py"],
      ...
    }
  }
}
```

The AI can then search multiple documentation sources:
```
Compare ownership in Mojo vs memory management in Rust
```

### Programmatic Access

You can also use the MCP server programmatically:

```python
import subprocess
import json

# Start server
process = subprocess.Popen(
    ["python", "/path/to/mojo_manual_mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Send MCP protocol messages
# (See MCP specification for protocol details)
```

## Best Practices

### For Better Results

1. **Be specific**: "How do I use @parameter decorator?" vs "Explain decorators"
2. **Use keywords**: Include technical terms from documentation
3. **Ask follow-ups**: AI has context from previous searches
4. **Reference examples**: "Show me an example of..." triggers code search

### For Performance

1. **Keep MAX running**: Don't start/stop between queries
2. **Use AUTO_START_MAX**: In VS Code for convenience
3. **Limit results**: Default top_k=5 is usually sufficient
4. **Use workspace config**: Project-specific settings load faster

### For Accuracy

1. **Verify responses**: Check provided documentation URLs
2. **Ask for sources**: "Where in the documentation does it say this?"
3. **Cross-reference**: Compare multiple documentation chunks
4. **Report issues**: If results seem wrong, check database freshness

## Next Steps

- **Create new servers**: See [CREATING_NEW_MCP.md](CREATING_NEW_MCP.md)
- **Understand architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Setup guide**: See [QUICKSTART.md](QUICKSTART.md), [SETUP_PIXI.md](SETUP_PIXI.md), or [SETUP_VENV.md](SETUP_VENV.md)

---

**Integration**: VS Code, Claude Desktop, any MCP-compatible client  
**Search Quality**: Hybrid (vector + keyword) with RRF fusion  
**Response Time**: <100ms typical (after initial load)
