# Shared Build Infrastructure

This directory contains reusable, development-time infrastructure used to build MCP servers.
**Note**: These are NOT included in distributed servers.

## Contents

- `preprocessing/` — Document processing pipeline (chunking, metadata extraction)
- `embedding/` — Embedding generation and data consolidation
- `templates/` — Code templates for new MCP servers
- `build/` — Generated artifacts (ephemeral, not committed)

## Usage

This infrastructure is used during development to process documentation and build indexed databases.
Processed databases are then committed to individual server directories in `/servers/`.

## Not Distributed

When distributing individual MCP servers (e.g., as GitHub repositories), 
only the `/servers/{mcp}/runtime/` directory is included, along with minimal configuration.
The shared infrastructure stays in the development repository.
