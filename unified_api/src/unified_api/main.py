"""Main unified API application.

Combines blueprint-cleaner and pieces copilot services under a single
FastAPI application with FastMCP integration.
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException, UploadFile
from pydantic import BaseModel

try:
    from fastapi_mcp import FastMCP
except ImportError:  # pragma: no cover - optional dependency
    FastMCP = None  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class BlueprintResponse(BaseModel):
    """Response from blueprint cleaning.

    @attr result: Cleaned blueprint text.
    @attr metadata: Basic metadata about processing.
    """

    result: str
    metadata: dict


class CopilotRequest(BaseModel):
    """Request for copilot query.

    @attr prompt: Question to ask copilot.
    """

    prompt: str


class CopilotResponse(BaseModel):
    """Response from copilot.

    @attr result: Copilot answer.
    """

    result: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    @param app: FastAPI instance.
    """
    logger.info("Unified API service starting")
    logger.info(f"Python version: {sys.version}")
    logger.info("Services: blueprint-cleaner, pieces-copilot")
    logger.info("Listening on port 8000")

    yield

    logger.info("Unified API service shutting down")


app = FastAPI(
    title="Unified Utilities API",
    description="Combined blueprint-cleaner and Pieces copilot services",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/blueprint/clean", response_model=BlueprintResponse)
async def clean_blueprint(
    file: UploadFile, format: str = Form("markdown")
) -> BlueprintResponse:
    """Clean a blueprint .COPY file.

    @param file: Uploaded .COPY file.
    @param format: Output format requested via form field.
    @return: Cleaned blueprint result.
    @raises HTTPException: On processing error.
    """
    from blueprint_cleaner.artifacts import AVAILABLE_FORMATS
    from blueprint_cleaner.pipeline import generate_blueprint_artifacts, render_output

    request_id = str(uuid.uuid4())
    logger.info(
        f"Request {request_id}: POST /blueprint/clean, file: {file.filename}, format: {format}"
    )

    try:
        content = await file.read()
        content_text = content.decode("utf-8")
        summariser = _select_summariser()
        format_choice = format.lower()
        if format_choice == "text":
            format_choice = "markdown"
        valid_formats = set(AVAILABLE_FORMATS + ["text"])
        if format_choice not in valid_formats:
            raise HTTPException(
                status_code=400, detail=f"Unsupported format '{format}'"
            )
        effective_format = "markdown" if format_choice == "text" else format_choice
        artifacts = generate_blueprint_artifacts(
            content_text,
            summariser=summariser,
        )
        result = render_output(artifacts, effective_format)

        logger.info(f"Request {request_id}: Success, output size: {len(result)} chars")

        return BlueprintResponse(
            result=result,
            metadata={
                "filename": file.filename,
                "format": format,
                "size": len(result),
                "formats": AVAILABLE_FORMATS,
                "cpp_class": artifacts.report.metadata.cpp_class_name,
            },
        )

    except Exception as exc:
        logger.error(f"Request {request_id}: Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/copilot/ask", response_model=CopilotResponse)
async def ask_copilot(request: CopilotRequest) -> CopilotResponse:
    """Ask the Pieces copilot a question.

    @param request: Copilot query.
    @return: Copilot response.
    @raises HTTPException: On copilot error.
    """
    from pieces_service.client import ask_copilot_question

    request_id = str(uuid.uuid4())
    logger.info(
        f"Request {request_id}: POST /copilot/ask, prompt length: {len(request.prompt)}, "
        f"first 200 chars: {request.prompt[:200]}"
    )

    try:
        result = ask_copilot_question(request.prompt)
        logger.info(f"Request {request_id}: Success, result size: {len(result)} chars")
        return CopilotResponse(result=result)
    except Exception as exc:
        logger.error(f"Request {request_id}: Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# Mount FastMCP
if FastMCP is not None:  # pragma: no branch - optional mounting
    mcp = FastMCP(app)
    mcp.mount()
else:
    mcp = None


def run() -> None:
    """Run the unified API using uvicorn."""

    import uvicorn

    uvicorn.run("unified_api.main:app", host="0.0.0.0", port=8000)


def _select_summariser():
    """Choose summariser callable, preferring Pieces when enabled."""

    use_pieces = os.getenv("PIECES_USE_SERVICE", "0").lower() in {"1", "true", "yes"}
    if use_pieces:
        try:
            from pieces_service.client import ask_copilot_question

            return ask_copilot_question
        except Exception as exc:  # pragma: no cover - log and fall back
            logger.warning(
                "Pieces service unavailable, falling back to stub summariser: %s", exc
            )

    def _stub(prompt: str) -> str:
        return "Generated summary unavailable in offline mode."

    return _stub
