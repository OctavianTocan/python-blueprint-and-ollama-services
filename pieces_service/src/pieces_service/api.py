"""FastAPI application for Pieces copilot service.

Provides HTTP endpoints (GET/POST) and FastMCP integration for copilot queries.
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastMCP

from .client import ask_copilot_question
from .logging_config import configure_logging, get_logger
from .models import AskRequest, AskResponse

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events.

    @param app: FastAPI application instance.
    """
    # Startup
    logger.info("Copilot service starting up")
    logger.info(f"Python version: {sys.version}")
    log_pieces_sdk_version()
    logger.info("Listening on port 4000")

    yield

    # Shutdown
    logger.info("Copilot service shutting down")


def log_pieces_sdk_version() -> None:
    """Log Pieces SDK version if available."""
    try:
        import pieces_os_client

        version = getattr(pieces_os_client, "__version__", "unknown")
        logger.info(f"pieces_os_client version: {version}")
    except ImportError:
        logger.info("pieces_os_client version: not available")


app = FastAPI(
    title="Copilot Service",
    description="HTTP wrapper for Pieces SDK Copilot",
    lifespan=lifespan,
)


@app.post("/copilot/ask", response_model=AskResponse)
async def post_ask(request: AskRequest) -> AskResponse:
    """Ask copilot a question via POST request.

    @param request: Request containing the prompt.
    @return: Response with copilot result.
    @raises HTTPException: On copilot error.
    """
    request_id = str(uuid.uuid4())
    prompt = request.prompt
    logger.info(
        f"Request {request_id}: POST /copilot/ask, prompt length: {len(prompt)}, "
        f"first 200 chars: {prompt[:200]}"
    )

    try:
        result = ask_copilot_question(prompt)
        logger.info(f"Request {request_id}: Success, result size: {len(result)} chars")
        return AskResponse(result=result)
    except Exception as exc:
        logger.error(f"Request {request_id}: Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/copilot/ask", response_model=AskResponse)
async def get_ask(prompt: str) -> AskResponse:
    """Ask copilot a question via GET request.

    @param prompt: Question query parameter.
    @return: Response with copilot result.
    @raises HTTPException: On copilot error.
    """
    request_id = str(uuid.uuid4())
    logger.info(
        f"Request {request_id}: GET /copilot/ask, prompt length: {len(prompt)}, "
        f"first 200 chars: {prompt[:200]}"
    )

    try:
        result = ask_copilot_question(prompt)
        logger.info(f"Request {request_id}: Success, result size: {len(result)} chars")
        return AskResponse(result=result)
    except Exception as exc:
        logger.error(f"Request {request_id}: Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# Mount FastMCP server
mcp = FastMCP(app)
mcp.mount()
