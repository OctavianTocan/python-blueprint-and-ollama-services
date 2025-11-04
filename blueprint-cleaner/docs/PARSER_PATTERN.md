# Parser Pattern Guide

## Overview

Adding a new parser to blueprint-cleaner follows a consistent pattern. This guide walks you through each step.

## The Parser Pattern

**Input:** Raw blueprint text or already-extracted intermediate structures  
**Output:** Typed dataclass (from `models.py`)  
**How:** Pure functions, no side effects, no inheritance

## Step-by-Step: Adding a New Parser

### 1. Define the Output Dataclass

Add a new dataclass to `models.py`:

```python
@dataclass
class MyExtractionResult:
    """Description of what this captures."""

    field_name: str
    optional_field: Optional[str] = None
```

**Guidelines:**

- Use descriptive names
- Document the purpose
- Use `Optional` for fields that might be missing
- Use `field(default_factory=list)` for collections

### 2. Create the Parser Module

Create a new file in `parsers/` or add functions to `widget_data.py` (if widget-related).

**File name:** `parsers/my_feature_parsing.py`

**Structure:**

```python
"""Extraction of MyFeature data from blueprint text.

Brief description of what this parser does and the patterns it looks for.
"""

from __future__ import annotations

import re
from typing import List, Optional

from ..models import MyExtractionResult
from toolkit.text_parsing import find_first_match

# Compiled regex patterns at module scope
MY_PATTERN_RE = re.compile(r'MyKey=("([^"]+)")')
ANOTHER_PATTERN_RE = re.compile(r'AnotherKey=\(([^)]+)\)')


def extract_my_feature(content: str) -> List[MyExtractionResult]:
    """Extract MyFeature data from blueprint text.

    Looks for MyKey= declarations and parses them into structured records.

    @param content: Raw blueprint text.
    @return: List of extracted features, empty if none found.
    """
    results: List[MyExtractionResult] = []

    for entry in _collect_my_entries(content):
        parsed = _parse_my_entry(entry)
        if parsed:
            results.append(parsed)

    return sorted(results, key=lambda x: x.field_name.lower())


def _collect_my_entries(content: str) -> List[str]:
    """Locate raw entry blocks for MyFeature."""
    # Implementation
    ...


def _parse_my_entry(entry: str) -> Optional[MyExtractionResult]:
    """Convert raw entry text into structured result."""
    field_name = _find_first(MY_PATTERN_RE, entry)
    if not field_name:
        return None

    optional_field = _find_first(ANOTHER_PATTERN_RE, entry)

    return MyExtractionResult(
        field_name=field_name,
        optional_field=optional_field,
    )


def _find_first(pattern: re.Pattern[str], text: str) -> Optional[str]:
    """Return first regex capture group or None."""
    match = pattern.search(text)
    return match.group(1) if match else None
```

**Key patterns:**

- Regex patterns at module scope for efficiency
- Helper functions prefixed with `_` for internal use
- Doxygen docstrings with `@param` and `@return`
- Return typed dataclass instances, not dicts or tuples
- Sort results for stable output (by name, ID, etc.)

### 3. Wire into the Report Builder

Open `report.py` and add your parser to `build_blueprint_report()`:

```python
from .my_feature_parsing import extract_my_feature

def build_blueprint_report(content: str, debug: bool = False) -> BlueprintReport:
    """Parse blueprint text into a structured report."""

    metadata = build_metadata(content)
    variables = extract_variables(content)
    graphs = summarize_graphs(content, debug)
    functions = build_function_synopses(graphs)
    widget_bindings = extract_widget_bindings(content)
    widget_animations = extract_widget_animations(content)
    widget_variables = extract_widget_variables(content)
    my_features = extract_my_feature(content)  # ← Add your parser here

    return BlueprintReport(
        metadata=metadata,
        variables=variables,
        graphs=graphs,
        functions=functions,
        widget_bindings=widget_bindings,
        widget_animations=widget_animations,
        widget_variables=widget_variables,
        my_features=my_features,  # ← Add field to dataclass
    )
```

### 4. Update the BlueprintReport Dataclass

Add a field to `models.py`:

```python
@dataclass
class BlueprintReport:
    """Top-level summary produced for a blueprint."""

    metadata: BlueprintMetadata
    variables: List[VariableInfo]
    graphs: List[GraphSummary]
    functions: List[FunctionSynopsis] = field(default_factory=list)
    widget_bindings: List[WidgetBinding] = field(default_factory=list)
    widget_animations: List[str] = field(default_factory=list)
    widget_variables: List[WidgetVariable] = field(default_factory=list)
    my_features: List[MyExtractionResult] = field(default_factory=list)  # ← Add here
```

### 5. Add Formatters

Update each formatter to emit your new data.

**For Markdown** (`formatters/markdown.py`):

```python
def format_as_markdown(report: BlueprintReport) -> str:
    """..."""
    sections = [
        _header(report),
        _at_a_glance(report),
        _variables_section(report),
        _graphs_section(report),
        _my_features_section(report),  # ← Add your formatter
    ]
    return "\n\n".join(s for s in sections if s)


def _my_features_section(report: BlueprintReport) -> str:
    """Format MyFeature data as markdown."""
    if not report.my_features:
        return ""

    lines = ["## My Features"]
    for feature in report.my_features:
        lines.append(f"- **{feature.field_name}**: {feature.optional_field or '—'}")

    return "\n".join(lines)
```

**For JSON** (`formatters/json_output.py`):

```python
def render_json_output(report: BlueprintReport) -> str:
    """..."""
    data = {
        "name": report.metadata.name,
        "variables": [_variable_to_dict(v) for v in report.variables],
        "graphs": [_graph_to_dict(g) for g in report.graphs],
        "my_features": [_feature_to_dict(f) for f in report.my_features],  # ← Add here
    }
    return json.dumps(data, indent=2)


def _feature_to_dict(feature: MyExtractionResult) -> dict:
    """Convert MyExtractionResult to dict."""
    return {
        "field_name": feature.field_name,
        "optional_field": feature.optional_field,
    }
```

### 6. Write Tests

Add a test fixture to `tests/test_blueprint_cleaner.py`:

```python
def test_extract_my_features():
    """Verify MyFeature extraction."""
    sample = """
    Begin Object Class=MyFeatureClass Name="MyFeature"
        MyKey="feature_value"
        AnotherKey=(SomeData)
    End Object
    """

    features = extract_my_feature(sample)

    assert len(features) == 1
    assert features[0].field_name == "feature_value"
    assert features[0].optional_field == "SomeData"
```

Run tests:

```bash
uv run pytest blueprint-cleaner/tests/test_blueprint_cleaner.py::test_extract_my_features -v
```

## Common Patterns

### Regex-Based Entry Collection

Extract multiple entries from a delimited section:

```python
def _collect_my_entries(content: str) -> List[str]:
    """Locate raw entry blocks for MyFeature."""
    # Pattern: MyFeatures(index)=...
    pattern = re.compile(r'MyFeatures\(\d+\)="([^"]*)"')
    return pattern.findall(content)
```

### Stack-Based Block Extraction

For nested structures, use a stack (see `parsers/block_extraction.py`):

```python
def collect_my_blocks(lines: Sequence[str]) -> List[MyBlock]:
    """Extract nested My blocks."""
    blocks = []
    stack = []

    for index, line in enumerate(lines):
        if line.strip().startswith("Begin Object"):
            stack.append((index, line))
        elif line.strip() == "End Object" and stack:
            start, header = stack.pop()
            block_lines = lines[start : index + 1]
            # Validate and append
            if _is_valid_my_block(block_lines):
                blocks.append(MyBlock(...))

    return blocks
```

### Using Toolkit Utilities

Leverage shared helpers from `toolkit`:

```python
from toolkit.text_parsing import extract_tail_identifier, find_first_match

# Reduce qualified paths to readable names
identifier = extract_tail_identifier(path)

# Simple regex extraction
name = find_first_match(r'Name="([^"]+)"', text)
```

## Testing Checklist

- [ ] Parser returns empty list on missing data (no crashes)
- [ ] Parser handles malformed entries gracefully
- [ ] Output is sorted/consistent (for stable tests)
- [ ] Doxygen docstrings present on public functions
- [ ] Test fixture added to `test_blueprint_cleaner.py`
- [ ] Formatters (markdown, JSON) updated
- [ ] `BlueprintReport` dataclass includes new field
- [ ] `report.build_blueprint_report()` calls parser

## Example: Full Widget Data Parser

See `widget_data.py` for a complete reference implementation extracting bindings, animations, and widget variables.

Key takeaways:

- Pure functions, no class inheritance
- Regex at module scope
- Returns typed dataclass instances
- Integrated into `report.py` orchestration
- Covered by tests and formatters
