"""Generate Unreal Engine C++ scaffolding from blueprint reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from ..models import BlueprintReport, FunctionSynopsis


@dataclass
class CppArtifacts:
    """Container for generated header and source text."""

    header: str
    source: str


def generate_unreal_cpp(report: BlueprintReport) -> CppArtifacts:
    """Produce Unreal-friendly header and source snippets."""

    class_name = _derive_class_name(report.metadata.name, report.metadata.parent_class)
    header_includes = _gather_header_includes(report.metadata.parent_class)
    header_text = _build_header(report, class_name, header_includes)
    source_text = _build_source(report, class_name)
    return CppArtifacts(header=header_text, source=source_text)


def _derive_class_name(name: str, parent_class: str | None) -> str:
    """Infer Unreal class name prefix from parent class."""

    prefix = "U"
    if parent_class:
        if parent_class.endswith("Actor"):
            prefix = "A"
        elif parent_class.endswith("Component"):
            prefix = "U"
        elif parent_class.endswith("Widget"):
            prefix = "U"
        elif parent_class.endswith("Controller"):
            prefix = "A"
    return f"{prefix}{name}" if not name.startswith(prefix) else name


def _gather_header_includes(parent_class: str | None) -> List[str]:
    """Select engine headers based on parent class."""

    includes = ["CoreMinimal.h"]

    include_map = {
        "Actor": "GameFramework/Actor.h",
        "Character": "GameFramework/Character.h",
        "PlayerController": "GameFramework/PlayerController.h",
        "Pawn": "GameFramework/Pawn.h",
        "ActorComponent": "Components/ActorComponent.h",
        "SceneComponent": "Components/SceneComponent.h",
        "UserWidget": "Blueprint/UserWidget.h",
    }

    if parent_class:
        for suffix, header in include_map.items():
            if parent_class.endswith(suffix):
                includes.append(header)
                break

    return includes


def _resolve_parent_cpp_class(parent_class: str | None) -> str:
    """Map blueprint parent class to Unreal C++ type."""

    if not parent_class:
        return "AActor"

    mapping = {
        "Actor": "AActor",
        "Character": "ACharacter",
        "Pawn": "APawn",
        "PlayerController": "APlayerController",
        "ActorComponent": "UActorComponent",
        "SceneComponent": "USceneComponent",
        "UserWidget": "UUserWidget",
    }

    for suffix, cpp_name in mapping.items():
        if parent_class.endswith(suffix):
            return cpp_name

    return parent_class


def _build_header(report: BlueprintReport, class_name: str, includes: Sequence[str]) -> str:
    """Compose header file text."""

    lines: List[str] = ["#pragma once", ""]
    for include in includes:
        lines.append(f"#include \"{include}\"")
    lines.append("")
    lines.append(f"#include \"{report.metadata.name}.generated.h\"")
    lines.append("")
    lines.append("UCLASS(BlueprintType)")
    parent = _resolve_parent_cpp_class(report.metadata.parent_class)
    lines.append(f"class {class_name} : public {parent}")
    lines.append("{")
    lines.append("    GENERATED_BODY()")
    lines.append("")
    lines.append("public:")
    lines.append(f"    {class_name}();")

    for synopsis in report.functions:
        prototype = _function_signature(synopsis)
        comment = synopsis.description.replace("\n", " ")
        lines.append("")
        lines.append(f"    /** {comment} */")
        lines.append("    UFUNCTION(BlueprintCallable, Category=\"BlueprintCleaner\")")
        lines.append(f"    void {prototype};")

    lines.append("};")
    return "\n".join(lines)


def _build_source(report: BlueprintReport, class_name: str) -> str:
    """Compose source file text."""

    body: List[str] = [f"#include \"{report.metadata.name}.h\"", ""]
    body.append(f"{class_name}::{class_name}()")
    body.append("{")
    body.append("    PrimaryActorTick.bCanEverTick = false;")
    body.append("}")

    for synopsis in report.functions:
        prototype = _function_signature(synopsis)
        qualified = f"void {class_name}::{prototype[:-2]}" if prototype.endswith("()") else f"void {class_name}::{prototype}"
        body.extend(["", f"{qualified}()", "{"])
        body.extend(_emit_function_body(synopsis))
        body.append("}")

    return "\n".join(body)


def _function_signature(synopsis: FunctionSynopsis) -> str:
    """Create a C++ function signature from synopsis."""

    return f"{_sanitize_identifier(synopsis.name)}()"


def _sanitize_identifier(name: str) -> str:
    """Sanitize blueprint names into valid C++ identifiers."""

    sanitized = (
        name.replace("::", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )
    return sanitized


def _emit_function_body(synopsis: FunctionSynopsis) -> List[str]:
    """Build informative comment body for generated source."""

    lines: List[str] = []
    if synopsis.calls:
        lines.append(f"    // Calls: {', '.join(synopsis.calls)}")
    if synopsis.reads:
        lines.append(f"    // Reads: {', '.join(synopsis.reads)}")
    if synopsis.writes:
        lines.append(f"    // Writes: {', '.join(synopsis.writes)}")
    lines.append("    // TODO: Implement translated logic from blueprint graph")
    return lines
