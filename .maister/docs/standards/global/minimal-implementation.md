## Minimal Implementation

### Build What You Need
Create only methods, classes, and functions that will actually be called.

### Clear Purpose
Every method should either be called or improve code readability; nothing else.

### Delete Exploration Artifacts
Remove helper methods and utilities created during development that ended up unused.

### No Future Stubs
Avoid empty methods, placeholder functions, or interfaces "for future extensibility".

### No Speculative Abstractions
Skip factories, strategies, or adapters unless there's an immediate need.

### Review Before Commit
Verify all new methods have callers or serve a clear readability purpose before completing a task.

### Unused Code Is Debt
Remove dead code promptly; it confuses readers and adds maintenance burden.

**Documented deviation — named protocol constants may be retained as documentation even when unused.** The constant block doubles as this project's wire-format reference, so 9 of ~75 constants are defined and never referenced on purpose: `haken.py` `CH15`, `CC_TRANSMIT_UPDATES`, `CC_PONG`, `CC_FORM_SEL`, `TEXT_PRESET_NAME`, `TEXT_PRESET_TEXT`, `TEXT_CATEGORY_NAME`, `CMD_TOGGLE_MUTE`; `formula.py` `SIGN_SLIDER`. The carve-out only pays off when the constant carries a comment saying what the value does — 6 of the 9 do; the `TEXT_*` trio and `CMD_TOGGLE_MUTE` do not and should be annotated.

The carve-out does **not** extend to unused functions, classes or code paths — those are still debt.

The inverse defect is also present and is a real bug risk: wire numbers hardcoded although a named constant exists. `server.py:279` hardcodes control `34` although `haken.CC_FORM_SEL = 34`; stream ids 19 and 20 are bare literals at `server.py:280,311,320,387,391`; the stream terminator 127 is a literal at `server.py:314,323,460` and `haken.py:241`. The standard is: define the constant and then **use** it.
