"""F9 - one labelling path for get_matrix and set_matrix_point, fed by the preset's own setup.

THE DEFECT
----------
Both tools label matrix cells from the STATIC tables `matrix_map.ROWS` / `matrix_map.COLS`.
Rows 9-12 and the bank and Master columns are not fixed by the layout - they depend on the
loaded preset:

  idRowTyp1 (stream-20 id 106)  decides whether rows  9/10 carry audio or delay taps
  idRowTyp2 (stream-20 id 107)  decides whether rows 11/12 carry the submix or delay taps
  idBankA/B/C (ids 91/92/93)    decide what columns 27-34 / 35-42 / 43-50 drive
  idMastCol1..6 (ids 27-32)     decide what the assignable Master columns 2-7 drive

The static table is wrong for 3 of 18 captured presets, `microdelay_wg_v1` among them - the
preset the Sitar work was built on, where rows 9-12 are delay taps and the tool calls them
"Audio In L/R" and "Sub L/R". A skill quoting those names routes a delay tap as an audio input.

WHY THE TWO TOOLS ARE TESTED TOGETHER
-------------------------------------
`get_matrix` labels through the `_named` helper; `set_matrix_point` labelled independently,
bypassing `_named` entirely. Fixing one and not the other makes the two tools disagree about the
same cell - `Tap 1` from one, `Audio In L` from the other - which is the exact harm F9 exists to
prevent. `test_get_matrix_and_set_matrix_point_agree_on_one_cell` pins the join, and also pins
that `set_matrix_point` shares the read it already performs instead of adding a third round-trip.

NO DEVICE, NO EDITOR
--------------------
Every fact here comes from the two committed captures, which carry stream 20. `conn` is never
touched: the one test that drives the tools replaces `_select_and_read` and `_read_setup`, so
nothing is transmitted and no `HAKEN_EDITOR_DIR` is needed (test-writing.md:27-31).
"""

from pathlib import Path

import mido

from eagan_mcp import haken, matrix_map, server, setup

FIXTURES = Path(__file__).parent / "fixtures"
# Bank A BiqBank, Bank B BiqBank, Bank C MicroDelay; rows 9-12 are all four delay taps.
MICRODELAY = FIXTURES / "microdelay_wg_v1_20261025_192903.mid"
# Bank A Kinetic; sets neither row-type selector nor any Master column selector.
BOWED = FIXTURES / "Bowed BiqBank_20261025_115829.mid"


def _stream20_pairs(path: Path) -> dict[int, int]:
    """The (id, value) pairs of stream 20 in a captured preset file."""
    pairs, cur = {}, None
    for m in mido.MidiFile(path):
        if m.type == "control_change" and m.channel == haken.CH16 and m.control == haken.CC_TEXT:
            cur = m.value
        elif m.type == "polytouch" and m.channel == haken.CH16 and cur == haken.STREAM_MAT_POKE:
            pairs[m.note] = m.value
    return pairs


def _stream20_messages(pairs: dict[int, int]) -> list[mido.Message]:
    """The same pairs back on the wire, as the Module sends them after a cell select."""
    return ([haken.cc16(haken.CC_TEXT, haken.STREAM_MAT_POKE)]
            + [mido.Message("polytouch", channel=haken.CH16, note=i, value=v)
               for i, v in pairs.items()])


def _labels(path: Path) -> dict:
    return matrix_map.preset_labels(setup.decode(_stream20_pairs(path)))


def test_microdelay_rows_9_to_12_label_as_taps():
    labels = _labels(MICRODELAY)
    got = {r: matrix_map.row_name(r, labels) for r in (9, 10, 11, 12)}
    assert got == {9: "Tap 1", 10: "Tap 2", 11: "Tap 3", 12: "Tap 4"}, (
        f"microdelay_wg_v1 sets idRowTyp1 = 1 and idRowTyp2 = 1, so rows 9-12 are the four "
        f"delay taps; the labelling join reported {got}. Labelling from the static table is "
        "what F9 fixes: it routes a delay tap as an audio input")
    assert (matrix_map.ROWS[9], matrix_map.ROWS[11]) == ("Audio In L", "Sub L"), (
        "the static table must keep the generic layout - it is what describe_matrix_layout "
        "returns, and the preset-specific names belong in preset_labels")


def test_default_setup_still_labels_audio_in_and_sub():
    labels = matrix_map.preset_labels(setup.decode({}))
    got = {r: matrix_map.row_name(r, labels) for r in (9, 10, 11, 12)}
    assert got == {9: "Audio In L", 10: "Audio In R", 11: "Sub L", 12: "Sub R"}, (
        f"with neither idRowTyp1 nor idRowTyp2 set, both selectors read 0 (Audio L/R, "
        f"Submix L/R) and the rows keep the generic names; got {got}")
    assert matrix_map.preset_labels(None) == {"rows": matrix_map.ROWS, "cols": matrix_map.COLS}, (
        "an empty or failed setup read must degrade to the generic layout, not to a wrong name")
    assert matrix_map.row_name(9) == "Audio In L" and matrix_map.col_name(11) == matrix_map.COLS[11]
    bowed = _labels(BOWED)
    assert matrix_map.row_name(9, bowed) == "Audio In L", (
        "Bowed BiqBank sets both selectors to 0, so its rows 9-12 really are audio and submix")


def test_bank_columns_label_by_bank_type():
    labels = _labels(MICRODELAY)
    banks = ((27, "A", "BiqBank"), (35, "B", "BiqBank"), (43, "C", "MicroDelay"))
    for base, bank, bank_type in banks:
        for col in range(base, base + 8):
            name = matrix_map.col_name(col, labels)
            assert f"Bank {bank}" in name and bank_type in name, (
                f"column {col} is Bank {bank}, which this preset runs as {bank_type} "
                f"(stream-20 id {setup.BANK_IDS[bank]}); got {name!r}")
    bowed = _labels(BOWED)
    assert "Kinetic" in matrix_map.col_name(27, bowed), (
        f"Bowed BiqBank's Bank A is Kinetic; got {matrix_map.col_name(27, bowed)!r}")
    assert "MicroDelay" not in matrix_map.col_name(43, bowed), (
        "Bowed BiqBank's Bank C is VoiceDelay; the label must come from this preset's own id 93")


def test_master_columns_2_to_7_label_from_idmastcol():
    labels = _labels(MICRODELAY)
    expected = {2: "Conv 1 Interp", 3: "Conv 1 Mix", 4: "Recirc R4",
                5: "Recirc Mix", 6: "Conv 2 Interp", 7: "Conv 2 Mix"}
    for col, target in expected.items():
        name = matrix_map.col_name(col, labels)
        assert target in name, (
            f"Master column {col} is driven by stream-20 id {setup.MASTER_COL_IDS[col - 2]}, "
            f"which this preset sets to {target!r}; got {name!r}")
    # The namespace collision the fix must not conflate: stream-20 ids 27-32 are the Master
    # column selectors, matrix columns 27-34 are Bank A.
    assert "Bank A" in matrix_map.col_name(27, labels), (
        "matrix column 27 is Bank A column 1, not Master column 1; stream-20 id 27 is the "
        "idMastCol1 selector and lives in a different number space")
    assert "Conv" not in matrix_map.col_name(27, labels)
    unset = matrix_map.col_name(2, _labels(BOWED))
    assert "assignable" in unset and "None" not in unset, (
        f"Bowed BiqBank sets no Master column selector, so column 2 keeps the generic name "
        f"rather than setup.decode's '?None'; got {unset!r}")


def test_get_matrix_and_set_matrix_point_agree_on_one_cell(monkeypatch):
    pairs = _stream20_pairs(MICRODELAY)
    dump = _stream20_messages(pairs)
    point = {"row": 9, "col": 27, "value": "A"}
    setup_reads = []

    def fake_select_and_read(row, col, extra, seconds):
        return [dict(point)], dump

    def fake_read_setup(seconds: float = 0.8):
        setup_reads.append(seconds)
        return dict(pairs)

    monkeypatch.setattr(server, "_select_and_read", fake_select_and_read)
    monkeypatch.setattr(server, "_read_setup", fake_read_setup)
    monkeypatch.setattr(server.time, "sleep", lambda *_: None)

    read = server.get_matrix()["points"][0]
    assert len(setup_reads) == 1, (
        "get_matrix labels from a setup read of its own - accepted deliberately, because an "
        "opt-in flag would leave the default wrong (spec Addendum 1 decision 4)")

    wrote = server.set_matrix_point(point["row"], point["col"], point["value"])
    assert (read["row_name"], read["col_name"]) == (wrote["row_name"], wrote["col_name"]), (
        f"the two tools disagree about cell (9, 27): get_matrix says "
        f"{(read['row_name'], read['col_name'])}, set_matrix_point says "
        f"{(wrote['row_name'], wrote['col_name'])}. One labelling path, or a skill reading both "
        "gets two different answers for the same cell")
    assert (read["row_name"], read["col_name"][:6]) == ("Tap 1", "Bank A")
    assert len(setup_reads) == 1, (
        "set_matrix_point added a third device round-trip; it must label off the full read it "
        "already performs for verification, which carries stream 20 after a cell select")
