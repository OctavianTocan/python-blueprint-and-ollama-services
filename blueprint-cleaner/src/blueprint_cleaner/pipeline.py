"""Public service entry points for blueprint cleaning."""

from __future__ import annotations

import json
import os
import traceback
from typing import Callable, Optional

from ollama_service import generate_rolling_summary
from toolkit.console import print_processing_header, print_success_footer

from .artifacts import BlueprintArtifacts
from .formatters.json_output import render_json_output
from .formatters.markdown import format_as_markdown
from .formatters.unreal_cpp import generate_unreal_cpp
from .io_utils import print_report_summary, read_text_file, write_text_file
from .report import build_blueprint_report

SummaryFn = Callable[[str], str]


def generate_blueprint_artifacts(
    content: str,
    summariser: Optional[SummaryFn] = None,
    summary_chunk_size: int = 4000,
    debug: bool = False,
) -> BlueprintArtifacts:
    """Produce all derived outputs for a blueprint."""

    report = build_blueprint_report(content, debug)
    markdown = format_as_markdown(report)
    json_text = render_json_output(report)

    cpp = generate_unreal_cpp(report)
    summary = generate_rolling_summary(
        markdown,
        summariser or _default_summariser(),
        chunk_size=summary_chunk_size,
    )

    return BlueprintArtifacts(
        report=report,
        markdown=markdown,
        json_text=json_text,
        ai_summary=summary,
        cpp_header=cpp.header,
        cpp_source=cpp.source,
        cpp_header_path=cpp.header_path,
        cpp_source_path=cpp.source_path,
        functions=report.functions,
    )


def write_artifact_bundle(
    content: str,
    output_path: str,
    summariser: Optional[SummaryFn] = None,
    summary_chunk_size: int = 4000,
    debug: bool = False,
) -> None:
    """Generate artifacts and write bundle to disk."""

    artifacts = generate_blueprint_artifacts(
        content,
        summariser=summariser,
        summary_chunk_size=summary_chunk_size,
        debug=debug,
    )
    bundle_text = json.dumps(artifacts.to_bundle(), indent=2)
    write_text_file(output_path, bundle_text)


def render_output(artifacts: BlueprintArtifacts, format_type: str) -> str:
    """Route to appropriate formatter based on format type."""

    fmt = format_type.lower()
    if fmt == "json":
        return artifacts.json_text
    if fmt == "bundle":
        return json.dumps(artifacts.to_bundle(), indent=2)
    if fmt == "summary":
        return artifacts.ai_summary
    if fmt == "cpp-header":
        return artifacts.cpp_header
    if fmt == "cpp-source":
        return artifacts.cpp_source
    return artifacts.markdown


def clean_blueprint_file(
    input_file: str,
    output_file: str,
    chunk_size: int = 4000,
    format_type: str = "markdown",
    debug: bool = False,
    summariser: Optional[SummaryFn] = None,
) -> bool:
    """Generate AI-focused summary for a UE5 blueprint file."""

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False

    print_processing_header(input_file, output_file, format_type)

    try:
        content = read_text_file(input_file)
        artifacts = generate_blueprint_artifacts(
            content,
            summariser=summariser or _default_summariser(),
            summary_chunk_size=chunk_size,
            debug=debug,
        )

        output_text = render_output(artifacts, format_type)
        write_text_file(output_file, output_text)
        print_report_summary(artifacts.report)
        print_success_footer(output_file)
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error processing file: {exc}")
        traceback.print_exc()
        return False


def _default_summariser() -> SummaryFn:
    """Create a summariser callback using the default LLM service.
    @return: Summariser function.
    """
    from ollama_service.client import ask_ollama_question
    from ollama_service.models import OllamaOptions

    # Keep the summary concise and cost-effective by limiting generation.
    # Tests assert this budget to be 320 tokens.
    options = OllamaOptions(num_predict=320)

    def _summarise(prompt: str) -> str:
        # TODO: This throws out an error
        return ask_ollama_question(prompt, options=options)

    return _summarise
