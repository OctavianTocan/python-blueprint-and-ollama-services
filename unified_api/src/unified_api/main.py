"""Main unified API application.

Combines blueprint-cleaner and pieces copilot services under a single
FastAPI application with FastMCP integration.
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi_mcp import FastMCP
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class BlueprintRequest(BaseModel):
    """Request for blueprint cleaning operation.

    @attr format: Output format (markdown or json).
    """

    format: str = "markdown"


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
async def clean_blueprint(file: UploadFile, request: BlueprintRequest = BlueprintRequest()) -> BlueprintResponse:
    """Clean a blueprint .COPY file.

    @param file: Uploaded .COPY file.
    @param request: Format options.
    @return: Cleaned blueprint result.
    @raises HTTPException: On processing error.
    """
    from blueprint_cleaner.pipeline import clean_blueprint_file
    import tempfile

    request_id = str(uuid.uuid4())
    logger.info(f"Request {request_id}: POST /blueprint/clean, file: {file.filename}, format: {request.format}")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".COPY") as tmp_in:
            content = await file.read()
            tmp_in.write(content)
            tmp_in_path = tmp_in.name

        # Process blueprint
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{request.format}") as tmp_out:
            tmp_out_path = tmp_out.name

        success = clean_blueprint_file(tmp_in_path, tmp_out_path, format_type=request.format)

        if not success:
            raise RuntimeError("Blueprint processing failed")

        # Read result
        with open(tmp_out_path, "r", encoding="utf-8") as f:
            result = f.read()

        # Cleanup
        Path(tmp_in_path).unlink(missing_ok=True)
        Path(tmp_out_path).unlink(missing_ok=True)

        logger.info(f"Request {request_id}: Success, output size: {len(result)} chars")

        return BlueprintResponse(
            result=result,
            metadata={
                "filename": file.filename,
                "format": request.format,
                "size": len(result),
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
mcp = FastMCP(app)
mcp.mount()
