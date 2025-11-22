import os
import sys
from pathlib import Path

# Add project root to path BEFORE any shared imports
_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

import json
import argparse
import requests
from openai import OpenAI
from tqdm import tqdm

from shared.config_loader import load_config_with_substitution



# --- Defaults ---
MAX_SERVER_URL = "http://localhost:8000/v1"
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
BATCH_SIZE = 64
# --- End Defaults ---

def check_max_server(server_url):
    """Check if MAX server is running and accessible.
    
    Args:
        server_url: Base URL of the MAX server
        
    Returns:
        True if server is accessible, False otherwise
    """
    try:
        # Try to reach the models endpoint
        response = requests.get(f"{server_url}/models", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_jsonl_files(directory):
    """Find all .jsonl files in the specified directory."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jsonl"):
                yield os.path.join(root, file)

def process_file(client, input_path, output_path):
    """
    Reads a .jsonl file, generates embeddings for the content in batches,
    and saves them to a new .jsonl file.
    """
    chunks_to_process = []
    chunk_ids = []

    # First pass: read all chunks to process
    with open(input_path, "r", encoding="utf-8") as f_in:
        for line in f_in:
            if line.strip():
                data = json.loads(line)
                content = data.get("content")
                # Only process chunks that have non-empty content
                if content and content.strip():
                    # Prepend Title/Section context to help embeddings
                    meta = data.get("metadata", {})
                    title = meta.get("title") or ""
                    section = meta.get("section_hierarchy") or []
                    section_path = " > ".join(section) if section else ""
                    if title and section_path:
                        text = f"Title: {title}\nSection: {section_path}\n\n{content}"
                    elif title:
                        text = f"Title: {title}\n\n{content}"
                    elif section_path:
                        text = f"Section: {section_path}\n\n{content}"
                    else:
                        text = content

                    chunks_to_process.append(text)
                    chunk_ids.append(data.get("chunk_id", ""))

    if not chunks_to_process:
        print(f"No processable content found in {input_path}")
        return

    # Prepare to write embeddings
    with open(output_path, "w", encoding="utf-8") as f_out:
        # Process in batches
        for i in tqdm(range(0, len(chunks_to_process), BATCH_SIZE), desc=f"Embedding {os.path.basename(input_path)}"):
            batch_texts = chunks_to_process[i:i + BATCH_SIZE]
            batch_ids = chunk_ids[i:i + BATCH_SIZE]

            # Ensure the batch is not empty
            if not batch_texts:
                continue

            try:
                # Create embeddings for the batch
                response = client.embeddings.create(
                    model=MODEL_NAME,
                    input=batch_texts,
                )

                # Write embeddings to the output file
                for chunk_id, embedding_data in zip(batch_ids, response.data):
                    embedding_dict = {
                        "chunk_id": chunk_id,
                        "embedding": embedding_data.embedding
                    }
                    f_out.write(json.dumps(embedding_dict) + "\n")

            except Exception as e:
                print(f"An error occurred while processing a batch from {input_path}: {e}")
                # Optionally, add error handling here, like skipping the batch or stopping.

def main():
    """Main function to generate embeddings for all chunk files.

    Uses a config file with variable substitution to determine input/output paths.
    """

    parser = argparse.ArgumentParser(description="Generate embeddings for chunked docs")
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
    parser.add_argument(
        "--config",
        type=str,
        required=False,
        help="Path to processing_config.yaml; used for variable substitution",
    )
    args = parser.parse_args()

    # Load config (optional) to resolve project/server roots; paths themselves are
    # currently convention-based under shared/build.
    if args.config:
        _ = load_config_with_substitution(args.config)

    mcp_name = args.mcp_name
    input_dir = os.path.join("shared", "build", "processed_docs", mcp_name, "chunks")
    output_dir = os.path.join("shared", "build", "embeddings", mcp_name)

    # Check if MAX server is running
    print(f"Checking MAX server at {MAX_SERVER_URL}...")
    if not check_max_server(MAX_SERVER_URL):
        print(f"\n❌ ERROR: MAX server is not running at {MAX_SERVER_URL}")
        print("\nPlease start the MAX server before running this script:")
        print(f"  max serve --model {MODEL_NAME}")
        print("\nOr run it via pixi:")
        print("  pixi run max-serve")
        print("\nIn MCP environments, the server is typically started automatically by the host.")
        print("In test/development, you must start it manually.\n")
        sys.exit(1)
    
    print(f"✓ MAX server is running at {MAX_SERVER_URL}")

    client = OpenAI(base_url=MAX_SERVER_URL, api_key="EMPTY")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Searching for .jsonl files in: {input_dir}")
    jsonl_files = list(get_jsonl_files(input_dir))

    if not jsonl_files:
        print("No .jsonl files found. Exiting.")
        return

    print(f"Found {len(jsonl_files)} files to process.")

    for input_path in jsonl_files:
        file_name = os.path.basename(input_path)
        output_path = os.path.join(output_dir, file_name.replace(".jsonl", "_embeddings.jsonl"))
        
        print(f"\nProcessing {input_path} -> {output_path}")
        process_file(client, input_path, output_path)

    print("\nEmbedding generation complete.")

if __name__ == "__main__":
    main()
