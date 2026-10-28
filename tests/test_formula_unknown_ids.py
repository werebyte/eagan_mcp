"""Stream-19 ids the formula decoder does not know must be surfaced, not dropped.

codec-conventions.md: "unknown values decoded to a visible ?<n> marker rather than
raising or dropping". formula.decode used to be pull-only - it fetched every value by a
known id and never iterated the pairs it was given - so any id outside COMPONENTS plus the
*_ID constants was discarded silently, and a blend, an ancillary or a psDuplex formula read
back as an ordinary one with no indication that anything had been lost.

The ids this suite was written around - ancillary 7-11, 56, 57, 100, 101; blend 39, 68;
interpolation 48, 82; persistence 63, 81; reluctance 96, 97; wZone 118, 119; flags 124,
125 - are now DECODED (formula.DECODE_ONLY_IDS), so they are no longer available as
examples of an unreported id. Persistence (id 63) was the sharpest case, being the only
way to build an envelope release: it is now read, not reported. The property under test is
unchanged, so the examples moved to ids the header leaves unassigned in its s_Form_Poke
definitions - 47, 83 and 102, each a "(n)" placeholder in SSL_Form_Poke
(docs/HakenMidi.h:241-257). `formula.KNOWN_IDS` now equals the header's 79 ids exactly, so
an id outside it is one the firmware uses and this project has never seen; surfacing it is
the only way a caller learns that something was lost.

The stronger form of this property - that every one of the 79 ids either changes the
decoded result or is reported - is pinned by
tests/test_shared_tables.py::test_every_form_poke_id_is_known_or_declared_decode_only.

SCOPE OF THIS SUITE
-------------------
Header-derived decoder behaviour only, and **not** device verification: nothing here opens
a MIDI port, touches the Module or reads `HAKEN_EDITOR_DIR`, `docs/` or `captures/`. A green
run says the decoder reports what it did not understand; it says nothing about what the
firmware does with any of these ids, and it closes no `ROADMAP.md` device item.
"""

from eagan_mcp import formula


def test_decode_surfaces_an_unknown_id():
    """id 47 is unassigned in the header's own id list and must still be reported."""
    decoded = formula.decode({47: 40})
    assert "unknown_ids" in decoded, "decode silently dropped an id it does not know"
    assert decoded["unknown_ids"] == {47: 40}


def test_decode_surfaces_several_unknown_ids():
    """Three unassigned ids at once, from three different reserved runs."""
    decoded = formula.decode({47: 40, 83: 2, 102: 40})
    assert decoded.get("unknown_ids") == {47: 40, 83: 2, 102: 40}


def test_decode_warns_when_ids_were_not_understood():
    """Doubt is returned as data (error-handling.md), so a caller can see the gap."""
    decoded = formula.decode({47: 40})
    assert decoded.get("warning"), "no warning field when unknown ids were present"
    assert "47" in str(decoded["warning"])


def test_known_ids_are_not_reported_as_unknown():
    """Control: a fully understood formula reports no unknown ids and no warning."""
    # W mode = Gated (id 40), height 0.50 (sign id 13 clear, id 42 = 50), operator 0.
    decoded = formula.decode({40: 1, 13: 0, 42: 50, formula.OPERATOR_ID: 0})
    assert not decoded.get("unknown_ids")
    assert not decoded.get("warning")
