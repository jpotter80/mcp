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
### Option A: Quick Start with Pixi (Recommended)

**Step 1**: Install pixi (if not already installed)

```bash
# macOS/Linux
curl -fsSL https://pixi.sh/install.sh | bash

# Or visit: https://pixi.sh/latest/
```

**Step 2**: Clone and setup

```bash
git clone jpotter80/mcp
cd mcp/servers/mojo-manual-mcp
pixi install  # Installs all dependencies automatically
```

**Step 3**: Configure for VS Code

Add to your VS Code user settings (`~/.config/Code/User/mcp.json` on Linux, or via Settings GUI):

```json
{
  "servers": {
    "mojo-manual": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "serve"],
      "cwd": "/path/to/mojo-manual-mcp"
    }
  }
}
```

Replace `/path/to/mojo-manual-mcp` with your actual server path. Get it with:
```bash
cd mcp/servers/mojo-manual-mcp && pwd
```



## Next Steps

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
- **Any MCP-compatible client**

Your AI assistant will automatically have access to Mojo documentation for answering questions.

## Getting Help

- **Architecture questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)

---
