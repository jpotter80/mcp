import os
import json
import pandas as pd
from tqdm import tqdm

# --- Configuration ---
CHUNKS_DIR = "../processed_docs/chunks"
EMBEDDINGS_DIR = "../processed_docs/embeddings"
OUTPUT_FILE = "../processed_docs/mojo_manual_embeddings.parquet"
# --- End Configuration ---

def load_jsonl(file_path):
    """Loads a .jsonl file and returns a list of dictionaries."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def main():
    """
    Consolidates chunks, metadata, and embeddings into a single Parquet file.
    """
    print("🔥 Starting data consolidation process...")

    # 1. Load all embeddings into a dictionary for quick lookup
    print("Loading embeddings...")
    embeddings_map = {}
    embedding_files = [f for f in os.listdir(EMBEDDINGS_DIR) if f.endswith("_embeddings.jsonl")]
    for file_name in tqdm(embedding_files, desc="Reading embedding files"):
        file_path = os.path.join(EMBEDDINGS_DIR, file_name)
        for item in load_jsonl(file_path):
            embeddings_map[item["chunk_id"]] = item["embedding"]
    print(f"✓ Loaded {len(embeddings_map)} embeddings.")

    # 2. Load all chunks and join with embeddings and metadata
    print("\nLoading chunks and metadata...")
    consolidated_data = []
    chunk_files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith(".jsonl")]
    for file_name in tqdm(chunk_files, desc="Reading chunk files"):
        file_path = os.path.join(CHUNKS_DIR, file_name)
        for chunk_data in load_jsonl(file_path):
            chunk_id = chunk_data.get("chunk_id")
            if not chunk_id:
                continue

            # Get the corresponding embedding
            embedding = embeddings_map.get(chunk_id)
            if not embedding:
                print(f"Warning: No embedding found for chunk_id {chunk_id}")
                continue

            # Extract relevant metadata
            metadata = chunk_data.get("metadata", {})
            
            # Create a unified record
            record = {
                "chunk_id": chunk_id,
                "document_id": chunk_data.get("document_id"),
                "content": chunk_data.get("content"),
                "embedding": embedding,
                "title": metadata.get("title"),
                "url": metadata.get("url"),
                "section_hierarchy": metadata.get("section_hierarchy", []),
            }
            consolidated_data.append(record)

    if not consolidated_data:
        print("❌ No data was consolidated. Exiting.")
        return

    print(f"✓ Consolidated {len(consolidated_data)} records.")

    # 3. Create a DataFrame and save to Parquet
    print("\nCreating DataFrame and saving to Parquet...")
    df = pd.DataFrame(consolidated_data)

    # Ensure the output directory exists
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"✅ Successfully saved consolidated data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
