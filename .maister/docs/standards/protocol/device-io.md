# Device I/O

The required shape of every read from and write to the Module over USB-MIDI: selection,
keepalive, bounded listen, and independent verification.

### Verify a Write With a Separate Independent Read

Do not believe a write until a separate read confirms it. The pattern is always: send,
short settle sleep (~0.2 s), issue a fresh read request, compare the device's value with
the requested one, and return both plus a boolean `verified`. Distrust and discard the
device's echo straight after a write — it is a partial dump that may stop before the
changed value and produce a false negative. For matrix cells, verify with a full read
(select cell 0,0) and a listen window of at least 2.5 s. Where the primary read cannot
observe the value, use a documented fallback read; where no read exists, say so in the
result rather than claiming success.

```python
conn.send(...)
time.sleep(0.2)
after = _read_setup()
return {"id": pid, "requested": value, "device_value": after.get(pid),
        "verified": after.get(pid) == value}
```

Source: `CLAUDE.md` ("the Module's echo right after a write is a partial matrix"); `server.py:390-396`, `server.py:219-223`, `server.py:504-509`

### Select the Target Before Writing, With No Traffic Between

Formula and matrix writes are addressed by selection, not by a field in the message.
Select the cell first (`cc41` column, `cc40` row, `cc45=115`), then send the change —
with no ping or other traffic in between, which has made a write fail. Reads use the same
idiom: selecting any cell makes the Module re-send the whole matrix, so state can be read
without reloading the preset.

Source: `CLAUDE.md` ("Write: select the cell FIRST", "A ping or other traffic between select and write made the write fail once")

### Retry Device Reads With a Longer Listen Window

The first read after a connect or a preset load can legitimately return nothing. When a
read comes back empty, retry with a longer window (~4 s) instead of reporting a failure,
and comment the reason at the retry site.

Source: `CLAUDE.md` ("get_matrix: first read after connect/load can be empty"); `server.py:206-208`

### Flush, Keepalive, Bounded Listen

Every read follows one sequence: clear the input buffer, send the Editor keepalive (the
device stays silent without it), send the request, then listen for a bounded time. Expose
the window as a `seconds: float` parameter with a per-operation default tuned to how much
the device sends, so a caller can widen it. Filter realtime noise (clock, active sensing)
out of the listen result, and flag truncation rather than silently dropping data.

```python
conn.clear()
_ping()
for m in haken.select_point_msgs(row, col):
    conn.send(m)
msgs = [m for _, m in conn.listen(seconds)]
```

Source: `server.py:79-80` and 7 other read paths; `midi_io.py:74-80`

### Pick an Unused Formula Letter and Check First

Formula letters are shared device-wide: editing one cell's formula changes every cell
that uses that letter. There are 44 available (A..V plus A'..V'), A..V preferred - the
primed letters exist on the wire (cell codes 23..44) but are the less travelled path, so
reach for an unprimed letter first and only move into A'..V' once A..V is exhausted. Pick
an unused letter for each new job and check with `get_matrix` which letters are already in
use before writing. Note that the Module omits all-zero cells from the matrix dump, so
fall back to reading the cell's formula number when the dump looks empty.

Source: `RECIPES.md` ("Formula letters are shared"); `CLAUDE.md` (the cell-code table,
"1..22 A..V, 23..44 A'..V'")
