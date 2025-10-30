"""Utilities for generating Unreal Engine C++ artifacts from blueprints."""

from __future__ import annotations

from typing import Optional

DEFAULT_MODULE = "Game"


def infer_cpp_class_name(blueprint_name: str, parent_class: Optional[str]) -> str:
    """Infer the Unreal C++ class name for a blueprint asset."""

    prefix = _resolve_prefix(parent_class)
    if blueprint_name.startswith(prefix):
        return blueprint_name
    return f"{prefix}{blueprint_name}"


def header_filename(blueprint_name: str) -> str:
    """Return the header filename for the blueprint-derived class."""

    return f"{blueprint_name}.h"


def source_filename(blueprint_name: str) -> str:
    """Return the source filename for the blueprint-derived class."""

    return f"{blueprint_name}.cpp"


def header_path(blueprint_name: str, module: str = DEFAULT_MODULE) -> str:
    """Return the Source/<Module> path for the generated header."""

    return f"Source/{module}/{header_filename(blueprint_name)}"


def source_path(blueprint_name: str, module: str = DEFAULT_MODULE) -> str:
    """Return the Source/<Module> path for the generated source."""

    return f"Source/{module}/{source_filename(blueprint_name)}"


def _resolve_prefix(parent_class: Optional[str]) -> str:
    """Determine UE naming prefix based on the parent class."""

    if not parent_class:
        return "U"

    mapping = {
        "Actor": "A",
        "Character": "A",
        "Controller": "A",
        "Pawn": "A",
        "GameMode": "A",
        "GameState": "A",
        "ActorComponent": "U",
        "SceneComponent": "U",
        "UserWidget": "U",
        "Widget": "U",
    }

    for suffix, prefix in mapping.items():
        if parent_class.endswith(suffix):
            return prefix

    return "U"
