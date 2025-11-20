# Quick Start Guide

Get the Mojo documentation MCP server running in under 5 minutes.

## Prerequisites

- **Git** - For cloning the repository
- **Python 3.10+** - Required for running the MCP server
- **Pixi** (optional but recommended) - For simplified dependency management

Check your Python version:
```bash
python3 --version  # Should show 3.10 or higher
```

## Choose Your Path

### Option A: Quick Start with Pixi (Recommended)

**Step 1**: Install pixi (if not already installed)

```bash
# macOS/Linux
curl -fsSL https://pixi.sh/install.sh | bash

# Or visit: https://prefix.dev/docs/pixi/overview
```

**Step 2**: Clone and setup

```bash
git clone <your-repo-url>
cd mcp
pixi install  # Installs all dependencies automatically
```

**Step 3**: Start the MAX embedding server

```bash
pixi run max-serve
# Leave this terminal running
```

**Step 4**: Test with MCP Inspector (in a new terminal)

```bash
cd mcp
pixi run mcp-dev
```

This opens the MCP Inspector in your browser where you can:
- View available tools and resources
- Test search queries
- Explore documentation chunks

**Step 5**: Configure for VS Code (optional)

Add to your VS Code settings (`.vscode/settings.json` or user settings):

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

**Replace `/absolute/path/to/mcp`** with your actual path. Get it with:
```bash
cd mcp && pwd
```

### Option B: Quick Start with Python venv

**Step 1**: Clone the repository

```bash
git clone <your-repo-url>
cd mcp
```

**Step 2**: Create virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r servers/mojo-manual-mcp/requirements.txt
```

**Step 3**: Install and start MAX server

```bash
# Install MAX (if not already installed)
pip install max-cli

# Start MAX embedding server
max serve --model sentence-transformers/all-mpnet-base-v2
# Leave this terminal running
```

**Step 4**: Run the MCP server (in a new terminal)

```bash
cd mcp
source venv/bin/activate  # Activate venv again
python servers/mojo-manual-mcp/runtime/mojo_manual_mcp_server.py
```

**Step 5**: Configure for VS Code (same as Option A above)

## Testing Your Setup

Once configured in VS Code:

1. Open VS Code
2. Open the Command Palette (Cmd/Ctrl+Shift+P)
3. Look for MCP-related commands or check your Copilot chat

Try asking questions like:
- "What is ownership in Mojo?"
- "How do I declare a variable?"
- "Explain Mojo's memory management"

## Troubleshooting

### Issue: "MAX server not running"

**Solution**: Make sure the MAX server is started in a separate terminal:
```bash
pixi run max-serve
# or
max serve --model sentence-transformers/all-mpnet-base-v2
```

### Issue: "Cannot find database file"

**Solution**: Ensure you're using absolute paths in your VS Code configuration. Get the path:
```bash
cd mcp
echo "$(pwd)/servers/mojo-manual-mcp/runtime/mojo_manual_mcp.db"
```

### Issue: "Module not found" errors

**Solution**: Make sure dependencies are installed:
```bash
# With pixi:
pixi install

# With venv:
source venv/bin/activate
pip install -r servers/mojo-manual-mcp/requirements.txt
```

### Issue: MAX server fails to start

**Solution**: Check if port 8000 is already in use:
```bash
lsof -i :8000  # macOS/Linux
# Kill the process if needed, then restart MAX
```

### Issue: Search returns no results

**Solution**: Verify the database exists and is not empty:
```bash
ls -lh servers/mojo-manual-mcp/runtime/*.db
# Should show mojo_manual_mcp.db with size > 50MB
```

If the database is missing or small, you may need to rebuild it:
```bash
pixi run mojo-build  # Runs full build pipeline
```

## Next Steps

- **Learn more about setup**: See [SETUP_PIXI.md](SETUP_PIXI.md) or [SETUP_VENV.md](SETUP_VENV.md)
- **Using in your IDE**: See [USING_MCP_SERVER.md](USING_MCP_SERVER.md)
- **Build from scratch**: See [SETUP_PIXI.md](SETUP_PIXI.md#rebuilding-from-source)
- **Create new servers**: See [CREATING_NEW_MCP.md](CREATING_NEW_MCP.md)

## Common Use Cases

### Querying Documentation

The MCP server provides two main ways to access documentation:

1. **Search tool**: Ask questions naturally
   - "How do I use decorators in Mojo?"
   - "What's the difference between var and let?"

2. **Resource access**: Browse by chunk ID
   - `mojo://chunk/{chunk_id}` - View specific documentation chunk
   - `mojo://search/{query}` - Perform hybrid search

### Integration with AI Tools

Once configured, the MCP server seamlessly integrates with:
- **GitHub Copilot** in VS Code
- **Claude Desktop** (with MCP support)
- **Any MCP-compatible client**

Your AI assistant will automatically have access to Mojo documentation for answering questions.

## Getting Help

- **Documentation issues**: Check [USING_MCP_SERVER.md](USING_MCP_SERVER.md)
- **Build issues**: See [SETUP_PIXI.md](SETUP_PIXI.md) or [SETUP_VENV.md](SETUP_VENV.md)
- **Development questions**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Architecture questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Time to complete**: ~5 minutes  
**Difficulty**: Beginner  
**Status**: Production Ready
