"""
Metadata extraction module for documentation files.
"""

from pathlib import Path
from typing import Dict, List, TYPE_CHECKING
from datetime import datetime

from .utils import generate_document_id, generate_url

if TYPE_CHECKING:
    from .chunker import DocumentChunk


class MetadataExtractor:
    """Extract and enrich metadata from processed documents."""

    def __init__(self, config: Dict):
        self.config = config
        self.metadata_config = config["metadata"]
        self.source_dir = Path(config["source"]["directory"])
        self.url_base = config["processing"]["url_base"]

    def extract_full_metadata(self, document: Dict, file_path: Path) -> Dict:
        """
        Extract complete metadata for a document including computed fields.
        
        Args:
            document: Processed document dictionary
            file_path: Path to the source file
            
        Returns:
            Dictionary with complete metadata
        """
        metadata = document.get("metadata", {}).copy()
        
        # Add file information
        metadata["file_path"] = str(file_path.relative_to(self.source_dir))
        metadata["file_name"] = file_path.name
        metadata["file_size"] = file_path.stat().st_size
        
        # Generate document ID
        if self.metadata_config.get("generate_document_id", True):
            metadata["document_id"] = generate_document_id(file_path, self.source_dir)
        
        # Generate URL
        if self.config["processing"].get("extract_urls", True):
            metadata["url"] = generate_url(file_path, self.source_dir, self.url_base)
        
        # Calculate content hash
        if self.metadata_config.get("calculate_content_hash", True):
            metadata["content_hash"] = document["content_hash"]
        
        # Extract statistics
        if self.metadata_config.get("include_statistics", True):
            metadata["statistics"] = self._calculate_statistics(document)
        
        # Add processing timestamp
        metadata["processed_at"] = datetime.now().isoformat()
        
        # Extract section hierarchy info
        if self.metadata_config.get("generate_section_hierarchy", True):
            metadata["sections"] = self._extract_section_info(document["headers"])
        
        return metadata

    def _calculate_statistics(self, document: Dict) -> Dict:
        """Calculate statistics about the document."""
        content = document["clean_content"]
        
        return {
            "char_count": len(content),
            "word_count": len(content.split()),
            "line_count": content.count("\n") + 1,
            "paragraph_count": len([p for p in content.split("\n\n") if p.strip()]),
            "header_count": len(document.get("headers", [])),
            "code_block_count": len(document.get("code_blocks", [])),
            "code_lines": sum(
                cb["code"].count("\n") + 1 for cb in document.get("code_blocks", [])
            ),
        }

    def _extract_section_info(self, headers: List[Dict]) -> List[Dict]:
        """Extract hierarchical section information."""
        sections = []
        for header in headers:
            sections.append({
                "level": header["level"],
                "title": header["text"],
                "anchor": header["anchor"],
            })
        return sections

    def enrich_chunk_metadata(
        self, chunk: "DocumentChunk", document_metadata: Dict
    ) -> Dict:
        """
        Enrich chunk with additional metadata for storage.
        
        Args:
            chunk: DocumentChunk object
            document_metadata: Full document metadata
            
        Returns:
            Dictionary with complete chunk metadata
        """
        chunk_meta = {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "position": chunk.position,
            "token_count": chunk.token_count,
            "has_code": chunk.has_code,
            "overlap_with_previous": chunk.overlap_with_previous,
            "section_hierarchy": chunk.section_hierarchy,
            
            # From document metadata
            "file_path": document_metadata.get("file_path"),
            "url": document_metadata.get("url"),
            "title": document_metadata.get("title", "Untitled"),
            "category": document_metadata.get("category"),
            "tags": document_metadata.get("tags", []),
            
            # Add section-specific URL if hierarchy exists
            "section_url": self._generate_section_url(
                document_metadata.get("url", ""),
                chunk.section_hierarchy
            ),
        }
        
        return chunk_meta

    def _generate_section_url(self, base_url: str, hierarchy: List[str]) -> str:
        """Generate URL with anchor for specific section."""
        if not hierarchy or not base_url:
            return base_url
        
        # Use the most specific (last) section for anchor
        section_text = hierarchy[-1]
        anchor = section_text.lower().replace(" ", "-")
        anchor = "".join(c for c in anchor if c.isalnum() or c == "-")
        
        return f"{base_url}#{anchor}"
