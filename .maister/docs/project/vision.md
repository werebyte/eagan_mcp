# Project Vision

## Overview

**eagan_mcp** is an MCP server that gives an LLM agent hands-on control of Haken
EaganMatrix hardware. It turns a plain-words description of a sound into the MIDI traffic
that builds that sound on the device.

## Current State

- **Age**: weeks. Created 2026-10; first hardware-verified session 2026-10-25.
- **Status**: active development. Early-production MVP — the core loop works and has been
  exercised on real hardware, but the protocol is not fully decoded.
- **Users**: the author, working against a single EaganMatrix Module on a Windows 10 host.
- **Tech Stack**: Python 3.11–3.12, FastMCP (`mcp[cli]` 1.x), `mido` + `python-rtmidi`,
  managed with `uv`. Three dependencies total. See [tech-stack.md](tech-stack.md).
- **Scale**: 4556 lines across 8 non-empty modules, exposing 32 MCP tools, plus a shipped
  knowledge base of 23 markdown documents and a 106-test host-only suite.

### What works today (verified on the device)

- Connection, Editor ping (`ch16 cc116`), preset loading, full preset capture to `.mid`
- Matrix read and write with named rows and columns, verified by read-back
- Formula read and write — W/X/Y/Z components, modes, magnitudes, macro modifiers,
  operators, shape-generator shape and phase
- Setup read and write — oscillator slot types, bank A/B types, shape-generator types,
  polyphony, bend range
- Naming, describing, and saving to user slots (with explicit confirmation)
- Searching the firmware 10.81 guides and the factory preset descriptions

### What does not work yet

- X/Y/Z begin/end range scaling, transfer functions and macros on X/Y/Z
- Bank C type values (delays), filter cascade and extreme-rate option values
- What each bank parameter column means per bank type (guide sections 6.3–6.17)
- Export of a built patch as a `.mid` file
- Negative formula heights are implemented from the header's sign semantics but have
  **not** been confirmed on the device

## Purpose

The EaganMatrix is a modulation-matrix synthesiser of unusual depth. Its power is also its
problem: building a patch means knowing which of dozens of rows to cross with which of
dozens of columns, and what formula to put in the cell — knowledge spread across hundreds
of pages of user guide and a protocol header.

This project closes that gap by making the device *addressable in natural language*. The
agent holds the protocol knowledge; the user describes the sound.

Three things make that possible, and they are the project's real content:

1. **A decoded protocol.** Message formats come from `docs/HakenMidi.h` and the user
   guides, never from guesswork, and each finding records the firmware version and the date
   it was confirmed on hardware.
2. **A vocabulary bridge.** `RECIPES.md` maps synthesis vocabulary ("pitch LFO", "FM with
   its own envelope", "filter envelope") onto concrete matrix cells and formulas.
3. **A safety contract.** Writes land in the edit slot. User slots require explicit
   confirmation. The system-slot path (`ch16 cc0=127`) is never used — it is the firmware
   update channel.

## Goals (Next 6–12 Months)

The three priorities confirmed by the user on 2026-10-26, in order:

### 1. Plain-words patch building — the core deliverable

Describe a patch in words and have the agent build it on the Module, end to end, in one
go. Every piece exists; what is missing is a verified run from a fresh conversation. This
is the goal the project is measured against.

### 2. Complete the protocol decoding

The remaining blank areas are what currently force fallbacks and guesses:

- X/Y/Z begin/end range scale, transfer functions, per-component macros
- Bank C type values; filter cascade and extreme-rate option values
- Bank parameter column meaning per bank type
- Confirm a negative formula height on hardware

### 3. A recipe library tested by ear

Every recipe in `RECIPES.md` verified on the Module by listening before it is published as
a recipe. Already done: pitch, volume, SG trigger, pitch LFO, FM with envelope, mod wheel,
macro. Next up: filter envelope, detune, pitch-proportional depth.

### Explicitly not a goal right now

Linting, type checking and CI are all absent and were *not* selected as priorities. They
remain real gaps, recorded in [architecture.md](architecture.md).

Test coverage is no longer among them in the blanket sense: a host-only suite of 106 tests
in 16 files now covers the pure codecs, the preset-file parse path on committed fixtures,
the flash-path pre-scan, the shipped JSON artifacts, tool validation, the skills and the
knowledge documents as text. What it deliberately does not cover is everything that needs
the Module - no test opens a MIDI port, so a green suite closes no device-test item - and
nothing in it can say whether a device claim in the knowledge base is *true*. Hardware
verification therefore remains the validation strategy for device behaviour, with the suite
guarding the offline half.

## Evolution

The project moved fast through three phases in its first days:

1. **Blind protocol work** — the server was written against the Continuum User Guide
   section 15 before any hardware test. Message formats were inferred from documentation.
2. **Hardware verification (2026-10-25)** — the Module came online and the inferences were
   checked. Several were wrong, and the corrections are the most valuable content in
   `CLAUDE.md`: polyphony is `s_Mat_Poke` id 39 and the original `set_polyphony` did
   nothing; bank values 8 and 10 were mis-guessed from menu order; columns 2–7 are
   assignable Master columns.
3. **Firmware 10.81 (since 2026-10-25)** — the official `HakenMidi.h` arrived with the
   Editor and became the source of truth, superseding findings reverse-engineered from the
   older 10.44 Max patches. The 10.81 Editor is JUCE, so the `.maxpat` route is gone.

The direction is clear: from *reading* the device, to *writing* individual parameters, to
*composing whole patches from intent*. Phase 3 is where the work is now.

Two lessons from phase 2 shape how the work proceeds, and both are worth preserving:

- **Cite the source.** A guessed message format costs more to debug than it saves to write.
- **Verify, with a date.** A finding without a verification date is a hypothesis. Firmware
  changes retire findings, and only a date makes that visible.

---
*Based on codebase analysis performed 2026-10-26*
