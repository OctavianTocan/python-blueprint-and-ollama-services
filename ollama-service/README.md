# Ollama Service

HTTP API wrapper for Ollama providing LLM query capabilities with FastMCP integration.

## Features

- **HTTP REST API**: GET/POST endpoints for Ollama queries
- **FastMCP Integration**: Optional compatibility layer for FastMCP
- **Configurable**: Models, endpoints, and generation options
- **Structured Logging**: For monitoring and debugging
- **Health Checks**: `/health` endpoint for service monitoring
- **Async Support**: Built with modern `async/await`

## Quick Start

### Installation

```bash
# Navigate to the service directory
cd ollama-service

# Install dependencies with uv
uv sync
```

### Running the Service

```bash
# Run with uvicorn
uv run uvicorn ollama_service.api:app --reload --port 4001
```

## Usage

### HTTP API

The service runs on port `4001` by default.

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
    "system": "You are a helpful assistant."
  }'
```

### Python Client

The service includes a lightweight Python client for programmatic access.

```python
from ollama_service.client import ask_ollama_question

response = ask_ollama_question(
    prompt="Explain machine learning",
    model="minimax-m2:cloud",
    system="You are a helpful assistant."
)
print(response)
```

## FastMCP Integration

If `fastmcp` is installed, the service automatically wraps the FastAPI app, making it compatible with FastMCP clients.

```python
# The following code in `api.py` enables the integration:
try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

# ...

if FastMCP is not None:
    mcp = FastMCP.from_fastapi(app=app)
```

## Configuration

### Environment Variables

- `OLLAMA_ENDPOINT`: Ollama API endpoint (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL`: Default model to use (default: `minimax-m2:cloud`)

### Request Options

- `temperature`: Controls randomness (0.0–1.0, default: 0.7)
- `num_ctx`: Token context window size (default: 2048)
- `num_predict`: Maximum tokens to generate (default: -1, unlimited)

## API Endpoints

- `GET /ollama/ask`: Ask a question via GET
- `POST /ollama/ask`: Ask a question via POST
- `GET /health`: Health check

## Dependencies

- **toolkit**: Shared utilities for text parsing, I/O, formatting
- FastAPI
- httpx
- Pydantic
- structlog
- uvicorn
- fastapi-mcp (optional)

## License

MIT
