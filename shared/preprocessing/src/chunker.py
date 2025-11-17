"""
Document chunking strategies for optimal embedding generation, specifically
designed for the sentence-transformers/all-mpnet-base-v2 model.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


@dataclass
class DocumentChunk:
    """Represents a chunk of document with metadata."""

    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    document_id: str
    position: int
    token_count: int
    overlap_with_previous: bool
    section_hierarchy: List[str]
    has_code: bool = False


class LangchainMarkdownChunker:
    """
    A document chunker that uses langchain's RecursiveCharacterTextSplitter,
    optimized for a specific sentence-transformer model and Markdown content.

    This chunker uses a single, powerful text splitter that is configured
    with both the sentence-transformer's tokenizer and a list of
    Markdown-specific separators. This allows it to respect semantic
    boundaries (like headers and code blocks) while ensuring that each
    chunk strictly adheres to the model's maximum input length.
    """

    def __init__(self, config: Dict[str, Any]):
        chunking_config = config["chunking"]
        self.model_name = chunking_config.get(
            "embedding_model_name", "sentence-transformers/all-mpnet-base-v2"
        )
        # The model's max sequence length is 384. We use a smaller chunk size
        # to leave a buffer for model-specific tokens.
        self.chunk_size = chunking_config.get("chunk_size", 350)
        self.chunk_overlap = chunking_config.get("chunk_overlap", 50)

        # Initialize the tokenizer from the sentence-transformer model
        # This is critical for accurately measuring chunk length.
        tokenizer = SentenceTransformer(self.model_name).tokenizer

        def length_function(text: str) -> int:
            """Calculate the number of tokens in a string."""
            return len(tokenizer.encode(text))

        self.length_function = length_function

        # Define a list of separators that are common in Markdown.
        # The splitter will try these in order, from headers down to characters.
        markdown_separators = [
            "\n# ",
            "\n## ",
            "\n### ",
            "\n#### ",
            "\n##### ",
            "\n###### ",
            "```\n",
            "\n\n",
            "\n",
            " ",
            "",
        ]

        # Set up the recursive text splitter with the model's tokenizer
        # and Markdown-aware separators.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=length_function,
            separators=markdown_separators,
        )

    def chunk_document(self, document: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Chunk a document using a single, tokenizer-aware recursive splitter.
        """
        content = document["clean_content"]
        document_id = document.get("document_id", "unknown")
        metadata = document.get("metadata", {})

        # Use the splitter to create documents, keeping metadata
        docs = self.text_splitter.create_documents([content], metadatas=[metadata])

        chunks = []
        for i, split_doc in enumerate(docs):
            # The splitter keeps the original metadata, which we can enrich
            chunk_metadata = split_doc.metadata

            # For now, we'll determine hierarchy based on the content
            # of the chunk itself. A more sophisticated approach could
            # be added later if needed.
            hierarchy = self._extract_hierarchy_from_chunk(split_doc.page_content)

            token_count = self.length_function(split_doc.page_content)

            chunk = DocumentChunk(
                content=split_doc.page_content,
                metadata=chunk_metadata,
                chunk_id=f"{document_id}-{i:03d}",
                document_id=document_id,
                position=i,
                token_count=token_count,
                overlap_with_previous=(i > 0 and self.chunk_overlap > 0),
                section_hierarchy=hierarchy,
                has_code="```" in split_doc.page_content,
            )
            chunks.append(chunk)

        return chunks

    def _extract_hierarchy_from_chunk(self, text: str) -> List[str]:
        """
        A simple method to extract the most prominent header from a chunk.
        """
        headers = re.findall(r"^(#{1,6})\s+(.*)", text, re.MULTILINE)
        if headers:
            # Return the text of the last header found in the chunk
            return [headers[-1][1].strip()]
        return []
