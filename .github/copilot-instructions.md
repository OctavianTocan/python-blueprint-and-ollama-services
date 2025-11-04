# Copilot Instructions for this Repo

Purpose: Make AI coding agents productive immediately in this workspace by capturing the project architecture, local conventions, and day‑to‑day workflows that aren’t obvious from code alone.

## Monorepo layout

- Top level is a uv/hatch Python workspace containing multiple packages:
  - toolkit/ (src/toolkit): shared utilities used everywhere (text parsing, file I/O, formatting, console)
  - blueprint-cleaner/ (src/blueprint_cleaner): parses Unreal Engine .COPY exports → reports + multiple formats
  - ollama-service/ (src/ollama_service): FastAPI wrapper around Ollama + optional FastMCP integration
- Python version: 3.13+. Dependency manager: uv. Build backends: hatchling or uv_build (per-package).

## Key workflows

- Sync dependencies per package:
  - cd <package>; uv sync
- Run tests from repo root (pytest is configured as a dev dep per package):
  - uv run pytest
  - Or focus: uv run pytest blueprint-cleaner/tests -q
- Run CLI (blueprint-cleaner):
  - uv run blueprint-cleaner data/in/BP_X.COPY -f markdown|json|bundle|summary|cpp-header|cpp-source [-o out]
- Start API server (ollama-service):
  - uv run uvicorn ollama_service.api:app --reload --port 4001

## Cross-package dependencies

- Local linking is done via [tool.uv.sources] in each pyproject:
  - blueprint-cleaner depends on: toolkit, ollama-service (path editable)
  - toolkit depends on: ollama-service (workspace)
- Import examples:
  - from toolkit.text_parsing import find_first_match, extract_tail_identifier
  - from ollama_service.client import ask_ollama_question

## Blueprint Cleaner architecture

### Understanding .COPY Files

Unreal `.COPY` exports are text snapshots with nested `Begin Object`/`End Object` blocks. Key patterns:

- **Graph blocks**: Must have both `Schema=` (e.g., EdGraphSchema, WidgetGraphSchema) AND `Nodes(` array
- **Node blocks**: Nested objects starting with `K2Node_*` (execution) or `EdGraphNode_Comment` (annotations)
- **Widget blueprints**: Add `WidgetTree=`, `Animations=`, `Bindings=` sections parsed separately
- Stack-based extraction: `parsers.block_extraction.collect_graph_blocks` tracks nesting with a stack until matching `End Object`

### Data Flow

1. **Entry**: `cli.py` → `pipeline.clean_blueprint_file`
2. **Report building** (`report.build_blueprint_report`):
   - `metadata.build_metadata` → name, parent class, cpp class
   - `variables.extract_variables` → variable declarations
   - `graphs.summarize_graphs` → `collect_graph_blocks` → `collect_node_blocks` → `node_parsing` extracts calls/vars/comments
   - `widget_data` extracts bindings, animations, widget variables (UMG only)
   - `analysis.build_function_synopses` deduplicates function calls across graphs
3. **Formatting**:
   - `formatters/markdown.py` → human-readable with tables and sections
   - `formatters/json_output.py` → machine-readable JSON
   - `formatters/unreal_cpp.py` → C++ header/source stubs
4. **Artifacts**: `BlueprintArtifacts` bundles all outputs; `to_bundle()` produces JSON payload

### Parser Layers (parsers/)

- **block_extraction**: `collect_graph_blocks(lines)` finds EdGraph blocks; `collect_node_blocks(graph)` extracts nodes
- **graph_classification**: Categorizes graphs (event, function, macro, construction script)
- **node_parsing**: Reads `K2Node_*` for function calls, variable reads/writes, developer comments
- **variable_collection**: `collect_variable_entries(content, anchor)` gathers variable metadata arrays
- **variable_parsing**: Converts variable entries to `VariableInfo` models

### Output Formats

CLI `-f` flag (see `cli.SUPPORTED_FORMATS`):

- `markdown` (default): Rich summary with tables
- `json`: Structured JSON
- `bundle`: JSON bundle with all formats embedded
- `summary`: AI-generated rolling summary (calls Ollama via `summaries.generate_rolling_summary`)
- `cpp-header`/`cpp-source`: C++ skeleton code

Format mapping in `cli.py`; extension logic in `pipeline.render_output`.

## Ollama Service architecture

- FastAPI app in ollama_service.api exposes:
  - POST /ollama/ask (body: OllamaRequest) and GET /ollama/ask (query params)
  - GET /health
  - Optional FastMCP adapter: FastMCP.from_fastapi(app) if fastmcp is installed
- Client usage inside repo:
  - ask_ollama_question(prompt, model?, system?, options?, endpoint?, headers?) → str
  - Builds payload via build_ollama_payload; httpx posts to endpoint (default http://localhost:11434/api/generate)
  - parse_ollama_response expects { "response": "..." }; strip_markdown_code_blocks removes ``` fences
- Pydantic models in models.py: OllamaOptions, OllamaRequest, OllamaResponse

## Project conventions

- Clean-code constraints enforced by convention, not tooling:
  - Functions ≤ ~20 lines (prefer 5–10), single responsibility, one abstraction level
  - Doxygen-style docstrings with @param/@return
  - Rich READMEs per package with quick start and architecture
- CLI defaults:
  - blueprint-cleaner default format is markdown; mapping of -f to file extensions handled in cli.py
  - When -f text is provided, it aliases markdown for backward-compat
- Summary generation:
  - summaries.generate_rolling_summary(windowed over markdown) calls a summariser callback
  - Default summariser in pipeline.\_default_summariser uses ollama_service.client.ask_ollama_question
  - Known pitfall: Ollama can return empty responses → client raises RuntimeError; tests stub summariser
- Widget blueprint handling:
  - UMG bindings stay in "UMG Bindings" section (widget → property → function)
  - Animations listed by name only (strip path/metadata)
  - Widget variables in separate section from blueprint variables

## Testing expectations

- Tests exist mainly in blueprint-cleaner/tests and ollama-service/tests
- Run targeted tests during development:
  - uv run pytest blueprint-cleaner/tests/test_blueprint_cleaner.py -q
  - uv run pytest ollama-service/tests/test_ollama_service.py -q
- Some tests describe desired future behavior (spec-first). Expect initial failures when features are not implemented yet.
- Widget tests: `test_widget_blueprint_reports_umg_metadata` validates bindings/animations/widget vars extraction + graph parsing

## Examples to follow

- CLI: blueprint_cleaner/cli.py shows option parsing and default extension mapping
- Rolling summary: blueprint_cleaner/summaries.py demonstrates chunking and prompt composition
- HTTP client: ollama_service/client.py shows payload building, response parsing, and code‑block stripping
- Bundle shape: blueprint_cleaner/artifacts.py → AVAILABLE_FORMATS and to_bundle() payload
- Widget extraction: widget_data.py regex-based parsing for bindings/animations/widget vars

## Environment & config

- Default Ollama endpoint: http://localhost:11434/api/generate
- API server default port: 4001
- No .env is required; options can be passed via request fields. If you add env vars, document them in the package README and reflect here.

## When adding code

- Prefer putting shared helpers in src/toolkit and wire via [tool.uv.sources]
- Keep public APIs small and concrete; document new CLI flags in the package README and update tests/CLIs accordingly
- If you add output formats, update:
  - cli.SUPPORTED_FORMATS
  - artifacts.AVAILABLE_FORMATS
  - pipeline.render_output branch
  - tests for bundles/outputs
- When extending parsers:
  - Add extraction logic in parsers/ or widget_data.py
  - Update models.py with new dataclasses
  - Wire into report.build_blueprint_report
  - Emit in formatters (markdown.py, json_output.py)
  - Add test fixture in test_blueprint_cleaner.py
