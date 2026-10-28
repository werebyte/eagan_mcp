## Coding Style

### Naming Consistency
Follow established naming patterns for variables, functions, classes, and files throughout the project.

This project is Python only (`CLAUDE.md`: "Python, snake_case everywhere"):
- **snake_case** for modules, functions, parameters, locals and MCP tool names — 32 of 32 tool functions follow it (`get_matrix`, `set_matrix_point`, `load_and_capture_preset`).
- **UPPER_SNAKE_CASE** for module-level protocol constants — 286 of 286 (`CC_EDITOR_PING = 116`). The only module-level names that are not UPPER_SNAKE_CASE are the two live singletons `mcp` and `conn` in `server.py`, correctly lowercase because they are instances, and twelve private tables that carry the leading underscore in front of the same upper-case spelling (`_X_IDS`, `_CENSUS`).
- **PascalCase** for classes — 3 of 3 (`EmConnection`, `midi_io.py:25`; `PresetFileError`, `preset_file.py:309`; the private `_MatrixBuilder`, `preset_file.py:399`).
- **Leading underscore** for private module-level helpers (37 functions, plus the twelve private constant tables above); they are not exported or imported across modules. One deliberate deviation: `sniff.py:13` imports `_find` from `midi_io`.

### Automatic Formatting
This project deliberately has **no formatter, linter or type checker configured** — `pyproject.toml` holds `[project]`, `[project.scripts]`, `[dependency-groups]`, `[build-system]` and exactly one `[tool.*]` table, `[tool.pytest.ini_options]`, which sets `testpaths` and nothing about style; there is no ruff/black/isort/mypy config, `.editorconfig`, pre-commit hook or CI (`config` scan). Style is carried by prose rules in `CLAUDE.md` and by matching the surrounding code. Do not assume a tool will fix formatting or catch type errors, and do not add a linter or CI config as a side effect of another task — that is a project-level decision.

The hand-kept conventions, uniform across all 8 non-empty modules:
- 4-space indent, no tabs (0 tab-indented lines).
- Soft ~100 column limit (13 of 4556 lines exceed it; longest 117).
- f-strings for every interpolation (120 f-strings, 0 uses of `%` or `str.format()`).
- Multi-entry constant tables aligned so they read as tables.

### Descriptive Names
Choose names that clearly communicate intent; avoid cryptic abbreviations or single-letter identifiers outside tight loops.

### Focused Functions
Write functions that do one thing well; smaller functions are easier to read, test, and maintain.

### Uniform Indentation
Standardize on spaces or tabs and enforce with editor/linter settings.

### No Dead Code
Remove unused imports, commented-out blocks, and orphaned functions instead of leaving them behind.

### No Backward Compatibility Unless Required
Avoid extra code paths for backward compatibility unless explicitly needed.

### DRY (Don't Repeat Yourself)
Extract repeated logic into reusable functions or modules.

### Builtin Generics and PEP 604 Unions
Modern annotation syntax only: builtin generics (`list[dict]`, `dict[int, int]`, `tuple[int, int]`) and `X | None` unions. The `typing` module is never imported — 0 imports across 8 non-empty modules, 0 uses of `Optional`/`List`/`Dict`. Annotate the return type of everything that returns a value (32 of 32 MCP tools, 124 of 133 module-level functions); only `None`-returning procedures and trivial internal helpers are left bare. Boundary returns are the unparameterised `dict`; internal functions carry precise element types.

```python
def encode_value(value: str) -> list[tuple[int, int]]: ...
def list_user_presets(seconds: float = 6.0, search: str | None = None) -> dict: ...
```

### Grouped Imports, Relative Within Package
Imports are module-level only — 0 inline or function-local imports in 4556 lines. Group them stdlib, then third-party, then local, one blank line between groups, with plain `import x` before `from x import y` inside a group. Intra-package imports are always relative. Pure data/codec modules (`formula.py`, `setup.py`, `matrix_map.py`) import nothing at all.

```python
import os
import time

import mido
from mcp.server.fastmcp import FastMCP

from . import formula, haken, matrix_map, midi_io, setup
```
