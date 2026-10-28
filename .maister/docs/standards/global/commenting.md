## Commenting

### Let Code Speak
Write code that explains itself through structure and naming.

### Comment Sparingly
Add brief comments only when the logic isn't self-evident from the code.

Docstrings go on the public surface only: all 32 exposed MCP tools have one, and of the 14 private underscore helpers in `server.py` just one does (`_select_and_read`, where the return value carries a second stream and the signature cannot say so). Non-tool public functions get a docstring only when the wire format needs stating (46 of 64 package-wide; the ratio rose with `preset_file.py`, whose decoders each state the layout they read).

A tool docstring is not decoration — it is the prompt the agent reads to decide whether and how to call the tool. So it must state:
- the **write scope**, explicitly: "Edit slot only, verified by read-back." / "Read-only."
- units, ranges and the exact accepted enum strings: `value (-1..1.27, step 0.01)`, `magnitude: ONE OF 0.001 ... 1000 (powers of ten only)`
- safety warnings for destructive or device-affecting paths.

These run long where the parameter space is large — the longest is 55 lines and enumerates every accepted query field and its matching rule (`search_factory_presets`, `server.py:786-841`); `set_formula` is the next longest for the same reason, enumerating every accepted enum value. That length is correct here: an under-specified docstring causes wrong device writes.

### No Change Comments
Avoid comments about recent fixes or changes; comments should be timeless explanations, not changelogs.
