"""Formula config (stream 19 = s_Form_Poke) decoding.
Authoritative since 10.81: docs/HakenMidi.h. Writes apply to the formula selected by ch16 cc34 (ccFormSel).

Source: Haken Editor 1044, HE Formula.maxpat (rxFormCfg/txFormCfg routes),
verified on the Module 2026-10-25 with Bowed BiqBank formula K.
Stream 19 = (id, value) pairs as ch16 poly pressure (note=id, value=value),
sent by the Module after a cell holding a formula is selected (cc34 = formula number)."""

# Source: docs/HakenMidi.h:1164-1178 idSgW, wSgConstant..wRMS = 0..13. Index == wire value.
W_MODES = ["Constant", "Gated", "SG1", "SG2", "SG3", "SG4", "SG5",
           "SG1b", "SG2b", "SG3b", "SG4b", "SG5b", "FormulaDelay", "RMS of row"]
# Source: docs/HakenMidi.h:1204-1211 idMultW/idMultX/idMultY/idMultZ, m0p001..m1000p0 = 0..6
# (7 = mavail, unassigned). An absent multiplier id means m1p0, not m0p001.
MAGNITUDES = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
MAGNITUDE_DEFAULT = 3
# Source: docs/HakenMidi.h:1212-1220 idScaleW. The header's own names (SCALE_W_NAMES in the
# 10.81 header listing) are wNone, wMacro, w127Macro, wDivFings = 1/fingersDown,
# wVoiceNum, wIfVoice1, wDivPoly = 1/thisDSPpoly. Values 3 and 6 are RECIPROCALS: the W
# value FALLS as fingers land or as DSP polyphony rises. The strings below are the accepted
# enum of a shipped tool (set_formula) and are deliberately NOT renamed; the semantics are
# recorded here and in set_formula's docstring.
W_MODIFIERS = ["x 1", "x Macro", "x 127 x Macro", "x Fingers scaler",
               "x Voice number", "x 1 if voice 1", "x Polyphony scaler"]
# Source: docs/HakenMidi.h:1237 xyzNoM=0, xyzI=1: 0 = no macro, 1..90 = i..vi, m7..m90.
MACROS = ["i", "ii", "iii", "iv", "v", "vi"] + [f"m{n}" for n in range(7, 96)]
# Transfer functions. Source: docs/HakenMidi.h:1235 idTransX values (xOctaves..xSteepS) and
# :1250 idTransY values (yzLinear..yzSteepS, also used by idTransZ and idTransBl).
X_TRANSFER = ["X Oct", "X kHz", "Linear", "Gentle S", "Squared", "SquareRoot",
              "2 step", "3 step", "Graph", "Offsets 1", "Offsets 2", "Steep S"]
YZ_TRANSFER = ["Linear", "Gentle S", "Squared", "SquareRoot", "2 step", "3 step",
               "Graph", "Offsets 1", "Offsets 2", "Steep S"]
# Per-component default transfer function, as a WIRE VALUE so that each table's index stays
# equal to the value the device sends. X defaults to kHz, not to Octaves: across the 668
# factory presets of Editor 1081, TransX = 0 is written explicitly 775 times and TransX = 1
# never, and a compressed preset omits only defaults (docs/HakenMidi.h:478-480), so the
# value that is never written is the default [C]. 334 factory formulas leave it absent.
# A corpus statistic is evidence about Haken's convention, never about what the firmware
# does, and it can never become device-verified: not confirmed on the Module.
# decode() below is the only reader, so the file decoder in preset_file.py gets this default
# by calling decode() rather than re-applying it - one site, not two that can drift apart.
TRANSFER_DEFAULT = {"X": 1, "Y": 0, "Z": 0}
# Source: docs/HakenMidi.h:1255-1262 idInitX/idInitY/idInitZ. cContinuous..cRelative = 0..3
# and cContinuousNT..cRelativeNT = 4..7 (X only, "no trim graph applied", since 10.36).
# Masking these with & 3 would discard the noTrim distinction.
XYZ_MODES = ["Continuous", "Initial", "Derivative", "Relative",
             "Continuous noTrim", "Initial noTrim", "Derivative noTrim", "Relative noTrim"]
Z_MODES = ["Continuous", "Initial", "Derivative", "Release F", "Release P"]
H_MAX = 12          # docs/HakenMidi.h:1232 hMax: the HBeg*/HEnd* shelf ids run 0..12

# How components combine (id 38). Source: HE Formula Equation.maxpat. Bowed BiqBank K has 1.
OPERATORS = ["W + X + Y + Z", "W x (X + Y + Z)", "(W + X + Y) x Z", "(W + X) x (Y + Z)",
             "(W x X) + (Y x Z)"]
OPERATOR_ID = 38

# SG waveform shape used by this formula (id 50; same id = buffer when W mode is FormulaDelay).
# Source: docs/HakenMidi.h:1179-1198 idShapeW. wRampUp..wSine = 0..11, then wSampHold = 12
# (sample-and-hold of a matrix row), wSampHoldA..wSampHoldV = 13..34 and
# wSampHoldA_..wSampHoldV_ = 35..56 (sample-and-hold of formula A..V, A'..V').
# The header notes sample-and-hold is unavailable for a dual SG (contCycle/singleCycle only).
SG_SHAPES = (["Ramp Up", "Ramp Down", "Pulse", "Pulse at End", "Triangle", "Hann",
              "Gentle Up", "Steep Up", "Gentle Down", "Steep Down", "Square", "Sine",
              "S+H row"]
             + [f"S+H {chr(65 + i)}" for i in range(22)]
             + [f"S+H {chr(65 + i)}'" for i in range(22)])
SG_SHAPE_ID = 50
# SG phase (id 117): 0 off, 1..3 = offset 0.25/0.5/0.75, then phase modulation by A..V, A'..V'.
# Source: docs/HakenMidi.h:1199-1200 idSgM, sg90=1 .. sgModV_=47.
SG_PHASES = ["Off", "0.25", "0.5", "0.75"] + [f"mod {chr(65 + i)}" for i in range(22)] + \
            [f"mod {chr(65 + i)}'" for i in range(22)]
SG_PHASE_ID = 117

# W zone: the note-number window in which W is active.
# Source: docs/HakenMidi.h:1221-1224 idLoW, idHiW, idAllW ("W zone repeats every octave"),
# idInitW ("idHiW/idLoW based on initial pitch").
W_ZONE_LOW_ID = 118
W_ZONE_HIGH_ID = 119
W_ZONE_ALL_OCTAVES_ID = 124
W_ZONE_FROM_INITIAL_ID = 125

# Ancillary formula: two chained operations applied to the component selected by idAncDom.
# Source: docs/HakenMidi.h:1275-1291 idAncOp/idAncOp2 (aMul..aCross = 0..12).
ANC_OPS = ["x", "abs then x", "invert then x", "/", "+", "-", "^", "log base",
           "mod", "quantize by", "min", "max", "crossing detect"]
# Source: docs/HakenMidi.h:1292-1312 idAncVal/idAncVal2: a0p0..a10p0 = 0..9, formula A..V =
# 10..31, A'..V' = 32..53, macro i..vi = 54..59, m7..m72 = 60..125, Midi time clock = 126.
ANC_VALUES = (["0.0", "0.25", "0.5", "1.0", "1.5", "2.0", "3.0", "4.0", "5.0", "10.0"]
              + [f"formula {chr(65 + i)}" for i in range(22)]
              + [f"formula {chr(65 + i)}'" for i in range(22)]
              + [f"macro {m}" for m in MACROS[:6]]
              + [f"macro m{n}" for n in range(7, 73)]
              + ["Midi time clock"])
# Source: docs/HakenMidi.h:1313-1314 idAncDom, aWXYZ=0,aW,aX,aY,aZ.
ANC_DOMAINS = ["WXYZ", "W", "X", "Y", "Z"]
# Source: docs/HakenMidi.h:1316-1317 idAncLookup, aLookNo..aLook2nd48 = 0..6.
ANC_LOOKUPS = ["no", "graph", "1st", "2nd", "graph48", "1st48", "2nd48"]
ANC_DOMAIN_ID = 7           # docs/HakenMidi.h:1313 idAncDom
ANC_LOOKUP_ID = 8           # docs/HakenMidi.h:1316 idAncLookup
ANC_LIMIT_ID = 9            # docs/HakenMidi.h:1319 idAncLimit: engage matrix column limiter
ANC_TO_NN_ID = 10           # docs/HakenMidi.h:1318 idAncNN: convert kHz to note number
ANC_TOUCH_AREA_ID = 11      # docs/HakenMidi.h:1315 idAncTAorAll: Touch Area / All Fingers
ANC_OP_IDS = (56, 100)      # docs/HakenMidi.h:1275-1276 idAncOp, idAncOp2
ANC_VALUE_IDS = (57, 101)   # docs/HakenMidi.h:1292-1293 idAncVal, idAncVal2

# Blend: which control crossfades the primary formula values into the secondary ones.
# Source: docs/HakenMidi.h:1326-1332 idBlend (ps0..psSos2 = 0..8 at :1328), idBlMacForm
# (the macro 0..95 or formula 0..44 psMacro/psForm select), idHBegBl/idHEndBl, idTransBl.
BLEND_CONTROLS = ["0", "1", "formula", "macro", "ch1 note", "duplex", "sustain",
                  "sostenuto", "sostenuto 2"]
BLEND_ID = 39
BLEND_MACRO_FORM_ID = 68
BLEND_SHELF_IDS = (121, 123)
BLEND_TRANSFER_ID = 12

# Shaping ids with no value table: each is a plain 0..127 setting.
# Source: docs/HakenMidi.h:1239 idZeroX (note number for zero X, 60 = middle C),
# :1240 idQuantX, :1321 idInterp (interpDef = 40), :1323 idPersist, :1324 idReluct,
# :1348-1350 idPersist2/idInterp2/idReluct2.
ZERO_X_ID = 44
QUANTIZE_X_ID = 112
INTERPOLATION_IDS = (48, 82)
PERSISTENCE_IDS = (63, 81)
RELUCTANCE_IDS = (96, 97)

# slider id -> its sign-bit id (sign bit always sent just before the slider)
SLIDER_SIGN = {42: 13, 73: 14, 45: 15, 75: 16, 46: 17, 76: 18, 51: 19, 77: 20,
               52: 21, 78: 22, 58: 23, 79: 24, 59: 25, 80: 26}
# The same pairing read the other way: Neg id -> the height id it precedes on the wire.
# Nothing calls it; it is kept as the project's reference for which of the 14 Neg ids
# (idNegW..idNegEndZ2, docs/HakenMidi.h:1201, :1227-1230, :1242-1246, :1265-1268) belongs to
# which height, which is the only way to read a stream-19 capture by eye - the flag arrives
# BEFORE its height and the ids are not adjacent. Retained unused under the
# minimal-implementation.md:24-26 carve-out for annotated wire-format constants.
SIGN_SLIDER = {v: k for k, v in SLIDER_SIGN.items()}
# The secondary (blend) heights, by component. Their primary counterparts are in COMPONENTS.
# Source: docs/HakenMidi.h:1335-1344 idHeightW2, idVBegX2..idVEndZ2.
SECONDARY_SLIDERS = {"W": (73,), "X": (75, 76), "Y": (77, 78), "Z": (79, 80)}

COMPONENTS = {
    "W": {"mode": 40, "magnitude": 41, "slider": 42, "slider2": 73, "modifier": 66, "macro": 67},
    "X": {"begin": 43, "end": 49, "multiplier": 1, "mode": 4, "height_begin": 45,
          "height_end": 46, "macro": 27, "transfer": 85},
    "Y": {"begin": 53, "end": 54, "multiplier": 2, "mode": 5, "height_begin": 51,
          "height_end": 52, "macro": 28, "transfer": 55},
    "Z": {"begin": 60, "end": 61, "multiplier": 3, "mode": 6, "height_begin": 58,
          "height_end": 59, "macro": 29, "transfer": 62},
}

# Every id the s_Form_Poke definitions name, as the header spells it. 79 entries.
# Source: docs/HakenMidi.h:1157-1352, the id DEFINITIONS - not the SSL_Form_Poke name list at
# :241-257, whose own "stream 19 id 114" comment is off by one over its last row and so puts
# SgM at 118 instead of 117 (idSgM = 117 at :1199, idLoW = 118 at :1221, idHiW = 119 at :1222,
# idHBegBl = 121 at :1330, idHEndBl = 123 at :1331). That list also carries the typo
# "AnvVal2" for idAncVal2 (:1293). Sparse id space -> dict keyed by the wire id.
FORM_POKE_NAMES = {
    1: "MultX", 2: "MultY", 3: "MultZ", 4: "InitX", 5: "InitY", 6: "InitZ", 7: "AncDom",
    8: "AncLookup", 9: "AncLimit", 10: "AncNN", 11: "AncTAorAll", 12: "TransBl", 13: "NegW",
    14: "NegW2", 15: "NegBegX", 16: "NegBegX2", 17: "NegEndX", 18: "NegEndX2", 19: "NegBegY",
    20: "NegBegY2", 21: "NegEndY", 22: "NegEndY2", 23: "NegBegZ", 24: "NegBegZ2", 25: "NegEndZ",
    26: "NegEndZ2", 27: "XMacr", 28: "YMacr", 29: "ZMacr", 38: "FormOp", 39: "Blend", 40: "SgW",
    41: "MultW", 42: "HeightW", 43: "HBegX", 44: "ZeroX", 45: "VBegX", 46: "VEndX", 48: "Interp",
    49: "HEndX", 50: "ShapeW", 51: "VBegY", 52: "VEndY", 53: "HBegY", 54: "HEndY", 55: "TransY",
    56: "AncOp", 57: "AncVal", 58: "VBegZ", 59: "VEndZ", 60: "HBegZ", 61: "HEndZ", 62: "TransZ",
    63: "Persist", 66: "ScaleW", 67: "SWMacr", 68: "BlMacForm", 73: "HeightW2", 75: "VBegX2",
    76: "VEndX2", 77: "VBegY2", 78: "VEndY2", 79: "VBegZ2", 80: "VEndZ2", 81: "Persist2",
    82: "Interp2", 85: "TransX", 96: "Reluct", 97: "Reluct2", 100: "AncOp2", 101: "AncVal2",
    112: "QuantX", 117: "SgM", 118: "LoW", 119: "HiW", 121: "BegBl", 123: "EndBl", 124: "AllW",
    125: "InitW",
}

# Ids decode() surfaces but encode_changes() cannot write: the ancillary formula, blend and
# the secondary (blend) values, the W zone, and the per-formula shaping settings. Read-only is
# deliberate this pass - the write surface is a tool-gap item, not a missing table - and the
# list is explicit so that "known" never quietly means "silently dropped": every id named here
# reaches the decoded result. Derived from the tables above, never re-literalled.
DECODE_ONLY_IDS = (
    {ANC_DOMAIN_ID, ANC_LOOKUP_ID, ANC_LIMIT_ID, ANC_TO_NN_ID, ANC_TOUCH_AREA_ID}
    | set(ANC_OP_IDS) | set(ANC_VALUE_IDS)
    | {BLEND_ID, BLEND_MACRO_FORM_ID, BLEND_TRANSFER_ID} | set(BLEND_SHELF_IDS)
    | {W_ZONE_LOW_ID, W_ZONE_HIGH_ID, W_ZONE_ALL_OCTAVES_ID, W_ZONE_FROM_INITIAL_ID}
    | {ZERO_X_ID, QUANTIZE_X_ID}
    | set(INTERPOLATION_IDS) | set(PERSISTENCE_IDS) | set(RELUCTANCE_IDS)
    | {i for ids in SECONDARY_SLIDERS.values() for i in ids}
    | {SLIDER_SIGN[i] for ids in SECONDARY_SLIDERS.values() for i in ids})

# Every stream-19 id this module accounts for, derived from the tables above so that adding an
# id to a table keeps the set correct. Anything outside it is reported by decode() in
# "unknown_ids" rather than dropped (codec-conventions.md:14-15: never raise, never drop).
KNOWN_IDS = ({i for c in COMPONENTS.values() for i in c.values()}
             | set(SLIDER_SIGN) | set(SLIDER_SIGN.values())
             | {OPERATOR_ID, SG_SHAPE_ID, SG_PHASE_ID}
             | DECODE_ONLY_IDS)


# Sign/height semantics. docs/HakenMidi.h:1201-1202 (idNegW "true for -idHeightW; no effect until
# idHeightW received", idHeightW "height for W with idNegW -1.00..1.27 in 0.01 steps"), and the
# same pair per component at :1227-1230, :1242-1246, :1265-1268. The header gives the RANGE but
# never the magnitude formula, so the reading below is not a misread spec.
# Settled 2026-10-26: the Neg flag is an OFFSET, not a sign-and-magnitude bit - a flag-set raw r
# means r/100 - 1.00. Re-measured over all 668 factory presets (Editor 1081 SysPresets) [C]:
# flag-set writes span raw 1..99 and never reach 100, while flag-clear writes run to 127; and 564
# writes set the flag with the height id absent (= raw 0), which is -1.00 under this reading and
# a pointless -0.00 under the mirror reading. NOT yet confirmed by ear on the device
# (ROADMAP.md "Verify a NEGATIVE formula height on the device").
def slider_value(raw: int, sign_bit: int) -> float:
    return round(raw / 100 - 1.0, 2) if sign_bit else round(raw / 100, 2)


def slider_encode(value: float, max_value: float = 1.27) -> tuple[int, int]:
    """value -> (neg_flag, raw). W allows up to 1.27, X/Y/Z heights up to 1.0."""
    if not -1.0 <= value <= max_value:
        raise ValueError(f"value must be within -1 .. {max_value}")
    value = round(value, 2)   # the wire steps by 0.01; -0.001 is -0.00 = zero, not raw 100
    if value < 0:
        return 1, round((value + 1.0) * 100)
    return 0, round(value * 100)


def _get(lst, i):
    return lst[i] if 0 <= i < len(lst) else f"?{i}"


def slider_from_pairs(pairs: dict[int, int], slider_id: int) -> float | None:
    """One height, read with its sign id. None when the formula does not set it at all.

    Orphan Neg flag: the flag set with its height id absent means raw 0, i.e. -1.00 - the only
    encoding of -1.00. 564 such orphan flags across the 668 factory presets [C]. The file
    decoder in preset_file.py reads heights through here too, so there is one reading.
    """
    sign = pairs.get(SLIDER_SIGN[slider_id], 0)
    if slider_id in pairs:
        return slider_value(pairs[slider_id], sign)
    return slider_value(0, 1) if sign else None


def decode(pairs: dict[int, int]) -> dict:
    def sl(i):
        return slider_from_pairs(pairs, i)

    def magnitude(i):
        return _get(MAGNITUDES, pairs.get(i, MAGNITUDE_DEFAULT) & 7)

    w = COMPONENTS["W"]
    out = {
        "W": {
            "mode": _get(W_MODES, pairs.get(w["mode"], 0) & 15),
            "value": sl(w["slider"]),
            "magnitude": magnitude(w["magnitude"]),
            "modifier": _get(W_MODIFIERS, pairs.get(w["modifier"], 0) & 63),
            "macro": _get(MACROS, pairs.get(w["macro"], 0)),
            "sg_shape": _get(SG_SHAPES, pairs.get(SG_SHAPE_ID, 0)),
            "sg_phase": _get(SG_PHASES, pairs.get(SG_PHASE_ID, 0)),
        }
    }
    for name in "XYZ":
        c = COMPONENTS[name]
        modes = Z_MODES if name == "Z" else XYZ_MODES
        hb, he = sl(c["height_begin"]), sl(c["height_end"])
        out[name] = {
            "active": bool(hb) or bool(he),
            "height_begin": hb, "height_end": he,
            "range_begin_raw": pairs.get(c["begin"]), "range_end_raw": pairs.get(c["end"]),
            "multiplier": magnitude(c["multiplier"]),
            "mode": _get(modes, pairs.get(c["mode"], 0) & 7),
            "transfer": _get(X_TRANSFER if name == "X" else YZ_TRANSFER,
                             pairs.get(c["transfer"], TRANSFER_DEFAULT[name])),
            "macro": _get(["none"] + MACROS, pairs.get(c["macro"], 0)),
        }
    w_on = out["W"]["value"] not in (None, 0)
    out["W"]["active"] = w_on
    out["operator"] = _get(OPERATORS, pairs.get(OPERATOR_ID, 0))
    out["w_zone"] = {
        "low_nn": pairs.get(W_ZONE_LOW_ID), "high_nn": pairs.get(W_ZONE_HIGH_ID),
        "every_octave": bool(pairs.get(W_ZONE_ALL_OCTAVES_ID, 0)),
        "from_initial_pitch": bool(pairs.get(W_ZONE_FROM_INITIAL_ID, 0)),
    }
    out["ancillary"] = {
        "op": _get(ANC_OPS, pairs[ANC_OP_IDS[0]]) if ANC_OP_IDS[0] in pairs else None,
        "value": _get(ANC_VALUES, pairs[ANC_VALUE_IDS[0]]) if ANC_VALUE_IDS[0] in pairs else None,
        "op2": _get(ANC_OPS, pairs[ANC_OP_IDS[1]]) if ANC_OP_IDS[1] in pairs else None,
        "value2": _get(ANC_VALUES, pairs[ANC_VALUE_IDS[1]]) if ANC_VALUE_IDS[1] in pairs else None,
        "domain": _get(ANC_DOMAINS, pairs.get(ANC_DOMAIN_ID, 0)),
        "lookup": _get(ANC_LOOKUPS, pairs.get(ANC_LOOKUP_ID, 0)),
        "column_limiter": bool(pairs.get(ANC_LIMIT_ID, 0)),
        "to_note_number": bool(pairs.get(ANC_TO_NN_ID, 0)),
        "touch_area_or_all_fingers": bool(pairs.get(ANC_TOUCH_AREA_ID, 0)),
    }
    out["blend"] = {
        "control": _get(BLEND_CONTROLS, pairs.get(BLEND_ID, 0)),
        "macro_or_formula_raw": pairs.get(BLEND_MACRO_FORM_ID, 0),
        "transfer": _get(YZ_TRANSFER, pairs.get(BLEND_TRANSFER_ID, 0)),
        "shelf_begin_raw": pairs.get(BLEND_SHELF_IDS[0]),
        "shelf_end_raw": pairs.get(BLEND_SHELF_IDS[1]),
    }
    secondary: dict = {
        "persistence_raw": pairs.get(PERSISTENCE_IDS[1]),
        "interpolation_raw": pairs.get(INTERPOLATION_IDS[1]),
        "reluctance_raw": pairs.get(RELUCTANCE_IDS[1]),
    }
    for name, ids in SECONDARY_SLIDERS.items():
        if name == "W":
            secondary[name] = {"value": sl(ids[0])}
        else:
            secondary[name] = {"height_begin": sl(ids[0]), "height_end": sl(ids[1])}
    out["secondary"] = secondary
    out["shaping"] = {
        "zero_x_nn": pairs.get(ZERO_X_ID), "quantize_x_raw": pairs.get(QUANTIZE_X_ID),
        "interpolation_raw": pairs.get(INTERPOLATION_IDS[0]),
        "persistence_raw": pairs.get(PERSISTENCE_IDS[0]),
        "reluctance_raw": pairs.get(RELUCTANCE_IDS[0]),
    }
    out["unknown_ids"] = {k: v for k, v in pairs.items() if k not in KNOWN_IDS}
    if out["unknown_ids"]:
        out["warning"] = (f"stream-19 ids not decoded: {sorted(out['unknown_ids'])}; "
                          "their raw values are in unknown_ids")
    return out


# The all-default formula: decode() applies the per-id defaults and nothing else, so decoding
# the empty pair set IS the formula a preset inherits when it writes no s_Form_Poke id at all.
# summary() reads it to tell "set to the default" apart from "not set". preset_file.py computes
# the same object a second time as its own DEFAULT_FORMULA (used there for the catalog's
# compression rule); the two should become one reference.
DEFAULT_FORMULA = decode({})


def _settings(section: dict, default: dict, path: str) -> list[str]:
    """`path.key=value` for each leaf of one decoded section that is not the default."""
    out = []
    for key, value in section.items():
        if key == "active":
            continue
        if isinstance(value, dict):
            out += _settings(value, default[key], f"{path}{key}.")
        elif value is not None and value != default[key]:
            out.append(f"{path}{key}={value}")
    return out


def summary(d: dict) -> str:
    """One line for a human. A formula with no active W/X/Y/Z may still be doing work - its
    content can sit on the secondary (blend) sliders, the ancillary operations or W's shaping
    ids, as 19 of the 563 formula letters in the shipped wiring blocks do - so when the four
    primary components render nothing, report everything the formula sets instead. Only a
    formula equal to DEFAULT_FORMULA is called empty."""
    parts = []
    w = d["W"]
    if w["active"]:
        s = f"W = {w['mode']} {w['value']} x {w['magnitude']}"
        if w["mode"].startswith("SG"):
            s += f" [shape {w['sg_shape']}" + (f", phase {w['sg_phase']}]" if w["sg_phase"] != "Off" else "]")
        if w["modifier"] != "x 1":
            s += f" {w['modifier']}" + (f" ({w['macro']})" if "Macro" in w["modifier"] else "")
        parts.append(s)
    for n in "XYZ":
        c = d[n]
        if c["active"]:
            parts.append(f"{n} = {c['mode']} {c['height_begin']}->{c['height_end']} x {c['multiplier']}")
    if not parts:
        sections = ("W", "X", "Y", "Z", "w_zone", "ancillary", "blend", "secondary", "shaping")
        settings = [text for name in sections
                    for text in _settings(d[name], DEFAULT_FORMULA[name], f"{name}.")]
        if d.get("unknown_ids"):
            settings.append(f"unknown_ids={sorted(d['unknown_ids'])}")
        if settings:
            parts = ["no active component, but " + ", ".join(settings)]
    body = " ; ".join(parts) or "(all components zero)"
    return f"[{d.get('operator', 'W + X + Y + Z')}] " + body


def _magnitude_index(value) -> int:
    for i, m in enumerate(MAGNITUDES):
        if abs(float(value) - m) < 1e-9:
            return i
    raise ValueError(f"magnitude must be one of {MAGNITUDES}")


def _index(options: list, value, what: str) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        if not 0 <= value < len(options):
            raise ValueError(f"{what} index out of range")
        return value
    for i, o in enumerate(options):
        if str(o).lower() == str(value).lower():
            return i
    raise ValueError(f"unknown {what} {value!r}; options: {options}")


def encode_changes(component: str, **kw) -> list[tuple[int, int]]:
    """Build (id, value) pairs for one component. Only given fields are encoded.
    W: mode, value, magnitude, modifier, macro, sg_shape, sg_phase
    X/Y/Z: height_begin, height_end, multiplier, mode, transfer, macro

    W mode "RMS of row" (wire 13) carries a device constraint the wire cannot express:
    only ONE formula may sit in a matrix RMS row in W. 34 factory formulas use it.
    The ancillary, blend, secondary, W-zone and shaping ids are decode-only
    (formula.DECODE_ONLY_IDS); nothing here writes them."""
    c = component.upper()
    ids = COMPONENTS[c]
    out: list[tuple[int, int]] = []

    w_sliders = (COMPONENTS["W"]["slider"], COMPONENTS["W"]["slider2"])

    def slider(sid, v):
        # Only W reaches 1.27 (docs/HakenMidi.h:1202); X/Y/Z heights cap at 1.00.
        sign, raw = slider_encode(float(v), 1.27 if sid in w_sliders else 1.0)
        out.extend([(SLIDER_SIGN[sid], sign), (sid, raw)])

    if c == "W":
        if kw.get("mode") is not None:
            out.append((ids["mode"], _index(W_MODES, kw["mode"], "W mode")))
        if kw.get("value") is not None:
            slider(ids["slider"], kw["value"])
        if kw.get("magnitude") is not None:
            out.append((ids["magnitude"], _magnitude_index(kw["magnitude"])))
        if kw.get("modifier") is not None:
            out.append((ids["modifier"], _index(W_MODIFIERS, kw["modifier"], "modifier")))
        if kw.get("macro") is not None:
            out.append((ids["macro"], _index(MACROS, kw["macro"], "macro")))
        if kw.get("sg_shape") is not None:
            out.append((SG_SHAPE_ID, _index(SG_SHAPES, kw["sg_shape"], "SG shape")))
        if kw.get("sg_phase") is not None:
            out.append((SG_PHASE_ID, _index(SG_PHASES, str(kw["sg_phase"]), "SG phase")))
    else:
        if kw.get("height_begin") is not None:
            slider(ids["height_begin"], kw["height_begin"])
        if kw.get("height_end") is not None:
            slider(ids["height_end"], kw["height_end"])
        if kw.get("multiplier") is not None:
            out.append((ids["multiplier"], _magnitude_index(kw["multiplier"])))
        if kw.get("mode") is not None:
            modes = Z_MODES if c == "Z" else XYZ_MODES
            out.append((ids["mode"], _index(modes, kw["mode"], f"{c} mode")))
        if kw.get("transfer") is not None:
            table = X_TRANSFER if c == "X" else YZ_TRANSFER
            out.append((ids["transfer"], _index(table, kw["transfer"], f"{c} transfer")))
        if kw.get("macro") is not None:
            out.append((ids["macro"], _index(["none"] + MACROS, kw["macro"], f"{c} macro")))
    if c == "W" and kw.get("transfer") is not None:
        raise ValueError("transfer applies to X, Y or Z")
    if kw.get("operator") is not None:
        out.append((OPERATOR_ID, _index(OPERATORS, kw["operator"], "operator")))
    if not out:
        raise ValueError("nothing to change")
    return out
