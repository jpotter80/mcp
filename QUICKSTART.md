# Quick Start Guide - Mojo Manual Preprocessing

## Overview
This guide will help you process the Mojo manual documentation in under 15 minutes.

## Prerequisites
- Kubuntu 24.04 (or similar Linux)
- Python 3.12+
- Internet connection (for initial setup)

## Step-by-Step Instructions

### 1. Install Pixi (if not already installed)

```bash
curl -fsSL https://pixi.sh/install.sh | bash
source ~/.bashrc  # or ~/.zshrc
```

Verify installation:
```bash
pixi --version
```

### 2. Navigate to Project Directory

```bash
cd /home/james/mcp
```

### 3. Install Dependencies

```bash
pixi install
```

This will:
- Create a Python 3.12 environment
- Install python-frontmatter, pyyaml, tiktoken, tqdm, pytest
- Set up the project

**Expected time**: 1-2 minutes

### 4. Verify Setup

```bash
# Check that manual directory exists and has files
ls -la manual/

# Should see files like:
# basics.mdx
# variables.mdx
# functions.mdx
# etc.

# Check configuration
cat preprocessing/config/processing_config.yaml
```

### 5. Run Preprocessing

```bash
pixi run process
```

You'll see:
```
🔥 Starting Mojo Manual Preprocessing Pipeline

Found 25 documentation files to process

Processing files: 100%|████████████| 25/25 [00:45<00:00, 1.82s/it]

============================================================
📊 Processing Summary
============================================================
Documents processed: 25
Total chunks generated: 487
Total tokens: 184,230
Average tokens per chunk: 378.23
Chunks with code: 156

Output directory: /home/james/mcp/processed_docs
============================================================
✅ Processing complete!

🔍 Validating processed output...

✅ Validation passed!
```

**Expected time**: 1-2 minutes

### 6. Explore Output

```bash
# View the manifest
cat processed_docs/manifest.json | jq '.'

# Check raw processed content
ls processed_docs/raw/
cat processed_docs/raw/basics.txt | head -n 20

# View metadata for a document
cat processed_docs/metadata/basics.json | jq '.'

# Examine chunks
head -n 3 processed_docs/chunks/basics.jsonl | jq '.'
```

### 7. View Statistics

```bash
pixi run stats
```

Output:
```
============================================================
📈 Detailed Statistics
============================================================

Documents: 25
Chunks: 487
Tokens: 184,230

Chunk Size Distribution:
  Min: 102 tokens
  Max: 498 tokens
  Average: 378.23 tokens
  Median: 387 tokens
============================================================
```

## Understanding the Output

### Directory Structure

```
processed_docs/
├── raw/              # Clean markdown text (25 files)
├── metadata/         # Document metadata JSON (25 files)
├── chunks/           # Chunked content JSONL (25 files)
└── manifest.json    # Processing summary
```

### Sample Chunk Format

Each line in a `*.jsonl` file contains one chunk:

```json
{
  "chunk_id": "basics-001",
  "document_id": "basics",
  "content": "# Mojo language basics\n\nThis page provides...",
  "position": 0,
  "token_count": 387,
  "has_code": true,
  "section_hierarchy": ["Mojo language basics", "Hello world"],
  "metadata": {
    "file_path": "manual/basics.mdx",
    "url": "https://docs.modular.com/mojo/manual/basics",
    "title": "Mojo language basics",
    "section_url": "https://docs.modular.com/mojo/manual/basics#hello-world"
  }
}
```

## Common Tasks

### Reprocess Everything

```bash
pixi run clean   # Remove old output
pixi run process # Process again
```

### Process with Custom Configuration

```bash
# Edit config
nano preprocessing/config/processing_config.yaml

# Change chunk_size, overlap, etc.

# Reprocess
pixi run process
```

### Validate Output

```bash
pixi run validate
```

### Clean Up Output

```bash
# Removes processed_docs/ but keeps original manual/
pixi run clean
```

## Troubleshooting

### Issue: "No files found to process"

**Solution**: Check the source directory path in config:
```bash
grep "directory:" preprocessing/config/processing_config.yaml
# Should be: /home/james/mcp/manual
```

### Issue: Import errors

**Solution**: Activate pixi shell:
```bash
pixi shell
python -m preprocessing.src.pipeline
```

### Issue: Permission denied

**Solution**: Check file permissions:
```bash
chmod -R u+w processed_docs/
```

### Issue: Out of memory

**Solution**: Process documents in smaller batches by editing the config to exclude some directories temporarily.

## Next Steps

After preprocessing, the data is ready for:

1. **Vector Embedding Generation**
   ```bash
   # Will use MAX serving with all-mpnet-base-v2
   # Generates 768-dimensional embeddings
   ```

2. **Database Storage**
   ```bash
   # Store in PostgreSQL with pgvector
   # Enable semantic search
   ```

3. **MCP Server Deployment**
   ```bash
   # Expose via Model Context Protocol
   # Enable AI agent access
   ```

## Verification Checklist

- [ ] Pixi installed and working
- [ ] Dependencies installed successfully  
- [ ] Manual directory contains MDX files
- [ ] Processing completed without errors
- [ ] Output directory created with all subdirectories
- [ ] Manifest file generated
- [ ] Validation passed
- [ ] Statistics look reasonable

## Success Indicators

✅ **You're ready for the next phase if:**
- Processing completed in 1-2 minutes
- Validation passed without errors
- Generated 400-600 chunks from ~25 documents
- Average chunk size is 350-400 tokens
- Manifest shows reasonable statistics

## Getting Help

1. **Read the docs**:
   - `preprocessing/README.md` - Detailed module documentation
   - `PREPROCESSING_PLAN.md` - Architecture and design
   - `PROJECT_STATUS.md` - Complete project overview

2. **Check the code**:
   - All modules have detailed docstrings
   - Configuration file has inline comments

3. **Examine output**:
   - Use `jq` to inspect JSON files
   - Check logs in terminal output

## Time Breakdown

- Setup (first time): ~3 minutes
- Processing: ~2 minutes  
- Validation: ~30 seconds
- Exploration: ~5 minutes
- **Total: ~10-15 minutes**

## What's Next?

You now have:
- ✅ Clean, processed documentation
- ✅ Optimally-sized chunks (400 tokens)
- ✅ Rich metadata for each chunk
- ✅ Section hierarchy preserved
- ✅ Code blocks intact
- ✅ URLs generated

Ready for:
- 🔜 Vector embedding generation (Phase 2)
- 🔜 Database storage with pgvector (Phase 3)
- 🔜 MCP resource server deployment (Phase 4)

---

**Quick Reference Commands**:
```bash
pixi install         # Setup
pixi run process     # Process all docs
pixi run validate    # Check output
pixi run stats       # View statistics
pixi run clean       # Remove output
```

Happy processing! 🔥
