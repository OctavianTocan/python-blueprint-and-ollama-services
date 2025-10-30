"""Integration specs for unified API blueprint endpoint.

These tests capture the intended multi-artifact response contract that bundles
markdown, JSON, AI summary, and generated C++ sources. They currently fail until
the API orchestrates the enhanced blueprint-cleaner pipeline.
"""

from __future__ import annotations

import json
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from unified_api.main import app

BLUEPRINT_SAMPLE = """
Begin Object Class=/Script/Engine.BlueprintGeneratedClass Name="BP_Test"
End Object

ParentClass=Class'"/Script/Engine.Actor"'
GeneratedClass=BlueprintGeneratedClass'"/Script/Engine.Actor"'

Begin Object Name="EventGraph"
   Schema=Class'/Script/BlueprintGraph.BPEdGraphSchema_K2'
   Nodes(0)=GraphNode'GraphNode_0'
   Begin Object Class=/Script/KismetCompiler.K2Node_FunctionEntry Name="K2Node_FunctionEntry_0"
      CustomGeneratedFunctionName="ExecuteUbergraph_BP_Test"
   End Object
   Begin Object Class=/Script/KismetCompiler.K2Node_CallFunction Name="K2Node_CallFunction_0"
      FunctionReference=(MemberParent=Class'"/Script/Engine.Actor"',MemberName="Jump")
   End Object
End Object
""".strip()


@pytest.fixture()
def client() -> TestClient:
    """Provide FastAPI test client."""

    return TestClient(app)


def test_clean_blueprint_bundle_returns_cpp_artifacts(client: TestClient) -> None:
    """Bundle responses should be JSON with AI summary and C++ header/source."""

    files = {
        "file": ("BP_Test.COPY", BytesIO(BLUEPRINT_SAMPLE.encode("utf-8")), "text/plain"),
    }

    response = client.post(
        "/blueprint/clean",
        data={"format": "bundle"},
        files=files,
    )

    assert response.status_code == 200

    payload = response.json()
    bundle = json.loads(payload["result"])

    assert bundle["metadata"]["name"] == "BP_Test"
    assert bundle["ai_summary"], "Expected AI summary in bundle response"

    cpp_bundle = bundle["cpp"]
    assert cpp_bundle["header"].startswith("#pragma once")
    assert "class ABP_Test" in cpp_bundle["header"]
    assert cpp_bundle["source"].startswith('#include "BP_Test.h"')
    assert cpp_bundle["header_path"] == "Source/Game/BP_Test.h"
    assert cpp_bundle["source_path"] == "Source/Game/BP_Test.cpp"

    assert "bundle" in payload["metadata"]["formats"]
    assert payload["metadata"]["cpp_class"] == "ABP_Test"
