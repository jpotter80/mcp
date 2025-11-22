"""
Template for hybrid search implementation using DuckDB VSS + FTS.
This file should be copied to servers/{mcp-name}/runtime/search.py and adapted as needed.

Usage patterns:
- Replace placeholders like duckdb-docs-mcp with actual values during scaffolding
- Update DB_PATH and TABLE_NAME defaults to match your MCP naming convention
- Adjust FTS weights, cache sizes, and other parameters as needed for your use case
"""

from collections import OrderedDict
from openai import OpenAI
import duckdb
import os
import argparse

# --- Configuration ---
_RUNTIME_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_DB_PATH = os.path.join(_RUNTIME_DIR, "duckdb_docs_mcp.db")

DB_PATH = os.getenv("DUCKDB_DOCS_MCP_DB_PATH", _DEFAULT_DB_PATH)
TABLE_NAME = os.getenv("DUCKDB_DOCS_MCP_TABLE_NAME", "duckdb_docs_indexed")
MAX_SERVER_URL = os.getenv("MAX_SERVER_URL", "http://localhost:8000/v1")
MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "sentence-transformers/all-mpnet-base-v2")
TOP_K = 5  # Default number of results to return
# FTS scoring weights (title boosted)
FTS_TITLE_WEIGHT = 2.0
FTS_CONTENT_WEIGHT = 1.0
# Debug/verification flags
DEBUG_EXPLAIN_VSS = False  # when True, prints EXPLAIN of VSS query to confirm HNSW_INDEX_SCAN
DEBUG_LOG_FTS_PATH = False  # when True, prints which FTS path was used
EMBED_CACHE_SIZE = int(os.getenv("EMBED_CACHE_SIZE", "512"))
# --- End Configuration ---


class _LRUCache:
    def __init__(self, capacity: int = 512):
        self.capacity = max(1, capacity)
        self._store: OrderedDict[str, list[float]] = OrderedDict()

    def get(self, key: str):
        if key in self._store:
            self._store.move_to_end(key)
            return self._store[key]
        return None

    def set(self, key: str, value: list[float]):
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self.capacity:
            self._store.popitem(last=False)


class HybridSearcher:
    """
    A class to perform hybrid search (vector + full-text) on the DuckDB database.
    """
    def __init__(
        self,
        db_path=DB_PATH,
        table_name=TABLE_NAME,
        max_server_url=MAX_SERVER_URL,
        model_name=MODEL_NAME,
        embed_cache_size=EMBED_CACHE_SIZE,
    ):
        self.db_path = db_path
        self.table_name = table_name
        self.openai_client = OpenAI(base_url=max_server_url, api_key="EMPTY")
        self._embed_cache = _LRUCache(capacity=embed_cache_size)
        self.db_connection = self._connect()

    def _connect(self):
        """Connects to the DuckDB database and loads required extensions."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found at {self.db_path}. Please run the indexing script first.")
        
        con = duckdb.connect(database=self.db_path, read_only=True)
        con.execute("INSTALL vss;")
        con.execute("LOAD vss;")
        con.execute("INSTALL fts;")
        con.execute("LOAD fts;")
        return con

    def _expand_fts_query(self, query_text: str) -> str:
        """Lightweight synonym expansion for FTS to improve lexical recall.
        
        Customize this method with domain-specific synonyms for your documentation.
        """
        extras: list[str] = []
        
        # Add domain-specific synonym expansions here
        # Example for programming documentation:
        # q = query_text.lower()
        # if "variable" in q or "declare" in q:
        #     extras.extend(["let", "var", "binding", "assign"])
        
        if extras:
            return f"{query_text} " + " ".join(sorted(set(extras)))
        return query_text

    def get_query_embedding(self, query_text: str):
        """Generates an embedding for the user's query."""
        cached = self._embed_cache.get(query_text)
        if cached is not None:
            return cached
        try:
            response = self.openai_client.embeddings.create(
                model=MODEL_NAME,
                input=[query_text],
            )
            emb = response.data[0].embedding
            self._embed_cache.set(query_text, emb)
            return emb
        except Exception as e:
            # Graceful fallback: if embeddings aren't available (e.g., MAX not running),
            # return None and let callers skip vector search.
            try:
                print(f"Warning: Failed to generate embedding: {e}")
            except Exception:
                pass
            return None

    def vector_search(self, query_vector, limit: int):
        """Performs vector similarity search using HNSW-backed operator when available."""
        query = f"""
        SELECT chunk_id, array_cosine_distance(embedding, CAST(? AS FLOAT[768])) AS score
        FROM {self.table_name}
        ORDER BY score ASC
        LIMIT {limit};
        """
        try:
            if DEBUG_EXPLAIN_VSS:
                explain_query = f"EXPLAIN {query}"
                explain_result = self.db_connection.execute(explain_query, [query_vector]).fetchall()
                print("VSS EXPLAIN:")
                for row in explain_result:
                    print(row)
            return self.db_connection.execute(query, [query_vector]).fetchall()
        except Exception:
            # Fallback to array_distance if operator not available
            fallback = f"""
            SELECT chunk_id, array_distance(embedding, CAST(? AS FLOAT[768])) AS score
            FROM {self.table_name}
            ORDER BY score ASC
            LIMIT {limit};
            """
            return self.db_connection.execute(fallback, [query_vector]).fetchall()

    def full_text_search(self, query_text: str, limit: int):
        """Performs full-text search with robust fallbacks and title boost."""
        expanded = self._expand_fts_query(query_text)

        # Attempt weighted field search
        query_weighted = f"""
        SELECT t.chunk_id,
               ({FTS_TITLE_WEIGHT} * COALESCE(
                    fts_main_{self.table_name}.match_bm25(
                        input_id := t.chunk_id,
                        query_string := CAST(? AS TEXT),
                        fields := 'title'
                    ), 0
               ) + {FTS_CONTENT_WEIGHT} * COALESCE(
                    fts_main_{self.table_name}.match_bm25(
                        input_id := t.chunk_id,
                        query_string := CAST(? AS TEXT),
                        fields := 'content'
                    ), 0
               )) AS score
        FROM {self.table_name} AS t
        ORDER BY score DESC
        LIMIT {limit};
        """
        try:
            rows = self.db_connection.execute(query_weighted, [expanded, expanded]).fetchall()
            if DEBUG_LOG_FTS_PATH:
                print("FTS: Using weighted field search")
            return rows
        except Exception:
            # Fallback to default fields
            query_default = f"""
            SELECT t.chunk_id,
                   fts_main_{self.table_name}.match_bm25(
                       input_id := t.chunk_id,
                       query_string := CAST(? AS TEXT)
                   ) AS score
            FROM {self.table_name} AS t
            ORDER BY score DESC
            LIMIT {limit};
            """
            try:
                rows = self.db_connection.execute(query_default, [expanded]).fetchall()
                if DEBUG_LOG_FTS_PATH:
                    print("FTS: Using default field search")
                return rows
            except Exception:
                # Final fallback: table function
                if DEBUG_LOG_FTS_PATH:
                    print("FTS: Using table function fallback")
                return []

    def hybrid_search(self, query_text: str, k: int = TOP_K, fts_weight: float = 0.4, vss_weight: float = 0.6):
        """Performs hybrid search using Reciprocal Rank Fusion (RRF)."""
        query_vector = self.get_query_embedding(query_text)

        # Get results from both search methods
        if query_vector is None:
            vector_results = []
        else:
            vector_results = self.vector_search(query_vector, limit=k * 2)
        fts_results = self.full_text_search(query_text, limit=k * 2)

        # --- Reciprocal Rank Fusion (RRF) ---
        rrf_scores = {}
        rrf_k = 60  # RRF constant, typically 60

        # Process vector search results
        for i, (chunk_id, _) in enumerate(vector_results):
            rank = i + 1
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + vss_weight / (rrf_k + rank)

        # Process full-text search results
        for i, (chunk_id, _) in enumerate(fts_results):
            rank = i + 1
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + fts_weight / (rrf_k + rank)

        # Sort results by RRF score and return top-k chunk_ids
        sorted_results = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        return [chunk_id for chunk_id, _ in sorted_results[:k]]

    def get_results_by_ids(self, chunk_ids: list):
        """Fetches the full document chunk details for a list of chunk_ids, preserving order."""
        if not chunk_ids:
            return []
        
        placeholders = ', '.join(['?'] * len(chunk_ids))
        query = f"SELECT chunk_id, title, content, url, section_hierarchy FROM {self.table_name} WHERE chunk_id IN ({placeholders})"
        
        # Fetch results and map them by chunk_id
        rows = self.db_connection.execute(query, chunk_ids).fetchall()
        results_map = {row[0]: row for row in rows}
        
        # Return results in the original, ranked order
        return [results_map[chunk_id] for chunk_id in chunk_ids if chunk_id in results_map]

    def close(self):
        """Closes the database connection."""
        if self.db_connection:
            self.db_connection.close()


def main():
    parser = argparse.ArgumentParser(description="docs Documentation Hybrid Search")
    parser.add_argument("-q", "--query", type=str, required=True, help="Search query")
    parser.add_argument("-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--fts-weight", type=float, default=0.4, help="Weight for FTS results")
    parser.add_argument("--vss-weight", type=float, default=0.6, help="Weight for VSS results")
    args = parser.parse_args()

    searcher = HybridSearcher()
    try:
        print(f"🔍 Searching for: '{args.query}'\n")

        # Get the top chunk IDs from the hybrid search
        top_chunk_ids = searcher.hybrid_search(
            args.query, k=args.k, fts_weight=args.fts_weight, vss_weight=args.vss_weight
        )

        if not top_chunk_ids:
            print("No results found.")
            return

        # Fetch the details for the top results
        results = searcher.get_results_by_ids(top_chunk_ids)

        # Print the results
        for i, (chunk_id, title, content, url, section_hierarchy) in enumerate(results):
            print(f"--- Result {i+1} ---")
            print(f"Title: {title}")
            if section_hierarchy:
                print(f"Section: {' > '.join(section_hierarchy)}")
            print(f"URL: {url}")
            print(f"Chunk ID: {chunk_id}")
            print(f"Content: {content[:300]}...")
            print()
    finally:
        searcher.close()


if __name__ == "__main__":
    main()
