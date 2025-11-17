# Mojo Manual Preprocessing

This preprocessing pipeline prepares the Mojo programming language manual for vector embedding and MCP resource server exposure.

## Overview

The pipeline transforms MDX documentation files into optimally-chunked, metadata-rich content ready for semantic search and AI agent consumption.

## Features

- **MDX Processing**: Cleans JSX components, imports, and preserves code blocks
- **Smart Chunking**: Recursive text splitting with 400-token chunks and 20% overlap
- **Metadata Extraction**: Frontmatter parsing, section hierarchy, and URL generation
- **Quality Validation**: Comprehensive checks for content preservation and integrity
- **Multiple Output Formats**: Raw text, JSON metadata, and JSONL chunks

## Quick Start

### 1. Install Dependencies

```bash
# Install pixi if not already installed
curl -fsSL https://pixi.sh/install.sh | bash

# Install project dependencies
pixi install
```

### 2. Run Preprocessing

```bash
# Process all manual files
pixi run process

# Validate output
pixi run validate

# View statistics
pixi run stats
```

### 3. Clean Output (if needed)

```bash
pixi run clean
```

## Directory Structure

```
preprocessing/
├── src/
│   ├── __init__.py
│   ├── pipeline.py           # Main orchestrator
│   ├── mdx_processor.py      # MDX parsing and cleaning
│   ├── chunker.py            # Document chunking
│   ├── metadata_extractor.py # Metadata extraction
│   └── utils.py              # Helper functions
├── config/
│   └── processing_config.yaml # Configuration
└── README.md

processed_docs/              # Output directory (created on run)
├── raw/                     # Cleaned text files
├── metadata/                # Document metadata (JSON)
├── chunks/                  # Chunked content (JSONL)
└── manifest.json           # Processing manifest
```

## Configuration

Edit `preprocessing/config/processing_config.yaml` to customize:

- **Chunk size**: Default 400 tokens (optimal for all-mpnet-base-v2)
- **Chunk overlap**: Default 80 tokens (20%)
- **Code block handling**: Preserve or extract separately
- **URL generation**: Base URL and patterns

## Output Formats

### 1. Raw Text (`processed_docs/raw/*.txt`)

Clean markdown content with JSX removed:

```
# Mojo language basics

This page provides an overview of the Mojo language...
```

### 2. Metadata (`processed_docs/metadata/*.json`)

Document metadata and statistics:

```json
{
  "title": "Mojo language basics",
  "document_id": "basics",
  "url": "https://docs.modular.com/mojo/manual/basics",
  "statistics": {
    "word_count": 3245,
    "code_block_count": 12
  }
}
```

### 3. Chunks (`processed_docs/chunks/*.jsonl`)

One chunk per line with full metadata:

```json
{"chunk_id": "basics-001", "content": "...", "token_count": 387, "section_hierarchy": ["Mojo language basics", "Hello world"]}
{"chunk_id": "basics-002", "content": "...", "token_count": 402, "section_hierarchy": ["Mojo language basics", "Variables"]}
```

### 4. Manifest (`processed_docs/manifest.json`)

Processing summary and index:

```json
{
  "processing_date": "2025-10-10T12:00:00Z",
  "total_documents": 25,
  "total_chunks": 487,
  "average_tokens_per_chunk": 378.5,
  "documents": [...]
}
```

## Processing Pipeline

1. **Discovery**: Find all `.mdx` and `.md` files in `/manual`
2. **MDX Processing**: 
   - Parse frontmatter
   - Remove JSX components and imports
   - Clean and normalize content
3. **Chunking**:
   - Split by section headers
   - Recursive paragraph/sentence splitting
   - Maintain 400-token target with 80-token overlap
4. **Metadata Extraction**:
   - Section hierarchy
   - Statistics (word count, code blocks, etc.)
   - URL generation
5. **Output Generation**:
   - Save raw, metadata, and chunks
   - Generate manifest
6. **Validation**:
   - Verify all files created
   - Check chunk sizes
   - Validate metadata completeness

## Chunking Strategy

Based on research-backed best practices for technical documentation:

- **Size**: 400 tokens (optimal for transformer models)
- **Overlap**: 80 tokens (20% - preserves context across boundaries)
- **Boundaries**: Respects paragraphs, sentences, and code blocks
- **Hierarchy**: Maintains section context for each chunk

## API Usage

```python
from preprocessing.src import DocumentProcessingPipeline

# Initialize pipeline
pipeline = DocumentProcessingPipeline("preprocessing/config/processing_config.yaml")

# Process all documents
manifest = pipeline.process_all_documents()

# Validate output
pipeline.validate_output()

# Print statistics
pipeline.print_statistics()
```

## Next Steps

After preprocessing, the output is ready for:

1. **Vector Embedding**: Generate embeddings using MAX serving
2. **Database Storage**: Store in PostgreSQL with pgvector
3. **MCP Server**: Expose via Model Context Protocol resource server
4. **Semantic Search**: Enable AI agents to query documentation

## Troubleshooting

### Import Errors

If you see import errors, ensure pixi environment is activated:

```bash
pixi shell
python -m preprocessing.src.pipeline
```

### Missing Files

If processing fails for specific files:

```bash
# Check file list
python -c "from preprocessing.src.utils import get_file_list; print(get_file_list('manual', ['*.mdx']))"

# Process with verbose output
python -m preprocessing.src.pipeline --verbose
```

### Token Count Issues

If chunks are too large/small, adjust in config:

```yaml
chunking:
  chunk_size: 500  # Increase for larger chunks
  chunk_overlap: 100  # Increase for more context
```

## Development

### Running Tests

```bash
pixi run test
```

### Code Formatting

```bash
pixi run format
```

### Adding New Processors

1. Create processor in `src/`
2. Import in `__init__.py`
3. Integrate into `pipeline.py`
4. Update configuration schema

## License

Part of the Mojo Manual MCP Resource Server project.
