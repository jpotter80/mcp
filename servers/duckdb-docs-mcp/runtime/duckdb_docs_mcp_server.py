"""
Template for MCP server exposing documentation search via resources and tools.
This file should be copied to servers/{mcp-name}/runtime/{mcp_name}_mcp_server.py and adapted.

Usage patterns:
- Replace placeholders like duckdb-docs-mcp with actual values during scaffolding
- Update resource URIs and tool descriptions to match your documentation
- Customize search result formatting as needed for your use case

Requires: pip install "mcp[cli]"
Run (dev inspector): mcp dev {mcp_name}_mcp_server.py
"""

from typing import List, Optional, AsyncIterator, Any
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import os
import socket
import time
import subprocess

import requests

try:
    from mcp.server.fastmcp import FastMCP, Context
except Exception as e:  # pragma: no cover - helpful message if not installed
    raise RuntimeError(
        "The 'mcp' package is required. Install with: pip install \"mcp[cli]\""
    ) from e

from pydantic import BaseModel, Field

# Ensure runtime dir and project root are on sys.path
_RUNTIME_DIR = Path(__file__).resolve().parent
_SERVER_ROOT = _RUNTIME_DIR.parent
_PROJECT_ROOT = _SERVER_ROOT.parent.parent

if str(_RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_DIR))

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Try to import config loader from shared, fallback to simple yaml load
try:
    from shared.config_loader import load_config_with_substitution as load_config
except ImportError:
    import yaml
    def load_config(config_path, server_root=None):
        with open(config_path, "r") as f:
            content = f.read()
            if server_root:
                content = content.replace("${SERVER_ROOT}", str(server_root))
            return yaml.safe_load(content)

# Import search module
# Note: This import will work once the template is copied to a server's runtime directory
import search as search_mod  # noqa: E402
HybridSearcher = search_mod.HybridSearcher
TOP_K = search_mod.TOP_K


# Structured result model for tools
class SearchResult(BaseModel):
    chunk_id: str
    title: str
    url: str
    section_hierarchy: Optional[List[str]] = Field(default=None)
    snippet: str


class AppState:
    def __init__(
        self, searcher: Any, max_proc: Optional[subprocess.Popen] = None
    ) -> None:  # type: ignore[name-defined]
        self.searcher = searcher
        self.max_proc = max_proc


def _parse_host_port_from_url(url: str) -> tuple[str, int]:
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        return host, port
    except Exception:
        return ("localhost", 8000)


def _tcp_connect_ok(host: str, port: int, timeout_s: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except Exception:
        return False


def _http_probe_ok(url: str, timeout_s: float = 0.75) -> bool:
    try:
        # Any HTTP response means the server is up; 404 is fine
        requests.get(url, timeout=timeout_s)
        return True
    except Exception:
        return False


def _ensure_max_running(
    base_url: str, model_name: str, auto_start: bool = True, wait_s: float = 20.0
) -> Optional[subprocess.Popen]:  # type: ignore[name-defined]
    """Ensure a MAX embeddings server is reachable at base_url. Optionally auto-start.

    Returns a subprocess handle if we started it, else None.
    """
    host, port = _parse_host_port_from_url(base_url)
    if _tcp_connect_ok(host, port) or _http_probe_ok(base_url):
        return None

    if not auto_start:
        return None

    # Start MAX server; hide stdio to avoid corrupting MCP stdio transport
    try:
        proc = subprocess.Popen(
            [
                os.environ.get("MAX_BINARY", "max"),
                "serve",
                "--model",
                model_name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    except Exception:
        return None

    # Wait for readiness (poll TCP/HTTP)
    deadline = time.time() + max(0.0, wait_s)
    while time.time() < deadline:
        if proc.poll() is not None:
            # process exited early
            return None
        if _tcp_connect_ok(host, port) or _http_probe_ok(base_url):
            return proc
        time.sleep(0.5)
    return proc  # may not be ready yet; caller can still proceed with FTS-only fallback


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppState]:
    """Startup/shutdown lifecycle to manage shared searcher."""
    
    # Load configuration
    config_path = _SERVER_ROOT / "config" / "server_config.yaml"
    config = {}
    if config_path.exists():
        try:
            config = load_config(str(config_path), server_root=_SERVER_ROOT)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}", file=sys.stderr)
    
    # Extract config values with fallbacks
    db_config = config.get("database", {})
    embed_config = config.get("embedding", {})
    search_config = config.get("search", {})
    
    # Resolve DB path relative to runtime dir if not absolute
    raw_db_path = db_config.get("path", os.getenv("DUCKDB_DOCS_MCP_DB_PATH", "duckdb_docs_mcp.db"))
    if not os.path.isabs(raw_db_path):
        if str(raw_db_path).startswith(str(_SERVER_ROOT)):
             db_path = raw_db_path
        else:
             db_path = str(_RUNTIME_DIR / raw_db_path)
    else:
        db_path = raw_db_path

    table_name = db_config.get("table_name", os.getenv("DUCKDB_DOCS_MCP_TABLE_NAME", "duckdb_docs_indexed"))
    
    base_url = embed_config.get("max_server_url", os.getenv("MAX_SERVER_URL", "http://localhost:8000/v1"))
    model_name = embed_config.get("model_name", os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-mpnet-base-v2"))
    
    auto_start_val = embed_config.get("auto_start", os.getenv("AUTO_START_MAX", "1"))
    if isinstance(auto_start_val, str):
        auto_start = auto_start_val.lower() not in ("false", "0", "no")
    else:
        auto_start = bool(auto_start_val)
        
    embed_cache_size = search_config.get("embed_cache_size", int(os.getenv("EMBED_CACHE_SIZE", "512")))

    # Optionally auto-start MAX embeddings server if not reachable
    max_proc = _ensure_max_running(base_url, model_name, auto_start=auto_start)

    searcher = HybridSearcher(
        db_path=db_path,
        table_name=table_name,
        max_server_url=base_url,
        model_name=model_name,
        embed_cache_size=embed_cache_size
    )  # opens read-only DuckDB, loads vss+fts
    try:
        yield AppState(searcher=searcher, max_proc=max_proc)
    finally:
        try:
            searcher.close()
        except Exception:
            pass
        # Clean up spawned MAX process if we started it
        try:
            if isinstance(max_proc, subprocess.Popen) and max_proc.poll() is None:  # type: ignore[arg-type]
                max_proc.terminate()
        except Exception:
            pass


mcp = FastMCP("Duckdb Docs", lifespan=app_lifespan)


def _make_results(searcher: Any, query: str, k: int = TOP_K) -> List[SearchResult]:
    ids = searcher.hybrid_search(query, k=k)
    rows = searcher.get_results_by_ids(ids)
    out: List[SearchResult] = []
    for chunk_id, title, content, url, section_hierarchy in rows:
        snippet = (content[:500] + ("…" if len(content) > 500 else "")).replace(
            "\n", " "
        )
        out.append(
            SearchResult(
                chunk_id=str(chunk_id),
                title=title or "",
                url=url or "",
                section_hierarchy=section_hierarchy if section_hierarchy else None,
                snippet=snippet,
            )
        )
    return out


@mcp.tool()
def search(
    query: str, k: int = TOP_K, ctx: Optional[Context] = None
) -> List[SearchResult]:
    """Hybrid search over docs documentation. Returns top-k results with snippets.

    Args:
      query: The natural language query.
      k: Number of results to return.
    """
    assert ctx is not None
    state: AppState = ctx.request_context.lifespan_context  # type: ignore[assignment]
    return _make_results(state.searcher, query, k=k)


@mcp.resource("duckdb-docs-mcp://search/{q}")
def search_resource(q: str, ctx: Optional[Context] = None) -> str:
    """Dynamic resource that returns a markdown view of top results for a query."""
    assert ctx is not None
    state: AppState = ctx.request_context.lifespan_context  # type: ignore[assignment]
    results = _make_results(state.searcher, q, k=TOP_K)
    lines: List[str] = [f"# Search results for: {q}"]
    for i, r in enumerate(results, start=1):
        path = " > ".join(r.section_hierarchy) if r.section_hierarchy else ""
        lines.append(f"\n## {i}. {r.title}\n")
        if path:
            lines.append(f"Section: {path}\n")
        lines.append(f"URL: {r.url}\n")
        lines.append(r.snippet)
    return "\n".join(lines)


@mcp.resource("duckdb-docs-mcp://chunk/{chunk_id}")
def chunk_resource(chunk_id: str, ctx: Optional[Context] = None) -> str:
    """Return a single chunk by id as markdown (title, section, content, url)."""
    assert ctx is not None
    state: AppState = ctx.request_context.lifespan_context  # type: ignore[assignment]
    rows = state.searcher.get_results_by_ids([chunk_id])
    if not rows:
        return f"Chunk {chunk_id} not found"
    cid, title, content, url, section_hierarchy = rows[0]
    path = " > ".join(section_hierarchy) if section_hierarchy else ""
    parts = [f"# {title}"]
    if path:
        parts.append(f"Section: {path}")
    parts.append(f"URL: {url}")
    parts.append("")
    parts.append(content)
    return "\n\n".join(parts)


if __name__ == "__main__":
    # Allow direct execution for convenience (e.g., python {mcp_name}_mcp_server.py)
    mcp.run()
