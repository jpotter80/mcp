# MCP Server Configuration Diagnostic Prompt

## Project Context

This is a **Model Context Protocol (MCP) resource server** for searchable Mojo language documentation. The server provides hybrid search (vector + BM25 full-text) over Mojo manual content via MCP tools and resources, intended for use with **VS Code + GitHub Copilot** in a local development environment.

### Technology Stack
- **MCP SDK**: `mcp[cli]` (FastMCP framework)
- **Database**: DuckDB with VSS (vector similarity) and FTS (full-text search) extensions
- **Embeddings**: MAX server (OpenAI-compatible API) using `sentence-transformers/all-mpnet-base-v2`
- **Python Environment**: Managed via Pixi (conda-like package manager)
- **Transport**: stdio (JSON-RPC over stdin/stdout)

---

## Current Project Structure

```
/home/james/mcp/
├── .vscode/
│   └── settings.json              # VS Code MCP server configuration
├── embedding/
│   ├── main.db                    # Original database (created by indexing pipeline)
│   ├── generate_embeddings.py
│   ├── consolidate_data.py
│   ├── load_to_ducklake.py
│   └── create_indexes.py          # Creates HNSW + FTS indexes
├── runtime/                        # 🎯 INTENDED deployment package
│   ├── README.md                  # Claims this is "minimal runtime package"
│   ├── main.db                    # ✓ Copy exists here
│   ├── search.py                  # ✓ Copy exists here (hybrid search logic)
│   ├── server.py                  # ❓ Wrapper file
│   └── mcp_server/
│       └── server.py              # ❓ Another wrapper file
├── mcp_server/
│   └── server.py                  # 🔧 ACTUAL MCP server implementation
├── main.db                         # Copy at project root (used for testing)
├── search.py                       # Original search implementation
└── .pixi/envs/default/             # Python environment with dependencies
```

### File Duplication Status (Confirmed by User)
- **main.db**: Exists in 3 locations (embedding/, project root, runtime/) - all identical copies
- **search.py**: Exists in 2 locations (project root, runtime/) - copies
- **server.py**: Exists in 3 locations with different purposes (see architecture below)

---

## Server Architecture (Current Implementation)

### File: `/home/james/mcp/mcp_server/server.py` (ACTUAL implementation)
- Contains the real FastMCP server logic
- Imports `HybridSearcher` from `search.py` via dynamic import
- Exposes MCP tools: `search(query: str, k: int) -> List[SearchResult]`
- Exposes MCP resources: `mojo://search/{q}` and `mojo://chunk/{chunk_id}`
- Has lifespan management for database connection
- Auto-starts MAX embeddings server if not running

### File: `/home/james/mcp/runtime/mcp_server/server.py` (THIN wrapper)
```python
# Adds project root to sys.path and imports from parent
RUNTIME_DIR = Path(__file__).resolve().parent.parent  # /home/james/mcp/runtime
PROJECT_ROOT = RUNTIME_DIR.parent  # /home/james/mcp
sys.path.insert(0, str(PROJECT_ROOT))
from mcp_server.server import mcp  # Imports from /home/james/mcp/mcp_server/
```
**Purpose**: Allows runtime folder to delegate to project-level implementation

### File: `/home/james/mcp/runtime/server.py` (ANOTHER wrapper)
- Similar import gymnastics
- Purpose unclear - appears redundant

---

## VS Code Configuration (Current - Not Working)

**File**: `/home/james/mcp/.vscode/settings.json`

```json
{
  "mcp.servers": {
    "mojo-docs": {
      "type": "stdio",
      "command": "/home/james/mcp/.pixi/envs/default/bin/python",
      "args": ["/home/james/mcp/runtime/mcp_server/server.py"],
      "cwd": "/home/james/mcp/runtime",
      "env": {
        "MOJO_DB_PATH": "/home/james/mcp/runtime/main.db",
        "MAX_SERVER_URL": "http://localhost:8000/v1",
        "EMBED_MODEL_NAME": "sentence-transformers/all-mpnet-base-v2",
        "AUTO_START_MAX": "1"
      }
    }
  }
}
```

### User-Reported Issue
- **VS Code/GitHub Copilot is NOT recognizing the MCP server**
- User has tried multiple settings.json configurations without success
- No error messages visible to user (unclear if VS Code logs show errors)

---

## Key Technical Constraints

### MCP Resource Server Requirements
1. **stdio Transport**: Server must communicate via JSON-RPC on stdin/stdout
2. **No stdout Pollution**: Cannot use `print()` statements (corrupts protocol)
3. **Capabilities Declaration**: Must properly respond to `initialize` handshake
4. **Tools vs Resources**:
   - **Tools**: Functions LLM can invoke (e.g., `search()`)
   - **Resources**: Static/dynamic content LLM can read (e.g., `mojo://search/{q}`)

### VS Code + GitHub Copilot MCP Integration
- Documentation is sparse compared to Claude Desktop
- Unclear if GitHub Copilot uses the same MCP configuration format
- No official examples found for "mcp.servers" in VS Code settings
- User cannot verify if MCP server is being discovered/loaded

### FastMCP Framework Specifics
- Uses Python decorators: `@mcp.tool()`, `@mcp.resource()`
- Requires `mcp.run()` to start stdio loop
- Supports lifespan context for shared resources (database connections)

---

## Hypothesized Problems

### 1. Import Path Confusion (Circular/Complex)
The wrapper files create a confusing import chain:
```
VS Code calls → runtime/mcp_server/server.py 
              → adds parent to sys.path 
              → imports from /home/james/mcp/mcp_server/server.py
              → which imports search.py from project root
```
**Question**: Is this fragile? Could import resolution fail?

### 2. Settings.json Path Issue
- The args path shows `/home/james/runtime/mcp_server/server.py` (missing "mcp" in path) // User fixed path typo
- Should it be `/home/james/mcp/runtime/mcp_server/server.py`?
- Or should it be a relative path from cwd?

### 3. VS Code MCP Integration Unknown
- Is `"mcp.servers"` the correct settings key for VS Code/Copilot?
- Does GitHub Copilot support MCP at all? (MCP docs focus on Claude Desktop)
- Could this require a VS Code extension to be installed?

### 4. Server Not Exposing Resources Correctly
- FastMCP uses `@mcp.resource()` decorator
- Is the resource URI format correct: `mojo://search/{q}`?
- Do resources require special registration beyond decorators?

### 5. Pixi Environment Activation
- Does VS Code spawn the Python process in a way that respects pixi environment?
- Could dependencies be missing despite pixi.toml being configured?

---

## User's Design Intent (Clarified)

1. **Runtime Package Goal**: A self-contained folder that can be shared/deployed for MCP server usage
2. **Local Usage**: Primary use case is VS Code + GitHub Copilot on user's Linux machine
3. **No Code Changes Yet**: User wants diagnostic understanding first, then structured plan

---

## Diagnostic Questions for LLM to Address

### Architecture Questions
1. **Should the runtime/ folder be truly self-contained**, or is it acceptable to have wrapper files that import from parent project?
2. **Best practice for file duplication**: Should main.db/search.py live ONLY in runtime/, or is the current multi-copy structure acceptable?
3. **Wrapper file necessity**: Are the wrapper files (`runtime/mcp_server/server.py`, `runtime/server.py`) needed, or should runtime/ have a single standalone server.py?

### Configuration Questions
4. **VS Code MCP settings format**: Is `"mcp.servers"` correct for VS Code/GitHub Copilot? Does it match Claude Desktop's configuration?
5. **Path specification**: Should args use absolute paths, relative-to-cwd paths, or module-style paths (`-m mcp.server.run`)?
6. **Python invocation**: Is directly calling `python server.py` correct, or should it be `python -m fastmcp run server.py`?

### MCP Protocol Questions
7. **Resource declaration**: Are resources automatically discovered via `@mcp.resource()` decorator, or do they need explicit registration?
8. **stdio transport debugging**: How can user verify the server is responding to MCP protocol messages correctly?
9. **VS Code MCP integration verification**: How can user confirm VS Code/Copilot is attempting to connect to the server?

### Troubleshooting Questions
10. **Minimal test case**: What's the simplest MCP server configuration that would work with VS Code/Copilot to rule out project-specific issues?
11. **Log visibility**: Where would error messages appear if the server fails to start or encounters import errors?
12. **Alternative approaches**: Should user try different transport (HTTP/SSE) or different client (MCP Inspector CLI) first?

---

## Expected LLM Output

Please provide a structured analysis covering:

### Phase 1: Root Cause Identification
- Determine the most likely reason VS Code/Copilot isn't recognizing the server
- Identify which of the hypothesized problems are actual issues vs. acceptable design choices
- Clarify any misunderstandings about MCP protocol or FastMCP framework

### Phase 2: Architecture Recommendations
- Propose the correct file structure for the runtime/ directory
- Specify whether wrapper files should exist and what they should do
- Define best practices for main.db and search.py placement

### Phase 3: Configuration Solution
- Provide the correct `.vscode/settings.json` format for this use case
- Specify exact paths (absolute vs. relative) and any required arguments
- Include any additional VS Code settings or extensions needed

### Phase 4: Verification Steps
- List manual tests to verify server works in isolation (stdio protocol testing)
- Provide commands to check if VS Code is loading the MCP server
- Suggest debugging approaches to see error messages

### Phase 5: Implementation Plan
- Outline step-by-step changes needed (file moves, edits, configurations)
- Prioritize fixes from critical to optional
- Include rollback steps if changes don't work

---

## Constraints for LLM Response

- **No code generation** until user explicitly requests it
- Focus on **understanding and planning**, not implementation
- Provide **specific, actionable guidance** (not generic advice)
- Address **VS Code/GitHub Copilot specifics** (not just general MCP theory)
- Consider **local development workflow** (not production deployment)

---

## Additional Context

### Working Components (Verified)
- ✓ Database exists with proper indexes (HNSW + FTS)
- ✓ Hybrid search works when tested directly (`pixi run search`)
- ✓ MAX embeddings server can be started and serves embeddings
- ✓ Python environment has all dependencies (mcp, duckdb, openai, etc.)

### Unknown/Unverified
- ❓ Does VS Code actually support MCP via "mcp.servers" config?
- ❓ Does GitHub Copilot have MCP integration enabled by default?
- ❓ Are there VS Code extension logs showing MCP server discovery attempts?
- ❓ Does the FastMCP server respond correctly to initialize handshake?

---

## Success Criteria

The solution is successful when:
1. User can see the MCP server listed in VS Code/GitHub Copilot UI
2. User can invoke the `search` tool from Copilot Chat (e.g., "search for ownership in Mojo docs")
3. User can reference MCP resources in Copilot prompts (e.g., `@mojo://search/ownership`)
4. The runtime/ folder structure is clean, maintainable, and properly documented