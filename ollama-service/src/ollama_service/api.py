"""FastAPI application for Ollama service.

Provides HTTP endpoints (GET/POST) and FastMCP integration for Ollama queries.
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .client import ask_ollama_question
from .logging_config import configure_logging, get_logger
from .models import OllamaRequest, OllamaResponse

# Optional FastMCP integration
try:
    from fastapi_mcp import FastMCP
except ImportError:
    FastMCP = None

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events.

    @param app: FastAPI application instance.
    """
    # Startup
    logger.info("Ollama service starting up")
    logger.info(f"Python version: {sys.version}")
    logger.info("Default Ollama endpoint: http://localhost:11434/api/generate")
    logger.info("Listening on port 4001")

    yield

    # Shutdown
    logger.info("Ollama service shutting down")


app = FastAPI(
    title="Ollama Service",
    description="HTTP wrapper for Ollama API",
    lifespan=lifespan,
)


@app.post("/ollama/ask", response_model=OllamaResponse)
async def post_ask(request: OllamaRequest) -> OllamaResponse:
    """Ask Ollama a question via POST request.

    @param request: Request containing the prompt and options.
    @return: Response with Ollama result.
    @raises HTTPException: On Ollama error.
    """
    request_id = str(uuid.uuid4())
    prompt = request.prompt
    logger.info(
        f"Request {request_id}: POST /ollama/ask, model: {request.model}, "
        f"prompt length: {len(prompt)}, first 200 chars: {prompt[:200]}"
    )

    try:
        result = ask_ollama_question(
            prompt=prompt,
            model=request.model,
            system=request.system,
            options=request.options,
            endpoint=request.endpoint or "http://localhost:11434/api/generate",
            headers=request.headers,
        )
        
        logger.info(f"Request {request_id}: Success, result size: {len(result)} chars")
        return OllamaResponse(
            result=result,
            model=request.model,
            done=True,
            metadata={"request_id": request_id}
        )
    except Exception as exc:
        logger.error(f"Request {request_id}: Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/ollama/ask", response_model=OllamaResponse)
async def get_ask(
    prompt: str,
    model: str = "llama2",
    system: str | None = None,
) -> OllamaResponse:
    """Ask Ollama a question via GET request.

    @param prompt: Question query parameter.
    @param model: Model name (default: llama2).
    @param system: Optional system prompt.
    @return: Response with Ollama result.
    @raises HTTPException: On Ollama error.
    """
    request_id = str(uuid.uuid4())
    logger.info(
        f"Request {request_id}: GET /ollama/ask, model: {model}, "
        f"prompt length: {len(prompt)}, first 200 chars: {prompt[:200]}"
    )

    try:
        result = ask_ollama_question(
            prompt=prompt,
            model=model,
            system=system,
        )
        
        logger.info(f"Request {request_id}: Success, result size: {len(result)} chars")
        return OllamaResponse(
            result=result,
            model=model,
            done=True,
            metadata={"request_id": request_id}
        )
    except Exception as exc:
        logger.error(f"Request {request_id}: Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    @return: Health status.
    """
    return {"status": "healthy", "service": "ollama-service"}


# Mount FastMCP server if available
if FastMCP is not None:
    mcp = FastMCP(app)
    mcp.mount()
