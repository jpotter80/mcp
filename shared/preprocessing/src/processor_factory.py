"""
Factory for creating document processors based on file format.

Implements the factory pattern to provide pluggable processor selection
based on file format (mdx, md, markdown, etc.).
"""

from typing import Dict

from .base_processor import BaseDocumentProcessor
from .markdown_processor import MarkdownProcessor
from .mdx_processor import MDXProcessor


class ProcessorFactory:
    """Factory for instantiating the appropriate document processor.
    
    Uses a registry of format -> processor class mappings to provide
    a pluggable architecture. New formats can be added by creating a
    processor class and registering it in PROCESSORS dict.
    """

    PROCESSORS: Dict[str, type] = {}

    @classmethod
    def register_processor(cls, format_type: str, processor_class: type) -> None:
        """Register a processor class for a given format.
        
        Args:
            format_type: File format identifier (e.g., 'mdx', 'md')
            processor_class: Class inheriting from BaseDocumentProcessor
            
        Raises:
            ValueError: If processor_class doesn't inherit from BaseDocumentProcessor
        """
        if not issubclass(processor_class, BaseDocumentProcessor):
            raise ValueError(
                f"Processor class {processor_class.__name__} must inherit "
                f"from BaseDocumentProcessor"
            )
        cls.PROCESSORS[format_type.lower()] = processor_class

    @classmethod
    def get_processor(cls, config: Dict, format_type: str) -> BaseDocumentProcessor:
        """Get an instance of the appropriate processor for given format.
        
        Args:
            config: Configuration dictionary for processor initialization
            format_type: File format ('mdx', 'md', 'markdown', etc.)
            
        Returns:
            Instantiated processor matching the format
            
        Raises:
            ValueError: If format_type is not supported/registered
        """
        format_key = format_type.lower()
        processor_class = cls.PROCESSORS.get(format_key)
        
        if processor_class is None:
            supported = list(cls.PROCESSORS.keys())
            raise ValueError(
                f"Unsupported format: {format_type}. "
                f"Supported formats: {supported}"
            )
        
        return processor_class(config)

    @classmethod
    def get_supported_formats(cls) -> list:
        """Get list of registered (supported) formats.
        
        Returns:
            List of format strings for which processors are registered
        """
        return list(cls.PROCESSORS.keys())


# Register processors
ProcessorFactory.register_processor("mdx", MDXProcessor)
ProcessorFactory.register_processor("md", MarkdownProcessor)
ProcessorFactory.register_processor("markdown", MarkdownProcessor)
