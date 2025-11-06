# Blueprint Cleaner

Transform Unreal Engine 5 blueprint `.COPY` files into AI-friendly summaries for analysis and documentation.

## Features

- **Clean extraction**: Parses variables, graphs, function calls, and metadata from blueprint exports
- **Multiple formats**: Output as Markdown or JSONC (JSON with Comments)
- **Batch processing**: Process multiple blueprint files at once with progress tracking
- **Graph insights**: Entry points, function calls, variable reads/writes, and developer comments
- **Modular architecture**: Small, focused modules following clean code principles

## Understanding Blueprint `.COPY` Files

When you export a Blueprint from Unreal Engine, you get a `.COPY` file—a text snapshot of your Blueprint's structure. Here's what the parser looks for:

### How to Export a .COPY File

1. In **Unreal Engine 5**, open the **Content Browser**
2. **Right-click** on your Blueprint asset
3. Select **Asset Actions** → **Export**
4. Choose a filename (e.g., `MyBlueprint.COPY`) and save

The resulting `.COPY` file is a text-based export that can be opened in any text editor. **Note:** `.COPY` files cannot be directly re-imported into UE5. To move Blueprints between projects, use the **Migrate** feature or copy `.uasset` files directly.

### Basic Building Blocks

**`Begin Object` … `End Object`**  
Think of these as containers. Everything in a Blueprint—graphs, nodes, variables—lives inside these paired tags. They can nest like folders within folders.

**`Name="SomeName"`**  
The friendly name you see in the Unreal editor. The parser extracts this to label graphs and nodes in the output.

### Graphs (Visual Script Diagrams)

**`Class=EdGraph`** or **`Schema=...`**  
Marks the start of a graph definition. Regular Blueprints use `EdGraph`, while UI widgets use `WidgetGraphSchema`. The parser only treats a block as a graph if it finds both a schema marker and a `Nodes(` array.

**`Nodes(`**  
Lists all the visual nodes in that graph. Each node is another nested `Begin Object` block.

### Nodes (Individual Action Boxes)

**`K2Node_*`**  
Blueprint execution nodes (like "Branch", "Set Variable", "Call Function"). The parser reads these to find what your Blueprint actually does.

**`EdGraphNode_Comment`**  
Developer notes you added in the graph. These show up as readable annotations in the summary.

### UI Blueprints (Widgets)

Widget Blueprints add extra sections:

- **`WidgetTree=`** — The hierarchy of UI elements (buttons, text boxes, etc.)
- **`Animations=`** — Timeline animations for your UI
- **`Bindings=`** — Connections between UI elements and Blueprint logic

The parser extracts these separately so your UI structure is easy to review.

---

**Where to look in the code:**  
Graph extraction → `parsers/block_extraction.py`  
Node parsing → `parsers/node_parsing.py`  
Widget data → `widget_data.py`  
Final report → `pipeline.py`

**Deep dives:**

- [Architecture & Design Decisions](./docs/ARCHITECTURE.md) — Why the parser uses pure functions instead of inheritance
- [Parser Pattern Guide](./docs/PARSER_PATTERN.md) — How to add new parsers
- [Debugging Patterns](./docs/DEBUGGING.md) — Troubleshooting common issues

## Quick Start

```bash
# Install with uv
cd blueprint-cleaner
uv sync

# Process a single blueprint file
uv run blueprint-cleaner data/in/MyBlueprint.COPY

# Custom output
uv run blueprint-cleaner data/in/MyBlueprint.COPY -o data/out/summary.md

# JSONC format (JSON with Comments)
uv run blueprint-cleaner data/in/MyBlueprint.COPY --format json

# Debug mode
uv run blueprint-cleaner data/in/MyBlueprint.COPY -d

# Batch process all .COPY files in a directory
uv run blueprint-cleaner data/in/ -o data/out/

# Batch process with custom format
uv run blueprint-cleaner data/in/ -o data/out/ --format json

# Batch process with fail-fast mode (stop on first error)
uv run blueprint-cleaner data/in/ -o data/out/ --fail-fast
```

## Batch Processing

Process multiple blueprint files at once by passing a directory path instead of a single file.

### Features

- **Recursive scanning**: Automatically finds all `.COPY` files in subdirectories
- **Progress tracking**: Shows "Processing 3/10 blueprints..." status
- **Error handling**: Continue processing on errors, or use `--fail-fast` to stop immediately
- **Summary report**: Displays success/failure counts after processing
- **Smart naming**: Output files are named after the blueprint (e.g., `BP_Character.md`)

### Usage

```bash
# Process all blueprints in a directory
uv run blueprint-cleaner data/blueprints/ -o data/output/

# The tool will:
# 1. Find all .COPY files recursively
# 2. Process each with the same format/options
# 3. Save to output directory maintaining filename
# 4. Show progress and summary
```

### Example Output

```
Found 3 .COPY files to process

[1/3] Processing EXAMPLE_BP_GameSettings...
✓ Extracted:
  - variables: 5
  - graphs: 2
  ...

[2/3] Processing EXAMPLE_BP_SimpleCharacter...
...

[3/3] Processing EXAMPLE_WBP_SimpleUI...
...

=========================
Batch Processing Summary:
  ✓ Successful: 3/3
  ✗ Failed: 0/3
=========================

✓ All files processed successfully
Output directory: data/output/
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

For a deep dive on design philosophy, see [Architecture & Design Decisions](./docs/ARCHITECTURE.md).

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

## Debugging & Troubleshooting

**Graphs not detected?** Check that `Schema=` and `Nodes(` are both present in the `.COPY` file. See [Debugging Patterns](./docs/DEBUGGING.md) for detailed checks.

**Widget data missing?** Verify your file is a WidgetBlueprint with `WidgetTree=`, `Bindings=`, or `Animations=` sections. Use debug mode:

```bash
blueprint-cleaner your_file.COPY -d
```

For more troubleshooting, see [Debugging Patterns](./docs/DEBUGGING.md).

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
blueprint-cleaner [-h] [-o OUTPUT] [-f {markdown,text,json,...}] [-d] [--fail-fast] input

Positional arguments:
  input                 Input .COPY file path or directory containing .COPY files

Options:
  -h, --help            Show help message
  -o, --output OUTPUT   Output file path (for single file) or directory (for batch processing)
                        Default: input_cleaned.md/json (single file) or input_cleaned/ (directory)
  -f, --format FORMAT   Output format: markdown, text, json, bundle, summary, cpp-header, cpp-source
                        Default: markdown
  -d, --debug           Enable debug mode with detailed logs
  --fail-fast           Stop batch processing on first error (only applies to directory input)
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

### JSONC (JSON with Comments)

```jsonc
{
  "name": "BPAC_IG_PCH_Melee",
  "parent_class": "IG_PlayerCharacter",
  "variables": [...],
  "graphs": [...]
}
```

## License

MIT
