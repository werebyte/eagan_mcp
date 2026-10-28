"""F5: the X transfer function defaults to kHz, not to Octaves, from ONE site.

`idTransX` (stream-19 id 85) selects X's transfer function. `formula.decode` read an absent
id 85 as wire value 0 = "X Oct", so 334 of the factory formulas that leave it absent read
back as "Octaves" where the device means kHz. The evidence is a corpus statistic [C], not a
device observation: across the 668 factory presets shipped with Haken Editor 1081,
`TransX = 0` is written explicitly 775 times and `TransX = 1` exactly zero times, and a
stored preset carries "only parameters that differ from default" (docs/HakenMidi.h:478-480),
so the value that is never written is the default. Per protocol-sources.md a [C] figure can
never upgrade to [D]: nothing here says what the firmware does, only what Haken's own
presets never bother to write.

TWO THINGS THIS SUITE PINS, AND WHY EACH IS A SEPARATE TEST
-----------------------------------------------------------
1. The fix is a per-component DEFAULT, not a table reordering. `X_TRANSFER[0]` has to stay
   "X Oct" because `xOctaves = 0` on the wire (docs/HakenMidi.h:1235), and
   codec-conventions.md:6-15 makes the list index the codec: moving "X kHz" to index 0 to
   get the right default would silently corrupt every explicit write and read of id 85.
2. The default lives at exactly ONE site. F5 exists because the default was wrong in two
   places at once - `formula.decode` and the research tree's `preset_decode.py:720`, whose
   id-85 binding is at `:708`. Two copies of a default that agree today are the state that
   drifted in the first place, so `preset_file.decode_formula` must get the default by
   calling `formula.decode`, not by re-applying it afterwards.

The complementary property - that `preset_file.py` declares no stream-19 value table of its
own - is pinned by tests/test_shared_tables.py.
"""

import ast
from pathlib import Path

from eagan_mcp import formula, preset_file

TRANSFER_IDS = {name: formula.COMPONENTS[name]["transfer"] for name in "XYZ"}


def _source(module) -> str:
    return Path(module.__file__).read_text(encoding="utf-8")


def _transfer_default_loads(module) -> list[str]:
    """Every place `module`'s CODE reads TRANSFER_DEFAULT, as `<line>: <expression>`.

    AST, not text: a docstring or comment naming the constant documents where the default
    lives and is not a second site. Covers both the bare name (inside `formula.py`) and the
    `formula.TRANSFER_DEFAULT` attribute (from any consumer).
    """
    out = []
    for node in ast.walk(ast.parse(_source(module))):
        if isinstance(node, ast.Name) and node.id == "TRANSFER_DEFAULT" \
                and isinstance(node.ctx, ast.Load):
            out.append(f"{node.lineno}: {ast.unparse(node)}")
        elif isinstance(node, ast.Attribute) and node.attr == "TRANSFER_DEFAULT":
            out.append(f"{node.lineno}: {ast.unparse(node)}")
    return out


def _xyz_int_dict_literals(module) -> list[tuple[int, dict]]:
    """Literal `{"X": n, "Y": n, "Z": n}` dicts - the shape a second default would take."""
    out = []
    for node in ast.walk(ast.parse(_source(module))):
        if not isinstance(node, ast.Dict):
            continue
        try:
            value = ast.literal_eval(node)
        except (ValueError, TypeError, SyntaxError):
            continue
        if set(value) == set("XYZ") and all(isinstance(v, int) for v in value.values()):
            out.append((node.lineno, value))
    return out


def test_x_transfer_defaults_to_khz_when_id_85_is_absent():
    """An absent id 85 is kHz; an explicit 0 is still Octaves. Both decoders agree."""
    assert formula.decode({})["X"]["transfer"] == "X kHz", (
        "formula.decode still reads an absent idTransX as wire 0 = Octaves; 334 factory "
        "formulas leave id 85 absent and mean kHz")
    assert preset_file.decode_formula({})["X"]["transfer"] == "X kHz"

    explicit = formula.decode({TRANSFER_IDS["X"]: 0})
    assert explicit["X"]["transfer"] == "X Oct", (
        "an explicitly written TransX = 0 must still decode as Octaves - the fix is a "
        "default for an ABSENT id, not a remapping of wire value 0")
    assert preset_file.decode_formula({TRANSFER_IDS["X"]: 0})["X"]["transfer"] == "X Oct"
    assert formula.decode({TRANSFER_IDS["X"]: 2})["X"]["transfer"] == "Linear"


def test_y_and_z_transfer_default_to_linear():
    """Y and Z have no Octaves/kHz pair: yzLinear = 0 (docs/HakenMidi.h:1250) is the default."""
    decoded = formula.decode({})
    for name in "YZ":
        assert decoded[name]["transfer"] == "Linear", (
            f"{name} transfer defaults to {decoded[name]['transfer']!r}; idTrans{name} "
            "value 0 is yzLinear and is the only sane absent-id reading")
        assert preset_file.decode_formula({})[name]["transfer"] == "Linear"
        explicit = formula.decode({TRANSFER_IDS[name]: 1})
        assert explicit[name]["transfer"] == "Gentle S", (
            f"an explicit idTrans{name} = 1 must survive the default")
    assert formula.TRANSFER_DEFAULT == {"X": 1, "Y": 0, "Z": 0}


def test_x_transfer_table_index_zero_is_still_x_oct():
    """codec-conventions.md:6-15: the list index IS the wire value, so F5 must not reorder.

    `X_TRANSFER` follows idTransX xOctaves..xSteepS (docs/HakenMidi.h:1235) and `YZ_TRANSFER`
    follows idTransY yzLinear..yzSteepS (:1250). The two tables differ by exactly the two X-only
    entries at the front, which is why the default is per component rather than per table.
    """
    assert formula.X_TRANSFER[0] == "X Oct", (
        "X_TRANSFER was reordered to make kHz the index-0 default; the index has to stay "
        "equal to the wire value or every explicit id-85 read and write breaks")
    assert formula.X_TRANSFER[1] == "X kHz"
    assert formula.YZ_TRANSFER[0] == "Linear"
    assert formula.X_TRANSFER[2:] == formula.YZ_TRANSFER, (
        "X_TRANSFER must be YZ_TRANSFER with xOctaves and xKHz prepended")
    for table in (formula.X_TRANSFER, formula.YZ_TRANSFER):
        for wire_value, name in enumerate(table):
            assert table[wire_value] == name
            assert table.index(name) == wire_value, f"{name!r} is listed twice in {table}"

    # The default is expressed as a wire value, so it indexes its own component's table.
    assert formula.X_TRANSFER[formula.TRANSFER_DEFAULT["X"]] == "X kHz"
    assert formula.YZ_TRANSFER[formula.TRANSFER_DEFAULT["Y"]] == "Linear"
    assert formula.YZ_TRANSFER[formula.TRANSFER_DEFAULT["Z"]] == "Linear"
    # The write side resolves names against the same tables and is untouched by the default.
    assert formula.encode_changes("X", transfer="X Oct") == [(TRANSFER_IDS["X"], 0)]
    assert formula.encode_changes("X", transfer="X kHz") == [(TRANSFER_IDS["X"], 1)]
    assert formula.encode_changes("Y", transfer="Linear") == [(TRANSFER_IDS["Y"], 0)]


def test_transfer_default_has_exactly_one_definition_site():
    """One definition, one reader. `preset_file` gets the default by calling `formula.decode`.

    `formula.decode` is the single reader. `preset_file.decode_formula` carried an interim
    four-line patch loop that re-applied the same constant because the live decoder did not
    yet; with the live decoder fixed that loop is a second site which can drift, so it is
    gone. This test fails if it comes back.
    """
    assert not _xyz_int_dict_literals(preset_file), (
        "preset_file.py carries its own per-component default dict: "
        f"{_xyz_int_dict_literals(preset_file)}")
    in_formula = _xyz_int_dict_literals(formula)
    assert [value for _line, value in in_formula] == [formula.TRANSFER_DEFAULT], (
        "formula.py must hold exactly one {X,Y,Z} int dict, TRANSFER_DEFAULT itself; found "
        f"{in_formula}")
    assert not _transfer_default_loads(preset_file), (
        "preset_file.py's code reads formula.TRANSFER_DEFAULT at "
        f"{_transfer_default_loads(preset_file)}. The default now reaches the file decoder "
        "through formula.decode; re-applying it there is the second site F5 removed")
    assert len(_transfer_default_loads(formula)) == 1, (
        "TRANSFER_DEFAULT must be read in exactly one place, formula.decode; found "
        f"{_transfer_default_loads(formula)}")

    # The behavioural form of the same property: the file decoder adds nothing on top.
    for pairs in ({}, {TRANSFER_IDS["X"]: 0}, {TRANSFER_IDS["Y"]: 3, TRANSFER_IDS["Z"]: 9}):
        live = formula.decode(pairs)
        archived = preset_file.decode_formula(pairs)
        for name in "XYZ":
            assert archived[name]["transfer"] == live[name]["transfer"], (
                f"preset_file.decode_formula changes {name} transfer for {pairs}; the two "
                "decoders must read one default")
