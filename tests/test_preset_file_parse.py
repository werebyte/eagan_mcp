"""`preset_file.decode_preset_file`, the top-level parse path, on committed captures.

WHY THIS FILE EXISTS (the G24 gap analysis, `test-writing.md:33-34`, `:39-40`)
-----------------------------------------------------------------------------
`eagan_mcp/preset_file.py` is the largest module in the package and the producer of all
four shipped JSON artifacts, yet before this file every test reached it only through a
leaf - `decode_formula` for one default, `WIRING_PRESETS` for one name list - or through
its finished output in `tests/test_shipped_data.py`. Its entry point `decode_preset_file`
had no test at all, and the only thing that exercised it end to end was the catalog build,
which needs `HAKEN_EDITOR_DIR`. On a fresh clone that is zero coverage of the parse path,
which is the condition I3 was written to forbid: a green suite must not mean "the parse
path was never run".

The four captures under `tests/fixtures/` are committed precisely so it can run offline.
Two of them (`first_capture` and `preset_20261025_123730`) had no reader before this file
and were unused shipped artifacts (`minimal-implementation.md:21`); they are the degenerate
inputs, and that is what they are used for here.

WHAT THESE TESTS DO AND DO NOT ESTABLISH
----------------------------------------
They pin the decoder to the semantics the project derived from `docs/HakenMidi.h` (fw
10.81) and from the captured bytes. They are **not** device verification: nothing here
opens a MIDI port, touches the Module, reads `HAKEN_EDITOR_DIR`, `docs/` or `captures/`,
and a green run says what the decoder reads out of a file, never what the firmware does.
`ROADMAP.md`'s device items are untouched by anything in this file.

THE ONE LABELLING PROPERTY, AND WHY IT IS ASSERTED HERE
-------------------------------------------------------
`preset_file.py` labels matrix rows from **two** places. The raw decoder at `:430` labels
from the static `matrix_map.ROWS`; `wiring_block` re-labels every cell through
`matrix_map.preset_labels`, the same preset-aware join F9 put behind `get_matrix` and
`set_matrix_point`. Only the second one reaches the shipped catalog, so the shipped data is
correct today - but the two paths disagree on any preset whose rows 9-12 are delay taps,
and a wiring cell labelled "Audio In L" where the preset means "Tap 1" is the exact harm F9
exists to prevent: a skill quoting it routes a delay tap as an audio input. The raw
decoder's static labelling is recorded in the G24 report as a latent defect in a build-only
path, not repaired here.

What is pinned is that `wiring_block` still does the relabelling. It cannot be pinned by
sweeping the shipped JSON: none of the 49 shipped wiring presets sets a row-type selector,
so such a sweep passes vacuously today and would keep passing after the join was deleted -
which is the I3 failure mode again, one level down. So the test shows the two labellings
disagreeing on the committed capture, which makes the join load-bearing, and then pins the
join itself, the way `test_formula_transfer_default.py` and `tests/test_shared_tables.py`
already pin their single-site properties. `tests/test_shipped_data.py` keeps sole ownership
of the shipped JSON's shape and counts; nothing here reads it.
"""

import inspect
from pathlib import Path

from eagan_mcp import matrix_map, preset_file

FIXTURES = Path(__file__).parent / "fixtures"
# Bank A BiqBank, Bank B BiqBank, Bank C MicroDelay; idRowTyp1 and idRowTyp2 both 1, so
# rows 9-12 are the four delay taps. The same capture backs tests/test_matrix_labels.py,
# which reads its stream 20 independently with mido - so the two files corroborate rather
# than restate each other.
MICRODELAY = FIXTURES / "microdelay_wg_v1_20261025_192903.mid"
# An empty MIDI track: one end_of_track meta message and no device traffic at all.
EMPTY_CAPTURE = FIXTURES / "first_capture_20261025_115208.mid"
# Thirteen all-notes-off controllers and nothing else: a capture that caught no preset.
SILENT_CAPTURE = FIXTURES / "preset_20261025_123730.mid"

# The generic names matrix_map.ROWS gives rows 9-12. A preset whose row-type selectors say
# "Tap" must never carry these in a shipped wiring cell.
GENERIC_ROW_NAMES = {9: "Audio In L", 10: "Audio In R", 11: "Sub L", 12: "Sub R"}


def test_decode_preset_file_reads_the_committed_capture_without_an_editor_install():
    """The parse path runs on a fresh clone and agrees with the stream-20 reading.

    Every fact asserted here is one `tests/test_matrix_labels.py` establishes from the same
    bytes by a different route, so a disagreement means one of the two readings of the
    capture is wrong rather than that a number was mistyped.
    """
    got = preset_file.decode_preset_file(str(MICRODELAY))

    assert got["name"] == "MicroDelay WaveGuide v1", (
        f"the capture's name stream decodes to {got['name']!r}; the preset it was taken "
        "from is 'MicroDelay WaveGuide v1' (the preset the Sitar work was built on)")
    assert got["firmware"] == {"raw": 1081, "text": "10.81"}, (
        f"the capture carries firmware {got['firmware']!r}; it was taken from the Module "
        "running 10.81, and the firmware reading is what decides generation-specific "
        "decoding")
    assert got["setup"]["banks"] == {"A": "BiqBank", "B": "BiqBank", "C": "MicroDelay"}, (
        f"decode_preset_file reads banks {got['setup']['banks']!r}; "
        "tests/test_matrix_labels.py reads the same stream 20 from the same file and gets "
        "BiqBank / BiqBank / MicroDelay (ids 91/92/93)")
    assert got["setup"]["row_types"] == {"audio_rows_9_10": "Tap 1/Tap 2",
                                         "submix_rows_11_12": "Tap 3/Tap 4"}, (
        f"decode_preset_file reads row types {got['setup']['row_types']!r}; this preset "
        "sets idRowTyp1 = 1 and idRowTyp2 = 1, so all four of rows 9-12 are delay taps")
    assert got["matrix"], (
        "the capture holds a 49-cell matrix; an empty matrix here means the container or "
        "the cc40/41/44 triples were not parsed, and the catalog is built on this path")


def test_decode_preset_file_returns_every_section_its_docstring_promises():
    """The return contract the docstring states is the one a caller gets.

    `commenting.md:9-16` makes a docstring testable surface. This one names twelve sections;
    a caller reading it and indexing a key that is absent gets a `KeyError`, and the catalog
    builder is exactly such a caller.
    """
    promised = ("name", "description", "matrix", "formulas", "setup", "unknown",
                "firmware", "generation", "macros", "graphs", "convolution", "container")
    got = preset_file.decode_preset_file(str(MICRODELAY))

    missing = [key for key in promised if key not in got]
    assert not missing, (
        f"decode_preset_file's docstring promises {', '.join(promised)}; the returned dict "
        f"is missing {missing}. Either the decoder dropped a section or the docstring "
        "outran it - both are defects, and the docstring is the shipped half")


def test_degenerate_captures_decode_to_an_empty_preset_instead_of_raising():
    """A capture that caught nothing must degrade, not explode.

    `error-handling.md`'s graceful degradation: a short or empty listen window is a recorded
    and recurring condition (`device-io.md:16-18`), so both captures of one are committed.
    The decoder has no preset to report and must say so by returning an empty one - with the
    filename as the name, since the name stream never arrived - rather than by raising out of
    a batch that is decoding 668 files.
    """
    for path in (EMPTY_CAPTURE, SILENT_CAPTURE):
        got = preset_file.decode_preset_file(str(path))

        assert got["name"] == path.stem, (
            f"{path.name} carries no name stream, so the name must fall back to the "
            f"filename stem {path.stem!r}; got {got['name']!r}")
        assert got["streams_present"] == [], (
            f"{path.name} carries no device streams at all; decode_preset_file reports "
            f"{got['streams_present']!r} present, so something is being invented")
        assert got["matrix"] == [] and got["formulas"] == {}, (
            f"{path.name} holds no matrix and no formulas; got {len(got['matrix'])} cells "
            f"and {len(got['formulas'])} formulas")
        assert got["firmware"] is None, (
            f"{path.name} carries no firmware reply, so the firmware must be reported "
            f"absent rather than guessed; got {got['firmware']!r}")


def test_wiring_block_relabels_rows_instead_of_copying_the_raw_decoder_name():
    """The F9 join is load-bearing in the catalog producer, and it has exactly one form.

    `preset_file.py` labels matrix rows from two places. The raw decoder at `:430` labels
    from the static `matrix_map.ROWS`; `wiring_block` re-labels every cell through
    `matrix_map.preset_labels`, the preset-aware join F9 put behind `get_matrix` and
    `set_matrix_point`. The first assertion below shows the two disagree on the committed
    capture - the relabelling is not a no-op, it is the whole difference between "Tap 1" and
    "Audio In L" - and the second pins that `wiring_block` does the relabelling rather than
    copying the raw name through.

    A data-level sweep of the shipped catalog cannot pin this: none of the 49 shipped wiring
    presets happens to set a row-type selector, so every such assertion passes vacuously
    today and would go on passing after the join was deleted. The property is therefore
    asserted where it is decidable, the same way
    `test_transfer_default_has_exactly_one_definition_site` and
    `tests/test_shared_tables.py` pin their single-site properties.
    """
    decoded = preset_file.decode_preset_file(str(MICRODELAY))
    labels = matrix_map.preset_labels(decoded["setup"])
    raw_names = {cell["row"]: cell["row_name"] for cell in decoded["matrix"]}
    joined = {row: matrix_map.row_name(row, labels) for row in GENERIC_ROW_NAMES}

    assert [raw_names.get(row) for row in sorted(GENERIC_ROW_NAMES)] == \
           [GENERIC_ROW_NAMES[row] for row in sorted(GENERIC_ROW_NAMES)], (
        f"the raw decoder is expected to label rows 9-12 from the static table; it gave "
        f"{raw_names}. If this changed, the raw matrix is now preset-aware and the second "
        "half of this test is measuring nothing")
    assert joined == {9: "Tap 1", 10: "Tap 2", 11: "Tap 3", 12: "Tap 4"}, (
        f"this capture sets idRowTyp1 = idRowTyp2 = 1, so the preset-aware join must name "
        f"all four of rows 9-12 as delay taps; got {joined}. The two labellings differing "
        "is what makes the relabelling in wiring_block load-bearing")

    source = inspect.getsource(preset_file.wiring_block)
    assert 'matrix_map.row_name(cell["row"], labels)' in source, (
        "wiring_block no longer labels its cells through matrix_map.row_name with the "
        "preset labels. Every delay tap in the shipped catalog then becomes 'Audio In L' / "
        "'Sub L', and a skill quoting the catalog routes a delay tap as an audio input - "
        "the exact harm F9 exists to prevent")
    assert 'cell["row_name"]' not in source, (
        "wiring_block copies the raw decoder's row_name into the shipped wiring block. "
        "That name comes from the static matrix_map.ROWS table and is wrong for any preset "
        "whose rows 9-12 are delay taps")
