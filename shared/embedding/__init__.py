"""
Shared embedding module for generating and managing embeddings.

This module provides scripts for the embedding pipeline:
- generate_embeddings.py: Generate embeddings using MAX server
- consolidate_data.py: Consolidate chunks and embeddings into parquet
- load_to_ducklake.py: Load data into DuckLake catalog
- create_indexes.py: Create HNSW and FTS indexes in DuckDB
"""

__all__ = [
    "generate_embeddings",
    "consolidate_data",
    "load_to_ducklake",
    "create_indexes",
]
