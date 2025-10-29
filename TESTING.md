# Testing Roadmap

Tests are scaffolded but intentionally not enforced yet. When ready to implement:

## Test Categories

### Blueprint Cleaner

- [ ] Variable parsing
- [ ] Graph extraction
- [ ] Node analysis
- [ ] Format rendering (markdown, JSON)
- [ ] I/O encoding handling

### Pieces Service

- [ ] Client wrapper functions
- [ ] API endpoints (GET/POST)
- [ ] Error handling
- [ ] Response formatting

### Unified API

- [ ] Blueprint upload and processing
- [ ] Copilot query forwarding
- [ ] FastMCP integration
- [ ] Multi-service orchestration

## Framework

Use `pytest` with:

- `pytest-asyncio` for async tests
- `httpx` or `TestClient` for API testing
- Fixtures for common setup

## Running Tests

```bash
# When tests are implemented:
pytest tests/
pytest tests/ -v           # Verbose
pytest tests/ -k "pattern" # Filter by pattern
```

## Coverage

Target 80%+ coverage for critical paths:

- Parsers and extraction logic
- API endpoints
- Error handling flows
