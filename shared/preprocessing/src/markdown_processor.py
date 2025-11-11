"""
Markdown document processor for cleaning and extracting content.

Handles standard Markdown files with optional YAML frontmatter.
Simpler than MDX processor as it doesn't need to handle JSX components.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import frontmatter  # type: ignore

from .base_processor import BaseDocumentProcessor
from .utils import calculate_content_hash, normalize_whitespace


class MarkdownProcessor(BaseDocumentProcessor):
    """Processes Markdown files and extracts content with metadata."""

    def __init__(self, config: Dict):
        """Initialize Markdown processor with configuration.
        
        Args:
            config: Configuration dictionary with processing settings
        """
        super().__init__(config)
        self.processing_config = config.get("processing", {})
        
        # Compile regex patterns for efficiency
        self.code_block_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
        self.header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        self.html_tag_pattern = re.compile(r"<[^>]+>", re.DOTALL)
        self.link_pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        self.image_pattern = re.compile(r"!\[([^\]]*)\]\(([^\)]+)\)")

    def process_file(self, file_path: Path) -> Dict:
        """
        Process a single Markdown file and extract all relevant information.
        
        Args:
            file_path: Path to the Markdown file to process
            
        Returns:
            Dictionary containing processed content and metadata
        """
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Extract metadata
        metadata = self._extract_metadata(post, file_path)
        
        # Clean content
        clean_content = self._clean_content(post.content)
        
        # Extract structure
        headers = self._extract_headers(post.content)
        code_blocks = self._extract_code_blocks(post.content)
        
        return {
            "file_path": str(file_path),
            "metadata": metadata,
            "clean_content": clean_content,
            "original_content": post.content,
            "headers": headers,
            "code_blocks": code_blocks,
            "content_hash": calculate_content_hash(post.content),
        }

    def _extract_metadata(self, post: frontmatter.Post, file_path: Path) -> Dict:
        """Extract frontmatter metadata from document.
        
        Args:
            post: Loaded frontmatter post object
            file_path: Path to the source file
            
        Returns:
            Dictionary of metadata fields
        """
        metadata = dict(post.metadata) if post.metadata else {}
        
        # Add computed metadata
        metadata["file_name"] = file_path.name
        metadata["file_stem"] = file_path.stem
        
        return metadata

    def _clean_content(self, content: str) -> str:
        """Remove HTML tags and normalize content while preserving structure.
        
        Args:
            content: Raw Markdown content
            
        Returns:
            Cleaned content
        """
        cleaned = content
        
        # Remove HTML tags if present
        if self.processing_config.get("remove_html_tags", True):
            cleaned = self.html_tag_pattern.sub("", cleaned)
        
        # Normalize whitespace
        if self.processing_config.get("normalize_whitespace", True):
            cleaned = normalize_whitespace(cleaned)
        
        return cleaned

    def _extract_headers(self, content: str) -> List[Dict]:
        """Extract document structure from headers.
        
        Args:
            content: Markdown content
            
        Returns:
            List of header dictionaries with level, text, anchor, position
        """
        headers = []
        for match in self.header_pattern.finditer(content):
            level = len(match.group(1))
            text = match.group(2).strip()
            
            # Generate anchor ID (lowercase, replace spaces with hyphens)
            anchor = re.sub(r"[^\w\s-]", "", text.lower())
            anchor = re.sub(r"[-\s]+", "-", anchor)
            
            headers.append({
                "level": level,
                "text": text,
                "anchor": anchor,
                "position": match.start(),
            })
        return headers

    def _extract_code_blocks(self, content: str) -> List[Dict]:
        """Extract code blocks with their language and content.
        
        Args:
            content: Markdown content
            
        Returns:
            List of code block dictionaries
        """
        code_blocks = []
        for match in self.code_block_pattern.finditer(content):
            language = match.group(1) or "text"
            code = match.group(2).strip()
            
            code_blocks.append({
                "language": language,
                "code": code,
                "position": match.start(),
                "length": len(code),
            })
        return code_blocks

    def get_section_hierarchy(self, headers: List[Dict], position: int) -> List[str]:
        """
        Get the section hierarchy for a given position in the document.
        
        Args:
            headers: List of header dictionaries
            position: Character position in document
            
        Returns:
            List of header texts from top level to current level
        """
        hierarchy = []
        current_levels = {}
        
        for header in headers:
            if header["position"] > position:
                break
            
            level = header["level"]
            current_levels[level] = header["text"]
            
            # Clear deeper levels
            for lvl in list(current_levels.keys()):
                if lvl > level:
                    del current_levels[lvl]
        
        # Build hierarchy from top level down
        for level in sorted(current_levels.keys()):
            hierarchy.append(current_levels[level])
        
        return hierarchy

    def extract_surrounding_context(
        self, content: str, start_pos: int, end_pos: int, context_chars: int = 200
    ) -> Tuple[str, str]:
        """Extract text before and after a given position for context.
        
        Args:
            content: Document content
            start_pos: Start position
            end_pos: End position
            context_chars: Number of characters to extract for context
            
        Returns:
            Tuple of (before_text, after_text)
        """
        before_start = max(0, start_pos - context_chars)
        before_text = content[before_start:start_pos].strip()
        
        after_end = min(len(content), end_pos + context_chars)
        after_text = content[end_pos:after_end].strip()
        
        return before_text, after_text
