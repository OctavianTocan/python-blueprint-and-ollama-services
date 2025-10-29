# Python Utilities Collection

Personal collection of Python utilities following clean code principles with modular architecture and shared toolkit foundation.

## Projects

### 1. **blueprint-cleaner**

Transform Unreal Engine 5 blueprint `.COPY` files into AI-friendly summaries.

- **Purpose**: Parse complex blueprint exports into markdown/JSON
- **Features**: Variable extraction, graph analysis, function call tracking
- **Tech**: Python 3.13, uv, custom parsers

[→ Documentation](./blueprint-cleaner/README.md)

### 2. **pieces-service**

HTTP wrapper for Pieces SDK Copilot with FastAPI and FastMCP integration.

- **Purpose**: Expose Pieces copilot via REST API
- **Features**: GET/POST endpoints, streaming responses, FastMCP
- **Tech**: FastAPI, Pieces SDK, FastMCP

[→ Documentation](./pieces_service/README.md)

### 3. **unified-api**

Combined service exposing all utilities under a single FastAPI application.

- **Purpose**: Unified interface for blueprint cleaning and copilot queries
- **Features**: Multi-service facade, file uploads, FastMCP
- **Tech**: FastAPI, FastMCP, python-multipart

[→ Documentation](./unified_api/README.md)

### 4. **toolkit**

Shared utilities for text parsing, file I/O, formatting, and console output.

- **Purpose**: Reusable helpers across all projects
- **Modules**: text_parsing, file_io, collections, formatting, console
- **Tech**: Pure Python, lightweight

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

cd ../pieces_service
uv sync
uv run uvicorn pieces_service.api:app --reload --port 4000

cd ../unified_api
uv sync
uv run uvicorn unified_api.main:app --reload --port 8000
```

### Dependencies

Projects declare local dependencies via `tool.uv.sources`:

```toml
[tool.uv.sources]
toolkit = { path = "../", editable = true }
blueprint-cleaner = { path = "../blueprint-cleaner", editable = true }
```

## Documentation

- **MEMORY_CAPTURE.md**: Learnings and patterns for memory systems
- **TESTING.md**: Test roadmap (scaffolded, not enforced)
- Individual project READMEs with API docs and examples

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
   # Add toolkit as dependency
   ```

2. **Implement with clean code principles**:

   - Small functions (5-10 lines)
   - Doxygen comments
   - Modular structure

3. **Test scaffolding**:

   ```bash
   mkdir tests
   # Add placeholder tests
   ```

4. **Documentation**:
   - Rich README with Quick Start
   - Architecture section
   - API examples

## Testing

Tests are scaffolded but intentionally not enforced:

- Structure ready for pytest
- Placeholder tests prevent import errors
- Will implement when ready to learn patterns

See [TESTING.md](./TESTING.md) for roadmap.

## Memory Systems

Learnings queued for openmemory/pieces LTM in [MEMORY_CAPTURE.md](./MEMORY_CAPTURE.md).

## License

MIT
