# System Architecture

## Overview

eagan_mcp is a single-process, single-package protocol translator. An MCP client (Claude
Desktop or Claude Code) launches it over stdio; it talks USB-MIDI to one EaganMatrix
Module. There is no server to deploy, no database, and no concurrency beyond the one
background thread that `mido` uses to deliver incoming MIDI.

```
MCP client (Claude)
      |  stdio, JSON-RPC
      v
server.py ............. MCP tool facade (32 tools)
      |
      +-- haken.py ..... documented protocol (Continuum guide sec. 15)
      +-- formula.py ... formula stream 19 codec
      +-- setup.py ..... matrix-config stream 20 codec
      +-- matrix_map.py  row/column name tables
      |
      v
midi_io.py ............ transport: port discovery, EmConnection, receive buffer
      |  USB-MIDI
      v
EaganMatrix Module (firmware 10.81)

preset_file.py ........ offline: decodes preset .mid files and builds the factory catalog,
      |                 importing the same codec modules. No I/O and no device.
      +-- formula.py / setup.py / matrix_map.py
sniff.py .............. standalone MIDI capture CLI over midi_io.py; not part of the server
```

## Architecture Pattern

**Pattern**: layered protocol stack behind a tool facade.

Three layers, with dependencies pointing strictly downward:

1. **Tool facade** (`server.py`) — the only layer the agent sees. Each tool is a complete
   device transaction: set up, send, listen, decode, verify, return a dict.
2. **Codec layer** (`haken.py`, `formula.py`, `setup.py`, `matrix_map.py`) — pure
   translation between Python values and wire bytes. No I/O.
3. **Transport** (`midi_io.py`) — deliberately protocol-agnostic, as its own module
   docstring states: *"Haken-specific encoding goes in haken.py."*

The split that matters most is *inside* layer 2, and it is drawn by evidence quality:

- `haken.py` holds the **documented** protocol, from the Continuum User Guide section 15.
- `formula.py` and `setup.py` hold **reverse-engineered** streams, now re-checked against
  the official `docs/HakenMidi.h`.

Keeping those apart is what lets `CLAUDE.md` state honestly which behaviour is certain and
which is inferred. It should survive refactoring.

## System Structure

### MCP tool facade

- **Location**: `eagan_mcp/server.py` (992 lines)
- **Purpose**: register and implement the 32 `@mcp.tool()` functions
- **Note**: tool docstrings are not internal documentation — they are the prompt the agent
  reads to decide whether and how to call the tool. They carry the safety warnings for
  that reason.
- **Tool groups**:

| Group | Tools |
|---|---|
| Transport | `list_midi_ports`, `connect`, `disconnect`, `send_raw`, `listen` |
| Device state | `ping_device`, `get_firmware_version`, `get_status` |
| Presets | `load_preset`, `load_and_capture_preset`, `send_preset_file`, `list_user_presets`, `set_preset_name`, `save_to_user_slot` |
| Matrix | `get_matrix`, `set_matrix_point`, `describe_matrix_layout` |
| Formulas | `get_formula`, `set_formula`, `write_formula_raw` |
| Setup | `get_setup`, `set_osc_type`, `set_bank_type`, `set_shape_generator`, `set_polyphony`, `set_bend_range` |
| Knowledge | `search_docs`, `read_docs`, `search_preset_descriptions`, `get_recipes`, `get_knowledge`, `search_factory_presets` |

- **Private helpers** (14): `_ping`, `_capture_config`, `_save_mid`, `_flash_write_reason`,
  `_named`, `_select_and_read`, `_stream_pairs`, `_read_formula_at`, `_read_setup`,
  `_write_setup`, `_grep`, `_knowledge_json`, `_module_matches`, `_preset_summary`. The
  `_select_and_read` / `_read_*` / `_write_*` trio is where the select-then-read idiom
  lives; `_knowledge_json`, `_module_matches` and `_preset_summary` serve the offline
  knowledge and catalog tools and touch no device.

### Documented protocol codec

- **Location**: `eagan_mcp/haken.py` (258 lines)
- **Purpose**: protocol constants, message builders, text-stream decoding
- **Contents**: channel and CC constants (`CH16`, `CC_EDITOR_PING`, ...), preset-select
  message construction, name/description text streams (streams 0 and 1 as ASCII pairs in
  channel-pressure messages), the store-to-user-slot sequence
- **Source**: Continuum User Guide section 15, cross-checked against `docs/HakenMidi.h`

### Formula codec

- **Location**: `eagan_mcp/formula.py` (444 lines)
- **Purpose**: decode and encode **stream 19** — the `(id, value)` pairs that define what a
  formula letter computes
- **Key detail**: slider values use a split sign encoding. A sign-bit id is sent
  immediately before its slider id (13 to 42, 14 to 73, 15 to 45, and so on), and
  `value = (raw + 100 * (not sign)) / 100 - 1`, range -1 to 1.27. The header's own
  semantics are a `Neg` flag plus a magnitude; the negative path is **not yet
  device-confirmed**.
- **Contents**: a `COMPONENTS` table describing W/X/Y/Z, plus mode, magnitude, modifier,
  macro and shape-generator id maps

### Setup codec

- **Location**: `eagan_mcp/setup.py` (241 lines)
- **Purpose**: decode and encode **stream 20** — the matrix configuration
- **Contents**: id 39 polyphony (1-8, with the expanded and double-rate flags), id 40 bend
  range, ids 72-76 oscillator slot type, 77-81 filter cascade, 82-86 extreme rate, 91/92/93
  bank A/B/C type, 100-104 shape-generator types, 105 delay select, plus the `OSC_TYPES`
  and bank-type value tables

### Row/column name tables

- **Location**: `eagan_mcp/matrix_map.py` (142 lines)
- **Purpose**: human-readable names for matrix rows and columns, so tool output names cells
  rather than numbering them
- **Convention worth keeping**: entries verified on the device are distinguished in-file
  from those taken only from the guide

### Transport

- **Location**: `eagan_mcp/midi_io.py` (93 lines)
- **Purpose**: port discovery and the live connection
- **Key pieces**:
  - `DEFAULT_PORT_HINT = "EaganMatrix"` — substring match against port names
  - `list_ports()`, `_find(names, hint)` — case-insensitive substring discovery
  - `EmConnection` — holds `in_port` / `out_port`, exposes `is_open`, and buffers inbound
    messages in a `deque(maxlen=20000)` guarded by a `threading.Lock`. `mido` delivers
    messages on its own thread via the `_on_msg` callback; tools drain the buffer.
  - `open()` raises `RuntimeError` naming the available ports and reminding the caller that
    the Haken Editor may be holding the device exclusively — the single most common failure
    on Windows.

### Offline preset-file decoder and catalog builder

- **Location**: `eagan_mcp/preset_file.py` (2347 lines, over half the package)
- **Purpose**: decode a preset "archive" `.mid` file into the logical preset - name,
  description, matrix, formulas, setup, macros, graphs - and, from `main()`, walk a whole
  system-preset folder to write the shipped factory catalog and its auxiliary JSON artifacts
- **Entry point**: `uv run eagan_catalog [output-directory]`. Standard library plus this
  package's own codecs; no device, no MIDI port
- **The 8th module, and a second consumer rather than a second codec.** It joins the codec
  layer from above, the way `server.py` does, and owns no wire semantics of its own:
  `formula.py` keeps stream 19, `setup.py` keeps stream 20, `matrix_map.py` keeps the row,
  column and cell-value names, and `preset_file.py` imports all three for every value table,
  default and sign reading. The evidence-quality split therefore survives the addition
  intact - `haken.py` is still documented protocol, `formula.py` and `setup.py` are still
  reverse-engineered, and nothing in `preset_file.py` mixes the two
- **Why it matters that it is a consumer**: an earlier standalone version of this decoder had
  drifted from `formula.py` into two different wrong readings of the same wire - a mirrored
  negative height and an `idTransX` default of Octaves - and a downstream script had grown
  local workarounds for both. Two copies of a codec that disagree about what the device means
  are a loss of evidence, not merely duplication

### Sniffer CLI

- **Location**: `eagan_mcp/sniff.py` (39 lines)
- **Purpose**: standalone real-time MIDI capture, used to discover protocol behaviour
  outside the MCP server
- **Entry point**: `uv run eagan_sniff`. Prints to the console; not part of the server.

## Data Flow

### A typical read

```
tool call
  -> ensure connection (EmConnection.is_open)
  -> _ping                        ch16 cc116: without it the Module stays silent
  -> send request                 e.g. select a matrix cell
  -> device streams a reply       cc56=<id> opens, poly-pressure pairs, cc56=127 closes
  -> _on_msg appends to deque     background mido thread
  -> listen window drains buffer  typically 2.5-4 s
  -> _stream_pairs reassembles    (id, value) pairs per stream
  -> codec decodes                formula.py / setup.py / haken.py
  -> return dict
```

Streams in use: **0** name, **1** description, **15** thumbnails, **19** formula,
**20** matrix config.

### A typical write

```
select the target first   (cc41 column, cc40 row, cc45=115)
  -> send the change       cc56=<stream> + poly-pressure (id, value) pairs
  -> separate full read    select cell 0,0 and listen >= 2.5 s
  -> compare and report verified / not verified
```

Two device behaviours force this shape and are easy to break by accident:

- **Select-then-read.** Selecting any matrix cell makes the Module re-send the whole
  matrix, which is how state is read without reloading the preset.
- **Verify by a separate read.** The echo immediately after a write is a *partial* matrix
  that may stop before the changed cell. Verifying from that echo produces false negatives.

Also load-bearing: a ping or other traffic *between* a select and its write has broken a
write at least once, and the first read after connect or preset load can come back empty,
so reads retry with a longer listen window.

## External Integrations

| Integration | Mechanism | Direction |
|---|---|---|
| EaganMatrix Module | USB-MIDI via `python-rtmidi`, ports matched by name substring | bidirectional |
| MCP client | stdio JSON-RPC via FastMCP | inbound calls |
| Firmware guides | `docs/` plain text, grepped by `_grep` for `search_docs` / `read_docs` | read-only |
| Haken Editor install | `HAKEN_EDITOR_DIR`, factory preset descriptions | read-only |
| Capture output | `.mid` files written to `captures/` by `_save_mid` | write-only |
| `RECIPES.md` | served to the agent by `get_recipes` | read-only |

## Database Schema

Not applicable — there is no database. Device state is the only state.

## Configuration

Configuration is minimal and currently split between an environment variable and
module-level constants:

| Setting | Where | Default |
|---|---|---|
| Haken Editor directory | `HAKEN_EDITOR_DIR` env var | a hardcoded absolute Windows path |
| MIDI port hint | `DEFAULT_PORT_HINT` in `midi_io.py` | `"EaganMatrix"` |
| Listen windows | per-tool literals in `server.py` | 2.5-4 s |
| Shipped knowledge base | `KNOWLEDGE_DIR` in `server.py` | `eagan_mcp/knowledge/` |

**`KNOWLEDGE_DIR` departs from `PROJECT_DIR` on purpose.** Every other path in `server.py` is
built from `PROJECT_DIR = Path(__file__).resolve().parent.parent`, the repository root, which is
where `docs/` and `captures/` belong: they are machine-local, regenerable and gitignored.
`KNOWLEDGE_DIR` is `Path(__file__).resolve().parent / "knowledge"` instead - inside the package.
The knowledge documents and their JSON artifacts are shipped data that an installed wheel has to
carry, and a path resolved from the repository root does not exist once the package is installed
elsewhere. The two path roots therefore mean different things and should stay distinct: repository
root for machine-local input, package directory for shipped data.

**Known weakness**: the Editor path default is a hardcoded absolute Windows path belonging
to one machine, and listen timeouts are scattered literals. Both are flagged as
improvement opportunities rather than fixed, since they do not currently block the work.

## Safety Architecture

The safety rules are architectural, not advisory, and they are enforced in three places at
once — tool docstrings (so the agent knows), tool implementations (so the agent cannot
bypass), and `CLAUDE.md` (so a future session knows):

1. **Edit slot by default.** Writes go to the edit buffer. Nothing else without explicit
   user confirmation.
2. **The system-slot path is never used.** Storing with `ch16 cc0=127` targets system slots
   — the firmware-update channel. User slots use `cc0=0`, `cc32=(N-1)>>7`,
   `cc112=(N-1)&127`.
3. **`send_preset_file` screens its input** in a pass over the whole file before the first
   byte goes out, and raises `RuntimeError` rather than forwarding a flash write. It
   refuses ch16 `cc112` (`ccStore`) at any value, ch16 `cc0=127` (the system-slot path of
   rule 2) and ch16 `cc109=8` (global settings to flash). A store in the last message of a
   file therefore stops the first message from being sent.
4. **Stores are verified indirectly.** `save_to_user_slot` confirms via
   `list_user_presets`, because the echo after a save varies between saves. Loading the
   slot to check would destroy the unsaved edit buffer — a lesson learned the hard way and
   recorded in `CLAUDE.md`.

## Deployment Architecture

None. The server is a subprocess of the MCP client:

```
claude mcp add eagan -- <venv>/Scripts/eagan_mcp.exe
```

Claude Desktop uses the equivalent `mcpServers` entry in
`%APPDATA%\Claude\claude_desktop_config.json`.

Operational consequences worth knowing:

- The process holds the MIDI port for its whole lifetime, so the Haken Editor cannot open
  the device concurrently. Releasing the port after each tool call is an open improvement.
- A new or changed tool is not visible until the MCP client restarts.
- The server disconnected once mid-session, cause unknown and unresolved.

## Known Architectural Gaps

Recorded here so they are not rediscovered. None is currently a priority.

1. **No CI, and a deliberately host-only suite.** The blanket gap is closed: 106 tests in
   16 files (2643 lines, about 1.5 s) now cover the pure codecs, the single-table property
   and the codec layer's import freedom, `preset_file.py`'s top-level parse path against
   four committed fixtures, the flash path's pre-scan, the shipped JSON artifacts' shape
   and counts, both new tools' validation, the three shipped skills, and the 23 knowledge
   documents as text. What remains a gap is narrower and should be read precisely:
   - **No CI.** Nothing runs the suite but a human typing
     `.venv/Scripts/python.exe -m pytest`.
   - **No device coverage, by construction.** No test opens a MIDI port, so a green run
     closes no device-test item. Uncovered for that reason: the device semantics of the
     negative-height offset reading, and anything else that can only be shown on the
     Module.
   - **Uncovered offline surfaces.** The 19 tool docstrings not yet repaired, and the
     catalog build from `HAKEN_EDITOR_DIR`.
   - **Truth of the knowledge base is out of scope.** The suite checks the 23 documents as
     text - structure, tags, encoding - and cannot say whether a device claim in them is
     *true*. That stays a listening test.
2. **No type checking.** Type hints are thorough but unverified; nothing catches a decoder
   whose declared return type has drifted.
3. **No logging.** There is no `logging` use anywhere; `sniff.py` prints. MIDI traffic,
   connection lifecycle and stream reassembly are invisible after the fact, which makes an
   intermittent failure — like the unexplained disconnect — hard to chase.
4. **Hardcoded configuration.** See the Configuration section.
5. **No retry policy.** Reads retry ad hoc per tool; the known "first load returns nothing"
   behaviour has no shared handling.
6. **The offline tools cannot be served without the MIDI stack.** `server.py` imports `mido` at
   module level and constructs `conn = midi_io.EmConnection()` at import time, before any tool
   runs. Every tool therefore shares that dependency, including the ones that touch no device at
   all: `get_knowledge`, `get_recipes`, `search_factory_presets`, `search_docs`, `read_docs` and
   `search_preset_descriptions` all read files only, yet the server will not start unless
   `python-rtmidi` is importable on the host. Noted, not fixed: the fix is a lazy import plus a
   lazily constructed connection, and nothing in the current single-machine workflow is blocked
   by it.
7. **`preset_file.py` labels matrix rows from two paths that disagree.** Its raw cell decoder
   names rows through the static `matrix_map.ROWS` table, while `wiring_block` re-labels the same
   cells through `matrix_map.preset_labels`, the preset-aware join that reads `idRowTyp1/2` out of
   the decoded setup. `decode_preset_file()` can therefore return a setup whose `row_types` say
   `Tap 1/Tap 2` beside its own matrix cells calling those rows `Audio In L/R`. This is the same
   defect that the labelling fix closed in the MCP tools, still alive in the catalog producer.
   Build-only and not agent-reachable: no MCP tool calls `decode_preset_file`, and the shipped
   catalog has no mislabelled cell because `wiring_block` re-labels everything it emits. Noted,
   not fixed.

---
*Based on codebase analysis performed 2026-10-26*
