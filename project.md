# Freelance Data Engineering Workflow Infrastructure Project

## Project Overview

This project creates a comprehensive, locally-hosted workflow infrastructure for freelance data engineering work, centered around intelligent agent coordination and dynamic documentation access. The system is designed with a systems mindset to be dynamic, resilient, and efficient across diverse project types.

## Core Architecture

### Central Components

**Project Manager Agent**
- Central orchestrator for all workflow activities
- PostgreSQL database for project context, task history, and agent coordination
- Workflow template library for common project patterns
- Agent capability registry and intelligent task routing
- Project lifecycle management (planning → execution → documentation → archiving)

**Documentation MCP Server Infrastructure**
- Generic framework transforming any markdown-based documentation into MCP servers
- Hybrid storage strategy: PostgreSQL for metadata + DuckLake for high-performance documentation corpus
- Scrapy-based acquisition pipeline for systematic documentation harvesting
- Standardized MCP interfaces across all generated servers

**Multi-Agent Architecture**
Three-tier agent system supporting varied work requirements:

*Specialized Task Agents:*
- YouTube Agent: URL → transcription/summarization/metadata
- OCR/Document Processing Agent: PDF/image → structured data
- Web Scraping Agent: Scrapy integration and data extraction
- GPU Programming Agent: CUDA/OpenCL optimization

*Domain Specialist Agents:*
- Data Engineering Agent: ETL, DuckDB CLI + Python, data quality
- ML/AI Agent: Model training, evaluation, deployment pipelines  
- Visualization Agent: Observable Framework, reporting dashboards
- Infrastructure Agent: MCP development, automation scripting

*General Purpose Agents:*
- Python Scripting Agent: Cross-domain Python capabilities
- SQL Agent: PostgreSQL, DuckDB, query optimization
- Research Agent: Literature review, technical documentation synthesis

## Technical Stack

### Core Dependencies (Minimized)
- **PostgreSQL**: Metadata, project management, agent coordination
- **DuckDB + DuckLake**: Documentation storage, workflow infrastructure
- **Scrapy**: Documentation acquisition and processing
- **Python MCP SDK**: Server development and agent integration
- **Command-line Integration Layer**: CLI-first tool interaction

### Development Environment
- **Platform**: Kubuntu 24.04 (local development)
- **Editors**: VSCode (coding), Neovim (text editing)
- **Interface Philosophy**: Command-line first, Python API for complex operations
- **Data Flow**: Accuracy prioritized over latency

## Work Domain Coverage

The infrastructure supports diverse freelance activities:
- OCR and document processing
- Synthetic data generation
- ETL pipeline development
- GPU programming and optimization
- Automation and workflow orchestration
- MCP and agent development
- Data visualization and reporting
- Research notebooks and analysis
- Machine learning model development
- Web scraping and data acquisition

## Storage Architecture

### DuckLake Integration
- **PostgreSQL Layer**: Metadata storage for documentation versioning, cross-references, agent access patterns
- **Object Storage Layer**: Processed documentation chunks, embeddings, cached agent results
- **DuckDB Integration**: High-performance querying across documentation corpus
- **Workflow Infrastructure**: Project templates, patterns, and specifications stored in same format

### Documentation Organization
- **Source Types**: GitHub repos, official docs, API specifications, curated community resources
- **Processing Pipeline**: Scrapy → Parser → Processor → DuckLake Storage → MCP Server
- **Update Strategy**: Scheduled batch updates (non-time-sensitive)
- **Version Management**: Tool version tracking, deprecation handling, conflict resolution

## Project Workflow Templates

### Standard Project Types
- **ETL Pipelines**: Source → Transform → Load patterns with data quality validation
- **ML Research**: Data → Model → Evaluation → Deployment lifecycle
- **Document Processing**: Ingestion → OCR → Structure → Analysis workflows  
- **Web Scraping**: Target → Extraction → Cleaning → Storage procedures
- **Automation**: Trigger → Action → Monitoring → Reporting cycles

### Cross-Project Patterns
- Data quality validation procedures
- Synthetic data generation templates
- Visualization and reporting standards
- Testing and validation frameworks
- Deployment and monitoring specifications

## Interface Preferences

### Tool Integration Patterns
- **DuckDB**: CLI with dot commands primary, Python API for complex operations
- **PostgreSQL**: psql CLI for administration, Python for agent interactions  
- **General Philosophy**: Command-line first with API fallback
- **Error Handling**: Safe CLI execution, output parsing, timeout management

### Agent Coordination
- **Task Delegation**: Project Manager routes tasks based on agent capabilities
- **Capability Overlap**: Clear protocols for agents with shared abilities
- **Handoff Procedures**: Multi-agent task coordination patterns
- **Result Aggregation**: Standardized output formats for agent interoperability

## Implementation Phases

### Phase 1: Core Infrastructure
1. PostgreSQL schema design for project management and agent coordination
2. DuckLake setup and documentation storage experimentation  
3. Basic MCP server template with proof-of-concept documentation
4. Project Manager Agent basic delegation logic

### Phase 2: Agent Development
1. YouTube Agent (isolated use case for testing patterns)
2. Python Scripting Agent (foundational cross-domain capability)
3. Documentation acquisition pipeline (Scrapy framework)
4. MCP server generation automation

### Phase 3: Workflow Integration
1. Cross-agent coordination refinement
2. Project template library development
3. Workflow infrastructure documentation system
4. Performance optimization and resilience testing

## Key Design Principles

### Systems Mindset
- **Dynamic**: Adapts to new tools and workflows without architectural changes
- **Resilient**: Graceful failure handling, data integrity, reliable service
- **Efficient**: Horizontal scaling across project types, minimal resource overhead

### Open Source Focus
- All tools and frameworks are open source
- Documentation primarily markdown-based
- Community contribution and reuse potential
- Standardized interfaces for broader adoption

## Current Status

- **Planning Phase**: Architecture design and component specification
- **Next Steps**: Documentation gathering for MCP, DuckLake, and tool-specific integration patterns
- **Critical Dependencies**: MCP SDK documentation, DuckLake technical specifications
- **Proof of Concept Target**: DuckDB documentation MCP server with basic agent interaction

## Success Metrics

### Immediate Goals
- Seamless documentation access across all tools in the stack
- Efficient task delegation and agent coordination
- Reliable project lifecycle management

### Long-term Vision
- Self-documenting infrastructure that evolves with tool ecosystem
- Reusable framework for other freelance developers
- Comprehensive knowledge base spanning entire technical domain
