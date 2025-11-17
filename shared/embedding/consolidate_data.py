import os
import sys
import json
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# Add project root to path to import shared module
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.config_loader import load_config_with_substitution

# --- Defaults ---
MIN_CHUNK_LENGTH = 80  # Relaxed threshold; consider token-based threshold downstream
# --- End Defaults ---

def load_jsonl(file_path):
    """Loads a .jsonl file and returns a list of dictionaries."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def main():
    """Consolidates chunks, metadata, and embeddings into a single Parquet file."""

    parser = argparse.ArgumentParser(description="Consolidate chunks and embeddings into Parquet")
    parser.add_argument(
        "--mcp-name",
        default="mojo",
        help="MCP server name (e.g., 'mojo', 'duckdb')",
    )
    parser.add_argument(
        "--config",
        type=str,
        required=False,
        help="Optional path to processing_config.yaml for variable substitution",
    )
    args = parser.parse_args()

    if args.config:
        _ = load_config_with_substitution(args.config)

    mcp_name = args.mcp_name
    chunks_dir = os.path.join("shared", "build", "processed_docs", mcp_name, "chunks")
    embeddings_dir = os.path.join("shared", "build", "embeddings", mcp_name)
    output_file = os.path.join("shared", "build", f"{mcp_name}_embeddings.parquet")

    print("🔥 Starting data consolidation process...")

    # 1. Load all embeddings into a dictionary for quick lookup
    print("Loading embeddings...")
    embeddings_map = {}
    embedding_files = [f for f in os.listdir(embeddings_dir) if f.endswith("_embeddings.jsonl")]
    for file_name in tqdm(embedding_files, desc="Reading embedding files"):
        file_path = os.path.join(embeddings_dir, file_name)
        for item in load_jsonl(file_path):
            embeddings_map[item["chunk_id"]] = item["embedding"]
    print(f"✓ Loaded {len(embeddings_map)} embeddings.")

    # 2. Load all chunks and join with embeddings and metadata
    print("\nLoading chunks and metadata...")
    consolidated_data = []
    chunk_files = [f for f in os.listdir(chunks_dir) if f.endswith(".jsonl")]
    for file_name in tqdm(chunk_files, desc="Reading chunk files"):
        file_path = os.path.join(chunks_dir, file_name)
        for chunk_data in load_jsonl(file_path):
            chunk_id = chunk_data.get("chunk_id")
            if not chunk_id:
                continue

            # --- Quality Filter ---
            # Only include chunks with a minimal length to avoid extreme noise.
            content = chunk_data.get("content")
            if not content or len(content) < MIN_CHUNK_LENGTH:
                # Keep short chunks if they look like headers or intros
                meta = chunk_data.get("metadata", {})
                section_h = meta.get("section_hierarchy", [])
                if not section_h:
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
                "content": content,
                "embedding": embedding,
                "title": metadata.get("title"),
                "url": metadata.get("url"),
                "section_hierarchy": metadata.get("section_hierarchy", []),
                # Persist a section_url if present; else fall back to url at read time
                "section_url": metadata.get("section_url"),
                # Persist useful quality features when present
                "token_count": chunk_data.get("token_count"),
                "has_code": chunk_data.get("has_code"),
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
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df.to_parquet(output_file, index=False)
    print(f"✅ Successfully saved consolidated data to {output_file}")

if __name__ == "__main__":
    main()
