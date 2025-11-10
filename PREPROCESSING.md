# Preprocessing Pipeline

Detailed reference for the build-time preprocessing stage: from raw Markdown/MDX to optimized chunks ready for embedding generation.

## Overview

The preprocessing pipeline transforms technical documentation into clean, semantically-meaningful chunks that are optimized for embedding generation and hybrid search.

```
Source Files (Markdown/MDX)
        ↓
Parse & Clean (remove JSX, normalize)
        ↓
Extract Metadata (frontmatter, hierarchy)
        ↓
Chunk Intelligently (tokenizer-aware, semantic boundaries)
        ↓
Generate Outputs (chunks, metadata, manifest)
        ↓
Processed Artifacts Ready for Embedding
```

---

## Configuration

The preprocessing pipeline is configured via `preprocessing/config/processing_config.yaml`.

### Source Configuration

```yaml
source:
  directory: "/home/james/mcp/manual"
  file_patterns:
    - "*.mdx"
    - "*.md"
  exclude_patterns:
    - "*.draft.mdx"
    - "node_modules/**"
```

- **directory**: Root directory containing documentation files
- **file_patterns**: Glob patterns for files to process
- **exclude_patterns**: Patterns to skip

### Output Configuration

```yaml
output:
  base_directory: "/home/james/mcp/processed_docs"
  raw_dir: "raw"
  metadata_dir: "metadata"
  chunks_dir: "chunks"
  manifest_file: "manifest.json"
```

All outputs are relative to `base_directory`.

### Chunking Configuration

```yaml
chunking:
  strategy: "recursive"           # Strategy: recursive or simple
  chunk_size: 400                 # Target size in tokens
  chunk_overlap: 80               # Overlap in tokens
  min_chunk_size: 100             # Minimum chunk size
  preserve_code_blocks: true      # Don't split code blocks
  code_block_threshold: 50        # Tokens to consider "code block"
```

**Key Parameters**:

- **chunk_size**: Optimal for `sentence-transformers/all-mpnet-base-v2` is 350–400 tokens
- **chunk_overlap**: 20% overlap (80 tokens) provides context preservation
- **min_chunk_size**: Chunks below 100 tokens are typically low-signal
- **preserve_code_blocks**: Keeps code examples intact (not split mid-function)

### Processing Configuration

```yaml
processing:
  remove_jsx_components: true     # Strip JSX (React components)
  remove_imports: true            # Remove import statements
  preserve_code_blocks: true      # Keep markdown code fences
  normalize_whitespace: true      # Clean up spacing
  extract_urls: true              # Generate documentation URLs
  url_base: "https://docs.modular.com/mojo/manual"  # Base for URLs
```

### Metadata Extraction

```yaml
metadata:
  extract_frontmatter: true       # Parse YAML frontmatter
  generate_section_hierarchy: true  # Build h1→h6 mapping
  calculate_content_hash: true    # SHA256 of content
  include_statistics: true        # Token counts, code block flags
```

### Validation Configuration

```yaml
validation:
  check_content_preservation: true      # Verify no data loss
  validate_chunk_sizes: true            # Ensure within limits
  verify_metadata_completeness: true    # All required fields
  generate_report: true                 # Detailed validation report
```

---

## How It Works

### Phase 1: Parsing & Cleaning

#### MDX-Specific Processing

**Input**: `manual/basics.mdx`

```mdx
---
title: "Mojo Language Basics"
description: "Getting started with Mojo"
sidebar_position: 1
---

import Button from "./components/Button"

# {frontmatter.title}

<Button href="/mojo/manual/hello-world">Get Started</Button>

Here's how to write your first program...

```mojo
fn main():
    print("Hello, world!")
```

:::note
This is important information.
:::
```

**Processing Steps**:

1. **Extract Frontmatter**
   ```yaml
   title: "Mojo Language Basics"
   description: "Getting started with Mojo"
   sidebar_position: 1
   ```

2. **Remove Imports**
   - Deletes lines matching `^import .+ from .+$`

3. **Remove JSX Components**
   - `<Button>...</Button>` → deleted or converted

4. **Preserve Code Blocks**
   - ``` ```mojo ... ``` ``` → preserved with language identifier

5. **Clean Markdown**
   - Normalize whitespace
   - Fix broken formatting
   - Keep special note/warning sections

**Output**: Clean markdown text ready for chunking

```markdown
# Mojo Language Basics

Here's how to write your first program...

```mojo
fn main():
    print("Hello, world!")
```

**Note**: This is important information.
```

---

### Phase 2: Chunking Strategy

The preprocessing uses **LangchainMarkdownChunker**, a tokenizer-aware chunker with the following strategy:

#### Chunking Algorithm (Recursive)

1. **Split by Headers** (Primary boundary)
   - Respect Markdown hierarchy (h1, h2, h3, ...)
   - Each header section becomes a candidate chunk

2. **Split by Paragraphs** (Secondary boundary)
   - Double newlines (`\n\n`) within sections
   - Preserve paragraph structure

3. **Split by Sentences** (Tertiary boundary)
   - Periods, exclamation marks, question marks
   - Maintain semantic coherence

4. **Split by Tokens** (Last resort)
   - If all else fails, split at word boundaries
   - Ensures chunk_size limit respected

#### Example Chunking

**Input Document**: "Mojo Language Basics" (800 tokens total)

```
Header 1: Mojo Language Basics (section_hierarchy = ["Mojo Language Basics"])
├─ Chunk 1: Introduction paragraph (380 tokens)
├─ Chunk 2: History section (390 tokens)
│
Header 2: Hello World (section_hierarchy = ["Mojo Language Basics", "Hello World"])
├─ Chunk 3: Code example + explanation (375 tokens)
├─ Chunk 4: Key concepts (355 tokens)
│
Header 2: Advanced Topics (section_hierarchy = ["Mojo Language Basics", "Advanced Topics"])
├─ Chunk 5: Performance optimization (420 tokens) [exceeds target, but code block preserved]
```

#### Code Block Handling

Code blocks are special:

- **Small code blocks** (<50 tokens): Include with surrounding text
- **Large code blocks** (>50 tokens): Create dedicated chunk if necessary
- **Multiple blocks**: Each gets its own "context chunk" with explanation

**Example**:

```markdown
## Function Definition

Here's how to define a function:

```mojo
fn add(x: Int, y: Int) -> Int:
    return x + y
```

Functions in Mojo are declared with the `fn` keyword...

```mojo
fn multiply(x: Int, y: Int) -> Int:
    return x * y
```
```

**Chunked as**:
- Chunk 1: "Function Definition" + first code block (300 tokens)
- Chunk 2: Second code block + explanation (280 tokens)

---

### Phase 3: Metadata Extraction

For each chunk, the following metadata is extracted:

```json
{
  "chunk_id": "basics-001",
  "document_id": "basics",
  "file_path": "manual/basics.mdx",
  "position": 0,
  "title": "Mojo Language Basics",
  "content": "...",
  "token_count": 380,
  "has_code": true,
  "section_hierarchy": ["Mojo Language Basics"],
  "section_url": "https://docs.modular.com/mojo/manual/basics",
  "url": "https://docs.modular.com/mojo/manual/basics",
  "frontmatter": {
    "sidebar_position": 1,
    "description": "Getting started with Mojo"
  }
}
```

#### Section Hierarchy

Extracted from header structure:

```markdown
# Mojo Language Basics          → ["Mojo Language Basics"]
## Hello World                  → ["Mojo Language Basics", "Hello World"]
### Running the Program         → ["Mojo Language Basics", "Hello World", "Running the Program"]
```

The section hierarchy enables:
- Better context in search results
- Breadcrumb-like navigation
- More accurate snippet generation

#### URL Generation

Generated based on:
1. **Source file path**: `manual/basics.mdx` → `basics`
2. **Section headers**: Auto-generate anchors (lowercase, hyphenated)
3. **Base URL**: From config (`url_base`)

```
File: manual/basics.mdx
Header: "Hello World" → anchor "hello-world"
Result: https://docs.modular.com/mojo/manual/basics#hello-world
```

---

## Output Formats

### 1. Raw Content (`processed_docs/raw/`)

Clean markdown text, one file per source document.

**File**: `processed_docs/raw/basics.txt`

```markdown
# Mojo Language Basics

[Full cleaned content without metadata or chunking]

All code blocks preserved.
All JSX removed.
Whitespace normalized.
```

### 2. Metadata (`processed_docs/metadata/`)

Document-level metadata (one JSON file per source doc).

**File**: `processed_docs/metadata/basics.json`

```json
{
  "document_id": "basics",
  "file_path": "manual/basics.mdx",
  "title": "Mojo Language Basics",
  "description": "Getting started with Mojo",
  "url": "https://docs.modular.com/mojo/manual/basics",
  "total_chunks": 4,
  "total_tokens": 1380,
  "has_code": true,
  "code_block_count": 3,
  "frontmatter": {
    "sidebar_position": 1
  }
}
```

### 3. Chunks (`processed_docs/chunks/`)

Chunked content in JSONL format (one JSON object per line).

**File**: `processed_docs/chunks/basics.jsonl`

```jsonl
{"chunk_id": "basics-001", "document_id": "basics", "title": "Mojo Language Basics", "content": "...", "token_count": 380, ...}
{"chunk_id": "basics-002", "document_id": "basics", "title": "Mojo Language Basics → Hello World", "content": "...", "token_count": 375, ...}
{"chunk_id": "basics-003", "document_id": "basics", "title": "Mojo Language Basics → Hello World → Running the Program", "content": "...", "token_count": 390, ...}
{"chunk_id": "basics-004", "document_id": "basics", "title": "Mojo Language Basics → Key Concepts", "content": "...", "token_count": 355, ...}
```

### 4. Manifest (`processed_docs/manifest.json`)

Summary of entire processing run.

```json
{
  "processing_date": "2025-11-07T15:30:00Z",
  "source_directory": "/home/james/mcp/manual",
  "total_documents": 25,
  "total_chunks": 487,
  "total_tokens": 184230,
  "configuration": {
    "chunk_size": 400,
    "chunk_overlap": 80,
    "preserve_code_blocks": true
  },
  "documents": [
    {
      "id": "basics",
      "file_path": "manual/basics.mdx",
      "title": "Mojo Language Basics",
      "chunks": 4,
      "tokens": 1380,
      "has_code": true
    },
    {
      "id": "variables",
      "file_path": "manual/variables.mdx",
      "title": "Variables and Types",
      "chunks": 5,
      "tokens": 1890,
      "has_code": true
    }
  ],
  "statistics": {
    "avg_chunk_size": 378.2,
    "min_chunk_size": 102,
    "max_chunk_size": 498,
    "median_chunk_size": 387,
    "chunks_with_code": 156,
    "processing_time_seconds": 87
  }
}
```

---

## Quality Assurance

### Validation Checks

The preprocessing pipeline performs these checks:

1. **File Discovery**
   - All source files found
   - Patterns match expected count

2. **Content Preservation**
   - No data loss during cleaning
   - Chunk reconstruction equals original
   - All code blocks present

3. **Metadata Completeness**
   - Every chunk has required fields
   - URLs well-formed
   - Section hierarchy valid

4. **Chunk Size Constraints**
   - All chunks within [min, max] token range
   - Overlap calculations correct
   - No empty chunks

5. **Code Block Integrity**
   - All code blocks preserved
   - Language identifiers correct
   - Syntax highlighting preserved

### Validation Report

Generated if `validation.generate_report: true`:

```
============================================================
📊 Processing Validation Report
============================================================

✅ FILE DISCOVERY
   Total files found: 25
   Expected: 25
   Status: PASS

✅ CONTENT PRESERVATION
   Original total tokens: 184230
   Reconstructed total tokens: 184230
   Difference: 0 (0.00%)
   Status: PASS

✅ CHUNK SIZE CONSTRAINTS
   Total chunks: 487
   Min size: 102 tokens
   Max size: 498 tokens
   Target: 400 tokens
   Chunks within ±25% of target: 456 (93.6%)
   Status: PASS

✅ METADATA COMPLETENESS
   Chunks with missing fields: 0
   Chunks with invalid URLs: 0
   Status: PASS

✅ CODE BLOCK INTEGRITY
   Original code blocks: 156
   Preserved code blocks: 156
   Missing: 0
   Status: PASS

============================================================
Summary: ALL CHECKS PASSED ✅
============================================================
```

---

## Running Preprocessing

### Quick Start

```bash
# Configure your source
nano preprocessing/config/processing_config.yaml
# Update: source.directory, url_base, etc.

# Run preprocessing
pixi run process
```

### Output Example

```
🔥 Starting Preprocessing Pipeline

Configuration:
  Source: /home/james/mcp/manual
  Chunk Size: 400 tokens
  Overlap: 80 tokens

Processing files: 100%|████████| 25/25 [00:45<00:00, 1.82s/it]

============================================================
📊 Processing Summary
============================================================
Documents processed: 25
Total chunks generated: 487
Total tokens: 184,230
Average tokens per chunk: 378.23
Chunks with code: 156

Output directory: /home/james/mcp/processed_docs
✅ Processing complete!
```

---

## Troubleshooting

### Issue: "No files found to process"

**Cause**: Source directory path incorrect or no matching files

**Solution**:
```bash
# Verify path exists
ls -la /path/to/docs/

# Check file patterns
find /path/to/docs -name "*.mdx" -o -name "*.md"

# Update config
nano preprocessing/config/processing_config.yaml
```

### Issue: Import errors

**Cause**: Dependencies not installed

**Solution**:
```bash
pixi install
pixi shell
python -m preprocessing.src.pipeline
```

### Issue: Out of memory

**Cause**: Processing too many large files at once

**Solution**:
```yaml
# In processing_config.yaml, add:
exclude_patterns:
  - "node_modules/**"
  - "images/**"
  - "*.backup.mdx"
```

### Issue: Chunks too small or too large

**Cause**: chunk_size parameter doesn't match content style

**Solution**:
```yaml
# Try adjusting:
chunking:
  chunk_size: 350      # Try 300–500 range
  chunk_overlap: 60    # Reduce if overlapping too much
  min_chunk_size: 80   # Lower for more chunks
```

---

## Performance Tips

1. **Exclude unnecessary directories**:
   ```yaml
   exclude_patterns:
     - "images/**"
     - "*.draft.mdx"
   ```

2. **Use appropriate chunk size** for your model:
   - `all-mpnet-base-v2`: 350–400 tokens
   - `all-MiniLM-L6-v2`: 200–250 tokens
   - Custom models: check token limits

3. **Preserve code blocks** if documentation is code-heavy:
   ```yaml
   preserve_code_blocks: true
   code_block_threshold: 50
   ```

4. **Validate in stages**:
   ```bash
   pixi run process
   # Check output before embedding
   ls -la processed_docs/
   head processed_docs/chunks/*.jsonl
   ```

---

## Next Steps

After preprocessing:

1. **Review output** — Spot-check chunks for quality
2. **Generate embeddings** — `pixi run generate-embeddings`
3. **Consolidate** — `pixi run consolidate`
4. **Load to DuckLake** — `pixi run load`
5. **Create indexes** — `pixi run index`

See [DEVELOPMENT.md](DEVELOPMENT.md) for full pipeline commands.

