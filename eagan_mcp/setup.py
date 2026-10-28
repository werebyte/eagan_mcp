"""Matrix config (stream 20 = s_Mat_Poke): oscillator slot types, bank types, shape generators.
Authoritative source since 10.81: docs/HakenMidi.h (shipped with the Haken Editor).

Source: Haken Editor 1044, HE Matrix.maxpat (rxMatCfg / txMatCfg).
Write: ch16 cc56=20 + poly pressure (id, value). Read: select any cell, the Module
sends stream 20 with all ids. Verified on the Module 2026-10-25 (osc type write)."""

# Osc slot type value -> name. From the Editor's menu value table
# "0 1 18 2 3 4 99 5 10 12 19 6 11 13 7 8 9 999 14 15 16 17".
OSC_TYPES = {
    0: "DSF Oscillator", 1: "Integrated DSF", 18: "PWM Oscillator", 2: "Jenny Oscillator",
    3: "Phase Generator", 4: "Noise from Seed",
    5: "Low Pass Filter", 10: "Shelving Low Pass", 12: "Single Pole Low Pass",
    19: "Ladder Low Pass", 6: "High Pass", 11: "Shelving High Pass",
    13: "Single Pole High Pass", 7: "Band Pass", 8: "Band Reject (Notch)", 9: "All Pass",
    14: "Signal Multiplier", 15: "Tanh", 16: "Bitcrusher", 17: "Pitch Shifter using Delay",
}
OSC_TYPE_IDS = [72, 73, 74, 75, 76]        # slot 1..5. Source: docs/HakenMidi.h:1507-1511
OSC_CASCADE_IDS = [77, 78, 79, 80, 81]     # filter cascade (menu: 1..4). :1535-1539
OSC_EXTREME_IDS = [82, 83, 84, 85, 86]     # 0 normal 1 kHz update, 1 extreme (sample rate). :1552

# What idOscFilOpt means depends on the slot's type (one id, five meanings).
# Source: docs/HakenMidi.h:1535-1551. Filter types LP..HP1 (wire 5..13) read it as a cascade
# count; the four other type families read it as their own variant selector.
OSC_CASCADE_VALUES = range(5, 14)
OSC_OPTIONS = {
    "cascade": ["no cascade", "cascade 2", "cascade 3", "cascade 4"],
    "PWM Oscillator": ["linear", "exponential"],
    "Phase Generator": ["sum of 7", "ramp up", "ramp down", "triangle"],
    "Jenny Oscillator": ["sharp decay", "smooth decay", "Hann decay", "no decay"],
    "Ladder Low Pass": ["transistor", "diode"],
}

# Bank types. Source: HakenMidi.h 10.81, s_Mat_Poke idBankA/B/C.
BANK_AB_TYPES = {0: "BiqBank", 1: "BiqGraph", 2: "BiqMouth", 3: "SineBank", 4: "SineSpray",
                 5: "WaveBank", 6: "HarMan", 7: "ModMan", 8: "CVC", 9: "Kinetic", 10: "Additive"}
# Bank C: delays, or an alias of Bank B's SineSpray/WaveBank/HarMan/CVC.
BANK_C_TYPES = {0: "VoiceDelay", 1: "SummedDelay", 2: "MicroDelay", 3: "FormulaDelay",
                4: "SineSpray (alias of B)", 5: "WaveBank (alias of B)", 6: "HarMan (alias of B)",
                8: "CVC (alias of B)"}
BANK_IDS = {"A": 91, "B": 92, "C": 93}
# Per-bank accessory selectors. Bank C shares Bank B's set, because a Bank C "alias of B"
# value means C is mirroring B's module. Source: docs/HakenMidi.h:1591-1592 idBankParamA/B,
# :1576-1577 idBankAcm1/idBankBcm1, :1584-1585 idBankAcm2/idBankBcm2,
# :1600-1601 idBqExtA/idBqExtB (0..5 = 8..48 biquad modes, 6 = variable),
# :1603-1604 idSSetA/idSSetB.
BANK_PARAM_IDS = {"A": 99, "B": 98}
BANK_CM1_IDS = {"A": 95, "B": 94}
BANK_CM2_IDS = {"A": 97, "B": 96}
BQ_EXT_IDS = {"A": 70, "B": 71}
SPECTRAL_SET_IDS = {"A": 64, "B": 65}
# Spectral set for a HarMan / ModMan bank, 38 entries. Source: docs/HakenMidi.h:1605-1619,
# Live = 0 .. ss_Crystal = 37 (nSSet terminates the list).
SPECTRAL_SETS = [
    "Live", "Bell", "Drum", "KalimbaHard", "KalimbaSoft", "MarimbaHard", "MarimbaSoft",
    "mBiraski", "Metal", "Sprong", "Noise1", "Noise2", "StringTap1", "StringTap2",
    "StringTap3", "ViolaLegato", "ViolaMarcato", "PizzicatoLoud", "PizzicatoSnap",
    "PizzicatoSoft", "SpiccatoLoud", "SpiccatoSoft", "AltoFlute", "AltoSax", "Brass",
    "Clarinet1", "Clarinet2", "Flute1", "Flute2", "Oboe1", "Oboe2", "Ukulele1",
    "Ukulele2", "Ukulele3", "ToyPiano1Strike", "ToyPiano1Release", "ToyPiano2Strike",
    "Crystal",
]
# The same ids select an analysis decade when the bank is Additive.
# Source: docs/HakenMidi.h:1620-1625 addM = 0 .. add4thDecade = 4.
ADDITIVE_SETS = ["Mahling Phrase", "Decade 1", "Decade 2", "Decade 3", "Decade 4"]
# idBankParamA/B when the bank is WaveBank. Source: docs/HakenMidi.h:1594-1597 wave_saw = 0.
WAVE_NAMES = ["sawtooth", "square", "triangle", "LeCaine square"]

# Recirculator (the shared effect the Master columns reach).
# Source: docs/HakenMidi.h:1479-1487 idReciType, R_shortRev = 0 .. R_longRev = 6, R_mask = 0x7.
RECI_TYPE_ID = 62
RECI_TYPE_MASK = 0x7
RECI_TYPES = ["Short Reverb", "Modulated Delay", "Swept Echo", "Analog Echo",
              "Digital Echo LPF", "Digital Echo HPF", "Long Reverb"]

# What matrix rows 9/10 and 11/12 actually carry in this preset. A static row table is wrong
# for 3 of 18 captured presets without these two selectors.
# Source: docs/HakenMidi.h:1634-1637 idRowTyp1 (rt1Aud/rt1Tap/rt1AudTap) and
# :1638-1643 idRowTyp2 (rt2Sub/rt2Tap/rt2SubTap/rt2Aud/rt2AudTap).
ROW_TYPE1_ID = 106
ROW_TYPES1 = ["Audio L/R", "Tap 1/Tap 2", "Mono Audio + Mono Tap 1+2"]
ROW_TYPE2_ID = 107
ROW_TYPES2 = ["Submix L/R", "Tap 3/Tap 4", "Mono Submix + Mono Tap 3+4", "Audio L/R",
              "Mono Audio + Mono Tap 3+4"]

# Delay time select: the delay line length is 50 ms * 2^n.
# Source: docs/HakenMidi.h:1632 idTimeSel.
DELAY_TIME_SEL_ID = 105

# Assignable Master columns 2..7 (since 10.60): ids 27..32 select what each column drives.
MASTER_COL_IDS = [27, 28, 29, 30, 31, 32]
MASTER_COL_TARGETS = {0: "Recirc R1", 1: "Recirc R2", 2: "Recirc R3", 3: "Recirc R4", 4: "Recirc R5",
                      5: "Recirc R6", 6: "Recirc Mix", 7: "Pre level", 8: "Comp Thresh / Tanh Drive",
                      9: "Comp Attack", 10: "Comp Ratio / Tanh Makeup", 11: "Comp/Tanh Mix",
                      12: "Post level", 13: "EQ Tilt", 14: "EQ Freq", 15: "EQ Mix",
                      16: "Conv 1 Interp", 17: "Conv 1 Mix", 18: "Conv 2 Interp", 19: "Conv 2 Mix"}

# Polyphony (s_Mat_Poke): base polyphony 1..8, expanded (+) flag, double computation rate (^).
POLY_ID = 39
BEND_RANGE_ID = 40  # 1..96 = all channels; 95+n = "96:n" (MPE 96, ch1 +-n)


def bend_range_label(v):
    """None when the Module did not send id 40 (it usually does not without a reload)."""
    if v is None:
        return None
    return f"96:{v - 95}" if v > 96 else f"{v} (all channels)"
OK_EXP_POLY_ID = 11
OK_INC_COMP_ID = 5

# Source: docs/HakenMidi.h:1623-1631 idSgTyp1..5, "two bits shape generator type".
SG_TYPES = ["Continuous Cycle", "Single Cycle", "Phase from Matrix Row", "Dual (W trigger, single cycle)"]
SG_IDS = [100, 101, 102, 103, 104]         # SG1..SG5, value & 3
SG_TYPE_MASK = 0x3

# Every id the s_Mat_Poke definitions name, as the header spells it. 98 entries, sparse ->
# dict keyed by the wire id. Source: docs/HakenMidi.h:261-281 SSL_Mat_Poke (whose id labels
# all line up, unlike SSL_Form_Poke's last row), cross-checked against the definitions at
# :1357-1663. Read by preset_file.py, which reports the ids a preset file actually set.
MAT_POKE_NAMES = {
    1: "SplitMode", 2: "NoteMode", 3: "ReciCol1", 4: "ReciCol2", 5: "OkIncComp", 6: "Prio",
    7: "SwTogInst", 8: "OctBtn", 9: "Reverse", 10: "RoundMode", 11: "OkExpPoly", 12: "Action",
    13: "Aes3", 15: "RecircDisab", 16: "CompOpt", 17: "MinY", 18: "MaxY", 19: "MinZ", 20: "MaxZ",
    21: "OutEnc1", 22: "OutEnc2", 23: "OutMin1", 24: "OutMax1", 25: "OutMin2", 26: "OutMax2",
    27: "MastCol1", 28: "MastCol2", 29: "MastCol3", 30: "MastCol4", 31: "MastCol5",
    32: "MastCol6", 35: "Program", 36: "Routing", 37: "LegacyCh1", 38: "OctY", 39: "Poly",
    40: "BendRange", 41: "Yencode", 42: "Zlegacy", 43: "Zencode", 44: "MiddleC", 45: "SplitPoint",
    46: "MonoFunc", 48: "MonoInterv", 52: "Pedal1", 53: "Pedal2", 54: "JackShift",
    56: "PreservSurf", 57: "PreservPed", 58: "PreservEncod", 59: "ConfigToMidi", 60: "TArea",
    61: "MiniI2C", 62: "ReciType", 63: "CvcCfg", 64: "SSetA", 65: "SSetB", 70: "BqExtA",
    71: "BqExtB", 72: "OscFilTyp1", 73: "OscFilTyp2", 74: "OscFilTyp3", 75: "OscFilTyp4",
    76: "OscFilTyp5", 77: "OscFilOpt1", 78: "OscFilOpt2", 79: "OscFilOpt3", 80: "OscFilOpt4",
    81: "OscFilOpt5", 82: "FilExtrm1", 83: "FilExtrm2", 84: "FilExtrm3", 85: "FilExtrm4",
    86: "FilExtrm5", 91: "BankA", 92: "BankB", 93: "BankC", 94: "BankBcm1", 95: "BankAcm1",
    96: "BankBcm2", 97: "BankAcm2", 98: "BankParamB", 99: "BankParamA", 100: "SgTyp1",
    101: "SgTyp2", 102: "SgTyp3", 103: "SgTyp4", 104: "SgTyp5", 105: "TimeSel", 106: "RowTyp1",
    107: "RowTyp2", 108: "AliasDelay", 109: "ShortAudioQ", 110: "Forbid102", 111: "TrsAllDat",
    125: "Atten", 126: "FromAnlys", 127: "ToAnlys",
}


def _name(table, value):
    """Wire value -> name, with an unknown value kept visible instead of raised or dropped."""
    if value is None:
        return None
    if isinstance(table, dict):
        return table.get(value, f"?{value}")
    return table[value] if 0 <= value < len(table) else f"?{value}"


def osc_option_name(type_value: int | None, raw: int | None):
    """idOscFilOpt decoded for the slot's type; the raw value when the type gives it no table."""
    if raw is None or type_value is None:
        return raw
    if type_value in OSC_CASCADE_VALUES:
        return _name(OSC_OPTIONS["cascade"], raw)
    table = OSC_OPTIONS.get(OSC_TYPES.get(type_value, ""))
    return _name(table, raw) if table else raw


def bank_param_name(type_name: str | None, raw: int | None):
    """idBankParamA/B: a waveform for WaveBank, otherwise the biquad deflate/IIT setting."""
    if raw is None:
        return None
    if type_name == "WaveBank":
        return _name(WAVE_NAMES, raw)
    return "IIT" if raw == 8 else f"deflate {raw}"


def decode(pairs: dict[int, int]) -> dict:
    def osc(i):
        v = pairs.get(OSC_TYPE_IDS[i])
        return {"slot": i + 1, "type": OSC_TYPES.get(v, f"?{v}"),
                "cascade_raw": pairs.get(OSC_CASCADE_IDS[i]),
                "option": osc_option_name(v, pairs.get(OSC_CASCADE_IDS[i])),
                "extreme_rate": bool(pairs.get(OSC_EXTREME_IDS[i], 0))}

    def bank(name):
        v = pairs.get(BANK_IDS[name])
        table = BANK_C_TYPES if name == "C" else BANK_AB_TYPES
        return table.get(v, f"?{v}")

    def bank_params(name):
        """Bank A's own accessories, or the set Bank B and Bank C share."""
        type_name = bank("B" if name == "B" else name)
        spectral = pairs.get(SPECTRAL_SET_IDS[name])
        sets = ADDITIVE_SETS if type_name == "Additive" else SPECTRAL_SETS
        return {
            "param_raw": pairs.get(BANK_PARAM_IDS[name]),
            "param": bank_param_name(type_name, pairs.get(BANK_PARAM_IDS[name])),
            "column_mode_1_raw": pairs.get(BANK_CM1_IDS[name]),
            "column_mode_2_raw": pairs.get(BANK_CM2_IDS[name]),
            "biquad_size_raw": pairs.get(BQ_EXT_IDS[name]),
            "spectral_set_raw": spectral,
            "spectral_set": _name(sets, spectral),
        }

    return {
        "polyphony": {"base": pairs.get(POLY_ID),
                      "expanded_plus": bool(pairs.get(OK_EXP_POLY_ID, 0)),
                      "double_computation_rate": bool(pairs.get(OK_INC_COMP_ID, 0))},
        "bend_range": bend_range_label(pairs.get(BEND_RANGE_ID)),
        "master_columns": {2 + i: MASTER_COL_TARGETS.get(pairs.get(mid), f"?{pairs.get(mid)}")
                           for i, mid in enumerate(MASTER_COL_IDS)},
        "oscillators": [osc(i) for i in range(5)],
        "banks": {n: bank(n) for n in "ABC"},
        "bank_params": {n: bank_params(n) for n in ("A", "B")},
        "shape_generators": [
            {"sg": i + 1, "type": SG_TYPES[pairs.get(SG_IDS[i], 0) & SG_TYPE_MASK]}
            for i in range(5)],
        "recirculator": _name(RECI_TYPES, pairs.get(RECI_TYPE_ID, 0) & RECI_TYPE_MASK),
        # Which signal matrix rows 9..12 carry in THIS preset. matrix_map's static table is
        # the generic layout; a labelling join needs these two.
        "row_types": {"audio_rows_9_10": _name(ROW_TYPES1, pairs.get(ROW_TYPE1_ID, 0)),
                      "submix_rows_11_12": _name(ROW_TYPES2, pairs.get(ROW_TYPE2_ID, 0))},
        "delay_time_select_raw": pairs.get(DELAY_TIME_SEL_ID),
    }


def osc_type_value(name: str) -> int:
    for v, n in OSC_TYPES.items():
        if n.lower() == name.lower() or n.lower().startswith(name.lower()):
            return v
    raise ValueError(f"unknown oscillator type {name!r}; options: {list(OSC_TYPES.values())}")


def bank_type_value(bank: str, name: str) -> int:
    table = BANK_C_TYPES if bank.upper() == "C" else BANK_AB_TYPES
    for i, n in table.items():
        if n.lower() == name.lower() or n.lower().split(" (")[0] == name.lower():
            if bank.upper() == "A" and i == 8:
                raise ValueError("CVC is only available in bank B/C")
            return i
    raise ValueError(f"unknown type {name!r} for bank {bank}; options: {table}")


def sg_type_value(name: str) -> int:
    for i, n in enumerate(SG_TYPES):
        if n.lower().startswith(name.lower()):
            return i
    raise ValueError(f"unknown SG type {name!r}; options: {SG_TYPES}")
