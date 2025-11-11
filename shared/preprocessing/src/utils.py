"""
Utility functions for the preprocessing pipeline.

Helper functions shared across all document processors.
"""

import hashlib
import re


def calculate_content_hash(content: str) -> str:
    """Calculate MD5 hash of content for change detection.
    
    Args:
        content: Text content to hash
        
    Returns:
        Hex-encoded MD5 hash string
    """
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace while preserving paragraph breaks.
    
    - Reduces multiple spaces to single space
    - Preserves double newlines (paragraph breaks)
    - Removes trailing whitespace from lines
    - Strips leading/trailing whitespace
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)
    
    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    
    return text.strip()
