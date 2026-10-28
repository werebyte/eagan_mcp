## Validation

### Server-Side Always
Validate on the server; client-side validation alone is insufficient for security and data integrity.

### Client-Side for Feedback
Use client-side validation for immediate user feedback, but duplicate checks server-side.

### Validate Early
Check inputs as early as possible and reject invalid data before processing.

**Validate arguments before touching the device.** Range and enum checks run at the top of a tool function, and a multi-part payload is pre-scanned in full, before a single byte of MIDI is emitted — so a bad call never leaves the device half-written. Encoding helpers validate too, which keeps the check next to the table that defines the limit. Correct example: `send_preset_file` pre-scans the whole file in a first pass and raises before sending anything, so a store command in the last message still stops the first one from going out. It screens the controllers that actually write flash — ch16 `cc112` (`ccStore`, `HakenMidi.h:475`) at any value, ch16 `cc0=127` (the system-slot path) and ch16 `cc109` at ANY value — and passes everything else through. The `cc109` screen is an ALLOWLIST, not a blocklist, and that distinction was earned: it originally screened only `cc109=8` and let ~14 other flash and erase tasks through, including `gridToFlash` (101), `burnUser489` (43), `preEraseUpdF1/F2` (57/58) and `startUpdF2` (103) — the very state in which the forbidden `ccBankH 127` system-slot write is accepted. `docs/HakenMidi.h:854` says "ccTask not stored within an 'archive' (preset in .mid file)", so no `cc109` belongs in a preset file at all and the whole controller can be refused. Where the header rules a controller out of the payload entirely, prefer refusing the controller over enumerating its dangerous values. Keep it anchored to named `haken` constants rather than bare wire numbers, and keep the two passes separate: the guarantee is about bytes emitted, not about which exception surfaced.

KNOWN VIOLATION: `write_formula_raw` validates its `framing` argument inside the send loop (`server.py:310-318`), so an unknown value raises only after pairs are already on the wire.

### Specific Errors
Provide clear, field-specific messages that help users correct their input.

**Errors name the allowed values.** A rejection message states what would have been accepted — the numeric range, or the full option list interpolated from the same lookup table that was consulted, so the message cannot drift from the code. Several also give the remedy or the reason. `EmConnection.open()` in `midi_io.py` lists the available MIDI ports and warns that the Haken Editor may be holding the device exclusively.

```python
raise ValueError(f"unknown oscillator type {name!r}; options: {list(OSC_TYPES.values())}")
raise ValueError("base polyphony is 1..8 (use expanded=True for more)")
```

### Allowlists Over Blocklists
Define what's allowed rather than trying to block everything else.

### Type and Format Checks
Validate data types, formats, ranges, and required fields systematically.

### Input Sanitization
Sanitize user input to prevent injection attacks (SQL, XSS, command injection).

### Business Rules
Validate business logic (sufficient balance, valid dates) at the appropriate layer.

### Consistent Enforcement
Apply validation uniformly across all entry points (forms, APIs, background jobs).
