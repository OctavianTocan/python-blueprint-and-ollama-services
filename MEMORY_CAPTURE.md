# Memory Capture Queue

Learnings and patterns to add to memory systems (openmemory/pieces LTM) once services become available.

## Python Utilities Architecture

### Modular Clean Code Patterns

1. **Single Responsibility Functions**

   - Keep functions 5-10 lines (max 20)
   - One level of abstraction per function
   - Extract helpers when logic has meaningful name
   - Stepdown rule: arrange functions in descending abstraction

2. **Toolkit Pattern**

   - Created `src/toolkit` with reusable utilities
   - text_parsing: regex helpers, metadata extraction
   - file_io: encoding detection, UTF-8/UTF-16 handling
   - collections: deduplication preserving order
   - formatting: inline lists, item decoration
   - console: metric summaries, progress output

3. **Parser/Formatter Separation**

   - Split extraction logic into `parsers/` subpackage
   - Split rendering into `formatters/` subpackage
   - Orchestration modules coordinate focused helpers
   - Clear separation of concerns improves testability

4. **Project Structure Template**
   ```
   project/
   ├── src/project_name/
   │   ├── parsers/          # Data extraction
   │   ├── formatters/       # Output rendering
   │   ├── models.py         # Data structures
   │   ├── pipeline.py       # Orchestration
   │   └── ...
   ├── data/
   │   ├── in/               # Input files
   │   └── out/              # Generated output
   ├── tests/                # Test scaffolds
   ├── README.md             # Rich documentation
   └── pyproject.toml        # uv project config
   ```

## Blueprint Cleaner Implementation

### Parsing Strategy

- Block extraction: Locate graph/node boundaries
- Classification: Categorize by naming patterns
- Node analysis: Extract calls, variables, comments
- Variable collection: Balanced parenthesis matching

### Output Formats

- Markdown: Human-readable summaries with tables
- JSON: Machine-readable structured data
- Inline lists: Truncated with overflow indicators

## Pieces Service Wrapper

### Client Simplification

- ask_copilot_question: Main entry point
- stream_copilot_response: Handle SDK streaming
- strip_markdown_code_blocks: Clean formatting

### API Design

- Dual interfaces: REST (GET/POST) + FastMCP
- Request tracking: UUID per request
- Structured logging: Request/response metrics
- Error handling: HTTP exceptions with details

## Unified API Pattern

### Multi-Service Facade

- Single endpoint exposing multiple utilities
- File uploads for blueprint processing
- Query forwarding to copilot
- FastMCP integration for both services

### Dependency Management with uv

- Editable local dependencies via `tool.uv.sources`
- Shared toolkit across projects
- Python 3.13+ for modern features

## Documentation Standards

### Doxygen-Style Comments

- @param for all parameters with role/constraints
- @return for outcomes and conditions
- @raises for exceptions with triggers
- Brief descriptions in present tense
- No function left undocumented (public or private)

### README Structure

- Quick Start with uv commands
- Project Structure tree
- Architecture explanation
- API documentation with examples
- Clear license statement

## Testing Approach

### Scaffolding Without Enforcement

- Create test directories upfront
- Placeholder tests to prevent import errors
- TESTING.md roadmap for future implementation
- User will implement when ready to learn patterns

## Key uv Commands

```bash
uv init --package                    # Create new package
uv sync                              # Install dependencies
uv add toolkit --editable --path ../ # Local editable dependency
uv run command                       # Run in virtual env
```

## Lessons Learned

1. **Start with small, focused modules** - easier to understand and compose
2. **Shared toolkit prevents duplication** - common utilities reusable across projects
3. **Documentation prevents context loss** - rich READMEs and inline docs essential
4. **Test scaffolds without pressure** - structure ready when user wants to learn
5. **FastMCP + FastAPI** - powerful combo for unified service exposure
6. **data/in and data/out** - clear organization improves discoverability

## Next Steps When Services Available

1. Retry memory capture with these learnings
2. Add specific code examples for each pattern
3. Document edge cases encountered
4. Share uv + Python 3.13 setup quirks
5. Include FastMCP integration gotchas

---

_Prepared: Oct 29, 2025_
_Tools: uv 0.9.2, Python 3.13, FastAPI, FastMCP_
