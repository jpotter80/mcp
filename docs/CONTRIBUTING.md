# Contributing to MCP Documentation Search

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discriminatory language, or unwelcome attention
- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Publishing others' private information without permission

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report**:
1. Check existing issues to avoid duplicates
2. Collect relevant information (error messages, logs, environment)
3. Try to reproduce the issue with minimal steps

**Submit a bug report**:
- Use the issue tracker
- Include a clear title and description
- Provide steps to reproduce
- Include error messages and logs
- Specify your environment (OS, Python version, etc.)

### Suggesting Enhancements

**Before suggesting an enhancement**:
1. Check if it already exists or has been proposed
2. Consider if it fits the project's scope and goals

**Submit an enhancement suggestion**:
- Use the issue tracker with `enhancement` label
- Explain the problem it solves
- Describe the proposed solution
- Provide examples if applicable

### Contributing Code

We welcome contributions! Here are areas where you can help:

#### 1. Adding New Documentation Servers

Create MCP servers for new documentation sources:
- Python standard library
- DuckDB documentation
- VS Code API
- Other popular tools/frameworks

See [CREATING_NEW_MCP.md](CREATING_NEW_MCP.md) for detailed instructions.

#### 2. Improving Existing Servers

- Optimize chunking strategies
- Enhance metadata extraction
- Improve search relevance
- Add test coverage

#### 3. Adding Documentation Format Support

Implement processors for new formats:
- reStructuredText (RST)
- AsciiDoc
- HTML
- Custom formats

#### 4. Enhancing Search

- Improve RRF fusion algorithm
- Add query understanding/rewriting
- Implement result re-ranking
- Add semantic caching

#### 5. Tooling and Automation

- Improve build scripts
- Add CI/CD pipelines
- Create monitoring tools
- Enhance error reporting

#### 6. Documentation

- Improve existing documentation
- Add tutorials and examples
- Create video guides
- Translate documentation

## Development Workflow

### Setup Development Environment

1. **Fork and clone**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/mcp.git
   cd mcp
   ```

2. **Install dependencies**:
   ```bash
   # With pixi (recommended)
   pixi install
   
   # Or with venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r servers/mojo-manual-mcp/requirements.txt
   ```

3. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

### Branch Naming Conventions

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test additions or fixes

### Making Changes

1. **Make your changes**: Edit code, add tests, update documentation

2. **Test your changes**:
   ```bash
   # Run tests
   pixi run test  # If tests exist
   
   # Test manually
   pixi run mojo-build
   pixi run search -- -q "test query"
   ```

3. **Check code quality**:
   ```bash
   # Python linting
   python -m py_compile path/to/file.py
   
   # Or use a linter
   pylint path/to/file.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add support for RST format"
   ```

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(preprocessing): Add RST format support
fix(search): Handle empty query gracefully
docs(quickstart): Update VS Code configuration example
refactor(embeddings): Improve batch processing efficiency
```

### Testing Locally

Before submitting a PR:

1. **Test the full pipeline**:
   ```bash
   # With a test server
   ./tools/scaffold_new_mcp.sh --name test --doc-type docs --format markdown
   # Add test docs
   ./tools/build_mcp.sh --mcp-name test
   # Verify search works
   cd servers/test-docs-mcp/runtime
   python search.py -q "test query"
   ```

2. **Test existing functionality**:
   ```bash
   pixi run mojo-build
   pixi run search -- -q "ownership"
   ```

3. **Verify no regressions**:
   - Existing servers still work
   - No broken imports
   - Configuration files valid

## Coding Standards

### Python Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/):

- Use 4 spaces for indentation
- Maximum line length: 100 characters (flexible for readability)
- Use descriptive variable names
- Add docstrings to functions and classes

**Example**:
```python
def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Perform hybrid search combining vector and keyword methods.
    
    Args:
        query: Search query string
        top_k: Number of results to return (default: 5)
        
    Returns:
        List of search results with scores and metadata
        
    Raises:
        ValueError: If query is empty or top_k < 1
    """
    # Implementation
    pass
```

### Configuration Files

- Use YAML for configuration
- Include comments explaining parameters
- Use variable substitution (${VAR}) for paths
- Provide sensible defaults

### Documentation

- Every public function needs a docstring
- Update README.md if adding user-facing features
- Add examples for new functionality
- Keep documentation in sync with code

## Testing Requirements

### Manual Testing Checklist

For new features:
- [ ] Feature works as intended
- [ ] Edge cases handled
- [ ] Error messages are clear
- [ ] Documentation updated
- [ ] Examples provided

For bug fixes:
- [ ] Bug is reproducible
- [ ] Fix resolves the issue
- [ ] Regression test added
- [ ] Related issues checked

### Automated Testing

If adding tests (encouraged):

```python
# tests/test_search.py
def test_hybrid_search():
    searcher = HybridSearcher(db_path="test.db")
    results = searcher.search("test query", top_k=5)
    assert len(results) <= 5
    assert all("title" in r for r in results)
```

Run tests:
```bash
pytest tests/
```

## Documentation

### Documentation Requirements

When contributing:

1. **Code documentation**:
   - Docstrings for all public functions/classes
   - Comments for complex logic
   - Type hints where appropriate

2. **User documentation**:
   - Update relevant markdown files
   - Add examples if introducing new features
   - Update configuration references

3. **README updates**:
   - Add new servers to available servers list
   - Document new capabilities
   - Update quick start if needed

### Documentation Structure

```
docs/
├── QUICKSTART.md          # Getting started
├── SETUP_PIXI.md          # Development setup (pixi)
├── SETUP_VENV.md          # Development setup (venv)
├── USING_MCP_SERVER.md    # Using servers in IDEs
├── CREATING_NEW_MCP.md    # Creating new servers
├── ARCHITECTURE.md        # System architecture
└── CONTRIBUTING.md        # This file
```

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass** (manual or automated)
2. **Update documentation** as needed
3. **Rebase on main** to avoid merge conflicts
4. **Review your own changes** - read the diff carefully

### Submitting a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR** on GitHub:
   - Use a clear title describing the change
   - Reference related issues (`Fixes #123`)
   - Provide a detailed description
   - Include testing instructions
   - Add screenshots if UI-related

3. **PR template** (suggested format):
   ```markdown
   ## Description
   Brief description of changes
   
   ## Motivation
   Why is this change needed?
   
   ## Changes
   - Added X
   - Modified Y
   - Fixed Z
   
   ## Testing
   How to test this PR
   
   ## Checklist
   - [ ] Code tested manually
   - [ ] Documentation updated
   - [ ] No regressions introduced
   - [ ] Commit messages follow convention
   ```

### Review Process

1. **Maintainer review**: A maintainer will review your PR
2. **Feedback**: Address any requested changes
3. **Approval**: Once approved, your PR will be merged
4. **Thank you!**: Your contribution is appreciated

### After Merge

- Delete your branch (optional)
- Pull latest main
- Celebrate your contribution! 🎉

## Project Structure

Understanding the project structure helps with contributions:

```
/mcp/
├── servers/              # MCP servers (contributions welcomed)
├── shared/               # Build infrastructure (core code)
│   ├── preprocessing/    # Document processing
│   ├── embedding/        # Embedding generation
│   └── templates/        # Templates for new servers
├── tools/                # Automation scripts
├── docs/                 # Documentation
└── source-documentation/ # Documentation sources
```

**Key files**:
- `shared/preprocessing/src/processor_factory.py` - Add format support here
- `shared/templates/*` - Update templates for new server features
- `tools/*.sh` - Automation scripts
- `docs/*.md` - User documentation

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **Discussions**: General questions, ideas
- **Pull Requests**: Code review, feedback

### Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [CREATING_NEW_MCP.md](CREATING_NEW_MCP.md) - Server creation
- [tools/README.md](../tools/README.md) - Tool documentation

### Mentorship

New to contributing? We're happy to help!
- Look for issues labeled `good first issue`
- Ask questions in issue comments
- Request clarification if anything is unclear

## Recognition

Contributors will be:
- Listed in project contributors
- Mentioned in release notes (for significant contributions)
- Credited in documentation (for major features)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing!** Your efforts make this project better for everyone.
