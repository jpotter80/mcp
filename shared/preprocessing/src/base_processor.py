"""
Base class for document processors.

Defines the interface that all format-specific processors must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class BaseDocumentProcessor(ABC):
    """Abstract base class for all document processors.
    
    Defines the contract that all processors must fulfill, enabling
    pluggable architecture for different file formats.
    """

    def __init__(self, config: Dict):
        """Initialize processor with configuration.
        
        Args:
            config: Configuration dictionary containing processing settings
        """
        self.config = config

    @abstractmethod
    def process_file(self, file_path: Path) -> Dict:
        """Process a single document file and extract content with metadata.
        
        This method must be implemented by all processor subclasses.
        
        Args:
            file_path: Path to the document file to process
            
        Returns:
            Dictionary containing:
                - file_path: str - path to the original file
                - metadata: Dict - extracted metadata (frontmatter, computed fields)
                - clean_content: str - processed content with formatting cleaned
                - original_content: str - unmodified content from file
                - headers: List[Dict] - extracted headers with hierarchy info
                - code_blocks: List[Dict] - extracted code blocks with metadata
                - content_hash: str - hash of original content for change detection
        """
        pass
