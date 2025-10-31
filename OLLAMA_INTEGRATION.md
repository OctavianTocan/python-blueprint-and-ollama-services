# Ollama Service Integration

This document describes the integration of the Ollama service with the blueprint-cleaner, providing an alternative to the Pieces SDK for AI-powered blueprint summarization.

## Overview

The implementation creates a new `ollama_service` module that mirrors the architecture of the existing `pieces_service`:

- **HTTP API Wrapper**: FastAPI application with GET/POST endpoints
- **Client Library**: Python client for direct integration
- **FastMCP Support**: Optional integration for tool compatibility
- **Service Selection**: Blueprint-cleaner can now choose between Pieces and Ollama

## Architecture

### Ollama Service Structure

```
ollama_service/
├── src/ollama_service/
│   ├── __init__.py          # Package initialization
│   ├── client.py            # HTTP client wrapper (port of C++ FOllamaClient)
│   ├── api.py              # FastAPI application with endpoints
│   ├── models.py           # Pydantic request/response models
│   └── logging_config.py  # Structured logging configuration
├── tests/
│   └── test_ollama_service.py  # Comprehensive unit tests
├── pyproject.toml          # Project configuration
└── README.md              # Service documentation
```

### Key Components

#### Client (`client.py`)
- `ask_ollama_question()`: Main interface for sending prompts
- `build_ollama_payload()`: Constructs JSON payload for Ollama API
- `parse_ollama_response()`: Extracts response content from API
- `strip_markdown_code_blocks()`: Cleans response formatting
- `validate_ollama_request()`: Validates input parameters

#### API (`api.py`)
- `GET /ollama/ask`: Simple query interface
- `POST /ollama/ask`: Advanced request with full options
- `GET /health`: Health check endpoint
- FastMCP integration (optional)

#### Models (`models.py`)
- `OllamaRequest`: Request configuration with validation
- `OllamaResponse`: Response structure with metadata
- `OllamaOptions`: Generation parameters (temperature, context, etc.)

## Integration with Blueprint-Cleaner

### Service Selection

The blueprint-cleaner now supports choosing the AI service:

```bash
# Use Pieces (default)
blueprint-cleaner input.copy

# Use Ollama
blueprint-cleaner input.copy -s ollama

# Explicit Pieces
blueprint-cleaner input.copy -s pieces
```

### Pipeline Integration

The `pipeline.py` module has been updated:

```python
def _default_summariser(service: str = "pieces") -> SummaryFn:
    """Create a summariser callable based on service choice."""
    if service == "ollama":
        from ollama_service.client import ask_ollama_question
        return ask_ollama_question
    
    # Default to pieces
    from pieces_service.client import ask_copilot_question
    return ask_copilot_question
```

### Configuration Updates

- `blueprint-cleaner/pyproject.toml`: Added `ollama-service` dependency
- CLI argument `-s/--service`: Choose between "pieces" and "ollama"
- Updated examples to demonstrate service selection

## Usage Examples

### Direct Ollama Service Usage

```python
from ollama_service.client import ask_ollama_question

# Basic usage
response = ask_ollama_question("Explain Unreal Engine blueprints")

# Advanced usage with options
response = ask_ollama_question(
    prompt="Analyze this blueprint code",
    model="codellama",
    system="You are a UE5 expert.",
    options=OllamaOptions(
        temperature=0.3,
        num_ctx=4096
    )
)
```

### HTTP API Usage

```bash
# GET request
curl "http://localhost:4001/ollama/ask?prompt=Hello&model=llama2"

# POST request
curl -X POST "http://localhost:4001/ollama/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain this blueprint",
    "model": "codellama",
    "options": {
      "temperature": 0.7,
      "num_ctx": 2048
    }
  }'
```

### Blueprint-Cleaner Integration

```bash
# Process with Ollama
blueprint-cleaner BP_Character.COPY -s ollama -o summary.md -f summary

# Debug mode with Ollama
blueprint-cleaner BP_Character.COPY -s ollama -d

# Generate C++ code using Ollama for summarization
blueprint-cleaner BP_Character.COPY -s ollama -f cpp-header
```

## Installation and Setup

### Prerequisites

1. **Ollama Installation**: Install and run Ollama locally
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   
   # Pull a model
   ollama pull llama2
   ```

2. **Python Environment**: Ensure Python 3.13+ with required dependencies

### Development Installation

```bash
# Install ollama-service
cd ollama_service
pip install -e .

# Install updated blueprint-cleaner
cd ../blueprint-cleaner
pip install -e .
```

### Running the Services

```bash
# Start Ollama (terminal 1)
ollama serve

# Start Ollama HTTP service (terminal 2)
ollama-service

# Use blueprint-cleaner (terminal 3)
blueprint-cleaner input.copy -s ollama
```

## Configuration

### Environment Variables

- `OLLAMA_ENDPOINT`: Custom Ollama API endpoint (default: `http://localhost:11434/api/generate`)
- `OLLAMA_MODEL`: Default model to use (default: `llama2`)

### Service Defaults

| Parameter | Pieces Service | Ollama Service |
|------------|----------------|-----------------|
| Default Model | Pieces OS default | `llama2` |
| Endpoint | Pieces SDK | `http://localhost:11434/api/generate` |
| Port | 4000 | 4001 |
| Temperature | N/A | 0.7 |
| Context Window | N/A | 2048 tokens |

## Testing

### Unit Tests

```bash
cd ollama_service
python -m pytest tests/ -v
```

### Integration Tests

```bash
# Run comprehensive integration test
python test_integration.py
```

### Manual Testing

```bash
# Test Ollama service directly
curl "http://localhost:4001/ollama/ask?prompt=Hello"

# Test blueprint-cleaner integration
blueprint-cleaner test_data/sample.COPY -s ollama -d
```

## Migration from Pieces to Ollama

### Advantages of Ollama

1. **Local Processing**: No external API dependencies
2. **Cost Control**: No per-request pricing
3. **Privacy**: Data stays on local machine
4. **Model Choice**: Support for various open-source models
5. **Offline Capability**: Works without internet connection

### Considerations

1. **Resource Usage**: Requires sufficient RAM/CPU for models
2. **Model Quality**: May vary compared to commercial services
3. **Setup Complexity**: Requires local Ollama installation
4. **Performance**: Dependent on hardware capabilities

### Migration Steps

1. **Install Ollama**: Set up local Ollama service
2. **Pull Models**: Download desired models (`ollama pull llama2`)
3. **Update Workflows**: Add `-s ollama` to blueprint-cleaner commands
4. **Validate Results**: Compare output quality with Pieces service
5. **Configure Models**: Choose optimal models for specific tasks

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure Ollama is running (`ollama serve`)
2. **Model Not Found**: Pull required model (`ollama pull <model>`)
3. **Memory Errors**: Use smaller models or increase system RAM
4. **Import Errors**: Verify package installation with `-e` flag

### Debug Commands

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check Ollama service health
curl http://localhost:4001/health

# Test with debug mode
blueprint-cleaner input.copy -s ollama -d
```

## Future Enhancements

1. **Model Auto-detection**: Automatically select best model based on content
2. **Batch Processing**: Handle multiple blueprints efficiently
3. **Streaming Support**: Real-time response streaming for long content
4. **Model Fine-tuning**: Custom models for blueprint analysis
5. **Performance Optimization**: Caching and parallel processing

## License

Copyright 2024, Spec-Driven AI, All Rights Reserved.
