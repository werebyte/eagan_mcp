"""`formula.summary` must not report a working formula as empty.

WHAT THESE TESTS DO AND DO NOT ESTABLISH
----------------------------------------
Everything here is derived from `docs/HakenMidi.h`'s s_Form_Poke id definitions
(:1157-1352) and from the 49 `wiring` blocks of the shipped
`eagan_mcp/knowledge/factory_catalog.json`. Nothing reads `HAKEN_EDITOR_DIR` and nothing
touches the Module: this is **not** device verification. A green run says the renderer
reports what the decoder read, never what the firmware does with it.

THE DEFECT
----------
`summary()` rendered the four primary components W, X, Y and Z and nothing else, so a
formula carrying its content on the secondary (blend) sliders, on the ancillary
operations or on W's shaping ids summarised as "(all components zero)" while doing real
work. `summary()` is what `get_formula` returns, so that reading was handed to the caller
as the state of the cell.

19 of the 563 formula letters in the shipped wiring blocks are affected (3.4%), and
exactly one letter in the corpus - `Cowell Triangles` `H`, a cell naming a formula that
was never written - is genuinely all-default. The empty answer has to stay available for
that one, which is why the fall-through is a fall-through and not a rewrite.

H12 (`formula.py` imports nothing) is asserted by
`tests/test_shared_tables.py::test_codec_modules_still_import_nothing` and is not
duplicated here.
"""

import json
from pathlib import Path

import eagan_mcp
from eagan_mcp import formula

CATALOG = Path(eagan_mcp.__file__).parent / "knowledge" / "factory_catalog.json"

# The all-default formula, as the catalog's compression rule resolves it: `decode()` has no
# default argument to apply, so decoding the empty pair set IS the default formula.
DEFAULTS = formula.decode({})

# Ids used below, as the header spells them (docs/HakenMidi.h):
#   14 NegW2 / 73 HeightW2 (:1335)  the secondary W height, reached only under a blend
#   39 Blend (:1326-1328)           3 = psMacro, "crossfade to the secondary values by macro"
#   56 AncOp / 57 AncVal (:1275, :1292)  the first ancillary operation and its operand
# Neither pair touches a primary component, so each formula below is "all components zero"
# to the old renderer.
SECONDARY_UNDER_BLEND = {14: 0, 73: 50, 39: 3}
ANCILLARY_ONLY = {56: 6, 57: 5}

# Current wording, captured before the fix, for formulas that already rendered correctly.
# Pinned so the fall-through cannot quietly reword the 96.6% of letters that were fine.
UNCHANGED_SUMMARIES = {
    # W = Constant 0.3 x 10 under operator 1, from ids 13/42 (NegW/HeightW), 41 (MultW), 38.
    (13, 0, 42, 30, 41, 4, 38, 1): "[W x (X + Y + Z)] W = Constant 0.3 x 10",
    # W = SG1 at full height, sine shape, quarter-phase, scaled by macro i.
    (40, 2, 42, 100, 66, 1, 67, 0, 50, 11, 117, 1):
        "[W + X + Y + Z] W = SG1 1.0 x 1 [shape Sine, phase 0.25] x Macro (i)",
    # X and Y heights only; Y begins at exactly 0.0, which must still read as active.
    (15, 1, 45, 88, 17, 0, 46, 12, 1, 5, 4, 0, 85, 0, 19, 0, 51, 0, 21, 0, 52, 50):
        "[W + X + Y + Z] X = Continuous -0.12->0.12 x 100 ; Y = Continuous 0.0->0.5 x 1",
}

EMPTY = "(all components zero)"


def _pairs(flat: tuple) -> dict[int, int]:
    return dict(zip(flat[::2], flat[1::2]))


def _merge(default: dict, chosen: dict) -> dict:
    """Put a pruned catalog record back over the default formula it was pruned against."""
    out = dict(default)
    for key, value in chosen.items():
        out[key] = _merge(default[key], value) if isinstance(value, dict) else value
    return out


def _expand(record: dict) -> dict:
    """One `wiring` letter record, expanded to what `formula.decode` produced for it.

    `preset_file._wiring_formula` writes each section as the difference from the
    all-default formula and drops `active`, which is a function of the heights. Round-trip
    is exact: `test_every_wiring_letter_round_trips_through_the_renderer` re-renders all
    563 letters and compares against the summary the catalog shipped.
    """
    out = {name: _merge(DEFAULTS[name], record[name]) if name in record else dict(DEFAULTS[name])
           for name in ("W", "X", "Y", "Z", "w_zone", "ancillary", "blend", "secondary",
                        "shaping")}
    out["operator"] = record["operator"]
    out["unknown_ids"] = record.get("unknown_ids", {})
    out["W"]["active"] = out["W"]["value"] not in (None, 0)
    for name in "XYZ":
        out[name]["active"] = bool(out[name]["height_begin"]) or bool(out[name]["height_end"])
    return out


def _wiring_letters() -> list[tuple[str, str, dict]]:
    presets = json.loads(CATALOG.read_text(encoding="utf-8"))["presets"]
    return [(preset["name"], letter, record)
            for preset in presets if "wiring" in preset
            for letter, record in preset["wiring"]["letters"].items()]


def test_secondary_slider_under_a_blend_is_not_summarised_as_empty():
    """`Shimmer Wbl` I and 15 more: the whole value sits on HeightW2 under a macro blend."""
    decoded = formula.decode(SECONDARY_UNDER_BLEND)
    assert decoded["secondary"]["W"]["value"] == 0.5
    assert decoded["blend"]["control"] == "macro"

    rendered = formula.summary(decoded)
    assert EMPTY not in rendered, (
        f"a formula crossfading to a secondary W height of 0.5 rendered as {rendered!r}; "
        "get_formula hands that string to the caller as the state of the cell")
    assert "0.5" in rendered and "macro" in rendered, (
        f"{rendered!r} says the formula is not empty but not what it sets")


def test_ancillary_operation_is_not_summarised_as_empty():
    """`The Long Goodbye` P: AncOp/AncVal on a W whose primary slider is zero."""
    decoded = formula.decode(ANCILLARY_ONLY)
    assert decoded["ancillary"]["op"] == "^" and decoded["ancillary"]["value"] == "2.0"

    rendered = formula.summary(decoded)
    assert EMPTY not in rendered, f"an ancillary ^2.0 rendered as {rendered!r}"
    assert "^" in rendered and "2.0" in rendered, (
        f"{rendered!r} does not name the ancillary operation it reports as set")


def test_a_genuinely_empty_formula_still_summarises_as_all_components_zero():
    """`Cowell Triangles` H is a real cell naming a formula nobody ever wrote."""
    assert formula.summary(DEFAULTS) == f"[W + X + Y + Z] {EMPTY}"


def test_formulas_with_primary_content_summarise_exactly_as_before():
    """The 96.6% that were already right must not be reworded by the fall-through."""
    for flat, expected in UNCHANGED_SUMMARIES.items():
        assert formula.summary(formula.decode(_pairs(flat))) == expected


def test_every_wiring_letter_round_trips_through_the_renderer():
    """The corpus check's own premise: `_expand` reproduces the decoded formula exactly.

    Every letter whose catalog summary is NOT the empty one must re-render to that exact
    string. If this fails, the counts in the next test are measuring the expansion, not
    the renderer.
    """
    for name, letter, record in _wiring_letters():
        if EMPTY in record["summary"]:
            continue
        assert formula.summary(_expand(record)) == record["summary"], (
            f"{name} {letter}: re-rendering the catalog record does not reproduce the "
            "summary the catalog shipped")


def test_only_the_one_all_default_letter_still_renders_as_empty():
    """19 of 563 letters before the fix, 1 after - and that one is genuinely all-default."""
    letters = _wiring_letters()
    assert len(letters) == 563

    # The catalog's summaries were baked by whichever renderer built it. It was built before
    # this fix and rebuilding it needs HAKEN_EDITOR_DIR, so 19 of the baked strings are still
    # the old reading; a rebuild makes that 1. Either is acceptable - the property under test
    # is what the CURRENT renderer produces, below.
    baked_empty = {f"{name} {letter}" for name, letter, record in letters
                   if EMPTY in record["summary"]}
    assert len(baked_empty) in (19, 1), (
        f"{len(baked_empty)} letters ship an empty summary; expected 19 (catalog baked "
        "before the fix) or 1 (rebuilt after it)")

    after = {f"{name} {letter}" for name, letter, record in letters
             if EMPTY in formula.summary(_expand(record))}
    assert after == {"Cowell Triangles H"}, (
        f"re-rendered, {sorted(after)} still read as empty; only `Cowell Triangles H` is "
        "all-default and may")
