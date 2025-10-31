# Ollama Service

HTTP API wrapper for Ollama providing LLM query capabilities with FastMCP integration.

## Features

- HTTP REST API (GET/POST endpoints)
- FastMCP integration for tool compatibility
- Configurable models and generation options
- Structured logging and monitoring
- Health check endpoints
- Async/await support

## Installation

```bash
pip install -e .
```

## Usage

### CLI

Start the service:

```bash
ollama-service
```

### HTTP API

The service runs on port 4001 by default.

#### GET Request

```bash
curl "http://localhost:4001/ollama/ask?prompt=Hello%20world&model=llama2"
```

#### POST Request

```bash
curl -X POST "http://localhost:4001/ollama/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "model": "llama2",
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
    model="llama2",
    system="You are a helpful assistant."
)
print(response)
```

## Configuration

### Environment Variables

- `OLLAMA_ENDPOINT`: Ollama API endpoint (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL`: Default model to use (default: `llama2`)

### Request Options

- `temperature`: Controls randomness (0.0-1.0, default: 0.7)
- `num_ctx`: Token context window size (default: 2048)
- `num_predict`: Maximum tokens to generate (default: -1, unlimited)

## API Endpoints

- `GET /ollama/ask` - Ask a question via GET
- `POST /ollama/ask` - Ask a question via POST
- `GET /health` - Health check

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Local Development

```bash
pip install -e ".[dev]"
uvicorn ollama_service.api:app --reload --port 4001
```

## Dependencies

- FastAPI
- httpx
- Pydantic
- structlog
- uvicorn
- fastapi-mcp (optional)

## License

Copyright 2024, Spec-Driven AI, All Rights Reserved.
