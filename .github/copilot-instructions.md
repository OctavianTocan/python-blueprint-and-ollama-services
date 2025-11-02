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

- Entry: blueprint_cleaner.cli: parses args and calls pipeline.clean_blueprint_file
- Pipeline:
  - build_blueprint_report(content) → dataclass BlueprintReport (see models.py)
  - formatters:
    - formatters/markdown.py → format_as_markdown(report)
    - formatters/json_output.py → render_json_output(report)
    - formatters/unreal_cpp.py → generate_unreal_cpp(report) producing header/source + paths
  - summaries.generate_rolling_summary(markdown, summariser, chunk_size) → AI summary
  - artifacts.BlueprintArtifacts aggregates outputs and bundles via to_bundle()
- Supported formats (CLI -f): markdown, json, bundle, summary, cpp-header, cpp-source
- Data flow in pipeline.clean_blueprint_file:
  - read_text_file → generate_blueprint_artifacts → render_output → write_text_file
  - console helpers from toolkit.console print processing header/summary/footer

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

## Testing expectations

- Tests exist mainly in blueprint-cleaner/tests and ollama-service/tests
- Run targeted tests during development:
  - uv run pytest blueprint-cleaner/tests/test_blueprint_cleaner.py -q
  - uv run pytest ollama-service/tests/test_ollama_service.py -q
- Some tests describe desired future behavior (spec-first). Expect initial failures when features are not implemented yet.

## Examples to follow

- CLI: blueprint_cleaner/cli.py shows option parsing and default extension mapping
- Rolling summary: blueprint_cleaner/summaries.py demonstrates chunking and prompt composition
- HTTP client: ollama_service/client.py shows payload building, response parsing, and code‑block stripping
- Bundle shape: blueprint_cleaner/artifacts.py → AVAILABLE_FORMATS and to_bundle() payload

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
