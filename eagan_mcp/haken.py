"""Haken config protocol: message building and parsing, no I/O.

Authoritative source since 10.81: docs/HakenMidi.h, shipped with the Haken Editor.
Where a controller predates the header it also appears in the Continuum User Guide,
section 15 "Configuration Controller Midi Encoding Assignments"
(docs/ContinuumUserGuide.txt, p.166-172).
Channel numbers here are 0-based (mido): ch16 = 15, ch15 = 14.

Matrix and formula editing over the live USB protocol is implemented here and in
server.py. The ch15 messages inside preset .mid files are a DIFFERENT format, decoded by
preset_file.py (the legacy generation, 422 of the 668 factory files, puts the matrix, the
setup block and the formulas on ch15 as bare cc); this module only passes them through."""

import mido

from . import matrix_map

CH16 = 15
CH15 = 14

# cc numbers on ch16
CC_CATEGORY = 0          # bank select = category, 0 = user presets
CC_PRESET_HI = 32        # high 7 bits of preset index within category
# NOTE: ch16 cc39 is NOT polyphony in 10.81 (reserved). Polyphony = s_Mat_Poke id 39 (setup.py).
CC_TEXT = 56             # ccStream (HakenMidi.h:1074): stream id follows as ch16 pressure or
                         # poly pressure pairs, end = STREAM_END
CC_PRESET_LSB = 57       # preset number attached to a name
CC_PRESET_MSB = 58
CC_FW_HI = 102
CC_FW_LO = 103
CC_COMMAND = 109         # multi-purpose command controller
CC_POLY_DSP = 72         # tx: actual DSP polyphony (HakenMidi.h ccPolyDsp)
CC_USAGE = 114           # tx after ping: 32*dsp# + 4%-units (0..25)
CC_LED = 111             # tx after ping: LED colour (low 4 bits) + AES bits
CC_PONG = 118            # tx after ping
CC_FORM_SEL = 34         # ccFormSel: formula that s_Form_Poke writes apply to
CC_EDITOR_PING = 116     # Editor sends this every second (any value, it alternates 85/42).
                         # Source: Haken Editor Max patch, "p Periodic Request".
                         # Without it the device does not stream presets over USB.

CMD_TRANSMIT_CONFIG = 16
CMD_TRANSMIT_NAMES = 32
CMD_STORE_CONFIG = 8     # writes flash, never send without user confirmation

# ccStream (CC_TEXT) stream ids. Source: docs/HakenMidi.h:1080-1149.
TEXT_PRESET_NAME = 0     # s_Name: ASCII preset name, max 32 data bytes
TEXT_PRESET_TEXT = 1     # s_ConText: ASCII preset description
TEXT_CATEGORY_NAME = 8   # SUSPECT: stream 8 is s_UpdF2 in 10.81 (HakenMidi.h:1097), not a
                         # category name. Unused; the name predates the header.
STREAM_FORM_POKE = 19    # s_Form_Poke (HakenMidi.h:1130): formula config (id, value) pairs
STREAM_MAT_POKE = 20     # s_Mat_Poke (HakenMidi.h:1132): matrix config (id, value) pairs
STREAM_END = 127         # s_StreamEnd (HakenMidi.h:1149): end of an sData stream

CATEGORIES = {
    0: "User", 1: "Strings", 2: "Winds", 3: "Vocal", 4: "Keyboard",
    5: "Classic", 6: "Other", 7: "Percussion", 8: "Tuned Percussion",
    9: "Processor", 10: "Drone", 11: "Midi", 12: "Control Voltage", 13: "Utility",
}


def cc16(control: int, value: int) -> mido.Message:
    return mido.Message("control_change", channel=CH16, control=control, value=value)


def load_preset_msgs(category: int, index: int) -> list[mido.Message]:
    """index is 0-based within the category."""
    return [
        cc16(CC_CATEGORY, category),
        cc16(CC_PRESET_HI, index >> 7),
        mido.Message("program_change", channel=CH16, program=index & 0x7F),
    ]


def decode_texts(msgs: list[mido.Message]) -> list[dict]:
    """Collect cc56-tagged ASCII strings (sent as ch16 channel pressure,
    terminated by 127). cc57/58 after a name give its preset number."""
    out, current, kind = [], None, None
    # Observed in preset .mid files (not in the guide): ch16 cc110=121 starts
    # the preset, 123/124 end it; ch15 cc110=125/126 bracket a block of
    # ch15 cc102/103/104 triples (probably matrix data). Unverified.
    def flush():
        nonlocal current
        if current:
            out.append({"kind": kind, "text": "".join(map(chr, current))})
        current = None

    for m in msgs:
        is_text_byte = m.type == "aftertouch" and m.channel == CH16
        if is_text_byte:
            if current is None:  # preset files send text without a cc56 tag
                current = []
            if m.value == 127:  # terminator per the guide
                flush()
            else:
                current.append(m.value)
            continue
        flush()  # preset files end text with ch15 pressure 0, or just move on
        if m.type == "control_change" and m.channel == CH16:
            if m.control == CC_TEXT:
                kind = m.value
            elif m.control == CC_PRESET_LSB and out:
                out[-1]["preset_lsb"] = m.value
            elif m.control == CC_PRESET_MSB and out:
                out[-1]["preset_msb"] = m.value
    flush()
    return out


def firmware_version(msgs: list[mido.Message]) -> int | None:
    hi = lo = None
    for m in msgs:
        if m.type == "control_change" and m.channel == CH16:
            if m.control == CC_FW_HI:
                hi = m.value
            elif m.control == CC_FW_LO:
                lo = m.value
    return None if hi is None or lo is None else (hi << 7) | lo


def decode_live_streams(msgs: list[mido.Message]) -> list[dict]:
    """Decode the live (USB) preset dump: ch16 cc56 = stream id, followed by
    ch16 poly pressure pairs (note, value) = 2 data bytes each; stream 127 ends.
    Observed on EM Module fw 10.x, 2026-10-25. Stream 0 = name, 1 = description.
    Other stream ids are binary, meaning unknown until HakenMidi.h."""
    out, cur = [], None
    for m in msgs:
        if m.type == "control_change" and m.channel == CH16 and m.control == CC_TEXT:
            if cur is not None and cur["id"] != 127:
                out.append(cur)
            cur = {"id": m.value, "bytes": []}
        elif m.type == "polytouch" and m.channel == CH16 and cur is not None:
            cur["bytes"] += [m.note, m.value]
    if cur is not None and cur["id"] != 127:
        out.append(cur)
    for st in out:
        if st["id"] in (0, 1):
            st["text"] = "".join(chr(b) for b in st["bytes"] if 32 <= b < 127 or b == 10).strip()
    return out


# ---------------- matrix (live USB format, fw 10.x) ----------------
# Source: Haken Editor 1044, HE MatrixPlotter.maxpat "p FormulaMidi":
#   route 45 34 40 41 44 43 42 on ch16
#   cc45 = control (126 start matrix send, 125 clear, 115 = Editor selects point)
#   cc40 = row (CRN), cc41 = column (CCN), cc44 = value (CVN)
#   cc44: low 6 bits = code, bit 6 (+64) = muted
#     0 blank, 1..22 A..V, 23..44 A'..V', 45..48 W..Z, 49 decimal, 50..58 = 1..9
#   decimal: cc43 = digits 1-2, cc42 = digits 3-4 (cc43 resets cc42 to 0), then cc44=49
CC_MATRIX_CTRL = 45
CC_ROW = 40
CC_COL = 41
CC_VALUE = 44
CC_DIGITS_HI = 43
CC_DIGITS_LO = 42
MATRIX_START = 126


def value_code_to_str(code: int) -> str:
    """Wire code -> cell label, from the one header-faithful table.

    Reads matrix_map.MAT_VALUES rather than recomputing the ranges. The hand-rolled version
    this replaces returned "Z" for code 48, but docs/HakenMidi.h:758 defines matZZ = 48 as
    "z squared" and there is NO plain Z code - so it mislabelled 36 shipped cells and told
    callers to write a squared pressure curve when they asked for pressure.
    """
    if 0 <= code < len(matrix_map.MAT_VALUES):
        return matrix_map.MAT_VALUES[code]
    return f"?{code}"


def decode_matrix(msgs: list[mido.Message]) -> list[dict]:
    """Return matrix points [{row, col, value, muted}] from a live dump."""
    points, row, col, hi, lo, active = [], None, None, 0, 0, False
    for m in msgs:
        if m.type != "control_change" or m.channel != CH16:
            continue
        c, v = m.control, m.value
        if c == CC_MATRIX_CTRL:
            active = v == MATRIX_START
            continue
        if not active:
            continue
        if c == CC_ROW:
            row = v
        elif c == CC_COL:
            col = v
        elif c == CC_DIGITS_HI:
            hi, lo = v, 0
        elif c == CC_DIGITS_LO:
            lo = v
        elif c == CC_VALUE:
            code = v & 63
            if code == 49:
                value = ("." + f"{hi * 100 + lo:04d}").rstrip("0")
            else:
                value = value_code_to_str(code)
            points.append({"row": row, "col": col, "value": value, "muted": bool(v & 64)})
    # One listen window can catch TWO dumps - e.g. a preset load's own dump plus a matRefresh -
    # and the same cell then appears twice. Measured on the device 2026-10-27: 50 decoded cells
    # for a 25-cell patch, every one duplicated. Keep the LAST reading of each cell, which is the
    # most recent state, so a caller cannot mistake duplicates for a bigger matrix.
    seen: dict[tuple[int, int], dict] = {}
    for p in points:
        seen[(p["row"], p["col"])] = p
    return list(seen.values())


CMD_SELECT_POINT = 115
CMD_TOGGLE_MUTE = 121
CMD_MATRIX_REFRESH = 124  # ccMatOp matRefresh: asks for matrix + formulas + text now.
                          # THE read trigger on fw 10.81 - a bare select returns nothing.


def encode_value(value: str) -> list[tuple[int, int]]:
    """Value string -> list of (cc, value) to send after selecting a point.
    Accepts: "" (delete), "A".."V", "A'".."V'", "W"/"X"/"Y", "z^2", "row^2", "row^3", "1".."9",
    ".5", ".05", ".1234" (4 decimal places max)."""
    v = value.strip().upper()
    if v == "":
        return [(CC_VALUE, 0)]
    if len(v) == 1 and "A" <= v <= "V":
        return [(CC_VALUE, ord(v) - 64)]
    if len(v) == 2 and v[1] == "'" and "A" <= v[0] <= "V":
        return [(CC_VALUE, ord(v[0]) - 64 + 22)]
    if len(v) == 1 and v in "WXY":
        return [(CC_VALUE, 45 + "WXY".index(v))]
    if v in ("Z^2", "Z2", "ZZ"):
        return [(CC_VALUE, 48)]                      # matZZ, docs/HakenMidi.h:758
    if v in ("ROW^2", "ROW2"):
        return [(CC_VALUE, 59)]                      # matSq, docs/HakenMidi.h:763
    if v in ("ROW^3", "ROW3"):
        return [(CC_VALUE, 60)]                      # matCu, docs/HakenMidi.h:764
    if v == "Z":
        raise ValueError(
            "there is no plain Z matrix value: docs/HakenMidi.h:758 defines code 48 as matZZ, "
            "'z squared'. Write 'z^2' if you want the squared pressure curve. If you wanted "
            "linear pressure, that is a FORMULA component, not a cell value - place a formula "
            "letter in the cell and set its Z component with set_formula(component='Z', ...)")
    if len(v) == 1 and "1" <= v <= "9":
        return [(CC_VALUE, 49 + int(v))]
    if v.startswith("0."):
        v = v[1:]
    if v.startswith(".") and v[1:].isdigit() and 1 <= len(v) - 1 <= 4:
        digits = v[1:].ljust(4, "0")
        n = int(digits)
        if n == 0:
            raise ValueError("zero: use '' to delete the point")
        return [(CC_DIGITS_HI, n // 100), (CC_DIGITS_LO, n % 100), (CC_VALUE, 49)]
    raise ValueError(f"unsupported matrix value {value!r}")


def select_point_msgs(row: int, col: int) -> list[mido.Message]:
    return [cc16(CC_COL, col), cc16(CC_ROW, row), cc16(CC_MATRIX_CTRL, CMD_SELECT_POINT)]



# ---------------- text out, store (Editor 1044 "p TextOut", "p BankHiLoPgmOut") ----------------
CC_STORE_LO = 112        # preset lo for store; with cc0 + cc32=hi
# Editor "p BankHiLoPgmOut": user slot N -> cc0=0, cc32=0, cc112=N-1.
# cc0=127 is the SYSTEM slot path (factory update only). Never use it.
STORE_CATEGORY_USER = 0


def text_stream_msgs(stream_id: int, text: str) -> list[mido.Message]:
    """cc56=id, ASCII as ch16 poly pressure pairs (note=char1, value=char2), zero pad, cc56=127."""
    data = [ord(c) & 0x7F for c in text]
    if len(data) % 2:
        data.append(0)
    out = [cc16(CC_TEXT, stream_id)]
    for i in range(0, len(data), 2):
        out.append(mido.Message("polytouch", channel=CH16, note=data[i], value=data[i + 1]))
    out.append(cc16(CC_TEXT, STREAM_END))
    return out


def store_user_slot_msgs(slot: int) -> list[mido.Message]:
    """Store current sound to user slot 1..128 (flash)."""
    if not 1 <= slot <= 128:
        raise ValueError("user slot must be 1..128")
    n = slot - 1
    return [cc16(CC_CATEGORY, STORE_CATEGORY_USER), cc16(CC_PRESET_HI, n >> 7), cc16(CC_STORE_LO, n & 127)]
