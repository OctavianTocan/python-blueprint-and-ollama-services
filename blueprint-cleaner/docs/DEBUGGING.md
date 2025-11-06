# Debugging Blueprint Cleaner

## Quick Troubleshooting

### Graphs Not Detected

**Symptom:** `report.graphs` is empty, but your `.COPY` file contains graph blocks.

**Checklist:**

1. Verify the blueprint file contains a schema declaration:
   ```
   Begin Object Class=EdGraph Name="EventGraph"
       Schema=... (or Class=EdGraphSchema, WidgetGraphSchema, etc.)
       Nodes(...)
   ```
2. Check that `Nodes(` array is present (not just `Schema=`)
3. Use debug mode to inspect blocks:
   ```bash
   blueprint-cleaner your_file.COPY -d
   ```
   This logs block detection details.

**How to debug:**

- Open the `.COPY` file in a text editor and search for `Begin Object`
- Look for lines containing both `Schema=` and `Nodes(`
- If you find them, the block should be detected. If not, check the schema string logic in `parsers/block_extraction.py::_line_has_graph_schema()`

---

### Node Parsing Not Working

**Symptom:** Graphs are detected but contain no nodes or calls.

**Checklist:**

1. Ensure nodes start with `K2Node_` or `EdGraphNode_Comment`:
   ```
   Begin Object Class=K2Node_CallFunction Name="K2Node_CallFunction_0"
   ```
2. Run `collect_node_blocks()` test:
   ```bash
   cd blueprint-cleaner
   uv run pytest tests/test_blueprint_cleaner.py::test_blueprint_cleaner -v
   ```
3. Check `node_parsing.py` for function/variable regex patterns

**How to debug:**

- Extract a graph block manually from the `.COPY`
- Write a small test:
  ```python
  from blueprint_cleaner.parsers.block_extraction import collect_graph_blocks, collect_node_blocks
  lines = open("your_file.COPY").readlines()
  graphs = collect_graph_blocks(lines)
  if graphs:
      nodes = collect_node_blocks(graphs[0])
      print(f"Found {len(nodes)} nodes")
      for n in nodes:
          print(f"  - {n.name}")
  ```

---

### Widget Data Missing

**Symptom:** Widget bindings, animations, or widget variables not appearing in output.

**Checklist:**

1. Verify the file is a `WidgetBlueprint`:
   ```bash
   grep "WidgetTree\|Bindings\|Animations" your_file.COPY
   ```
2. If found, check the anchor text in `widget_data.py`:
   - `Bindings=` for widget bindings
   - `Animations(` for animations
   - `WidgetVariableNameToGuidMap=` for widget variables
3. Run widget extraction in isolation:
   ```python
   from blueprint_cleaner.widget_data import extract_widget_bindings
   content = open("your_file.COPY").read()
   bindings = extract_widget_bindings(content)
   print(f"Found {len(bindings)} bindings")
   ```

---

### Encoding Issues

**Symptom:** "Codec error" or garbled output.

**Root cause:** The `.COPY` file may use UTF-16 or have a byte order mark (BOM).

**Solution:** The parser auto-detects encoding via `toolkit.file_io.read_text_with_encoding_detection()`. If you're manually reading a file, use that utility:

```python
from toolkit.file_io import read_text_with_encoding_detection
content = read_text_with_encoding_detection("your_file.COPY")
```

---

### Empty AI Summary

**Symptom:** `-f summary` returns no summary text.

**Cause:** Ollama may be unavailable or returning an empty response.

**Troubleshoot:**

1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/health
   ```
2. Try using a local model:
   ```bash
   blueprint-cleaner your_file.COPY -f summary
   # If still empty, Ollama might be timing out or the model isn't available
   ```
3. Fall back to markdown/JSON formats (guaranteed to work without Ollama)

---

## Developer Debugging Patterns

### Probe: Count Schema and Nodes Markers

Quickly verify a `.COPY` file has graph content:

```python
content = open("your_file.COPY").read()
schema_lines = [l for l in content.split("\n") if "Schema=" in l]
nodes_lines = [l for l in content.split("\n") if "Nodes(" in l]
print(f"Schema markers: {len(schema_lines)}")
print(f"Nodes markers: {len(nodes_lines)}")
```

If counts are low or zero, graphs won't be detected.

### Probe: Validate Begin/End Object Nesting

Check that all `Begin Object` blocks have matching `End Object`:

```python
def validate_nesting(file_path: str) -> bool:
    """Check balanced Begin/End Object pairs."""
    lines = open(file_path).readlines()
    balance = 0
    for i, line in enumerate(lines, 1):
        if "Begin Object" in line:
            balance += 1
        elif line.strip() == "End Object":
            balance -= 1
        if balance < 0:
            print(f"Unmatched End Object at line {i}")
            return False
    if balance != 0:
        print(f"Final balance: {balance} (should be 0)")
        return False
    print("✓ All Begin/End pairs balanced")
    return True
```

### Probe: Extract and Inspect a Single Block

Manually extract and pretty-print a block:

```python
from blueprint_cleaner.parsers.block_extraction import collect_graph_blocks
lines = open("your_file.COPY").readlines()
graphs = collect_graph_blocks(lines)
if graphs:
    g = graphs[0]
    print(f"Graph: {g.name}\n")
    print("\n".join(g.lines[:50]))  # First 50 lines
```

### Probe: Test Regex Patterns in Isolation

Verify a regex pattern matches what you expect:

```python
import re
pattern = re.compile(r'FunctionReference=\(([^)]*)\)')
text = 'FunctionReference=(MemberParent=BP_X.BP_X_C,MemberName=Setup,MemberGuid=ABC123)'
match = pattern.search(text)
if match:
    print(f"Captured: {match.group(1)}")
else:
    print("No match!")
```

### Targeted Test Runs

Run a specific test to isolate failures:

```bash
# Test graph extraction
uv run pytest tests/test_blueprint_cleaner.py::test_blueprint_cleaner -v -k graph

# Test widget blueprints
uv run pytest tests/test_blueprint_cleaner.py::test_widget_blueprint_reports_umg_metadata -v

# Test with detailed output
uv run pytest tests/test_blueprint_cleaner.py -vv --tb=short
```

### Debug Mode

Run the CLI with debug logging:

```bash
blueprint-cleaner your_file.COPY -d -f markdown
```

This enables verbose logging (see `logging_config.py`). Logs print to stderr; output still goes to stdout or file.

---

## Common Gotchas

### Gotcha 1: Widget vs. Standard Blueprints

Widget blueprints have `WidgetTree`, `Animations`, `Bindings`. Standard blueprints don't. If your widget data isn't appearing, verify the file is actually a widget blueprint:

```bash
grep -c "WidgetTree=" your_file.COPY  # Should be 1+
```

### Gotcha 2: Graph Schema Variations

`EdGraph`, `WidgetGraphSchema`, and others are valid. The detector in `_line_has_graph_schema()` checks for `graphschema` or `edgraph` substrings (case-insensitive). If you add a new schema type, update the check.

### Gotcha 3: Node Name Prefixes

Nodes are only captured if they start with:

- `K2Node_*` (Blueprint nodes)
- `EdGraphNode_Comment` (Developer comments)

Other object types in the file are skipped. This is intentional to avoid noise.

### Gotcha 4: Sorted Output

All parser outputs are sorted by name for stable, reproducible results. If you're comparing outputs, make sure you're comparing sorted lists.

---

## When All Else Fails

1. **Verify the input file is valid .COPY**: Open it in a text editor. Look for `Begin Object`, `End Object`, `Class=`, `Name=` patterns.
2. **Check test fixtures**: Look at `test_blueprint_cleaner.py` for known-good `.COPY` samples.
3. **Simplify the problem**: Extract a single graph block and test just that.
4. **Enable debug mode**: `blueprint-cleaner file.COPY -d` to see parser logs.
5. **Check file encoding**: Use `detect_encoding_from_bom()` to verify UTF-8 or UTF-16.

---
