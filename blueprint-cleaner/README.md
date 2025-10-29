# Blueprint Cleaner

Transform Unreal Engine 5 blueprint `.COPY` files into AI-friendly summaries for analysis and documentation.

## Features

- **Clean extraction**: Parses variables, graphs, function calls, and metadata from blueprint exports
- **Multiple formats**: Output as Markdown or JSON
- **Graph insights**: Entry points, function calls, variable reads/writes, and developer comments
- **Modular architecture**: Small, focused modules following clean code principles

## Quick Start

```bash
# Install with uv
cd blueprint-cleaner
uv sync

# Process a blueprint file
uv run blueprint-cleaner data/in/MyBlueprint.COPY

# Custom output
uv run blueprint-cleaner data/in/MyBlueprint.COPY -o data/out/summary.md

# JSON format
uv run blueprint-cleaner data/in/MyBlueprint.COPY --format json

# Debug mode
uv run blueprint-cleaner data/in/MyBlueprint.COPY -d
```

## Project Structure

```
blueprint-cleaner/
├── src/blueprint_cleaner/
│   ├── parsers/           # Text parsing (graphs, variables, nodes)
│   ├── formatters/        # Output rendering (markdown, JSON)
│   ├── cli.py            # Command-line interface
│   ├── pipeline.py       # Main orchestration
│   ├── report.py         # Report builder
│   ├── metadata.py       # Blueprint metadata extraction
│   ├── graphs.py         # Graph summarization
│   ├── variables.py      # Variable extraction
│   ├── io_utils.py       # File I/O wrappers
│   └── models.py         # Data structures
├── data/
│   ├── in/               # Input .COPY files
│   └── out/              # Generated summaries
└── README.md
```

## Architecture

### Parsers

Small, focused modules for extracting data from blueprint text:

- **block_extraction**: Locate graph and node blocks
- **graph_classification**: Categorize graphs by type
- **node_parsing**: Extract calls, variables, comments from nodes
- **variable_collection**: Gather variable metadata entries
- **variable_parsing**: Parse variable records

### Formatters

Output renderers for different formats:

- **markdown**: Rich human-readable summaries
- **json_output**: Machine-readable structured data

### Pipeline

Orchestrates the full workflow:

1. Read blueprint file (auto-detect encoding)
2. Extract metadata, variables, graphs
3. Build structured report
4. Render in requested format
5. Write output file

## Dependencies

- **toolkit**: Shared utilities for text parsing, I/O, formatting
- Python 3.13+

## Development

The project follows strict clean code principles:

- Functions < 20 lines (ideally 5-10)
- Single responsibility per function
- One level of abstraction per function
- Comprehensive Doxygen-style documentation

## CLI Options

```
blueprint-cleaner [-h] [-o OUTPUT] [-f {markdown,text,json}] [-d] input

Positional arguments:
  input                 Input .COPY file path

Options:
  -h, --help            Show help message
  -o, --output OUTPUT   Output file path (default: input_cleaned.md/json)
  -f, --format FORMAT   Output format: markdown, text, json (default: markdown)
  -d, --debug           Enable debug mode with detailed logs
```

## Example Output

### Markdown

```markdown
# Blueprint: BPAC_IG_PCH_Melee

_Parent Class:_ `IG_PlayerCharacter`

## At a glance

- Variables: 11
- Graphs: 8
- Event Handlers: 6
- Unique Calls: 22

## Variables

| Name            | Type                 | Category | Notes |
| --------------- | -------------------- | -------- | ----- |
| `AttackMontage` | object (AnimMontage) | Default  | —     |

...
```

### JSON

```json
{
  "name": "BPAC_IG_PCH_Melee",
  "parent_class": "IG_PlayerCharacter",
  "variables": [...],
  "graphs": [...]
}
```

## License

MIT
