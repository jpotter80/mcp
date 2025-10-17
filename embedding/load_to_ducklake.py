import duckdb
import os

# --- Configuration ---
DUCKLAKE_CATALOG_PATH = "../mojo_catalog.ducklake"
PARQUET_INPUT_FILE = "../processed_docs/mojo_manual_embeddings.parquet"
TABLE_NAME = "mojo_docs"
# --- End Configuration ---

def main():
    """
    Initializes a DuckLake catalog and loads the consolidated embeddings data
    from a Parquet file into a versioned table.
    """
    print("🔥 Initializing DuckLake and loading data...")

    # Ensure the directory for the catalog exists
    catalog_dir = os.path.dirname(DUCKLAKE_CATALOG_PATH)
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
        print(f"Attaching DuckLake catalog at: {DUCKLAKE_CATALOG_PATH}")
        con.execute(f"ATTACH 'ducklake:{DUCKLAKE_CATALOG_PATH}' AS mojo_lake;")
        con.execute("USE mojo_lake;")
        print("✓ DuckLake catalog attached.")

        # Check if the table already exists
        result = con.execute(f"SELECT 1 FROM information_schema.tables WHERE table_name = '{TABLE_NAME}'").fetchone()

        if result:
            print(f"Table '{TABLE_NAME}' already exists. Performing an upsert...")
            # --- Upsert Logic ---
            # Load new data into a temporary table
            con.execute(f"CREATE OR REPLACE TEMP TABLE new_mojo_docs AS SELECT * FROM read_parquet('{PARQUET_INPUT_FILE}');")
            
            # Begin a transaction for the upsert
            con.begin()
            
            # Delete old versions of chunks that are present in the new data
            print("Deleting old records...")
            con.execute(f"DELETE FROM {TABLE_NAME} WHERE chunk_id IN (SELECT chunk_id FROM new_mojo_docs);")
            
            # Insert the new data
            print("Inserting new records...")
            con.execute(f"INSERT INTO {TABLE_NAME} SELECT * FROM new_mojo_docs;")
            
            # Commit the transaction to create a new snapshot
            con.commit()
            print("✓ Upsert complete. A new snapshot has been created.")

        else:
            print(f"Table '{TABLE_NAME}' not found. Creating it from Parquet file...")
            # --- Initial Load Logic ---
            con.execute(f"""
                CREATE TABLE {TABLE_NAME} AS
                SELECT * FROM read_parquet('{PARQUET_INPUT_FILE}');
            """)
            print(f"✓ Table '{TABLE_NAME}' created successfully.")

        # Verify the data
        result = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()
        row_count = result[0] if result else 0
        print(f"\n✅ Success! The '{TABLE_NAME}' table now contains {row_count} records.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        con.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
