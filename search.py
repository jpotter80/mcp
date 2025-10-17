import duckdb
import os
import argparse
from openai import OpenAI

# --- Configuration ---
DB_PATH = "main.db"
TABLE_NAME = "mojo_docs_indexed"
MAX_SERVER_URL = "http://localhost:8000/v1"
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
TOP_K = 5  # Number of results to return
# --- End Configuration ---

class HybridSearcher:
    """
    A class to perform hybrid search (vector + full-text) on the DuckDB database.
    """
    def __init__(self, db_path="main.db", table_name="mojo_docs_indexed"):
        self.db_path = db_path
        self.table_name = table_name
        self.openai_client = OpenAI(base_url=MAX_SERVER_URL, api_key="EMPTY")
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

    def get_query_embedding(self, query_text: str):
        """Generates an embedding for the user's query."""
        response = self.openai_client.embeddings.create(
            model=MODEL_NAME,
            input=[query_text],
        )
        return response.data[0].embedding

    def vector_search(self, query_vector, limit: int):
        """Performs vector similarity search."""
        query = f"""
        SELECT chunk_id, array_distance(embedding, CAST(? AS FLOAT[768])) AS score
        FROM {self.table_name}
        ORDER BY score ASC
        LIMIT {limit};
        """
        return self.db_connection.execute(query, [query_vector]).fetchall()

    def full_text_search(self, query_text: str, limit: int):
        """Performs full-text search."""
        query = f"""
        SELECT chunk_id, score
        FROM (
            SELECT *, fts_main_{self.table_name}.match_bm25(chunk_id, ?) AS score
            FROM {self.table_name}
        )
        WHERE score IS NOT NULL
        ORDER BY score DESC
        LIMIT {limit};
        """
        return self.db_connection.execute(query, [query_text]).fetchall()

    def hybrid_search(self, query_text: str, fts_weight: float = 0.4, vss_weight: float = 0.6):
        """
        Performs hybrid search using Reciprocal Rank Fusion (RRF).
        """
        query_vector = self.get_query_embedding(query_text)

        # Get results from both search methods
        vector_results = self.vector_search(query_vector, limit=TOP_K * 2)
        fts_results = self.full_text_search(query_text, limit=TOP_K * 2)

        # --- Reciprocal Rank Fusion (RRF) ---
        rrf_scores = {}
        k = 60  # RRF constant, typically 60

        # Process vector search results
        for i, (chunk_id, _) in enumerate(vector_results):
            rank = i + 1
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0
            rrf_scores[chunk_id] += 1 / (k + rank) * vss_weight

        # Process full-text search results
        for i, (chunk_id, _) in enumerate(fts_results):
            rank = i + 1
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0
            rrf_scores[chunk_id] += 1 / (k + rank) * fts_weight

        # Sort results by RRF score
        sorted_results = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        
        return [chunk_id for chunk_id, _ in sorted_results[:TOP_K]]

    def get_results_by_ids(self, chunk_ids: list):
        """
        Fetches the full document chunk details for a list of chunk_ids,
        preserving the original order.
        """
        if not chunk_ids:
            return []
        
        placeholders = ', '.join(['?'] * len(chunk_ids))
        query = f"SELECT chunk_id, title, content, url FROM {self.table_name} WHERE chunk_id IN ({placeholders})"
        
        # Fetch results and map them by chunk_id
        results_map = {chunk_id: (chunk_id, title, content, url) for chunk_id, title, content, url in self.db_connection.execute(query, chunk_ids).fetchall()}
        
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
        top_chunk_ids = searcher.hybrid_search(args.query, args.fts_weight, args.vss_weight)
        
        if not top_chunk_ids:
            print("No results found.")
            return

        # Fetch the details for the top results
        results = searcher.get_results_by_ids(top_chunk_ids)
        
        # Print the results
        for i, (chunk_id, title, content, url) in enumerate(results):
            print(f"--- Result {i+1} ---")
            print(f"Title: {title}")
            print(f"URL: {url}")
            print(f"Content:\n{content}\n")
            
    finally:
        searcher.close()

if __name__ == "__main__":
    main()
