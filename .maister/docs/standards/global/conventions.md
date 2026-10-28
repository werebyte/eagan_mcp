## Development Conventions

### Predictable Structure
Organize files and directories in a logical, navigable layout.

**Layered modules: I/O, wire, codec.** Three strict layers, each module's docstring stating its own boundary: `midi_io.py` owns ports, threading and buffering and knows no Haken semantics; `haken.py` builds and parses messages and never performs I/O; `formula.py`, `setup.py` and `matrix_map.py` are pure tables plus pure functions over an already-decoded `{id: value}` dict and import nothing at all. `server.py` is the only module holding the connection and the only one with MCP decorators. No module imports `server.py`; there are no cycles. `preset_file.py` is a second consumer of the same codec layer, not a parallel codec: it decodes preset `.mid` files offline and imports `formula.py`, `setup.py` and `matrix_map.py` for every value table, default and name rather than restating any of them. `sniff.py` sits beside the server as a standalone capture CLI and shares nothing but `midi_io.py`. Note the evidence-quality split: `haken.py` encodes documented protocol, while `formula.py` and `setup.py` are reverse-engineered — keep that distinction visible when moving code between them, and a new consumer must not blur it either.

**Console-script entry points via uv.** Every executable surface is a named console script under `[project.scripts]` pointing at a module-level `main()`; the build backend is hatchling with a flat `eagan_mcp/` package (no `src/` layout, no `setup.py`). Invoke through `uv run <script>`, never `python path/to/file.py`. A new runnable tool means a module with `main()` plus a script entry, not a loose script file.

**Keep protocol findings, plan, recipes and the knowledge base in separate documents.** The documents have fixed, non-overlapping roles: `CLAUDE.md` = protocol details and findings; `ROADMAP.md` = the plan and its completion tracking only; `RECIPES.md` = synthesis vocabulary mapped to matrix cells and formulas, tested on the Module by ear; `README.md` = setup plus the safety rule; and a documented fifth role, `eagan_mcp/knowledge/` = the shipped knowledge base an agent reads before building a patch (`model.md`, `modules/`, `patterns.md`, `pitfalls.md`, `worked_examples.md` - 23 markdown documents in all), evidence-graded per `.maister/docs/standards/protocol/protocol-sources.md` and served through the MCP rather than read by a human. Residue rule between the fourth role and the fifth: **a pitfall inseparable from a recipe's steps stays in `RECIPES.md` as that recipe's context; standalone pitfalls are canonical in `eagan_mcp/knowledge/pitfalls.md`** - the same split applies to any fact a recipe cannot be followed without. Two further documents sit outside the five and under the same no-duplication rule: `tools_spec.md` = the specification of tools that do not exist yet, never a description of shipped behaviour; `RESEARCH_REPORT.md` = one research pass's findings and their provenance, never a standard. Cross-reference between all of them; never duplicate.

**Shipped data lives inside the package, and that is a deliberate departure.** `server.py` builds
every other path from `PROJECT_DIR = Path(__file__).resolve().parent.parent` - the repository root -
so `docs/` and `captures/` sit beside the package. `KNOWLEDGE_DIR` is the one exception:
`Path(__file__).resolve().parent / "knowledge"`, inside `eagan_mcp/` itself. The reason is
distribution, not taste: the knowledge base and its four JSON artifacts are shipped data an
installed wheel must carry, and anything resolved from the repository root is absent once the
package is installed somewhere else. This also departs from the research brief, whose deliverables
table places them at `knowledge/` in the repository root (`research-brief.md` section 6, an
untracked task artifact under `.maister/tasks/`); the shipped layout is `eagan_mcp/knowledge/`.
A new shipped data file goes there, under `KNOWLEDGE_DIR`, never under `PROJECT_DIR`.

### Up-to-Date Documentation
Keep README files current with setup steps, architecture overview, and contribution guidelines.

**Module docstrings must track reality.** Docstrings here carry protocol facts and firmware versions, so a stale one is a correctness risk, not a cosmetic issue. When a source of truth changes (new firmware, header obtained, feature shipped), every docstring citing it changes in the same edit.

FIXED - the three module docstrings that described the pre-10.81 state (`server.py:3-4`, `haken.py:1`/`:8`, `midi_io.py:2`, all claiming the header was unavailable and matrix editing unimplemented) now describe reality. But two of them went stale again by 2026-10-27, for a different reason: they called the ch15 preset-file format "still undecoded" after `preset_file.py` had decoded it for 422 of the 668 factory files. That is exactly the failure mode this rule exists to catch, and it recurred inside a single pass - so when a source of truth changes, grep for every docstring that cites it in the same edit rather than trusting a hand-kept list like this one to stay current.

### Clean Version Control
Write clear commit messages, use feature branches, and add meaningful descriptions to pull requests.

**Vendored reference and device captures stay out of version control.** `.gitignore` excludes whole regenerable directories — `ref/`, `docs/`, `_to_delete/`, `__pycache__/`, `.venv/`, `captures/` — so new vendor copies, extracted guides and capture output go into those existing directories and the command that regenerates them belongs in `README.md`. `uv.lock` is deliberately NOT ignored: the pinned resolution is shared, the installed environment is not.

UNRESOLVED CONFLICT: `.gitignore` excludes `docs/`, yet `CLAUDE.md` names `docs/HakenMidi.h` the protocol source of truth. The authoritative reference is therefore untracked and must be re-extracted from the Haken Editor install on every machine.

### Environment Variables
Store configuration in environment variables; never commit secrets or API keys.

`HAKEN_EDITOR_DIR` is the only environment variable in the package: read at import time with a hardcoded default (`server.py`, `EDITOR_DIR` and the `DESCRIPTIONS_DIR` beneath it - cited by symbol, because those lines move) plus a layout fallback for the older Editor directory structure, so the server starts unconfigured. There is no `.env`, settings module or config file — one documented variable per external dependency, listed in `README.md`.

WEAKNESS: the default is one machine's absolute Windows path, so anyone else must set the variable.

### Minimal Dependencies
Keep dependencies lean and up-to-date; document why major ones are included.

Exactly three runtime dependencies: `mcp[cli]`, `mido`, `python-rtmidi`. A dependency gets an upper bound only when a known upstream break exists, and the reason is recorded. `mcp[cli]>=1.2,<2` is capped because MCP SDK 2.x renamed/moved FastMCP, which `server.py:11` imports as `from mcp.server.fastmcp import FastMCP` — the pin must not be relaxed without porting `server.py`. `mido>=1.3` and `python-rtmidi>=1.5` carry floors only. Hard constraint (user-stated): no new runtime dependencies; dev groups decided case by case - `pytest>=8` was approved on exactly that basis and sits in `[dependency-groups] dev`, never in `[project.dependencies]`, so it never reaches the wheel and an installed `eagan_mcp` still needs only the three above. Prefer the standard library either way.

### Consistent Reviews
Follow a defined code review process with clear expectations for reviewers and authors.

### Testing Standards
Define required test coverage (unit, integration, etc.) before merging.

### Feature Flags
Use flags for incomplete features instead of long-lived branches.

### Changelog Updates
Maintain a changelog or release notes for significant changes.

DISPOSITION: this project has no changelog file and deliberately does not add one. The role split
above governs instead - `ROADMAP.md` is the plan and its completion tracking, and
`RESEARCH_REPORT.md` is the dated record of a research pass. Between them they carry what a
changelog would, at the granularity the project actually works in. Source documents therefore carry
no change-history, no "updated on" line and no edit date; a fact that has changed is rewritten in
place, not appended to.

### Build What's Needed
Avoid speculative code and "just in case" additions (see minimal-implementation.md).

### Bounded Interpreter Window
Python is constrained at both ends: `requires-python = ">=3.11,<3.13"`, with `.python-version` pinning 3.12 as the working interpreter. The ceiling is deliberate — `python-rtmidi` is a C extension, so a newly allowed interpreter needs a usable wheel or build. Raising it means editing `pyproject.toml` and `.python-version` and re-running `uv lock` in one change, after confirming `python-rtmidi` builds there. Keep `pyproject.toml`, `.python-version` and `uv.lock`'s `requires-python` in agreement.

### Flat dict Result Envelope with Echoed Request
MCP tools return a flat dict of primitives that echoes the request (`requested`, `row`/`col`, `slot`) next to what the device reports (`device_value`, `name_at_slot`), plus a count field for anything list-shaped. Partial or unknown results are represented as fields rather than omitted — e.g. `verified: None` when the device cannot echo the value back. Nesting appears only where the device data is genuinely nested.

```python
return {"id": pid, "requested": value, "device_value": after.get(pid),
        "verified": after.get(pid) == value}
```
