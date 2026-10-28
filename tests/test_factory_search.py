"""`search_factory_presets`, the structured query over the 668-preset factory corpus.

SCOPE OF THIS SUITE
-------------------
This file owns **every** assertion about the tool. `tests/test_shipped_data.py` owns every
assertion about the JSON it reads. The split is deliberate: a defect in the data must
surface there as a data failure, not here as a tool failure. So the expected option lists
below are re-derived from `census.json` rather than typed out - a hardcoded list here would
assert the same thing twice and drift from the data on the next rebuild.

Nothing here reads `HAKEN_EDITOR_DIR`, nothing opens a MIDI port and nothing touches the
Module (criterion 9). Importing `eagan_mcp.server` loads the four shipped JSON artifacts and
nothing else.

THE `ValueError` TEXTS ARE PINNED LITERALLY (A2.13 m23)
-------------------------------------------------------
D9.3 describes the refusals but never writes them out, and the `preset`-plus-filter case has
no text at all. They are the prompt the calling agent reads when it guesses wrong, so they
are pinned here as literal templates with the option list interpolated from the same census
the tool consults (`validation.md:19`): the message cannot drift from the data, and a
rewording of the prose is a deliberate change to a shipped interface, not an accident.
"""

import json
from pathlib import Path

import pytest

import eagan_mcp
from eagan_mcp import server

KNOWLEDGE_DIR = Path(eagan_mcp.__file__).parent / "knowledge"
CENSUS = json.loads((KNOWLEDGE_DIR / "census.json").read_text(encoding="utf-8"))
PRESET_INDEX = json.loads(
    (KNOWLEDGE_DIR / "preset_index_1081.json").read_text(encoding="utf-8"))

# The accepted strings, re-derived. `category` is the UNION of the 13 populated tags and the
# 14-slot menu, so `UP` is accepted and returns nothing (m20). `module` is the 37-value census
# space plus the two A2.2 additions, neither of which is a bank or oscillator type.
EXPECTED_CATEGORIES = sorted(set(CENSUS["category_main"]) | set(PRESET_INDEX["menu_order"]))
EXPECTED_EMPTY_CATEGORIES = sorted(PRESET_INDEX["menu_slots_with_no_presets"])
EXPECTED_MODULES = sorted(
    list(CENSUS["modules_used_including_defaults"]) + ["Recirculator", "Convolution"])
EXPECTED_TECHNIQUES = sorted(CENSUS["techniques"])
EXPECTED_BANKS = ["A", "B", "C"]

# One of the 49 presets carrying a decoded `wiring` block, and one of the 619 without.
PRESET_WITH_WIRING = "Additive Gnilham"
PRESET_WITHOUT_WIRING = "Acrylic Clock 2"


def test_each_enum_argument_rejects_an_unknown_value_with_the_full_option_list():
    """m23 + `validation.md:19`: every refusal is pinned, and carries the live option list."""
    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(category="ZZ")
    assert str(excinfo.value) == (
        f"unknown category 'ZZ'; options: {EXPECTED_CATEGORIES}, of which "
        f"{EXPECTED_EMPTY_CATEGORIES} hold no factory presets and return count 0")

    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(module="Biqbank")
    assert str(excinfo.value) == (
        f"unknown module 'Biqbank'; options: {EXPECTED_MODULES}")

    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(technique="granular_delay")
    assert str(excinfo.value) == (
        f"unknown technique 'granular_delay'; options: {EXPECTED_TECHNIQUES}")

    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(bank="D")
    assert str(excinfo.value) == f"unknown bank 'D'; options: {EXPECTED_BANKS}"

    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(preset="No Such Preset")
    assert str(excinfo.value) == (
        "unknown preset 'No Such Preset'; preset= takes one exact factory preset name out "
        "of the 668 in the catalog - find one with text=, then look it up")

    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(preset=PRESET_WITH_WIRING, category="OT")
    assert str(excinfo.value) == (
        f"preset={PRESET_WITH_WIRING!r} is a full-record lookup and cannot be combined with "
        "a filter; drop ['category'] to look it up, or drop preset= and search")

    # The option lists are the live tables, not a copy: a sanity bound on the three sizes,
    # whose exact values are test_shipped_data.py's to assert.
    assert len(EXPECTED_CATEGORIES) == 14 and len(EXPECTED_MODULES) == 39
    assert len(EXPECTED_TECHNIQUES) == 52


def test_preset_lookup_returns_a_full_record_with_and_without_wiring():
    """Lookup mode returns the whole trimmed record - this is how a 33rd tool is avoided."""
    with_wiring = server.search_factory_presets(preset=PRESET_WITH_WIRING)
    assert set(with_wiring) == {"preset"}
    record = with_wiring["preset"]
    assert record["name"] == PRESET_WITH_WIRING
    assert len(record) == 27, (
        "one of the 49 decoded presets carries the 26 descriptive keys plus `wiring`. The 26th "
        "is `category_index`, added once the per-category collation was device-verified")
    assert record["wiring"]["cells"], "a wiring block must carry its decoded matrix cells"

    without = server.search_factory_presets(preset=PRESET_WITHOUT_WIRING)["preset"]
    assert without["name"] == PRESET_WITHOUT_WIRING
    assert "wiring" not in without
    assert len(without) == 26, (
        "a preset with no wiring block carries the 26 descriptive keys; the 26th is "
        "`category_index`, the number load_preset's second argument takes")

    # The compression trap is resolved at build time (G10): the five fields a naive consumer
    # would read as "this preset has no bank/oscillator/SG" are resolved and never null.
    for field in ("banks", "oscillators", "shape_generators", "recirculator", "polyphony"):
        assert without[field], f"{field} must be resolved, never null (compression_rule_resolved)"


def test_preset_plus_a_filter_raises():
    """The two modes are exclusive; every filter name appears in the refusal."""
    for kwargs in ({"text": "bowed"}, {"category": "ST"}, {"module": "BiqBank"},
                   {"technique": "granular"}, {"bank": "A"}):
        with pytest.raises(ValueError) as excinfo:
            server.search_factory_presets(preset=PRESET_WITH_WIRING, **kwargs)
        message = str(excinfo.value)
        assert "full-record lookup" in message
        assert repr(list(kwargs)) in message, (
            f"the refusal must name the filter that collided, got {message!r}")

    # Several at once are all named, sorted, so the caller sees the whole collision.
    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(preset=PRESET_WITH_WIRING, bank="A", category="ST")
    assert "['bank', 'category']" in str(excinfo.value)


def test_count_is_total_and_truncated_is_set_above_max_hits():
    """m21. `count` is the TOTAL matches; `presets` carries at most `max_hits` of them."""
    capped = server.search_factory_presets(category="OT", max_hits=5)
    assert set(capped) == {"count", "truncated", "presets"}
    assert capped["count"] == 167, (
        "count must be the total number of matches, not the length of the capped page")
    assert len(capped["presets"]) == 5
    assert capped["truncated"] is True

    whole = server.search_factory_presets(category="OT", max_hits=1000)
    assert whole["count"] == 167 and len(whole["presets"]) == 167
    assert whole["truncated"] is False

    # The summary shape is fixed and compact: a search never returns full records.
    summary = capped["presets"][0]
    assert set(summary) == {"name", "category", "system_slot", "flat_preset_number",
                            "generation", "modules", "polyphony", "macro_labels",
                            "techniques", "has_wiring"}
    assert isinstance(summary["polyphony"], int)
    assert isinstance(summary["has_wiring"], bool)

    with pytest.raises(ValueError) as excinfo:
        server.search_factory_presets(category="OT", max_hits=0)
    assert str(excinfo.value) == "max_hits must be 1 or more, got 0"


def test_category_up_returns_zero_not_a_raise():
    """m20. `UP` is a valid menu slot that holds no factory presets."""
    assert EXPECTED_EMPTY_CATEGORIES == ["UP"]
    empty = server.search_factory_presets(category="UP")
    assert empty == {"count": 0, "truncated": False, "presets": []}


def test_module_filter_normalises_the_alias_of_b_suffix():
    """A2.2 + A2.1: alias normalisation, text over name AND description, and the two
    non-module filters A2.2 requires to answer."""
    # `WaveBank` is the discriminating case: 97 presets carry the bare string, and one more
    # ("Orchester") carries only `WaveBank (alias of B)`, which means Bank C mirrors Bank B's
    # WaveBank. A bare-name search must find all 98; the suffixed string must find only the 1.
    bare = server.search_factory_presets(module="WaveBank", max_hits=1000)
    suffixed = server.search_factory_presets(module="WaveBank (alias of B)", max_hits=1000)
    assert bare["count"] == 98 and suffixed["count"] == 1
    assert suffixed["presets"][0]["name"] == "Orchester"
    assert "Orchester" in {p["name"] for p in bare["presets"]}

    # HarMan's five alias presets all carry the bare string too, so the bare search is a
    # superset rather than strictly larger. Both spellings are accepted.
    harman = server.search_factory_presets(module="HarMan", max_hits=1000)
    harman_alias = server.search_factory_presets(
        module="HarMan (alias of B)", max_hits=1000)
    assert harman_alias["count"] == 5
    assert {p["name"] for p in harman_alias["presets"]} <= {p["name"] for p in harman["presets"]}

    # A2.2: these two must stop raising. Neither is a bank or oscillator type, so each reads
    # the state the record actually carries.
    recirculator = server.search_factory_presets(module="Recirculator", max_hits=1000)
    assert recirculator["count"] == 263, (
        "Recirculator matches the presets that select a type other than the inherited "
        "default Short Reverb")
    convolution = server.search_factory_presets(module="Convolution", max_hits=1000)
    assert convolution["count"] == 107

    # A2.1: `text` matches over the preset name PLUS descriptions.json. "breathy" appears in
    # no preset name at all, so a hit can only have come from the description text.
    breathy = server.search_factory_presets(text="breathy", max_hits=1000)
    assert breathy["count"] >= 5
    assert not any("breathy" in p["name"].lower() for p in breathy["presets"])
    by_name = server.search_factory_presets(text="Acrylic Clock")
    assert "Acrylic Clock" in {p["name"] for p in by_name["presets"]}

    # Filters combine with AND.
    both = server.search_factory_presets(module="WaveBank", bank="C", max_hits=1000)
    assert both["count"] < bare["count"]
    assert all("WaveBank" in " ".join(p["modules"]) for p in both["presets"])
