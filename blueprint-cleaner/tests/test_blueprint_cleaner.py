"""Regression tests for blueprint-cleaner artifacts.

These specs intentionally describe the desired richer output behaviour before the
implementation exists. They should fail until the pipeline produces multi-format
artifacts, integrates Pieces-driven summarisation, and emits Unreal-ready C++.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass

import pytest

BLUEPRINT_SAMPLE = """
Begin Object Class=/Script/Engine.BlueprintGeneratedClass Name="BP_Test"
End Object

ParentClass=Class'"/Script/Engine.Actor"'
GeneratedClass=BlueprintGeneratedClass'"/Script/Engine.Actor"'

VariablesDescriptions=(FriendlyName="Health",Category="Stats",PinCategory="Float")

Begin Object Name="EventGraph"
   Schema=Class'/Script/BlueprintGraph.BPEdGraphSchema_K2'
   Nodes(0)=GraphNode'GraphNode_0'
   Begin Object Class=/Script/KismetCompiler.K2Node_FunctionEntry Name="K2Node_FunctionEntry_0"
      CustomGeneratedFunctionName="ExecuteUbergraph_BP_Test"
   End Object
   Begin Object Class=/Script/KismetCompiler.K2Node_CallFunction Name="K2Node_CallFunction_0"
      FunctionReference=(MemberParent=Class'"/Script/Engine.Actor"',MemberName="Jump")
   End Object
   Begin Object Class=/Script/KismetCompiler.K2Node_VariableGet Name="K2Node_VariableGet_0"
      VariableReference=(MemberName="Health")
   End Object
   Begin Object Class=/Script/KismetCompiler.K2Node_VariableSet Name="K2Node_VariableSet_0"
      VariableReference=(MemberName="Health")
   End Object
   Begin Object Class=/Script/BlueprintGraph.EdGraphNode_Comment Name="EdGraphNode_Comment_0"
      NodeComment="Apply jump if healthy"
   End Object
End Object
""".strip()


def make_stub_summariser():
    """Create a deterministic stub summariser for batch aggregation tests."""

    calls: list[str] = []

    def _summarise(prompt: str) -> str:
        calls.append(prompt)
        return f"<summary-{len(calls)}>"

    return _summarise, calls


def test_generate_artifacts_exposes_all_required_outputs():
    """Blueprint artifacts should expose markdown, JSON, AI summary, and C++ sources."""

    from blueprint_cleaner.pipeline import generate_blueprint_artifacts

    summariser, prompts = make_stub_summariser()
    artifacts = generate_blueprint_artifacts(
        BLUEPRINT_SAMPLE,
        summariser=summariser,
        summary_chunk_size=120,
    )

    # Structured report should remain a dataclass for introspection.
    assert is_dataclass(artifacts.report)
    assert artifacts.report.metadata.name == "BP_Test"
    assert artifacts.report.metadata.cpp_class_name == "ABP_Test"
    assert any("Health" in variable.name for variable in artifacts.report.variables)

    # Markdown and JSON outputs must be populated and consistent.
    assert "# Blueprint: BP_Test" in artifacts.markdown
    payload = json.loads(artifacts.json_text)
    assert payload["name"] == "BP_Test"
    assert payload["cpp_class"] == "ABP_Test"
    assert payload["graphs"], "Expected serialized graphs in JSON output"

    # AI summary should derive from batch prompts.
    assert artifacts.ai_summary.startswith("<summary-")
    assert len(prompts) >= 2, (
        "Rolling summary should invoke summariser for multiple batches"
    )

    # Generated C++ scaffolding must include professional UE boilerplate.
    assert artifacts.cpp_header.startswith("#pragma once")
    assert "UCLASS(" in artifacts.cpp_header
    assert "class ABP_Test" in artifacts.cpp_header
    assert artifacts.cpp_source.startswith('#include "BP_Test.h"')
    assert "void ABP_Test::" in artifacts.cpp_source
    assert artifacts.cpp_header_path == "Source/Game/BP_Test.h"
    assert artifacts.cpp_source_path == "Source/Game/BP_Test.cpp"


def test_generate_bundled_output_returns_json_bundle(tmp_path):
    """Pipeline bundle output should serialise to JSON containing C++ artifacts."""

    from blueprint_cleaner.pipeline import write_artifact_bundle

    summariser, _ = make_stub_summariser()
    bundle_path = tmp_path / "bp_test.bundle.json"

    write_artifact_bundle(
        BLUEPRINT_SAMPLE,
        output_path=str(bundle_path),
        summariser=summariser,
        summary_chunk_size=120,
    )

    bundle_text = bundle_path.read_text(encoding="utf-8")
    bundle = json.loads(bundle_text)

    assert bundle["metadata"]["name"] == "BP_Test"
    assert "bundle" in bundle["metadata"]["formats"]
    assert bundle["ai_summary"].startswith("<summary-")

    cpp_bundle = bundle["cpp"]
    assert "header" in cpp_bundle and "source" in cpp_bundle
    assert cpp_bundle["header"].startswith("#pragma once")
    assert "class ABP_Test" in cpp_bundle["header"]
    assert cpp_bundle["source"].startswith('#include "BP_Test.h"')
    assert cpp_bundle["header_path"] == "Source/Game/BP_Test.h"
    assert cpp_bundle["source_path"] == "Source/Game/BP_Test.cpp"


@pytest.mark.parametrize("chunk_size, expected_calls", [(80, 3), (400, 1)])
def test_rolling_summary_batches_respect_chunk_size(
    chunk_size: int, expected_calls: int
) -> None:
    """Rolling summaries should chunk long documents while keeping short ones single-pass."""

    from blueprint_cleaner.summaries import generate_rolling_summary

    base_doc = "\n".join(
        f"Section {idx}: Lorem ipsum dolor sit amet." for idx in range(12)
    )

    summariser, calls = make_stub_summariser()

    summary = generate_rolling_summary(
        base_doc,
        summariser=summariser,
        chunk_size=chunk_size,
    )

    assert summary.startswith("<summary-")
    assert len(calls) == expected_calls
