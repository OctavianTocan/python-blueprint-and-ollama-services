# Blueprint Cleaner Architecture

## Design Philosophy: Why No Inheritance?

This project deliberately avoids inheritance-based patterns for parsers. Instead, it uses **composition of pure functions** orchestrated by a central report builder. Here's why:

### The Parser Pattern: Pure Functions, Not Classes

Each parser (block extraction, node parsing, variable parsing, widget data) is a **pure function** or module of pure functions:

```python
# Each parser: text or structures → typed dataclass
def extract_variables(content: str) -> List[VariableInfo]:
    """Input: raw blueprint text → Output: structured variable list."""
    ...

def extract_widget_bindings(content: str) -> List[WidgetBinding]:
    """Input: raw blueprint text → Output: structured binding list."""
    ...
```

**No inheritance, no base class, no shared state.**

### Why This Design?

#### 1. **Single Responsibility**

Each parser module does one thing: extract and structure one type of data. No mixing of concerns.

#### 2. **Testability**

Pure functions with clear inputs/outputs are trivial to unit test. No mocking, no fixture state, no inheritance chains to navigate.

#### 3. **Composability**

New parsers plug in without modifying existing code. `report.build_blueprint_report()` orchestrates them:

```python
def build_blueprint_report(content: str, debug: bool = False) -> BlueprintReport:
    metadata = build_metadata(content)
    variables = extract_variables(content)
    graphs = summarize_graphs(content, debug)
    widget_bindings = extract_widget_bindings(content)
    # ... etc
    return BlueprintReport(...)
```

Adding a new parser? Just call it in the orchestrator.

#### 4. **No Abstraction Tax**

Inheritance imposes a contract (base class interface) that multiple implementations must follow. If parsers have different structures and responsibilities, inheritance creates artificial coupling. Here, each parser is free to:

- Take whatever text or structures it needs
- Return its own dataclass
- Use internal regex, logic, or helper functions
- Evolve independently

#### 5. **Clarity**

When you read `report.py`, you see exactly what data flows where. When you read `parsers/node_parsing.py`, you see pure extraction logic with no hidden callbacks or polymorphic dispatch.

### Contrast: What Inheritance Would Look Like

If we used a base class:

```python
# Anti-pattern (not used in this project)
class Parser:
    def parse(self, content: str) -> Any:
        raise NotImplementedError

class VariableParser(Parser):
    def parse(self, content: str) -> List[VariableInfo]:
        ...

class NodeParser(Parser):
    def parse(self, content: str) -> List[NodeBlock]:
        ...

# Then in report.py:
parsers = [VariableParser(), NodeParser(), ...]
for parser in parsers:
    parser.parse(content)  # Polymorphic dispatch
```

**Problems:**

- Parser return types are now `Any` or a union, requiring casting
- Adding a new parser type (e.g., widget bindings) requires creating a new class
- Inheritance implies all parsers have the same interface, which breaks when one needs different inputs
- Harder to test; more setup overhead

### The Architecture in Practice

**Data flow:**

```
.COPY file (raw text)
    ↓
[Parsed into lines by io_utils]
    ↓
report.build_blueprint_report(content)
    ├─ metadata.build_metadata(content) → BlueprintMetadata
    ├─ variables.extract_variables(content) → List[VariableInfo]
    ├─ graphs.summarize_graphs(content) → List[GraphSummary]
    ├─ widget_data.extract_widget_bindings(content) → List[WidgetBinding]
    ├─ widget_data.extract_widget_animations(content) → List[str]
    └─ widget_data.extract_widget_variables(content) → List[WidgetVariable]
    ↓
BlueprintReport (immutable dataclass)
    ↓
formatters (markdown, JSON, C++) consume and render
```

Each extractor is **independent**. If you need to add support for (say) animation timelines, you'd:

1. Create `extract_animation_timeline(content: str) -> List[AnimationTimeline]`
2. Add a field to `BlueprintReport`
3. Call it in `build_blueprint_report()`
4. Update formatters to emit it
5. Add tests

No inheritance ceremony. No shared mutable state. No polymorphic dispatch.

### Detailed Parser Structure

Each parser module follows this pattern:

**Inputs:**

- Raw blueprint text, or
- Already-extracted intermediate structures (e.g., `GraphBlock` from block extraction)

**Outputs:**

- Typed dataclass from `models.py` (e.g., `VariableInfo`, `WidgetBinding`, `GraphSummary`)

**Internal tools:**

- Compiled regex patterns at module scope (e.g., `FUNCTION_REF_RE`)
- Helper functions (e.g., `_sanitize_name()`, `_extract_tail_id()`)
- No global state, no side effects

**Example: Variable Parsing**

```python
# In parsers/variable_parsing.py

CONTAINER_RE = re.compile(r"ContainerType=([A-Za-z]+)")

def parse_variable_entry(entry: str) -> Optional[VariableInfo]:
    """Translate raw variable metadata into structured record.

    @param entry: Raw variable metadata text.
    @return: Structured variable info or None if name not found.
    """
    name = extract_variable_name(entry)
    if not name:
        return None

    category = parse_category(entry) or "Uncategorized"
    pin_category, pin_subcategory = parse_pin_type(entry)
    # ... more extraction

    return VariableInfo(
        name=name,
        category=category,
        var_type=type_label,
        container=parse_container_type(entry),
        subtype=subtype,
    )
```

**No class. No inheritance. Just input → logic → output.**

### Summary

This architecture prioritizes:

- **Clarity**: Each parser is a self-contained function with a clear contract
- **Testability**: Pure functions, no mocks or fixtures
- **Flexibility**: Parsers evolve independently; new ones plug in without touching existing code
- **Alignment with clean code**: Single responsibility, one abstraction level per module

If you're adding a new parser, follow this pattern. Don't reach for inheritance unless you genuinely have multiple implementations of the same interface—which is rare in a single-purpose tool like blueprint-cleaner.
