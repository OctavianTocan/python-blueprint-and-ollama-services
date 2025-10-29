# Unified Utilities API

Combined FastAPI service exposing both `blueprint-cleaner` and `pieces-service` under a single endpoint with FastMCP integration.

## Features

- **Blueprint cleaning**: Upload .COPY files and receive AI-ready summaries
- **Copilot queries**: Ask the Pieces copilot programming questions
- **FastMCP integration**: Model Context Protocol support
- **Unified interface**: Single service for all utility operations

## Quick Start

```bash
cd unified_api
uv sync
uv run uvicorn unified_api.main:app --reload --port 8000
```

## Endpoints

### POST /blueprint/clean

Upload and clean a blueprint file.

```bash
curl -X POST http://localhost:8000/blueprint/clean \
  -F "file=@blueprint.COPY" \
  -F "format=markdown"
```

Response:

```json
{
  "result": "# Blueprint: MyBlueprint\n...",
  "metadata": {
    "filename": "blueprint.COPY",
    "format": "markdown",
    "size": 2048
  }
}
```

### POST /copilot/ask

Query the Pieces copilot.

```bash
curl -X POST http://localhost:8000/copilot/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How do I use async/await in Python?"}'
```

Response:

```json
{
  "result": "Async/await in Python allows you to write concurrent code..."
}
```

## Architecture

The unified API acts as a facade over two specialized services:

1. **blueprint-cleaner**: Parses UE5 blueprint files
2. **pieces-service**: Wraps Pieces SDK copilot

All endpoints use FastAPI with FastMCP for MCP protocol support.

## Dependencies

- **fastapi**: Web framework
- **fastapi-mcp**: MCP integration
- **uvicorn**: ASGI server
- **python-multipart**: File upload support
- **blueprint-cleaner**: Blueprint processing (local)
- **pieces-service**: Copilot wrapper (local)

## License

MIT
