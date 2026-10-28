# Documentation Index

**IMPORTANT**: Read this file at the beginning of any development task to understand available documentation and standards.

## Quick Reference

### Project Documentation
Project-level documentation generated from codebase analysis: **vision**, **tech-stack**, **architecture**. The roadmap lives at the repository root (`ROADMAP.md`).

### Technical Standards
Coding standards, conventions, and best practices organized by domain. Initialized categories: **global**, **protocol**, **testing**.

---

## Project Documentation

Located in `.maister/docs/project/`

#### Vision (`project/vision.md`)
What eagan_mcp is — an MCP server that turns a plain-words sound description into the MIDI
traffic that builds it on a Haken EaganMatrix Module. Covers current state (early-production
MVP, Python 3.11–3.12, 4556 lines across 8 non-empty modules, 32 MCP tools, 23 shipped
knowledge documents and a 106-test host-only suite), an explicit verified-vs-not
split of device capabilities, the three pillars (a cited protocol, the `RECIPES.md` vocabulary
bridge, the edit-slot safety contract), the three prioritised 6–12 month goals (plain-words
patch building, finishing the protocol decode, a recipe library tested by ear), what is
deliberately *not* a goal right now (linting, type checking, CI - test coverage no longer in
that list, but the suite is host-only and closes no device-test item), and the project's
three-phase evolution from blind protocol work to firmware 10.81.

#### Technology Stack (`project/tech-stack.md`)
The deliberately tiny stack and the reasoning behind each choice: Python `>=3.11,<3.13` (the
ceiling exists because `python-rtmidi` ships compiled wheels), FastMCP via `mcp[cli]` `>=1.2,<2`
over stdio (the `<2` pin is intentional — 2.x reorganised FastMCP), `mido` + `python-rtmidi` for
MIDI. Records the user-stated hard constraint of no new runtime dependencies; dev groups decided
case by case (`pytest>=8` sits in `[dependency-groups] dev` and never reaches the wheel), the
absence of a frontend, database, linting, type checking, containers and CI, the `uv` +
`hatchling` + `uv.lock` toolchain, all three entry points (`eagan_mcp`, `eagan_sniff`,
`eagan_catalog`), the 106-test host-only suite and the three-part manual loop that still carries
every device claim, external references that are consulted but not imported
(`docs/HakenMidi.h`, `docs/`, `docs_1044/`, `ref/pachde-CHEM/` for pachde CHEM and `ref/cohem/`
for pachde cohem - two separate projects), firmware as the version that matters
most, and the Windows / USB-MIDI port-exclusivity platform constraints.

#### System Architecture (`project/architecture.md`)
The layered protocol stack behind a tool facade: `server.py` (32 tools) over the codec layer
(`haken.py` documented protocol, `formula.py` stream 19, `setup.py` stream 20, `matrix_map.py`
name tables) over `midi_io.py` transport, with `preset_file.py` as an offline consumer of the same
codecs and `sniff.py` as a standalone capture CLI beside the server. Explains why the codec layer
is split by evidence quality (documented vs reverse-engineered) and that the split should survive
refactoring.
Includes the tool-group table, per-module responsibilities and key details (the formula split
sign encoding, `EmConnection`'s buffered deque), the read and write data flows with the two
device behaviours that force their shape (select-then-read, verify by a *separate* read), the
streams in use (0, 1, 15, 19, 20), external integrations, configuration and its known
weaknesses, the four architectural safety rules (edit slot by default, never the `cc0=127`
system-slot path, `send_preset_file` input screening, stores verified via `list_user_presets`),
the stdio deployment model, and the recorded architectural gaps (no CI and a deliberately
host-only suite, no type checking, no logging, hardcoded config, no retry policy, the import-time
MIDI dependency that the knowledge tools inherit, and `preset_file.py`'s two disagreeing
matrix-row labelling paths).

**Note**: `project/roadmap.md` is intentionally absent — the project's roadmap lives at the
repository root in `ROADMAP.md`.

**Note**: This project also maintains substantial hand-written documentation at the repository root, which remains authoritative for device/protocol work:

- `CLAUDE.md` - firmware 10.81 protocol findings, verified MIDI/matrix/formula semantics, session handoffs
- `RECIPES.md` - patch-building recipes, each tested on the Module by ear. Standalone pitfalls are no longer here: they are canonical in `eagan_mcp/knowledge/pitfalls.md`, and only a pitfall inseparable from a recipe's steps stays with that recipe
- `ROADMAP.md` - development roadmap and its completion tracking
- `README.md` - project overview, setup and the safety rule
- `tools_spec.md` - ranked specifications (`T1`..`T22`) for tools that do not exist yet; never a description of shipped behaviour
- `RESEARCH_REPORT.md` - one research pass's findings and their provenance; never a standard
- `eagan_mcp/knowledge/` - the shipped knowledge base an agent reads before building a patch (`model.md`, `modules/`, `patterns.md`, `pitfalls.md`, `worked_examples.md`), served through the `get_knowledge` MCP tool rather than read by a human. Every claim carries exactly one evidence tag per `standards/protocol/protocol-sources.md`
- `.claude/skills/` - the patch skills (`eagan-patch-design`, `eagan-patch-debug`, `eagan-factory-mining`) that route every device fact through the knowledge, recipe and factory-catalog tools
- `docs/` - the user guides as text, stamped firmware 10.61 to 10.80, plus `HakenMidi.h`, which is the 10.81 protocol source of truth; `docs_1044/` keeps the older 10.44 guides for diffing

---

## Technical Standards

### Global Standards

Located in `.maister/docs/standards/global/`

#### Coding Style (`standards/global/coding-style.md`)
Naming consistency (snake_case everywhere, `UPPER_SNAKE_CASE` protocol constants, `PascalCase`
classes, leading-underscore private helpers, with the one recorded deviation), the deliberate
absence of any formatter/linter/type-checker - `[tool.pytest.ini_options]` is the one `[tool.*]`
table and configures the runner, not style - and the hand-kept conventions that replace it
(4-space indent, soft ~100 columns, f-strings only, aligned constant tables), descriptive names,
focused functions, uniform indentation, no dead code, no backward-compatibility layers unless
required, DRY, builtin generics and PEP 604 unions with `typing` never imported and return types
annotated, and grouped module-level imports (stdlib / third-party / local) that are relative
within the package.

#### Commenting (`standards/global/commenting.md`)
Let code speak for itself; comment sparingly — docstrings on the public surface only (all 32 MCP
tools, one of `server.py`'s 14 private helpers), and an MCP tool docstring treated as the prompt the agent
reads: it must state the write scope, units, ranges and exact accepted enum strings, plus safety
warnings, even when that runs long - the longest runs to 55 lines. No change-history or changelog
comments in source.

#### Development Conventions (`standards/global/conventions.md`)
Predictable structure (the strict I/O / wire / codec layering, console-script entry points via
`uv`, and the fixed non-overlapping roles of `CLAUDE.md`, `ROADMAP.md`, `RECIPES.md`, `README.md`,
`eagan_mcp/knowledge/`, `tools_spec.md` and `RESEARCH_REPORT.md`),
up-to-date documentation with module docstrings that must track firmware reality (including the
recorded stale-docstring defects), clean version control (vendored reference and captures stay
untracked, `uv.lock` deliberately tracked), environment variables (`HAKEN_EDITOR_DIR` only),
minimal dependencies with recorded upper-bound reasons and the no-new-runtime-dependencies
constraint (dev groups decided case by case),
consistent reviews, testing standards, feature flags, changelog updates, building only what's
needed, the bounded interpreter window (`>=3.11,<3.13` kept in sync across `pyproject.toml`,
`.python-version` and `uv.lock`), and the flat dict result envelope that echoes the request
alongside what the device reports.

#### Error Handling (`standards/global/error-handling.md`)
Clear user-facing messages, fail fast with no defensive try/except (device and MIDI errors
propagate; only 4 blocks exist, every one for expected control flow), typed exceptions on a fixed
split (`ValueError` for unencodable arguments, `RuntimeError` for environment/device conditions,
no custom classes), centralized handling, graceful degradation in which failure and doubt are
returned as data — a tri-state `verified` flag plus `note`/`warning`, raw values kept beside
unknown-scale interpretations, refusals returned normally — retry with backoff, and guaranteed
resource cleanup.

#### Minimal Implementation (`standards/global/minimal-implementation.md`)
Build only what you need now, give every artifact a clear purpose, delete exploration artifacts,
no future stubs, no speculative abstractions, review before commit, and treat unused code as
debt — with one documented carve-out: named protocol constants may be retained unused as the
project's wire-format reference, but only when annotated, and the carve-out never extends to
unused functions, classes or code paths. Also records the inverse defect (wire numbers hardcoded
although a named constant exists) and the rule: define the constant and then use it.

#### Validation (`standards/global/validation.md`)
Server-side validation always, client-side for feedback only, validate early — range and enum
checks at the top of a tool and whole payloads pre-scanned before a single MIDI byte is emitted,
with the one known violation named — specific errors that interpolate the allowed range or full
option list from the same lookup table the code consults, allowlists over blocklists, type and
format checks, input sanitization, business-rule validation, and consistent enforcement across
entry points.

### Protocol Standards

Located in `.maister/docs/standards/protocol/`

#### Device Safety (`standards/protocol/device-safety.md`)
The hard constraints protecting the Module's flash and the user's unsaved work: writes go to the
edit slot only, enforced in code with a `confirm: bool = False` refusal dict, payload pre-scans
and the write scope stated in the first docstring lines; never send the system-slot store path
(`cc0=127`) — user stores are `cc0=0` + `cc32`/`cc112`; never verify a store by loading the slot
(use the read-only `list_user_presets` name comparison, since loading destroys the edit slot and
the save echo varies); check the DSP budget with `get_status` after every big change and apply
the fixes in the given order; and respect the numbered patch-construction pitfalls from
`RECIPES.md` (shared drift LFO, macros off oscillator F columns, BiqBank rather than a delay loop
for bendable strings, build around Y for the mod wheel, always give a Continuous/Single Cycle SG
its T column).

#### Protocol Sources and Evidence (`standards/protocol/protocol-sources.md`)
How wire-format knowledge is allowed to enter the project: cite the protocol source and never
guess — formats come from `HakenMidi.h` with the header line cited, with a fixed fallback order
(firmware guides, the Haken Editor's MIDI logic, pachde CHEM) and citations placed at the
definition; mark every finding verified or unverified using the project's fixed vocabulary, with
date and firmware, surfacing uncertainty to the caller and recording source conflicts; and
confirm preset indices by capture with `load_and_capture_preset` rather than trusting the
printed list.

#### Device I/O (`standards/protocol/device-io.md`)
The required shape of every device read and write: verify a write with a separate independent
read (send, ~0.2 s settle, fresh read, return requested plus `device_value` and `verified`) and
distrust the post-write echo; select the target before writing with no traffic in between; retry
an empty read with a longer (~4 s) listen window; the flush / keepalive / request / bounded-listen
sequence with the window exposed as a `seconds: float` parameter and realtime noise filtered out;
and pick an unused formula letter after checking `get_matrix`, since the letters are shared
device-wide - 44 available (A..V plus A'..V'), A..V preferred - and all-zero cells are omitted
from the dump.

#### Codec Conventions (`standards/protocol/codec-conventions.md`)
How the pure wire-translation modules declare tables and name functions: lookup tables shaped
like the wire (a list when the device's values are a contiguous 0-based enumeration, a dict when
sparse), naming by wire role (`CC_*`, `CMD_*`, `*_ID`, `*_IDS`, plural value->name maps), derived
reverse maps, and unknown values decoded to a visible `?<n>` marker rather than raising or
dropping; plus codec function naming by direction (`decode*` in, `encode*`/`*_msgs`/`*_value`
out), one entry point per wire stream with an identical `decode(pairs) -> dict` signature, and
human rendering kept in a separate `summary()`.

### Testing Standards

Located in `.maister/docs/standards/testing/`

#### Test Writing (`standards/testing/test-writing.md`)
Opens with the project's actual position: a host-only suite of 106 tests in 16 files (2643 lines,
about 1.5 s) covers the pure codecs, the preset-file parse path on four committed fixtures, the
flash-path pre-scan, the shipped JSON artifacts, tool validation, the three skills and the 23
knowledge documents as text - and deliberately covers nothing that needs the Module, so a green
run closes no device-test item and cannot say whether a device claim is *true*. Device validation
stays hardware-based (in-tool read-back, dated device tests, listening tests). Then: test
behavior rather than implementation — with hardware
listening as the gate for patch knowledge, untested ideas confined to a "Candidates" section and
tested recipes tagged with date and preset; listening tests run one change at a time followed by a
single yes/no question, with the user messaged before a long listen; clear descriptive names, mock
external dependencies, fast execution, risk-based test selection, balancing coverage against
velocity, critical-path focus, and choosing appropriate test depth.

### Frontend Standards

*Not initialized for this project. If you need frontend standards, you can:*
- *Add them manually using the docs-manager skill*
- *Run `/maister:standards-discover --scope=frontend` to auto-discover*

### Backend Standards

*Not initialized for this project. If you need backend standards, you can:*
- *Add them manually using the docs-manager skill*
- *Run `/maister:standards-discover --scope=backend` to auto-discover*

---

## How to Use This Documentation

1. **Start Here**: Always read this INDEX.md first to understand what documentation exists
2. **Project Context**: Read relevant project documentation before starting work — including the root `CLAUDE.md` and `RECIPES.md` for device/protocol work
3. **Standards**: This index only points to the standards — open and follow the specific standard files relevant to your task; don't rely on the index alone
4. **Keep Updated**: Update documentation when making significant changes
5. **Customize**: Adapt all documentation to your project's specific needs

## Updating Documentation

- Project documentation should be updated when goals, tech stack, or architecture changes
- Technical standards should be updated when team conventions evolve
- Always update INDEX.md when adding, removing, or significantly changing documentation
