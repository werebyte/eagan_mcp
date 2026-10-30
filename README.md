# eagan_mcp

MCP server for Haken EaganMatrix devices. Target: EM Module over USB-MIDI, Windows.

## Read this before you point it at your instrument

**This lets a language model write MIDI into an expensive, niche instrument, using a protocol
that has been verified on exactly one unit.** That is a real risk and you should decide about it
deliberately rather than discover it.

What that means concretely:

- **Normal operation only touches the volatile edit slot.** Nothing is persisted, so the worst
  outcome is a sound you do not like; reloading any preset clears it. That is the default and
  the code enforces it.
- **Saving writes to your device's flash.** `save_to_user_slot` overwrites one of the 128 user
  presets, there is no undo, and a preset you built by hand over hours is gone. The tool
  requires the slot to be named explicitly. Back up slots you care about first - see
  `backups/user_slots/` for what a snapshot looks like.
- **`send_preset_file` can carry firmware-level commands.** Preset archives may contain `ccTask`
  messages that erase or flash. Every payload is pre-scanned and those are refused, but the
  screen is an allowlist built from `HakenMidi.h`, not a proof.
- **`cc0=127` is the system-slot path used by firmware updates. This project never sends it.**
  If you extend the code, do not.
- **Turn your gain down before you let it build anything.** A wrong formula can jump to
  full-scale output between one note and the next - an output level set to 1.0 instead of 0.1,
  a feedback path that runs away, a note that never releases. On headphones that is a hearing
  risk and on a PA it is a speaker risk, and no software guard here prevents it: the matrix
  is an audio patchbay and the device will do what it is told. The Haken guide says the same
  thing ("Always turn down your gain / attenuation when experimenting making changes"), and
  the knowledge base starts every output formula at 0.1 for this reason.
- **`send_raw` is the one tool that can reach past the guards.** It refuses the system-slot
  path outright and needs `allow_flash=True` for a store or a device task, but everything else
  it sends arrives unchanged and unverified. It exists for protocol exploration. If you are not
  doing that, you do not need it, and an agent should not reach for it to do something a typed
  tool already does.
- An agent can be confidently wrong. Read what it proposes before you confirm a store.

If any of that is unacceptable for your instrument, use the read-only half: the knowledge base,
the recipes and the 668-preset factory catalog all work with no device attached.

## Status

**Everything here was developed and verified against one EaganMatrix Module, on firmware 10.81,
on Windows, judged by one person's ears.** Within that scope the matrix, formula and setup
tools are exercised on real hardware and the device findings are dated and evidence-tagged.
Outside it, treat this as untested:

- **Other EaganMatrix hardware is untried.** Nothing has been run against a Continuum,
  ContinuuMini, EaganMatrix Micro or CVC. They share the EaganMatrix engine, so much of it
  should carry over - but "should" is doing the work in that sentence.
- **Other firmware is untried.** `docs/HakenMidi.h` is the 10.81 header and is the source of
  truth; the prose guides in `docs/` are stamped 10.61-10.80, so a guide citation is 10.80 at
  best and 10.81-only behaviour is documented nowhere but the header.
- **Other platforms are untried.** Nothing is deliberately Windows-only beyond the example port
  names, but no other OS has been run.
- **Audible claims rest on listening tests, not measurement.** Where something was never heard,
  the knowledge base says so rather than implying confidence it does not have.

`ROADMAP.md` lists what is still open; `RESEARCH_REPORT.md` carries the unrun device-test plan.

Two of the 32 tools need a git checkout rather than an installed package: `search_docs` and
`read_docs` read `docs/`, which is 6.5 MB of guide text that is gitignored and not shipped in
the wheel. They raise a clear error instead of silently returning nothing. Everything else,
including the whole knowledge base and factory catalog, works from a plain `pip install`.

- Raw: `list_midi_ports`, `connect`, `disconnect`, `send_raw`, `listen`
- Device: `ping_device`, `get_firmware_version`, `get_status`, `load_preset`,
  `load_and_capture_preset`, `send_preset_file`
- Matrix: `get_matrix`, `set_matrix_point`, `describe_matrix_layout`
  (edit slot only; a write is verified by a separate full read, not by the Module's echo)
- Formulas: `get_formula`, `set_formula`, `write_formula_raw`
- Setup: `get_setup`, `set_osc_type`, `set_bank_type`, `set_shape_generator`,
  `set_polyphony`, `set_bend_range`
- Presets: `list_user_presets`, `set_preset_name`, `save_to_user_slot`
- Knowledge: `get_knowledge` (the shipped knowledge base in `eagan_mcp/knowledge/`),
  `get_recipes` (`RECIPES.md`), `search_factory_presets` (the shipped factory catalog),
  `search_docs` / `read_docs` (the guides in `docs/`; **checkout only**, not in the wheel),
  `search_preset_descriptions` (the 661 factory preset descriptions, from shipped JSON)

## Credits

The EaganMatrix, its factory preset library and the preset descriptions are the work of
**Haken Audio** (https://www.hakenaudio.com). The 661 preset descriptions shipped in
`eagan_mcp/knowledge/descriptions.json`, and the factory catalog decoded from Haken's preset
files, are included with the kind permission of Edmund Eagan of Haken Audio and remain
Haken Audio's copyright. They are not covered by this project's MIT licence; see the
carve-outs at the end of `LICENSE`.

The wire protocol is implemented from Lippold Haken's `HakenMidi.h`, which ships with the Haken
Editor and is not redistributed here. The preset-file decoding draws on pachde's cohem and
CHEM projects (Paul Chase Dempsey).

This project is not affiliated with or endorsed by Haken Audio.

## Requirements

- **Python 3.11 or 3.12.** Not 3.13: `python-rtmidi` ships compiled wheels and 3.13 is not
  covered, so `pip` would try to build it from source.
- **A Haken EaganMatrix device on USB**, firmware 10.81. Developed against the EaganMatrix
  Module on Windows. Nothing here is Windows-specific except the port names in the examples,
  but no other platform has been tested.
- **Nothing else.** No network, no database, no Haken Editor, no build step. The knowledge base
  and the 668-preset factory catalog are committed inside the package.

Everything read-only works with no device attached: the knowledge base, the recipes, the
factory catalog and the preset-description search. The device is needed only to play or build.

## Install

Two ways. Use the first unless you intend to change the code.

**As a package** - this is all a new user needs:

```
pip install eagan_mcp-0.1.0-py3-none-any.whl
```

That installs three console scripts: `eagan_mcp` (the MCP server), `eagan_sniff` (a MIDI
capture CLI) and `eagan_catalog` (rebuilds the shipped JSON; needs a Haken Editor install).

**From a checkout**, to develop:

```
git clone <this repo> && cd eagan_mcp
uv sync
```

Smoke test (Haken Editor closed, Module plugged in):

```
.venv\Scripts\python.exe -c "import mido; print(mido.get_input_names(), mido.get_output_names())"
```

`uv sync` and `uv run` fail with `os error 32` while the MCP server is running, because the
client holds `.venv/Scripts/eagan_mcp.exe` open. Either stop the MCP client first, or call the
interpreter directly and skip `uv` entirely:

```
.venv\Scripts\python.exe -c "import mido; print(mido.get_input_names())"
.venv\Scripts\python.exe -m pytest
```

## Connecting a client

The server speaks MCP over stdio and takes no arguments. It does not care what the working
directory is, so point your client straight at the installed script.

**Claude Desktop** - Settings > Developer > Edit Config, which opens
`%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "eagan": {
      "command": "C:\\path\\to\\venv\\Scripts\\eagan_mcp.exe"
    }
  }
}
```

Restart Desktop afterwards. On a checkout the script is at
`.venv\Scripts\eagan_mcp.exe` inside the repo.

**Claude Code** - `claude mcp add eagan -- C:\path\to\venv\Scripts\eagan_mcp.exe`

Prefer the console script over `uv run --directory ...`: `uv` holds the executable open, which
is what produces `os error 32` when you then try to run the tests.

On connect the server sends the client its own instructions - the build workflow, the
edit-slot safety contract, and the reminder that only the user can hear the result. A client
that has neither this repo's `CLAUDE.md` nor the skills in `.claude/skills/` is oriented by
those instructions alone, so start a session by asking for `get_knowledge()`.

### One port, one process

A USB-MIDI port on Windows is exclusive. The Haken Editor, this server and any MIDI bridge
all want the same port, and whoever gets there first keeps it. Symptoms of losing the race
are a `RuntimeError` naming the ports on `connect`, or a device that answers nothing. Close
the Editor before starting a session, and do not run two MCP clients against one device.

## Sniffing

- What the **Module** sends (preset load, knob on device):
  `.venv\Scripts\python.exe -m eagan_mcp.sniff` (the `eagan_sniff` console script, called
  directly so it works whether or not the MCP client is holding the venv)
- What the **Editor** sends: needs a spy in between, because Windows USB-MIDI
  ports are usually exclusive. Not verified yet which works with the Haken Editor:
  Windows MIDI Services (multi-client, Win 11) or loopMIDI + MIDI-OX routing.

## Safety rule

Writes go to the **edit slot** only. A store to a user slot needs the slot named explicitly
and the user's confirmation in that turn; the system-slot path is never sent at all. The long
version, and why each rule exists, is at the top of this file under "Read this before you point
it at your instrument".

Four rules the code enforces rather than merely documents:

1. Every matrix and formula write targets the edit slot. `save_to_user_slot` is the only tool
   that persists anything, and it refuses without `confirm=True` plus a named slot.
2. `cc0=127`, the system-slot store path, is never emitted by any tool - including `send_raw`,
   where not even `allow_flash=True` unlocks it. User stores are `cc0=0` with `cc32`/`cc112`.
3. `send_preset_file` pre-scans the whole payload and refuses any `ccTask` message before a
   single MIDI byte is sent. `send_raw` applies the same screen to its whole batch, so a flash
   command hidden mid-batch blocks the messages before it too, and a store or device task needs
   an explicit `allow_flash=True`.
4. A store is verified by comparing names through the read-only `list_user_presets`, never by
   loading the slot back - loading destroys the unsaved edit slot.

## Editor path

`HAKEN_EDITOR_DIR` is **optional and has no default**. It points at a Haken Editor
installation and is needed only to *rebuild* the shipped JSON artifacts - reading them needs
nothing, and the 661 factory preset descriptions are served from `descriptions.json` inside
the package. Set it to the folder containing `Firmware/` (an older Max-based Editor puts that
under `HE/`), for example:

```
set HAKEN_EDITOR_DIR=D:\Haken Editor 1081
```

Leaving it unset is correct for normal use; `eagan_catalog` will tell you to set it.

## Regenerating the factory catalog

The shipped catalog under `eagan_mcp/knowledge/` is decoded offline from the system presets in
`HAKEN_EDITOR_DIR`; no device is involved. Rebuild it in place with:

```
uv run eagan_catalog eagan_mcp/knowledge
```

or, while the MCP server is holding the venv:

```
.venv\Scripts\python.exe -m eagan_mcp.preset_file eagan_mcp/knowledge
```

It writes `factory_catalog.json`, `preset_index_1081.json`, `census.json` and
`descriptions.json`, which are tracked, plus `factory_catalog_full.json`, which is the mining
input and is gitignored.

The guides under `docs/` and `docs_1044/` and the reference checkouts under `ref/` are
gitignored too: `docs/` is extracted from the Haken Editor install (`docs/HakenMidi.h` is the
protocol source of truth and must be copied there on every machine), and `ref/` holds
`git clone https://codeberg.org/pachde/cohem.git ref/cohem` and
`git clone https://github.com/Paul-Dempsey/pachde-CHEM.git ref/pachde-CHEM`.
