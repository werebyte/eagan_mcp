# Codec Conventions

How the pure wire-translation modules (`formula.py`, `setup.py`, `matrix_map.py`,
`haken.py`) declare their tables and name their functions.

### Lookup Tables Shaped Like the Wire

Declare a value table so the data structure itself encodes the wire mapping: a list when
the device's values are a contiguous 0-based enumeration (the index IS the wire value, so
`index()` and `[v]` are the codec), a dict keyed by wire value when they are sparse or
reordered. Name by wire role: `CC_*` for controller numbers, `CMD_*` for command values,
`*_ID` for a single poke id, `*_IDS` for a per-slot list indexed by `slot - 1`, and a
plural table name for value->name maps. Generate repeated blocks with loops and derive
reverse maps rather than duplicating them. Decode an unknown value to a visible `?<n>`
marker — never raise, never drop it.

```python
W_MODES = ["Constant", "Gated", "SG1", ...]             # index == wire value
OSC_TYPES = {0: "DSF Oscillator", 18: "PWM Oscillator"}  # sparse: keyed by wire value
```

Source: `formula.py`, `setup.py`, `matrix_map.py:26-36`, `haken.py`

### Codec Function Naming by Direction

Make the direction of translation visible in the name, and give each wire stream exactly
one entry point. `decode*` takes raw messages or an `{id: value}` dict and returns plain
Python. `encode*`, `*_msgs` and `*_value` go the other way: `*_msgs` returns a
ready-to-send `list[mido.Message]`, `*_value` resolves a human name to a wire number.
Stream codecs share the identical signature `decode(pairs: dict[int, int]) -> dict`.
Render decoded data for humans in a separate `summary()`, never inside the decoder.

```python
def decode(pairs: dict[int, int]) -> dict:                        # wire -> python
def encode_changes(component: str, **kw) -> list[tuple[int, int]]:  # python -> wire
```

Source: `haken.py:54,64,110,162,221,233,245`; `formula.py:74,110,146`; `setup.py:56,82`
