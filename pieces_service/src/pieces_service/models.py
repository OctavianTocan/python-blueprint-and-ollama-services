"""Request/response models for Pieces API.

Defines Pydantic models for API contract validation.
"""

from __future__ import annotations

from pydantic import BaseModel


class AskRequest(BaseModel):
    """Request model for copilot ask endpoint.

    @attr prompt: Question or prompt to send to copilot.
    """

    prompt: str


class AskResponse(BaseModel):
    """Response model for copilot ask endpoint.

    @attr result: Copilot response text.
    """

    result: str
