# Example .COPY Files

This directory contains both full-sized blueprint exports and minimal example `.COPY` files to help you understand the parser.

## Minimal Examples

These are intentionally simple and well-documented to serve as learning material:

### EXAMPLE_BP_SimpleCharacter.COPY

A **standard character Blueprint** with:

- Two event graphs (BeginPlay, DeathEvent)
- Multiple node types (Event, CallFunction, VariableSet, Comment)
- Three blueprint variables (Health, MaxHealth, IsAlive)
- Developer comments explaining each section

**Good for learning:**

- How graphs are structured
- What node types look like
- Variable metadata format
- Comment node usage

**Try it:**

```bash
uv run blueprint-cleaner data/in/EXAMPLE_BP_SimpleCharacter.COPY -f json
```

---

### EXAMPLE_WBP_SimpleUI.COPY

A **Widget Blueprint (UMG)** with:

- Widget tree structure (Canvas, Button, TextBlock, Image)
- Widget variable mapping (button, text, image references)
- UMG bindings (Button enabled state, text color)
- Animations (fade-in, hover effect)
- One event graph (Construct event)

**Good for learning:**

- UMG-specific structure (WidgetTree, Bindings, Animations)
- Widget variable naming and GUIDs
- Property → Function bindings
- Widget blueprint differences from standard blueprints

**Try it:**

```bash
uv run blueprint-cleaner data/in/EXAMPLE_WBP_SimpleUI.COPY -f json
```

---

### EXAMPLE_BP_GameSettings.COPY

A **Data Asset Blueprint** with:

- Minimal graph structure
- Four different variable types (Int, String, Bool, Enum)
- Variable categorization
- Entry/Get/Return node pattern

**Good for learning:**

- Minimal viable blueprint structure
- Variable type representation
- How data assets differ from standard blueprints
- FunctionEntry → Get → FunctionResult flow

**Try it:**

```bash
uv run blueprint-cleaner data/in/EXAMPLE_BP_GameSettings.COPY -f json
```

---

## Full-Sized Examples

The other `.COPY` files in this directory are real-world exports from a game project. They're more complex but show realistic structures:

- **BP_IG_Character.COPY** - Complex character with many graphs and nodes
- **WBP_HUD_02.COPY** - Full UI widget with extensive bindings and animations
- **ABP_IG_Character.COPY** - Animation Blueprint
- **BP_IG_Gun.COPY** - Weapon Blueprint
- **DA_IG_Pistol_AnimBP_Settings_BODYCAM.COPY** - Data table settings

**These are useful for:**

- Understanding parser scalability
- Testing with realistic complexity
- Seeing edge cases and patterns

---

## Parsing Examples

### View minimal example as Markdown:

```bash
uv run blueprint-cleaner data/in/EXAMPLE_BP_SimpleCharacter.COPY -f markdown
```

### View as JSON:

```bash
uv run blueprint-cleaner data/in/EXAMPLE_WBP_SimpleUI.COPY -f json
```

### Compare outputs:

```bash
# Generate all formats for a simple example
uv run blueprint-cleaner data/in/EXAMPLE_BP_GameSettings.COPY -f markdown -o /tmp/gs.md
uv run blueprint-cleaner data/in/EXAMPLE_BP_GameSettings.COPY -f json -o /tmp/gs.json
```

---

## For Developers

If you're working on the parser:

### Quick validation:

```bash
# Should extract 3 graphs from simple character
uv run blueprint-cleaner data/in/EXAMPLE_BP_SimpleCharacter.COPY -f json | grep graphs

# Should find widget bindings in the UI example
uv run blueprint-cleaner data/in/EXAMPLE_WBP_SimpleUI.COPY -f json | grep bindings
```

### Debugging parser issues:

1. Start with **EXAMPLE_BP_GameSettings.COPY** (smallest, simplest)
2. Move to **EXAMPLE_BP_SimpleCharacter.COPY** (multiple graphs)
3. Test widget support with **EXAMPLE_WBP_SimpleUI.COPY**
4. Validate scalability with full examples

### File sizes:

- EXAMPLE_BP_GameSettings.COPY: ~2 KB (data asset, minimal)
- EXAMPLE_BP_SimpleCharacter.COPY: ~3 KB (character, multiple graphs)
- EXAMPLE_WBP_SimpleUI.COPY: ~2.5 KB (widget, bindings + animations)
- BP_IG_Character.COPY: ~75 MB (real game blueprint, complex)

**Tip:** If you hit a parser bug, try to reproduce it with one of the minimal examples first. They're much easier to debug than the full-sized files.

---

## Understanding the Structure

See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for an in-depth explanation of how `.COPY` files are structured and what the parser extracts.

See [../docs/PARSER_PATTERN.md](../docs/PARSER_PATTERN.md) if you want to understand how to add new parsers.
