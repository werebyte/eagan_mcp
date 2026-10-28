## Error Handling

### Clear User Messages
Show helpful, actionable messages without exposing internal details or security-sensitive information.

### Fail Fast
Validate inputs and check preconditions early; reject invalid data before it causes deeper issues.

**No defensive try/except.** Device and MIDI errors are not caught — they propagate out of the tool function to the MCP framework, which reports them to the caller. Only 4 try/except blocks exist in 4556 lines, every one of them where an exception is an expected control-flow event: an unreadable docs file during a grep (`server.py`), `KeyboardInterrupt` ending the sniffer loop (`sniff.py`), and in the offline catalog builder a `UnicodeDecodeError` driving the encoding-fallback loop plus a per-file decode failure recorded into the build's `failures` list so it stays visible instead of aborting the batch (`preset_file.py`). There is no logging module and no error-swallowing fallback; never wrap `conn.send` / `conn.listen` in a catch-all.

### Typed Exceptions
Use specific exception types instead of generic ones to enable precise error handling.

Two exception types only, with a fixed split:
- `ValueError` — a caller argument that cannot be encoded: out of range, unknown enum name, nothing to change (22 sites).
- `RuntimeError` — an environment or device condition the caller cannot fix by changing arguments: no MIDI port, not connected, refusing a dangerous file (3 sites).

No bare `raise`, no re-wrapping. **One custom class is permitted and only one exists**: `preset_file.PresetFileError(ValueError)`, which marks "this file is not a preset archive" so a batch decode over 668 files can catch it distinctly from a bad argument. It subclasses `ValueError` so the split above still holds for any caller that does not care. Add another only for a condition a caller must distinguish; a new class purely to name an error is still forbidden.

```python
raise ValueError("slot must be 1..5")
raise RuntimeError("Not connected. Call connect first.")
```

### Centralized Handling
Catch and process errors at appropriate boundaries (controllers, API layers) rather than scattering try-catch throughout.

### Graceful Degradation
When non-critical services fail, continue operating with reduced functionality rather than crashing entirely.

**Failure and doubt returned as data, not raised.** Once a command has reached the device, the outcome is reported in the result dict rather than thrown: a boolean `verified` flag plus a `note` or `warning` explaining in plain language why a result is unverified or partial. `verified` is tri-state — `None` means the device cannot echo the value back, so success is unknowable rather than false. Raw values are kept beside their interpretation where the scale is unknown (`range_begin_raw`, `cascade_raw`). A refused destructive call also returns normally, with the refusal in the dict.

```python
res["verified"] = None
res["note"] = "sent; the Module does not echo id 40, verify by playing or with listen"
```

### Retry with Backoff
Use exponential backoff for transient failures when calling external services.

### Resource Cleanup
Always release resources (file handles, connections) in finally blocks or equivalent cleanup mechanisms.
