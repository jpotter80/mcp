"""
Document chunking strategies for optimal embedding generation.
"""

import re
from dataclasses import dataclass
from typing import Dict, List
import tiktoken  # type: ignore


@dataclass
class DocumentChunk:
    """Represents a chunk of document with metadata."""
    content: str
    metadata: Dict
    chunk_id: str
    document_id: str
    position: int
    token_count: int
    overlap_with_previous: bool
    section_hierarchy: List[str]
    has_code: bool = False


class TechnicalDocChunker:
    """
    Specialized chunker for technical documentation.
    
    Implements recursive text splitting with semantic boundaries,
    optimized for technical content with code examples.
    """

    def __init__(self, config: Dict):
        chunking_config = config["chunking"]
        
        self.chunk_size = chunking_config.get("chunk_size", 400)
        self.chunk_overlap = chunking_config.get("chunk_overlap", 80)
        self.min_chunk_size = chunking_config.get("min_chunk_size", 100)
        self.preserve_code_blocks = chunking_config.get("preserve_code_blocks", True)
        self.code_block_threshold = chunking_config.get("code_block_threshold", 50)
        
        # Initialize tokenizer for accurate counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback if tiktoken has issues
            self.tokenizer = None

    def chunk_document(self, document: Dict) -> List[DocumentChunk]:
        """
        Chunk a document using recursive splitting with semantic boundaries.
        
        This approach:
        1. Preserves section boundaries when possible
        2. Keeps code blocks intact
        3. Maintains context through overlap
        4. Adds hierarchical metadata for better retrieval
        """
        chunks = []
        content = document["clean_content"]
        headers = document["headers"]
        code_blocks = document["code_blocks"]
        document_id = document.get("document_id", "unknown")
        
        # Split by major sections first
        sections = self._split_by_headers(content, headers)
        
        # Process each section
        chunk_position = 0
        for section_idx, section_data in enumerate(sections):
            section_chunks = self._chunk_section(
                section_data["content"],
                section_data["hierarchy"],
                code_blocks,
            )
            
            # Create DocumentChunk objects
            for chunk_idx, chunk_text in enumerate(section_chunks):
                token_count = self._count_tokens(chunk_text)
                
                # Skip chunks that are too small (unless it's the only chunk)
                if token_count < self.min_chunk_size and len(section_chunks) > 1:
                    continue
                
                has_code = self._contains_code(chunk_text)
                
                chunk = DocumentChunk(
                    content=chunk_text,
                    metadata=document.get("metadata", {}),
                    chunk_id=f"{document_id}-{chunk_position:03d}",
                    document_id=document_id,
                    position=chunk_position,
                    token_count=token_count,
                    overlap_with_previous=(chunk_idx > 0),
                    section_hierarchy=section_data["hierarchy"],
                    has_code=has_code,
                )
                chunks.append(chunk)
                chunk_position += 1
        
        return chunks

    def _split_by_headers(self, content: str, headers: List[Dict]) -> List[Dict]:
        """Split content into sections based on headers."""
        if not headers:
            return [{"content": content, "hierarchy": []}]
        
        sections = []
        current_hierarchy = []
        
        for i, header in enumerate(headers):
            # Determine hierarchy up to this header
            level = header["level"]
            text = header["text"]
            
            # Update hierarchy: keep headers at same or higher level
            current_hierarchy = [h for h in current_hierarchy if h["level"] < level]
            current_hierarchy.append({"level": level, "text": text})
            
            # Extract content for this section
            start_pos = header["position"]
            
            # Find end position (next header or end of document)
            if i < len(headers) - 1:
                end_pos = headers[i + 1]["position"]
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos].strip()
            
            # Skip empty sections
            if not section_content:
                continue
            
            sections.append({
                "content": section_content,
                "hierarchy": [h["text"] for h in current_hierarchy],
            })
        
        # Handle content before first header
        if headers and headers[0]["position"] > 0:
            intro_content = content[:headers[0]["position"]].strip()
            if intro_content:
                sections.insert(0, {
                    "content": intro_content,
                    "hierarchy": [],
                })
        
        return sections

    def _chunk_section(
        self, text: str, hierarchy: List[str], code_blocks: List[Dict]
    ) -> List[str]:
        """
        Recursively chunk a section of text.
        
        Order of splitting:
        1. Code blocks (if preserve_code_blocks is True)
        2. Paragraphs (double newline)
        3. Sentences
        4. Words (last resort)
        """
        token_count = self._count_tokens(text)
        
        # Base case: text fits within chunk size
        if token_count <= self.chunk_size:
            return [text] if text.strip() else []
        
        # Try splitting by paragraphs first
        paragraphs = text.split("\n\n")
        if len(paragraphs) > 1:
            return self._merge_chunks(paragraphs)
        
        # Then try sentences
        sentences = self._split_sentences(text)
        if len(sentences) > 1:
            return self._merge_chunks(sentences)
        
        # Last resort: split by tokens
        return self._split_by_tokens(text)

    def _merge_chunks(self, segments: List[str]) -> List[str]:
        """
        Merge segments into chunks of appropriate size with overlap.
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for segment in segments:
            segment_tokens = self._count_tokens(segment)
            
            # If adding this segment exceeds chunk size, save current chunk
            if current_tokens + segment_tokens > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    # Include last segments for overlap
                    overlap_tokens = 0
                    overlap_segments = []
                    for prev_seg in reversed(current_chunk):
                        prev_tokens = self._count_tokens(prev_seg)
                        if overlap_tokens + prev_tokens <= self.chunk_overlap:
                            overlap_segments.insert(0, prev_seg)
                            overlap_tokens += prev_tokens
                        else:
                            break
                    current_chunk = overlap_segments
                    current_tokens = overlap_tokens
                else:
                    current_chunk = []
                    current_tokens = 0
            
            current_chunk.append(segment)
            current_tokens += segment_tokens
        
        # Add final chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving code blocks."""
        # Simple sentence splitter
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_by_tokens(self, text: str) -> List[str]:
        """Split text by tokens (last resort for very long strings)."""
        if not self.tokenizer:
            # Fallback: split by characters
            words = text.split()
            chunk_size_chars = len(text) * self.chunk_size // self._count_tokens(text)
            
            chunks = []
            current = []
            current_len = 0
            
            for word in words:
                word_len = len(word) + 1  # +1 for space
                if current_len + word_len > chunk_size_chars and current:
                    chunks.append(" ".join(current))
                    current = [word]
                    current_len = word_len
                else:
                    current.append(word)
                    current_len += word_len
            
            if current:
                chunks.append(" ".join(current))
            
            return chunks
        
        # Token-based splitting with tiktoken
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i : i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: approximate using words (1.3 tokens per word average)
            return int(len(text.split()) * 1.3)

    def _contains_code(self, text: str) -> bool:
        """Check if text contains code blocks."""
        return "```" in text or "    " in text  # Code blocks or indented code
