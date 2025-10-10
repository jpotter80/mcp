"""
Mojo Manual Preprocessing Package

This package provides tools for preprocessing MDX documentation files
to prepare them for vector embedding and MCP resource server exposure.
"""

from .pipeline import DocumentProcessingPipeline, init_directories
from .mdx_processor import MDXProcessor
from .chunker import TechnicalDocChunker, DocumentChunk
from .metadata_extractor import MetadataExtractor

__version__ = "0.1.0"

__all__ = [
    "DocumentProcessingPipeline",
    "init_directories",
    "MDXProcessor",
    "TechnicalDocChunker",
    "DocumentChunk",
    "MetadataExtractor",
]
