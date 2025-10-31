"""
Main preprocessing pipeline orchestrator.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm  # type: ignore
import shutil

from .utils import (
    load_config,
    save_json,
    save_jsonl,
    create_directory_structure,
    get_file_list,
    generate_document_id,
)
from .mdx_processor import MDXProcessor
from .chunker import LangchainMarkdownChunker, DocumentChunk
from .metadata_extractor import MetadataExtractor


def init_directories(config: Dict | None = None) -> None:
    """Initialize output directory structure, cleaning it first."""
    if config is None:
        config = load_config()
    
    base_dir = Path(config["output"]["base_directory"])
    subdirs = [
        config["output"]["raw_dir"],
        config["output"]["metadata_dir"],
        config["output"]["chunks_dir"],
    ]

    # Clean existing output directories to prevent stale files
    for subdir_name in subdirs:
        subdir_path = base_dir / subdir_name
        if subdir_path.exists():
            print(f"🧹 Cleaning stale output from {subdir_path}...")
            shutil.rmtree(subdir_path)
    
    create_directory_structure(base_dir, subdirs)
    print(f"✓ Created fresh output directories in {base_dir}")


class DocumentProcessingPipeline:
    """
    Complete pipeline for processing documentation into searchable chunks.
    
    Workflow:
    1. Discover all documentation files
    2. Process each file (clean MDX, extract metadata)
    3. Chunk documents into optimal sizes
    4. Save processed output in multiple formats
    5. Generate processing manifest
    """

    def __init__(self, config_path: str = "preprocessing/config/processing_config.yaml"):
        self.config = load_config(config_path)
        self.base_dir = Path(self.config["output"]["base_directory"])
        self.source_dir = Path(self.config["source"]["directory"])
        
        # Initialize processors
        self.mdx_processor = MDXProcessor(self.config)
        self.chunker = LangchainMarkdownChunker(self.config)
        self.metadata_extractor = MetadataExtractor(self.config)
        
        # Initialize output directories
        init_directories(self.config)

    def process_all_documents(self) -> Dict:
        """
        Process all documentation files in the source directory.
        
        Returns:
            Processing manifest dictionary
        """
        print("🔥 Starting Mojo Manual Preprocessing Pipeline\n")
        
        # Discover files
        files = self._discover_files()
        print(f"Found {len(files)} documentation files to process\n")
        
        if not files:
            print("❌ No files found to process!")
            return {}
        
        # Process each file
        all_chunks = []
        processed_docs = []
        
        for file_path in tqdm(files, desc="Processing files"):
            try:
                # Process the file
                document = self.mdx_processor.process_file(file_path)
                
                # Add document ID
                document["document_id"] = generate_document_id(
                    file_path, self.source_dir
                )
                
                # Extract full metadata
                metadata = self.metadata_extractor.extract_full_metadata(
                    document, file_path
                )
                document["metadata"] = metadata
                
                # Chunk the document
                chunks = self.chunker.chunk_document(document)
                
                # Save outputs
                self._save_document_outputs(document, chunks)
                
                # Track for manifest
                all_chunks.extend(chunks)
                processed_docs.append({
                    "file_path": str(file_path.relative_to(self.source_dir)),
                    "document_id": document["document_id"],
                    "chunks_generated": len(chunks),
                    "content_hash": document["content_hash"],
                })
                
            except Exception as e:
                print(f"\n❌ Error processing {file_path}: {e}")
                continue
        
        # Generate and save manifest
        manifest = self._generate_manifest(processed_docs, all_chunks)
        self._save_manifest(manifest)
        
        # Print summary
        self._print_summary(manifest)
        
        return manifest

    def _discover_files(self) -> List[Path]:
        """Discover all documentation files to process."""
        patterns = self.config["source"]["file_patterns"]
        exclude = self.config["source"].get("exclude_patterns", [])
        
        return get_file_list(self.source_dir, patterns, exclude)

    def _save_document_outputs(self, document: Dict, chunks: List[DocumentChunk]) -> None:
        """Save processed document in multiple formats."""
        doc_id = document["document_id"]
        
        # 1. Save raw cleaned content
        raw_path = self.base_dir / self.config["output"]["raw_dir"] / f"{doc_id}.txt"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(document["clean_content"])
        
        # 2. Save metadata
        metadata_path = (
            self.base_dir / self.config["output"]["metadata_dir"] / f"{doc_id}.json"
        )
        save_json(document["metadata"], metadata_path)
        
        # 3. Save chunks as JSONL
        chunks_path = (
            self.base_dir / self.config["output"]["chunks_dir"] / f"{doc_id}.jsonl"
        )
        
        chunks_data = []
        for chunk in chunks:
            chunk_data = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "content": chunk.content,
                "position": chunk.position,
                "token_count": chunk.token_count,
                "has_code": chunk.has_code,
                "section_hierarchy": chunk.section_hierarchy,
                "metadata": self.metadata_extractor.enrich_chunk_metadata(
                    chunk, document["metadata"]
                ),
            }
            chunks_data.append(chunk_data)
        
        save_jsonl(chunks_data, chunks_path)

    def _generate_manifest(
        self, processed_docs: List[Dict], all_chunks: List[DocumentChunk]
    ) -> Dict:
        """Generate processing manifest with statistics."""
        total_tokens = sum(chunk.token_count for chunk in all_chunks)
        avg_tokens = total_tokens / len(all_chunks) if all_chunks else 0
        
        chunks_with_code = sum(1 for chunk in all_chunks if chunk.has_code)
        
        return {
            "processing_date": datetime.now().isoformat(),
            "source_directory": str(self.source_dir),
            "output_directory": str(self.base_dir),
            "total_documents": len(processed_docs),
            "total_chunks": len(all_chunks),
            "total_tokens": total_tokens,
            "average_tokens_per_chunk": round(avg_tokens, 2),
            "chunks_with_code": chunks_with_code,
            "configuration": {
                "chunk_size": self.config["chunking"]["chunk_size"],
                "chunk_overlap": self.config["chunking"]["chunk_overlap"],
                "preserve_code_blocks": self.config["chunking"]["preserve_code_blocks"],
            },
            "documents": processed_docs,
        }

    def _save_manifest(self, manifest: Dict) -> None:
        """Save processing manifest."""
        manifest_path = self.base_dir / self.config["output"]["manifest_file"]
        save_json(manifest, manifest_path)

    def _print_summary(self, manifest: Dict) -> None:
        """Print processing summary."""
        print("\n" + "=" * 60)
        print("📊 Processing Summary")
        print("=" * 60)
        print(f"Documents processed: {manifest['total_documents']}")
        print(f"Total chunks generated: {manifest['total_chunks']}")
        print(f"Total tokens: {manifest['total_tokens']:,}")
        print(f"Average tokens per chunk: {manifest['average_tokens_per_chunk']}")
        print(f"Chunks with code: {manifest['chunks_with_code']}")
        print(f"\nOutput directory: {manifest['output_directory']}")
        print("=" * 60)
        print("✅ Processing complete!\n")

    def validate_output(self) -> bool:
        """Validate processed output."""
        print("🔍 Validating processed output...\n")
        
        manifest_path = self.base_dir / self.config["output"]["manifest_file"]
        if not manifest_path.exists():
            print("❌ Manifest file not found!")
            return False
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check all documented files exist
        errors = []
        for doc in manifest["documents"]:
            doc_id = doc["document_id"]
            
            # Check raw file
            raw_path = self.base_dir / self.config["output"]["raw_dir"] / f"{doc_id}.txt"
            if not raw_path.exists():
                errors.append(f"Missing raw file: {raw_path}")
            
            # Check metadata file
            meta_path = (
                self.base_dir / self.config["output"]["metadata_dir"] / f"{doc_id}.json"
            )
            if not meta_path.exists():
                errors.append(f"Missing metadata file: {meta_path}")
            
            # Check chunks file
            chunks_path = (
                self.base_dir / self.config["output"]["chunks_dir"] / f"{doc_id}.jsonl"
            )
            if not chunks_path.exists():
                errors.append(f"Missing chunks file: {chunks_path}")
        
        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("✅ Validation passed!\n")
        return True

    def print_statistics(self) -> None:
        """Print detailed statistics about processed documents."""
        manifest_path = self.base_dir / self.config["output"]["manifest_file"]
        if not manifest_path.exists():
            print("❌ No manifest found. Run processing first.")
            return
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        print("\n" + "=" * 60)
        print("📈 Detailed Statistics")
        print("=" * 60)
        
        # Document statistics
        print(f"\nDocuments: {manifest['total_documents']}")
        print(f"Chunks: {manifest['total_chunks']}")
        print(f"Tokens: {manifest['total_tokens']:,}")
        
        # Chunk size distribution
        chunk_sizes = []
        for doc in manifest["documents"]:
            doc_id = doc["document_id"]
            chunks_path = (
                self.base_dir / self.config["output"]["chunks_dir"] / f"{doc_id}.jsonl"
            )
            
            with open(chunks_path) as f:
                for line in f:
                    chunk = json.loads(line)
                    chunk_sizes.append(chunk["token_count"])
        
        if chunk_sizes:
            print("\nChunk Size Distribution:")
            print(f"  Min: {min(chunk_sizes)} tokens")
            print(f"  Max: {max(chunk_sizes)} tokens")
            print(f"  Average: {sum(chunk_sizes) / len(chunk_sizes):.2f} tokens")
            print(f"  Median: {sorted(chunk_sizes)[len(chunk_sizes) // 2]} tokens")
        
        print("=" * 60 + "\n")


def main():
    """Main entry point for the preprocessing pipeline."""
    parser = argparse.ArgumentParser(
        description="Preprocessing pipeline for Mojo manual documentation"
    )
    parser.add_argument(
        "--config",
        default="preprocessing/config/processing_config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing output",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only print statistics",
    )
    
    args = parser.parse_args()
    
    try:
        pipeline = DocumentProcessingPipeline(args.config)
        
        if args.validate_only:
            success = pipeline.validate_output()
            sys.exit(0 if success else 1)
        
        if args.stats_only:
            pipeline.print_statistics()
            sys.exit(0)
        
        # Run full processing
        pipeline.process_all_documents()
        
        # Auto-validate
        pipeline.validate_output()
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
