"""EaganMatrix MCP server.

Protocol source of truth: docs/HakenMidi.h (firmware 10.81), with the Continuum User
Guide section 15 behind it for the older config controllers. Matrix, formula and setup
editing are implemented over the live USB streams (cc56 = 19 / 20); the ch15 streams
inside preset .mid files are a separate format, decoded offline by preset_file.py."""

import json
import os
import re
import time
from pathlib import Path

import mido
from mcp.server.fastmcp import FastMCP

from . import formula, haken, matrix_map, midi_io, setup

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_DIR / "docs"
CAPTURE_DIR = PROJECT_DIR / "captures"
# The Haken Editor install, used only to REBUILD the shipped JSON artifacts - never to serve
# them. There is no default: a hardcoded absolute path would be one developer's home directory
# shipped to every user, and a wrong guess fails more confusingly than an unset variable.
_EDITOR_ENV = os.environ.get("HAKEN_EDITOR_DIR", "")
EDITOR_DIR = Path(_EDITOR_ENV) if _EDITOR_ENV else None
DESCRIPTIONS_DIR = None
if EDITOR_DIR is not None:
    DESCRIPTIONS_DIR = EDITOR_DIR / "Firmware" / "Descriptions"
    if not DESCRIPTIONS_DIR.exists():  # older Max-based Editor layout
        DESCRIPTIONS_DIR = EDITOR_DIR / "HE" / "Firmware" / "Descriptions"

# Sent to the client on connect. A Claude Code session in this repo gets CLAUDE.md and the
# three skills under .claude/skills/; any other client - Claude Desktop, a phone, anything
# speaking MCP - gets neither, and would otherwise have to guess how to drive a Haken module.
# These instructions are that client's whole orientation, so they state the workflow and the
# safety contract and then hand off to get_knowledge for everything else.
INSTRUCTIONS = """This server builds sounds on a Haken EaganMatrix Module (firmware 10.81) over USB-MIDI, by
writing its modulation matrix and formulas live.

START HERE, BEFORE BUILDING ANYTHING
  1. get_knowledge() - the shipped knowledge base: 23 documents covering the voice model, 18
     module cards, patterns, pitfalls and two worked end-to-end patch plans. It needs no device
     and no network. Read the relevant parts BEFORE writing to the matrix; the device facts in
     it are evidence-tagged and are not reconstructible by reasoning about synthesis.
  2. get_recipes() - the recipes already confirmed by ear on real hardware.
  3. search_factory_presets(...) - 668 decoded factory presets. Starting from one that already
     does what you want is almost always faster than building from nothing.
  4. connect() - opens the MIDI port. Each device tool pings the Module itself, so no keepalive
     is needed, but the Module answers nothing at all until something pings it.

SAFETY - these are not stylistic preferences
  * Every write goes to the EDIT SLOT, which is volatile. That is the safe default: the worst
    outcome is a sound nobody likes.
  * NEVER store to a user slot unless the user names the slot in that turn and confirms it.
    A store overwrites a preset they may have built by hand over hours. There is no undo.
  * Verify a write with a SEPARATE read, not the echo that comes back with it.
  * An empty read usually means "nothing changed since the last read", not "the patch is
    empty" - retry with a longer window before concluding anything.
  * Check get_status after a structural change. Above ~90% DSP the Module drops voices and the
    panel knobs go sluggish.

WHAT ONLY EARS CAN SETTLE
  You cannot hear the device. Several parameters have no readable units, and some documented
  values have never been confirmed by listening. State plainly what a patch SHOULD sound like,
  change ONE thing at a time, and ask the user a single yes/no question about what they hear.
  Treat their answer as outranking anything in the knowledge base.
"""

mcp = FastMCP("eagan_mcp", instructions=INSTRUCTIONS)
conn = midi_io.EmConnection()


# ---------- raw ----------

@mcp.tool()
def list_midi_ports() -> dict:
    """List MIDI input and output port names on this computer."""
    return midi_io.list_ports()


@mcp.tool()
def connect(port_hint: str = midi_io.DEFAULT_PORT_HINT) -> dict:
    """Open in+out ports whose name contains port_hint (case-insensitive).
    Close the Haken Editor first: on Windows ports are usually exclusive."""
    return conn.open(port_hint)


@mcp.tool()
def disconnect() -> str:
    """Close the MIDI ports."""
    conn.close()
    return "closed"


@mcp.tool()
def send_raw(messages: list[dict], listen_seconds: float = 0.5,
             allow_flash: bool = False) -> dict:
    """Send mido-dict messages, then collect replies. Largely unguarded: anything
    not named below reaches the device unchanged. Channels are 0-based (ch16 = 15),
    and this is for protocol exploration only.

    Being raw, it is the one tool that can put the device in a state no other
    tool can produce. Use it to explore, not to build - the typed tools verify
    their writes against a separate read and this one cannot.

    Two screens, applied to the WHOLE batch before any message is sent:
      - ch16 cc0=127, the system-slot store path, is refused ALWAYS, even with
        allow_flash=True. It is valid only during an Update File 2 firmware
        write and would overwrite a factory preset.
      - a user-slot store (ch16 cc112), and any ch16 cc109 device task - cc109=8
        writes the global settings to flash, and about fifteen other task values
        write or erase it - are refused unless you pass allow_flash=True, which
        you may only do after the user has asked for that specific operation in
        that turn.

    A refusal sends nothing at all and names the offending message, so a batch
    is never half-applied."""
    msgs = [midi_io.dict_to_msg(d) for d in messages]
    for i, m in enumerate(msgs):
        reason = _flash_write_reason(m)
        if not reason:
            continue
        system_slot = (m.type == "control_change" and m.channel == haken.CH16
                       and m.control == haken.CC_CATEGORY and m.value == 127)
        if system_slot:
            raise RuntimeError(
                f"refused, nothing sent: message {i} is {reason}. This is never sent by this "
                "server under any circumstances.")
        if not allow_flash:
            raise RuntimeError(
                f"refused, nothing sent: message {i} is {reason}. If the user asked for exactly "
                "this, call again with allow_flash=True; to store a preset use save_to_user_slot, "
                "which verifies the result.")
    conn.clear()
    for m in msgs:
        conn.send(m)
    replies = conn.listen(listen_seconds)
    return {"sent": len(msgs), "replies": [midi_io.msg_to_dict(m) for _, m in replies],
            "flash_allowed": allow_flash}


@mcp.tool()
def listen(seconds: float = 3.0, max_messages: int = 500) -> dict:
    """Record what the device sends for a few seconds."""
    conn.clear()                      # fresh window: listen() no longer clears for us
    items = conn.listen(seconds)
    out = [midi_io.msg_to_dict(m) for _, m in items[:max_messages]]
    return {"count": len(items), "truncated": len(items) > max_messages, "messages": out}


# ---------- typed, documented ----------

def _ping():
    conn.send(haken.cc16(haken.CC_EDITOR_PING, 85))


def _capture_config(seconds: float) -> list[mido.Message]:
    conn.clear()
    _ping()
    conn.send(haken.cc16(haken.CC_COMMAND, haken.CMD_TRANSMIT_CONFIG))
    return [m for _, m in conn.listen(seconds)]


def _save_mid(msgs: list[mido.Message], name: str) -> Path:
    CAPTURE_DIR.mkdir(exist_ok=True)
    safe = re.sub(r"[^\w\- ]", "_", name).strip() or "capture"
    path = CAPTURE_DIR / f"{safe}_{time.strftime('%Y%m%d_%H%M%S')}.mid"
    f = mido.MidiFile()
    track = mido.MidiTrack()
    f.tracks.append(track)
    for m in msgs:
        track.append(m.copy(time=0))
    f.save(path)
    return path


@mcp.tool()
def load_and_capture_preset(category: int, index: int, save_as: str = "", seconds: float = 3.0) -> dict:
    """Load a preset and capture the full dump the device streams back.
    Saves the raw dump as .mid in captures/. Unsaved edits on the device are lost.
    category: 0=User, 1=Strings ... 13=Utility; index is 0-based."""
    conn.clear()
    _ping()
    for m in haken.load_preset_msgs(category, index):
        conn.send(m)
    msgs = [m for _, m in conn.listen(seconds)]
    streams = haken.decode_live_streams(msgs)
    name = next((st.get("text") for st in streams if st["id"] == 0), "") or "preset"
    path = _save_mid(msgs, save_as or name)
    return {
        "name": name,
        "description": next((st.get("text") for st in streams if st["id"] == 1), ""),
        "message_count": len(msgs),
        "streams": [{"id": st["id"], "bytes": len(st["bytes"])} for st in streams],
        "saved_to": str(path),
    }


@mcp.tool()
def ping_device() -> dict:
    """Send the Editor keepalive (ch16 cc116) and return the status reply."""
    conn.clear()
    _ping()
    return {"replies": [midi_io.msg_to_dict(m) for _, m in conn.listen(1.0)]}


@mcp.tool()
def get_firmware_version(seconds: float = 2.0) -> dict:
    """Read firmware version from the transmit-config response (cc102/103)."""
    v = haken.firmware_version(_capture_config(seconds))
    return {"firmware_raw": v}


@mcp.tool()
def load_preset(category: int, index: int) -> dict:
    """Load a preset into the edit slot, DESTROYING unsaved edits there - the
    current sound is gone and cannot be recovered. Save it first if it matters.
    category: 0=User, 1=Strings ... 13=Utility; index is 0-based within the
    category. Uses ch16 cc0, cc32, program change.
    Do NOT read the index off a printed list - the 10.81 firmware is off by one
    against the published numbering in most categories. Get both numbers from
    the shipped catalog: search_factory_presets(preset="FM Bells") returns
    category_menu_index and category_index, which are exactly this tool's two
    arguments. That ordering is device-verified in ALL THIRTEEN categories
    (2026-10-28): the first and last preset of each was loaded by the
    catalog's numbers and the Module reported the expected name back, 25 of
    26 probes. To confirm one yourself, load it and read list_user_presets'
    last entry, which is the edit slot's name.
    Returns the request only - the device is not read back."""
    for m in haken.load_preset_msgs(category, index):
        conn.send(m)
    return {"category": haken.CATEGORIES.get(category, category), "index": index}


@mcp.tool()
def get_status() -> dict:
    """Ping the Module and report DSP usage and LED state. High DSP usage (>~90%)
    explains dropped voices, sluggish macro knobs and pops.
    dsp_polyphony is ALWAYS null here: cc72 arrives after a matRefresh, not after a
    plain ping (device-observed 2026-10-27/28), so the actual voice count cannot be
    confirmed with this tool. Use get_matrix or get_setup first if you need it to
    have been asked for. dsp_usage_percent is allocated DSP for the patch, not
    instantaneous load - it does not move when a note is held."""
    conn.clear()
    _ping()
    msgs = [m for _, m in conn.listen(1.0)]
    out = {"dsp_usage_percent": {}, "dsp_polyphony": None, "led": None}
    leds = {0: "off", 1: "blue", 2: "red", 3: "bright green", 4: "green", 5: "white",
            6: "yellow", 7: "purple"}
    for m in msgs:
        if m.type != "control_change" or m.channel != haken.CH16:
            continue
        if m.control == haken.CC_USAGE:
            out["dsp_usage_percent"][f"dsp{m.value >> 5}"] = (m.value & 31) * 4
        elif m.control == haken.CC_POLY_DSP:
            out["dsp_polyphony"] = m.value
        elif m.control == haken.CC_LED:
            out["led"] = leds.get(m.value & 0x0F, m.value & 0x0F)
    return out


def _flash_write_reason(m: mido.Message) -> str:
    if m.type != "control_change" or m.channel != haken.CH16:
        return ""
    if m.control == haken.CC_STORE_LO:
        return f"a store to a user slot (ch16 cc112 = {m.value})"
    if m.control == haken.CC_CATEGORY and m.value == 127:
        return "the system-slot store path (ch16 cc0=127), valid only during a firmware update"
    if m.control == haken.CC_COMMAND:
        # ch16 cc109 is ccTask, and docs/HakenMidi.h:854 states "ccTask not stored within an
        # 'archive' (preset in .mid file)" - so a legitimate preset file carries NO cc109 at
        # all, which makes this an allowlist rather than a blocklist. Screening only
        # CMD_STORE_CONFIG (8) let ~14 other flash/erase tasks through, including gridToFlash
        # (101), startUpdF2 (103, the state in which the forbidden ccBankH 127 system-slot
        # write is accepted), burnUser489 (43), storeTopo (51) and preEraseUpdF1/F2 (57/58).
        if m.value == haken.CMD_STORE_CONFIG:
            return "a write of the global settings to flash (ch16 cc109=8)"
        return (f"a device task command (ch16 cc109={m.value}); no ccTask belongs in a preset "
                "file (docs/HakenMidi.h:854), and several write or erase flash")
    return ""


@mcp.tool()
def send_preset_file(path: str, delay_ms: float = 1.0) -> dict:
    """Stream a preset .mid file to the device. Edit slot only: nothing here
    writes flash. The whole file is scanned first, so a file carrying a
    flash-writing command is refused with nothing sent at all. Refused:
    ch16 cc112 (ccStore, the user-slot store), ch16 cc0=127 (the system-slot
    path, never to be sent) and ch16 cc109 at ANY value - no ccTask belongs in
    a preset archive (docs/HakenMidi.h:854) and several of them write or erase
    flash. Everything else in the file is passed through unchanged."""
    msgs = [m for t in mido.MidiFile(path).tracks for m in t if not m.is_meta]
    for m in msgs:
        reason = _flash_write_reason(m)
        if reason:
            raise RuntimeError(
                f"File contains {reason} ({m}); refusing to send it, nothing was emitted. "
                "A preset file may carry any traffic except ch16 cc112, ch16 cc0=127 and "
                "ch16 cc109=8.")
    for m in msgs:
        conn.send(m)
        if delay_ms:
            time.sleep(delay_ms / 1000)
    return {"sent": len(msgs), "texts": haken.decode_texts(msgs)}


# ---------- matrix ----------

def _named(points: list[dict], labels: dict) -> list[dict]:
    return [{**p, "row_name": matrix_map.row_name(p["row"], labels),
             "col_name": matrix_map.col_name(p["col"], labels)} for p in points]


def _select_and_read(row: int, col: int, extra: list[tuple[int, int]],
                     seconds: float) -> tuple[list[dict], list[mido.Message]]:
    """The decoded matrix plus the raw reply, which also carries stream 20 after a select."""
    conn.clear()
    _ping()
    for m in haken.select_point_msgs(row, col):
        conn.send(m)
    for cc, v in extra:
        conn.send(haken.cc16(cc, v))
    # Then ask for a full refresh. Device-verified 2026-10-27 (fw 10.81): a cell select ALONE
    # returns a cc45 echo and no matrix at all - 13 messages - so the "selecting a cell makes
    # the Module re-send the matrix" rule in CLAUDE.md does not hold on this firmware.
    # ccMatOp 124 (matRefresh) does: ~1,100 messages carrying the matrix, stream 20, the text
    # streams and cc72. A write just above counts as the state change it wants.
    conn.send(haken.cc16(haken.CC_MATRIX_CTRL, haken.CMD_MATRIX_REFRESH))
    msgs = [m for _, m in conn.listen(seconds)]
    return haken.decode_matrix(msgs), msgs


@mcp.tool()
def get_matrix(seconds: float = 2.5) -> dict:
    """Read-only. The current matrix without reloading the preset (unsaved edits
    survive). Selects cell (0,0) and then sends ccMatOp 124 (matRefresh): on fw
    10.81 a select ALONE returns an echo and no matrix, so the refresh is what
    makes the state come back. A refresh with no state change since the last one
    returns almost nothing, which is why an empty read is retried with a longer
    window rather than treated as an empty matrix.
    row_name/col_name come from THIS preset's setup, so rows 9-12 read as delay
    taps in a preset that routes taps there; describe_matrix_layout only ever
    returns the generic layout."""
    points, _ = _select_and_read(0, 0, [], max(seconds, 4.0))
    if not points:  # a refresh with no state change since the last one returns almost nothing
        time.sleep(0.3)
        points, _ = _select_and_read(0, 0, [], max(seconds, 5.0))
    # A second device read, roughly doubling this tool's round-trip. Deliberate: the static
    # row/column table is wrong for 3 of 18 captured presets, and an opt-in flag would leave
    # the default wrong - an agent that does not know the flag exists cannot set it.
    labels = matrix_map.preset_labels(setup.decode(_read_setup()))
    return {"points": _named(points, labels), "count": len(points)}


@mcp.tool()
def set_matrix_point(row: int, col: int, value: str, seconds: float = 2.5) -> dict:
    """Set one matrix cell in the current (edit) preset. Not stored to flash.
    value: "" deletes; "A".."V", "A'".."V'" user formulas; "W","X","Y" predefined;
    "z^2" (code 48 is matZZ, z SQUARED - there is no plain Z cell value, so for linear
    pressure place a formula letter and set its Z component with set_formula);
    "row^2"/"row^3" square or cube the row; "1".."9" constants; ".5", ".1234" decimals.
    row_name/col_name are this preset's, the same ones get_matrix reports;
    describe_matrix_layout is the generic layout only. Verified by a separate full read
    after the write, not by the echo, which can stop before the changed cell."""
    extra = haken.encode_value(value)
    _select_and_read(row, col, extra, 0.3)
    # The echo right after a write is a partial matrix that can stop before the
    # changed cell. Verify with a separate full read instead.
    time.sleep(0.1)
    points, msgs = _select_and_read(0, 0, [], seconds)
    # Label through get_matrix's entry point, off the read that just happened: selecting a
    # cell makes the Module send stream 20 as well, so this costs no extra round-trip. It
    # sits after the write, never between the select and the write (device-io.md:27-35).
    labels = matrix_map.preset_labels(
        setup.decode(_stream_pairs(msgs, haken.STREAM_MAT_POKE) or _read_setup()))
    here = next((p for p in points if p["row"] == row and p["col"] == col), None)
    got = here["value"] if here else ""
    want = value.strip().upper()
    if want.startswith("0."):
        want = want[1:]
    if want.startswith("."):
        want = want.rstrip("0")
    verified = got == want
    note = None
    if not verified and want and want[0].isalpha():
        # The Module omits cells whose formula is all zero from the matrix dump.
        # Check the formula number at the cell instead.
        num, _pairs = _read_formula_at(row, col, 1.0)
        if num is not None and haken.value_code_to_str(num) == want:
            verified = True
            got = want
            note = "formula is still all zero; the Module hides such cells until the formula is defined"
    out = {
        "row": row, "col": col,
        "row_name": matrix_map.row_name(row, labels),
        "col_name": matrix_map.col_name(col, labels),
        "requested": value, "device_value": got,
        "verified": verified,
        "matrix_count": len(points),
    }
    if note:
        out["note"] = note
    return out


@mcp.tool()
def describe_matrix_layout() -> dict:
    """Read-only, and preset-independent by design: the GENERIC row (source) and
    column (destination) layout, no device access. Rows 9-12 and the bank and
    Master columns depend on the loaded preset, so do not cross-reference this
    with get_matrix - get_matrix labels from the preset's own setup and is the
    authority for a specific preset. The verified/guide markers are source
    comments in matrix_map.py; this tool does not return them."""
    return {"rows": matrix_map.ROWS, "cols": matrix_map.COLS}


# ---------- formulas ----------

def _stream_pairs(msgs, stream_id: int) -> dict[int, int]:
    pairs, cur = {}, None
    for m in msgs:
        if m.type == "control_change" and m.channel == haken.CH16 and m.control == haken.CC_TEXT:
            cur = m.value
        elif m.type == "polytouch" and m.channel == haken.CH16 and cur == stream_id:
            pairs[m.note] = m.value
    return pairs


def _read_formula_at(row: int, col: int, seconds: float):
    conn.clear()
    _ping()
    for m in haken.select_point_msgs(row, col):
        conn.send(m)
    msgs = [m for _, m in conn.listen(seconds)]
    num = next((m.value for m in msgs if m.type == "control_change"
                and m.channel == haken.CH16 and m.control == haken.CC_FORM_SEL), None)
    return num, _stream_pairs(msgs, haken.STREAM_FORM_POKE)


@mcp.tool()
def get_formula(row: int, col: int, include_raw: bool = False, seconds: float = 1.0) -> dict:
    """Select the cell (row, col) and decode the formula it holds.
    Returns a one-line summary and decoded W/X/Y/Z components."""
    num, pairs = _read_formula_at(row, col, seconds)
    if not pairs:
        return {"row": row, "col": col, "formula": None,
                "note": "no formula stream; the cell is empty or holds a constant"}
    letter = haken.value_code_to_str(num) if num else None
    d = formula.decode(pairs)
    out = {"row": row, "col": col, "formula_number": num, "formula": letter,
           "summary": formula.summary(d), "decoded": d}
    if include_raw:
        out["raw"] = pairs
    return out


@mcp.tool()
def write_formula_raw(row: int, col: int, pairs: list[list[int]],
                      framing: str = "per_pair", seconds: float = 1.0) -> dict:
    """EXPERIMENTAL. Select the cell, write formula config (id, value) pairs to
    its formula, then read the formula back and report which ids changed.
    framing: "per_pair" (cc56=19 before each pair, like the Editor),
    "block" (cc56=19 once, then all pairs, then cc56=127),
    "per_pair_term" (cc56=19, pair, cc56=127 for each)."""
    before_num, before = _read_formula_at(row, col, seconds)
    for pid, val in pairs:
        if framing in ("per_pair", "per_pair_term"):
            conn.send(haken.cc16(haken.CC_TEXT, haken.STREAM_FORM_POKE))
            conn.send(mido.Message("polytouch", channel=haken.CH16, note=pid, value=val))
            if framing == "per_pair_term":
                conn.send(haken.cc16(haken.CC_TEXT, haken.STREAM_END))
        elif framing == "block":
            pass
        else:
            raise ValueError("unknown framing")
    if framing == "block":
        conn.send(haken.cc16(haken.CC_TEXT, haken.STREAM_FORM_POKE))
        for pid, val in pairs:
            conn.send(mido.Message("polytouch", channel=haken.CH16, note=pid, value=val))
        conn.send(haken.cc16(haken.CC_TEXT, haken.STREAM_END))
    time.sleep(0.2)
    after_num, after = _read_formula_at(row, col, seconds)
    changed = {k: [before.get(k), after.get(k)] for k in set(before) | set(after) if before.get(k) != after.get(k)}
    requested = {pid: val for pid, val in pairs}
    return {
        "formula_before": before_num, "formula_after": after_num,
        "requested": requested,
        "applied": all(after.get(k) == v for k, v in requested.items()),
        "changed_ids": changed,
        "summary_after": formula.summary(formula.decode(after)) if after else None,
    }


@mcp.tool()
def set_formula(row: int, col: int, component: str,
                mode: str | None = None, value: float | None = None,
                magnitude: float | None = None, modifier: str | None = None,
                macro: str | None = None, height_begin: float | None = None,
                height_end: float | None = None, multiplier: float | None = None,
                sg_shape: str | None = None, sg_phase: str | None = None,
                operator: str | None = None, transfer: str | None = None) -> dict:
    """Change the formula held by cell (row, col). Edit slot only.
    Returns summary_after - the formula as the device reports it back - plus
    changed_ids. There is NO `verified` field here, unlike set_matrix_point.
    An empty changed_ids with applied=true means the formula already matched the
    request, not that the write was lost.
    IMPORTANT: a formula letter is shared. Changing the formula in one cell changes
    it in every cell that uses the same letter.
    component "W": mode (Constant, Gated, SG1..SG5, SG1b..SG5b, FormulaDelay, "RMS of row"
      = the RMS of this matrix row over an 8 ms sliding window; only ONE formula can appear
      in a matrix RMS row in W),
      value (-1..1.27, step 0.01; W is the only component that reaches 1.27),
      magnitude: ONE OF 0.001, 0.01, 0.1, 1, 10, 100, 1000
      (powers of ten only; use it with value for finer steps), modifier ("x 1", "x Macro",
      "x 127 x Macro", "x Fingers scaler", "x Voice number", "x 1 if voice 1",
      "x Polyphony scaler"), macro ("i".."vi", "m7"..).
      Two of those modifier names mislead and are kept only because they are the shipped
      enum: "x Fingers scaler" is the header's wDivFings = 1/fingersDown, and
      "x Polyphony scaler" is wDivPoly = 1/thisDSPpoly (docs/HakenMidi.h:1212-1220). Both
      are RECIPROCALS - they divide, so W FALLS as more fingers land or as DSP polyphony
      rises. Use them to keep a sum constant across voices, not to emphasise one.
      sg_shape (when W mode is SGn): "Ramp Up", "Ramp Down", "Pulse", "Pulse at End",
      "Triangle", "Hann", "Gentle Up", "Steep Up", "Gentle Down", "Steep Down",
      "Square", "Sine" (last two bipolar), then sample-and-hold: "S+H row" (holds this
      matrix row) and "S+H A".."S+H V", "S+H A'".."S+H V'" (hold formula A..V / A'..V').
      Sample-and-hold needs a Continuous or Single Cycle SG; it is unavailable on a Dual SG.
      sg_phase, all 48 values: "Off", "0.25", "0.5", "0.75" (phase offsets of this SG),
      then phase modulation by a formula - "mod A".."mod V" and "mod A'".."mod V'".
      Build quadrature LFOs from ONE SG plus sg_phase offsets rather than from several SGs:
      several continuous SGs on different osc F columns make the panel knobs unusable,
      while one SG shared by those columns does not
      (get_knowledge("pitfalls") section 5, item 42 - the tested construction table).
    operator (any component): how W, X, Y, Z combine: "W + X + Y + Z" (default),
      "W x (X + Y + Z)", "(W + X + Y) x Z", "(W + X) x (Y + Z)", "(W x X) + (Y x Z)".
      E.g. envelope scaled by mod wheel: W = SGn envelope, Y on, operator "W x (X + Y + Z)".
    Incoming MIDI CC 1 (mod wheel) is read as Y. Macros i..iv = CC 12..15 on channel 1.
    The cell must already hold a formula letter (set_matrix_point first).
    Read get_knowledge("pitfalls") section 5 before putting SGs, macros or X formulas on
    osc F columns.
    component "X"/"Y"/"Z": height_begin, height_end (-1..1, step 0.01; both 0 = off;
      equal non-zero heights = constant offset); X/Y/Z heights cap at +-1.00 and W alone
      reaches further. multiplier ONE OF 0.001 .. 1000 (powers of ten),
      mode (Continuous, Initial, Derivative, Relative; X also "Continuous noTrim",
      "Initial noTrim", "Derivative noTrim", "Relative noTrim" = no trim graph applied,
      accepted for Y as well; Z instead has Release F, Release P),
      transfer (X: "X Oct", "X kHz", "Linear", "Gentle S", "Squared", "SquareRoot", "2 step",
      "3 step", "Graph", "Offsets 1", "Offsets 2", "Steep S"; Y/Z: same without X Oct/X kHz),
      macro ("none", "i".."vi", "m7"..) scales that component.
    X = finger left-right (pitch), Y = front-back, Z = pressure.
    A negative value or height is written with the header's sign encoding, which has never
    been confirmed on the Module (the open ROADMAP item "Verify a NEGATIVE formula
    height on the device"), so the result carries a warning."""
    pairs = formula.encode_changes(component, mode=mode, value=value, magnitude=magnitude,
                                   modifier=modifier, macro=macro, height_begin=height_begin,
                                   height_end=height_end, multiplier=multiplier,
                                   sg_shape=sg_shape, sg_phase=sg_phase, operator=operator,
                                   transfer=transfer)
    res = write_formula_raw(row, col, [list(p) for p in pairs])
    # Doubt is returned as data once the write has reached the device (error-handling.md:31),
    # and the envelope stays a flat dict of primitives (conventions.md:59-65), so two
    # concurrent warnings join into the one key instead of becoming a list or a second key.
    warnings = []
    if res.get("formula_before") in (None, 0):
        warnings.append("cell held no formula before; place a formula letter with set_matrix_point first")
    if any(v is not None and v < 0 for v in (value, height_begin, height_end)):
        warnings.append(
            "a negative value/height was written with the header's sign encoding, which has "
            "NOT been confirmed on the Module - the open ROADMAP item 'Verify a NEGATIVE "
            "formula height on the device' - so listen before trusting it. "
            "The encoding fix does not repair negative heights already stored in user slots "
            "4 and 5; rewrite those cells to correct them")
    if warnings:
        res["warning"] = " ; ".join(warnings)
    return res


# ---------- setup (oscillator types, banks, shape generators) ----------

def _read_setup(seconds: float = 4.0) -> dict[int, int]:
    """Stream-20 setup pairs. Needs matRefresh, not just a select (device-verified 10.81):
    with the select alone every selector read back as "?None"."""
    conn.clear()
    _ping()
    for m in haken.select_point_msgs(0, 0):
        conn.send(m)
    conn.send(haken.cc16(haken.CC_MATRIX_CTRL, haken.CMD_MATRIX_REFRESH))
    return _stream_pairs([m for _, m in conn.listen(seconds)], haken.STREAM_MAT_POKE)


def _write_setup(pid: int, value: int) -> dict:
    conn.send(haken.cc16(haken.CC_TEXT, haken.STREAM_MAT_POKE))
    conn.send(mido.Message("polytouch", channel=haken.CH16, note=pid, value=value))
    time.sleep(0.2)
    after = _read_setup()
    return {"id": pid, "requested": value, "device_value": after.get(pid),
            "verified": after.get(pid) == value}


@mcp.tool()
def get_setup() -> dict:
    """Read the current preset's setup: polyphony, the 5 oscillator/filter slot types,
    bank A/B/C types and shape generator types. Does not reload the preset."""
    return setup.decode(_read_setup())


@mcp.tool()
def set_osc_type(slot: int, type_name: str) -> dict:
    """Set oscillator/filter slot 1..5 type, e.g. "DSF Oscillator", "Jenny Oscillator",
    "Low Pass Filter", "Ladder Low Pass", "High Pass", "Band Pass", "Signal Multiplier",
    "Tanh", "Noise from Seed". Edit slot only, verified by read-back."""
    if not 1 <= slot <= 5:
        raise ValueError("slot must be 1..5")
    res = _write_setup(setup.OSC_TYPE_IDS[slot - 1], setup.osc_type_value(type_name))
    res["slot"], res["type"] = slot, setup.OSC_TYPES.get(res["device_value"])
    return res


@mcp.tool()
def set_bank_type(bank: str, type_name: str) -> dict:
    """Set bank A/B/C type. A/B: BiqBank, BiqGraph, BiqMouth, SineBank, SineSpray,
    WaveBank, HarMan, ModMan, Additive, Kinetic (B also CVC, unverified).
    C: VoiceDelay, SummedDelay, MicroDelay, FormulaDelay (+ Bank B shared types).
    Bank C values are not verified yet. Edit slot only, verified by read-back."""
    b = bank.upper()
    if b not in setup.BANK_IDS:
        raise ValueError("bank must be A, B or C")
    res = _write_setup(setup.BANK_IDS[b], setup.bank_type_value(b, type_name))
    res["bank"] = b
    return res


@mcp.tool()
def set_shape_generator(sg: int, type_name: str) -> dict:
    """Set shape generator 1..5 type: "Continuous Cycle" (LFO), "Single Cycle"
    (envelope-like, one cycle per trigger), "Phase from Matrix Row", "Dual".
    Frequency and trigger are set in the matrix: SG n columns 51+2(n-1) (F) and 52+2(n-1) (T).
    Use it in a formula with W mode "SGn". Edit slot only, verified by read-back."""
    if not 1 <= sg <= 5:
        raise ValueError("sg must be 1..5")
    res = _write_setup(setup.SG_IDS[sg - 1], setup.sg_type_value(type_name))
    res["sg"] = sg
    return res


# ---------- naming, user presets, saving ----------

@mcp.tool()
def list_user_presets(seconds: float = 6.0, search: str | None = None) -> dict:
    """Read-only. Ask the Module for user preset names (ch16 cc109=32).
    names_in_order: user slots 1..128 in order, then the current edit-slot name as the last entry.
    "-" = empty slot. search: return only matching names with their position (slot = position+1)."""
    conn.clear()
    _ping()
    conn.send(haken.cc16(haken.CC_COMMAND, haken.CMD_TRANSMIT_NAMES))
    msgs = [m for _, m in conn.listen(seconds)]
    entries, cur_id, buf, ctx = [], None, [], {}
    for m in msgs:
        if m.type == "control_change" and m.channel == haken.CH16:
            if m.control == haken.CC_TEXT:
                if cur_id is not None and cur_id != haken.STREAM_END and buf:
                    entries.append({"stream": cur_id, "text": "".join(chr(b) for b in buf if b).strip(), **ctx})
                cur_id, buf = m.value, []
            elif m.control in (0, 32, 57, 58, 112):
                ctx = {**ctx, f"cc{m.control}": m.value}
        elif m.type == "polytouch" and m.channel == haken.CH16 and cur_id is not None:
            buf += [m.note, m.value]
    names = [e for e in entries if e["stream"] == 0]
    out = {"message_count": len(msgs), "entries_count": len(entries),
           "name_count": len(names), "stream_ids": sorted({e["stream"] for e in entries})}
    if search:
        out["matches"] = [{"position": i, **e} for i, e in enumerate(names)
                          if search.lower() in e["text"].lower()]
    else:
        out["names_in_order"] = [e["text"] for e in names]
    return out


@mcp.tool()
def set_preset_name(name: str, description: str | None = None) -> dict:
    """Set the current (edit slot) preset's name (stream 0) and optionally its description
    (stream 1). Description conventions from factory presets: macro labels like
    "i=FM_Depth ii=Tone", then "C=<category codes>" and "A=<author>" on separate lines."""
    if len(name) > 32:
        raise ValueError("keep the name short (<= 32 chars)")
    for m in haken.text_stream_msgs(0, name):
        conn.send(m)
    if description is not None:
        for m in haken.text_stream_msgs(1, description):
            conn.send(m)
    return {"sent_name": name, "sent_description": description}


@mcp.tool()
def save_to_user_slot(slot: int, confirm: bool = False) -> dict:
    """Store the current sound to USER slot 1..128 in flash. Overwrites what is there.
    Only call with confirm=True after the user explicitly agreed to this exact slot.
    Verified working 2026-10-25 (cc0=0 user path). Verify with list_user_presets (read-only),
    not by loading the slot. Never verify by loading the slot before you know the store worked:
    loading replaces the edit slot and the unsaved sound is lost. Use list_user_presets first."""
    if not confirm:
        return {"stored": False, "note": "not stored: ask the user to confirm the slot, then call with confirm=True"}
    for m in haken.store_user_slot_msgs(slot):
        conn.send(m)
    conn.listen(1.5)  # the echo varies between saves; do not rely on it
    names = list_user_presets().get("names_in_order", [])
    current = names[-1] if names else None
    at_slot = names[slot - 1] if len(names) >= slot else None
    return {"stored": True, "slot": slot, "name_at_slot": at_slot, "current_name": current,
            "verified": at_slot is not None and at_slot == current,
            "note": "verified = the slot now carries the current sound's name (read-only check)"}


@mcp.tool()
def get_recipes() -> str:
    """Read-only. Tested recipes: how to build common synth ideas (pitch, volume, LFO,
    envelope, FM, mod wheel, macros) out of matrix cells and formulas, each one tried by ear
    on the Module. Read this before building a patch.
    A pitfall inseparable from a recipe's steps stays with that recipe here; the standalone
    ones live in get_knowledge("pitfalls"), which is canonical for them, and the reference
    behind these recipes is get_knowledge()."""
    # PROJECT_DIR is the repo when running from a checkout; on a wheel install it is
    # site-packages/ and holds no RECIPES.md, so fall back to the copy force-included
    # into the package. Same bytes, one source of truth (pyproject.toml).
    for path in (PROJECT_DIR / "RECIPES.md", KNOWLEDGE_DIR / "recipes.md"):
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise RuntimeError(
        "RECIPES.md not found at either the repo root or inside the installed package; "
        "a wheel built without the force-include in pyproject.toml would do this")


@mcp.tool()
def set_polyphony(voices: int, expanded: bool | None = None,
                  double_computation_rate: bool | None = None) -> dict:
    """Set base polyphony 1..8 (s_Mat_Poke id 39). Edit slot only, verified by read-back.
    expanded = "+" (more voices if DSP allows), double_computation_rate = "^" (better highs,
    half the voices). The Module may still run fewer voices if the patch is too heavy: check
    get_status (dsp_polyphony, dsp_usage_percent).
    The 1..8 ceiling is the header's own (docs/HakenMidi.h:1357, idPoly "values 1..8") and
    this tool keeps it, although 24 factory presets (of 668) store 10, 12 or 14 and the
    same header names maxNonMpePoly = 14 at :1360 (14 voices when nothing plays on channels
    1 and 16). Writing past a documented bound is not something to try blind: device test
    TEST-POLY-14 would settle it. Until it runs, use expanded=True for more voices."""
    low, high = 1, 8        # docs/HakenMidi.h:1357 idPoly: "values 1..8"
    if not low <= voices <= high:
        raise ValueError(
            f"base polyphony is {low}..{high} (use expanded=True for more). "
            f"docs/HakenMidi.h:1357 bounds idPoly at {low}..{high}; :1360 names "
            "maxNonMpePoly = 14 and 24 factory presets store 10/12/14, so the ceiling may "
            "really be higher - unverified, and device test TEST-POLY-14 is what would "
            "settle it")
    res = {"base": _write_setup(setup.POLY_ID, voices)}
    if expanded is not None:
        res["expanded"] = _write_setup(setup.OK_EXP_POLY_ID, int(expanded))
    if double_computation_rate is not None:
        res["double_rate"] = _write_setup(setup.OK_INC_COMP_ID, int(double_computation_rate))
    res["verified"] = all(r["verified"] for r in res.values() if isinstance(r, dict))
    return res


@mcp.tool()
def set_bend_range(semitones: int, all_channels: bool = False) -> dict:
    """Set the preset's pitch bend range (s_Mat_Poke id 40, saved with the preset).
    Default (all_channels=False): Haken "96:n" form. MPE channels keep +-96 and a plain MIDI
    keyboard on channel 1 bends +-semitones (value 95+n, e.g. 96:2 = 97, 96:12 = 107), n 2..32.
    all_channels=True: the same range everywhere (value = semitones, 1..96).
    The Module does not echo this value without a preset reload: check by playing, or with
    listen while moving the wheel (voice bends are reported at 96 st scale, so +-2 st shows
    as about +-170 of 8192). Edit slot only."""
    if all_channels:
        if not 1 <= semitones <= 96:
            raise ValueError("semitones must be 1..96")
        value, label = semitones, f"{semitones} (all channels)"
    else:
        if not 2 <= semitones <= 32:
            raise ValueError("channel-1 range in the 96:n form must be 2..32")
        value, label = 95 + semitones, f"96:{semitones}"
    res = _write_setup(setup.BEND_RANGE_ID, value)
    res["setting"] = label
    if res["device_value"] is None:
        res["verified"] = None
        res["note"] = "sent; the Module does not echo id 40, verify by playing or with listen"
    return res


# ---------- knowledge ----------

def _grep(files: list[Path], query: str, max_hits: int, context: int,
          root: Path) -> list[dict]:
    words = [w.lower() for w in query.split() if w]
    hits = []
    for fp in files:
        try:
            lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            low = line.lower()
            if all(w in low for w in words):
                lo, hi = max(0, i - context), min(len(lines), i + context + 1)
                # as_posix(), not str(): a Path is not JSON-serialisable through MCP and
                # Windows would yield "modules\\x.md", missing the forward-slash topic keys.
                hits.append({"file": fp.relative_to(root).as_posix(), "line": i + 1,
                             "snippet": "\n".join(lines[lo:hi])})
                if len(hits) >= max_hits:
                    return hits
    return hits


def _require_docs() -> None:
    """Fail loudly when docs/ is missing instead of reporting "no hits".

    docs/ is gitignored (6.5 MB of guide text) and is NOT in the wheel, so on any install
    that is not a checkout these two tools have nothing to read. _grep swallows OSError and
    continues, so without this guard search_docs returned [] - indistinguishable from "the
    guides say nothing", on the one evidence base the knowledge documents cite 1,081 times.
    """
    if not DOCS_DIR.is_dir():
        raise RuntimeError(
            f"the Haken guides are not installed at {DOCS_DIR}. They are gitignored and not "
            "shipped in the wheel, so a [G] citation in the knowledge base cannot be followed "
            "from here. Copy the 10.81 guide text and HakenMidi.h into that directory, or read "
            "the quoted evidence in the knowledge documents themselves via get_knowledge")


@mcp.tool()
def search_docs(query: str, max_hits: int = 10, context: int = 4) -> list[dict]:
    """Read-only. Search the Haken user guides, cookbooks and HakenMidi.h (the official
    MIDI protocol header) as text under docs/. All words must appear on the same line.
    Cite file and line in answers. RAISES if docs/ is absent rather than returning no
    hits, because the knowledge base's [G] citations all point here: an empty result
    must mean "the guides do not say that", never "the guides are not installed"."""
    _require_docs()
    files = sorted(DOCS_DIR.glob("*.txt")) + [DOCS_DIR / "HakenMidi.h"]
    return _grep(files, query, max_hits, context, DOCS_DIR)


@mcp.tool()
def read_docs(file: str, start_line: int, num_lines: int = 80) -> str:
    """Read-only. Read a range of lines from a docs/ file found via search_docs."""
    _require_docs()
    lines = (DOCS_DIR / file).read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[max(0, start_line - 1): start_line - 1 + num_lines])


@mcp.tool()
def search_preset_descriptions(query: str, max_hits: int = 20) -> list[dict]:
    """Read-only. Search the 661 factory preset descriptions written by Haken Audio's preset
    designers (copyright Haken Audio, included with permission; credit Haken Audio when quoting).

    Answers from descriptions.json inside this package, so it needs no device, no MIDI port
    and no HAKEN_EDITOR_DIR. Every space-separated word must appear in the same description.
    Returns {"preset": <name>, "snippet": <the matching text>} per hit.

    These are the designers' own prose about what a preset is and which controls do what, so
    they are the best plain-words index into the factory library; search_factory_presets is
    the structural counterpart over decoded wiring.
    """
    words = [w.lower() for w in query.split() if w]
    if not words:
        raise ValueError("query is empty")
    hits = []
    for name, text in FACTORY_DESCRIPTIONS.items():
        low = text.lower()
        if all(w in low for w in words):
            hits.append({"preset": name, "snippet": text})
            if len(hits) >= max_hits:
                break
    return hits


# Deliberately package-relative, NOT PROJECT_DIR like DOCS_DIR, CAPTURE_DIR and RECIPES.md
# above: the knowledge base must travel with the wheel. A `pip install eagan_mcp` on a phone
# has to answer every knowledge query with no repository checked out, no Haken Editor
# installed and no build step - so the data lives inside the package and is addressed from
# __file__. This is the one data path in this file that breaks the repo-relative convention,
# and the reason is that constraint alone.
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"


# The shipped JSON artifacts, loaded once at import. They are committed package data, not
# built at install time, so every filter below answers with no device, no MIDI port and no
# HAKEN_EDITOR_DIR. Read-only and parsed in about 10 ms, so a caching layer would be the
# speculative abstraction `minimal-implementation.md:15-16` forbids.
def _knowledge_json(name: str) -> dict:
    return json.loads((KNOWLEDGE_DIR / name).read_text(encoding="utf-8"))


FACTORY_CATALOG = _knowledge_json("factory_catalog.json")
FACTORY_PRESETS = FACTORY_CATALOG["presets"]
FACTORY_PRESETS_BY_NAME = {record["name"]: record for record in FACTORY_PRESETS}
FACTORY_DESCRIPTIONS = _knowledge_json("descriptions.json")
_CENSUS = _knowledge_json("census.json")
_PRESET_INDEX = _knowledge_json("preset_index_1081.json")

# Each allowlist is derived from census.json, so it cannot drift from the data it filters
# and the refusals below list exactly what the lookup consults (`validation.md:19`).
# `category` is the UNION of the 13 populated tags and the Module's 14-slot category menu:
# UP is a real menu slot holding no factory preset, so it is accepted and matches nothing.
CATEGORY_TAGS = sorted(set(_CENSUS["category_main"]) | set(_PRESET_INDEX["menu_order"]))
EMPTY_CATEGORY_TAGS = sorted(_PRESET_INDEX["menu_slots_with_no_presets"])
TECHNIQUE_TAGS = sorted(_CENSUS["techniques"])
BANK_NAMES = sorted(setup.BANK_IDS)
# Recirculator and Convolution are not module types - neither appears in the census' module
# space and `convolution` is a technique tag - but both have a module card and both queries
# have to answer, so each is unioned in here and matched on the state the records carry.
MODULE_NAMES = sorted(list(_CENSUS["modules_used_including_defaults"])
                      + ["Recirculator", "Convolution"])
DEFAULT_RECIRCULATOR = FACTORY_CATALOG["resolved_defaults"]["recirculator"]


def _module_matches(record: dict, module: str) -> bool:
    if module == "Recirculator":
        # No record says "this preset uses the recirculator": every record carries a
        # RESOLVED type, 364 of them inherited. Selecting a type other than the default is
        # the only deliberate-use signal in the shipped data, and it misses the 41 presets
        # that explicitly select the default, which read here exactly like the inherited one.
        return record["recirculator"] != DEFAULT_RECIRCULATOR
    if module == "Convolution":
        return "convolution" in record["techniques"]
    modules = record["modules_used_including_defaults"]
    # A bare name also matches the Bank C "(alias of B)" form, because a caller asking for
    # WaveBank wants it in any bank. The suffixed string matches only itself.
    return module in modules or f"{module} (alias of B)" in modules


def _preset_summary(record: dict) -> dict:
    return {"name": record["name"], "category": record["category_main_tag"],
            "system_slot": record["system_slot"],
            "flat_preset_number": record["flat_preset_number"],
            "generation": record["generation"],
            "modules": record["modules_used_including_defaults"],
            "polyphony": record["polyphony"]["base"],
            "macro_labels": record["macro_labels"],
            "techniques": record["techniques"],
            "has_wiring": "wiring" in record}


@mcp.tool()
def search_factory_presets(text: str | None = None, category: str | None = None,
                           module: str | None = None, technique: str | None = None,
                           bank: str | None = None, preset: str | None = None,
                           max_hits: int = 20) -> dict:
    """Read-only. Query the 668 factory presets of Haken Editor 1081 from data committed
    inside this package: no device, no MIDI port, no HAKEN_EDITOR_DIR, nothing written.
    The presets are Haken Audio's factory library, decoded and included with permission.

    Two modes, and they are exclusive.

    SEARCH - any of text/category/module/technique/bank, combined with AND; no argument at
    all returns the whole corpus. Returns {"count": <total matches>, "truncated": <total is
    above max_hits>, "presets": [<summary>, ...]} with at most max_hits summaries. `count`
    is the TOTAL, not the page length, so `truncated` says what the page left out. A
    summary carries name, category, system_slot, flat_preset_number, generation, modules,
    polyphony (the base voice count), macro_labels, techniques and has_wiring - never a
    full record.

    LOOKUP - preset="<exact preset name>" returns {"preset": {<the full 25-field record>}},
    plus a `wiring` block of decoded matrix cells and formula letters on the 49 presets
    that carry one (has_wiring in the summary says which). This is the only route to a full
    record. preset= together with any filter is a ValueError: search first, then look the
    name up.

    text      all words must appear, case-insensitively, in the preset name or in its long
              description (661 of the 668 have one), so plain-words requests such as
              "breathy" or "bowed string" stay reachable.
    category  ONE OF ST Strings, WI Winds, VO Vocal, KY Keyboard, CL Classic, OT Other,
              PE Percussion, PT Perc Tuned, PR Processor, DO Drone, MD Midi, CV CVC,
              UT Utility - plus UP, a real slot of the Module's 14-slot category menu that
              holds no factory preset: it is accepted and returns count 0 rather than a
              refusal.
    module    ONE OF 39 strings, in setup.py's spellings. The five most frequent are
              "DSF Oscillator" (466 presets), "BiqBank" (151), "VoiceDelay" (110),
              "HarMan" (105) and "SummedDelay" (98); the ValueError on an unknown value
              lists all 39. A bare name also matches the Bank C "<name> (alias of B)" form,
              which means Bank C mirrors Bank B's module - so module="WaveBank" finds 98
              and module="WaveBank (alias of B)" finds the 1 of them whose Bank C does it.
              Both spellings are accepted. "Recirculator" and "Convolution" are accepted
              although neither is a bank or oscillator type: Recirculator matches the 263
              presets selecting a type other than the inherited default Short Reverb (the
              41 that explicitly select the default cannot be told apart here from the 364
              that inherit it), and Convolution matches the `convolution` technique tag.
              "Granulate Delay Tap" is deliberately absent: it is a delay tap mode rather
              than a module and has no module card, so technique="granulate_tap" is the
              query for it.
    technique ONE OF 52 tags. The five most frequent are "direct_additive_row" (646),
              "z_modulation" (602), "direct_multiply_row" (553), "shape_generator_wired"
              (539) and "shape_generator_formula" (536); the ValueError on an unknown value
              lists all 52.
    bank      ONE OF "A", "B", "C" - the presets where that bank is IN USE, which is
              narrower than the bank type the device runs in that slot (every preset
              resolves to a type there, used or not).
    max_hits  1 or more, default 20. Caps `presets` only; `count` is unaffected.

    A resolved type says what the device RUNS in a slot, not that the preset uses it; only
    the 49 wiring blocks settle that for oscillators, shape generators and the recirculator.
    Inside a wiring block, a formula letter whose summary reads "(all components zero)" may
    still carry content on its blend and secondary sliders - 19 of 563 letters do - so read
    that letter's `blend` and `secondary` keys rather than its summary.
    """
    if max_hits < 1:
        raise ValueError(f"max_hits must be 1 or more, got {max_hits}")
    if category is not None and category not in CATEGORY_TAGS:
        raise ValueError(
            f"unknown category {category!r}; options: {CATEGORY_TAGS}, of which "
            f"{EMPTY_CATEGORY_TAGS} hold no factory presets and return count 0")
    if module is not None and module not in MODULE_NAMES:
        raise ValueError(f"unknown module {module!r}; options: {MODULE_NAMES}")
    if technique is not None and technique not in TECHNIQUE_TAGS:
        raise ValueError(f"unknown technique {technique!r}; options: {TECHNIQUE_TAGS}")
    if bank is not None and bank not in BANK_NAMES:
        raise ValueError(f"unknown bank {bank!r}; options: {BANK_NAMES}")

    if preset is not None:
        given = sorted(name for name, value in (("text", text), ("category", category),
                                                ("module", module),
                                                ("technique", technique), ("bank", bank))
                       if value is not None)
        if given:
            raise ValueError(
                f"preset={preset!r} is a full-record lookup and cannot be combined with a "
                f"filter; drop {given} to look it up, or drop preset= and search")
        record = FACTORY_PRESETS_BY_NAME.get(preset)
        if record is None:
            raise ValueError(
                f"unknown preset {preset!r}; preset= takes one exact factory preset name "
                "out of the 668 in the catalog - find one with text=, then look it up")
        return {"preset": record}

    words = [word.lower() for word in text.split()] if text else []
    hits = []
    for record in FACTORY_PRESETS:
        if category is not None and record["category_main_tag"] != category:
            continue
        if technique is not None and technique not in record["techniques"]:
            continue
        if bank is not None and not record["bank_in_use"][bank]:
            continue
        if module is not None and not _module_matches(record, module):
            continue
        if words:
            haystack = (record["name"] + "\n"
                        + FACTORY_DESCRIPTIONS.get(record["name"], "")).lower()
            if not all(word in haystack for word in words):
                continue
        hits.append(record)
    return {"count": len(hits), "truncated": len(hits) > max_hits,
            "presets": [_preset_summary(record) for record in hits[:max_hits]]}


# The topic allowlist: the ONLY route from a caller's string to a file. It is a lookup, never
# a path join, so an argument that is not already a key cannot reach the filesystem at all
# (`validation.md:26`, allowlists over blocklists) - which is how `get_knowledge` avoids the
# unvalidated `(DOCS_DIR / file)` traversal `read_docs` still has above. The same dict feeds
# the refusal message, so the advertised options cannot drift from the accepted ones
# (`validation.md:19`). Every value is a file that ships in the package: a topic with nothing
# behind it is forbidden by `minimal-implementation.md:12`, and a card with no topic in front
# of it would be unreachable through the MCP. `tests/test_knowledge_topics.py` pins both
# directions.
KNOWLEDGE_TOPICS = {
    "model": "model.md",
    "modules": "modules/index.md",
    "modules/additive": "modules/additive.md",
    "modules/biqbank": "modules/biqbank.md",
    "modules/biqgraph": "modules/biqgraph.md",
    "modules/biqmouth": "modules/biqmouth.md",
    "modules/convolution": "modules/convolution.md",
    "modules/cvc": "modules/cvc.md",
    "modules/formuladelay": "modules/formuladelay.md",
    "modules/harman": "modules/harman.md",
    "modules/kinetic": "modules/kinetic.md",
    "modules/microdelay": "modules/microdelay.md",
    "modules/modman": "modules/modman.md",
    "modules/oscillator-slots": "modules/oscillator-slots.md",
    "modules/recirculator": "modules/recirculator.md",
    "modules/sinebank": "modules/sinebank.md",
    "modules/sinespray": "modules/sinespray.md",
    "modules/summeddelay": "modules/summeddelay.md",
    "modules/voicedelay": "modules/voicedelay.md",
    "modules/wavebank": "modules/wavebank.md",
    "patterns": "patterns.md",
    "pitfalls": "pitfalls.md",
    "worked-examples": "worked_examples.md",
}


@mcp.tool()
def get_knowledge(topic: str | None = None, query: str | None = None, max_hits: int = 10,
                  context: int = 4) -> str | dict | list[dict]:
    """Read-only. The EaganMatrix knowledge base, committed inside this package: no device,
    no MIDI port, no HAKEN_EDITOR_DIR, nothing written. Read it before building a patch.

    Three modes.

    NO ARGUMENT - get_knowledge() returns {"topics": [<the 23 topic strings>], "index":
    "<the whole of modules/index.md>", "count": 23}. Start here: the index names the nine
    shared module facts and the Master chain tables, so one call orients you.

    ONE TOPIC - get_knowledge("model") returns that whole document as a string.

    TOPIC PLUS QUERY - get_knowledge("modules/biqbank", query="sF") greps INSIDE that one
    document and returns [{"file", "line", "snippet"}, ...]: all words must appear on the
    same line, case-insensitively, and each hit carries `context` lines either side. `query`
    without a `topic` is a ValueError - there is nothing to scope the search to. Cite file
    and line in answers.

    topic     ONE OF, exactly:
              "model"              how a voice is computed, the five loudness rules N1-N5,
                                   what this MCP cannot do, and the standing hazards
              "modules"            the module index: shared facts and the Master chain
              "patterns"           reusable constructions across modules
              "pitfalls"           the 76 ways to break a patch, in the order you hit them
              "worked-examples"    complete patches built step by step
              and one card per module type:
              "modules/additive"          "modules/biqbank"        "modules/biqgraph"
              "modules/biqmouth"          "modules/convolution"    "modules/cvc"
              "modules/formuladelay"      "modules/harman"         "modules/kinetic"
              "modules/microdelay"        "modules/modman"         "modules/oscillator-slots"
              "modules/recirculator"      "modules/sinebank"       "modules/sinespray"
              "modules/summeddelay"       "modules/voicedelay"     "modules/wavebank"
    max_hits  cap on returned hits in query mode (default 10, as search_docs).
    context   lines of context either side of a hit (default 4, as search_docs).

    Every claim in these documents carries an evidence tag; treat an unverified one as a
    hypothesis to test on the Module, not as fact. RECIPES.md (get_recipes) is the separate,
    tested-by-ear recipe book - this is the reference behind it."""
    if topic is not None and topic not in KNOWLEDGE_TOPICS:
        raise ValueError(f"unknown knowledge topic {topic!r}; options: {sorted(KNOWLEDGE_TOPICS)}")
    if topic is None and query is not None:
        raise ValueError(
            f"query={query!r} greps inside one document, so it needs a topic; call "
            f"get_knowledge() with no argument for the index, or name one of "
            f"{sorted(KNOWLEDGE_TOPICS)}")

    if topic is None:
        return {"topics": sorted(KNOWLEDGE_TOPICS),
                "index": (KNOWLEDGE_DIR / KNOWLEDGE_TOPICS["modules"]).read_text(
                    encoding="utf-8"),
                "count": len(KNOWLEDGE_TOPICS)}
    path = KNOWLEDGE_DIR / KNOWLEDGE_TOPICS[topic]
    if query is None:
        return path.read_text(encoding="utf-8")
    return _grep([path], query, max_hits, context, KNOWLEDGE_DIR)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
