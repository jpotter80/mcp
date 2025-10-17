# Agent Implementation Examples

## Examples from Modular using their MAX model server

## MAX-MCP-AGENT

### Build an Agent That Uses MCP Tools

AI agent that uses Model Context Protocol (MCP) to interact with external tools

README

This recipe demonstrates how to create AI agents that leverage Model Context Protocol (MCP) servers using MAX. You'll learn how to build an agent that discovers and uses MCP tools dynamically, enabling your AI models to interact with external systems through a standardized protocol.

### What You'll Build
- AI agent that can discover and use MCP tools at runtime
- Simple MCP server with FastMCP
- FastAPI service that bridges a MAX model with an MCP server
- Web UI for interacting with your agent, using Alpine.js and Pico CSS

### Requirements
- Python 3.12 or higher
- MAX 25.3.0 or higher
- FastMCP 2.3.4 or higher

### Quick Start
For this recipe, you will need:

- A valid Hugging Face token for accessing Llama 3
- Access to the meta-llama/Llama-3.2-1B-Instruct model

1. Install Dependencies

```shell
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc

# Clone the recipe
git clone https://github.com/modularml/max-recipes.git
cd max-recipes/max-mcp-agent
```

2. Configure Environment

Create a .env file with your configuration:

```shell
cp .env.sample .env
printf "\nHUGGING_FACE_HUB_TOKEN=your_token_here" >> .env
```

Optional: Configure Model Weights

The .env.sample file includes an optional MODEL_WEIGHTS configuration for quantized CPU weights. If you don't have a GPU available or want to use CPU-only inference, uncomment this line in your .env file:

```shell
MODEL_WEIGHTS="bartowski/Llama-3.2-1B-Instruct-GGUF/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
```

For GPU requirements and compatibility information, see the MAX GPU Requirements documentation.

3. Start the Services

The easiest way to run all services is using the Invoke task runner:

```shell
# Start all services (MAX server, demo MCP server, and Agent API)
uv run invoke app
```

Troubleshooting uv Build Errors

If the launch fails with an error ending with help: sentencepiece (v0.2.0) was included because..., it is because the project's dependency chain requires pkg-config and cmake.

To fix this on an Ubuntu Linux machine, run:

```shell
sudo apt update && sudo apt install -y pkg-config cmake build-essential
```

To fix this on a macOS machine, run:

```shell
xcode-select --install  # For Xcode Command Line Tools
brew install pkg-config cmake  # Using Homebrew - https://brew.sh/
```

Run Services Individually
You can also launch the individual services by running the following commands:

```shell
uv run invoke max  # Terminal 1: Start MAX model server
uv run invoke mcp  # Terminal 2: Start the demo MCP server  
uv run invoke api  # Terminal 3: Start the agent API
```

4. Test the Agent

The agent provides both a web UI and REST API for interaction:

Using the Web UI

- Open your browser to http://localhost:8080
- Enter a natural language query (e.g., "How many R's are in strawberry?")
- Click "Send" to see the results

Using the REST API

```shell
# Query the agent with a counting task
curl -X POST http://localhost:8000/api/count \
    -H "Content-Type: application/json" \
    -d '{"query": "Count the letter L in Hello World"}'
```

Example response:

```json
{
  "char_found": "l",
  "in_string": "Hello World",
  "num_times": 3
}
```

### Understanding the Architecture
System Overview

Web Client

Agent API

MAX Serve

MCP Server

Core Components

1. Agent API (max_mcp_agent/): FastAPI service that orchestrates the interaction between the MAX model and MCP server

- Serves a web UI at / for browser-based interaction
- Exposes REST API at /api/count for programmatic access
- Handles CORS for cross-origin requests

2. Demo MCP Server (demo_mcp_server/): A simple example MCP server that provides a character counting tool - this is intentionally separate from the agent to demonstrate clean architecture

3. Web Interface (max_mcp_agent/static/): Simple, responsive UI built with:

- Alpine.js for reactive state management
- Pico CSS for minimal, elegant styling
- Vanilla JavaScript for API communication
4. MCP Client Integration: Uses FastMCP to discover and call tools from MCP servers

5. OpenAI-Compatible Interface: Leverages MAX's OpenAI-compatible API for seamless integration with the OpenAI Python client

### Technical Deep Dive
Agent Workflow

The agent follows a structured workflow for processing queries:
```python
# 1. Initialize clients
openai_client = OpenAI(base_url=MAX_SERVE_URL, api_key="EMPTY")
mcp_client = MCPClient(MCP_URL)

# 2. Create session with user query
session = await _init_session(query, openai_client, mcp_client)

# 3. Discover available MCP tools
session = await _discover_tools(session)

# 4. Send message to LLM with tools
session = await _send_message(session)

# 5. Execute tool calls if needed
session = await _call_tool(session)
```

MCP Tool Discovery

The agent dynamically discovers tools from the MCP server and formats them for use with the OpenAI Python client:
```python
async def _discover_tools(session: ChatSession) -> ChatSession:
    mcp_tools = await session.mcp_client.list_tools()
    tools = []
    
    for tool in mcp_tools:
        formatted_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        tools.append(formatted_tool)
    
    session.tools = tools
    return session
```

OpenAI API Limitation: Tool Formatting

⚠️ Important: While MAX is fully compatible with the OpenAI Chat Completions API, there's a crucial limitation to understand. Tools exposed by an MCP server that are discovered by an MCP client cannot be passed directly to the OpenAI Python client - they require specific formatting.

The code block above shows the essential transformation that bridges MCP tools to the OpenAI format:

1. MCP Tool Discovery: await session.mcp_client.list_tools() retrieves raw MCP tool definitions

2. Format Conversion: Each MCP tool is reformatted into the OpenAI function calling format with:
- "type": "function" - Required by OpenAI's function calling API
- "function" object containing name, description, and parameters

3. Validation: The code ensures all required fields (name, description, parameters) are present before formatting

This formatting step is essential for making MCP tools compatible with MAX's OpenAI-compatible interface. Without this transformation, the tools would not be recognized by the OpenAI Python client used here to connect with MAX.

### Extending the Agent
The following are a couple ways you can build upon this recipe for your own use cases.

Implementing Multi-Turn Conversations

The current implementation in agent.py provides a clean foundation that demonstrates a single-tool workflow:

1. Receives a user query
2. Discovers available tools
3. Sends the query to the LLM with tools
4. Executes ONE tool call if requested
5. Returns the result

This architecture is intentionally simple to showcase the core MCP integration. You can enhance it to support:

- Multiple sequential tool calls: Enable the agent to use multiple tools in sequence to solve complex problems
- Conversation loops: Allow back-and-forth interactions where tool results inform follow-up questions
- Complex multi-step workflows: Build agents that can plan and execute sophisticated task sequences
- Stateful conversations: Maintain context across multiple user interactions

### Adding New MCP Tools

The demo_mcp_server module provides a simple example of an MCP server with a single tool:

```python
@mcp.tool()
def count_characters(
    character: str,
    string: str,
) -> ToolResponse:
    """Counts the occurrences of a character within a string"""
    count = string.lower().count(character.lower())
    return ToolResponse(char_found=character, in_string=string, num_times=count)
```

This demonstrates the simplicity of creating MCP tools - just a Python function with a decorator. The separation between the demo_mcp_server and max_mcp_agent modules is intentional, showing how:

1. MCP servers can be developed independently from MCP clients
2. Agents can discover tools and use dynamically at runtime

You can extend this by:

1. Adding tools to the demo server: Simply add more @mcp.tool() decorated functions

2. Creating new MCP servers: Build separate MCP servers for different domains (database operations, file management, API integrations, etc.)

3. Integrating existing MCP servers: Connect to any MCP-compatible server by updating the MCP_URL in your configuration

4. Running multiple MCP servers: Modify the agent to connect to multiple MCP endpoints for access to diverse tool sets

### Task Automation with Invoke

This project uses Invoke for task automation. All tasks are defined in tasks.py and can be run with uv run invoke .

Available Tasks

```shell
# Start all services with automatic health checks
uv run invoke app

# Run individual services
uv run invoke api    # Start the Agent API server
uv run invoke mcp    # Start the MCP demo server  
uv run invoke max    # Start the MAX model server

# Clean up ports (useful if services didn't shut down cleanly)
uv run invoke clean
uv run invoke clean --ports=8000,8001,8002
```

How It Works

The tasks.py file defines several key tasks:

1. app: Orchestrates all three services using Honcho process manager

- Automatically cleans up ports before starting
- Manages all services in a single terminal
- Handles graceful shutdown

2. api: Starts the Agent API with health check waiting

- Waits for MAX and MCP services to be healthy
- Retries health checks with exponential backoff
- Only starts once dependencies are ready

3. max: Launches the MAX model server

- Configures the model and weights paths
- Uses GGUF quantized weights for efficiency

4. mcp: Runs the demo MCP server (demo_mcp_server module)

- Provides a simple character counting tool as an example
- Runs independently from the agent
- Uses debug logging for development

5. clean: Port cleanup utility

- Kills processes occupying specified ports
- Useful for development when services don't shut down cleanly

Troubleshooting

Common Issues

1. Connection Refused: Ensure all three services are running and ports are available

2. Tool Not Found: Verify the MCP server is running and accessible at the configured URL

3. Model Loading Issues: Ensure you have access to the meta-llama/Llama-3.2-1B-Instruct model

Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
## AUTODOC-REPO-CHAT-AGENT

Auto Documentation Agent for GitHub Repository
Learn How to Build a GitHub Chat and Auto-Doc Agent with Qwen2.5 and MAX Serve

README

This recipe demonstrates how to build a powerful GitHub repository assistant that combines:

Qwen2.5-7B-Instruct-1M for intelligent code analysis and documentation generation
gitingest for efficient GitHub repository analysis
Qdrant for vector storage and semantic search
sentence-transformers for code embedding generation
MkDocs with Material theme for beautiful documentation sites
MAX Serve for efficient model serving
The agent provides three main capabilities:

Repository-aware Q&A for answering questions about specific codebases
Automatic documentation generation for Python and Mojo repositories
General programming chat for development assistance
While this recipe focuses on Python code, the patterns demonstrated here can be adapted for various needs like:

API documentation generation
Code explanation and tutorials
Technical specification creation
Knowledge base construction
Educational content development
Requirements
Please make sure your system meets our system requirements.

This recipe assumes you are using uv to work with Python. Install uv if you don't have it already by visiting docs.astral.sh/uv/.

Important: GPU requirements
This recipe requires a GPU. Please visit MAX GPU requirements to view compatible GPUs.

Quick start
Download the code for this recipe using the git CLI:

git clone https://github.com/modular/max-recipes.git
cd max-recipes/autodoc-repo-chat-agent
Start the LLM server:

Make sure the port 8010 is available. You can adjust the port settings in pyproject.toml.

uv run poe server
In a new terminal, run the agent:

uv run poe agent
When prompted, you can:

Ask questions about a specific repository
Include URL of a GitHub repository and start asking questions about it
Ask to generate documentation for a Python GitHub repository (larger code bases are more time consuming)
To clean up generated files:

uv run poe clean
System architecture
Services

Backend

User Interface

Rich CLI Interface

GitHub Repository Analyzer

Code Chunk Extractor

Sentence Transformer

Qdrant Vector DB

Documentation Generator

MkDocs Site Builder

Repository Q&A

General Chat

MAX Serve with Qwen2.5

The architecture consists of several key components:

User Interface: Rich CLI for interaction
Repository Analysis:
GitHub repository ingestion
Code chunk extraction
Embedding generation
Query Handling:
Documentation generation
Repository-aware Q&A
General programming chat
LLM Integration:
MAX Serve with Qwen2.5
Context-aware prompting
Response formatting
Request flow
Here's how a typical request flows through the system:

MkDocs Builder
Qwen2.5
Qdrant
Sentence Transformer
Code Extractor
GitIngest
Query Type Detector
CLI Interface
User
MkDocs Builder
Qwen2.5
Qdrant
Sentence Transformer
Code Extractor
GitIngest
Query Type Detector
CLI Interface
User
alt
[Documentation Generation]
[Repository Q&A]
[General Chat]
Enter query
Determine query type
Fetch repository
Extract code chunks
Generate embeddings
Store vectors
Send code for analysis
Generate documentation
Return site URL
Fetch repository
Extract code chunks
Generate embeddings
Store vectors
Query relevant code
Send code + query
Return answer
Send query
Return answer
Technical deep dive
Main application flow
The main entry point orchestrates the different handlers and manages the conversation flow:

async def main():
    """Main entry point for the application."""
    console = Console()
    client = AsyncOpenAI(base_url=LLM_SERVER, api_key=LLM_API_KEY)

    handlers = {
        QueryType.CHAT: ChatHandler(client, console),
        QueryType.DOC_GEN: DocGenHandler(client, console),
        QueryType.REPO_QA: RepoQAHandler(client, console)
    }

    console.print(Panel(
        "[bold blue]Welcome to GitHub Repo Helper[/bold blue]\n\n"
        "I can help you with:\n"
        "- [green]Generating documentation[/green] for GitHub repositories\n"
        "- [green]Answering questions[/green] about repository code\n"
        "- [green]General questions[/green] about programming and development\n\n"
        "Type your query or 'quit' to exit",
        title="🤖 GitHub Repo Helper",
        border_style="blue",
        expand=False
    ))

    # Global conversation history
    conversation_history = []
    # Track the current handler type to maintain context
    current_handler_type = None
    # Track the current repo URL
    current_repo_url = None

    while True:
        console.print("[bold cyan]You:[/bold cyan] ", end="")
        query = input()

        if query.lower() in ['quit', 'exit', 'bye']:
            console.print("[bold blue]Thanks for using GitHub Repo Helper. Goodbye![/bold blue]")
            break

        # Add user query to global conversation history
        conversation_history.append({"role": "user", "content": query})

        query_type, repo_url = await determine_query_type(query, client)
        context = QueryContext(query=query, repo_url=repo_url)

        # Handle the query with the appropriate handler
        handler = handlers[query_type]
        result = await handler.handle(context)

        # Update global conversation history with the assistant's response
        conversation_history.append({"role": "assistant", "content": result})
Key features:

Rich console interface with colorful formatting
Conversation history management across handlers
Query type detection and routing
Context preservation between interactions
Query type detection
The system automatically determines the type of query to route it to the appropriate handler:

async def determine_query_type(query: str, client: AsyncOpenAI) -> Tuple[QueryType, Optional[str]]:
    """Determine the type of query and extract GitHub repository URL if present."""
    # Check for GitHub URL in the query
    github_url_match = re.search(r'https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+', query)
    github_url = github_url_match.group(0) if github_url_match else None

    # Simple heuristics for query classification
    if re.search(r'(generate|create|build|make)\s+(docs|documentation)', query.lower()):
        return QueryType.DOC_GEN, github_url

    if github_url or re.search(r'(repo|repository|codebase)', query.lower()):
        return QueryType.REPO_QA, github_url

    return QueryType.CHAT, None
Key features:

URL extraction with regex
Keyword-based classification
Default fallback to general chat
Repository Q&A
The system provides context-aware answers to questions about repositories:

class RepoQAHandler(BaseHandler):
    async def handle(self, context: QueryContext):
        """Handle repository Q&A with context and conversation history."""
        # Process repository if needed
        if context.repo_url and not context.repo_content:
            with self.console.status("[bold green]Processing repository...", spinner="dots"):
                summary, tree, raw_content = await ingest_async(context.repo_url)
                context.repo_content = self._process_raw_content(raw_content)

                # Parse code and generate embeddings
                await code_parse(context.repo_content, self.collection_name, console=self.console)
                self.embeddings_created = True

        # Perform semantic search to find relevant code chunks
        relevant_chunks = []
        if context.repo_content and self.embeddings_created:
            query_embedding = get_embedding_model().encode(context.query)

            # Search for relevant code chunks
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=5
            )

            # Get the actual chunks from search results
            for result in search_results:
                chunk_id = result.id
                chunk = self.chunk_cache.get(chunk_id)
                if chunk:
                    relevant_chunks.append(chunk)

        # Generate response with context
        system_prompt = f"""You are a helpful assistant that answers questions about code repositories.
Current repository: {context.repo_url or 'Unknown'}
Use the provided code context to answer questions accurately.
If you don't know the answer, say so rather than making something up."""

        # Prepare context from relevant chunks
        context_text = ""
        if relevant_chunks:
            context_text = "Here are code snippets that might help answer the question:\n\n"
            for i, chunk in enumerate(relevant_chunks):
                context_text += f"Snippet {i+1} from {chunk.file_path}:\n```{chunk.metadata.get('language', 'python')}\n{chunk.content}\n```\n\n"

        # Generate response
        response = await self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{context_text}\nQuestion: {context.query}"}
            ]
        )

        return response.choices[0].message.content
Features:

Repository content caching
Semantic search for relevant code
Context-aware prompting
Conversation history tracking
Code extraction and analysis
The system uses gitingest to analyze repositories and extract meaningful code chunks:

async def extract_code_chunks(repo_content, language='python'):
    """Extract meaningful code chunks from repository content."""
    chunks = []
    config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS['python'])

    for file_path, content in repo_content.items():
        if not any(file_path.endswith(ext) for ext in config['extensions']):
            continue

        for chunk_type, pattern in config['patterns'].items():
            for match in re.finditer(pattern, content, re.DOTALL):
                chunk_content = match.group(0)

                # Extract name using the language-specific pattern
                name_match = re.search(config['name_pattern'], chunk_content)
                name = name_match.group(2) if name_match else "Unknown"

                chunks.append(CodeChunk(
                    content=chunk_content,
                    start_line=content[:match.start()].count('\n') + 1,
                    end_line=content[:match.end()].count('\n') + 1,
                    file_path=file_path,
                    chunk_type=chunk_type,
                    metadata={
                        'language': language,
                        'name': name
                    }
                ))

    return chunks
Key features:

Language-specific pattern matching
Intelligent chunk extraction
Metadata collection for context
Documentation generation
The LLM generates documentation based on code analysis:

async def generate_documentation(chunk, prompt, doc_type, client):
    """Generate documentation or examples using the LLM."""
    language = chunk.metadata.get('language', 'python')
    config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS['python'])

    system_content = get_language_prompt(language, doc_type)

    try:
        enhanced_prompt = f"""
{prompt}

When creating code examples:
1. Always use proper code blocks with ```{config['code_block']} at the start and ``` at the end
2. Make sure examples are complete and runnable
3. Include necessary imports using the format: {config['import_format'].format(package=chunk.file_path.split('/')[0], name=chunk.metadata.get('name'))}
4. Use proper variable names that match the codebase
5. Reference only existing functions and classes
6. When linking to other components, use proper markdown links: [ComponentName](ComponentName.md)
7. Demonstrate these language-specific features where appropriate:
{chr(10).join(f'   - {feature}' for feature in config['features'])}
"""

        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": enhanced_prompt}
            ]
        )
        content = response.choices[0].message.content
        return ensure_code_blocks_closed(content)
    except Exception as e:
        return e
Key capabilities:

Language-specific prompting
Code example generation
Proper formatting and linking
Error handling
MkDocs site generation
The documentation generator creates a complete MkDocs site with proper navigation:

async def build_doc_site(documentation, top_level_examples, output_dir, readme_content, repo_info):
    """Build a complete documentation site with MkDocs."""
    # Create directory structure
    os.makedirs(output_dir, exist_ok=True)
    docs_dir = os.path.join(output_dir, "docs")
    api_dir = os.path.join(docs_dir, "api")
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(api_dir, exist_ok=True)

    # Organize components by type
    components = {
        'Classes': [],
        'Functions': [],
        'Constants': [],
        'Other': []
    }

    # Categorize documentation components
    for name in documentation.keys():
        chunk_type = name.split(':', 1)[0] if ':' in name else 'Other'
        clean_name = name.split(':', 1)[1] if ':' in name else name

        if chunk_type.lower() == 'class':
            components['Classes'].append(clean_name)
        elif chunk_type.lower() == 'function':
            components['Functions'].append(clean_name)
        elif chunk_type.lower() in ['constant', 'variable']:
            components['Constants'].append(clean_name)
        else:
            components['Other'].append(clean_name)

    # Generate index.md
    index_content = f"# {repo_info['repo']} Documentation\n\n"
    if readme_content:
        index_content += readme_content
    else:
        index_content += f"Welcome to the documentation for {repo_info['repo']}.\n\n"
        index_content += "## Overview\n\n"
        index_content += f"This documentation provides details about the {repo_info['repo']} codebase.\n\n"

    # Write all files in parallel
    file_tasks = [
        write_file(os.path.join(docs_dir, "index.md"), index_content),
        write_file(os.path.join(docs_dir, "installation.md"), top_level_examples.get('installation', f"# Installation\n\nInstructions for installing {repo_info['repo']}.")),
    ]

    # Write API documentation files
    for name, doc_content in documentation.items():
        clean_name = name.split(':', 1)[1] if ':' in name else name
        file_tasks.append(
            write_file(
                os.path.join(api_dir, f"{re.sub(r'[^a-zA-Z0-9_-]', '_', clean_name)}.md"),
                f"# {clean_name}\n\n{doc_content}"
            )
        )

    # Write mkdocs.yml configuration
    file_tasks.append(
        write_file(os.path.join(output_dir, "mkdocs.yml"), f"""site_name: {repo_info['repo']} Documentation
theme:
  name: material
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.sections
    - navigation.expand
    - navigation.indexes
    - toc.integrate
    - search.suggest
    - search.highlight
markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
nav:
  - Home: index.md
  - Installation: installation.md
  - API Documentation:
    - Overview: api/index.md
    - Classes:
{chr(10).join(['      - ' + name + ': api/' + re.sub(r'[^a-zA-Z0-9_-]', '_', name) + '.md' for name in components['Classes']])}
    - Functions:
{chr(10).join(['      - ' + name + ': api/' + re.sub(r'[^a-zA-Z0-9_-]', '_', name) + '.md' for name in components['Functions']])}
""")
    )

    # Execute all file writing tasks in parallel
    await asyncio.gather(*file_tasks)
Features:

Parallel file writing for performance
Automatic component categorization
Structured navigation generation
Markdown extension configuration
Example creation and verification
The system generates usage examples for each component and verifies their correctness:

async def generate_examples(self, documentation, repo_content, repo_info, console):
    """Generate usage examples for documented components."""
    examples = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[bold blue]Generating examples...", total=len(documentation))

        for name, doc_content in documentation.items():
            # Extract component type and name
            component_type = name.split(':', 1)[0] if ':' in name else 'unknown'
            component_name = name.split(':', 1)[1] if ':' in name else name

            # Find relevant code chunks for context
            relevant_chunks = []
            for file_path, content in repo_content.items():
                if component_name in content:
                    relevant_chunks.append(f"File: {file_path}\n```python\n{content}\n```")

            context = "\n\n".join(relevant_chunks[:3])  # Limit context size

            prompt = f"""Create a practical usage example for '{component_name}' ({component_type}) in the {repo_info['repo']} repository.

            Here's the documentation:
            {doc_content}

            Here's some relevant code for context:
            {context}

            Create a complete, runnable example that demonstrates the main functionality.
            Include imports, setup code, and comments explaining key steps.
            """

            example = await self.generate_documentation(
                CodeChunk(
                    content="",
                    start_line=0,
                    end_line=0,
                    file_path="",
                    chunk_type=component_type,
                    metadata={"name": component_name, "language": "python"}
                ),
                prompt,
                "example",
                self.client
            )

            examples[component_name] = example
            progress.update(task, advance=1)

    return examples

async def verify_examples(self, examples, documentation, console):
    """Verify generated examples for correctness."""
    verified_docs = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[bold blue]Verifying examples...", total=len(examples))

        for name, example in examples.items():
            doc_content = documentation.get(name, "")

            prompt = f"""Verify if this example correctly demonstrates the usage of '{name}'.

            Documentation:
            {doc_content}

            Example:
            {example}

            If the example is correct, respond with "VERIFIED".
            If there are issues, respond with "ISSUES:" followed by a description of the problems.
            """

            response = await self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a code reviewer verifying documentation examples."},
                    {"role": "user", "content": prompt}
                ]
            )

            verification = response.choices[0].message.content

            if verification.startswith("VERIFIED"):
                # Add the verified example to the documentation
                verified_docs[name] = f"{doc_content}\n\n## Example\n\n{example}"
            else:
                # Add the example but note the issues
                issues = verification.replace("ISSUES:", "").strip()
                verified_docs[name] = f"{doc_content}\n\n## Example\n\n{example}\n\n> **Note:** This example may have issues: {issues}"

            progress.update(task, advance=1)

    return verified_docs
This process ensures:

Examples are contextually relevant to the codebase
Each component has practical usage demonstrations
Examples are verified for correctness
Issues are clearly marked for user awareness
Documentation includes both API reference and usage examples
Customization options
You can customize the system in several ways:

1. Language configuration
LANGUAGE_CONFIGS = {
    'python': {
        'features': [
            'Type hints',
            'Decorators',
            'Context managers',
            'Async/await',
            'Generator functions'
        ],
        'import_format': 'from {package} import {name}',
        'code_block': 'python',
        'type_system': 'Python type hints (str, int, List[str], etc.)',
        'patterns': {
            'function': r'def\s+\w+\s*\(.*?\).*?:(?:(?!\ndef\s+).)*',
            'class': r'class\s+\w+(?:\(.*?\))?.*?:(?:(?!\nclass\s+).)*'
        },
        'extensions': ['.py'],
        'name_pattern': r'(def|class)\s+(\w+)'
    },
    # Add more languages as needed
}
2. LLM parameters
# Change LLM model
LLM_MODEL = "Qwen/Qwen2.5-7B-Instruct-1M"  # Try different models

# Adjust batch processing
BATCH_SIZE = 50  # Increase/decrease based on memory

# Modify system prompts
system_content = get_language_prompt(language, doc_type)  # Customize prompts
3. Documentation format
# Customize MkDocs configuration
mkdocs_config = """site_name: {repo_info['repo']} Documentation
theme:
  name: material
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.sections
    - navigation.expand
    - navigation.indexes
    - toc.integrate
    - search.suggest
    - search.highlight
"""

# Adjust documentation structure
components = {
    'Classes': [],
    'Functions': [],
    'Constants': [],
    'Other': []
}
Troubleshooting
Common issues and solutions:

GPU Memory Issues

Error: "CUDA out of memory"
Solution: Reduce BATCH_SIZE in configuration
Ensure no other GPU processes are running
Repository Access Issues

Error: "Failed to clone repository"
Solution: Check repository URL and permissions
Try using HTTPS instead of SSH
Documentation Generation Issues

Error: "Failed to generate documentation"
Solution: Check language configuration
Ensure code is properly formatted
MAX Serve Issues

Error: "Connection refused to MAX Serve"
Solution: Ensure MAX Serve is running
Check GPU requirements are met
