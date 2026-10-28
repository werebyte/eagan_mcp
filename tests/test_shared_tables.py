"""The I2 refactor: one wire table per stream, shared by the live codec and the file decoder.

`eagan_mcp/preset_file.py` was ported from the research tree's `preset_decode.py` +
`build_catalog.py`. Ported as-is it would have been a SECOND decoder for stream 19
(`s_Form_Poke`) and stream 20 (`s_Mat_Poke`), against `codec-conventions.md:24-31`'s
one-entry-point-per-stream rule. That is not a tidiness point: the two copies had already
drifted apart on what the device *means*. Both carried the mirrored negative height, and the
research copy's workaround for it (a local `height_offset()` helper and an "idTransX default
is kHz" comment, in a script that is deliberately not ported) existed only because the shared
codec was wrong. Two copies of a codec that disagree are drift in evidence, so the tests here
pin the single-table property rather than any particular value.

SCOPE OF THIS SUITE
-------------------
Corpus-derived and header-derived semantics only. Nothing here touches the Module, and a
green run says nothing about what the firmware does. The height, transfer-function and
sample-and-hold readings pinned below come from `docs/HakenMidi.h` (fw 10.81) and from the
668 factory presets shipped with Haken Editor 1081; the device tests they still want are
listed in `ROADMAP.md`.
"""

import ast
from pathlib import Path

from eagan_mcp import formula, preset_file, setup

CODEC_MODULES = (formula, setup)


def _module_source(module) -> str:
    return Path(module.__file__).read_text(encoding="utf-8")


def _module_level_literals(module) -> list[tuple[str, object]]:
    """Every module-level assignment in `module` whose value is a plain literal."""
    tree = ast.parse(_module_source(module))
    out: list[tuple[str, object]] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if not names:
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError, SyntaxError):
            continue            # built by a loop or a comprehension, not a literal table
        for name in names:
            out.append((name, value))
    return out


def _wire_value_tables() -> dict[str, object]:
    """The stream-19/20 value tables, collected from the codec modules themselves.

    A value table is wire value -> name: a list when the device's values are a contiguous
    0-based enumeration, a dict keyed by the wire value when they are sparse
    (`codec-conventions.md:6-15`). Collected by shape rather than by a hardcoded name list,
    so a table added to `formula.py` or `setup.py` later is covered without editing this test.
    """
    tables: dict[str, object] = {}
    for module in CODEC_MODULES:
        for name, value in vars(module).items():
            if name.startswith("_") or not name.isupper():
                continue
            if isinstance(value, (list, tuple)) and value and all(
                    isinstance(v, str) for v in value):
                tables[f"{module.__name__}.{name}"] = list(value)
            elif isinstance(value, dict) and value and all(
                    isinstance(k, int) and isinstance(v, str) for k, v in value.items()):
                tables[f"{module.__name__}.{name}"] = dict(value)
    return tables


def test_preset_file_declares_no_stream_19_or_20_value_table():
    """D5.1's acceptance criterion, as a property of the source rather than of a name list.

    A reproduction of a wire table is a literal that carries the same wire->name mapping:
    a list whose elements repeat the shared list's order, or a dict that repeats its
    wire-value keys. Three matching entries is the threshold - fewer can be a coincidence
    of vocabulary (a module name used as a dictionary key is not a copy of the type table).
    """
    shared = _wire_value_tables()
    assert shared, "no wire value tables found in formula.py / setup.py - the collector broke"
    offences = []
    for name, value in _module_level_literals(preset_file):
        for table_name, table in shared.items():
            if isinstance(table, list) and isinstance(value, (list, tuple)):
                strings = [v for v in value if isinstance(v, str)]
                overlap = sum(1 for i, v in enumerate(strings)
                              if i < len(table) and v == table[i])
                if overlap >= 3:
                    offences.append(f"{name} repeats the order of {table_name} "
                                    f"({overlap} entries)")
            elif isinstance(table, dict) and isinstance(value, dict):
                overlap = sum(1 for k, v in value.items() if table.get(k) == v)
                if overlap >= 3:
                    offences.append(f"{name} repeats {overlap} wire mappings of {table_name}")
    assert not offences, (
        "preset_file.py declares its own stream-19/20 value table(s): "
        + "; ".join(offences)
        + ". codec-conventions.md:24-31 allows one entry point per wire stream; import the "
          "table from formula.py / setup.py instead of restating it")


def test_sg_shapes_has_57_entries():
    """F11. The header names idShapeW 0..56; 12..56 are the sample-and-hold sources."""
    assert len(formula.SG_SHAPES) == 57, (
        f"SG_SHAPES has {len(formula.SG_SHAPES)} entries; docs/HakenMidi.h:1179-1198 defines "
        "wRampUp..wSampHoldV_ = 0..56")
    assert formula.SG_SHAPES[11] == "Sine"
    assert formula.SG_SHAPES[12] == "S+H row"
    assert formula.SG_SHAPES[13] == "S+H A"
    assert formula.SG_SHAPES[34] == "S+H V"
    assert formula.SG_SHAPES[35] == "S+H A'"
    assert formula.SG_SHAPES[56] == "S+H V'"
    assert "S+H option" not in _module_source(formula), (
        "the f\"S+H option {n}\" fallback is still in formula.py; with all 57 shapes named "
        "it is unreachable, and minimal-implementation.md forbids dead code")
    decoded = formula.decode({formula.SG_SHAPE_ID: 18})
    assert decoded["W"]["sg_shape"] == "S+H F", (
        "a sample-and-hold shape must decode to its name, not to a numbered placeholder")


def test_w_modes_has_14_entries_and_rms_of_row_is_writable():
    """F12. 34 factory formulas use the RMS W mode, so refusing to write it is wrong."""
    assert len(formula.W_MODES) == 14, (
        f"W_MODES has {len(formula.W_MODES)} entries; docs/HakenMidi.h:1164-1178 defines "
        "wSgConstant..wRMS = 0..13")
    assert formula.W_MODES[13] == "RMS of row"
    assert formula.encode_changes("W", mode="RMS of row") == [(formula.COMPONENTS["W"]["mode"], 13)]
    assert formula.encode_changes("W", mode=13) == [(formula.COMPONENTS["W"]["mode"], 13)]
    assert "not verified yet" not in _module_source(formula), (
        "encode_changes still refuses the RMS W mode; the real constraint is that only one "
        "formula may sit in a matrix RMS row in W, and it belongs in the docstring")


def test_transfer_default_is_defined_once_in_formula():
    """F5's single site. 334 factory formulas read "Octaves" for kHz under the old default."""
    assert formula.TRANSFER_DEFAULT == {"X": 1, "Y": 0, "Z": 0}, (
        "TRANSFER_DEFAULT must be the per-component default transfer WIRE VALUE, not a "
        "reordering of X_TRANSFER: the list index has to stay equal to the wire value")
    assert formula.X_TRANSFER[formula.TRANSFER_DEFAULT["X"]] == "X kHz"
    assert formula.YZ_TRANSFER[formula.TRANSFER_DEFAULT["Y"]] == "Linear"
    redefined = [name for name, _v in _module_level_literals(preset_file)
                 if name == "TRANSFER_DEFAULT"]
    assert not redefined, (
        "preset_file.py redefines TRANSFER_DEFAULT; F5 exists because the default was wrong "
        "in two places at once, so there must be exactly one site")
    # Behavioural half: the file decoder must INHERIT the default rather than hold its own.
    # This replaces an earlier `"formula.TRANSFER_DEFAULT" in source` text check, which could
    # not discriminate - it passed both before and after F5 was wired into formula.decode, and
    # once the interim patch was removed it was satisfied only by a docstring phrase, so a
    # reworded paragraph would have turned it red for no defect. The structural property
    # ("exactly one definition site") is pinned by
    # tests/test_formula_transfer_default.py::test_transfer_default_has_exactly_one_definition_site,
    # which is AST-based and was shown to fail when a second site is restored.
    for component in "XYZ":
        from_live = formula.decode({})[component]["transfer"]
        from_file = preset_file.decode_formula({})[component]["transfer"]
        assert from_live == from_file, (
            f"{component} transfer default disagrees between the live decoder ({from_live!r}) "
            f"and the file decoder ({from_file!r}); F5 exists because it was wrong in two "
            "places at once")


def test_every_form_poke_id_is_known_or_declared_decode_only():
    """F4's harm, closed over the whole header id space rather than over one example.

    `KNOWN_IDS` is derived from the tables, so an id can become "known" - and therefore be
    kept out of `unknown_ids` - without `decode` surfacing its value anywhere. A formula
    using such an id then reads back silently incomplete, which is exactly what F4 exists to
    prevent. Every one of the 79 ids the header defines must therefore either change the
    decoded result or be reported, and `DECODE_ONLY_IDS` records the ids that are read but
    deliberately not writable this pass.
    """
    assert len(formula.FORM_POKE_NAMES) == 79, (
        f"FORM_POKE_NAMES has {len(formula.FORM_POKE_NAMES)} entries; the s_Form_Poke "
        "definitions at docs/HakenMidi.h:1157-1352 name 79 ids")
    assert formula.KNOWN_IDS <= set(formula.FORM_POKE_NAMES), (
        "KNOWN_IDS contains ids the header does not define: "
        f"{sorted(formula.KNOWN_IDS - set(formula.FORM_POKE_NAMES))}")
    assert formula.DECODE_ONLY_IDS <= formula.KNOWN_IDS, (
        "DECODE_ONLY_IDS lists ids that decode() does not account for: "
        f"{sorted(formula.DECODE_ONLY_IDS - formula.KNOWN_IDS)}")

    baseline = formula.decode({})
    invisible = []
    for wire_id in sorted(formula.FORM_POKE_NAMES):
        if wire_id not in formula.KNOWN_IDS:
            reported = formula.decode({wire_id: 1})["unknown_ids"]
            if wire_id not in reported:
                invisible.append(wire_id)
            continue
        if not any(formula.decode({wire_id: v}) != baseline for v in (1, 2, 5)):
            invisible.append(wire_id)
    assert not invisible, (
        "these s_Form_Poke ids are treated as known but their values never reach the decoded "
        f"result: {[(i, formula.FORM_POKE_NAMES[i]) for i in invisible]}. Surface them, or "
        "report them in unknown_ids (codec-conventions.md:14-15: never raise, never drop)")

    secondary_sliders = {75, 76, 77, 78, 79, 80}
    assert secondary_sliders <= formula.KNOWN_IDS
    decoded = formula.decode({75: 30, 15: 0})
    assert decoded["secondary"]["X"]["height_begin"] == 0.3, (
        "the six secondary (blend) sliders 75-80 are in SLIDER_SIGN, so KNOWN_IDS counts them "
        "as known; decode() must therefore surface them")


def test_codec_modules_still_import_nothing():
    """H12. The three wire-table modules stay importable from anywhere, including a doc build."""
    from eagan_mcp import matrix_map
    for module in (formula, setup, matrix_map):
        tree = ast.parse(_module_source(module))
        imports = [node for node in ast.walk(tree)
                   if isinstance(node, (ast.Import, ast.ImportFrom))]
        assert not imports, (
            f"{module.__name__} imports "
            f"{[ast.unparse(node) for node in imports]}; the wire-table modules must stay "
            "dependency-free (H12). preset_file.py is the consumer and may import them")
