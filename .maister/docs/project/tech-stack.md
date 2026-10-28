# Technology Stack

## Overview

This document describes the technology choices and rationale for **eagan_mcp** — an MCP
server that drives Haken EaganMatrix hardware (EM Module) over USB-MIDI.

The stack is deliberately tiny. This is a protocol-translation layer between an LLM agent
and a MIDI device: there is no web surface, no persistence layer and no user-facing UI, so
anything that would normally pull in a framework has been left out on purpose.

**Hard constraint (user-stated, 2026-10-26):** no new runtime dependencies; dev groups
decided case by case. The runtime set stays `mcp`, `mido` and `python-rtmidi` unless there
is a concrete justification; a dev-only group is a normal choice and `pytest>=8` was
approved on exactly that basis. Prefer the standard library either way.

## Languages

### Python (>=3.11, <3.13)

- **Usage**: 100% of the codebase (4556 lines across 8 non-empty modules; `__init__.py` is
  empty) plus 2643 lines of tests
- **Pinned in**: `pyproject.toml` (`requires-python = ">=3.11,<3.13"`) and `.python-version`
- **Rationale**: the MCP Python SDK is the reference implementation, and `mido` /
  `python-rtmidi` are the mature MIDI stack for Python. The `<3.13` ceiling exists because
  `python-rtmidi` ships compiled wheels and lags new CPython releases.
- **Key features used**:
  - Modern builtin generics and union syntax — `list[dict]`, `str | None`, `dict[int, int]`
  - `threading` + `collections.deque` for the MIDI receive buffer
  - Decorator-based registration (`@mcp.tool()`)

## Frameworks

### Frontend

None. There is no UI surface of any kind — no HTML, CSS, templates or web assets. The
"frontend" is whatever MCP client the user runs (Claude Desktop or Claude Code).

### Backend

#### FastMCP, via `mcp[cli]` (>=1.2, <2)

- **Import path**: `mcp.server.fastmcp.FastMCP`
- **Usage**: all 32 tools in `eagan_mcp/server.py` are registered with `@mcp.tool()`
- **Transport**: stdio. The server is launched on demand by the MCP client, not hosted.
- **Rationale for the `<2` ceiling**: MCP SDK 2.x renamed and reorganised FastMCP. The pin
  is intentional and must not be relaxed without porting `server.py`.

#### No web framework, no ORM, no database client

Nothing is persisted between runs except opaque capture files under `captures/`.

### Testing

#### pytest (>=8), dev group only

- **Declared in**: `pyproject.toml` `[dependency-groups] dev`, never in
  `[project.dependencies]`, so it does not reach the wheel
- **Configured by**: `[tool.pytest.ini_options]`, which sets `testpaths = ["tests"]` and
  nothing else
- **Suite**: 106 tests in 16 files, 2643 lines, about 1.5 s with
  `.venv/Scripts/python.exe -m pytest`
- **Scope**: host-only by construction. No test opens a MIDI port, so the suite covers the
  pure codecs, the offline preset-file parse path against four committed fixtures in
  `tests/fixtures/`, the flash-path pre-scan, the shipped JSON artifacts, tool validation,
  the three skills and the knowledge documents as text - and no device behaviour at all

See `../standards/testing/test-writing.md` for what the suite deliberately leaves to the
device and to a human.

Validation of device behaviour therefore remains a three-part manual loop:

1. **Read-back verification inside the tools** — write tools such as `set_matrix_point`,
   `set_formula` and `set_osc_type` re-read device state and report whether the change took.
2. **Hardware testing** against the real EM Module, with the verification date recorded in
   `CLAUDE.md` next to each finding.
3. **Listening tests** — one change at a time, then a yes/no question to the user.

## Database

None. No relational store, no NoSQL store, no ORM, no cache.

The authoritative state lives on the device itself (edit slot, 128 user slots, system
slots). Captured device dumps are written to `captures/` as `.mid` files for later diffing;
they are artifacts, not a datastore.

## Build Tools & Package Management

| Concern | Tool | Notes |
|---|---|---|
| Package manager | `uv` | `uv sync` to install, `uv run` to execute |
| Lock file | `uv.lock` | revision 5, ~90 KB, full transitive pinning |
| Build backend | `hatchling` | declared in `[build-system]` |
| Virtual env | `.venv/` | created and managed by `uv sync` |

### Entry points

```
eagan_mcp     = "eagan_mcp.server:main"        # the MCP server
eagan_sniff   = "eagan_mcp.sniff:main"         # standalone MIDI capture CLI
eagan_catalog = "eagan_mcp.preset_file:main"   # offline factory-catalog rebuild
```

## Infrastructure

### Containerization

None, and none is appropriate — the process needs direct access to a physical USB-MIDI
device on the host.

### CI/CD

None, by choice. The project IS a git repository (branch `master`, no remote configured), so a pipeline could be attached - there just isn't one, and CI is on the explicit not-a-goal list. The 118-test suite runs in about 5 s locally, which is the whole gate.

### Hosting

Not hosted. The server runs locally as a subprocess of the MCP client:

```
claude mcp add eagan -- <venv>/Scripts/eagan_mcp.exe
```

## Development Tools

### Linting & Formatting

None configured — no `ruff`, `black`, `flake8` or `pylint` config exists. Style is
consistent by hand: 4-space indentation, 80–100 character lines, `snake_case` throughout,
`UPPER_SNAKE_CASE` for protocol constants, `PascalCase` for classes.

### Type Checking

None configured — no `mypy` or `pyright` setup. Type hints are present on essentially every
function signature but are not verified at build time, so they document intent rather than
enforce it.

## Key Dependencies

| Dependency | Constraint | Role |
|---|---|---|
| `mcp[cli]` | `>=1.2,<2` | MCP server framework (FastMCP 1.x), tool registration, stdio transport |
| `mido` | `>=1.3` | MIDI message construction and parsing, `.mid` file read/write |
| `python-rtmidi` | `>=1.5` | `mido` backend providing actual Windows USB-MIDI port access |

Three direct runtime dependencies. That is the whole runtime list, and it should stay that
way. One dev-only addition sits outside it: `pytest>=8` in `[dependency-groups] dev`.

## External References (not dependencies)

These are consulted but not imported:

- `docs/HakenMidi.h` — the official protocol header, firmware 10.81. **Source of truth.**
- `docs/` — firmware 10.81 user guides as extracted text, searched by `search_docs`
- `docs_1044/` — the older 10.44 guides, kept only for diffing against 10.81
- `ref/pachde-CHEM/` - pachde CHEM, Controller for the Haken Eagan Matrix (VCV Rack plugin,
  C++), the reference for live device handling
- `ref/cohem/` - pachde cohem, a compiler/decompiler between preset `.mid` files and plain
  text. A separate project from CHEM, and the reference for the offline preset-file format
- `HAKEN_EDITOR_DIR` — Haken Editor install, read for factory preset descriptions

## Version Management

- Python runtime: floor and ceiling in `pyproject.toml`, exact version in `.python-version`
- Dependencies: minimum versions in `pyproject.toml`, exact resolution in `uv.lock`
- **Firmware** is the version that matters most in practice. The device runs **10.81**
  (since 2026-10-25). Protocol findings in `CLAUDE.md` are tagged with the firmware they
  were verified against, because a firmware change can invalidate them.
- Project version: `0.1.0`, not yet published anywhere.

## Platform Constraints

- **OS**: Windows 10 is the only tested host. Paths in config and docs are Windows-shaped.
- **Device**: EaganMatrix Module over USB-MIDI, ports named
  `"EaganMatrix Module <serial> 3"` (in) / `"... 4"` (out), the serial being per-unit. The
  code never hardcodes it: `DEFAULT_PORT_HINT` is the substring `"EaganMatrix"`.
- **Port exclusivity**: Windows USB-MIDI ports are normally exclusive, so the Haken Editor
  and this server cannot hold the device at the same time. Multi-client access (Windows
  MIDI Services) is untested.

---
*Last Updated*: 2026-10-26
*Auto-detected*: language and version bounds, package manager, lock file, build backend,
dependencies and constraints, entry points, module count and line counts, tool count, test
count and suite scope, absence of linting / type checking / CI, naming and typing
conventions.
*User-provided*: the no-new-runtime-dependencies constraint.
