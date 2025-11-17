# Document Embedding Generation

This document outlines the process for generating embeddings from pre-processed document chunks using a MAX model server. The script is designed to be robust and efficient, handling large volumes of text by processing files in batches.

## Prerequisites

Before running the script, ensure you have the following:

1.  **Python 3.8+**: The script is written in Python and requires a modern version.
2.  **MAX Server**: A running instance of a MAX model server that provides an OpenAI-compatible embeddings endpoint. The model `sentence-transformers/all-mpnet-base-v2` is recommended for its performance.
3.  **Processed Chunks**: The document chunks should be located in `processed_docs/chunks/` in `.jsonl` format. Each line in the file should be a JSON object containing at least a `content` field with the text to be embedded and a `chunk_id` to identify it.

## Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies**:
    The script requires the `openai` and `tqdm` libraries. You can install them using pip:
    ```bash
    pip install openai tqdm
    ```

## How It Works

The `generate_embeddings.py` script automates the process of creating vector embeddings for your document chunks.

### Configuration

The script starts with a configuration section where you can set the following parameters:

-   `MAX_SERVER_URL`: The URL of your running MAX server's OpenAI-compatible endpoint (e.g., `http://localhost:8000/v1`).
-   `MODEL_NAME`: The name of the model to use for generating embeddings (e.g., `sentence-transformers/all-mpnet-base-v2`).
-   `INPUT_DIR`: The directory where your `.jsonl` chunk files are located.
-   `OUTPUT_DIR`: The directory where the generated embeddings will be saved.
-   `BATCH_SIZE`: The number of chunks to process in each request to the MAX server. Adjust this based on your server's capacity and available memory.

### Execution Flow

1.  **File Discovery**: The script scans the `INPUT_DIR` for all `.jsonl` files.
2.  **Chunk Processing**: For each file found, it reads the content and prepares it for batch processing.
3.  **Batching**: The chunks are grouped into batches of the size defined by `BATCH_SIZE`.
4.  **Embedding Generation**: Each batch is sent to the MAX server via an API call to the embeddings endpoint.
5.  **Saving Embeddings**: The returned embeddings are saved to a new `.jsonl` file in the `OUTPUT_DIR`. The output filename is derived from the input filename (e.g., `basics.jsonl` becomes `basics_embeddings.jsonl`). Each line in the output file contains the `chunk_id` and the corresponding `embedding` vector.

## Usage

1.  **Start the MAX Server**:
    Open a terminal and start the MAX server with the desired model.
    ```bash
    max serve --model sentence-transformers/all-mpnet-base-v2
    ```
    Ensure the server is running and accessible at the URL specified in the script's configuration.

2.  **Run the Embedding Script**:
    Open another terminal, navigate to the `embedding` directory, and run the script:
    ```bash
    python generate_embeddings.py
    ```

3.  **Monitor the Process**:
    The script will print its progress, including the files it's processing and a progress bar for each file.

4.  **Verify the Output**:
    Once the script finishes, you will find the embedding files in the `processed_docs/embeddings/` directory. Each file will contain the embeddings for the corresponding chunk file.

## Example Output Format

The output files will be in `.jsonl` format, with each line representing a chunk's embedding:

```json
{"chunk_id": "basics-000", "embedding": [0.021, -0.034, ..., 0.056]}
{"chunk_id": "basics-001", "embedding": [-0.011, 0.042, ..., -0.023]}
```

This format is optimized for easy loading into vector databases like Weaviate, Pinecone, or Qdrant.
