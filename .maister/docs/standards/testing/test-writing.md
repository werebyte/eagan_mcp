## Test Writing

An automated suite exists: 106 tests in 16 files under `tests/`, 2643 lines, run with
`.venv/Scripts/python.exe -m pytest` and finishing in about 1.5 s. It is a host-only suite by
construction - no test opens a MIDI port - so it complements hardware validation rather than
replacing it.

What the suite covers: the pure codecs (`formula.py`, `setup.py`, `matrix_map.py`), the
single-table property and the import freedom of the codec layer, `preset_file.py`'s top-level
parse path against four committed fixtures under `tests/fixtures/`, the flash path's pre-scan,
the shape and counts of the shipped JSON artifacts, the validation of both new tools, the three
shipped skills, and the 23 knowledge documents as text.

What it deliberately does not cover, and what therefore still needs the device or a human:
anything requiring the Module - **a green run closes no device-test item** - the device semantics
of the negative-height offset reading, the 19 tool docstrings not yet repaired, the catalog build
from `HAKEN_EDITOR_DIR`, and whether any device claim in the knowledge documents is *true*. Those
remain hardware-based: in-tool read-back verification, device testing with recorded dates, and
listening tests.

A new test belongs with the pure functions wherever it can be written there. A behaviour that can
only be shown on the Module is not a gap in the suite; it is a listening test, and the rules below
apply to it instead.

### Test Behavior
Focus on what code does, not how it does it, to allow safe refactoring.

For patch-building knowledge, hardware listening is the validation gate: a recipe may only enter
`RECIPES.md` once it has been tested by ear on the EM Module. Untested ideas go in a clearly
separated "Candidates" section and are never presented as working recipes. Tested recipes are
tagged with the date and the preset they were proven in (e.g. "tested 2026-10-25, 'Saw Swarm
Warm'"). Source: `RECIPES.md`.

### Listening Tests: One Change, One Yes/No Question
Change exactly one thing at a time, then ask the user a single yes/no question. Send the user a
message immediately before starting a long listen so they can play the device during the
recording. To debug a regression, remove one construction at a time and re-test after each step.
Source: `CLAUDE.md`, `RECIPES.md`.

### Clear Names
Use descriptive names explaining what's tested and expected (`shouldReturnErrorWhenUserNotFound`).

### Mock External Dependencies
Isolate tests by mocking databases, APIs, and external services.

### Fast Execution
Keep unit tests fast (milliseconds) so developers run them frequently.

### Risk-Based Testing
Prioritize testing based on business criticality and likelihood of bugs.

### Balance Coverage and Velocity
Adjust test coverage based on project needs and team workflow.

### Critical Path Focus
Ensure core user workflows and critical business logic are well-tested.

### Appropriate Depth
Match edge case testing to the risk profile of the code.
