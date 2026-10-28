# Device Safety

Rules that protect the EaganMatrix Module's persistent memory and the user's unsaved
work. These are hard constraints: a wrong store overwrites a factory preset or destroys
the edit slot, and neither is recoverable from this side of the USB cable.

### Writes Go to the Edit Slot Only

Write the edit slot. Never write a user preset slot or a system preset slot without the
user explicitly confirming that slot first. Enforce the rule in code, not just in prose:
give every flash-writing tool a `confirm: bool = False` parameter that returns a refusal
dict instead of acting, pre-scan whole payloads (e.g. preset files) and reject them
before the first byte goes out if they contain a store command, and state the write scope
("Edit slot only", "Not stored to flash", "Read-only") in the first lines of the
docstring. Put a never-send comment on the dangerous wire constant itself.

```python
if not confirm:
    return {"stored": False,
            "note": "not stored: ask the user to confirm the slot, then call with confirm=True"}
```

Source: `CLAUDE.md`, `README.md` ("Safety rule"); `server.py:494,500`, `server.py:169-175`, `haken.py:37`

### Never Send the System-Slot Store Path

Store to a user slot with ch16 `cc0=0`, `cc32=(N-1)>>7`, `cc112=(N-1)&127`. Never send
`cc0=127` — that is the system/factory slot path, valid only during an Update File 2
firmware write. Keep the warning on the constant so it cannot be reintroduced.

Source: `CLAUDE.md` ("NEVER cc0=127"); `haken.py:228-229`

### Never Verify a Store by Loading the Slot

Verify a store with the read-only user-preset listing (`cc109=32`, `list_user_presets`):
the slot's name must equal the current edit-slot name. Never load the target slot to
check it — loading replaces the unsaved edit slot and the sound is lost. The device's
echo after a save varies between saves and is not verification either.

Source: `CLAUDE.md` ("LESSON: do not verify a store by loading the slot"); `server.py:497-509`

### Check DSP Budget After Every Big Change

Call `get_status` (`dsp_usage_percent`, `dsp_polyphony`) after every substantial patch
change. Over budget, the Module silently runs fewer voices than configured, which the
user hears as sluggish knobs, pops and late notes. Apply the fixes in this order: drop a
heavy module (Ladder -> Low Pass Filter, PWM -> DSF), lower base polyphony by one while
keeping "+", then simplify formulas on oscillator F columns.

Source: `RECIPES.md` ("Pitfalls on the EM Module"); EaganMatrix User Guide 10.81 sec. 8.5

### Respect the Documented Patch-Construction Pitfalls

Follow the numbered pitfall rules in `RECIPES.md` when building patches: share one
drift/vibrato LFO instead of one per oscillator; keep macros off oscillator F columns;
avoid Direct x on oscillator F columns when the panel must stay responsive; state the
trade-off for pitch-proportional detune and let the user choose; build bendable strings
as a tuned resonator bank (BiqBank), not a delay loop; and build around Y for the mod
wheel (CC 1 arrives as Y) rather than asking the user to remap their keyboard. Always
give a Continuous/Single Cycle SG its T column, and never leave sB empty.

Source: `RECIPES.md` ("Pitfalls on the EM Module", "Strings and plucks"); `CLAUDE.md`
