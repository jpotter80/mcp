import os
import json
from openai import OpenAI
from tqdm import tqdm

# --- Configuration ---
MAX_SERVER_URL = "http://localhost:8000/v1"
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INPUT_DIR = "processed_docs/chunks"
OUTPUT_DIR = "processed_docs/embeddings"
BATCH_SIZE = 64
# --- End Configuration ---

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
    """Main function to generate embeddings for all chunk files."""
    client = OpenAI(base_url=MAX_SERVER_URL, api_key="EMPTY")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Searching for .jsonl files in: {INPUT_DIR}")
    jsonl_files = list(get_jsonl_files(INPUT_DIR))

    if not jsonl_files:
        print("No .jsonl files found. Exiting.")
        return

    print(f"Found {len(jsonl_files)} files to process.")

    for input_path in jsonl_files:
        file_name = os.path.basename(input_path)
        output_path = os.path.join(OUTPUT_DIR, file_name.replace('.jsonl', '_embeddings.jsonl'))
        
        print(f"\nProcessing {input_path} -> {output_path}")
        process_file(client, input_path, output_path)

    print("\nEmbedding generation complete.")

if __name__ == "__main__":
    main()
