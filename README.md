# Python Utilities Collection

Personal collection of Python utilities following clean code principles with modular architecture and shared toolkit foundation.

## Projects

### 1. **blueprint-cleaner**

Transform Unreal Engine 5 blueprint `.COPY` files into AI-friendly summaries.

- **Purpose**: Parse complex blueprint exports into markdown/JSON
- **Features**: Variable extraction, graph analysis, function call tracking
- **Tech**: Python 3.13, uv, custom parsers
- **Docs spotlight**: The [Unreal Blueprint Glossary](./blueprint-cleaner/README.md#unreal-blueprint-glossary) explains terms like `Begin Object`, `EdGraph`, and widget bindings so newcomers can read exports confidently.

[→ Documentation](./blueprint-cleaner/README.md)

### 2. **ollama-service**

HTTP API wrapper for Ollama providing LLM query capabilities with FastMCP integration.

- **Purpose**: Expose Ollama API via REST endpoints
- **Features**: GET/POST endpoints, structured logging, health checks
- **Tech**: FastAPI, httpx, FastMCP, structlog

[→ Documentation](./ollama-service/README.md)

### 3. **toolkit**

Shared utilities for text parsing, file I/O, formatting, and console output.

- **Purpose**: Reusable helpers across all projects
- **Modules**: text_parsing, file_io, collections, formatting, console
- **Tech**: Pure Python, lightweight

[→ Documentation](./src/toolkit/README.md)

## Architecture

### Shared Toolkit Foundation

All projects leverage a common `toolkit` package:

```python
from toolkit.text_parsing import find_first_match, extract_tail_identifier
from toolkit.file_io import read_text_with_encoding_detection
from toolkit.console import print_metric_summary
```

### Clean Code Principles

Every project follows strict guidelines:

- **Functions < 20 lines** (ideally 5-10)
- **Single responsibility** per function
- **One abstraction level** per function
- **Comprehensive Doxygen documentation**
- **Stepdown rule** for readability

### Standard Project Structure

```
project/
├── src/project_name/
│   ├── parsers/          # Data extraction
│   ├── formatters/       # Output rendering
│   ├── models.py         # Data structures
│   ├── pipeline.py       # Orchestration
│   └── ...
├── data/
│   ├── in/               # Input files
│   └── out/              # Generated output
├── tests/                # Test scaffolds (not enforced yet)
├── README.md
└── pyproject.toml
```

## Quick Start

### Setup

```bash
# Clone or navigate to Utils folder
cd Utils

# Each project uses uv for dependency management
cd blueprint-cleaner
uv sync
uv run blueprint-cleaner --help

cd ../ollama-service
uv sync
uv run uvicorn ollama_service.api:app --reload --port 4001
```

### Dependencies

Projects declare local dependencies via `tool.uv.sources`:

```toml
[tool.uv.sources]
toolkit = { path = "../", editable = true }
ollama-service = { workspace = true, editable = true }
```

## Documentation

Each package includes comprehensive documentation:

- Individual project READMEs with Quick Start guides
- API documentation and usage examples
- Architecture and design decisions

## Tools & Versions

- **Python**: 3.13+
- **Package Manager**: uv 0.9.2
- **Web Framework**: FastAPI
- **MCP Integration**: FastMCP
- **Build Backend**: hatchling / uv_build

## Development Workflow

1. **Create new utility**:

   ```bash
   uv init --package new-project
   cd new-project
   # Add toolkit as dependency in pyproject.toml
   ```

2. **Implement with clean code principles**:

   - Small functions (5-10 lines)
   - Doxygen comments
   - Modular structure
   - Single responsibility

3. **Test scaffolding**:

   ```bash
   mkdir tests
   # Add placeholder tests
   ```

4. **Documentation**:
   - README with Quick Start
   - Architecture section
   - API examples
   - Module documentation

## Testing

Tests are scaffolded but intentionally not enforced:

- Structure ready for pytest
- Placeholder tests prevent import errors
- Run tests: `uv run pytest`

## License

MIT
