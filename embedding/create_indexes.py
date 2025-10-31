import duckdb
import os

# --- Configuration ---
DUCKLAKE_CATALOG_PATH = "mojo_catalog.ducklake"
DUCKLAKE_TABLE_NAME = "mojo_docs"
INDEXED_TABLE_NAME = "mojo_docs_indexed"
MAIN_DB_PATH = "main.db"
# --- End Configuration ---

def main():
    """
    Creates a materialized, indexed copy of the DuckLake data for fast querying.
    This script will:
    1. Connect to a main DuckDB database.
    2. Attach the versioned DuckLake catalog.
    3. Create a new native table by copying the latest data from DuckLake.
    4. Build HNSW and FTS indexes on this new native table.
    """
    print("🔥 Starting materialized view and index creation process...")

    if not os.path.exists(DUCKLAKE_CATALOG_PATH):
        print(f"❌ Error: DuckLake catalog not found at '{DUCKLAKE_CATALOG_PATH}'.")
        print("Please run the data loading script first.")
        return

    # Connect to a persistent main DuckDB database file
    con = duckdb.connect(database=MAIN_DB_PATH, read_only=False)

    try:
        # Attach the DuckLake database
        print(f"Attaching DuckLake catalog at: {DUCKLAKE_CATALOG_PATH}")
        con.execute(f"ATTACH 'ducklake:{DUCKLAKE_CATALOG_PATH}' AS mojo_lake (READ_ONLY);")
        print("✓ DuckLake catalog attached in read-only mode.")

        # 1. Materialize the latest data from DuckLake into a native table
        print(f"\nMaterializing data into native table '{INDEXED_TABLE_NAME}'...")
        con.execute(f"DROP TABLE IF EXISTS {INDEXED_TABLE_NAME};")
        # Explicitly cast the embedding column to the required FLOAT[768] type for HNSW indexing
        con.execute(f"""
            CREATE TABLE {INDEXED_TABLE_NAME} AS 
            SELECT 
                chunk_id, 
                document_id, 
                content, 
                CAST(embedding AS FLOAT[768]) AS embedding, 
                title, 
                url, 
                section_hierarchy 
            FROM mojo_lake.{DUCKLAKE_TABLE_NAME};
        """)
        print(f"✓ Successfully copied data to '{INDEXED_TABLE_NAME}'.")

        # 2. Create HNSW index for Vector Search on the native table
        print("\nCreating HNSW index for vector search...")
        con.execute("INSTALL vss;")
        con.execute("LOAD vss;")
        # Enable experimental persistence for HNSW indexes
        con.execute("SET hnsw_enable_experimental_persistence = true;")
        # Recreate the index to ensure the desired metric is applied
        con.execute("DROP INDEX IF EXISTS mojo_hnsw_idx;")
        con.execute(
            f"CREATE INDEX mojo_hnsw_idx ON {INDEXED_TABLE_NAME} USING HNSW (embedding) WITH (metric = 'cosine');"
        )
        print("✓ HNSW index created or already exists.")

        # 3. Create FTS index for Full-Text Search on the native table
        print("\nCreating FTS index for full-text search...")
        con.execute("INSTALL fts;")
        con.execute("LOAD fts;")
        # Index only textual fields relevant for BM25 ranking
        # According to DuckDB FTS docs, the 2nd arg is the document identifier column
        # Here we use 'chunk_id' as the document identifier, and index 'title' and 'content' fields
        con.execute(
            f"PRAGMA create_fts_index('{INDEXED_TABLE_NAME}', 'chunk_id', 'title', 'content', overwrite=1);"
        )
        print("✓ FTS index created successfully.")

        # Verify the final table
        result = con.execute(f"SELECT COUNT(*) FROM {INDEXED_TABLE_NAME}").fetchone()
        row_count = result[0] if result else 0
        print(f"\n✅ Success! Materialized table '{INDEXED_TABLE_NAME}' contains {row_count} records and is fully indexed.")

    except Exception as e:
        print(f"\n❌ An error occurred during the process: {e}")
    finally:
        con.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
