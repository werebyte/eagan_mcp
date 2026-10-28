"""The three read-path fixes made during the 2026-10-27 device session.

All three were found with the rack powered on and fixed by hand; none had a test, so a
refactor could silently undo them and the only symptom would be "the device seems quiet
again" - the exact condition that wasted the first hour of that session.

  1. `midi_io.listen()` cleared the receive buffer as its first act. Every request-then-read
     caller in server.py does `clear()` -> send request -> `listen()`, and the Module answers
     in milliseconds, so the reply was discarded before the sleep even started. get_status
     reported all nulls against a working device.
  2. A cell select alone does NOT make the Module dump its state on fw 10.81 - it returns a
     cc45 echo and nothing else. `ccMatOp 124` (matRefresh) is the trigger, so the read paths
     have to send it.
  3. One listen window can catch TWO dumps (a preset load's own, plus a matRefresh), and the
     same cell then decodes twice. Measured: 50 cells for a 25-cell patch.

SCOPE OF THIS SUITE
-------------------
Host-only. These pin the SHAPE of the read path - what gets sent, what survives buffering -
not what the firmware does with it. No MIDI port is opened and a green run closes no
device-test item.
"""

import time

import mido

from eagan_mcp import haken, midi_io, server


# ---------------------------------------------------------------- 1. the listen() race

def test_listen_does_not_discard_what_already_arrived():
    """The race, as a property: a reply buffered BEFORE listen() must survive it.

    This is the whole bug. The device answers a request faster than the interpreter reaches
    the next line, so anything that clears on entry throws the answer away. Restoring the
    `self.clear()` that used to open this method makes this test fail.
    """
    conn = midi_io.EmConnection()
    reply = mido.Message("control_change", channel=15, control=114, value=14)
    conn._on_msg(reply)                      # the device answered while we were still setting up

    got = [m for _, m in conn.listen(0.01)]
    assert got == [reply], (
        "listen() dropped a message that was already buffered. Clearing is the CALLER's job, "
        "before it sends its request - see midi_io.listen's docstring")


def test_listen_still_collects_what_arrives_during_the_window():
    conn = midi_io.EmConnection()
    conn._on_msg(mido.Message("control_change", channel=15, control=111, value=1))
    conn._on_msg(mido.Message("control_change", channel=15, control=118, value=8))
    assert len(conn.listen(0.01)) == 2


def test_listen_still_filters_realtime_noise():
    conn = midi_io.EmConnection()
    conn._on_msg(mido.Message("clock"))
    conn._on_msg(mido.Message("control_change", channel=15, control=114, value=14))
    kept = [m for _, m in conn.listen(0.01)]
    assert [m.type for m in kept] == ["control_change"]
    assert len(conn.listen(0.01, skip_realtime=False)) == 0, "drain must have emptied it"


# ------------------------------------------------- 2. the read paths must ask for a refresh

class _SpyConn:
    """Records what the server sends and replays a canned reply."""

    def __init__(self, reply=()):
        self.sent: list[mido.Message] = []
        self._reply = list(reply)

    def clear(self):
        pass

    def send(self, msg):
        self.sent.append(msg)

    def listen(self, seconds, skip_realtime=True):
        return [(time.time(), m) for m in self._reply]

    def ch16(self, control):
        return [m.value for m in self.sent
                if m.type == "control_change" and m.channel == haken.CH16
                and m.control == control]


def test_get_matrix_asks_for_a_matrix_refresh(monkeypatch):
    """A select alone returns nothing on fw 10.81, so the read path must send ccMatOp 124.

    Device-observed 2026-10-27: selecting cell (0,0) produced 13 messages, all status, and no
    matrix at all; matRefresh produced ~1,100 carrying the matrix, stream 20 and the texts.
    """
    spy = _SpyConn()
    monkeypatch.setattr(server, "conn", spy)
    server._select_and_read(0, 0, [], 0.01)

    assert haken.CMD_MATRIX_REFRESH in spy.ch16(haken.CC_MATRIX_CTRL), (
        "the read path never sent ccMatOp 124 (matRefresh). Without it the Module returns an "
        f"echo and no state: sent {spy.ch16(haken.CC_MATRIX_CTRL)}")


def test_read_setup_asks_for_a_matrix_refresh(monkeypatch):
    """Without the refresh every setup selector read back as "?None" against a loaded preset."""
    spy = _SpyConn()
    monkeypatch.setattr(server, "conn", spy)
    server._read_setup(0.01)

    assert haken.CMD_MATRIX_REFRESH in spy.ch16(haken.CC_MATRIX_CTRL), (
        "_read_setup never sent matRefresh; stream 20 does not arrive from a bare select")


def test_the_refresh_follows_the_select_not_precedes_it(monkeypatch):
    """Order matters: select the cell, THEN ask for the dump.

    device-io.md requires nothing between a select and the write it targets, and the refresh
    is what makes the state come back, so it belongs last.
    """
    spy = _SpyConn()
    monkeypatch.setattr(server, "conn", spy)
    server._select_and_read(3, 4, [], 0.01)

    ops = [(m.control, m.value) for m in spy.sent
           if m.type == "control_change" and m.channel == haken.CH16
           and m.control == haken.CC_MATRIX_CTRL]
    assert ops, "no ccMatOp traffic at all"
    assert ops[0][1] == haken.CMD_SELECT_POINT, f"first ccMatOp should be the select, got {ops}"
    assert ops[-1][1] == haken.CMD_MATRIX_REFRESH, f"last ccMatOp should be the refresh: {ops}"


# ----------------------------------------------------------- 3. two dumps in one window

def _matrix_msgs(cells):
    out = [mido.Message("control_change", channel=haken.CH16,
                        control=haken.CC_MATRIX_CTRL, value=haken.MATRIX_START)]
    for row, col, code in cells:
        out += [
            mido.Message("control_change", channel=haken.CH16, control=haken.CC_ROW, value=row),
            mido.Message("control_change", channel=haken.CH16, control=haken.CC_COL, value=col),
            mido.Message("control_change", channel=haken.CH16, control=haken.CC_VALUE,
                         value=code),
        ]
    return out


def test_decode_matrix_dedupes_two_dumps_in_one_window():
    """A load's own dump plus a matRefresh gives every cell twice; 25 cells read as 50."""
    cells = [(13, 28, 46), (6, 0, 48), (13, 51, 45)]
    once = haken.decode_matrix(_matrix_msgs(cells))
    twice = haken.decode_matrix(_matrix_msgs(cells) + _matrix_msgs(cells))

    assert len(once) == len(cells)
    assert len(twice) == len(cells), (
        f"two dumps decoded to {len(twice)} cells for a {len(cells)}-cell patch; duplicates "
        "make a caller believe the matrix is bigger than it is")
    assert {(p["row"], p["col"]) for p in twice} == {(r, c) for r, c, _ in cells}


def test_decode_matrix_keeps_the_LAST_reading_of_a_cell():
    """When a cell appears twice the newer value wins - it is the more recent state."""
    first = _matrix_msgs([(13, 28, 46)])                 # X
    second = _matrix_msgs([(13, 28, 47)])                # Y, a later edit
    points = haken.decode_matrix(first + second)

    assert len(points) == 1
    assert points[0]["value"] == haken.value_code_to_str(47), (
        "the earlier reading won; a read taken after a write would report the pre-write value")


# --------------------------------------------- 4. the docs must teach the mechanism that works

def test_get_matrix_docstring_does_not_teach_the_superseded_read():
    """The docstring is the prompt an agent reads, so a stale one is a wrong mental model.

    This exists because it happened. `get_matrix`'s docstring said "Works by selecting cell
    (0,0); the Module re-sends the matrix" for a day AFTER the device showed that a bare select
    returns an echo and no matrix. The edit meant to fix it was a `.replace()` with the wrong
    indentation and no assertion, so it silently did nothing and was committed anyway - and the
    acceptance test then reported, correctly, that a fresh session has a wrong model of every
    read. A test is cheaper than remembering.
    """
    doc = (getattr(server.get_matrix, "fn", server.get_matrix).__doc__ or "")
    assert "matRefresh" in doc or "124" in doc, (
        "get_matrix's docstring does not name the refresh that makes a read work on fw 10.81")
    assert "re-sends the matrix" not in doc, (
        "get_matrix's docstring still teaches the superseded mechanism - a cell select alone "
        "returns an echo and no matrix on fw 10.81")


def test_the_knowledge_base_explains_how_a_read_works():
    """A fresh session has only the shipped documents; the read mechanism has to be in them.

    The acceptance test found `matRefresh` in 0 of the 23 knowledge documents while the device
    notes had recorded it for a day. The knowledge base is what someone installing the package
    gets, so a device fact that only lives in CLAUDE.md is a fact they do not have.
    """
    from pathlib import Path
    docs = sorted(Path("eagan_mcp/knowledge").rglob("*.md"))
    assert docs, "no knowledge documents found"
    hits = [p.name for p in docs
            if "matRefresh" in p.read_text(encoding="utf-8")
            or "ccMatOp 124" in p.read_text(encoding="utf-8")]
    assert hits, (
        "no shipped knowledge document explains how a read works on fw 10.81. An agent with "
        "only this package cannot know that a cell select returns nothing and matRefresh is "
        "the trigger")


def test_set_formula_does_not_claim_a_verified_field_it_never_returns():
    """set_formula returns summary_after, NOT verified - and the skill used to say otherwise.

    Followed literally, the old wording ("`set_matrix_point` and `set_formula` each report
    `device_value` and `verified` ... treat `verified` as false or unknown as a stop") makes
    EVERY formula write a stop. Checked against the live signature rather than the source, which
    is how the contradiction was missed the first time.
    """
    from pathlib import Path
    doc = (getattr(server.set_formula, "fn", server.set_formula).__doc__ or "")
    assert "no" in doc.lower() and "verified" in doc.lower(), (
        "set_formula's docstring must say it returns no `verified` field, so a caller does not "
        "wait for one")

    skill = Path(".claude/skills/eagan-patch-design/SKILL.md").read_text(encoding="utf-8")
    offending = "`set_matrix_point` and `set_formula` each\n    report `device_value` and `verified`"
    assert offending not in skill, (
        "eagan-patch-design still claims set_formula reports `verified`; it does not, so the "
        "skill's own stop-on-unverified rule would halt every formula write")
