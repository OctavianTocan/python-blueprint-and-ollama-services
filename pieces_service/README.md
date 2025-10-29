# Pieces Copilot Service

This is a minimal HTTP wrapper around the Pieces SDK Copilot functionality. It provides a simple FastAPI service that exposes the copilot's `ask` capability via HTTP endpoints.

## Features

- Synchronous `ask` API for querying the Pieces copilot
- Automatic host discovery for Pieces OS server
- Clear logging for observability and debugging
- Docker containerized for easy deployment

## Endpoints

- `POST /copilot/ask` - JSON body: `{"prompt": "..."}` - Response: `{"result": "..."}`
- `GET /copilot/ask?prompt=...` - Convenience GET endpoint returning same JSON shape

## Build and Run

### Build

```bash
docker build -t pieces-copilot-service pieces_service/
```

### Run (Windows Docker Desktop)

```bash
docker run --rm -p 4000:4000 pieces-copilot-service
```

### Example Usage

POST request:

```bash
curl -X POST http://localhost:4000/copilot/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is the capital of France?"}'
```

GET request:

```bash
curl "http://localhost:4000/copilot/ask?prompt=What%20is%20the%20capital%20of%20France%3F"
```

## Connectivity Notes

The service attempts to connect to a Pieces OS server running on the host machine. It tries the following hosts in order:

1. `http://host.docker.internal:1000` (Windows Docker Desktop default)
2. `http://host.docker.internal:5323` (Linux Docker Desktop default)
3. `http://localhost:1000`
4. `http://localhost:5323`

### Requirements

- Pieces OS must be running and exposing an HTTP endpoint on the host
- For Docker Desktop on Windows, `host.docker.internal` should resolve to the host
- If `host.docker.internal` doesn't work in your environment, try:

```bash
docker run --rm -p 4000:4000 --add-host=host.docker.internal:host-gateway pieces-copilot-service
```

### Troubleshooting

- Ensure Pieces OS is running and accessible
- Check the service logs for host discovery attempts and errors
- If Pieces OS uses a different port, the service may need modification
- The service assumes Pieces OS exposes an HTTP API; if it only uses local IPC/sockets, additional configuration is required

## Dependencies

- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `pieces_os_client` - Pieces SDK client
- `pydantic` - Data validation

## Logging

The service logs all requests, host discovery attempts, SDK interactions, and errors to stdout with timestamps and request IDs for correlation.