"""Output rendering orchestration for blueprint artifacts."""

from __future__ import annotations

import commentjson

from .artifacts import BlueprintArtifacts


def render_output(artifacts: BlueprintArtifacts, format_type: str) -> str:
    """Render blueprint artifacts in the requested format."""

    fmt = format_type.lower()
    if fmt == "json":
        return artifacts.json_text
    if fmt == "bundle":
        return commentjson.dumps(artifacts.to_bundle(), indent=2)
    if fmt == "summary":
        return artifacts.ai_summary
    if fmt == "cpp-header":
        return artifacts.cpp_header
    if fmt == "cpp-source":
        return artifacts.cpp_source
    return artifacts.markdown
