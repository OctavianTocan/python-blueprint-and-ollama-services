#!/usr/bin/env python3
"""
FastAPI application for the copilot service.

Provides HTTP endpoints to ask questions to the Pieces copilot.
"""

import logging
import sys
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel

from .copilot import ask_copilot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    """Request model for the ask endpoint."""

    prompt: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Copilot service starting up")
    logger.info(f"Python version: {sys.version}")
    try:
        import pieces_os_client

        version = getattr(pieces_os_client, "__version__", "unknown")
        logger.info(f"pieces_os_client version: {version}")
    except ImportError:
        logger.info("pieces_os_client version: not available")
    logger.info("Listening on port 4000")

    yield

    # Shutdown (if needed in the future)
    logger.info("Copilot service shutting down")


app = FastAPI(
    title="Copilot Service",
    description="HTTP wrapper for Pieces SDK Copilot",
    lifespan=lifespan,
)


@app.post("/copilot/ask")
async def post_ask(request: AskRequest) -> dict:
    """
    Ask the copilot a question via POST request.

    Args:
        request: The request containing the prompt.

    Returns:
        A dictionary with the result.
    """
    request_id = str(uuid.uuid4())
    prompt = request.prompt
    logger.info(
        f"Request {request_id}: POST /copilot/ask, prompt length: {len(prompt)}, "
        f"first 200 chars: {prompt[:200]}"
    )

    try:
        result = ask_copilot(prompt)
        logger.info(f"Request {request_id}: Success, result size: {len(result)} chars")
        return {"result": result}
    except Exception as e:
        logger.error(f"Request {request_id}: Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/copilot/ask")
async def get_ask(prompt: str) -> dict:
    """
    Ask the copilot a question via GET request.

    Args:
        prompt: The prompt query parameter.

    Returns:
        A dictionary with the result.
    """
    request_id = str(uuid.uuid4())
    logger.info(
        f"Request {request_id}: GET /copilot/ask, prompt length: {len(prompt)}, "
        f"first 200 chars: {prompt[:200]}"
    )

    try:
        result = ask_copilot(prompt)
        logger.info(f"Request {request_id}: Success, result size: {len(result)} chars")
        return {"result": result}
    except Exception as e:
        logger.error(f"Request {request_id}: Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Create and mount the MCP server
mcp = FastApiMCP(app)
mcp.mount()
