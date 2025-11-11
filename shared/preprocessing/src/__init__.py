"""
Shared preprocessing module for document processing.

Provides pluggable, format-agnostic document processing architecture.
"""

from .base_processor import BaseDocumentProcessor
from .markdown_processor import MarkdownProcessor
from .mdx_processor import MDXProcessor
from .processor_factory import ProcessorFactory

# Register processors
ProcessorFactory.register_processor("mdx", MDXProcessor)
ProcessorFactory.register_processor("md", MarkdownProcessor)
ProcessorFactory.register_processor("markdown", MarkdownProcessor)

__all__ = [
    "BaseDocumentProcessor",
    "MDXProcessor",
    "MarkdownProcessor",
    "ProcessorFactory",
]
