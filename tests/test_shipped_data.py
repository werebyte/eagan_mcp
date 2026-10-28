"""The shipped JSON data artifacts under `eagan_mcp/knowledge/`.

SCOPE OF THIS SUITE
-------------------
This file owns **every** assertion about the shipped JSON. `tests/test_factory_search.py`
owns every assertion about `search_factory_presets`. The split is deliberate: a defect in
the data must surface here as a data failure, not there as a tool failure.

Nothing here reads `HAKEN_EDITOR_DIR` and nothing here touches the Module. The build does
both; the shipped files are the build's output and must stand on their own on a fresh clone
and on a phone, which is the whole reason they are committed.

WHAT THESE NUMBERS ARE
----------------------
Corpus statistics over the 668 factory presets shipped with Haken Editor 1081, and the
offline consequences of `docs/HakenMidi.h`'s compression rule (`:478-480`). A green run
says nothing about what the firmware does. In particular the preset index's two candidate
collations are **not** discriminated by anything offline - see
`test_preset_index_ships_both_collations_and_13_populated_categories`.
"""

import json
import re
from pathlib import Path

import eagan_mcp
from eagan_mcp import preset_file

KNOWLEDGE_DIR = Path(eagan_mcp.__file__).parent / "knowledge"

# Measured from the rebuilt census, NOT taken from the specification, which carries
# 13/37/51. Two of the three reproduce; `techniques` is 52, because the corrected codec
# makes the `formula_delay_buffer` check fire for the first time (8 presets) and it is a
# 52nd tag. The module space is 37 and contains both `HarMan` and `HarMan (alias of B)`,
# `Low Pass Filter`, and `Pitch Shifter using Delay` for wire value 17 - `setup.py`'s
# spelling, which is what `set_osc_type` accepts. It does NOT contain `Recirculator` or
# `Convolution`: neither is a bank or oscillator type, so a filter for them reads a
# different census key.
#
# These are the acceptance target for D9.3 and for `search_factory_presets`' docstring: a
# docstring that names a count the data cannot produce is a prompt defect, not a typo.
ALLOWLIST_SIZES = {
    "category_main": 13,
    "modules_used_including_defaults": 37,
    "techniques": 52,
}

# `census.double_computation_rate.explicit_true`. The 16 that circulated earlier is the
# base-polyphony-2 bucket of these 41 ({1:4, 2:16, 3:11, 4:6, 5:1, 8:1, absent:2}) read as
# though it were the total.
DCR_EXPLICIT_TRUE = 41

# 661 of 668 presets have a long-form description `.txt`; 7 have none.
PRESETS_WITH_A_DESCRIPTION = 661


def _load(name: str) -> dict:
    path = KNOWLEDGE_DIR / name
    assert path.is_file(), (
        f"{path} is missing. The three auxiliary artifacts are committed, not regenerated "
        "at install time; rebuild with "
        "`.venv/Scripts/python.exe -m eagan_mcp.preset_file eagan_mcp/knowledge`")
    return json.loads(path.read_text(encoding="utf-8"))


def test_preset_index_ships_both_collations_and_13_populated_categories():
    """D6. Both candidate orderings ship, because neither is confirmed on the device.

    The two collations - by on-disk filename and by displayed preset name - diverge in 10
    of the 13 populated categories, and all four device observations on record fall on
    positions where they agree. So the corpus cannot choose, the file must say so, and
    `protocol-sources.md:43-49` stands: confirm an index by capture with
    `load_and_capture_preset`, never by the printed list.
    """
    index = _load("preset_index_1081.json")

    assert len(index["menu_order"]) == 14, (
        "menu_order is the Module's 14-slot local category menu "
        "(docs/HakenMidi.h:408 SSL_MainCat_Cont_E2x)")
    for key in ("by_filename_collation", "by_name_collation"):
        assert key in index, f"both collations must ship; {key} is missing"
        assert len(index[key]) == 13, (
            f"{key} has {len(index[key])} categories; 13 of the 14 menu slots are populated")
        assert "UP" not in index[key], (
            "UP is a menu slot with zero presets, so it is in menu_order and in neither "
            "collation. A consumer that treats the collation keys as the menu inverts this")
    assert "UP" in index["menu_order"]
    assert index["menu_slots_with_no_presets"] == ["UP"]

    # Every preset appears exactly once, at a contiguous 0-based index, in both collations,
    # and the two collations are permutations of the same set - they differ in ORDER only.
    sets = {}
    for key in ("by_filename_collation", "by_name_collation"):
        names = []
        for tag, record in index[key].items():
            presets = record["presets"]
            assert record["count"] == len(presets)
            assert sorted(int(i) for i in presets) == list(range(record["count"])), (
                f"{key}[{tag}] indices are not contiguous and 0-based")
            names.extend(presets.values())
        assert len(names) == len(set(names)), (
            f"{key} carries {len(names)} names but only {len(set(names))} distinct; a "
            "preset may occupy one index in one category")
        sets[key] = set(names)
    assert sets["by_filename_collation"] == sets["by_name_collation"], (
        "the two collations must order the same presets, not different ones")

    # The header, not a comment somewhere else, has to carry the ANSWER now. The collation was
    # device-verified on 2026-10-28: three presets in three categories loaded by the index
    # by_filename_collation predicts, and a 17-position scan of PT matched entry for entry.
    # The divergence figures stay in the note as history - they are why it was open so long.
    assert index["collation_status"].startswith("resolved: by_filename_collation"), (
        f"the header must state which collation the device uses; it reads "
        f"{index['collation_status']!r}")
    note = index["collation_note"]
    assert "RESOLVED" in note and "device" in note.lower(), (
        f"the header must say how it was settled. It reads: {note!r}")
    assert "10 of 13" in note and "130" in note, (
        "the header must keep the measured divergence as history: 10 of 13 populated "
        f"categories, 130 positions in all. It reads: {note!r}")
    assert len(index["collation_divergence"]) == 10, (
        f"{len(index['collation_divergence'])} categories diverge; 10 was measured")
    assert sum(entry["positions"] for entry in index["collation_divergence"].values()) == 130

    # The four device observations on record pass under BOTH orderings, which is precisely
    # why they do not discriminate.
    assert len(index["regression_checks"]) == 4
    for check in index["regression_checks"]:
        assert check["pass"], f"device regression check failed: {check}"
        assert (check["filename_collation_index"] == check["name_collation_index"]
                == check["device_index"])


def test_census_double_computation_rate_explicit_true_is_41():
    """The corrected count. 41 presets set Double Computation Rate, not 16.

    Double rate is the first thing to turn off when a preset runs out of DSP
    (`RECIPES.md`, user slot 3: 6 base voices became 3 with DCR on), so the frequency with
    which Haken itself uses it is load-bearing for the pitfalls document.
    """
    census = _load("census.json")
    dcr = census["double_computation_rate"]
    assert dcr["explicit_true"] == DCR_EXPLICIT_TRUE, (
        f"census reports {dcr['explicit_true']} presets with Double Computation Rate set; "
        f"{DCR_EXPLICIT_TRUE} was measured over the 668 factory presets. The 16 that "
        "circulated earlier is the base-polyphony-2 bucket of these 41, not the total")
    assert dcr["explicit_true"] + dcr["absent_so_default"] == census["presets"] == 668, (
        "every preset either sets the id or inherits the default; the two must partition "
        "the corpus (docs/HakenMidi.h:478-480)")


def test_descriptions_entry_count_matches_presets_with_a_description():
    """A2.1. 661 entries, and the 7 presets with no description are OMITTED.

    An empty string would be indistinguishable from a description that failed to decode,
    and it would make `text=` searches match a preset that has nothing to match on.
    `has_long_description` in the catalog stays the authoritative flag; this file is the
    text, and absence here means absence there.
    """
    descriptions = _load("descriptions.json")
    census = _load("census.json")

    assert len(descriptions) == PRESETS_WITH_A_DESCRIPTION, (
        f"descriptions.json has {len(descriptions)} entries; {PRESETS_WITH_A_DESCRIPTION} "
        "of the 668 Module presets have a description .txt")
    assert len(descriptions) == census["has_long_description"], (
        f"descriptions.json has {len(descriptions)} entries but the census counts "
        f"{census['has_long_description']} presets with has_long_description set. The two "
        "are built from the same folder in the same run and must agree")

    empty = [name for name, text in descriptions.items() if not text.strip()]
    assert not empty, (
        f"these entries carry no text and must be omitted instead: {empty}")
    assert all(isinstance(text, str) for text in descriptions.values())

    # H10: ASCII only. The source .txt files are mixed UTF-8 / CP1252 and 39 of them carry
    # smart punctuation, which the build folds to its ASCII equivalent.
    non_ascii = [name for name, text in descriptions.items()
                 if not name.isascii() or not text.isascii()]
    assert not non_ascii, f"non-ASCII text survived the build in: {non_ascii}"


def test_census_allowlist_sizes_are_the_measured_values():
    """A2.9. `census.json` is the allowlist source for `category`/`module`/`technique`.

    The sizes are asserted against step 9.6's measurement rather than against the
    specification's 13/37/51, because the module figure does not reproduce: A2.2 adds
    `Low Pass Filter`, `Recirculator` and `Convolution` to a count of 37 that already
    included them, and `setup.py`'s spelling of wire value 17 differs from the research
    decoder's. Pinning the measured number here is what stops `search_factory_presets`'
    docstring from advertising a list it cannot produce.
    """
    census = _load("census.json")
    measured = {key: len(census[key]) for key in ALLOWLIST_SIZES}
    assert measured == ALLOWLIST_SIZES, (
        f"allowlist sizes changed: {measured} against the measured {ALLOWLIST_SIZES}. "
        "These are D9.3's three enum allowlists; a change here changes what "
        "search_factory_presets accepts and what its ValueError lists")

    # Each allowlist is a value -> count map, so the keys ARE the accepted strings and the
    # tool cannot drift from the data by reading a hardcoded list.
    for key in ALLOWLIST_SIZES:
        table = census[key]
        assert all(isinstance(name, str) and name for name in table), (
            f"census.{key} keys are the accepted enum strings; one is empty or not a string")
        assert all(isinstance(count, int) and count > 0 for count in table.values()), (
            f"census.{key} must count only values that occur; a zero entry would advertise "
            "a filter that can never match")

    assert set(census["category_main"]) <= set(
        _load("preset_index_1081.json")["menu_order"]), (
        "every category in the census must be a menu slot; an unknown tag means the "
        "description parser took something that is not a category")


# The shipped record shape, pinned (A2.13 m19). 26 keys: the 25 Keep fields with
# `implicit_defaults` replaced by the resolved values plus `bank_in_use`, and
# `category_index` - the number load_preset's second argument takes, added once the
# filename collation was device-verified (2026-10-28).
# `implicit_defaults` replaced by the resolved values plus `bank_in_use`. The 49 worked
# examples carry one more, `wiring`.
SHIPPED_RECORD_KEYS = {
    "name", "file", "system_slot", "flat_preset_number", "generation", "firmware",
    "category_main_tag", "category_main_name", "category_menu_index", "category_tags",
    "category_tag_names", "category_index", "author", "macro_labels",
    "has_long_description", "banks",
    "bank_in_use", "oscillators", "polyphony", "recirculator", "shape_generators",
    "modules_used", "modules_used_including_defaults", "dsp_heavy_modules",
    "dsp_cost_classes", "techniques",
}

# Dropped from the full catalog's 42 fields. Keep(25) + Drop(17) = 42 exactly, so nothing
# is overlooked; `implicit_defaults` is one of the 25 Keep fields and is dropped as well,
# because the corrected view APPLIES it instead of shipping the rule.
DROPPED_RECORD_KEYS = {
    "matrix", "formulas", "macro_values", "setup_explicit_values", "setup_explicit_ids",
    "setup_unknown_pokes", "streams_present", "macro_labels_normalised",
    "category_tag_number", "other_description_tags", "fade", "bend_range_raw",
    "spectral_set_raw", "row_type_raw", "delay_time_select_raw", "macro_source",
    "master_columns", "implicit_defaults",
}

WIRING_KEYS = {"generation", "firmware", "setup", "cells", "letters", "notes"}

# matA..matV' (docs/HakenMidi.h:331-347): the cell values that name a formula. matW/matX/
# matY/matZZ, matDec and mat1..mat9 are sources and constants, not formula letters.
FORMULA_LETTER = re.compile(r"^[A-V]'?$")

# Criterion 7's ceiling. It is a self-imposed budget, not a platform limit: nothing in git,
# the wheel or MCP imposes a size on this file. Its purpose is to keep "load the catalog once
# at import, no caching layer" defensible (`minimal-implementation.md:15-16`).
#
# It was 1 MiB, from a 909 KB projection taken before three changes the spec itself mandated
# landed: the kHz transfer default and the offset negative heights (G5/G6), `bank_in_use`, and
# the formula-letter fix for the 19 letters that rendered as "(all components zero)" while
# carrying blend-slider content. Measured afterwards the file is 1,290,428 B.
#
# Raised to 1.5 MiB rather than cutting content, because the cost the old number was proxying
# for does not exist at this scale: the whole file parses in 9.3 ms, and dropping the 355 KB
# wiring block into a second file would save 3.7 ms. The ceiling is kept - not removed - so a
# future tenfold growth still fails loudly.
CATALOG_SIZE_LIMIT = 3 * 1024 * 1024 // 2        # 1.5 MiB

# `census.polyphony_base.absent_so_default`: the presets whose base polyphony is the
# device default. The default VALUE is undocumented - the header defines `defBendRange`
# but no `defPoly` - so these records carry the resolution as a flag.
PRESETS_INHERITING_POLYPHONY = 31


def test_shipped_catalog_has_668_records_with_26_keys():
    """m19. The trim is a contract, not a size optimisation.

    A consumer reads this file instead of the 3.4 MB full catalog, so the field set it may
    rely on has to be pinned. The 17 dropped fields are asserted absent by name too:
    dropping `matrix`/`formulas` is what makes the file shippable at all, and a rebuild that
    reinstated them would otherwise surface only as a size failure.
    """
    catalog = _load("factory_catalog.json")
    presets = catalog["presets"]
    assert len(presets) == 668, (
        f"{len(presets)} records; the Module ships 668 factory presets")
    assert catalog["counts"]["failures"] == 0

    for record in presets:
        keys = set(record) - {"wiring"}
        assert keys == SHIPPED_RECORD_KEYS, (
            f"{record['name']}: unexpected {sorted(keys - SHIPPED_RECORD_KEYS)}, "
            f"missing {sorted(SHIPPED_RECORD_KEYS - keys)}")
        assert not keys & DROPPED_RECORD_KEYS
    assert all(len(record) in (26, 27) for record in presets), (
        "a record is the 26 shipped keys, plus `wiring` on the 49 worked examples")


def test_no_record_has_a_null_bank_oscillator_sg_or_polyphony():
    """D5.2's compression trap, resolved at build time so no consumer can invert it.

    Wire value 0 of `idBankA/B/C` and `idOscFilTyp*` is BiqBank / VoiceDelay / DSF, and a
    compressed preset omits whatever equals the default (`docs/HakenMidi.h:478-480`). A raw
    record therefore reads `banks: {A: "WaveBank", B: null, C: null}` while the device runs
    BiqBank on B and VoiceDelay on C. Each of the five fields below is the resolved reading,
    and `bank_in_use` - not a `null` - is what says whether a bank is wired.
    """
    presets = _load("factory_catalog.json")["presets"]
    for record in presets:
        name = record["name"]
        assert set(record["banks"]) == {"A", "B", "C"}
        assert all(isinstance(t, str) and t for t in record["banks"].values()), (
            f"{name}: null bank type in {record['banks']}")
        assert set(record["bank_in_use"]) == {"A", "B", "C"}
        assert all(isinstance(v, bool) for v in record["bank_in_use"].values())

        for field in ("oscillators", "shape_generators"):
            assert len(record[field]) == 5
            assert all(isinstance(t, str) and t for t in record[field]), (
                f"{name}: null entry in {field}: {record[field]}")

        assert isinstance(record["recirculator"], str) and record["recirculator"]

        poly = record["polyphony"]
        assert set(poly) == {"base", "base_from_default", "expanded",
                             "double_computation_rate"}
        assert isinstance(poly["base"], int) and poly["base"] > 0, (
            f"{name}: polyphony base is {poly['base']!r}")
        assert all(isinstance(poly[flag], bool) for flag in
                   ("base_from_default", "expanded", "double_computation_rate"))

    # The one resolution the header cannot justify must be visible as data, not only in a
    # note: `idPoly`'s absent value is undocumented, so the records that inherit it say so.
    inherited = [r["name"] for r in presets if r["polyphony"]["base_from_default"]]
    assert len(inherited) == PRESETS_INHERITING_POLYPHONY, (
        f"{len(inherited)} records inherit the base-polyphony default; the census counts "
        f"{PRESETS_INHERITING_POLYPHONY} presets with no idPoly. A consumer that cites "
        "polyphony for one of these has to see the flag")


def test_49_records_carry_a_seven_key_wiring_block():
    """C6, resolved to 49 presets (A2.6 M1). 43 is the `###` block count, not the presets.

    The selection list is `corpus-module-wiring.md`'s 43 worked-example blocks, which name 49
    distinct presets; the data is produced by `preset_file.py` from the preset files, never
    transcribed from the markdown. The `letters` block is what makes a cell teachable: a cell
    reading `= D` is useless without D's expansion, so every letter a cell names must be
    expanded here - including one whose formula is all-default and so absent from the file.
    """
    presets = _load("factory_catalog.json")["presets"]
    blocks = {r["name"]: r["wiring"] for r in presets if "wiring" in r}

    assert len(blocks) == 49, f"{len(blocks)} wiring blocks; 49 presets are named"
    assert set(blocks) == set(preset_file.WIRING_PRESETS), (
        "the shipped set and the builder's selection list disagree: "
        f"missing {sorted(set(preset_file.WIRING_PRESETS) - set(blocks))}, "
        f"unexpected {sorted(set(blocks) - set(preset_file.WIRING_PRESETS))}")

    for name, wiring in blocks.items():
        assert set(wiring) == WIRING_KEYS, (
            f"{name}: wiring keys differ by {sorted(set(wiring) ^ WIRING_KEYS)}")
        assert wiring["generation"] in ("modern", "legacy")
        assert wiring["cells"], f"{name}: a worked example with no matrix cells"
        for cell in wiring["cells"]:
            assert set(cell) == {"row", "col", "value", "row_name", "col_name", "muted"}, (
                f"{name}: cell keys are {sorted(cell)}")
            assert isinstance(cell["row_name"], str) and cell["row_name"]
            assert isinstance(cell["col_name"], str) and cell["col_name"]
            if FORMULA_LETTER.match(str(cell["value"])):
                assert cell["value"] in wiring["letters"], (
                    f"{name}: cell {cell['col_name']} <- {cell['row_name']} = "
                    f"{cell['value']} names a formula the block does not expand")
        for letter, form in wiring["letters"].items():
            assert FORMULA_LETTER.match(letter), f"{name}: {letter!r} is not a formula letter"
            assert form["summary"] and form["operator"], f"{name}: letter {letter} is empty"
        assert wiring["notes"], f"{name}: the notes field is empty"


def test_shipped_catalog_is_within_its_size_budget():
    """Criterion 7, measured. The file is written compact, so its own size IS the measure.

    See `CATALOG_SIZE_LIMIT` for why the ceiling is 1.5 MiB and not the 1 MiB first written.

    Also H10 (ASCII only) and H9: a generated artifact carries no "written on <date>" line.
    A date recording when a FACT was established is fine; one recording when a FILE was
    written is a changelog entry (`commenting.md:18-19`).
    """
    path = KNOWLEDGE_DIR / "factory_catalog.json"
    raw = path.read_bytes()
    assert len(raw) <= CATALOG_SIZE_LIMIT, (
        f"{len(raw)} bytes, {len(raw) / (1024 * 1024):.3f} MiB, over the "
        f"{CATALOG_SIZE_LIMIT / (1024 * 1024):.1f} MiB budget. Raise the budget deliberately "
        "rather than silently dropping one of the 25 Keep fields - dropping one pushes the "
        "compression rule back onto every consumer, which is what this catalog exists to prevent")
    assert raw.isascii(), "H10: the shipped catalog must be ASCII only"

    catalog = json.loads(raw)
    assert len(raw) == len(json.dumps(catalog, separators=(",", ":")).encode("ascii")), (
        "the file is not written compact, so its own size is not the measured quantity")

    header = " ".join(value for value in catalog.values() if isinstance(value, str))
    for changelog in ("generated on", "written on", "built on", "updated on", "rebuilt on"):
        assert changelog not in header.lower(), (
            f"H9: the header carries a {changelog!r} line; a build timestamp is a changelog "
            "entry, not a fact about the device")

# Device-observed on 2026-10-27/28, fw 10.81: each preset was loaded with
# load_preset(category_menu_index, category_index) and the Module reported the expected name
# back (read via list_user_presets' last entry, which is the edit slot). A 17-position scan of
# PT matched the predicted order entry for entry, including `Dolce Cristallo Space` before
# `Dolce Cristallo` - the signature of the filename collation (" " sorts before ".").
DEVICE_VERIFIED_INDICES = (
    ("FM Bells", "PT", 8, 16),
    ("Metal Rainstick", "PE", 7, 11),
    ("Windtube Air Reed", "WI", 2, 54),
)


def test_category_index_matches_what_the_device_loaded():
    """The one field a caller needs to load a preset, pinned against real device observations.

    `category_index` is derived, not measured: it is the position within a category when the
    668 presets are ordered by `system_slot`. A rebuild that changed the collation - or that
    dropped a preset and shifted everything after it - would silently make every published
    index wrong, and `load_preset` would quietly load a neighbour. These three are the
    positions actually confirmed on the Module, so they are the ones worth pinning.
    """
    presets = _load("factory_catalog.json")["presets"]
    by_name = {record["name"]: record for record in presets}
    for name, tag, menu_index, index in DEVICE_VERIFIED_INDICES:
        record = by_name.get(name)
        assert record is not None, f"{name} is not in the shipped catalog"
        assert record["category_main_tag"] == tag
        assert record["category_menu_index"] == menu_index, (
            f"{name}: category_menu_index is {record['category_menu_index']}, and the device "
            f"loaded it from menu slot {menu_index}")
        assert record["category_index"] == index, (
            f"{name}: category_index is {record['category_index']}, but the device loaded it "
            f"at {index}. Either the collation changed or a preset was added/dropped ahead of "
            "it; published indices are now wrong and load_preset will load a neighbour")


def test_category_index_is_a_dense_0_based_run_per_category():
    """Whatever the collation, the indices must be usable: 0..n-1 with no gaps or repeats.

    A gap means load_preset would be handed a number that addresses nothing; a repeat means
    two presets claim the same slot.
    """
    presets = _load("factory_catalog.json")["presets"]
    per_tag: dict[str, list[int]] = {}
    for record in presets:
        tag = record["category_main_tag"]
        if tag is None:
            assert record["category_index"] is None, (
                f"{record['name']} has no category tag but carries a category_index")
            continue
        per_tag.setdefault(tag, []).append(record["category_index"])
    assert per_tag, "no preset carries a category tag"
    for tag, indices in sorted(per_tag.items()):
        assert sorted(indices) == list(range(len(indices))), (
            f"category {tag} indices are not a dense 0-based run: {sorted(indices)[:12]}...")
