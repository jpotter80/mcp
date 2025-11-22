import argparse
import duckdb
import os


def _build_paths(mcp_name: str, doc_type: str = "manual"):
    """Build paths for MCP-specific files using both mcp_name and doc_type.
    
    Args:
        mcp_name: Tool name (e.g., 'mojo', 'duckdb')
        doc_type: Documentation type (e.g., 'manual', 'docs', 'guide')
    
    Returns:
        Tuple of (catalog_path, parquet_input, table_name)
    """
    mcp_dir = f"{mcp_name}-{doc_type}-mcp"
    catalog_path = os.path.join("servers", mcp_dir, "runtime", f"{mcp_name}_catalog.ducklake")
    parquet_input = os.path.join("shared", "build", f"{mcp_name}_embeddings.parquet")
    table_name = f"{mcp_name}_docs"
    return catalog_path, parquet_input, table_name

def main():
    """Initialize a DuckLake catalog and load consolidated embeddings into a versioned table."""

    parser = argparse.ArgumentParser(description="Load consolidated embeddings into DuckLake")
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
    ducklake_catalog_path, parquet_input_file, table_name = _build_paths(mcp_name, doc_type)

    print("🔥 Initializing DuckLake and loading data...")

    # Ensure the directory for the catalog exists
    catalog_dir = os.path.dirname(ducklake_catalog_path)
    if catalog_dir and not os.path.exists(catalog_dir):
        os.makedirs(catalog_dir)

    # Connect to DuckDB.
    con = duckdb.connect()

    try:
        # Install and load the DuckLake extension
        print("Installing and loading DuckLake extension...")
        con.execute("INSTALL ducklake;")
        con.execute("LOAD ducklake;")
        print("✓ DuckLake extension loaded.")

        # Attach the DuckLake database. This creates the catalog and data directory on first run.
        print(f"Attaching DuckLake catalog at: {ducklake_catalog_path}")
        con.execute(f"ATTACH 'ducklake:{ducklake_catalog_path}' AS mojo_lake;")
        con.execute("USE mojo_lake;")
        print("✓ DuckLake catalog attached.")

        # Check if the table already exists
        result = con.execute(
            f"SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}'"
        ).fetchone()

        if result:
            print(f"Table '{table_name}' already exists. Performing an upsert...")
            # --- Upsert Logic ---
            # Load new data into a temporary table
            con.execute(
                f"CREATE OR REPLACE TEMP TABLE new_mojo_docs AS SELECT * FROM read_parquet('{parquet_input_file}');"
            )

            # Begin a transaction for the upsert
            con.begin()

            # Delete old records for documents present in the new data
            # Using document_id ensures we replace the entire document's chunk set
            print("Deleting old records...")
            con.execute(
                f"DELETE FROM {table_name} WHERE document_id IN (SELECT DISTINCT document_id FROM new_mojo_docs);"
            )

            # Insert the new data
            print("Inserting new records...")
            con.execute(f"INSERT INTO {table_name} SELECT * FROM new_mojo_docs;")

            # Commit the transaction to create a new snapshot
            con.commit()
            print("✓ Upsert complete. A new snapshot has been created.")

        else:
            print(f"Table '{table_name}' not found. Creating it from Parquet file...")
            # --- Initial Load Logic ---
            con.execute(
                f"""
                CREATE TABLE {table_name} AS
                SELECT * FROM read_parquet('{parquet_input_file}');
                """
            )
            print(f"✓ Table '{table_name}' created successfully.")

        # Verify the data
        result = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        row_count = result[0] if result else 0
        print(f"\n✅ Success! The '{table_name}' table now contains {row_count} records.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        con.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
