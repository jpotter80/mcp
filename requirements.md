# Project Requirements and Model Instructions

## Project Context

You are working on a comprehensive freelance data engineering workflow infrastructure project. This is a locally-hosted system designed to support diverse technical work through intelligent agent coordination and dynamic documentation access.

## Core Architecture Understanding

### System Components
- **Project Manager Agent**: Central orchestrator with PostgreSQL backend
- **Documentation MCP Servers**: Auto-generated from tool documentation using DuckLake storage
- **Multi-tier Agent System**: Specialized, domain specialist, and general purpose agents
- **Workflow Infrastructure**: Templates and patterns for common project types

### Technical Stack
- **PostgreSQL**: Primary database for metadata and coordination
- **DuckDB + DuckLake**: Documentation corpus and high-performance querying
- **Scrapy**: Documentation acquisition pipeline
- **Python MCP SDK**: Server development framework
- **Command-line Integration**: CLI-first approach with Python API fallback

## Development Environment
- **Platform**: Kubuntu 24.04 (local development only)
- **Tools**: VSCode, Neovim, command-line focused workflow
- **Philosophy**: Accuracy over latency, open-source tools only

## Key Tools in Stack
- DuckDB (database and analytics)
- Mojo programming language (systems programming)
- UV and Pixi (Python package managers)
- Observable Framework (data visualization)
- Marimo notebooks (interactive computing)

**Note**: Most tools except Python are new/niche with limited training data representation.

## Work Domain Coverage
OCR/document processing, synthetic data generation, ETL pipelines, GPU programming, automation, MCP/agent development, data visualization, reporting, research notebooks, machine learning, web scraping.

## Design Principles

### Systems Mindset Requirements
- **Dynamic**: Must adapt to new tools without architectural changes
- **Resilient**: Graceful failure handling and data integrity
- **Efficient**: Horizontal scaling with minimal resource overhead

### Interface Preferences
- Command-line first for all tool interactions
- PostgreSQL via psql CLI and Python APIs
- DuckDB via CLI dot commands and Python integration
- Safe CLI execution with proper error handling

### Documentation Strategy
- Markdown-based documentation primary target
- Scrapy for systematic acquisition
- Version tracking and update management
- Hybrid storage: PostgreSQL metadata + DuckLake corpus

## Agent Architecture Patterns

### Specialized Task Agents
Focus on single, well-defined capabilities (YouTube processing, OCR, web scraping, GPU programming).

### Domain Specialist Agents  
Cover broad technical domains (data engineering, ML/AI, visualization, infrastructure).

### General Purpose Agents
Provide foundational capabilities shared across domains (Python scripting, SQL, research).

### Coordination Requirements
- Clear task delegation protocols
- Capability overlap management
- Multi-agent handoff procedures
- Standardized result formats

## Implementation Approach

### Phase-based Development
1. **Core Infrastructure**: PostgreSQL schema, DuckLake setup, basic MCP servers
2. **Agent Development**: Start with YouTube agent, add Python scripting, build pipeline
3. **Workflow Integration**: Cross-agent coordination, templates, optimization

### Proof of Concept Strategy
Begin with DuckDB documentation as MCP server test case, then scale framework.

## Critical Success Factors

### Documentation Quality
High-quality, up-to-date documentation access is paramount given niche tool selection.

### Workflow Organization
Project templates and cross-project patterns must capture institutional knowledge.

### Agent Interoperability
Standardized interfaces and coordination protocols across all agent types.

### Infrastructure Resilience
System must handle tool updates, documentation changes, and coordination failures gracefully.

## Response Guidelines

### Planning Focus
Prioritize system architecture, component interaction, and workflow integration over individual feature implementation.

### Documentation Awareness
Acknowledge when tool-specific knowledge may be limited and suggest documentation gathering needs.

### Practical Considerations
Balance ideal architecture with practical implementation constraints for solo freelance developer.

### Code Generation Policy
Generate planning documents, specifications, and pseudo-code only. Actual implementation code should be minimal and focused on architectural examples.

## Current Project Status

**Phase**: Planning and architecture design
**Next Steps**: Documentation gathering and proof-of-concept development  
**Critical Needs**: MCP SDK documentation, DuckLake specifications, tool integration patterns

The system is designed to be a comprehensive solution that grows with the developer's work and serves as both infrastructure and institutional knowledge repository.
