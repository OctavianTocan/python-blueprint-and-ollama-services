# Pieces Service

HTTP API wrapper for the Pieces SDK Copilot, providing simple GET/POST endpoints and FastMCP integration for AI-powered code assistance.

## Features

- **Dual interfaces**: REST API (GET/POST) and FastMCP for flexible integration
- **Streaming responses**: Real-time copilot answers
- **Clean architecture**: Modular design with focused single-purpose functions
- **Request logging**: UUID-tracked requests with detailed metrics

## Quick Start

```bash
# Install dependencies
cd pieces_service
uv sync

# Run the service
uv run uvicorn pieces_service.api:app --reload --port 4000
```

## API Endpoints

### POST /copilot/ask

Send a question to the Pieces copilot.

```bash
curl -X POST http://localhost:4000/copilot/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How do I reverse a list in Python?"}'
```

Response:

```json
{
  "result": "You can reverse a list using .reverse() method or [::-1] slicing..."
}
```

### GET /copilot/ask

Query via URL parameter:

```bash
curl "http://localhost:4000/copilot/ask?prompt=Explain+async+await+in+Python"
```

## Project Structure

```
pieces_service/
├── src/pieces_service/
│   ├── api.py              # FastAPI application and endpoints
│   ├── client.py           # Pieces SDK wrapper
│   ├── models.py           # Pydantic request/response models
│   ├── logging_config.py   # Logging setup
│   └── __init__.py
├── data/
│   ├── in/                 # Input data (if needed)
│   └── out/                # Output logs/responses
├── app/                    # Legacy compatibility (deprecated)
└── README.md
```

## Architecture

### Client Layer (`client.py`)

Thin wrapper around Pieces SDK:

- `ask_copilot_question`: Main entry point
- `stream_copilot_response`: Handle SDK streaming
- `strip_markdown_code_blocks`: Clean response formatting

### API Layer (`api.py`)

FastAPI application with:

- Lifespan management for startup/shutdown
- Request logging with UUIDs
- Error handling and HTTP exceptions
- FastMCP integration

### Models (`models.py`)

Pydantic validation for:

- `AskRequest`: Incoming prompts
- `AskResponse`: Copilot results

## Dependencies

- **fastapi**: Web framework
- **fastapi-mcp**: MCP protocol integration
- **uvicorn**: ASGI server
- **pieces_os_client**: Pieces SDK
- **pydantic**: Data validation

## Development

All code follows clean code principles:

- Functions < 20 lines
- Single responsibility per function
- Comprehensive Doxygen documentation
- Clear separation of concerns

## License

MIT
