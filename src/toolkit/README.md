# Toolkit

Shared utilities for Python projects providing text parsing, file I/O, formatting, and console output helpers.

## Overview

The `toolkit` package is a collection of lightweight, reusable utility modules designed to be shared across multiple Python projects. All functions follow clean code principles with comprehensive Doxygen documentation.

## Modules

### text_parsing

Text parsing utilities for extracting patterns from structured text.

**Key Functions:**

- `find_first_match(pattern, text)`: Extract first capture group from regex
- `strip_quote_wrappers(value)`: Remove surrounding quotes and whitespace
- `extract_tail_identifier(raw)`: Reduce qualified references to readable tail identifiers
- `normalize_multiline_comment(comment)`: Sanitize comment text, removing escape sequences
- `parse_key_value_pairs(chunk, pair_pattern)`: Convert structured text to dictionary

**Example:**

```python
from toolkit.text_parsing import extract_tail_identifier, find_first_match

# Extract tail identifier from blueprint path
path = "Blueprint'/Game/Characters/SKEL_Character_C'"
identifier = extract_tail_identifier(path)  # "Character"

# Find first regex match
pattern = r"Name=(\\w+)"
text = "Name=MyBlueprint Type=Actor"
name = find_first_match(pattern, text)  # "MyBlueprint"
```

### file_io

File I/O utilities with encoding detection and safe text handling.

**Key Functions:**

- `read_text_with_encoding_detection(path)`: Load text file with automatic encoding detection
- `detect_encoding_from_bom(payload)`: Identify encoding from byte order mark
- `write_text_utf8(path, text)`: Persist text to disk using UTF-8

**Example:**

```python
from toolkit.file_io import read_text_with_encoding_detection, write_text_utf8

# Read file with automatic encoding detection (handles UTF-16, UTF-8 BOM, etc.)
content = read_text_with_encoding_detection("data/blueprint.COPY")

# Write UTF-8 file
write_text_utf8("output/summary.md", content)
```

### collections

Collection utilities for deduplication and list processing.

**Key Functions:**

- `dedupe_preserve_order(items)`: Remove duplicates while preserving first occurrence order

**Example:**

```python
from toolkit.collections import dedupe_preserve_order

items = ["apple", "banana", "apple", "cherry", "banana"]
unique = dedupe_preserve_order(items)  # ["apple", "banana", "cherry"]
```

### formatting

Text formatting utilities for rendering lists and structured output.

**Key Functions:**

- `format_inline_list(values, limit, decorator)`: Format sequence as inline comma-separated list with overflow indicator
- `wrap_items_with_decorator(items, decorator)`: Wrap each item with a decorator character

**Example:**

```python
from toolkit.formatting import format_inline_list, wrap_items_with_decorator

# Format inline list with limit
functions = ["Setup", "Tick", "BeginPlay", "EndPlay", "Destroy"]
formatted = format_inline_list(functions, limit=3, decorator="`")
# Result: "`Setup`, `Tick`, `BeginPlay`, … (+2 more)"

# Wrap items for markdown code
items = ["variable1", "variable2", "variable3"]
wrapped = wrap_items_with_decorator(items, "`")
# Result: ["`variable1`", "`variable2`", "`variable3`"]
```

### console

Console output helpers for progress and summary reporting.

**Key Functions:**

- `print_processing_header(input_path, output_path, format_type)`: Display processing configuration
- `print_success_footer(output_path)`: Display successful completion message
- `print_metric_summary(label, value, indent)`: Print a single metric line with consistent formatting

**Example:**

```python
from toolkit.console import print_processing_header, print_success_footer, print_metric_summary

# Display processing header
print_processing_header(
    input_path="data/in/blueprint.COPY",
    output_path="data/out/summary.md",
    format_type="markdown"
)

# Display metrics
print_metric_summary("Variables", 15)
print_metric_summary("Graphs", 8)

# Display success footer
print_success_footer("data/out/summary.md")
```

## Installation

The toolkit is designed to be used as a local dependency in other projects within the workspace.

### As a Workspace Dependency

In your project's `pyproject.toml`:

```toml
[project]
dependencies = [
    "toolkit",
]

[tool.uv.sources]
toolkit = { path = "../", editable = true }
```

### Standalone Installation

```bash
cd Utils
uv sync
```

## Usage

Import utilities directly from their modules:

```python
from toolkit.text_parsing import find_first_match, extract_tail_identifier
from toolkit.file_io import read_text_with_encoding_detection
from toolkit.console import print_metric_summary
from toolkit.collections import dedupe_preserve_order
from toolkit.formatting import format_inline_list
```

## Design Principles

All functions in the toolkit follow strict clean code guidelines:

- **Small functions**: 5-10 lines (max 20)
- **Single responsibility**: Each function does one thing well
- **One abstraction level**: Consistent level of abstraction per function
- **Comprehensive documentation**: Doxygen-style docstrings
- **Type hints**: Full type annotations for clarity

## Dependencies

The toolkit has minimal dependencies to maintain lightweight portability:

- **Python 3.13+**: Modern Python features
- **No external dependencies**: Pure Python implementation

## Development

### Project Structure

```
src/toolkit/
├── __init__.py
├── text_parsing.py    # Regex and text extraction utilities
├── file_io.py         # File reading/writing with encoding detection
├── collections.py     # List and collection utilities
├── formatting.py      # Text formatting and rendering
└── console.py         # Terminal output helpers
```

### Adding New Utilities

When adding new utilities to the toolkit:

1. **Choose the appropriate module** or create a new one if needed
2. **Follow clean code principles**: Small, focused functions
3. **Add comprehensive docstrings**: Doxygen format with @param and @return
4. **Include type hints**: Full type annotations
5. **Provide examples**: Usage examples in docstrings or README
6. **Keep it lightweight**: Avoid external dependencies when possible

### Testing

```bash
uv run pytest tests/
```

## Used By

The toolkit is used by the following projects in this workspace:

- **blueprint-cleaner**: Blueprint parsing and analysis
- **ollama-service**: HTTP wrapper for Ollama API

## License

MIT
