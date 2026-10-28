"""Negative formula-height encoding: offset, not sign-and-magnitude.

WHAT THESE TESTS DO AND DO NOT ESTABLISH
----------------------------------------
They pin the CODEC to the corpus-derived semantics. They are NOT device verification.
No offline test can establish what the Module implements; only the audible test can
(ROADMAP.md "Verify a NEGATIVE formula height on the device"). Do not read a green run
here as closing that item.

Evidence for the offset reading (value = raw/100 - 1 when the Neg flag is set),
re-measured over all 668 factory presets in Haken Editor 1081/Firmware/SysPresets:

  1. 14,147 height writes total. Neg flag CLEAR takes raw 1..127 (5,050 of them >= 100,
     consistent with idHeightW's documented -1.00..1.27). Neg flag SET takes raw 1..99
     only - never 0, never >= 100. Under the mirror reading raw >= 100 with the flag set
     would duplicate values already expressible; the asymmetric ceiling fits the offset.
  2. 564 ORPHAN Neg flags: the flag is set while its height id is absent entirely
     (267 NegBegX, 125 NegW, 38 NegBegY, 30 NegBegZ, ...). An absent height id means
     raw 0, so under the offset reading each orphan is exactly -1.00 - and it is the only
     way to express -1.00. Under the mirror reading all 564 are -0.00, i.e. pointless noise.
     This is the discriminating argument.
  3. Distribution: the 1,055 flag-set writes have median raw 81. That is -0.19 under the
     offset reading and -0.81 under the mirror. 66.3% fall within |v| <= 0.30 under the
     offset against 5.7% under the mirror, while positive heights are 31.1% within 0.30 -
     so the mirror would make near-full-scale the normal case for negatives only.
  4. A trace of the 10.44 Editor to exact Max objects shows an offset encoding with no
     sign-test machinery anywhere in the slider chain.

Header: docs/HakenMidi.h:1201-1202 (idNegW "true for -idHeightW; no effect until idHeightW
received", idHeightW "-1.00..1.27 in 0.01 steps"), :1227-1230, :1242-1246, :1265-1268.
The header states the range but never the magnitude formula, so the offset reading is not
a misread spec.
"""

import pytest

from eagan_mcp import formula

# (value, neg_flag, raw) under the offset reading. -0.50 is deliberately excluded:
# it is the mirror's fixed point and cannot discriminate the two readings.
OFFSET_GOLDEN = [
    (-0.01, 1, 99),
    (-0.10, 1, 90),
    (-0.12, 1, 88),   # the most common negative in the corpus, 223 occurrences
    (-0.20, 1, 80),   # CLAUDE.md's "Harkonnen Voice" wheel sweep
    (-0.31, 1, 69),
    (-0.33, 1, 67),
    (-0.90, 1, 10),
    (-1.00, 1, 0),    # only expressible as raw 0; written as an orphan flag in the corpus
]

POSITIVE_GOLDEN = [
    (0.0, 0, 0),
    (0.12, 0, 12),
    (0.50, 0, 50),
    (1.00, 0, 100),
    (1.27, 0, 127),   # W ceiling, idHeightW
]


@pytest.mark.parametrize("value,neg,raw", OFFSET_GOLDEN)
def test_negative_height_encodes_as_offset(value, neg, raw):
    """slider_encode must emit raw = (value + 1.00) * 100 for a negative height."""
    assert formula.slider_encode(value) == (neg, raw)


@pytest.mark.parametrize("value,neg,raw", OFFSET_GOLDEN)
def test_negative_height_decodes_as_offset(value, neg, raw):
    """slider_value must read a flag-set raw as raw/100 - 1.00."""
    assert formula.slider_value(raw, neg) == pytest.approx(value)


@pytest.mark.parametrize("value,neg,raw", POSITIVE_GOLDEN)
def test_positive_height_is_unchanged(value, neg, raw):
    """Control: the positive branch is already correct and must not move."""
    assert formula.slider_encode(value) == (neg, raw)
    assert formula.slider_value(raw, neg) == pytest.approx(value)


def test_minus_one_half_is_the_fixed_point():
    """Control: -0.50 encodes identically under both readings, so it proves nothing.

    Recorded so nobody later 'verifies' the encoding with the one value that cannot
    discriminate it. The research struck two filed device tests for exactly this reason.
    """
    assert formula.slider_encode(-0.50) == (1, 50)


def test_encoder_never_emits_raw_at_or_above_100_with_the_sign_flag_set():
    """Corpus invariant: 1,055 flag-set height writes span raw 1..99, none >= 100.

    The mirror encoding violates this at exactly -1.00, where it emits raw 100.
    """
    offenders = []
    for hundredths in range(0, 101):          # -1.00 .. 0.00 in 0.01 steps
        value = round(-hundredths / 100, 2)
        neg, raw = formula.slider_encode(value)
        if neg and raw >= 100:
            offenders.append((value, raw))
    assert offenders == [], f"flag set with raw >= 100 at: {offenders}"


def test_orphan_neg_flag_decodes_as_minus_one():
    """A Neg flag with its height id absent is -1.00, not None and not 0.

    564 formulas in the 668-preset factory corpus are encoded this way (267 NegBegX,
    125 NegW, ...), and it is the only encoding for -1.00. formula.py's decode currently
    returns None here, so every one of those formulas reads as an inactive component.
    """
    # NegBegX (id 15) set; the height id it governs (idVBegX = 45) is absent entirely.
    decoded = formula.decode({15: 1})
    assert decoded["X"]["height_begin"] == pytest.approx(-1.00)
    assert decoded["X"]["active"] is True


def test_sub_hundredth_negative_rounds_to_a_representable_value():
    """A negative finer than 0.01 must round to a representable hundredth BEFORE encoding.

    The wire carries 0.01 steps (docs/HakenMidi.h:1202, "-1.00..1.27 in 0.01 steps"), so
    -0.001 has no encoding of its own. Encoding it directly gives
    round((-0.001 + 1.0) * 100) = 100, i.e. the Neg flag set with raw 100, which decodes to
    0.00 and breaks the corpus invariant above (flag set never reaches raw 100).

    Rounding first, -0.001 becomes -0.00, which is 0.0: raw 0 with NO flag. (1, 0) stays
    reserved for -1.00, the orphan-flag encoding. OFFSET_GOLDEN covers exact hundredths
    only and cannot catch this.
    """
    assert formula.slider_encode(-0.001) == (0, 0)     # -0.00 is zero, not an offset of 100
    assert formula.slider_encode(-0.006) == (1, 99)    # rounds to -0.01
    assert formula.slider_encode(-0.994) == (1, 1)     # rounds to -0.99
    assert formula.slider_encode(-0.996) == (1, 0)     # rounds to -1.00


def test_round_trip_cannot_discriminate_the_two_readings():
    """Control, and the reason a read-back device test was struck from the plan.

    encode and decode are mirrored in the SAME direction, so a round-trip is
    self-consistent under either reading at every value. This test passes before and
    after the fix. It exists to document that it is worthless as evidence.
    """
    for hundredths in range(-100, 128):
        value = round(hundredths / 100, 2)
        neg, raw = formula.slider_encode(value)
        assert formula.slider_value(raw, neg) == pytest.approx(value), value
