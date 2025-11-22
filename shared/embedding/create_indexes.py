import argparse
import duckdb
import os


def _build_paths(mcp_name: str, doc_type: str = "manual"):
    """Build paths for MCP-specific files using both mcp_name and doc_type.
    
    Args:
        mcp_name: Tool name (e.g., 'mojo', 'duckdb')
        doc_type: Documentation type (e.g., 'manual', 'docs', 'guide')
    
    Returns:
        Tuple of (ducklake_catalog_path, ducklake_table_name, indexed_table_name, main_db_path)
    """
    mcp_dir = f"{mcp_name}-{doc_type}-mcp"
    ducklake_catalog_path = os.path.join("servers", mcp_dir, "runtime", f"{mcp_name}_catalog.ducklake")
    ducklake_table_name = f"{mcp_name}_docs"
    indexed_table_name = f"{mcp_name}_docs_indexed"
    # Use underscores in database filename for SQL compatibility
    main_db_path = os.path.join("servers", mcp_dir, "runtime", f"{mcp_name}_{doc_type}_mcp.db")
    return ducklake_catalog_path, ducklake_table_name, indexed_table_name, main_db_path

def main():
    """Create a materialized, indexed copy of the DuckLake data for fast querying."""

    parser = argparse.ArgumentParser(description="Create materialized indexed DuckDB tables for search")
    parser.add_argument(
        "--mcp-name",
        default="mojo",
        help="MCP server name (e.g., 'mojo', 'duckdb')",
    )
    parser.add_argument(
        "--doc-type",
        default="manual",
        help="Documentation type (e.g., 'manual', 'docs', 'guide')",
    )
    args = parser.parse_args()

    mcp_name = args.mcp_name
    doc_type = args.doc_type
    ducklake_catalog_path, ducklake_table_name, indexed_table_name, main_db_path = _build_paths(mcp_name, doc_type)

    print("🔥 Starting materialized view and index creation process...")

    if not os.path.exists(ducklake_catalog_path):
        print(f"❌ Error: DuckLake catalog not found at '{ducklake_catalog_path}'.")
        print("Please run the data loading script first.")
        return

    # Connect to a persistent main DuckDB database file
    con = duckdb.connect(database=main_db_path, read_only=False)

    try:
        # Attach the DuckLake database
        print(f"Attaching DuckLake catalog at: {ducklake_catalog_path}")
        con.execute(f"ATTACH 'ducklake:{ducklake_catalog_path}' AS mojo_lake (READ_ONLY);")
        print("✓ DuckLake catalog attached in read-only mode.")

        # 1. Materialize the latest data from DuckLake into a native table
        print(f"\nMaterializing data into native table '{indexed_table_name}'...")
        con.execute(f"DROP TABLE IF EXISTS {indexed_table_name};")
        # Explicitly cast the embedding column to the required FLOAT[768] type for HNSW indexing
        con.execute(
            f"""
            CREATE TABLE {indexed_table_name} AS 
            SELECT 
                chunk_id, 
                document_id, 
                content, 
                CAST(embedding AS FLOAT[768]) AS embedding, 
                title, 
                url, 
                section_hierarchy 
            FROM mojo_lake.{ducklake_table_name};
            """
        )
        print(f"✓ Successfully copied data to '{indexed_table_name}'.")

        # 2. Create HNSW index for Vector Search on the native table
        print("\nCreating HNSW index for vector search...")
        con.execute("INSTALL vss;")
        con.execute("LOAD vss;")
        # Enable experimental persistence for HNSW indexes
        con.execute("SET hnsw_enable_experimental_persistence = true;")
        # Recreate the index to ensure the desired metric is applied
        con.execute("DROP INDEX IF EXISTS mojo_hnsw_idx;")
        con.execute(
            f"CREATE INDEX mojo_hnsw_idx ON {indexed_table_name} USING HNSW (embedding) WITH (metric = 'cosine');"
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
            f"PRAGMA create_fts_index('{indexed_table_name}', 'chunk_id', 'title', 'content', overwrite=1);"
        )
        print("✓ FTS index created successfully.")

        # Verify the final table
        result = con.execute(f"SELECT COUNT(*) FROM {indexed_table_name}").fetchone()
        row_count = result[0] if result else 0
        print(f"\n✅ Success! Materialized table '{indexed_table_name}' contains {row_count} records and is fully indexed.")

    except Exception as e:
        print(f"\n❌ An error occurred during the process: {e}")
    finally:
        con.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
