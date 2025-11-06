# Ollama Service

HTTP API wrapper for Ollama providing LLM query capabilities with FastMCP integration.

## Features

- **FastAPI REST endpoints**: GET/POST for LLM queries
- **FastMCP integration**: Tool compatibility and structured interactions
- **Configurable models**: Support for any Ollama-compatible model
- **Structured logging**: Request/response monitoring with structlog
- **Health checks**: Service availability endpoints
- **Async/await**: Non-blocking request handling

## Installation

```bash
cd ollama-service
uv sync
```

## Quick Start

### Start the API Server

```bash
# Development mode with auto-reload
uv run -m uvicorn ollama_service.api:app --reload --port 4001

# Production mode
uv run -m uvicorn ollama_service.api:app --host 0.0.0.0 --port 4001
```

**Note:** On Windows, use `uv run -m uvicorn` instead of `uv run uvicorn` to avoid "Failed to canonicalize script path" errors.

The service will be available at `http://localhost:4001`.

### Using the HTTP API

#### Health Check

```bash
curl http://localhost:4001/health
```

#### GET Request

```bash
curl "http://localhost:4001/ollama/ask?prompt=Hello%20world&model=minimax-m2:cloud"
```

#### POST Request

```bash
curl -X POST "http://localhost:4001/ollama/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "model": "minimax-m2:cloud",
    "system": "You are a helpful assistant.",
    "options": {
      "temperature": 0.7,
      "num_ctx": 2048
    }
  }'
```

### Python Client

```python
from ollama_service.client import ask_ollama_question

response = ask_ollama_question(
    prompt="Explain machine learning",
    model="minimax-m2:cloud",
    system="You are a helpful assistant."
)
print(response)
```

## Configuration

### Environment Variables

- `OLLAMA_ENDPOINT`: Ollama API endpoint (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL`: Default model to use (default: `minimax-m2:cloud`)

### Request Options

All generation options supported by Ollama can be passed via the `options` field:

- `temperature`: Controls randomness (0.0-1.0, default: 0.7)
- `num_ctx`: Token context window size (default: 2048)
- `num_predict`: Maximum tokens to generate (default: -1, unlimited)
- `top_k`: Top-k sampling parameter
- `top_p`: Top-p (nucleus) sampling parameter

See [Ollama API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md) for complete options.

## API Endpoints

### POST /ollama/ask

Ask a question to the LLM with full configuration options.

**Request Body:**

```json
{
  "prompt": "string (required)",
  "model": "string (optional)",
  "system": "string (optional)",
  "options": {
    "temperature": 0.7,
    "num_ctx": 2048
  }
}
```

**Response:**

```json
{
  "response": "string"
}
```

### GET /ollama/ask

Simplified query interface using URL parameters.

**Query Parameters:**

- `prompt` (required): The question to ask
- `model` (optional): Override default model
- `system` (optional): System prompt

**Response:**

```json
{
  "response": "string"
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

## FastMCP Integration

The service is designed for FastMCP compatibility, making it easy to expose as MCP tools.

For FastMCP integration examples, see:

- [FastMCP + FastAPI Integration](https://gofastmcp.com/integrations/fastapi)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Local Development

```bash
# Install with dev dependencies
uv sync

# Run with auto-reload
uv run -m uvicorn ollama_service.api:app --reload --port 4001

# Check logs for request/response monitoring
```

## Project Structure

```
ollama-service/
├── src/ollama_service/
│   ├── __init__.py
│   ├── api.py              # FastAPI application and endpoints
│   ├── client.py           # HTTP client for Ollama API
│   ├── models.py           # Pydantic request/response models
│   └── logging_config.py   # Structured logging setup
├── tests/
│   └── test_ollama_service.py
├── pyproject.toml
└── README.md
```

## Dependencies

- **FastAPI**: Modern web framework for APIs
- **httpx**: Async HTTP client
- **Pydantic**: Data validation and serialization
- **structlog**: Structured logging
- **uvicorn**: ASGI server
- **FastMCP**: MCP integration (optional)

## Architecture

The service follows a clean, modular design:

1. **API Layer** (`api.py`): FastAPI routes and endpoint definitions
2. **Client Layer** (`client.py`): HTTP communication with Ollama
3. **Models** (`models.py`): Pydantic schemas for request/response validation
4. **Logging** (`logging_config.py`): Centralized structured logging setup

## License

MIT
