"""EaganMatrix row/column names. Authoritative: docs/HakenMidi.h ccRow/ccCol (fw 10.81).

Verified on the EM Module 2026-10-25 = checked against factory presets
whose matrix is described in the EaganMatrix User Guide.
Guide = order taken from the guide / Editor layout, not tested yet."""

ROWS = {
    0: "Noise",                                   # verified (Noise - Pink)
    1: "Osc 1", 2: "Osc 2", 3: "Osc 3", 4: "Osc 4", 5: "Osc 5",  # Osc 1 verified (Sine Wave)
    6: "Bank A", 7: "Bank B", 8: "Bank C",        # A, B verified (Noise - Pink, Bowed BiqBank)
    9: "Audio In L", 10: "Audio In R",            # verified (Audio Through)
    11: "Sub L", 12: "Sub R",                     # HakenMidi.h rSubL/rSubR
    13: "Direct +", 14: "Direct + (2)",           # rDirect1/rDirect2 (both verified on device)
    15: "Direct -",                               # rNegDirect
    16: "Direct x (multiply)",                    # rMultiply
}

COLS = {
    0: "Master SL", 1: "Master SR",
    # 2..7 are assignable Master columns since 10.60 (Mat_Poke ids 27..32); see get_setup
    # "master_columns" for what each one drives in the current preset.
    2: "Master col 1 (assignable)", 3: "Master col 2 (assignable)", 4: "Master col 3 (assignable)",
    5: "Master col 4 (assignable)", 6: "Master col 5 (assignable)", 7: "Master col 6 (assignable)",
    8: "Master/Dry mix (SM)", 9: "Dry L", 10: "Dry R",
    # Source: docs/HakenMidi.h:680 cSep = 11, "separator column (used for no column
    # selected)". A modern preset file selects row 0 / column 11 to end its matrix block,
    # so a decoder that has no name for 11 mislabels the end marker of every preset.
    11: "Separator (cSep)",
}
for n in range(5):
    base = 12 + 3 * n
    COLS[base] = f"Osc/Filter {n + 1} input (audio in / phase)"
    COLS[base + 1] = f"Osc/Filter {n + 1} F (freq, kHz)"
    COLS[base + 2] = f"Osc/Filter {n + 1} B/S (bandwidth or spectral balance)"
for bank, base in (("A", 27), ("B", 35), ("C", 43)):
    for i in range(8):
        COLS[base + i] = f"Bank {bank} col {i + 1} (meaning depends on bank type)"
for n in range(5):
    COLS[51 + 2 * n] = f"SG {n + 1} F (Hz) / P (phase)"
    COLS[52 + 2 * n] = f"SG {n + 1} T (trigger) / F2 (dual)"


# What a matrix cell holds (ccMatVal, low 6 bits; bit 6 = muted). Contiguous 0-based
# enumeration, so the index IS the wire code.
# Source: docs/HakenMidi.h:331-347 SSL_ccMatVal, codes 0..60: matA..matV = 1..22,
# matA'..matV' = 23..44 (added in 10.30, docs/HakenMidi.h:751), matW/matX/matY/matZZ =
# 45..48, matDec = 49, mat1..mat9 = 50..58, matSq/matCu = 59..60.
MAT_VALUES = ([""]
              + [chr(65 + i) for i in range(22)]
              + [chr(65 + i) + "'" for i in range(22)]
              + ["W", "X", "Y", "z^2", "<decimal>"]
              + [str(n) for n in range(1, 10)]
              + ["row^2", "row^3"])
MAT_VALUE_DECIMAL = 49           # docs/HakenMidi.h:760 matDec: the digits follow on cc42/cc43
MAT_VALUE_MUTED_BIT = 64         # docs/HakenMidi.h:765 matDisBit


# ---- the preset-specific layer over ROWS/COLS ----------------------------------------------
# ROWS/COLS above are the GENERIC layout. Four groups of entries are not fixed by the layout
# at all - they depend on the loaded preset, and labelling them from the static table is wrong
# for 3 of 18 captured presets:
#   rows  9/10        idRowTyp1 (stream-20 id 106): audio, or delay taps 1/2
#   rows 11/12        idRowTyp2 (stream-20 id 107): the submix, audio, or delay taps 3/4
#   columns 2..7      idMastCol1..6 (stream-20 ids 27..32): what each Master column drives
#   columns 27..50    idBankA/B/C (stream-20 ids 91/92/93): which module each bank runs
#
# NAMESPACE COLLISION - these must not be conflated: stream-20 ids 27..32 are the Master
# column *selectors*; matrix columns 27..34 are Bank A. Same numbers, two different spaces.
#
# preset_labels takes the ALREADY-DECODED setup dict (setup.decode of stream 20), so this
# module still imports nothing (H12).

# setup.decode's row_types strings -> one name per row, rows 9/10 then rows 11/12. Keyed by the
# exact strings of setup.ROW_TYPES1 / setup.ROW_TYPES2, because a decoded dict is all that
# crosses between the two modules; keep this table in step with those two.
# Source: docs/HakenMidi.h:1634-1637 idRowTyp1, :1638-1643 idRowTyp2.
ROW_PAIR_NAMES = {
    "Audio L/R": ("Audio In L", "Audio In R"),
    "Tap 1/Tap 2": ("Tap 1", "Tap 2"),
    "Mono Audio + Mono Tap 1+2": ("Audio In (mono)", "Tap 1+2 (mono)"),
    "Submix L/R": ("Sub L", "Sub R"),
    "Tap 3/Tap 4": ("Tap 3", "Tap 4"),
    "Mono Submix + Mono Tap 3+4": ("Sub (mono)", "Tap 3+4 (mono)"),
    "Mono Audio + Mono Tap 3+4": ("Audio In (mono)", "Tap 3+4 (mono)"),
}

# setup.decode renders an id the preset never set as "?None" (its _name helper). Such a
# selector says nothing about the preset, so the generic name is kept instead.
_UNSET = "?None"


def preset_labels(decoded_setup: dict | None) -> dict:
    """Row and column names for ONE preset, from its decoded setup (setup.decode, stream 20).

    The single labelling path: get_matrix and set_matrix_point both read a cell through this,
    so they cannot disagree about the same cell. Returns {"rows": {...}, "cols": {...}}.
    A missing setup (an empty device read) or an unset selector falls back to the generic
    ROWS/COLS entry, so the result degrades to the static layout rather than to a wrong name.
    """
    rows, cols = dict(ROWS), dict(COLS)
    if not decoded_setup:
        return {"rows": rows, "cols": cols}
    row_types = decoded_setup.get("row_types") or {}
    for first, key in ((9, "audio_rows_9_10"), (11, "submix_rows_11_12")):
        pair = row_types.get(key)
        if not pair or pair == _UNSET:
            continue
        # An unrecognised selector keeps the decoder's visible "?<n>" rather than inventing a
        # name (codec-conventions.md:14-15: never raise, never drop).
        rows[first], rows[first + 1] = ROW_PAIR_NAMES.get(
            pair, (f"{pair} (first)", f"{pair} (second)"))
    for col, target in (decoded_setup.get("master_columns") or {}).items():
        if target and target != _UNSET:
            cols[col] = f"Master col {col - 1}: {target}"
    for bank, base in (("A", 27), ("B", 35), ("C", 43)):
        bank_type = (decoded_setup.get("banks") or {}).get(bank)
        if not bank_type or bank_type == _UNSET:
            continue
        for i in range(8):
            cols[base + i] = f"Bank {bank} col {i + 1} ({bank_type})"
    return {"rows": rows, "cols": cols}


def row_name(r: int, labels: dict | None = None) -> str:
    """labels = a preset_labels result; without one, the generic layout."""
    return (labels["rows"] if labels else ROWS).get(r, f"row {r}")


def col_name(c: int, labels: dict | None = None) -> str:
    """labels = a preset_labels result; without one, the generic layout."""
    return (labels["cols"] if labels else COLS).get(c, f"col {c}")


def value_label(code: int) -> str:
    return MAT_VALUES[code] if 0 <= code < len(MAT_VALUES) else f"?{code}"


def formula_letter(number: int) -> str:
    """ccFormSel / ccMatVal formula number -> letter. Source: docs/HakenMidi.h:748-759."""
    if 1 <= number <= 44:
        return MAT_VALUES[number]
    return f"?{number}"
