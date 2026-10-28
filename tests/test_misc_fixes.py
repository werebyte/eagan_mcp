"""Four fixes that would otherwise ship untested, one of them in the flash path.

`save_to_user_slot` is the only tool that writes the Module's flash, so
`device-safety.md:6-12` makes its read-back guard testable surface rather than a detail.
The guard read `len(names) > slot` where the index it protects is `names[slot - 1]`, so
the last listed entry was reported as `None`. `list_user_presets` returns 128 slot names
plus the edit-slot name, so on a complete listing the guard is merely off by one and never
fires; it fires when the listen window returns a short list, which `device-io.md:16-18`
records as a real and recurring condition. A successful store would then be reported
`verified: False`.

`matrix_map.COLS` stopped at 10 and then jumped to 12, so column 11 fell through `col_name`
to the generic `"col 11"`. The header names it `cSep` ("no column selected",
docs/HakenMidi.h:680), and modern preset files select row 0 / column 11 to end the matrix
block, so the hole is on a path every preset read crosses.

`haken.CC_TRANSMIT_UPDATES = 55` was unused *and* wrong for 10.81: ch16 cc55 is
`ccCreaArchFin` (docs/HakenMidi.h:815), not an auto-transmit flag. The cc55 config
mechanism is pre-1009 and was replaced by `s_Mat_Poke idCfgOut`.
`minimal-implementation.md:24-26`'s unused-constant carve-out keeps a constant that
documents the wire correctly; a constant that misnames a controller is not documentation,
so the fix is deletion. This test pins the outcome either way: the attribute is gone, or
it is correct (header-cited) and has a caller.

`set_formula` writes a negative height with a sign encoding that has never been confirmed
on the Module, and it already carried one `warning` of its own for a cell with no formula
letter. Both doubts can apply to the same call, and `conventions.md:59-65` allows only a
flat dict of primitives, so they join with `" ; "` into the one `warning` key. The write
proceeds either way: a negative height is how the vowel wah is built, so refusing it would
refuse a shipped recipe (`error-handling.md:31` - doubt is returned, not raised).

SCOPE OF THIS SUITE
-------------------
Like every test file here, this suite pins the codec and the tool surface to
corpus-derived semantics. It is NOT device verification: nothing here touches the Module,
and a green run says nothing about what the firmware does.
"""

from pathlib import Path

from eagan_mcp import haken, matrix_map, server


class _SilentConn:
    """Stands in for the open USB connection: swallows sends, hears nothing back."""

    def __init__(self):
        self.sent = []

    def send(self, msg):
        self.sent.append(msg)

    def listen(self, seconds):
        return []

    def clear(self):
        pass


def test_save_to_user_slot_accepts_the_last_listed_slot(monkeypatch):
    """With len(names) == slot the slot's name must be returned, not None."""
    names = ["Sitar Mute Pluck", "Sitar FM Pluck", "Saw Swarm Warm", "Sitar Modal Pluck"]
    slot = len(names)
    conn = _SilentConn()
    monkeypatch.setattr(server, "conn", conn)
    monkeypatch.setattr(server, "list_user_presets", lambda *a, **kw: {"names_in_order": names})

    out = server.save_to_user_slot(slot, confirm=True)

    assert out["stored"] is True
    assert out["name_at_slot"] == names[slot - 1], (
        f"save_to_user_slot reported {out['name_at_slot']!r} for the last listed slot; "
        "the guard must be len(names) >= slot, not > slot")
    assert out["name_at_slot"] is not None
    assert conn.sent, "save_to_user_slot sent nothing to the device"


def test_transmit_updates_constant_corrected_or_absent():
    """haken.CC_TRANSMIT_UPDATES is deleted, or else correct, header-cited and called."""
    if not hasattr(haken, "CC_TRANSMIT_UPDATES"):
        return  # deleted: ch16 cc55 is ccCreaArchFin, so the name was wrong for 10.81

    source = Path(haken.__file__).read_text(encoding="utf-8")
    definition = next(line for line in source.splitlines()
                      if line.startswith("CC_TRANSMIT_UPDATES"))
    assert "HakenMidi.h" in definition, (
        "CC_TRANSMIT_UPDATES is retained but its comment does not cite docs/HakenMidi.h; "
        "ch16 cc55 is ccCreaArchFin (docs/HakenMidi.h:815), so the old comment was wrong")
    callers = [line for line in source.splitlines()
               if "CC_TRANSMIT_UPDATES" in line and not line.startswith("CC_TRANSMIT_UPDATES")]
    assert callers, (
        "CC_TRANSMIT_UPDATES is retained with no caller; a constant that misnames a "
        "controller is not documentation (minimal-implementation.md:24-26)")


def test_matrix_col_11_separator():
    """F13. Column 11 is cSep, the column a modern preset selects to end its matrix block."""
    assert 11 in matrix_map.COLS, (
        "matrix_map.COLS has no entry for column 11; docs/HakenMidi.h:680 names it cSep and "
        "modern preset files select row 0 / column 11 to end the matrix block")
    assert "cSep" in matrix_map.COLS[11], (
        f"COLS[11] is {matrix_map.COLS[11]!r}; it must name the header's own cSep so a label "
        "quoted from this table can be traced back to docs/HakenMidi.h")
    assert matrix_map.col_name(11) == matrix_map.COLS[11]
    assert matrix_map.COLS[10] == "Dry R" and matrix_map.COLS[12].startswith("Osc/Filter 1"), (
        "COLS[11] must sit between Dry R and the first oscillator column, not replace one")


def test_warning_fields_join_with_separator(monkeypatch):
    """DC7. A negative height is written and doubted, and two doubts stay ONE warning key.

    `error-handling.md:31` returns doubt as data once the command has reached the device,
    and `conventions.md:59-65` keeps the envelope a flat dict of primitives - so two
    concurrent warnings join with " ; " into the single `warning` key rather than becoming
    a list or a second key. The write proceeds: a negative height is how a vowel wah is
    built, so refusing it would refuse a shipped recipe.
    """
    monkeypatch.setattr(server, "conn", _SilentConn())
    # Nothing is heard back, so formula_before is None: the "no formula letter" warning
    # applies. The negative heights add the second one.
    out = server.set_formula(5, 27, "X", height_begin=-0.2, height_end=-0.2)

    warning = out["warning"]
    assert isinstance(warning, str), (
        f"warning must be a primitive string, got {type(warning).__name__}; "
        "conventions.md:59-65 requires a flat dict of primitives")
    assert "warnings" not in out, "the two warnings must join, not add a second key"
    assert warning.count(" ; ") == 1, (
        f"both warnings apply, so exactly one ' ; ' join is expected, got {warning!r}")
    assert "cell held no formula before" in warning, (
        "joining must not drop the pre-existing 'cell held no formula before' warning")
    lowered = warning.lower()
    assert "negative" in lowered, "the negative-height doubt is not named"
    assert "Verify a NEGATIVE formula height on the device" in warning, (
        "the warning must name the open device test by its ROADMAP item text, not by line "
        "number: ROADMAP.md:57 used to be that item and is now a COMPLETED one, so a line "
        "citation here silently came to contradict the warning it supports. The header's sign "
        "semantics have never been confirmed on the Module for a negative value")
    assert "slots 4 and 5" in warning, (
        "the warning must say the codec fix does NOT repair the negative heights already "
        "saved in user slots 4 and 5 (H6)")

    # Control, in the same test so this file keeps A2.10's exact four: the negative-height
    # warning is conditional, so a positive write leaves the single pre-existing warning.
    positive = server.set_formula(5, 27, "X", height_begin=0.2, height_end=0.6)
    assert " ; " not in positive["warning"], (
        f"only one warning applies to a positive write, got {positive['warning']!r}")
    assert "negative" not in positive["warning"].lower()
    assert "cell held no formula before" in positive["warning"]
