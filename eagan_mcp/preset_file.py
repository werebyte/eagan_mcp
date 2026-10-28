"""Offline decoder for EaganMatrix preset .mid files, and the factory-catalog builder.

Standard library plus this package's wire tables, no device access. Reads a preset
"archive" .mid file and returns the logical preset: name, description, matrix, formulas,
setup, macros, graphs. `main()` walks a whole system-preset folder and writes the catalog.

THIS MODULE IS A CONSUMER OF THE CODEC LAYER, NOT A SECOND CODEC.
`formula.py` owns stream 19 (`s_Form_Poke`) and `setup.py` owns stream 20 (`s_Mat_Poke`):
every value table, default and sign reading comes from there, and nothing of the sort is
restated here (`codec-conventions.md:24-31`, one entry point per wire stream). That is not
tidiness. The earlier standalone version of this decoder and `formula.py` had both drifted
into the same two wrong readings - a mirrored negative height and an `idTransX` default of
Octaves - and a downstream script had grown local workarounds for them. Two copies of a
codec that disagree about what the device means are drift in evidence, not duplication.
`matrix_map.py` owns the row, column and cell-value names.

THE COMPRESSION RULE, which shapes every catalog field below:
`ccStore` saves a *compressed* preset - "only parameters that differ from default are
included; this is also true for archives" (docs/HakenMidi.h:478-480). An absent
`s_Mat_Poke` id means DEFAULT, not blank and not zero. Every setup field in the catalog is
therefore reported as `null` when the id was absent, never as a decoder's default-filled
value, and `setup_explicit_ids` lists exactly what the file set. A consumer that reads
`banks: {A: "BiqBank"}` without that distinction inverts the truth, because BiqBank is the
value a compressed preset never writes.
That is the FULL catalog's contract, and it is deliberately the awkward one: it keeps
"absent" readable. `build_shipped_catalog` is the other half. It applies the rule ONCE, at
build time, so the 25 fields of a shipped record are resolved type strings that are never
null - which is what stops every skill and knowledge document downstream from
re-implementing the rule, each with its own chance of inverting it.

Two file generations exist in the factory corpus and both are handled here:

  modern (246 of 668 factory files, firmware >= ~10.2x)
      ch16 only. Text and poke streams use ch16 polyKeyPres (two 7-bit sData per message)
      selected by ch16 cc56 (ccStream). The matrix uses ch16 cc40/41/42/43/44/45.
  legacy (422 of 668 factory files, firmware ~9.55 .. ~10.2x)
      ch16 channel pressure carries text one character per message; the matrix, the
      bank/setup block and the formulas live on **ch15** as bare cc, with cc numbers that
      partly equal the modern s_Form_Poke id numbers and partly pack two modern fields
      into one 7-bit value. See LEGACY_* below.

EVIDENCE
--------
Wire constants cite `docs/HakenMidi.h` (fw 10.81) at their definition. The LEGACY_* tables
are *derived*, not documented: established by differential decode against modern re-saves
of the same presets and then checked corpus-wide, as each one's comment records. Nothing
here is device-verified - this module never touches the Module.

ATTRIBUTION
-----------
Prior art: ref/cohem (codeberg pachde/cohem), MIT licence, Copyright (c) Paul Chase
Dempsey, ref/cohem/LICENSE.txt. Reused ideas, with thanks: the MThd/MTrk running-status
reader shape (src/midi_file.zig), the "sticky row/col + poke accumulator" state machine
(src/emc.zig onCh16Cc/onMessage), the "dirty id set" idea of treating an absent poke as
"default, omitted" rather than zero, and the SSL_* name tables being the natural lookup
tables. Two of its details are deliberately NOT reproduced: `src/emc.zig:1579-1588`
indexes cells as `(row * 60) + column` where `nCols` is 61, and its legacy
channel-pressure text path is annotated `// FW 1099` as though legacy were a *future*
firmware - leaning on that reading decodes 422 of the 668 factory files as empty. cohem
does not decode the legacy ch15 generation at all (`src/emc.zig` carries a
"TODO: old presets: ch14 == matrix" stub); that decode is derived here.
"""

import collections
import glob
import json
import os
import re
import struct
import sys
import unicodedata

from . import formula, matrix_map, setup

# ---------------------------------------------------------------- MIDI status

STATUS_NOTE_OFF = 0x80
STATUS_NOTE_ON = 0x90
STATUS_POLY_KEY_PRESSURE = 0xA0          # HakenMidi.h:93  polyKeyPres; carries sData pairs
STATUS_CONTROL_CHANGE = 0xB0             # HakenMidi.h:107 ctlChg
STATUS_PROGRAM_CHANGE = 0xC0             # HakenMidi.h:110 progChg
STATUS_CHANNEL_PRESSURE = 0xD0           # HakenMidi.h:116 chanPres
STATUS_PITCH_BEND = 0xE0

CHANNEL_CH1 = 0                          # HakenMidi.h:163 ch1
CHANNEL_CH2 = 1                          # HakenMidi.h:167 ch2
CHANNEL_LEGACY_CONFIG = 14               # ch15 1-based; legacy matrix/formula channel (derived)
CHANNEL_CH16 = 15                        # HakenMidi.h:170 ch16

# ------------------------------------------------------------- ch16 config cc

CC_BANK_H = 0                            # HakenMidi.h:380 ccBankH  category select
CC_BANK_L = 32                           # HakenMidi.h:467 ccBankL  preset# MSB
CC_FORM_SEL = 34                         # HakenMidi.h:614 ccFormSel
CC_FORM_COPY = 35                        # HakenMidi.h:615 ccFormCopy
CC_ROW = 40                              # HakenMidi.h:649 ccRow
CC_COL = 41                              # HakenMidi.h:668 ccCol
CC_MAT_DEC_LO = 42                       # HakenMidi.h:743 ccMatDecLo
CC_MAT_DEC_HI = 43                       # HakenMidi.h:745 ccMatDecHi
CC_MAT_VAL = 44                          # HakenMidi.h:747 ccMatVal
CC_MAT_OP = 45                           # HakenMidi.h:766 ccMatOp
CC_GRID = 51                             # HakenMidi.h:800 ccGrid
CC_STREAM = 56                           # HakenMidi.h:1074 ccStream
CC_ANLYS_SLOT = 57                       # HakenMidi.h:809 ccAnlysSlot
CC_VERS_HI = 102                         # HakenMidi.h:838 ccVersHi
CC_VERS_LO = 103                         # HakenMidi.h:839 ccVersLo
CC_CVC_HIGH = 104                        # HakenMidi.h:840 ccCVCHigh
CC_TASK = 109                            # HakenMidi.h:850 ccTask
CC_D_INFO = 110                          # HakenMidi.h:989 ccDInfo
CC_STORE = 112                           # HakenMidi.h:472 ccStore
CC_ARCH_CNT = 119                        # HakenMidi.h:1062 ccArchCnt
CC_FRAC_I_M48 = 86                       # HakenMidi.h:536 ccFracIM48
CC_FRAC_M49_M90 = 97                     # HakenMidi.h:537 ccFracM49M90

# ccDInfo values that bracket a preset archive in a .mid file. HakenMidi.h:1001-1011.
D_INFO_RETRIEVE_ARCH = 121               # cfRetrieveArch - archive begins
D_INFO_ARCHIVE_TO_FILE = 124             # archiveToFile - Editor stops recording, saves

# ccMatOp values seen in preset files. HakenMidi.h:348-367 SSL_ccMatOp.
MAT_OP_NAMES = {
    102: "matRedRefresh", 103: "matClrBankA", 104: "matClrBankB", 105: "matClrBankC",
    106: "colFloat", 107: "noFloat", 108: "formFloat", 109: "matNoRefresh",
    110: "nyqDis", 111: "nyqOff", 112: "nyqOn", 113: "thumbRefresh", 114: "matSendArrays",
    115: "matSelPosAlt", 116: "matBegPos", 117: "matHiliteWide", 118: "matHilite",
    119: "matNoHilite", 120: "matAtHilite", 121: "matTogMute", 122: "matSetMute",
    123: "matClrMute", 124: "matRefresh", 125: "matClear", 126: "matStart", 127: "matSelPos",
}
MAT_OP_CLEAR = 125
# ccCol ranges cleared by matClrBankA/B/C. HakenMidi.h:712-742 cA1..cC8.
MAT_OP_CLEAR_BANK = {103: (27, 35), 104: (35, 43), 105: (43, 51)}

# ---------------------------------------------------------------- streams

STREAM_NAME = 0                          # HakenMidi.h:1080 s_Name
STREAM_CON_TEXT = 1                      # HakenMidi.h:1082 s_ConText
STREAM_GRAPH = 2                         # HakenMidi.h:1084 s_Graph
STREAM_GRAPH_O1 = 3                      # HakenMidi.h:1086 s_GraphO1
STREAM_GRAPH_O2 = 4                      # HakenMidi.h:1087 s_GraphO2
STREAM_GRAPH_T0 = 5                      # HakenMidi.h:1089 s_GraphT0
STREAM_GRAPH_T1 = 6                      # HakenMidi.h:1090 s_GraphT1
STREAM_LOG = 7                           # HakenMidi.h:1095 s_Log
STREAM_FLOAT = 10                        # HakenMidi.h:1099 s_Float
STREAM_KINET = 11                        # HakenMidi.h:1101 s_Kinet
STREAM_BIQ_SIN = 12                      # HakenMidi.h:1103 s_BiqSin
STREAM_SYS = 13                          # HakenMidi.h:1105 s_Sys
STREAM_CONV = 14                         # HakenMidi.h:1113 s_Conv
STREAM_THUMB = 15                        # HakenMidi.h:1115 s_Thumb
STREAM_MACRO_HI = 16                     # HakenMidi.h:1123 s_MacroHi
STREAM_MACRO_LO = 17                     # HakenMidi.h:1126 s_MacroLo
STREAM_MACR_USES = 18                    # HakenMidi.h:1128 s_MacrUses
STREAM_FORM_POKE = 19                    # HakenMidi.h:1130 s_Form_Poke
STREAM_MAT_POKE = 20                     # HakenMidi.h:1132 s_Mat_Poke
STREAM_GRAPH_POKE = 21                   # HakenMidi.h:1134 s_Graph_Poke
STREAM_GRAPH_O1_POKE = 22                # HakenMidi.h:1135 s_GraphO1_Poke
STREAM_GRAPH_O2_POKE = 23                # HakenMidi.h:1136 s_GraphO2_Poke
STREAM_KINET_POKE = 24                   # HakenMidi.h:1137 s_Kinet_Poke
STREAM_BIQ_SIN_POKE = 25                 # HakenMidi.h:1139 s_BiqSin_Poke
STREAM_CONV_POKE = 26                    # HakenMidi.h:1141 s_Conv_Poke
STREAM_ANLYS_NAME = 27                   # HakenMidi.h:1143 s_AnlysName
STREAM_END = 127                         # HakenMidi.h:1149 s_StreamEnd

# HakenMidi.h:230-238 SSL_streams. Contiguous 0-based enumeration -> list.
STREAM_NAMES = [
    "Name", "ConText", "Graph", "GraphO1", "GraphO2", "GraphT0", "GraphT1", "Log", "UpdF2",
    "retiredDemoA", "Float", "Kinetic", "BiqSin", "Sys", "Conv", "Thumbnail", "MacroH",
    "MacroL", "MacrUses", "Form_Poke", "Mat_Poke", "Graph_Poke", "GraphO1_Poke",
    "GraphO2_Poke", "Kinet_Poke", "BiqSin_Poke", "Conv_Poke", "AnlysName", "UtilMinMax",
    "UtilData",
]

TEXT_STREAMS = (STREAM_NAME, STREAM_CON_TEXT, STREAM_LOG, STREAM_ANLYS_NAME)
# Streams whose sData is a positional array. The header states the Kinetic / BiqSin / Conv
# poke id assignments "correspond to the sData ordering" (HakenMidi.h:1667, 1727, 1786).
ARRAY_STREAMS = {
    STREAM_GRAPH: "graph", STREAM_GRAPH_O1: "graph_o1", STREAM_GRAPH_O2: "graph_o2",
    STREAM_GRAPH_T0: "pitch_trim_y0", STREAM_GRAPH_T1: "pitch_trim_y1",
    STREAM_KINET: "kinetic", STREAM_BIQ_SIN: "biq_sin", STREAM_CONV: "convolution",
    STREAM_MACRO_HI: "macro_hi", STREAM_MACRO_LO: "macro_lo", STREAM_THUMB: "thumbnails",
    STREAM_SYS: "system_info", STREAM_FLOAT: "float_debug", STREAM_MACR_USES: "macro_uses",
}
POKE_STREAM_TARGETS = {
    STREAM_GRAPH_POKE: "graph", STREAM_GRAPH_O1_POKE: "graph_o1",
    STREAM_GRAPH_O2_POKE: "graph_o2", STREAM_KINET_POKE: "kinetic",
    STREAM_BIQ_SIN_POKE: "biq_sin", STREAM_CONV_POKE: "convolution",
}

# ---------------------------------------- ch1/ch2 global cc (preset globals)

# HakenMidi.h:175-199 SSL_ch1_ch2. The header notes that on ch16 these cc "are reserved for
# preset files, but will be translated to ch1/ch2" (HakenMidi.h:177). Sparse -> dict.
GLOBAL_CC_NAMES = {
    1: "Mod", 2: "Breath", 4: "Foot", 7: "Vol", 8: "OctShift", 9: "MonoSw", 10: "FineTune",
    11: "Express", 12: "macro i", 13: "macro ii", 14: "macro iii", 15: "macro iv",
    16: "macro v", 17: "macro vi", 18: "Post", 19: "AudIn", 20: "Reci1", 21: "Reci2",
    22: "Reci3", 23: "Reci4", 24: "ReciMix", 25: "RoundRate", 26: "Pre", 27: "Atten",
    28: "RndIni", 29: "Jack1", 30: "Jack2", 31: "Advance",
    64: "Sus", 65: "Stretch", 66: "Sos", 67: "HpLevel", 68: "LineLevel", 69: "Sos2",
    70: "Actuation", 74: "Y", 76: "min1", 77: "max1", 78: "min2", 79: "max2",
    83: "EqTilt", 84: "EqFrq", 85: "EqMix", 88: "MSpL", 89: "MSpH", 90: "ThrDrv",
    91: "AtkCut", 92: "RatMkp", 93: "CoThMix", 95: "Reci5", 96: "Reci6",
}
MACRO_CC_I = 12                          # HakenMidi.h:540 ccI..ccVI = 12..17
MACRO_COUNT = 90                         # HakenMidi.h:1123 s_MacroHi: i..vi, m7..m90
MAX_14 = 0x3F80                          # HakenMidi.h:108 max14: 1.0 for 0..1 macros
ZERO_14 = 0x2000                         # HakenMidi.h:109 zero14: 0.0 for -1..1 macros

# ch16 cc that only a live device sends (status, not preset content). HakenMidi.h:200-229
# SSL_ch16 plus the definitions at HakenMidi.h:838-1072. Sparse -> dict.
CH16_STATUS_CC_NAMES = {
    36: "MacrUses", 37: "PedType", 46: "Neighbor", 47: "ModMatInd", 48: "ModMatVal",
    54: "CreaArch", 55: "CreaArchFin", 58: "(58)", 59: "MiniMicro_LB",
    71: "PolyTrad", 72: "PolyDsp", 73: "PolyCvc", 75: "Test", 80: "NHyst",
    104: "CVCHi", 105: "CVCMed", 106: "CVCLo", 107: "RxSNBN",
    111: "LedAesState", 113: "txSNBN", 114: "UsgDisp", 115: "LogDump", 116: "Ping",
    118: "Pong", 122: "CRC0", 123: "CRC1", 124: "CRC2", 125: "CRC3", 126: "CRC4",
}

# -------------------------------------------- legacy (ch15) formula unpacking

POLY_BASE_MASK = 63                      # idPoly carries the base count in its low 6 bits
LEGACY_POLY_EXPANDED_BIT = 64            # derived: legacy ch16 cc39 bit 6 is the "+" flag

_W = formula.COMPONENTS["W"]
# Derived, not in the header: the legacy ch15 generation packs several modern s_Form_Poke
# ids into one 7-bit cc value. Each entry maps a legacy ch15 cc to the modern ids it carries,
# as (modern_id, bit_shift, bit_width). Established by differential decode against modern
# re-saves of the same presets (Bullroarer/Plutonium/Victrola/Soundboard and their "Wbl"/"2"
# twins) and confirmed corpus-wide: of 1881 occurrences of the packed cc 43/49/53/54/60/61,
# 1880 satisfy the field-width constraint.
LEGACY_W_SCALER = -1                     # sentinel target: see LEGACY_W_SCALER_MAX_MACRO
LEGACY_FORM_PACK = {
    39: ((formula.BLEND_MACRO_FORM_ID, 0, 3), (formula.BLEND_ID, 3, 4)),
    40: ((_W["mode"], 0, 4), (formula.W_ZONE_FROM_INITIAL_ID, 4, 1),
         (formula.W_ZONE_ALL_OCTAVES_ID, 5, 1)),
    41: ((_W["magnitude"], 0, 3), (LEGACY_W_SCALER, 3, 4)),
    43: ((43, 0, 4), (1, 4, 3)),              # HBegX, MultX
    49: ((49, 0, 4), (4, 4, 3)),              # HEndX, InitX
    53: ((53, 0, 4), (2, 4, 3)),              # HBegY, MultY
    54: ((54, 0, 4), (5, 4, 3)),              # HEndY, InitY
    56: ((56, 0, 4), (7, 4, 3)),              # AncOp, AncDom
    60: ((60, 0, 4), (3, 4, 3)),              # HBegZ, MultZ
    61: ((61, 0, 4), (6, 4, 3)),              # HEndZ, InitZ
}
# Legacy ch15 cc71 / cc72 are bitmasks of the seven primary / secondary Neg flags, most
# significant bit first: W, Xbegin, Xend, Ybegin, Yend, Zbegin, Zend.
LEGACY_NEG_MASK_PRIMARY = [13, 15, 17, 19, 21, 23, 25]
LEGACY_NEG_MASK_SECONDARY = [14, 16, 18, 20, 22, 24, 26]
LEGACY_CC_NEG_PRIMARY = 71
LEGACY_CC_NEG_SECONDARY = 72
# Legacy W scaler selector: 0 = none, 1..6 observed = ScaleW "x macro" with SWMacr 0..5.
LEGACY_W_SCALER_MAX_MACRO = 6
LEGACY_W_SCALER_MACRO_MODE = 1           # W_MODIFIERS index of "x Macro"
# Fields whose unpacked value equals the device default are suppressed, so that a legacy
# decode produces the same "defaults omitted" id set as a modern re-save of the preset
# (HakenMidi.h:473 "only parameters that differ from default are included").
# HEndX (49) and HEndZ (61) default to the right end of their range: across the 246 modern
# factory files neither is ever written as 12, while legacy files carry 12 in 42 and 77
# formulas respectively. HEndY (54) is different - modern files do write 12, 186 times.
LEGACY_SUPPRESS_DEFAULT = {
    1: formula.MAGNITUDE_DEFAULT, 2: formula.MAGNITUDE_DEFAULT,
    3: formula.MAGNITUDE_DEFAULT, _W["magnitude"]: formula.MAGNITUDE_DEFAULT,
    _W["macro"]: 0, 49: formula.H_MAX, 61: formula.H_MAX,
}
# Multiplier fields have a non-zero default, so an unpacked 0 is meaningful and is kept.
LEGACY_MULTIPLIER_TARGETS = (1, 2, 3, _W["magnitude"])
# Legacy ch15 cc57 (AncVal) carries idAncNN in bit 6: in both twin pairs that show it, a
# legacy value of 67 corresponds to a modern AncNN=1. Inferred, two observations.
LEGACY_ANC_VAL_NN_BIT = 64
# Legacy matrix cc on ch15 (derived; proven against the BiqMouth - Basic live capture).
LEGACY_CC_ROW = 102
LEGACY_CC_COL = 103
LEGACY_CC_MAT_VAL = 104
LEGACY_CC_MAT_OP = 110
LEGACY_CC_MAT_DEC_LO = 115
LEGACY_CC_MAT_DEC_HI = 116
LEGACY_CC_FORM_SEL = 34
# Legacy ccMatVal codes: matA'..matV' were added in 10.30 (HakenMidi.h:751), so every legacy
# code at or above matA' sits 22 lower than its modern equivalent.
LEGACY_MAT_VAL_SHIFT_FROM = 23
LEGACY_MAT_VAL_SHIFT = 22
# The legacy generation splits the single s_Mat_Poke id space across two channels, because
# the formula ids need the low cc numbers. Derived from the corpus (422 legacy files) and
# cross-checked against the 10.81 header's own value tables:
#   ch16 cc 34..63 before the first ccStream  -> s_Mat_Poke id 34..63
#       (id 42 Zlegacy matches its "only legal values 0,1,2,3,4,7,11,69,70,127" exactly;
#        id 44 MiddleC carries note numbers; id 45 SplitPoint note numbers; id 60 TArea
#        carries nnTOff=16 for "disabled"; ids 52/53 Pedal1/Pedal2 carry cc numbers)
#   ch15 cc 64..99 before the first ccFormSel -> s_Mat_Poke id 64..99
#       (ids 91/92/93 BankA/B/C in 0..10 and 94..99 column-mode/param selects in 0..8)
# ch15 cc 100 and above in that block are the matrix cc (102/103/104/110/115/116) or an
# unresolved older id space, and are returned raw.
LEGACY_MAT_CH16_RANGE = (34, 63)
LEGACY_MAT_CH15_RANGE = (64, 99)
# Legacy ids whose value carries an extra flag bit or an unresolved high field.
LEGACY_MAT_UNRESOLVED_IDS = (34, 47, 49, 61, 70, 71)


def _name(table: list | dict, value: int | None) -> str | None:
    """Look a wire value up in a table, rendering an unknown value as a visible marker."""
    if value is None:
        return None
    if isinstance(table, dict):
        return table.get(value, f"?{value}")
    return table[value] if 0 <= value < len(table) else f"?{value}"


# ----------------------------------------------------------- MIDI file reading

class PresetFileError(ValueError):
    """The file is not a readable single-track MIDI preset archive."""


def _read_var_len(data: bytes, pos: int) -> tuple[int, int]:
    acc = 0
    for _ in range(4):
        if pos >= len(data):
            raise PresetFileError("truncated variable-length quantity")
        byte = data[pos]
        pos += 1
        acc = (acc << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return acc, pos
    raise PresetFileError("variable-length quantity too large")


def read_midi_events(data: bytes) -> tuple[dict, list[tuple[int, int, int, int | None]]]:
    """Parse an SMF byte string into (header, [(channel, status, data1, data2)]).

    Handles running status and skips meta and sysex events.
    """
    if data[:4] != b"MThd":
        raise PresetFileError("not a MIDI file (no MThd)")
    header_size = struct.unpack_from(">I", data, 4)[0]
    fmt, track_count, division = struct.unpack_from(">HHH", data, 8)
    header = {"format": fmt, "tracks": track_count, "division": division}
    pos = 8 + header_size
    events: list[tuple[int, int, int, int | None]] = []
    for _ in range(track_count):
        if data[pos:pos + 4] != b"MTrk":
            raise PresetFileError("missing MTrk chunk")
        track_size = struct.unpack_from(">I", data, pos + 4)[0]
        pos += 8
        end = pos + track_size
        running_status = 0
        while pos < end:
            _delta, pos = _read_var_len(data, pos)
            first = data[pos]
            if first == 0xFF:
                pos += 2
                meta_len, pos = _read_var_len(data, pos)
                pos += meta_len
                continue
            if first in (0xF0, 0xF7):
                pos += 1
                sysex_len, pos = _read_var_len(data, pos)
                pos += sysex_len
                continue
            if first & 0x80:
                running_status = first
                pos += 1
            status = running_status & 0xF0
            channel = running_status & 0x0F
            data1 = data[pos]
            pos += 1
            data2 = None
            if status not in (STATUS_PROGRAM_CHANGE, STATUS_CHANNEL_PRESSURE):
                data2 = data[pos]
                pos += 1
            events.append((channel, status, data1, data2))
        pos = end
    return header, events


# ------------------------------------------------------------------ containers

def _decode_container(events: list[tuple[int, int, int, int | None]]) -> dict:
    """The ccDInfo markers that bracket a preset archive. HakenMidi.h:1001-1011."""
    markers = [v for ch, st, cc, v in events
               if ch == CHANNEL_CH16 and st == STATUS_CONTROL_CHANGE and cc == CC_D_INFO]
    arch = [v for ch, st, cc, v in events
            if ch == CHANNEL_CH16 and st == STATUS_CONTROL_CHANGE and cc == CC_ARCH_CNT]
    return {
        "markers": markers,
        "starts_with_retrieve_arch": bool(markers) and markers[0] == D_INFO_RETRIEVE_ARCH,
        "ends_with_archive_to_file": bool(markers) and markers[-1] == D_INFO_ARCHIVE_TO_FILE,
        "arch_count": arch[-1] if arch else None,
    }


def _firmware(cc16: dict[int, int]) -> dict | None:
    if CC_VERS_HI not in cc16 or CC_VERS_LO not in cc16:
        return None
    raw = (cc16[CC_VERS_HI] << 7) | cc16[CC_VERS_LO]
    return {"raw": raw, "text": f"{raw // 100}.{raw % 100:02d}"}


# -------------------------------------------------------------- matrix decoding

class _MatrixBuilder:
    """Sticky row/column matrix accumulator, as the wire format requires.

    ccRow and ccCol persist until changed; ccMatVal commits the currently selected cell;
    ccMatDecHi/ccMatDecLo supply the digits of a matDec value.
    """

    def __init__(self) -> None:
        self.row = 0
        self.col = 0
        self.dec_hi: int | None = None
        self.dec_lo: int | None = None
        self.cells: dict[tuple[int, int], dict] = {}

    def set_row(self, value: int) -> None:
        self.row = value

    def set_col(self, value: int) -> None:
        self.col = value

    def set_dec_hi(self, value: int) -> None:
        self.dec_hi = value

    def set_dec_lo(self, value: int) -> None:
        self.dec_lo = value

    def commit(self, raw: int) -> None:
        disabled = bool(raw & matrix_map.MAT_VALUE_MUTED_BIT)
        code = raw & ~matrix_map.MAT_VALUE_MUTED_BIT
        cell: dict = {
            "row": self.row,
            "row_name": matrix_map.row_name(self.row),
            "col": self.col,
            "col_name": matrix_map.col_name(self.col),
            "code": code,
            "disabled": disabled,
        }
        if code == matrix_map.MAT_VALUE_DECIMAL:
            hi = self.dec_hi or 0
            lo = self.dec_lo or 0
            cell["value"] = round(hi / 100.0 + lo / 10000.0, 4)
            cell["label"] = f"{cell['value']:.4f}".rstrip("0").rstrip(".")
        else:
            cell["label"] = matrix_map.value_label(code)
            cell["value"] = None
        if code == 0:
            self.cells.pop((self.row, self.col), None)
        else:
            self.cells[(self.row, self.col)] = cell
        self.dec_hi = None
        self.dec_lo = None

    def clear(self) -> None:
        self.cells.clear()

    def clear_cols(self, first: int, last: int) -> None:
        for key in [k for k in self.cells if first <= k[1] < last]:
            del self.cells[key]

    def result(self) -> list[dict]:
        return [self.cells[k] for k in sorted(self.cells)]


# ------------------------------------------------------------ formula decoding

def decode_formula(pairs: dict[int, int]) -> dict:
    """One formula's s_Form_Poke (stream 19) pairs, decoded by `formula.decode`.

    An absent id means "device default, omitted from the archive"
    (HakenMidi.h:473-476: a stored preset contains "only parameters that differ from
    default"), so defaults are applied rather than an absent id read as zero. Every such
    default belongs to `formula.decode` and none is re-applied here - including the
    per-component transfer function, whose single site is `formula.TRANSFER_DEFAULT`
    (absent idTransX means kHz, not Octaves). Two decoders restating one default is the
    drift F5 removed, so this function adds only the archive-specific views below.
    """
    out = formula.decode(pairs)
    out["pokes"] = {formula.FORM_POKE_NAMES.get(i, f"?{i}"): v for i, v in sorted(pairs.items())}
    out["unknown_pokes"] = {i: v for i, v in sorted(pairs.items())
                            if i not in formula.FORM_POKE_NAMES}
    return out


# -------------------------------------------------------------- setup decoding

def decode_setup(pairs: dict[int, int]) -> dict:
    """One preset's s_Mat_Poke (stream 20) pairs, decoded by `setup.decode`.

    `pokes` names what the file actually set; everything the file omitted is a device
    default the decoded view has filled in, so a catalog consumer must read `pokes` and not
    the filled view (see THE COMPRESSION RULE in the module docstring).
    """
    out = setup.decode(pairs)
    out["pokes"] = {setup.MAT_POKE_NAMES.get(i, f"?{i}"): v for i, v in sorted(pairs.items())}
    out["unknown_pokes"] = {i: v for i, v in sorted(pairs.items())
                            if i not in setup.MAT_POKE_NAMES}
    return out


# ------------------------------------------------------------- macros, graphs

def _decode_macros(hi: list[int], lo: list[int]) -> dict:
    """Macros i..vi (0..1, scaled by max14) and m7..m90 (-1..1, offset by zero14)."""
    out: dict[str, float] = {}
    for index in range(MACRO_COUNT):
        high = hi[index] if index < len(hi) else 0
        low = lo[index] if index < len(lo) else 0
        if not high and not low:
            continue
        raw = (high << 7) | low
        if index < 6:
            out[formula.MACROS[index]] = round(raw / MAX_14, 4)
        else:
            out[f"m{index + 1}"] = round((raw - ZERO_14) / ZERO_14, 4)
    return out


def _decode_pitch_trim(values: list[int]) -> list[dict]:
    """s_GraphT0/T1 triples: nn (multiple of 6, 0 terminates), lo, hi. HakenMidi.h:1091-1094."""
    points = []
    for i in range(0, len(values) - 2, 3):
        nn = values[i]
        if nn == 0:
            break
        cents = (values[i + 2] << 7) | values[i + 1]
        points.append({"nn": nn, "cents_raw": cents, "cents": cents - 299})
    return points


def _decode_thumbnails(values: list[int]) -> list[dict]:
    """s_Thumb quads: formula#, lowest macro (127 = none), SG/Tap + FormOp, dim bits.

    HakenMidi.h:1115-1122.
    """
    out = []
    for i in range(0, len(values) - 3, 4):
        formula_number, macro, sg_op, dim = values[i:i + 4]
        if formula_number == 0:
            continue
        out.append({
            "formula": matrix_map.formula_letter(formula_number),
            "lowest_macro": None if macro == 127 else macro,
            "sg_or_tap": sg_op & 0x0F,
            "operator": _name(formula.OPERATORS, sg_op >> 4),
            "dim_z": bool(dim & 1), "dim_y": bool(dim & 2),
            "dim_x": bool(dim & 4), "dim_w": bool(dim & 8),
        })
    return out


# ----------------------------------------------------------- legacy ch15 block

def _legacy_unpack_formula(cc_values: dict[int, int]) -> tuple[dict[int, int], dict[int, int]]:
    """Map one legacy ch15 formula block to modern s_Form_Poke ids.

    Returns (modern_pairs, leftover) where leftover holds legacy cc this decoder does not
    account for.
    """
    pairs: dict[int, int] = {}
    leftover: dict[int, int] = {}
    anc_val_id = formula.ANC_VALUE_IDS[0]
    for cc, value in cc_values.items():
        if cc in LEGACY_FORM_PACK:
            for target, shift, width in LEGACY_FORM_PACK[cc]:
                field = (value >> shift) & ((1 << width) - 1)
                if target == LEGACY_W_SCALER:
                    if field == 0:
                        continue
                    pairs[_W["modifier"]] = LEGACY_W_SCALER_MACRO_MODE
                    if field <= LEGACY_W_SCALER_MAX_MACRO:
                        if field - 1:
                            pairs[_W["macro"]] = field - 1
                    else:
                        leftover[cc] = value
                elif field != LEGACY_SUPPRESS_DEFAULT.get(target) and (
                        field or target in LEGACY_MULTIPLIER_TARGETS):
                    pairs[target] = field
        elif cc == anc_val_id and value & LEGACY_ANC_VAL_NN_BIT:
            pairs[formula.ANC_TO_NN_ID] = 1
            pairs[anc_val_id] = value & ~LEGACY_ANC_VAL_NN_BIT
        elif cc == LEGACY_CC_NEG_PRIMARY:
            for bit, target in enumerate(LEGACY_NEG_MASK_PRIMARY):
                if value & (1 << (6 - bit)):
                    pairs[target] = 1
        elif cc == LEGACY_CC_NEG_SECONDARY:
            for bit, target in enumerate(LEGACY_NEG_MASK_SECONDARY):
                if value & (1 << (6 - bit)):
                    pairs[target] = 1
        elif cc in formula.FORM_POKE_NAMES:
            pairs[cc] = value
        else:
            leftover[cc] = value
    return pairs, leftover


def _parse_legacy(events: list[tuple[int, int, int, int | None]]) -> dict:
    """Parse the ch15 configuration block of a legacy preset file.

    Everything before the first ch15 ccFormSel is the matrix and an older setup id space;
    everything after it is formula data, one block per ccFormSel. Verified corpus-wide:
    across the 422 legacy factory files the two id groups never overlap except cc66.
    """
    matrix = _MatrixBuilder()
    formulas: dict[int, dict[int, int]] = {}
    mat_block: dict[int, int] = {}
    ch16_block: dict[int, int] = {}
    current: int | None = None
    mat_ops: list[int] = []
    stream_seen = False
    for channel, status, cc, value in events:
        if channel == CHANNEL_CH16 and status == STATUS_CONTROL_CHANGE:
            if cc == CC_STREAM:
                stream_seen = True
            elif not stream_seen and cc not in (CC_VERS_HI, CC_VERS_LO, CC_D_INFO):
                ch16_block[cc] = value
            continue
        if channel != CHANNEL_LEGACY_CONFIG or status != STATUS_CONTROL_CHANGE:
            continue
        if cc == LEGACY_CC_FORM_SEL:
            current = value
            formulas.setdefault(value, {})
            continue
        if current is not None:
            formulas[current][cc] = value
            continue
        if cc == LEGACY_CC_ROW:
            matrix.set_row(value)
        elif cc == LEGACY_CC_COL:
            matrix.set_col(value)
        elif cc == LEGACY_CC_MAT_DEC_HI:
            matrix.set_dec_hi(value)
        elif cc == LEGACY_CC_MAT_DEC_LO:
            matrix.set_dec_lo(value)
        elif cc == LEGACY_CC_MAT_VAL:
            code = value & ~matrix_map.MAT_VALUE_MUTED_BIT
            if code >= LEGACY_MAT_VAL_SHIFT_FROM:
                code += LEGACY_MAT_VAL_SHIFT
            matrix.commit(code | (value & matrix_map.MAT_VALUE_MUTED_BIT))
        elif cc == LEGACY_CC_MAT_OP:
            mat_ops.append(value)
            if value == MAT_OP_CLEAR:
                matrix.clear()
            elif value in MAT_OP_CLEAR_BANK:
                matrix.clear_cols(*MAT_OP_CLEAR_BANK[value])
        else:
            mat_block[cc] = value
    decoded: dict[str, dict] = {}
    legacy_leftover: dict[str, dict[int, int]] = {}
    for number, cc_values in sorted(formulas.items()):
        pairs, leftover = _legacy_unpack_formula(cc_values)
        letter = matrix_map.formula_letter(number)
        decoded[letter] = decode_formula(pairs)
        decoded[letter]["summary"] = formula.summary(decoded[letter])
        decoded[letter]["legacy_cc"] = dict(sorted(cc_values.items()))
        if leftover:
            legacy_leftover[letter] = leftover
    setup_pairs: dict[int, int] = {}
    raw_config: dict[str, int] = {}
    for source, (low, high) in ((ch16_block, LEGACY_MAT_CH16_RANGE),
                                (mat_block, LEGACY_MAT_CH15_RANGE)):
        for cc, value in sorted(source.items()):
            if low <= cc <= high and cc not in LEGACY_MAT_UNRESOLVED_IDS:
                setup_pairs[cc] = value
            else:
                raw_config[f"ch{16 if source is ch16_block else 15}_cc{cc}"] = value
    poly_raw = setup_pairs.get(setup.POLY_ID)
    if poly_raw is not None:
        setup_pairs[setup.POLY_ID] = poly_raw & POLY_BASE_MASK
        if poly_raw & LEGACY_POLY_EXPANDED_BIT:
            setup_pairs[setup.OK_EXP_POLY_ID] = 1
    decoded_setup = decode_setup(setup_pairs)
    decoded_setup["note"] = (
        "legacy generation: s_Mat_Poke ids 34..63 were read from ch16 cc before the first "
        "ccStream and ids 64..99 from ch15 cc before the first ccFormSel. Ids 100+ and the "
        "ids listed in LEGACY_MAT_UNRESOLVED_IDS are returned raw under "
        "unknown.legacy_config_cc. Shape-generator types and row types are not recoverable "
        "from a legacy file by this decoder.")
    return {
        "matrix": matrix.result(),
        "matrix_ops": mat_ops,
        "formulas": decoded,
        "setup": decoded_setup,
        "legacy_config_cc": raw_config,
        "legacy_formula_leftover": legacy_leftover,
    }


# ----------------------------------------------------------- modern ch16 block

def _parse_modern(events: list[tuple[int, int, int, int | None]]) -> dict:
    """Parse the ch16 stream/matrix block of a modern preset file (or a live capture)."""
    matrix = _MatrixBuilder()
    stream: int | None = None
    text: dict[int, bytearray] = {}
    arrays: dict[int, list[int]] = {}
    form_pairs: dict[int, dict[int, int]] = {}
    mat_pairs: dict[int, int] = {}
    poke_targets: dict[str, dict[int, int]] = {}
    current_formula: int | None = None
    mat_ops: list[int] = []
    cc16: dict[int, int] = {}
    globals_cc: dict[int, int] = {}
    device_status: dict[int, int] = {}
    unknown_messages: list[dict] = []
    preset_select: list[dict] = []

    def sdata(values: list[int]) -> None:
        if stream is None:
            unknown_messages.append({"what": "sData with no stream selected", "values": values})
        elif stream in TEXT_STREAMS:
            text.setdefault(stream, bytearray()).extend(values)
        elif stream in ARRAY_STREAMS:
            arrays.setdefault(stream, []).extend(values)
        elif stream == STREAM_FORM_POKE:
            if current_formula is None:
                unknown_messages.append({"what": "s_Form_Poke with no ccFormSel",
                                         "values": values})
            else:
                for i in range(0, len(values) - 1, 2):
                    form_pairs.setdefault(current_formula, {})[values[i]] = values[i + 1]
        elif stream == STREAM_MAT_POKE:
            for i in range(0, len(values) - 1, 2):
                mat_pairs[values[i]] = values[i + 1]
        elif stream in POKE_STREAM_TARGETS:
            target = poke_targets.setdefault(POKE_STREAM_TARGETS[stream], {})
            for i in range(0, len(values) - 1, 2):
                target[values[i]] = values[i + 1]
        else:
            unknown_messages.append({"what": f"sData in stream {stream}", "values": values})

    for channel, status, data1, data2 in events:
        if channel == CHANNEL_CH16 and status == STATUS_CONTROL_CHANGE:
            cc = data1
            value = data2 or 0
            cc16[cc] = value
            if cc == CC_STREAM:
                stream = None if value == STREAM_END else value
            elif cc == CC_FORM_SEL:
                current_formula = value
                form_pairs.setdefault(value, {})
            elif cc == CC_ROW:
                matrix.set_row(value)
            elif cc == CC_COL:
                matrix.set_col(value)
            elif cc == CC_MAT_DEC_HI:
                matrix.set_dec_hi(value)
            elif cc == CC_MAT_DEC_LO:
                matrix.set_dec_lo(value)
            elif cc == CC_MAT_VAL:
                matrix.commit(value)
            elif cc == CC_MAT_OP:
                mat_ops.append(value)
                if value == MAT_OP_CLEAR:
                    matrix.clear()
                elif value in MAT_OP_CLEAR_BANK:
                    matrix.clear_cols(*MAT_OP_CLEAR_BANK[value])
            elif cc in (CC_BANK_H, CC_BANK_L, CC_STORE):
                preset_select.append({"cc": cc, "value": value})
            elif cc in (CC_VERS_HI, CC_VERS_LO, CC_D_INFO, CC_ARCH_CNT, CC_TASK,
                        CC_CVC_HIGH, CC_ANLYS_SLOT, CC_GRID, CC_FORM_COPY,
                        CC_FRAC_I_M48, CC_FRAC_M49_M90):
                pass
            elif cc in CH16_STATUS_CC_NAMES:
                device_status[cc] = value
            elif cc in GLOBAL_CC_NAMES:
                globals_cc[cc] = value
            else:
                unknown_messages.append({"channel": 16, "cc": cc, "value": value})
        elif channel == CHANNEL_CH16 and status == STATUS_POLY_KEY_PRESSURE:
            sdata([data1, data2 or 0])
        elif channel == CHANNEL_CH16 and status == STATUS_CHANNEL_PRESSURE:
            sdata([data1])
        elif channel in (CHANNEL_CH1, CHANNEL_CH2) and status == STATUS_CONTROL_CHANGE:
            if data1 in GLOBAL_CC_NAMES:
                globals_cc.setdefault(data1, data2 or 0)
        elif status == STATUS_PROGRAM_CHANGE:
            preset_select.append({"program_change": data1, "channel": channel + 1})
        elif status in (STATUS_NOTE_ON, STATUS_NOTE_OFF, STATUS_PITCH_BEND):
            unknown_messages.append({"channel": channel + 1, "status": hex(status),
                                     "data": [data1, data2]})

    formulas: dict[str, dict] = {}
    for number, pairs in sorted(form_pairs.items()):
        if not pairs:
            continue
        letter = matrix_map.formula_letter(number)
        formulas[letter] = decode_formula(pairs)
        formulas[letter]["summary"] = formula.summary(formulas[letter])
    return {
        "matrix": matrix.result(),
        "matrix_ops": mat_ops,
        "formulas": formulas,
        "setup": decode_setup(mat_pairs),
        "text": text,
        "arrays": arrays,
        "poke_targets": poke_targets,
        "cc16": cc16,
        "globals_cc": globals_cc,
        "device_status": device_status,
        "preset_select": preset_select,
        "unknown_messages": unknown_messages,
    }


# ----------------------------------------------------------------- entry point

def _ascii(raw: bytes) -> str:
    return raw.split(b"\x00")[0].decode("ascii", "replace").rstrip()


def decode_preset_file(path: str) -> dict:
    """Decode one EaganMatrix preset .mid file into its logical preset.

    Returns name, description, matrix, formulas, setup and unknown, plus firmware,
    generation, macros, graphs, convolution and the raw container markers.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    header, events = read_midi_events(data)
    legacy = any(ch == CHANNEL_LEGACY_CONFIG and st == STATUS_CONTROL_CHANGE
                 for ch, st, _d1, _d2 in events)
    modern = _parse_modern(events)
    container = _decode_container(events)
    firmware = _firmware(modern["cc16"])

    unknown: dict = {"messages": modern["unknown_messages"]}
    if legacy:
        parsed = _parse_legacy(events)
        matrix = parsed["matrix"]
        formulas = parsed["formulas"]
        preset_setup = parsed["setup"]
        matrix_ops = parsed["matrix_ops"]
        unknown["legacy_config_cc"] = parsed["legacy_config_cc"]
        if parsed["legacy_formula_leftover"]:
            unknown["legacy_formula_cc"] = parsed["legacy_formula_leftover"]
    else:
        matrix = modern["matrix"]
        formulas = modern["formulas"]
        preset_setup = modern["setup"]
        matrix_ops = modern["matrix_ops"]

    arrays = modern["arrays"]
    macros = _decode_macros(arrays.get(STREAM_MACRO_HI, []), arrays.get(STREAM_MACRO_LO, []))
    macro_source = "s_MacroHi/s_MacroLo"
    if not macros:
        # No macro stream: the preset carries macros i..vi as plain cc 12..17 instead.
        macros = {formula.MACROS[cc - MACRO_CC_I]: round(v / 127.0, 4)
                  for cc, v in modern["globals_cc"].items()
                  if MACRO_CC_I <= cc < MACRO_CC_I + 6 and v}
        macro_source = "cc 12..17" if macros else "absent"
    if legacy:
        config_range = set(range(*LEGACY_MAT_CH16_RANGE)) | {LEGACY_MAT_CH16_RANGE[1]}
        unknown["messages"] = [m for m in unknown["messages"]
                               if m.get("cc") not in config_range]
    # s_Name is absent from every factory archive; the on-disk filename carries the name.
    name_stream = modern["text"].get(STREAM_NAME)
    result: dict = {
        "path": os.path.abspath(path),
        "name": _ascii(bytes(name_stream)) if name_stream else os.path.splitext(
            os.path.basename(path))[0],
        "name_source": "s_Name stream" if name_stream else "filename",
        "description": _ascii(bytes(modern["text"][STREAM_CON_TEXT]))
        if STREAM_CON_TEXT in modern["text"] else None,
        "analysis_name": _ascii(bytes(modern["text"][STREAM_ANLYS_NAME]))
        if STREAM_ANLYS_NAME in modern["text"] else None,
        "generation": "legacy" if legacy else "modern",
        "firmware": firmware,
        "midi_header": header,
        "container": container,
        "matrix": matrix,
        "matrix_ops": [_name(MAT_OP_NAMES, op) for op in matrix_ops],
        "formulas": formulas,
        "setup": preset_setup,
        "macros": macros,
        "macro_source": macro_source,
        "globals": {GLOBAL_CC_NAMES[cc]: v for cc, v in sorted(modern["globals_cc"].items())},
        # In a legacy file the ch16 cc in this range are s_Mat_Poke ids, not device status,
        # so the status bucket is meaningful only for the modern generation.
        "device_status": {} if legacy else {
            CH16_STATUS_CC_NAMES[cc]: v for cc, v in sorted(modern["device_status"].items())},
        "preset_select": modern["preset_select"],
        "graphs": {
            name: arrays[stream] for stream, name in ARRAY_STREAMS.items()
            if stream in arrays and stream in (STREAM_GRAPH, STREAM_GRAPH_O1, STREAM_GRAPH_O2)
        },
        "pitch_trim": {
            "y0": _decode_pitch_trim(arrays.get(STREAM_GRAPH_T0, [])),
            "y1": _decode_pitch_trim(arrays.get(STREAM_GRAPH_T1, [])),
        },
        "kinetic": arrays.get(STREAM_KINET),
        "biq_sin": arrays.get(STREAM_BIQ_SIN),
        "convolution": arrays.get(STREAM_CONV),
        "thumbnails": _decode_thumbnails(arrays.get(STREAM_THUMB, [])),
        "streams_present": sorted(
            set(modern["text"]) | set(arrays)
            | {s for s, t in POKE_STREAM_TARGETS.items() if t in modern["poke_targets"]}
            | ({STREAM_FORM_POKE} if modern["formulas"] else set())
            | ({STREAM_MAT_POKE} if modern["setup"]["pokes"] else set())
        ),
        "unknown": unknown,
    }
    result["stream_names"] = [_name(STREAM_NAMES, s) for s in result["streams_present"]]
    return result


# ================================================================= catalog build

# ----------------------------------------------------------------- source paths

def editor_dir() -> str:
    """The Haken Editor installation the catalog is built from, per conventions.md:32.

    No default: this is only needed to REBUILD the shipped artifacts, and a hardcoded absolute
    path would ship one developer's home directory to every user.
    """
    value = os.environ.get("HAKEN_EDITOR_DIR", "")
    if not value:
        raise RuntimeError(
            "HAKEN_EDITOR_DIR is not set. It is only needed to rebuild the shipped JSON "
            "artifacts from a Haken Editor installation; reading them needs nothing. Set it to "
            "the Editor folder containing Firmware/ (or HE/Firmware/ on the older Max-based "
            "Editor), for example: HAKEN_EDITOR_DIR=D:/Haken Editor 1081")
    return value


def source_paths() -> dict[str, str]:
    """Every input the catalog reads, resolved from HAKEN_EDITOR_DIR."""
    firmware_dir = os.path.join(editor_dir(), "Firmware")
    return {
        "firmware": firmware_dir,
        "presets": os.path.join(firmware_dir, "SysPresets", "EaganMatrixModule"),
        "descriptions": os.path.join(firmware_dir, "Descriptions"),
        "slot_manifest": os.path.join(firmware_dir,
                                      "Update File2 1081 EaganMatrixModule.txt"),
    }


# ------------------------------------------------------------ category numbering

# docs/HakenMidi.h:408  #define SSL_MainCat_Cont_E2x "UP ST WI VO KY CL OT PE PT PR DO MD CV UT"
# The 14-entry local menu order of the EaganMatrix Module (E2x). Contiguous 0-based -> list.
MAIN_CAT_TAGS = ["UP", "ST", "WI", "VO", "KY", "CL", "OT", "PE", "PT", "PR", "DO", "MD",
                 "CV", "UT"]

# docs/HakenMidi.h:396-406  #define SSL_Cat1_Cat91, cat1..cat91. Contiguous 1-based -> list.
CAT1_CAT91_TAGS = (
    "AC AD AG AI AN AT BA BB BG BH BI BM BO BR C1 CH "
    "CL CM CN CV DA DF DM DP DS DV DI DO DT DY EC EL "
    "EM EN EP EV FL FM HM HY IC IN KI KY LE LF LP LY "
    "MD MI MM MO MT NA NO OR OS OJ OP OT PA PE PT PL "
    "PO PR RD RS RN RO RV SB SD SE SH SI SO SP SR SS "
    "ST SU SV SY TA UT VO WA WB WI WO"
).split()

# docs/HakenMidi.h:410-460, the header's own tag glossary (MainType / SubType / Character /
# EaganMatrix / Setting blocks). Sparse by nature -> dict.
CAT_TAG_NAMES = {
    # MainType
    "CL": "Classic", "CV": "CVC", "DO": "Drone", "KY": "Keyboard", "MD": "Midi",
    "OT": "Other", "PE": "Percussion", "PR": "Processor", "PT": "Perc Tuned",
    "ST": "Strings", "UT": "Utility", "VO": "Vocal", "WI": "Winds", "UP": "User Presets",
    # SubType
    "AT": "Atonal", "BA": "Bass", "BO": "Bowed", "BR": "Brass", "DP": "Demo Preset",
    "EP": "Elec Piano", "FL": "Flute", "LE": "Lead", "OR": "Organ", "PA": "Pad",
    "PL": "Plucked", "RD": "Reed Double", "RS": "Reed Single", "SU": "Struck",
    # Character
    "AC": "Acoustic", "AG": "Aggressive", "AI": "Airy", "AN": "Analog", "BG": "Big",
    "BI": "Bright", "CH": "Chords", "CN": "Clean", "DA": "Dark", "DI": "Digital",
    "DT": "Distorted", "DY": "Dry", "EC": "Echo", "EL": "Electric", "EN": "Ensemble",
    "EV": "Evolving", "FM": "FM", "HY": "Hybrid", "IC": "Icy", "IN": "Intimate",
    "LF": "Lo-fi", "LP": "Looping", "LY": "Layered", "MO": "Morphing", "MT": "Metallic",
    "NA": "Nature", "NO": "Noise", "RN": "Random", "RV": "Reverberant", "SD": "Snd Design",
    "SE": "Stereo", "SH": "Shaking", "SI": "Simple", "SO": "Soft", "SR": "Strumming",
    "SY": "Synthetic", "WA": "Warm", "WO": "Woody",
    # EaganMatrix
    "AD": "Additive", "BB": "BiqBank", "BH": "BiqGraph", "BM": "BiqMouth",
    "CM": "Cutoff Mod", "DF": "Delay Formula", "DM": "Delay Micro", "DS": "Delay Sum",
    "DV": "Delay Voice", "EM": "Ext Midi Clk", "HM": "HarMan", "KI": "Kinetic",
    "MM": "ModMan", "OJ": "Osc Jenny", "OP": "Osc Phase", "OS": "Osc DSF",
    "SB": "SineBank", "SS": "SineSpray", "WB": "WaveBank",
    # Setting
    "C1": "Channel 1", "MI": "Mono Interval", "PO": "Portamento", "RO": "Rounding",
    "SP": "Split Voice", "SV": "Single Voice", "TA": "Touch Area",
}

# ---------------------------------------------------------- DSP cost classification

# Documented cost class per module, keyed by the module name `setup.py` uses - its strings
# are the accepted enum of a shipped tool (`set_osc_type` / `set_bank_type`), so they win
# project-wide and one name per module holds across prose, data and tool enums.
# Each entry cites the guide line that supports it.
DSP_COST_CLASS = {
    # banks
    "Additive": ("heavy", "polyphony capped when Additive is in use; "
                          "EaganMatrixUserGuide.txt:3657-3661"),
    "BiqBank": ("medium-heavy", "cost proportional to mode count 8..48/variable; "
                                "EaganMatrixUserGuide.txt:2264-2272"),
    "BiqGraph": ("medium-heavy", "same biquad engine as BiqBank; "
                                 "EaganMatrixUserGuide.txt:2657-2660"),
    "ModMan": ("medium-heavy", "biquad mode bank plus a load-time STFT; "
                               "EaganMatrixUserGuide.txt:3466-3472"),
    "HarMan": ("heavy", "up to 64+ interpolated grains per voice; "
                        "EaganMatrixUserGuide.txt:2240-2252"),
    "SineBank": ("medium", "scales with partial count 8..32; "
                           "EaganMatrixUserGuide.txt:3168-3172"),
    "SineSpray": ("light-medium", "gated by A; A=0 generates no grains; "
                                  "EaganMatrixUserGuide.txt:3187-3189"),
    "WaveBank": ("light-medium", "gated by A and by filled F columns; "
                                 "EaganMatrixUserGuide.txt:3235-3243"),
    "BiqMouth": ("unknown", "no cost statement in the guide"),
    "Kinetic": ("unknown", "no cost statement or Reduce-Polyphony warning in the guide"),
    "CVC": ("negligible", "no audio synthesised; formula values to a converter"),
    # oscillator / filter slot types
    "PWM Oscillator": ("heavy", "\"Computationally intensive\"; may produce Reduce Polyphony; "
                                "EaganMatrixUserGuide.txt:1623, :2106-2112"),
    "Ladder Low Pass": ("heavy", "\"computationally intensive objects which may produce "
                                 "'Reduce Polyphony' messages\"; "
                                 "EaganMatrixUserGuide.txt:7372-7373"),
    "Signal Multiplier": ("light-medium", "multiplies at sample rate not control rate; "
                                          "EaganMatrixUserGuide.txt:2142-2144"),
    "Pitch Shifter using Delay": ("light", "\"very unrefined but processor efficient\"; "
                                           "EaganMatrixUserGuide.txt:2240-2252"),
}
# Modules whose use is a DSP-budget risk a patch-building agent must weigh up front.
DSP_HEAVY_MODULES = {name for name, (cls, _why) in DSP_COST_CLASS.items()
                     if cls in ("heavy", "medium-heavy")}

# ------------------------------------------------------------------- matrix geometry

ROW_NOISE = 0
ROWS_OSC = range(1, 6)
ROWS_BANK = range(6, 9)
ROWS_AUDIO_IN = (9, 10)
ROWS_SUB = (11, 12)
ROW_DIRECT_PLUS = (13, 14)
ROW_DIRECT_MINUS = 15
ROW_DIRECT_TIMES = 16

COLS_MASTER_ASSIGNABLE = range(2, 8)
COLS_DRY = (9, 10)
COLS_OSC_F = (13, 16, 19, 22, 25)        # Osc/Filter 1..5 F (pitch) column
COLS_OSC_IN = (12, 15, 18, 21, 24)       # Osc/Filter 1..5 In column
COLS_SG_T = (52, 54, 56, 58, 60)         # SG 1..5 T (trigger) column
COLS_SG = range(51, 61)
COLS_BANK_C = range(43, 51)
COLS_BANK = {"A": range(27, 35), "B": range(35, 43), "C": range(43, 51)}
ROW_BANK = {"A": 6, "B": 7, "C": 8}
COLS_OSC_SLOT = {1: (12, 13, 14), 2: (15, 16, 17), 3: (18, 19, 20), 4: (21, 22, 23),
                 5: (24, 25, 26)}

# Wire value 0 of these ids is the device default, so a compressed file omits it rather than
# writing it (docs/HakenMidi.h:478-480). An omitted id therefore means THIS module, not
# "no module": Bank A/B default to BiqBank, Bank C to VoiceDelay, every oscillator slot to
# DSF Oscillator.
DEFAULT_BANK_AB_TYPE = setup.BANK_AB_TYPES[0]
DEFAULT_BANK_C_TYPE = setup.BANK_C_TYPES[0]
DEFAULT_OSC_TYPE = setup.OSC_TYPES[0]
# The same rule for the two remaining type selectors: an omitted idSgTyp* is a Continuous
# Cycle shape generator, an omitted idReciType is the Short Reverb recirculator. The type is
# what the device RUNS; whether the preset uses it is a matrix question.
DEFAULT_SG_TYPE = setup.SG_TYPES[0]
DEFAULT_RECI_TYPE = setup.RECI_TYPES[0]

# What `idPoly` means when the preset never wrote it. UNDOCUMENTED, unlike the four above:
# docs/HakenMidi.h:1357 defines idPoly as "base polyphony ... values 1..8" and :1370 names
# defBendRange for idBendRange, but the header defines no defPoly, and the guide says only
# that polyphony is "defaulted per preset" (docs/EaganMatrix Preset Cookbook.txt:776). The
# documented floor is taken so the field is never null, and every record that inherits it
# carries `base_from_default` so no consumer quotes it as a value read from the file.
# Settles on the device by loading one of those presets and reading cc72 (DSP polyphony).
DEFAULT_POLY_BASE = 1

# Macros v and vi were previously called Gen1/g1 and Gen2/g2; a description uses one naming
# or the other, never both. docs/ContinuumUserGuide.txt:2859-2862.
MACRO_SLOT_ALIASES = {"g1": "v", "g2": "vi"}


# -------------------------------------------------------------------- small readers

def read_system_slots(path: str) -> dict[str, int]:
    """Map preset name -> 1-based system slot from the firmware flash manifest."""
    slots: dict[str, int] = {}
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = re.match(r'\s*-(\d+)\s*,\s*"SysPresets/EaganMatrixModule/(.+)\.mid"\s*$',
                             line.strip())
            if match:
                slots[match.group(2)] = int(match.group(1))
    return slots


def read_long_descriptions(path: str) -> set[str]:
    """Names that have a long-form description `.txt` in the shared Descriptions folder."""
    return {os.path.splitext(entry)[0] for entry in os.listdir(path)
            if entry.lower().endswith(".txt") and entry.lower() != "desktop.ini"}


# The description .txt files are mixed-encoding: most are UTF-8, a handful are CP1252 with
# bare smart punctuation (0x92/0x93/0x94/0x96/0x85). UTF-8 strict first, so a CP1252 byte
# cannot be silently mojibaked into a valid-but-wrong UTF-8 reading.
DESCRIPTION_ENCODINGS = ("utf-8", "cp1252")

# The characters the factory descriptions actually use beyond ASCII, with faithful ASCII
# equivalents. The shipped artifacts carry ASCII only, and folding beats escaping here: a
# plain-words `text=` search for "buzzing" has to match a description that spells it with
# typographic quotes.
ASCII_FOLD = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "″": '"',
    "–": "-", "—": "-", "−": "-", "­": "-",
    "…": "...", " ": " ", "•": "*", "°": " deg",
    "×": "x", "±": "+-", "→": "->", "←": "<-",
}


def to_ascii(text: str) -> str:
    """Fold text to ASCII: known equivalents first, then accent-stripping, then drop.

    Dropping is lossy by construction and the corpus has exactly one case where it loses
    meaning - `Sinseong-ri`'s Korean gloss of its own title - so the loss is bounded and
    visible rather than worth a transliteration dependency.
    """
    folded = "".join(ASCII_FOLD.get(char, char) for char in text)
    decomposed = unicodedata.normalize("NFKD", folded)
    return "".join(char for char in decomposed if char.isascii())


def read_description_text(path: str) -> str:
    """One description `.txt`, decoded, newline-normalised and folded to ASCII."""
    with open(path, "rb") as handle:
        raw = handle.read()
    for encoding in DESCRIPTION_ENCODINGS:
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("ascii", errors="replace")
    return to_ascii(text.replace("\r\n", "\n").replace("\r", "\n")).strip()


def build_descriptions(entries: list[dict], descriptions_dir: str) -> dict[str, str]:
    """preset name -> long-form description text, for the presets that have one.

    A preset with no description file is **omitted**, not mapped to an empty string: an
    empty value is indistinguishable from a description that failed to decode, and it would
    let a text search match a preset with nothing to match on. `has_long_description` in the
    catalog stays the authoritative flag, and absence here means absence there.

    The Descriptions folder is shared by all four device families and is not pruned, so it
    is read per preset rather than listed - see `describe_description_asymmetry`.
    """
    out: dict[str, str] = {}
    for entry in entries:
        if not entry["has_long_description"]:
            continue
        text = read_description_text(os.path.join(descriptions_dir,
                                                  entry["name"] + ".txt"))
        if text:
            out[entry["name"]] = text
    return out


def parse_description_tags(text: str | None) -> dict:
    """Split a preset's embedded description into macro labels, category tags and author.

    The embedded `s_ConText` string is a flat `key=value` list, e.g.
    `i=Mouth_0g ii=FreqMult_Min_Max ... C=UT A=A.Nonymous`. `C=` carries one
    underscore-joined tag run whose FIRST element is the MainType
    (docs/HakenMidi.h:410-424); the rest are SubType / Character / EaganMatrix / Setting tags.
    """
    out: dict = {"macro_labels": {}, "category_tags": [], "author": None,
                 "fade": None, "other_tags": {}}
    if not text:
        return out
    roman = tuple(formula.MACROS[:6])
    for key, value in re.findall(r"(?:^|\s)([A-Za-z][A-Za-z0-9]*)=(\S*)", text):
        low = key.lower()
        if low in roman or re.fullmatch(r"g[12]", low):
            out["macro_labels"][low] = value
        elif key == "C":
            out["category_tags"] = [tag for tag in value.split("_") if tag]
        elif key == "A":
            out["author"] = value
        elif low == "fade":
            out["fade"] = int(value) if value.isdigit() else value
        else:
            out["other_tags"][key] = value
    return out


# ---------------------------------------------------------- explicit-only accessors

def explicit_banks(pokes: dict) -> dict:
    """Bank A/B/C type, `null` where the file did not set it (= device default)."""
    out = {}
    for slot, poke, table in (("A", "BankA", setup.BANK_AB_TYPES),
                              ("B", "BankB", setup.BANK_AB_TYPES),
                              ("C", "BankC", setup.BANK_C_TYPES)):
        raw = pokes.get(poke)
        out[slot] = {
            "explicit": poke in pokes,
            "raw": raw,
            "type": table.get(raw) if raw is not None else None,
        }
    return out


def explicit_oscillators(pokes: dict) -> list[dict]:
    """Per-slot oscillator/filter type, option and extreme-rate flag, explicit only."""
    out = []
    for index in range(5):
        type_poke = f"OscFilTyp{index + 1}"
        opt_poke = f"OscFilOpt{index + 1}"
        ext_poke = f"FilExtrm{index + 1}"
        raw = pokes.get(type_poke)
        out.append({
            "slot": index + 1,
            "explicit": type_poke in pokes,
            "raw": raw,
            "type": setup.OSC_TYPES.get(raw) if raw is not None else None,
            "option_raw": pokes.get(opt_poke),
            "option": setup.osc_option_name(raw, pokes.get(opt_poke)),
            "extreme_rate": bool(pokes.get(ext_poke)) if ext_poke in pokes else None,
        })
    return out


def explicit_polyphony(pokes: dict) -> dict:
    """Polyphony, keeping "absent" distinct from "set to this value".

    `Poly` is `s_Mat_Poke` id 39 with the base count in the low 6 bits; `OkExpPoly` (id 11)
    is the `+` expanded flag and `OkIncComp` (id 5) the double-computation-rate flag
    (CLAUDE.md, 2026-10-25, fw 10.81).
    """
    raw = pokes.get("Poly")
    return {
        "base": (raw & POLY_BASE_MASK) if raw is not None else None,
        "base_explicit": "Poly" in pokes,
        "expanded": bool(pokes.get("OkExpPoly")) if "OkExpPoly" in pokes else None,
        "expanded_explicit": "OkExpPoly" in pokes,
        "double_computation_rate": bool(pokes.get("OkIncComp")) if "OkIncComp" in pokes else None,
        "double_rate_explicit": "OkIncComp" in pokes,
    }


def explicit_shape_generators(pokes: dict) -> list[dict]:
    """SG 1..5 type, explicit only. Not recoverable at all from a legacy file."""
    out = []
    for index in range(5):
        poke = f"SgTyp{index + 1}"
        raw = pokes.get(poke)
        out.append({
            "sg": index + 1,
            "explicit": poke in pokes,
            "raw": raw,
            "type": setup.SG_TYPES[raw & setup.SG_TYPE_MASK] if raw is not None else None,
        })
    return out


def explicit_master_columns(pokes: dict) -> list[dict]:
    out = []
    for index in range(6):
        poke = f"MastCol{index + 1}"
        if poke not in pokes:
            continue
        raw = pokes[poke]
        out.append({
            "column": index + 2,
            "raw": raw,
            "target": setup.MASTER_COL_TARGETS.get(raw),
        })
    return out


# ----------------------------------------------------------- matrix / formula census

def matrix_profile(cells: list[dict]) -> dict:
    """Mechanical shape of the matrix: counts and which structural regions are in use."""
    rows = {cell["row"] for cell in cells}
    cols = {cell["col"] for cell in cells}
    audio_rows = set(ROWS_OSC) | set(ROWS_BANK) | set(ROWS_AUDIO_IN) | set(ROWS_SUB) | {ROW_NOISE}
    return {
        "cells": len(cells),
        "muted_cells": sum(1 for cell in cells if cell["disabled"]),
        "numeric_cells": sum(1 for cell in cells if cell["value"] is not None),
        "formula_cells": sum(1 for cell in cells
                             if cell["value"] is None and 1 <= cell["code"] <= 44),
        "rows_used": sorted(rows),
        "cols_used": sorted(cols),
        "row_names_used": sorted({cell["row_name"] for cell in cells}),
        "uses_noise_row": ROW_NOISE in rows,
        "uses_audio_in": any(row in rows for row in ROWS_AUDIO_IN),
        "uses_submix_rows": any(row in rows for row in ROWS_SUB),
        "uses_direct_plus": any(row in rows for row in ROW_DIRECT_PLUS),
        "uses_direct_minus": ROW_DIRECT_MINUS in rows,
        "uses_direct_times": ROW_DIRECT_TIMES in rows,
        "uses_sg_columns": any(col in cols for col in COLS_SG),
        "sg_triggers_fed": sorted(COLS_SG_T.index(col) + 1 for col in cols
                                  if col in COLS_SG_T),
        "uses_bank_c_columns": any(col in cols for col in COLS_BANK_C),
        "uses_dry_columns": any(col in cols for col in COLS_DRY),
        "uses_master_assignable": any(col in cols for col in COLS_MASTER_ASSIGNABLE),
        "audio_rate_into_osc_f": sorted(
            {(cell["row_name"], cell["col_name"]) for cell in cells
             if cell["col"] in COLS_OSC_F and cell["row"] in audio_rows}),
        "audio_into_osc_in": sorted(
            {(cell["row_name"], cell["col_name"]) for cell in cells
             if cell["col"] in COLS_OSC_IN and cell["row"] in audio_rows}),
    }


# Which s_Form_Poke ids belong to which part of a formula, by the header's own id NAMES
# (formula.FORM_POKE_NAMES). Groupings, not wire tables: the census counts how many
# formulas SET an id, which is the only thing a compressed preset can tell us.
_X_IDS = {"HBegX", "HEndX", "VBegX", "VEndX", "MultX", "InitX", "TransX", "XMacr", "ZeroX",
          "QuantX", "NegBegX", "NegEndX"}
_Y_IDS = {"HBegY", "HEndY", "VBegY", "VEndY", "MultY", "InitY", "TransY", "YMacr",
          "NegBegY", "NegEndY"}
_Z_IDS = {"HBegZ", "HEndZ", "VBegZ", "VEndZ", "MultZ", "InitZ", "TransZ", "ZMacr",
          "NegBegZ", "NegEndZ"}
_MACRO_IDS = {"XMacr", "YMacr", "ZMacr", "SWMacr", "BlMacForm"}
_ANC_OP_IDS = {"AncOp", "AncVal", "AncOp2", "AncVal2"}
_ANC_FLAG_IDS = {"AncDom", "AncLookup", "AncLimit", "AncNN", "AncTAorAll"}
_NEG_IDS = {"NegW", "NegW2", "NegBegX", "NegBegX2", "NegEndX", "NegEndX2", "NegBegY",
            "NegBegY2", "NegEndY", "NegEndY2", "NegBegZ", "NegBegZ2", "NegEndZ", "NegEndZ2"}
_SECONDARY_IDS = {"HeightW2", "VBegX2", "VEndX2", "VBegY2", "VEndY2", "VBegZ2", "VEndZ2",
                  "Persist2", "Interp2", "Reluct2", "TransBl", "Blend", "BlMacForm"}


def formula_profile(formulas: dict) -> dict:
    """Which formula machinery the preset actually sets, by explicit id only."""
    ids: collections.Counter = collections.Counter()
    w_modes: collections.Counter = collections.Counter()
    operators: collections.Counter = collections.Counter()
    shapes: collections.Counter = collections.Counter()
    negative = set()
    for decoded in formulas.values():
        pokes = decoded["pokes"]
        # Count how many formulas SET each id, not the sum of the values they set.
        ids.update(pokes.keys())
        # A Neg* id present with value 0 is an explicit POSITIVE sign, not a negative one.
        negative |= {key for key, value in pokes.items() if key in _NEG_IDS and value}
        if "SgW" in pokes:
            w_modes[decoded["W"]["mode"]] += 1
        if "FormOp" in pokes:
            operators[decoded["operator"]] += 1
        if "ShapeW" in pokes:
            shapes[decoded["W"]["sg_shape"]] += 1
    present = set(ids)
    return {
        "count": len(formulas),
        "letters": sorted(formulas),
        "explicit_id_formula_counts": dict(sorted(ids.items())),
        "w_sources": dict(w_modes),
        "operators": dict(operators),
        "w_shapes": dict(shapes),
        "uses_x": bool(present & _X_IDS),
        "uses_y": bool(present & _Y_IDS),
        "uses_z": bool(present & _Z_IDS),
        "uses_macro": bool(present & _MACRO_IDS),
        "uses_ancillary_op": bool(present & _ANC_OP_IDS),
        "uses_ancillary_flag": bool(present & _ANC_FLAG_IDS),
        "negative_sign_ids_set": sorted(negative),
        "uses_negative_height": bool(negative),
        "uses_secondary_blend": bool(present & _SECONDARY_IDS),
        "uses_shape_generator": any(src and src.startswith("SG") for src in w_modes),
        "uses_formula_delay": any(src == "FormulaDelay" for src in w_modes),
        "uses_gated_w": w_modes.get("Gated", 0) > 0,
    }


# ---------------------------------------------------------------- technique tagging

def implicit_default_modules(banks: dict, oscillators: list[dict], cells: list[dict]) -> dict:
    """Modules the preset runs on the DEFAULT type because it never wrote the type id.

    Only reported where the preset actually wires that bank's or slot's matrix region - an
    untouched bank with no columns wired is a default sitting idle, not a module in use.
    """
    rows = {cell["row"] for cell in cells}
    cols = {cell["col"] for cell in cells}
    out: dict = {"banks": {}, "oscillator_slots": {}}
    for slot in "ABC":
        default = DEFAULT_BANK_C_TYPE if slot == "C" else DEFAULT_BANK_AB_TYPE
        wired = any(col in cols for col in COLS_BANK[slot]) or ROW_BANK[slot] in rows
        out["banks"][slot] = {
            "implicit": not banks[slot]["explicit"],
            "wired_in_matrix": wired,
            "implied_type": default if not banks[slot]["explicit"] else None,
            "counts_as_in_use": (not banks[slot]["explicit"]) and wired,
        }
    for entry in oscillators:
        slot = entry["slot"]
        wired = any(col in cols for col in COLS_OSC_SLOT[slot]) or slot in rows
        out["oscillator_slots"][str(slot)] = {
            "implicit": not entry["explicit"],
            "wired_in_matrix": wired,
            "implied_type": DEFAULT_OSC_TYPE if not entry["explicit"] else None,
            "counts_as_in_use": (not entry["explicit"]) and wired,
        }
    return out


# Module name -> technique tag. Names are `setup.py`'s, so one name per module holds across
# prose, data and tool enums.
BANK_TECHNIQUES = {
    "BiqMouth": "formant_filtering", "BiqBank": "modal_resonator",
    "BiqGraph": "modal_resonator", "ModMan": "modal_resonator",
    "SineBank": "sine_partials", "SineSpray": "granular", "HarMan": "granular",
    "WaveBank": "wavetable", "Additive": "additive", "Kinetic": "physical_kinetic",
    "CVC": "control_voltage", "VoiceDelay": "delay_per_voice",
    "SummedDelay": "delay_summed", "MicroDelay": "delay_micro",
    "FormulaDelay": "delay_formula",
}
OSC_TECHNIQUES = {
    "Ladder Low Pass": "ladder_filter", "PWM Oscillator": "pwm",
    "DSF Oscillator": "dsf_oscillator", "Integrated DSF": "dsf_oscillator",
    "Jenny Oscillator": "jenny_oscillator", "Phase Generator": "phase_generator",
    "Noise from Seed": "noise_oscillator", "Signal Multiplier": "ring_mod_multiply",
    "Tanh": "saturation", "Bitcrusher": "bitcrush",
    "Pitch Shifter using Delay": "granulate_tap",
}
# The slot types whose idOscFilOpt is a cascade count are exactly the multimode filters.
MULTIMODE_FILTER_TYPES = {setup.OSC_TYPES[v] for v in setup.OSC_CASCADE_VALUES}


def technique_tags(banks: dict, oscillators: list[dict], matrix: dict, formulas: dict,
                   polyphony: dict, decoded: dict) -> list[str]:
    """Shallow, mechanical technique tags.

    Deliberately surface-level: each tag is a direct restatement of an explicitly set setup
    id, an occupied matrix region or an explicitly set formula id. Deep pattern mining (what
    the wiring *achieves*) is a separate job.
    """
    tags: set[str] = set()
    bank_types = {entry["type"] for entry in banks.values() if entry["type"]}
    osc_types = {entry["type"] for entry in oscillators if entry["type"]}

    for name in bank_types:
        # A Bank C "alias of B" value names the same module as its Bank B form.
        bare = name.split(" (alias")[0]
        if bare in BANK_TECHNIQUES:
            tags.add(BANK_TECHNIQUES[bare])
    for name in osc_types:
        if name in OSC_TECHNIQUES:
            tags.add(OSC_TECHNIQUES[name])
    if osc_types & MULTIMODE_FILTER_TYPES:
        tags.add("multimode_filter")

    if matrix["uses_noise_row"]:
        tags.add("noise_source")
    if matrix["uses_audio_in"]:
        tags.add("external_audio_input")
    if matrix["uses_submix_rows"]:
        tags.add("submix_feedback")
    if matrix["uses_direct_times"]:
        tags.add("direct_multiply_row")
    if matrix["uses_direct_minus"]:
        tags.add("direct_negative_row")
    if matrix["uses_direct_plus"]:
        tags.add("direct_additive_row")
    if matrix["audio_rate_into_osc_f"]:
        tags.add("audio_rate_fm")
    if matrix["audio_into_osc_in"]:
        tags.add("audio_through_slot")
    if matrix["uses_dry_columns"]:
        tags.add("dry_path")
    if matrix["uses_master_assignable"]:
        tags.add("master_column_modulation")
    if matrix["uses_sg_columns"]:
        tags.add("shape_generator_wired")
    if matrix["sg_triggers_fed"]:
        tags.add("shape_generator_triggered")

    if formulas["uses_shape_generator"]:
        tags.add("shape_generator_formula")
    if formulas["uses_formula_delay"]:
        tags.add("formula_delay_buffer")
    if formulas["uses_gated_w"]:
        tags.add("gated_envelope")
    if formulas["uses_x"]:
        tags.add("x_modulation")
    if formulas["uses_y"]:
        tags.add("y_modulation")
    if formulas["uses_z"]:
        tags.add("z_modulation")
    if formulas["uses_macro"]:
        tags.add("macro_modulation")
    if formulas["uses_ancillary_op"]:
        tags.add("ancillary_math")
    if formulas["uses_ancillary_flag"]:
        tags.add("ancillary_flag")
    if formulas["uses_negative_height"]:
        tags.add("negative_height")
    if formulas["uses_secondary_blend"]:
        tags.add("blend_secondary_formula")

    if polyphony["base"] == 1:
        tags.add("monophonic")
    if polyphony["double_computation_rate"]:
        tags.add("double_computation_rate")
    if polyphony["expanded"]:
        tags.add("expanded_polyphony")
    if decoded.get("convolution"):
        tags.add("convolution")
    if decoded.get("kinetic"):
        tags.add("kinetic_properties")
    if decoded.get("biq_sin"):
        tags.add("biq_sine_properties")
    if decoded.get("graphs"):
        tags.add("graph_data")
    return sorted(tags)


# ------------------------------------------------------------------------ catalog build

def build_entry(path: str, slots: dict[str, int], long_desc: set[str]) -> dict:
    decoded = decode_preset_file(path)
    pokes = decoded["setup"]["pokes"]
    tags = parse_description_tags(decoded["description"])
    banks = explicit_banks(pokes)
    oscillators = explicit_oscillators(pokes)
    polyphony = explicit_polyphony(pokes)
    matrix = matrix_profile(decoded["matrix"])
    formulas = formula_profile(decoded["formulas"])

    main_tag = tags["category_tags"][0] if tags["category_tags"] else None
    modules = sorted({entry["type"] for entry in banks.values() if entry["type"]}
                     | {entry["type"] for entry in oscillators if entry["type"]})
    defaults = implicit_default_modules(banks, oscillators, decoded["matrix"])
    implied = {entry["implied_type"] for group in defaults.values()
               for entry in group.values() if entry["counts_as_in_use"]}
    name = decoded["name"]
    slot = slots.get(name)
    reci_raw = pokes.get("ReciType")
    return {
        "name": name,
        "file": os.path.basename(path),
        "system_slot": slot,
        "flat_preset_number": (128 + slot) if slot else None,
        "generation": decoded["generation"],
        "firmware": decoded["firmware"]["text"],
        "category_main_tag": main_tag,
        "category_main_name": CAT_TAG_NAMES.get(main_tag),
        "category_menu_index": MAIN_CAT_TAGS.index(main_tag) if main_tag in MAIN_CAT_TAGS
        else None,
        "category_tag_number": (CAT1_CAT91_TAGS.index(main_tag) + 1)
        if main_tag in CAT1_CAT91_TAGS else None,
        "category_tags": tags["category_tags"],
        "category_tag_names": [CAT_TAG_NAMES.get(tag, f"?{tag}")
                               for tag in tags["category_tags"]],
        "author": tags["author"],
        "macro_labels": tags["macro_labels"],
        "macro_labels_normalised": {MACRO_SLOT_ALIASES.get(slot_name, slot_name): label
                                    for slot_name, label in tags["macro_labels"].items()},
        "fade": tags["fade"],
        "other_description_tags": tags["other_tags"],
        "has_long_description": name in long_desc,
        "banks": banks,
        "oscillators": oscillators,
        "polyphony": polyphony,
        "bend_range_raw": pokes.get("BendRange"),
        "recirculator": {
            "explicit": "ReciType" in pokes,
            "raw": reci_raw,
            "type": _name(setup.RECI_TYPES, reci_raw & setup.RECI_TYPE_MASK)
            if reci_raw is not None else None,
        },
        "spectral_set_raw": {"A": pokes.get("SSetA"), "B": pokes.get("SSetB")},
        "shape_generators": explicit_shape_generators(pokes),
        "master_columns": explicit_master_columns(pokes),
        "row_type_raw": {"audio": pokes.get("RowTyp1"), "submix": pokes.get("RowTyp2")},
        "delay_time_select_raw": pokes.get("TimeSel"),
        "implicit_defaults": defaults,
        "modules_used": modules,
        "modules_used_including_defaults": sorted(set(modules) | implied),
        "dsp_heavy_modules": sorted(set(modules) & DSP_HEAVY_MODULES),
        "dsp_cost_classes": {module: DSP_COST_CLASS[module][0] for module in modules
                             if module in DSP_COST_CLASS},
        "matrix": matrix,
        "formulas": formulas,
        "techniques": technique_tags(banks, oscillators, matrix, formulas, polyphony,
                                     decoded),
        "setup_explicit_ids": sorted(pokes),
        "setup_explicit_values": dict(sorted(pokes.items())),
        "setup_unknown_pokes": decoded["setup"]["unknown_pokes"],
        "streams_present": decoded["stream_names"],
        "macro_values": decoded["macros"],
        "macro_source": decoded["macro_source"],
    }


def _sort_key_name(name: str) -> str:
    """Case-insensitive sort on the preset name as displayed."""
    return name.lower()


def _sort_key_filename(name: str) -> str:
    """Case-insensitive sort on the on-disk filename, extension included.

    This is the collation the firmware flash manifest demonstrably uses: sorting the 668
    `Update File2 1081 EaganMatrixModule.txt` entries by `(name + ".mid").lower()`
    reproduces its slot order exactly, while sorting by the bare name does not
    (`Acrylic Clock 2` precedes `Acrylic Clock` because " " < ".").
    """
    return (name + ".mid").lower()


def _annotate_category_index(entries: list[dict]) -> None:
    """Add `category_index`: the number load_preset(category, index) actually takes.

    The catalog already carries `system_slot` (1..668 global) and `category_menu_index`
    (which menu slot), but NOT the 0-based position WITHIN that category, which is the
    second argument every load takes. Computed here because it needs all entries at once.

    Entries arrive sorted by `system_slot`, and that order is the filename collation
    (`(name + ".mid").lower()`), so `Acrylic Clock 2` precedes `Acrylic Clock` because
    " " < ".". Device-verified 2026-10-27/28 on three presets in three categories:
    `FM Bells` PT 16, `Metal Rainstick` PE 11, `Windtube Air Reed` WI 54 - each loaded by
    the computed number and the device reported the expected name back. The Editor's own
    `SysPresetsColl.*.txt` lists the 668 presets in this same order, independently.
    """
    seen: dict[str, int] = {}
    for entry in entries:
        tag = entry["category_main_tag"]
        if not tag:
            entry["category_index"] = None
            continue
        entry["category_index"] = seen.get(tag, 0)
        seen[tag] = entry["category_index"] + 1


def build_preset_index(entries: list[dict]) -> dict:
    """category -> 0-based index -> name, in both candidate collations.

    Which collation the Module's own per-category menu uses is unresolved offline: the two
    orders differ in 10 of 13 categories, and none of the four device observations on record
    falls on a differing position. Both are emitted; `primary` names the better-supported one.
    """
    by_tag: dict[str, list[str]] = collections.defaultdict(list)
    for entry in entries:
        tag = entry["category_main_tag"]
        if tag:
            by_tag[tag].append(entry["name"])

    def table(key) -> dict:
        out = {}
        for tag, names in by_tag.items():
            ordered = sorted(names, key=key)
            out[tag] = {
                "tag": tag,
                "name": CAT_TAG_NAMES.get(tag),
                "menu_index": MAIN_CAT_TAGS.index(tag) if tag in MAIN_CAT_TAGS else None,
                "cat1_91_number": (CAT1_CAT91_TAGS.index(tag) + 1)
                if tag in CAT1_CAT91_TAGS else None,
                "count": len(ordered),
                "presets": {str(index): name for index, name in enumerate(ordered)},
            }
        return dict(sorted(out.items(),
                           key=lambda item: MAIN_CAT_TAGS.index(item[0])
                           if item[0] in MAIN_CAT_TAGS else 99))

    filename_table = table(_sort_key_filename)
    name_table = table(_sort_key_name)
    checks = [("UT", "BiqMouth - Basic", 7), ("UT", "Comb Filter Basics", 8),
              ("UT", "Karplus - 1", 15), ("ST", "MicroDelay WaveGuide v1", 31)]
    regression = []
    for tag, name, expected in checks:
        got_f = next((int(k) for k, v in filename_table[tag]["presets"].items()
                      if v == name), None)
        got_n = next((int(k) for k, v in name_table[tag]["presets"].items()
                      if v == name), None)
        regression.append({
            "category_tag": tag, "name": name, "device_index": expected,
            "filename_collation_index": got_f, "name_collation_index": got_n,
            "pass": got_f == expected and got_n == expected,
        })
    divergence = {}
    for tag in filename_table:
        a = [filename_table[tag]["presets"][str(i)]
             for i in range(filename_table[tag]["count"])]
        b = [name_table[tag]["presets"][str(i)] for i in range(name_table[tag]["count"])]
        differing = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if differing:
            divergence[tag] = {"positions": len(differing),
                               "first_index": differing[0],
                               "filename_collation": a[differing[0]],
                               "name_collation": b[differing[0]]}
    empty_slots = [tag for tag in MAIN_CAT_TAGS if tag not in filename_table]
    return {
        "firmware": "10.81",
        "device": "EaganMatrix Module",
        "derivation": "category = index of the FIRST C= tag of each preset's embedded "
                      "description in SSL_MainCat_Cont_E2x (docs/HakenMidi.h:408); index = "
                      "0-based position in the alphabetical ordering within that category",
        "menu_order": MAIN_CAT_TAGS,
        "menu_slots_with_no_presets": empty_slots,
        "primary": "by_filename_collation",
        "collation_status": "resolved: by_filename_collation, device-verified 2026-10-28",
        "collation_note":
            "RESOLVED 2026-10-28: the Module uses by_filename_collation. Three presets in "
            "three categories were loaded by the index that collation predicts and the device "
            "reported the expected name back (FM Bells PT 16, Metal Rainstick PE 11, Windtube "
            "Air Reed WI 54), and a 17-position scan of PT matched it entry for entry including "
            "`Dolce Cristallo Space` before `Dolce Cristallo`. The Editor's own "
            "SysPresetsColl.*.txt lists all 668 in the same order, independently. DT3 is "
            "retired. Each preset's own number is `category_index`. For history, the two "
            "candidates had diverged. "
            f"The two candidates diverge in {len(divergence)} of {len(filename_table)} "
            f"populated categories, "
            f"{sum(e['positions'] for e in divergence.values())} positions in all ("
            + ", ".join(f"{tag} {entry['positions']}" for tag, entry in
                        sorted(divergence.items(), key=lambda item: -item[1]["positions"]))
            + "). Those device observations all fell where the two agreed, which is "
              "why it stayed open as long as it did. "
              "Menu slots with "
              f"no presets: {', '.join(empty_slots)} - so {len(filename_table)} of the "
              f"{len(MAIN_CAT_TAGS)} slots are populated and the empty ones appear in "
              "neither collation. protocol-sources.md:43-49: confirm a preset index by "
              "capture with load_and_capture_preset, never by the printed list - published "
              "index numbers do not reliably match the device on fw 10.81.",
        "regression_checks": regression,
        "collation_divergence": divergence,
        "by_filename_collation": filename_table,
        "by_name_collation": name_table,
    }


def build_census(entries: list[dict]) -> dict:
    """Roll-up counts. Every count distinguishes explicitly-set from absent."""
    census: dict = {}
    census["presets"] = len(entries)
    census["generation"] = dict(collections.Counter(e["generation"] for e in entries))
    census["firmware_stamp"] = dict(sorted(
        collections.Counter(e["firmware"] for e in entries).items()))
    census["category_main"] = dict(sorted(
        collections.Counter(e["category_main_tag"] for e in entries).items(),
        key=lambda item: MAIN_CAT_TAGS.index(item[0]) if item[0] in MAIN_CAT_TAGS else 99))
    census["category_tag_frequency"] = dict(collections.Counter(
        tag for e in entries for tag in e["category_tags"]).most_common())
    census["category_tags_not_in_cat1_91"] = {
        tag: [e["name"] for e in entries if tag in e["category_tags"]]
        for tag in sorted({tag for e in entries for tag in e["category_tags"]}
                          - set(CAT1_CAT91_TAGS))}
    census["presets_whose_first_tag_is_not_a_menu_category"] = [
        e["name"] for e in entries if e["category_menu_index"] is None]
    census["unknown_setup_pokes"] = dict(collections.Counter(
        poke for e in entries for poke in e["setup_explicit_ids"]
        if poke.startswith("?")).most_common())
    census["author"] = dict(collections.Counter(e["author"] for e in entries).most_common())
    census["macro_label_slots"] = dict(collections.Counter(
        slot for e in entries for slot in e["macro_labels"]).most_common())
    census["macro_label_slots_normalised"] = dict(collections.Counter(
        slot for e in entries for slot in e["macro_labels_normalised"]).most_common())
    census["macro_slot_naming_by_generation"] = {
        gen: dict(collections.Counter(
            slot for e in entries if e["generation"] == gen
            for slot in e["macro_labels"] if slot in ("g1", "g2", "v", "vi")))
        for gen in ("legacy", "modern")}
    census["macro_label_count_distribution"] = dict(sorted(
        collections.Counter(len(e["macro_labels"]) for e in entries).items()))
    census["macro_label_style_codes"] = dict(collections.Counter(
        part for e in entries for label in e["macro_labels"].values()
        for part in label.split("_")[1:2] if re.fullmatch(r"\d[a-z]", part)).most_common())
    census["has_long_description"] = sum(1 for e in entries if e["has_long_description"])
    census["modules_by_category"] = {
        tag: dict(collections.Counter(
            module for e in entries if e["category_main_tag"] == tag
            for module in e["modules_used"]).most_common())
        for tag in MAIN_CAT_TAGS if any(e["category_main_tag"] == tag for e in entries)}
    census["polyphony_by_generation"] = {
        gen: dict(sorted(collections.Counter(
            e["polyphony"]["base"] for e in entries
            if e["generation"] == gen and e["polyphony"]["base_explicit"]).items()))
        for gen in ("legacy", "modern")}
    census["setup_recoverability_by_generation"] = {
        gen: {
            "presets": sum(1 for e in entries if e["generation"] == gen),
            "bank_A_explicit": sum(1 for e in entries if e["generation"] == gen
                                   and e["banks"]["A"]["explicit"]),
            "any_sg_type_explicit": sum(1 for e in entries if e["generation"] == gen
                                        and any(sg["explicit"]
                                                for sg in e["shape_generators"])),
            "row_type_explicit": sum(1 for e in entries if e["generation"] == gen
                                     and e["row_type_raw"]["audio"] is not None),
            "recirculator_explicit": sum(1 for e in entries if e["generation"] == gen
                                         and e["recirculator"]["explicit"]),
        }
        for gen in ("legacy", "modern")}

    for slot in "ABC":
        explicit = [e for e in entries if e["banks"][slot]["explicit"]]
        census[f"bank_{slot}"] = {
            "explicit": len(explicit),
            "absent_so_default": len(entries) - len(explicit),
            "types": dict(collections.Counter(
                e["banks"][slot]["type"] for e in explicit).most_common()),
        }
    osc_explicit: collections.Counter = collections.Counter()
    osc_types: collections.Counter = collections.Counter()
    for entry in entries:
        for slot_entry in entry["oscillators"]:
            if slot_entry["explicit"]:
                osc_explicit[slot_entry["slot"]] += 1
                osc_types[slot_entry["type"]] += 1
    census["oscillator_slot_explicit"] = dict(sorted(osc_explicit.items()))
    census["oscillator_types"] = dict(osc_types.most_common())
    census["presets_with_any_oscillator_slot"] = sum(
        1 for e in entries if any(s["explicit"] for s in e["oscillators"]))

    census["polyphony_base"] = {
        "explicit": sum(1 for e in entries if e["polyphony"]["base_explicit"]),
        "absent_so_default": sum(1 for e in entries
                                 if not e["polyphony"]["base_explicit"]),
        "values": dict(sorted(collections.Counter(
            e["polyphony"]["base"] for e in entries
            if e["polyphony"]["base_explicit"]).items())),
    }
    census["polyphony_expanded"] = {
        "explicit_true": sum(1 for e in entries if e["polyphony"]["expanded"]),
        "explicit_false": sum(1 for e in entries
                              if e["polyphony"]["expanded_explicit"]
                              and not e["polyphony"]["expanded"]),
        "absent_so_default": sum(1 for e in entries
                                 if not e["polyphony"]["expanded_explicit"]),
    }
    census["double_computation_rate"] = {
        "explicit_true": sum(1 for e in entries
                             if e["polyphony"]["double_computation_rate"]),
        "absent_so_default": sum(1 for e in entries
                                 if not e["polyphony"]["double_rate_explicit"]),
    }
    census["recirculator"] = {
        "explicit": sum(1 for e in entries if e["recirculator"]["explicit"]),
        "absent_so_default": sum(1 for e in entries if not e["recirculator"]["explicit"]),
        "types": dict(collections.Counter(
            e["recirculator"]["type"] for e in entries
            if e["recirculator"]["explicit"]).most_common()),
    }
    census["shape_generator_types_explicit"] = dict(collections.Counter(
        sg["type"] for e in entries for sg in e["shape_generators"]
        if sg["explicit"]).most_common())
    census["presets_with_explicit_sg_type"] = {
        "modern": sum(1 for e in entries if e["generation"] == "modern"
                      and any(sg["explicit"] for sg in e["shape_generators"])),
        "legacy": sum(1 for e in entries if e["generation"] == "legacy"
                      and any(sg["explicit"] for sg in e["shape_generators"])),
    }
    census["modules_used"] = dict(collections.Counter(
        module for e in entries for module in e["modules_used"]).most_common())
    census["modules_used_including_defaults"] = dict(collections.Counter(
        module for e in entries
        for module in e["modules_used_including_defaults"]).most_common())
    census["implicit_default_modules"] = {
        "note": "wire value 0 of BankA/BankB/BankC/OscFilTyp* is the device default, so a "
                "compressed file never writes it; these are the presets that run a module "
                "ON that default while wiring its matrix region",
        "explicit_bank_value_0_occurrences": {
            slot: sum(1 for e in entries if e["banks"][slot]["raw"] == 0)
            for slot in "ABC"},
        "banks": {
            slot: {
                "type_id_absent": sum(1 for e in entries
                                      if e["implicit_defaults"]["banks"][slot]["implicit"]),
                "absent_and_wired": sum(
                    1 for e in entries
                    if e["implicit_defaults"]["banks"][slot]["counts_as_in_use"]),
                "implied_type": DEFAULT_BANK_C_TYPE if slot == "C"
                else DEFAULT_BANK_AB_TYPE,
            }
            for slot in "ABC"},
        "oscillator_slots": {
            str(slot): {
                "type_id_absent": sum(
                    1 for e in entries
                    if e["implicit_defaults"]["oscillator_slots"][str(slot)]["implicit"]),
                "absent_and_wired": sum(
                    1 for e in entries
                    if e["implicit_defaults"]["oscillator_slots"][str(slot)]
                    ["counts_as_in_use"]),
                "implied_type": DEFAULT_OSC_TYPE,
            }
            for slot in range(1, 6)},
        "presets_with_an_implicit_biqbank": sum(
            1 for e in entries
            if any(e["implicit_defaults"]["banks"][slot]["counts_as_in_use"]
                   for slot in "AB")),
        "presets_with_an_implicit_voicedelay": sum(
            1 for e in entries
            if e["implicit_defaults"]["banks"]["C"]["counts_as_in_use"]),
        "presets_with_an_implicit_dsf_oscillator": sum(
            1 for e in entries
            if any(e["implicit_defaults"]["oscillator_slots"][str(slot)]
                   ["counts_as_in_use"] for slot in range(1, 6))),
        "biqbank_category_tag_cross_check": {
            "presets_tagged_BB": sum(1 for e in entries if "BB" in e["category_tags"]),
            "of_those_with_no_explicit_bank_A_or_B": sum(
                1 for e in entries if "BB" in e["category_tags"]
                and not e["banks"]["A"]["explicit"] and not e["banks"]["B"]["explicit"]),
            "of_those_with_an_implicit_wired_bank": sum(
                1 for e in entries if "BB" in e["category_tags"]
                and any(e["implicit_defaults"]["banks"][slot]["counts_as_in_use"]
                        for slot in "AB")),
        },
    }
    census["presets_using_a_dsp_heavy_module"] = sum(
        1 for e in entries if e["dsp_heavy_modules"])
    census["dsp_heavy_module_frequency"] = dict(collections.Counter(
        module for e in entries for module in e["dsp_heavy_modules"]).most_common())
    census["techniques"] = dict(collections.Counter(
        tag for e in entries for tag in e["techniques"]).most_common())
    census["setup_id_frequency"] = dict(collections.Counter(
        poke for e in entries for poke in e["setup_explicit_ids"]).most_common())
    census["setup_id_count_distribution"] = dict(sorted(collections.Counter(
        len(e["setup_explicit_ids"]) for e in entries).items()))
    formula_ids: collections.Counter = collections.Counter()
    formula_ids_by_preset: collections.Counter = collections.Counter()
    for entry in entries:
        formula_ids.update(entry["formulas"]["explicit_id_formula_counts"])
        formula_ids_by_preset.update(entry["formulas"]["explicit_id_formula_counts"].keys())
    census["formula_id_frequency_by_formula"] = dict(formula_ids.most_common())
    census["formula_id_frequency_by_preset"] = dict(formula_ids_by_preset.most_common())
    census["matrix_cells"] = {
        "total": sum(e["matrix"]["cells"] for e in entries),
        "empty_matrix_presets": sum(1 for e in entries if e["matrix"]["cells"] == 0),
        "max": max(e["matrix"]["cells"] for e in entries),
    }
    census["formula_counts"] = {
        "total": sum(e["formulas"]["count"] for e in entries),
        "no_formula_presets": sum(1 for e in entries if e["formulas"]["count"] == 0),
        "max": max(e["formulas"]["count"] for e in entries),
    }
    return census


def describe_description_asymmetry(paths: dict[str, str]) -> dict:
    """Account for the 723 description `.txt` against the 668 Module presets."""
    long_desc = read_long_descriptions(paths["descriptions"])
    per_device = {}
    for device in ("ContinuuMini", "Continuum", "EaganMatrixMicro", "EaganMatrixModule"):
        pattern = os.path.join(paths["firmware"], "SysPresets", device, "*.mid")
        per_device[device] = {os.path.splitext(os.path.basename(p))[0]
                              for p in glob.glob(pattern)}
    union = set().union(*per_device.values())
    module = per_device["EaganMatrixModule"]
    return {
        "files_in_folder": len(os.listdir(paths["descriptions"])),
        "description_txt_files": len(long_desc),
        "note": "the Descriptions folder is shared by all four device families and is not "
                "pruned when a preset is dropped; one of its entries is a desktop.ini, "
                "which is excluded from description_txt_files",
        "module_presets": len(module),
        "union_of_all_device_presets": len(union),
        "descriptions_matching_a_module_preset": len(long_desc & module),
        "module_presets_without_a_description": sorted(module - long_desc),
        "descriptions_for_other_device_families_only": sorted(
            (long_desc & union) - module),
        "descriptions_matching_no_current_preset_on_any_device": sorted(long_desc - union),
        "per_device_preset_counts": {k: len(v) for k, v in per_device.items()},
    }


def build_catalog(paths: dict[str, str]) -> tuple[dict, dict]:
    """Decode every factory preset and return (catalog, preset_index)."""
    slots = read_system_slots(paths["slot_manifest"])
    long_desc = read_long_descriptions(paths["descriptions"])
    entries = []
    failures = []
    for path in sorted(glob.glob(os.path.join(paths["presets"], "*.mid"))):
        try:
            entries.append(build_entry(path, slots, long_desc))
        except Exception as exc:                     # a decode failure must be visible
            failures.append({"file": os.path.basename(path), "error": repr(exc)})
    entries.sort(key=lambda entry: entry["system_slot"] or 10_000)
    _annotate_category_index(entries)
    catalog = {
        "device": "EaganMatrix Module",
        "firmware": "10.81",
        "source": {key: paths[key] for key in ("presets", "descriptions", "slot_manifest")},
        "compression_rule": "docs/HakenMidi.h:478-480 - ccStore writes only parameters that "
                            "differ from default, archives included. An absent setup id means "
                            "DEFAULT, not blank and not zero. Every setup field here is null "
                            "when absent; setup_explicit_ids lists what the file actually set.",
        "timing_warning": "eagan_mcp/server.py zeroes every delta time on save, so the "
                          "corpus supports no timing claims.",
        "counts": {"presets": len(entries), "failures": len(failures)},
        "failures": failures,
        "description_asymmetry": describe_description_asymmetry(paths),
        "census": build_census(entries),
        "presets": entries,
    }
    return catalog, build_preset_index(entries)


# ------------------------------------------------- the shipped, corrected-view catalog

# The 14 descriptive and 5 roll-up fields the shipped record passes through unchanged. The
# other 6 of its 25 fields are resolved below. `implicit_defaults` is deliberately NOT among
# them: the shipped catalog APPLIES the compression rule rather than shipping it, and
# `bank_in_use` takes its place (D5.2, A2.13 m19).
SHIPPED_DESCRIPTIVE_KEYS = (
    "name", "file", "system_slot", "flat_preset_number", "generation", "firmware",
    "category_main_tag", "category_main_name", "category_menu_index", "category_tags",
    "category_tag_names", "category_index", "author", "macro_labels",
    "has_long_description",
)
SHIPPED_ROLLUP_KEYS = (
    "modules_used", "modules_used_including_defaults", "dsp_heavy_modules",
    "dsp_cost_classes", "techniques",
)

# The 49 factory presets the shipped catalog carries cell-level wiring for: every preset
# named in the 43 `###` worked-example blocks of the research finding
# `analysis/findings/corpus-module-wiring.md`. 43 blocks name 49 presets because nine
# headings name 2-4 of them, six names repeat across sections and `18d. Convolution` names
# none - so C6's "43" is the block count, not the preset count (spec A2.6 M1).
# That markdown is the SELECTION LIST ONLY. Every value in a wiring block is decoded from
# the preset file by this module; nothing is transcribed from the prose.
WIRING_PRESETS = (
    "Additive Gnilham", "Additive Horn 1 Wbl", "Additive Vocal 1 Transform",
    "AllPass Metal Sheet", "Basic LeCaine", "Bass Monster", "Bell Rub", "Bells of Digul",
    "BiqMouth - Basic", "Bird Echoer", "Bird Whistler Wbl", "Boson Particles Wbl",
    "Bowed BiqBank", "Bowed KinBanjo", "Bowed OtherMood", "BuzzStrings",
    "CVC 10v Linear Z", "CVC Four Shape Generators", "Cascade", "Choir and Ext",
    "Cowell Triangles", "Cycle Kalimba", "Drum-Machine", "Drum-Machine Windowed",
    "Dueling BiqBanks", "Electric Guitar", "FM Bells", "Hal Dreams of Macros",
    "Harmonic Viol", "Harmonoid Spark", "Instant Reich", "Kinetic SatPad", "Koto",
    "MicroDelay WaveGuide v1", "Model String Wind", "Organzilla", "Ping Pong",
    "Resonant Drum 2", "Shimmer Wbl", "Should I Stay or Should I Go", "Silver Bar",
    "SineBank - Basic", "Soundboard 2", "Space Jaw", "Squaresville", "The Long Goodbye",
    "Touch Reed T", "Underwater Ceramics", "Voyager",
)

# The cell values that name a formula, taken from the shared table rather than restated:
# matA..matV' are matrix_map.MAT_VALUES[1:45]. matW/matX/matY/matZZ, matDec and mat1..mat9
# are sources and constants, so a cell holding one of those expands to nothing.
FORMULA_LETTERS = frozenset(matrix_map.MAT_VALUES[1:45])


def _resolved_type(field: dict, default: str) -> str:
    """An explicit-only `{explicit, raw, type}` triple, read as the device will run it.

    The whole point of the shipped catalog: an absent id is the default, not a blank, so
    this never returns None. An id the file DID set but whose value no table names keeps the
    decoder's visible `?<n>` (`codec-conventions.md:14-15`) instead of being silently
    reported as the default, which would hide a firmware change.
    """
    if not field["explicit"]:
        return default
    return field["type"] or f"?{field['raw']}"


def shipped_record(entry: dict) -> dict:
    """One full catalog entry, trimmed to the 25 shipped fields and corrected.

    Six fields change shape. `banks`, `oscillators`, `shape_generators` and `recirculator`
    collapse from `{explicit, raw, type}` triples to the plain type string the device runs,
    `polyphony` to three resolved values, and `implicit_defaults` is replaced by
    `bank_in_use`. That collapse is both the correction and most of the size saving.

    `bank_in_use` is `wired_in_matrix`, not `counts_as_in_use`: the latter is true only for
    a bank running on its DEFAULT type, so an explicitly-set WaveBank would read `false` and
    the field would invert exactly the truth it exists to carry.
    """
    banks = entry["banks"]
    wired = entry["implicit_defaults"]["banks"]
    poly = entry["polyphony"]
    record = {key: entry[key] for key in SHIPPED_DESCRIPTIVE_KEYS}
    record["banks"] = {
        slot: _resolved_type(banks[slot],
                             DEFAULT_BANK_C_TYPE if slot == "C" else DEFAULT_BANK_AB_TYPE)
        for slot in "ABC"}
    record["bank_in_use"] = {slot: wired[slot]["wired_in_matrix"] for slot in "ABC"}
    record["oscillators"] = [_resolved_type(slot, DEFAULT_OSC_TYPE)
                             for slot in entry["oscillators"]]
    record["polyphony"] = {
        "base": poly["base"] if poly["base_explicit"] else DEFAULT_POLY_BASE,
        "base_from_default": not poly["base_explicit"],
        "expanded": bool(poly["expanded"]),
        "double_computation_rate": bool(poly["double_computation_rate"]),
    }
    record["recirculator"] = _resolved_type(entry["recirculator"], DEFAULT_RECI_TYPE)
    record["shape_generators"] = [_resolved_type(sg, DEFAULT_SG_TYPE)
                                  for sg in entry["shape_generators"]]
    record.update({key: entry[key] for key in SHIPPED_ROLLUP_KEYS})
    return record


# A formula no id of which the file set: the baseline every shipped formula is reported
# against. `formula.decode({})` is the device's own reading of an omitted id, so nothing
# here restates a default (`codec-conventions.md:24-31`).
DEFAULT_FORMULA = formula.decode({})


def _non_default(section: dict, default: dict) -> dict:
    """The entries of one decoded formula section that this preset actually chose."""
    chosen = {}
    for key, value in section.items():
        if isinstance(value, dict):
            inner = _non_default(value, default[key])
            if inner:
                chosen[key] = inner
        elif value is not None and value != default[key]:
            chosen[key] = value
    return chosen


def _wiring_formula(form: dict) -> dict:
    """One formula letter, expanded far enough to be read without the device.

    An ACTIVE component is carried in full, because its mode, transfer and multiplier are
    needed to read its heights. Everything else is carried as the difference from the
    all-default formula, which is the same compression rule the catalog resolves, applied to
    presentation: what the preset chose, and nothing it merely inherited.

    The difference matters. 19 of the 563 letters in the shipped wiring blocks have no active
    component at all and are nonetheless doing work - `Shimmer Wbl`'s `I` carries its value
    on the SECONDARY W slider (`HeightW2`) under a blend, and `The Long Goodbye`'s `I` sets a
    buffer and a shape on a W whose primary slider is zero. Dropping an inactive component
    wholesale would have expanded those cells to "(all components zero)".

    `formula.summary` is the single human rendering (`codec-conventions.md:24-31`) and it
    renders the four primary components only, so for such a letter the summary reads as
    empty while the fields below carry the content. Heights are in the corrected offset
    reading by construction: this reads `formula.decode`'s output, and `slider_value` is the
    one sign-encoding site.
    """
    out = {"summary": formula.summary(form), "operator": form["operator"]}
    for name in "WXYZ":
        component = form[name]
        if component["active"]:
            out[name] = {key: value for key, value in component.items()
                         if key != "active" and value is not None}
        else:
            chosen = _non_default(component, DEFAULT_FORMULA[name])
            chosen.pop("active", None)
            if chosen:
                out[name] = chosen
    for section in ("w_zone", "ancillary", "blend", "secondary", "shaping"):
        chosen = _non_default(form[section], DEFAULT_FORMULA[section])
        if chosen:
            out[section] = chosen
    if form["unknown_ids"]:
        out["unknown_ids"] = form["unknown_ids"]
    return out


def _wiring_notes(decoded: dict, cells: list[dict], letters: dict, entry: dict) -> str:
    """What a reader of this block needs told that the cells and letters do not say."""
    parts = [f"{len(cells)} matrix cells, {len(letters)} formula letters"]
    muted = sum(1 for cell in cells if cell["muted"])
    if muted:
        parts.append(f"{muted} muted")
    macros = []
    for letter in sorted(letters):
        form = decoded["formulas"].get(letter)
        if not form:
            continue
        used = [form["W"]["macro"]] if "Macro" in form["W"]["modifier"] else []
        used += [form[name]["macro"] for name in "XYZ" if form[name]["macro"] != "none"]
        for macro in used:
            if macro not in macros:
                macros.append(macro)
    if macros:
        # A description labels macros v and vi under either naming, never both, so the
        # aliases are folded before the lookup or half the labels go missing.
        labels = {MACRO_SLOT_ALIASES.get(slot, slot): label
                  for slot, label in entry["macro_labels"].items()}
        parts.append("macros driven: " + ", ".join(
            macro + (f" ({labels[macro]})" if macro in labels else "") for macro in macros))
    if decoded["generation"] == "legacy":
        parts.append("legacy file: it carries no SG type, row type or master-column "
                     "selector at all, so those read as the device default rather than as "
                     "something this preset chose")
    return "; ".join(parts)


def wiring_block(path: str, entry: dict, resolved: dict) -> dict:
    """Cell-level wiring for one worked-example preset, decoded from its own file.

    `resolved` is this preset's `shipped_record`, whose bank types label the bank columns -
    a compressed preset's own setup leaves them unset, and `matrix_map.preset_labels` then
    falls back to "meaning depends on bank type", which is the wrong label for a bank that
    is running on the default.

    Cells read `column <- row = value`, the orientation `set_matrix_point(row, col, value)`
    takes. A block quoted the other way round teaches a skill to swap the two arguments.
    """
    decoded = decode_preset_file(path)
    preset_setup = decoded["setup"]
    labels = matrix_map.preset_labels(dict(preset_setup, banks=resolved["banks"]))
    cells = [{
        "row": cell["row"],
        "col": cell["col"],
        "value": cell["label"],
        "row_name": matrix_map.row_name(cell["row"], labels),
        "col_name": matrix_map.col_name(cell["col"], labels),
        "muted": cell["disabled"],
    } for cell in decoded["matrix"]]

    letters = {}
    for letter in sorted({cell["value"] for cell in cells} & FORMULA_LETTERS):
        # A formula every one of whose ids equals the default is absent from the file while
        # the cell still names it, so the all-default decode is what the device runs.
        letters[letter] = _wiring_formula(decoded["formulas"].get(letter)
                                          or decode_formula({}))

    # Explicit-only, from the record: a master column the preset never assigned says nothing
    # about it, and 1 of the 49 assigns one at all.
    master = {str(column["column"]): column["target"] or f"?{column['raw']}"
              for column in entry["master_columns"]}
    osc_wired = entry["implicit_defaults"]["oscillator_slots"]
    block = {
        "generation": decoded["generation"],
        "firmware": decoded["firmware"]["text"],
        "setup": {
            "banks": {slot: resolved["banks"][slot] for slot in "ABC"
                      if resolved["bank_in_use"][slot]},
            # Bank A's and B's accessories, for the banks this preset actually wires: the
            # decoded view names a parameter for every slot, so an unwired bank would
            # otherwise read as though it had been set up.
            "bank_param": {slot: params["param"]
                           for slot, params in preset_setup["bank_params"].items()
                           if params["param"] and resolved["bank_in_use"][slot]},
            "oscillators": {str(slot): resolved["oscillators"][slot - 1]
                            for slot in range(1, 6)
                            if osc_wired[str(slot)]["wired_in_matrix"]},
            "recirculator": resolved["recirculator"],
            "master_columns": master,
        },
        "cells": cells,
        "letters": letters,
    }
    if preset_setup["delay_time_select_raw"] is not None:
        block["setup"]["delay_time_select_raw"] = preset_setup["delay_time_select_raw"]
    block["notes"] = _wiring_notes(decoded, cells, letters, entry)
    return block


def build_shipped_catalog(catalog: dict, presets_dir: str) -> dict:
    """The committed catalog: 668 corrected 25-field records, 49 of them with `wiring`.

    This is the file every skill and knowledge document reads, which is why the compression
    rule is applied HERE: an absent setup id means the device default (`HakenMidi.h:478-480`)
    and a consumer that reads a raw `null` as "nothing" inverts the truth. Resolving it once
    at build time is what stops 18 module cards from each re-implementing the rule.
    """
    wanted = set(WIRING_PRESETS)
    records = []
    decoded = set()
    for entry in catalog["presets"]:
        record = shipped_record(entry)
        if entry["name"] in wanted:
            record["wiring"] = wiring_block(
                os.path.join(presets_dir, entry["file"]), entry, record)
            decoded.add(entry["name"])
        records.append(record)
    if decoded != wanted:
        raise RuntimeError(
            "worked-example presets missing from the corpus: "
            f"{sorted(wanted - decoded)}. The wiring blocks must cover all "
            f"{len(wanted)} presets named in corpus-module-wiring.md; check that "
            "HAKEN_EDITOR_DIR points at a Haken Editor 1081 installation")
    return {
        "device": catalog["device"],
        "firmware": catalog["firmware"],
        "source": "Haken Editor 1081, Firmware/SysPresets/EaganMatrixModule",
        "counts": {"presets": len(records), "failures": catalog["counts"]["failures"],
                   "wiring_blocks": len(decoded)},
        "record_shape": "25 fields per preset, plus `wiring` on the "
                        f"{len(decoded)} worked examples. The full 42-field decode, with "
                        "the matrix, the formulas and the raw setup values of all "
                        f"{len(records)} presets, is factory_catalog_full.json, which is "
                        "regenerable and not committed.",
        "compression_rule_resolved": "ccStore writes only the parameters that differ from "
                                     "default, archives included (docs/HakenMidi.h:478-480), "
                                     "and wire value 0 of the bank and oscillator type ids "
                                     "is a real module. So an absent id means THIS module, "
                                     "not none. banks, oscillators, shape_generators, "
                                     "recirculator and polyphony below are already resolved "
                                     "and are never null: read them directly, and do not "
                                     "re-apply the rule.",
        "resolved_defaults": {
            "banks": {"A": DEFAULT_BANK_AB_TYPE, "B": DEFAULT_BANK_AB_TYPE,
                      "C": DEFAULT_BANK_C_TYPE},
            "oscillator_slots": DEFAULT_OSC_TYPE,
            "shape_generators": DEFAULT_SG_TYPE,
            "recirculator": DEFAULT_RECI_TYPE,
            "polyphony_base": DEFAULT_POLY_BASE,
            "polyphony_base_evidence": "UNDOCUMENTED. docs/HakenMidi.h:1357 defines idPoly "
                                       "as values 1..8 and :1370 names defBendRange for "
                                       "idBendRange, but the header defines no defPoly. The "
                                       "documented floor is used so the field is never "
                                       "null, and the records that inherit it carry "
                                       "polyphony.base_from_default = true. Settles on the "
                                       "device: load one of them and read cc72.",
            "type_versus_use": "a resolved type says what the device RUNS in that slot, not "
                               "that the preset uses it. bank_in_use says so for the three "
                               "banks; for an oscillator slot, a shape generator or the "
                               "recirculator, the matrix cells decide, and only the 49 "
                               "wiring blocks carry those.",
        },
        "cell_orientation": "a wiring cell reads `column <- row = value`, which is the "
                            "orientation set_matrix_point(row, col, value) takes.",
        "wiring_selection": "the presets worked through in the research finding "
                            "corpus-module-wiring.md: 43 example blocks naming "
                            f"{len(decoded)} distinct presets. Every value in a block is "
                            "decoded from the preset file, not transcribed from that prose.",
        "presets": records,
    }


def main() -> int:
    """Rebuild the factory catalog and its four auxiliary artifacts from HAKEN_EDITOR_DIR.

    Usage: eagan_catalog [output-directory]. The output directory defaults to the current
    working directory and is reported as an absolute path - the artifacts never land "next
    to this module" inside the installed package.

    Five files are written:

      factory_catalog_full.json   all 42 decoded fields per preset, ~3.4 MB. Regenerable
                                  and gitignored: it is the mining input, not shipped data.
      factory_catalog.json        the shipped catalog, written compact: 25 corrected fields
                                  per preset, with the compression rule already applied, and
                                  cell-level `wiring` for the 49 worked-example presets.
      preset_index_1081.json      category -> index -> name, both candidate collations.
      census.json                 the roll-up counts, and the allowlist source for
                                  search_factory_presets' category/module/technique enums.
      descriptions.json           preset name -> long-form description text.

    All but the first are committed under `eagan_mcp/knowledge/`, so the catalog, text
    search and the enum allowlists work on a fresh clone with no Haken Editor installed.
    The full catalog and the shipped one are two different files on purpose: writing both
    under one name would make a rebuild destroy the committed artifact.
    """
    out_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    paths = source_paths()
    if not os.path.isdir(paths["presets"]):
        print(f"preset folder not found: {paths['presets']}\n"
              "set HAKEN_EDITOR_DIR to the Haken Editor installation", file=sys.stderr)
        return 2
    if not os.path.isdir(out_dir):
        print(f"output directory not found: {out_dir}", file=sys.stderr)
        return 2
    catalog, index = build_catalog(paths)
    census = dict(device=catalog["device"], firmware=catalog["firmware"],
                  **catalog["census"])
    descriptions = build_descriptions(catalog["presets"], paths["descriptions"])
    shipped = build_shipped_catalog(catalog, paths["presets"])
    written = []
    # The shipped catalog is the one file written compact: its size is measured against a
    # 1.5 MiB budget, so indentation would be a third of the budget spent on whitespace.
    for filename, payload, indent in (("factory_catalog_full.json", catalog, 1),
                                      ("factory_catalog.json", shipped, None),
                                      ("preset_index_1081.json", index, 1),
                                      ("census.json", census, 1),
                                      ("descriptions.json", descriptions, 1)):
        target = os.path.join(out_dir, filename)
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=indent, sort_keys=False,
                      separators=None if indent else (",", ":"))
        written.append(target)

    print(f"presets: {catalog['counts']['presets']}  "
          f"failures: {catalog['counts']['failures']}")
    for target in written:
        print(f"wrote {target} ({os.path.getsize(target)} bytes)")
    print("\nregression checks against the four device observations:")
    for check in index["regression_checks"]:
        print("   %-24s %-26s device=%s filename=%s name=%s %s" % (
            check["category_tag"], check["name"], check["device_index"],
            check["filename_collation_index"], check["name_collation_index"],
            "PASS" if check["pass"] else "FAIL"))
    print("\ncategory sizes:", {k: v["count"] for k, v in
                                index["by_filename_collation"].items()})
    print("\nsearch allowlist sizes (census.json is the source):")
    for key in ("category_main", "modules_used_including_defaults", "techniques"):
        print(f"   {key:36} {len(census[key])}")
    print(f"\ndescriptions: {len(descriptions)} of {catalog['counts']['presets']} presets")
    shipped_bytes = os.path.getsize(os.path.join(out_dir, "factory_catalog.json"))
    print(f"\nshipped catalog: {shipped_bytes} bytes compact, "
          f"{shipped_bytes / 1048576:.3f} MiB of the 1.5 MiB budget, "
          f"{shipped['counts']['wiring_blocks']} wiring blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
