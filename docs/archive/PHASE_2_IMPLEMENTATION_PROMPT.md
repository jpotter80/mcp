# Phase 2 Implementation Prompt for Next Session

## Context
The MCP project restructuring is proceeding with Phase 2. Phase 1 (directory structure and configuration templates) has been completed and merged to main. Phase 2 introduces a pluggable multi-format document processor architecture to support `.mdx`, `.md`, and other formats.

## Current State
- Main branch has Phase 1 changes merged
- Directory structure from Phase 1 is in place
- Ready to implement Phase 2 processor architecture

## Task: Execute Phase 2

### Objective
Create a pluggable, format-agnostic document processor architecture that supports `.mdx`, `.md`, and other formats via factory pattern. This enables support for multiple documentation sources (Mojo, DuckDB, etc.) each potentially using different formats.

### Branch
`restructure/02-multi-format-doc-support`

### Instructions to Follow
1. Reference: `/home/james/mcp/RESTRUCTURING_PLAN.md` (lines 464-550, "Phase 2: Support Multi-Format Processing" section)
2. Execute all steps in sequence:
   - Create feature branch
   - Create base processor abstract class
   - Create MarkdownProcessor for .md files
   - Create ProcessorFactory for format-based processor selection
   - Update existing MDXProcessor to inherit from base class
   - Update pipeline.py to use the factory pattern
   - Verify all processors work correctly
   - Commit with clear Phase 2 message
   - Merge to main

### Key Files to Create
- `shared/preprocessing/src/base_processor.py` — Abstract base class for all processors
- `shared/preprocessing/src/markdown_processor.py` — Processor for `.md` files
- `shared/preprocessing/src/processor_factory.py` — Factory for creating processors based on format

### Key Files to Modify
- `shared/preprocessing/src/mdx_processor.py` — Update to inherit from BaseDocumentProcessor
- `shared/preprocessing/src/pipeline.py` — Update to use ProcessorFactory instead of hardcoded MDXProcessor
- `servers/mojo-manual-mcp/config/processing_config.yaml` — Ensure `format: "mdx"` is specified

### Implementation Details

#### Step 1: Create Feature Branch
```bash
cd /home/james/mcp
git checkout main
git pull
git checkout -b restructure/02-multi-format-doc-support
```

#### Step 2: Create base_processor.py
Location: `shared/preprocessing/src/base_processor.py`

Create an abstract base class with:
- `__init__(self, config: Dict)` — Initialize with config
- `@abstractmethod process_file(self, file_path: Path) -> Dict` — Process a single file
- Abstract methods for any common interface all processors must implement

Reference existing MDXProcessor to understand the expected interface and return structure.

#### Step 3: Create markdown_processor.py
Location: `shared/preprocessing/src/markdown_processor.py`

Create MarkdownProcessor class that:
- Inherits from BaseDocumentProcessor
- Handles YAML frontmatter (if present)
- Processes markdown-specific syntax
- Returns same structure as MDXProcessor (to ensure compatibility)
- Can be tested with sample .md files

#### Step 4: Create processor_factory.py
Location: `shared/preprocessing/src/processor_factory.py`

Create ProcessorFactory class that:
- Has a `PROCESSORS` dict mapping format strings to processor classes
- Implements `get_processor(config: Dict, format_type: str)` classmethod
- Raises ValueError if format is unsupported
- Currently supports: "mdx", "md", "markdown"

Code template provided in RESTRUCTURING_PLAN.md (lines 475-490).

#### Step 5: Update mdx_processor.py
- Import BaseDocumentProcessor
- Change class definition: `class MDXProcessor(BaseDocumentProcessor):`
- Move `__init__` call to super()
- Ensure `process_file()` method signature matches base class
- No logic changes needed

#### Step 6: Update pipeline.py
- Import ProcessorFactory at top
- In `process_all_documents()` method:
  - Get format from config: `format_type = self.config["source"].get("format", "mdx")`
  - Create processor via factory: `processor = ProcessorFactory.get_processor(self.config, format_type)`
  - Use processor instead of hardcoded MDXProcessor instance
- Verify the rest of pipeline logic works unchanged

#### Step 7: Verify Configuration
- Check `servers/mojo-manual-mcp/config/processing_config.yaml`
- Ensure `source.format: "mdx"` is present (lines 6-7)
- If not, add it before the `file_patterns` section

#### Step 8: Test & Verification
Run a quick test to ensure processors can be instantiated:
```bash
python3 -c "
from shared.preprocessing.src.processor_factory import ProcessorFactory
config = {'source': {}}
mdx = ProcessorFactory.get_processor(config, 'mdx')
md = ProcessorFactory.get_processor(config, 'md')
print('✓ MDXProcessor created:', type(mdx).__name__)
print('✓ MarkdownProcessor created:', type(md).__name__)
try:
    bad = ProcessorFactory.get_processor(config, 'invalid')
except ValueError as e:
    print('✓ ValueError raised for unsupported format:', str(e))
"
```

#### Step 9: Commit Changes
```bash
git add -A
git commit -m "feat: Add pluggable multi-format document processor support

- Create BaseDocumentProcessor abstract class defining processor interface
- Create MarkdownProcessor for .md file processing with YAML frontmatter support
- Create ProcessorFactory for format-based processor selection
- Update MDXProcessor to inherit from BaseDocumentProcessor
- Update pipeline.py to use factory pattern for processor instantiation
- Configuration now supports 'format' field (mdx, markdown, etc.)
- Supports mixed formats in same documentation source

Factory pattern allows easy addition of new processors for other formats.
Pipeline remains unchanged except for processor instantiation method.

Phase: 2/8
Branch: restructure/02-multi-format-doc-support"
```

#### Step 10: Merge to Main
```bash
git checkout main
git merge restructure/02-multi-format-doc-support -m "Merge Phase 2: Multi-format document processor support"
```

### Verification Checklist
- [ ] All 3 new files created with valid Python syntax
- [ ] BaseDocumentProcessor is abstract (has @abstractmethod decorators)
- [ ] MarkdownProcessor inherits from BaseDocumentProcessor
- [ ] ProcessorFactory.get_processor() works for "mdx", "md", "markdown"
- [ ] ProcessorFactory raises ValueError for unsupported formats
- [ ] MDXProcessor inherits from BaseDocumentProcessor without logic changes
- [ ] pipeline.py uses ProcessorFactory correctly
- [ ] processing_config.yaml has `format: "mdx"` specified
- [ ] Test script passes all checks (see Step 8)
- [ ] Git branch is clean and ready to merge
- [ ] All changes committed locally
- [ ] Merged successfully to main branch

### Success Criteria
- All 3 new processor files created with correct inheritance
- Factory pattern working and tested
- Pipeline uses factory for processor selection
- No errors when running test verification
- Single logical commit with clear message
- Changes merged to main

### Key Design Patterns
- **Abstract Base Class**: BaseDocumentProcessor defines the interface all processors must implement
- **Factory Pattern**: ProcessorFactory centralizes processor creation and format mapping
- **Pluggable Architecture**: New formats can be added by creating a processor class and registering in PROCESSORS dict
- **Configuration-Driven**: Format selection via config (not hardcoded)

### Resources
- RESTRUCTURING_PLAN.md (lines 464-550) — Detailed Phase 2 specification
- Existing `preprocessing/src/mdx_processor.py` — Reference implementation
- `shared/preprocessing/config/processing_config.yaml` — Template config

### If Issues Arise
- **Import errors**: Ensure `__init__.py` exists in `shared/preprocessing/src/`
- **Abstract method errors**: Use `from abc import ABC, abstractmethod` and `@abstractmethod` decorator
- **Processor not registered**: Check ProcessorFactory.PROCESSORS dict has correct format keys
- **Config issues**: Ensure processing_config.yaml has `format` field under `source` section

### Architecture Note
This phase prepares the foundation for Phase 3 (parameterized build scripts) and beyond. The factory pattern keeps the code maintainable as more documentation sources are added. Each format can have its own processor with custom logic, while the pipeline remains format-agnostic.

---

**Start with**: `git checkout -b restructure/02-multi-format-doc-support`

**Follow**: Implementation steps 1-10 above in order

**Complete when**: All changes merged to main branch and verified working
