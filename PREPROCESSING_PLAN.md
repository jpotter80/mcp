# Mojo Manual Preprocessing Plan

## Overview
This document outlines the preprocessing pipeline for the Mojo manual documentation located in `/manual`. The processed output will be prepared for vectorization and exposure through an MCP resource server.

## Objectives

1. **Preserve Original Content**: Maintain unmodified copies of all source files
2. **Clean MDX Content**: Remove JSX components, imports, and non-textual elements
3. **Extract Metadata**: Parse frontmatter and document structure
4. **Generate Hierarchical Chunks**: Create semantically meaningful text segments
5. **Prepare for Vectorization**: Output structured data ready for embedding generation

## Architecture

### Directory Structure
```
/home/james/mcp/
├── manual/                          # Original documentation (READ-ONLY)
├── processed_docs/                  # Output directory
│   ├── raw/                        # Cleaned text without metadata
│   ├── metadata/                   # Extracted frontmatter and structure
│   ├── chunks/                     # Pre-chunked content
│   └── manifest.json               # Processing metadata
├── preprocessing/                   # Processing scripts
│   ├── src/
│   │   ├── mdx_processor.py       # MDX parsing and cleaning
│   │   ├── chunker.py             # Document chunking logic
│   │   ├── metadata_extractor.py  # Frontmatter and structure extraction
│   │   ├── pipeline.py            # Main orchestration
│   │   └── utils.py               # Helper functions
│   └── config/
│       └── processing_config.yaml  # Configuration settings
├── pixi.toml                       # Project dependencies
```

## Processing Pipeline

### Phase 1: Initialization
- Set up Pixi environment
- Install dependencies (python-frontmatter, pyyaml, tiktoken, etc.)
- Create output directory structure
- Generate processing manifest

### Phase 2: MDX Processing
For each `.mdx` file in `/manual`:

1. **Parse Frontmatter**
   - Extract YAML metadata (title, description, sidebar info)
   - Capture file path and hierarchy
   - Generate unique document ID

2. **Clean Content**
   - Remove JSX imports (`import ... from ...`)
   - Strip JSX components (`<Component>...</Component>`)
   - Preserve code blocks with language identifiers
   - Clean markdown artifacts
   - Normalize whitespace

3. **Extract Structure**
   - Identify header hierarchy (H1-H6)
   - Map section relationships
   - Extract code blocks with context
   - Identify special elements (notes, warnings, tips)

### Phase 3: Chunking Strategy

Following the research-backed approach from `vector.md`:

**Chunking Parameters:**
- Base chunk size: 400 tokens (optimal for all-mpnet-base-v2)
- Overlap: 80 tokens (20%)
- Minimum chunk size: 100 tokens
- Strategy: Recursive text splitting with semantic boundaries

**Chunk Hierarchy:**
1. Split by major sections (headers)
2. Split by paragraphs (double newline)
3. Split by sentences (periods, maintaining code blocks)
4. Token-level split (last resort)

**Metadata per Chunk:**
```json
{
  "chunk_id": "basics-001",
  "document_id": "basics",
  "file_path": "manual/basics.mdx",
  "section_hierarchy": ["Mojo language basics", "Hello world"],
  "position": 1,
  "token_count": 387,
  "has_code": true,
  "chunk_type": "section",
  "url": "https://docs.modular.com/mojo/manual/basics#hello-world"
}
```

### Phase 4: Output Generation

**1. Raw Content** (`processed_docs/raw/`)
- Plain text files with cleaned content
- One file per source document
- Preserves paragraph structure

**2. Metadata** (`processed_docs/metadata/`)
- JSON files with extracted frontmatter
- Document structure information
- Section mappings

**3. Chunks** (`processed_docs/chunks/`)
- JSONL format (one chunk per line)
- Includes content and all metadata
- Ready for embedding pipeline

**4. Manifest** (`processed_docs/manifest.json`)
```json
{
  "processing_date": "2025-10-10T12:00:00Z",
  "source_directory": "/home/james/mcp/manual",
  "total_documents": 25,
  "total_chunks": 487,
  "configuration": {
    "chunk_size": 400,
    "chunk_overlap": 80,
    "preserve_code_blocks": true
  },
  "documents": [
    {
      "file_path": "manual/basics.mdx",
      "document_id": "basics",
      "chunks_generated": 23,
      "content_hash": "a1b2c3d4..."
    }
  ]
}
```

## Implementation Details

### MDX Processing Rules

**JSX Component Handling:**
- `<Button>`: Remove entirely (navigation element)
- `<DocLink>`: Extract href and convert to markdown link
- `<CodeExample>`: Preserve as code block with language
- Custom components: Extract text content or remove

**Import Statement Removal:**
```python
import_pattern = re.compile(r'^import .+ from .+$', re.MULTILINE)
```

**Special Markdown Elements:**
- `:::note` → Extract as NOTE marker
- `:::warning` → Extract as WARNING marker
- Code blocks → Preserve with language identifier
- Tables → Keep markdown structure

### Code Block Preservation

Code blocks are crucial for Mojo documentation. Strategy:

1. **Detect Code Blocks**: Preserve fenced code blocks (``` or ~~~)
2. **Extract Language**: Capture language identifier (mojo, python, etc.)
3. **Context Preservation**: Include surrounding explanation text
4. **Chunking Decision**: 
   - Small code blocks (<50 tokens): Include with surrounding text
   - Large code blocks (>50 tokens): Create dedicated chunk with context

### Hierarchical Section Tracking

Maintain section context for each chunk:

```python
section_hierarchy = []
current_h1 = None
current_h2 = None
current_h3 = None

# Example output: ["Mojo language basics", "Variables", "Type inference"]
```

## Quality Assurance

### Validation Checks

1. **Content Preservation**
   - Verify all source files processed
   - Ensure no data loss during cleaning
   - Validate chunk reconstruction

2. **Metadata Accuracy**
   - Confirm frontmatter extraction
   - Verify section hierarchy correctness
   - Check URL generation

3. **Token Counts**
   - Validate chunk sizes within limits
   - Ensure overlap calculations correct
   - Verify minimum chunk requirements

4. **Code Block Integrity**
   - Confirm all code blocks preserved
   - Verify language identifiers correct
   - Check syntax highlighting compatibility

### Output Validation Script

Generate validation report including:
- Total documents processed
- Total chunks generated
- Average chunk size
- Token distribution histogram
- Code block statistics
- Missing metadata warnings
- Processing errors and warnings

## Configuration

### `processing_config.yaml`

```yaml
source:
  directory: "/home/james/mcp/manual"
  file_patterns:
    - "*.mdx"
    - "*.md"
  exclude_patterns:
    - "*.draft.mdx"
    - "node_modules/**"

output:
  base_directory: "/home/james/mcp/processed_docs"
  raw_dir: "raw"
  metadata_dir: "metadata"
  chunks_dir: "chunks"
  manifest_file: "manifest.json"

chunking:
  strategy: "recursive"
  chunk_size: 400
  chunk_overlap: 80
  min_chunk_size: 100
  preserve_code_blocks: true
  code_block_threshold: 50  # tokens

processing:
  remove_jsx_components: true
  remove_imports: true
  preserve_code_blocks: true
  normalize_whitespace: true
  extract_urls: true
  url_base: "https://docs.modular.com/mojo/manual"

metadata:
  extract_frontmatter: true
  generate_section_hierarchy: true
  calculate_content_hash: true
  include_statistics: true

validation:
  check_content_preservation: true
  validate_chunk_sizes: true
  verify_metadata_completeness: true
  generate_report: true
```

## Next Steps

1. **Initialize Pixi Project**: Create `pixi.toml` with dependencies
2. **Implement Core Modules**: Build processor, chunker, and pipeline
3. **Test with Sample Files**: Validate on 2-3 manual files
4. **Full Processing**: Run on complete manual directory
5. **Quality Review**: Examine output for accuracy
6. **Documentation**: Generate processing report
7. **Integration Prep**: Prepare data for vectorization phase

## Success Metrics

- ✅ All 25+ manual files processed without errors
- ✅ 400-600 total chunks generated (estimated)
- ✅ Average chunk size: 350-400 tokens
- ✅ Code blocks preserved with 100% accuracy
- ✅ Section hierarchy correctly extracted
- ✅ Metadata complete for all documents
- ✅ Output ready for embedding pipeline

## Dependencies

- Python 3.12+
- python-frontmatter (MDX frontmatter parsing)
- pyyaml (configuration)
- tiktoken (accurate token counting)
- regex (advanced pattern matching)
- pathlib (file operations)
- json (data serialization)

## Timeline Estimate

- Setup & Configuration: 30 minutes
- Core Implementation: 2-3 hours
- Testing & Validation: 1 hour
- Full Processing: 15 minutes
- Documentation & Review: 30 minutes

**Total: ~4-5 hours**

## Notes

- This preprocessing step is separate from vectorization
- Output format optimized for MAX embedding pipeline
- All processing is deterministic and reproducible
- Original files remain untouched
- Processing can be re-run with updated configuration
