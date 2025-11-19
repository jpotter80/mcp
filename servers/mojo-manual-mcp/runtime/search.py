import duckdb
import os
import argparse
from collections import OrderedDict
from openai import OpenAI
import sys

# --- Configuration ---
_RUNTIME_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_DB_PATH = os.path.join(_RUNTIME_DIR, "mojo_manual_mcp.db")

DB_PATH = os.getenv("MOJO_DB_PATH", _DEFAULT_DB_PATH)
TABLE_NAME = os.getenv("MOJO_TABLE_NAME", "mojo_docs_indexed")
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
        Only affects FTS (VSS uses the raw query).
        """
        q = query_text.lower()
        extras: list[str] = []
        # Minimal, targeted expansions — grow this map as needed
        if "variable" in q or "declare" in q:
            extras.extend(["let", "var", "binding", "assign"])
        if "ownership" in q:
            extras.extend(["own", "borrow", "move", "alias"])  # conservative
        # Return original plus expansions as a single space-joined string
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
                print(f"[WARN] Embedding generation failed, falling back to FTS only: {e}")
            except Exception:
                pass
            return None

    def vector_search(self, query_vector, limit: int):
        """Performs vector similarity search using HNSW-backed operator when available.
        Uses cosine distance as per vss docs; HNSW will accelerate ORDER BY array_cosine_distance with LIMIT.
        """
        # Prefer array_cosine_distance to ensure HNSW acceleration with cosine metric
        query = f"""
        SELECT chunk_id, array_cosine_distance(embedding, CAST(? AS FLOAT[768])) AS score
        FROM {self.table_name}
        ORDER BY score ASC
        LIMIT {limit};
        """
        try:
            if DEBUG_EXPLAIN_VSS:
                plan = self.db_connection.execute("EXPLAIN " + query, [query_vector]).fetchall()
                try:
                    sys.stderr.write("[DEBUG] VSS EXPLAIN plan:\n")
                    for row in plan:
                        sys.stderr.write(str(row[0]) + "\n")
                    sys.stderr.flush()
                except Exception:
                    pass
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
        """Performs full-text search with robust fallbacks and title boost.
        Strategy (in order):
        1) Macro with per-field scores (title/content) and weighted sum
        2) Macro with default fields only (no per-field control)
        3) Table-function search() joined on rowid
        """
        expanded = self._expand_fts_query(query_text)

        # Attempt 1: Correct match_bm25 usage with chunk_id as input_id; search both fields
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
                try:
                    sys.stderr.write("[DEBUG] FTS path: match_bm25 per-field weighted\n")
                    sys.stderr.flush()
                except Exception:
                    pass
            return rows
        except Exception:
            # Attempt 2: default fields only
            query_default = f"""
            SELECT t.chunk_id,
                   fts_main_{self.table_name}.match_bm25(
                     input_id := t.chunk_id,
                     query_string := CAST(? AS TEXT)
                   ) AS score
            FROM {self.table_name} AS t
            WHERE score IS NOT NULL
            ORDER BY score DESC
            LIMIT {limit};
            """
            try:
                rows = self.db_connection.execute(query_default, [expanded]).fetchall()
                if DEBUG_LOG_FTS_PATH:
                    try:
                        sys.stderr.write("[DEBUG] FTS path: match_bm25 default fields\n")
                        sys.stderr.flush()
                    except Exception:
                        pass
                return rows
            except Exception:
                # Attempt 3: version-agnostic keyword fallback using LIKE presence scoring
                # Build a simple heuristic score: title matches are weighted higher than content matches
                tokens = [tok for tok in expanded.lower().split() if len(tok) >= 2]
                tokens = list(dict.fromkeys(tokens))  # de-duplicate preserving order
                if not tokens:
                    return []

                # Build dynamic SQL segments for title/content presence
                title_clauses = ["(CASE WHEN lower(t.title) LIKE '%' || ? || '%' THEN 1 ELSE 0 END)" for _ in tokens]
                content_clauses = ["(CASE WHEN lower(t.content) LIKE '%' || ? || '%' THEN 1 ELSE 0 END)" for _ in tokens]

                title_sum = " + ".join(title_clauses) if title_clauses else "0"
                content_sum = " + ".join(content_clauses) if content_clauses else "0"

                query_kw = f"""
                SELECT t.chunk_id,
                       ({FTS_TITLE_WEIGHT} * ({title_sum}) + {FTS_CONTENT_WEIGHT} * ({content_sum})) AS score
                FROM {self.table_name} AS t
                ORDER BY score DESC
                LIMIT {limit};
                """
                params = tokens + tokens  # first for title LIKEs, then for content LIKEs
                rows = self.db_connection.execute(query_kw, params).fetchall()
                if DEBUG_LOG_FTS_PATH:
                    try:
                        sys.stderr.write("[DEBUG] FTS path: LIKE-based fallback\n")
                        sys.stderr.flush()
                    except Exception:
                        pass
                return rows

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
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0
            rrf_scores[chunk_id] += 1.0 / (rrf_k + rank) * vss_weight

        # Process full-text search results
        for i, (chunk_id, _) in enumerate(fts_results):
            rank = i + 1
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0
            rrf_scores[chunk_id] += 1.0 / (rrf_k + rank) * fts_weight

        # Sort results by RRF score and return top-k chunk_ids
        sorted_results = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        return [chunk_id for chunk_id, _ in sorted_results[:k]]

    def get_results_by_ids(self, chunk_ids: list):
        """
        Fetches the full document chunk details for a list of chunk_ids,
        preserving the original order.
        """
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
    parser = argparse.ArgumentParser(description="Mojo Documentation Hybrid Search")
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
                try:
                    path = " > ".join(section_hierarchy)
                    print(f"Section: {path}")
                except Exception:
                    pass
            print(f"URL: {url}")
            # Print a short snippet for readability
            snippet = content[:240].replace("\n", " ") + ("…" if len(content) > 240 else "")
            print(f"Content:\n{snippet}\n")
    finally:
        searcher.close()

if __name__ == "__main__":
    main()
