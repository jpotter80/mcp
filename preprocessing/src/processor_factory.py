"""
Re-export ProcessorFactory from shared preprocessing module.

This allows local imports to use the same factory pattern.
"""

from shared.preprocessing.src.processor_factory import ProcessorFactory  # noqa: F401
from shared.preprocessing.src.base_processor import BaseDocumentProcessor  # noqa: F401

__all__ = ["ProcessorFactory", "BaseDocumentProcessor"]
