"""A tool docstring is the prompt the agent reads, so it is testable surface.

`commenting.md:9-16`: a tool docstring must state the write scope in its first lines, the
units, ranges and exact enum strings, and the safety warnings - length is explicitly not a
concern. Four docstrings currently fail that bar in ways that cost device safety:

  `send_raw`     names ch16 cc109=8 and cc57/cc58 as the store commands. cc57 is
                 ccAnlysSlot (docs/HakenMidi.h:809) and cc58 is undefined in 10.81
                 (docs/HakenMidi.h:214) - neither stores anything. The two controllers
                 that do are ch16 cc112 (ccStore, docs/HakenMidi.h:475) and ch16 cc0=127
                 (catSSlot, the system-slot path). `send_raw` is the only tool that can
                 reach cc112 and it has no code guard, so this docstring is the entire
                 defence.

  `load_preset`  performs the same three-message write as `load_and_capture_preset`, which
                 warns at server.py:100 that unsaved edits are lost. `load_preset` carries
                 no such warning, and no note that the preset index may be off by one
                 (`protocol-sources.md:43-49`).

  `set_formula`  misleads in four ways at once: it promises X/Y/Z heights up to 1.27 when
                 `encode_changes`' `slider()` passes 1.0 as their max; it labels `idScaleW`
                 values 3 and 6 "x Fingers scaler" / "x Polyphony scaler" when the header
                 names them `wDivFings = 1/fingersDown` and `wDivPoly = 1/thisDSPpoly`
                 (docs/HakenMidi.h:1212-1220) - reciprocals, so the W value FALLS as
                 fingers land; it advertises 4 of 48 `sg_phase` values; and it says nothing
                 about the RMS W mode or the 45 sample-and-hold shapes, which the codec
                 accepts. The accepted enum strings are NOT renamed - they are a shipped
                 tool's interface - so the semantics live in the prose.

  `set_polyphony` caps at 8 (docs/HakenMidi.h:1357 `idPoly`, "values 1..8") while 24 of the
                 668 factory presets store 10, 12 or 14 and the same header names
                 `maxNonMpePoly = 14` at :1360. The cap stays: this tool writes to the
                 device, and a header bound outranks a corpus statistic. The refusal has to
                 carry the evidence instead, so the next device session knows what to try.

SCOPE OF THIS SUITE
-------------------
Like every test file here, this suite pins the codec and the tool surface to
corpus-derived semantics. It is NOT device verification: nothing here touches the Module,
and a green run says nothing about what the firmware does. The negative-height device
test stays open.

The write-scope opening is asserted on six tools only, not on all 30: 21 of the 30 fail it
today against a deliberately generous vocabulary, and only four docstrings are in scope for
repair in this pass (A2.3). The accepted opening tokens are pinned as a literal list below.
"""

import pytest

from eagan_mcp import server


def test_send_raw_docstring_names_the_real_store_controllers():
    """The two flash paths must be named; the two false positives must be gone."""
    doc = server.send_raw.__doc__
    assert doc, "send_raw has no docstring"
    assert "112" in doc, "send_raw's docstring does not name ch16 cc112 (ccStore)"
    assert "cc0=127" in doc, "send_raw's docstring does not name the system-slot path cc0=127"
    assert "cc109=8" in doc, "send_raw's docstring dropped cc109=8 (global settings to flash)"
    assert "cc57" not in doc, "send_raw's docstring still names cc57 (ccAnlysSlot stores nothing)"
    assert "cc58" not in doc, "send_raw's docstring still names cc58 (undefined in 10.81)"


def test_load_preset_docstring_warns_about_the_edit_slot():
    """The warning belongs in the first lines (commenting.md:12), with the index caveat."""
    doc = server.load_preset.__doc__
    assert doc, "load_preset has no docstring"
    opening = " ".join(doc.splitlines()[:2]).lower()
    assert "edit slot" in opening, (
        "load_preset's first two lines do not warn that loading destroys the edit slot")
    lowered = doc.lower()
    assert "category_index" in doc, (
        "load_preset's docstring must point at the catalog field that carries the index, "
        "since guessing it is the documented failure mode")
    assert "off by one" in lowered, (
        "load_preset's docstring does not carry the off-by-one index note "
        "(protocol-sources.md:43-49)")
    # NOT load_and_capture_preset any more. On fw 10.81 it returns name "preset" and no
    # streams at all (device-observed 2026-10-27), so telling an agent to confirm an index with
    # it sends it to a tool that cannot answer. What works is list_user_presets' LAST entry,
    # which is the edit slot's name. The docstring must name a route that actually functions.
    assert "list_user_presets" in doc, (
        "load_preset's docstring must name a WORKING way to confirm which preset loaded. "
        "load_and_capture_preset is not it on fw 10.81: it returns the literal name 'preset' "
        "and no streams")
    assert "load_and_capture_preset" not in doc, (
        "load_preset's docstring still recommends load_and_capture_preset for confirming an "
        "index; that tool returns no usable name on fw 10.81")


# A2.3's accepted opening tokens, pinned as a literal list so the write-scope assertion is
# machine-checkable rather than a judgement call. Compared case-insensitively against the
# first two lines of the docstring (`commenting.md:12`).
WRITE_SCOPE_TOKENS = (
    "read-only",
    "edit slot only",
    "edit slot",
    "not stored to flash",
    "unguarded",
    "writes the preset to flash",
    "writes flash",
)

# The six tools in scope (A2.3). All six exist now - `search_factory_presets` and
# `get_knowledge` were the two built later in this pass - so the assertion is unconditional.
# The other ~24 tools are deliberately OUT of scope: 21 of 30 fail this bar today and only
# four docstrings were in scope for repair in this pass.
WRITE_SCOPE_TOOLS = ("send_raw", "set_formula", "load_preset", "set_polyphony",
                     "get_knowledge", "search_factory_presets")

# The two read-only knowledge tools answer from data committed inside the package. Their
# write scope is not merely absent, it is a promise the caller relies on, so the generous
# vocabulary above is not enough for them: both must open with `Read-only.` literally.
READ_ONLY_TOOLS = ("get_knowledge", "search_factory_presets")


@pytest.mark.parametrize("tool_name", WRITE_SCOPE_TOOLS)
def test_scoped_tool_opens_with_a_write_scope_token(tool_name):
    """The write scope must appear in the first two lines, in one of the pinned forms."""
    doc = getattr(server, tool_name).__doc__
    assert doc, f"{tool_name} has no docstring"
    opening = " ".join(doc.splitlines()[:2]).lower()
    assert any(token in opening for token in WRITE_SCOPE_TOKENS), (
        f"{tool_name}'s first two lines state no write scope; commenting.md:12 requires one of "
        f"{list(WRITE_SCOPE_TOKENS)}, got {opening!r}")


@pytest.mark.parametrize("tool_name", READ_ONLY_TOOLS)
def test_knowledge_tools_docstrings_open_with_read_only(tool_name):
    """`commenting.md:12`: "Read-only." is the exact opening these two owe the caller."""
    doc = getattr(server, tool_name).__doc__
    assert doc, f"{tool_name} has no docstring"
    assert doc.lstrip().startswith("Read-only."), (
        f"{tool_name}'s docstring must open with the literal 'Read-only.'; the agent decides "
        f"whether a call is safe from the first line, got {doc.splitlines()[0]!r}")


def _set_formula_segments() -> tuple[str, str]:
    """set_formula's docstring, split into its W half and its X/Y/Z half."""
    doc = server.set_formula.__doc__
    assert doc, "set_formula has no docstring"
    marker = 'component "X"/"Y"/"Z"'
    assert marker in doc, (
        f"set_formula's docstring no longer carries the {marker!r} section marker, so the "
        "per-component range assertions below cannot be scoped")
    cut = doc.index(marker)
    return doc[:cut], doc[cut:]


def test_set_formula_docstring_states_reciprocal_modifiers_and_all_48_phases():
    """F8 a-d: the height ranges, the reciprocals, every sg_phase, and the widened enums."""
    w_part, xyz_part = _set_formula_segments()

    # (a) the height range. X/Y/Z cap at 1.00 - encode_changes' slider() already passes 1.0
    # as the max for them, so a docstring promising 1.27 contradicts the code.
    assert "-1..1.27" in w_part, (
        "set_formula's W section does not state value (-1..1.27); W is the one component "
        "that reaches 1.27 (docs/HakenMidi.h:1202)")
    assert "1.27" not in xyz_part, (
        "set_formula's X/Y/Z section still mentions 1.27; those heights cap at 1.00 and "
        "encode_changes' slider() passes 1.0 as their max")
    assert "-1..1" in xyz_part, (
        "set_formula's X/Y/Z section does not state the -1..1 height range")

    # (b) the two reciprocal modifiers, under the header's own names.
    assert "1/fingersDown" in w_part, (
        '"x Fingers scaler" is wDivFings = 1/fingersDown (docs/HakenMidi.h:1212-1220); the '
        "docstring must say so, because the W value FALLS as fingers land")
    assert any(name in w_part for name in ("1/thisDSPpoly", "1/dspPoly")), (
        '"x Polyphony scaler" is wDivPoly = 1/thisDSPpoly (docs/HakenMidi.h:1212-1220); the '
        "docstring must name the reciprocal")
    lowered = w_part.lower()
    assert "reciprocal" in lowered, (
        "the docstring names the header's reciprocals but does not say they are reciprocals")
    # H3: the accepted enum strings are unchanged, misleading or not.
    for enum_string in ('"x Fingers scaler"', '"x Polyphony scaler"'):
        assert enum_string in w_part, (
            f"{enum_string} is a shipped tool's accepted enum value and must stay advertised "
            "verbatim; only the semantics move into prose")

    # (c) all 48 sg_phase values, as the generative rule with both endpoints.
    for phase in ('"Off"', '"0.25"', '"0.5"', '"0.75"', '"mod A"', '"mod V"', "mod V'"):
        assert phase in w_part, (
            f"set_formula's docstring does not expose sg_phase {phase}; 4 of 48 values were "
            "advertised, hiding the 44 phase-modulation options")
    # The knob-lag construction table moved out of RECIPES.md into the knowledge base, so the
    # citation moved with it (`conventions.md:15`: a stale citation is a correctness risk, not
    # a cosmetic one). It is cited by section and item, not by line, because line numbers in a
    # 600-line document drift on every edit.
    assert 'get_knowledge("pitfalls")' in w_part, (
        "the docstring does not cite the knob-lag-free construction's new home; it is why one "
        "SG plus sg_phase is the quadrature route rather than several SGs")
    assert "item 42" in w_part, (
        "the citation does not name pitfalls item 42, the tested construction table itself")
    assert "RECIPES.md:18-19" not in w_part, (
        "RECIPES.md:18-19 is now 'Pitch follows the keyboard'; the knob-lag table moved to "
        "eagan_mcp/knowledge/pitfalls.md and the stale line citation must be gone")

    # (d) the modes and shapes F11/F12 made reachable.
    assert "RMS of row" in w_part, (
        "W mode 13 (wRMS) is accepted by encode_changes now; the docstring must advertise it")
    assert "RMS row" in w_part, (
        "the docstring must carry the real constraint: only one formula can appear in a "
        "matrix RMS row in W")
    assert "S+H" in w_part, (
        "sg_shape accepts the 45 sample-and-hold values now; the docstring must advertise them")
    for shape in ('"S+H row"', '"S+H A"', "S+H V'"):
        assert shape in w_part, (
            f"set_formula's docstring does not expose sg_shape {shape}")


def test_set_polyphony_docstring_and_valueerror_name_the_header_bound():
    """DC2. The ceiling stays 8, and both the docstring and the refusal say why."""
    doc = server.set_polyphony.__doc__
    assert doc, "set_polyphony has no docstring"
    evidence = ("maxNonMpePoly", "14", "24 factory presets", "TEST-POLY-14")
    for token in evidence:
        assert token in doc, (
            f"set_polyphony's docstring does not name {token!r}; the conflict between the "
            "header's 1..8 bound and the corpus must be visible to the caller")
    assert "1..8" in doc, "set_polyphony's docstring no longer states the 1..8 range"

    # The ceiling is unchanged: this tool writes to the device against an explicit header
    # bound (docs/HakenMidi.h:1357), and [G] header outranks [C] corpus.
    for refused in (0, 9, 10, 14):
        with pytest.raises(ValueError) as excinfo:
            server.set_polyphony(refused)
        message = str(excinfo.value)
        assert "1..8" in message, (
            f"set_polyphony({refused}) must interpolate the allowed range into its refusal "
            f"(validation.md:19), got {message!r}")
        for token in evidence:
            assert token in message, (
                f"set_polyphony({refused})'s refusal does not name {token!r}; the next device "
                "session has to be told what to try")
