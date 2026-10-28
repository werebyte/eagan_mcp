# tools_spec.md - ranked specifications for tools that do not exist yet

This document specifies MCP tools and codec surfaces the project **has not built**. It is never a
description of shipped behaviour; `README.md` and the tool docstrings are that
(`.maister/docs/standards/global/conventions.md:10`). Where an entry has since been built, the
entry stays and its `Status` says so, because the rank is what the next reader needs in order to
tell "already done" from "out of scope" from "overlooked".

Every claim carries exactly one bracket tag, inline, per
`.maister/docs/standards/protocol/protocol-sources.md`: `[D]` device-verified (line + ISO date +
firmware), `[D-cap]` recorded in `captures/`, `[G]` from the docs (`file:line`), `[C]` a corpus
statistic with its denominator, `[I]` inferred with the inference stated. Resolution order is
`[G]` header > `[D]` > `[D-cap]` > `[G]` guide > `[C]` > `[I]`. A `[G]` **header** citation is
firmware 10.81; a `[G]` **guide** citation is firmware 10.80 at best `[G]`
`docs/EaganMatrixUserGuide.txt:3-4`, verbatim: "Firmware Version 10.61 to 10.80".

**Research root.** Paths of the form `outputs/...` and `analysis/findings/...` are relative to
`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/`.

**Code citations name the symbol, not only the line.** `eagan_mcp/server.py` is being edited in
the same pass that writes this file, so a bare line number in it goes stale within the hour. A
code reference here is `eagan_mcp/<module>.py` plus the function or table name.

---

## 1. The label scheme

`.maister/docs/standards/` has no label scheme of its own; this one is the implementation plan's
A2.8, made normative so that documents written *before* this file could already cite it.

| Namespace | Meaning | In use | Reserved to |
|---|---|---|---|
| `T<n>` | a tool-gap rank in this document | `T1`..`T22` | `T22` |
| `DT<n>` | a device-test rank in the merged device plan, `analysis/synthesis.md` section 10 | `DT1`..`DT21` | `DT45` |

The two namespaces are disjoint and neither is ever written as a bare "rank n". `T<n>` and
`DT<n>` are different sequences: `T15` is `set_osc_option`, `DT15` is the defaults the corpus
cannot see.

**Why `DT` is reserved to 45 but only 21 are in use.** The device plan merges 79 filed test blocks
into **~45 distinct tests**, grouped into **21 ranked rows** `[G]`
`analysis/synthesis.md:989-1011`. A `DT<n>` is a row of that table, so `DT1`..`DT21` are the live
labels; the namespace is held open to 45 so that splitting a row later does not renumber it.

**Why `research-report.md` needs this at all.** Its section 9 uses "rank n" for a recommendation
and Appendix A uses "rank n" for a device test, in the same cells - `outputs/research-report.md`
section 9 rank 1 reads "Run device test rank 1". Without two namespaces that sentence cannot be
disambiguated. Here it is: run `DT1`, then ship `T1`.

---

## 2. There are twenty-two ranks, not twenty

`T1`..`T20` are **exactly** `outputs/research-report.md` section 9 rank 1..20, in order, one for
one. That mapping is load-bearing and must not drift.

**Section 9's twenty are the research's ranked recommendations, not a complete capability map.**
This is the correction this document makes. Two capability gaps have **no rank at all** in section
9, in `analysis/findings/formulas-mcp-gaps.md` section 6, or in
`analysis/findings/modules-mcp-reachability.md` section 5's twelve, and both are load-bearing:

1. **A write for `idMastCol1..6`.** `outputs/research-report.md` section 9 rank 4 is the
   **read** side - "make `get_matrix`
   label its rows and columns" - which this pass shipped as `eagan_mcp/setup.py`
   `MASTER_COL_TARGETS` and `eagan_mcp/matrix_map.py` `preset_labels`. The **write** side is what
   `eagan_mcp/knowledge/patterns.md` P17 needs, and P17 says so: "`tools_spec.md` `T4` covers the
   read side, which already ships; the **write** side is unranked and is flagged for
   `tools_spec.md`". It is `T21`.
2. **A write for an arbitrary `s_Mat_Poke` id.** `outputs/research-report.md` section 9 rank 15
   is `set_osc_option` for
   `idOscFilOpt1..5` **only**. The WaveBank waveform, the spectral set, the biquad size, all four
   column-mode toggles and the CVC configuration id are *other* `s_Mat_Poke` ids with no rank.
   Six module cards flag the hole in the same words - "**No rank in `T1..T20` covers writing an
   arbitrary `s_Mat_Poke` id**" - and name `analysis/findings/modules-mcp-reachability.md`
   section 5 rank 1, 2, 6 and 7 as the lists this document "has still to fold into the `T`
   namespace" (`eagan_mcp/knowledge/modules/wavebank.md`, `biqbank.md`, `cvc.md`, `harman.md`,
   `modman.md`, `additive.md`, `biqmouth.md`). It is `T22`, and `wavebank.md` calls it "the
   highest-value single-id gap on this card". `[I]` The inference that it is one tool rather than
   several is the cards' own: `_write_setup` already exists in `eagan_mcp/server.py`, so what is
   missing is a validated tool entry, not protocol knowledge.

`T21` and `T22` **originated in the development pass**, from the module cards and `patterns.md`,
not in the research. Neither the cards nor `patterns.md` invented a label to fill the hole: both
cited the finding and the section, and flagged the gap upward. That is why it was catchable.

**Known consequence for the already-written cards.** Seven cards say "no rank in `T1..T20` covers
writing an arbitrary `s_Mat_Poke` id". With `T22` defined, the span is now `T1..T22` and the
sentence is stale. The claim was accurate when written and is recorded here rather than silently
left; repairing the seven spans belongs to the citation-repair pass, not to this document.

---

## 3. `outputs/research-report.md` section 9 ranks 1-6 "need no new wire semantics" - that is
## true, and it is not "offline"

The two are different claims and the document says so in one place so no reader conflates them.
Of section 9 ranks 1-6, only `T2`, `T3` and `T4` are device-free:

| Rank | New wire semantics? | Device? |
|---|---|---|
| `T1` | no | **one listen** (`DT1`): offset or sign-and-magnitude is audible, not readable |
| `T2` | no | offline |
| `T3` | no | offline |
| `T4` | no | offline - validatable against `tests/fixtures/` `[D-cap]` |
| `T5` | no | **one read** (`DT8`): the interpolation default is 40-or-0 |
| `T6` | no | **one read** (`DT16`) - and `T6` reads **stream 18**, which has no codec |

`T6` is the one that is routinely mis-stated. `ccMacrUses` is a single controller, so "no new wire
semantics" is fair; but its answer arrives as `s_MacrUses` stream 18 `[G]`
`docs/HakenMidi.h:1128`, header comment: "Response to ccMacrUses (from Continuum to Editor)", and
the project has **no decoder for stream 18 at all**. Streams 0, 1, 15, 19 and 20 are decoded;
18 is not. `T6` is therefore a new codec plus a device read, not a two-line change.

**No entry in this document is marked `offline` if it needs the device.** The `Device` field of
every rank below takes exactly one of: `offline`, `one listen`, `one read`,
`one write (edit slot)`, `mixed`.

---

## 4. The `ROADMAP.md:26` contradiction, and its amendment

`ROADMAP.md:26` read:

```
- [ ] Ancillary options, blend, interpolation, persistence (rarely needed)
```

**Persistence is not rarely needed.** There is no ADSR on this instrument `[G]`
`outputs/research-report.md` section 4 F7; decay and release **are** persistence, `s_Form_Poke`
`idPersist` id 63 `[G]` `docs/HakenMidi.h:1323`, header comment: "formula persistence 0..127".
`T5` ranks it **high**. Leaving `:26` as it stood meant the plan document actively argued against
this specification's own top-ranked unbuilt item, so `:26` is amended in the same change that
creates this file:

```
- [ ] Persistence (s_Form_Poke id 63): decay and release - there is no ADSR (tools_spec.md T5)
- [ ] Ancillary options, blend, interpolation
```

"(rarely needed)" is gone and persistence is its own item. `ROADMAP.md` grew by one line, so
every item below the old `:26` moved down by one.

---

## 5. What this pass built, and what it deliberately did not

`.maister/docs/standards/global/minimal-implementation.md` forbids an entry nobody will build **as
code**. A ranked specification document is not a stub - it is the record that distinguishes "out
of scope" from "overlooked" - but the standard still binds every entry to name what it unblocks,
and every entry below has an `Unblocks` field for exactly that reason.

**Built in this pass**, and so no longer a gap: `T1` (the negative-height codec, as F1/F2/F3, with
its listen still owed as `DT1`), `T2` (F4), `T3` (F6/F7), `T4` (F9), `T10` (F5), `T17` (the census
fix), `T18` (the repository), plus `search_factory_presets` and `get_knowledge`, which are
`outputs/research-report.md` section 9's rank-4-adjacent and rank-7-adjacent reading tools rather
than ranks of their own. The tool count is **32**.

**Not built, with the reason**, one per entry: see each rank's `Status`. The reasons reduce to
four. (a) It needs the device and the pass is offline. (b) It is a device *write* and
`.maister/docs/standards/protocol/device-safety.md` gates those behind a confirmed scope. (c) It
is a new codec for a stream the project does not decode. (d) It is deferred debt with a named
owner, recorded in section 8.

---

## 6. The ranks

Field meanings. `Status`: built, not built, or built-with-a-debt. `Kind`: what sort of change it
is - the word "tool" or "argument" means there is a callable surface and a real `ValueError`.
`Device`: one of the five vocabulary values from section 3. `Signature`: authored fresh here;
**zero** of the proposed tools carries a documented signature or return shape in the findings, and
that omission is deliberate there, so every one below is new work. `Write scope`: the first line
of the docstring the tool must carry
(`.maister/docs/standards/global/commenting.md:11-14`). `Source rank`: the ranked lists this
entry compresses.

### T1 - negative formula heights are mirrored

- **Status:** built in this pass as F1/F2/F3 (`eagan_mcp/formula.py` `slider_value` /
  `slider_encode`); the device confirmation is still owed as `DT1`.
- **Kind:** codec fix inside a shipped tool, no new tool surface.
- **Device:** one listen
- **Name:** `formula.slider_encode` / `formula.slider_value`, reached through `set_formula`.
- **Signature:** `slider_encode(value: float, max_value: float = 1.27) -> tuple[int, int]`
- **Returns:** the component dict inside `get_formula`'s result.
  ```python
  {"W": {"height_begin": -0.20, "height_end": -0.20, "mode": "Constant"}}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"value must be within -1 .. {max_value}"`
- **Wire ids:** `idNegW` 13 + `idHeightW` 42 and the twelve other sign/slider pairs `[G]`
  `docs/HakenMidi.h:1201-1202`, header comment: "true for -idHeightW; no effect until idHeightW
  received".
- **Citation:** `[G]` `docs/HakenMidi.h:1202`, header comment: "height for W with idNegW
  -1.00..1.27 in 0.01 steps".
- **Unblocks:** every negative height; `[C]` 493 of 668 factory presets' mined recipes; the
  Harkonnen vowel wah; and it corrects two saved user slots.
- **Source rank:** `outputs/research-report.md` section 9 rank 1;
  `analysis/findings/formulas-mcp-gaps.md` section 6 rank 1.

### T2 - pass unknown ids through `decode` and set a warning

- **Status:** built in this pass as F4 (`eagan_mcp/formula.py` `KNOWN_IDS`).
- **Kind:** codec change inside a shipped tool, no new tool surface.
- **Device:** offline
- **Name:** `formula.decode`, reached through `get_formula`.
- **Signature:** `decode(pairs: dict[int, int]) -> dict`
- **Returns:**
  ```python
  {"operator": "W + X + Y + Z", "W": {...},
   "unknown_ids": {63: 90}, "warning": "1 id was not understood"}
  ```
- **Write scope:** read-only.
- **ValueError:** none - the codec never raises and never drops
  (`.maister/docs/standards/protocol/codec-conventions.md:14-15`).
- **Wire ids:** every `s_Form_Poke` id outside `KNOWN_IDS`, stream 19 `[G]`
  `docs/HakenMidi.h:1130`, header comment: "Formula Configuration poke".
- **Citation:** `[G]` `docs/HakenMidi.h:1154`, header comment: "These affect the formula selected
  by ccFormSel; ccFormSel must precede use of id below".
- **Unblocks:** turns `get_formula`'s confident partial answer into a visible gap, so a blend, an
  ancillary or a `psDuplex` formula no longer reads as an ordinary one.
- **Source rank:** `outputs/research-report.md` section 9 rank 2;
  `analysis/findings/formulas-mcp-gaps.md` section 6 rank 2.

### T3 - `send_preset_file`'s pre-scan and `send_raw`'s docstring

- **Status:** built in this pass as F6/F7.
- **Kind:** validation fix plus a docstring fix on two shipped tools, no new tool surface.
- **Device:** offline
- **Name:** `send_preset_file`, `send_raw`.
- **Signature:** `send_preset_file(path: str) -> dict` (unchanged)
- **Returns:**
  ```python
  {"path": "...", "messages_sent": 0, "refused": True,
   "reason": "file contains ch16 cc112 (ccStore), which writes flash"}
  ```
- **Write scope:** refuses before the first byte; nothing is emitted until the whole file passes.
- **ValueError:** `"refusing to send: message 412 is ch16 cc112 (ccStore), which writes a preset
  slot to flash"`
- **Wire ids:** `ccStore` 112 at any value and `ccBankH` 0 with value 127 (the system-slot path);
  `ccTask` 109 value 8 is global settings to flash, not a preset store.
- **Citation:** `[G]` `docs/HakenMidi.h:475`, header comment: "ch16: store flash; ccBankH =
  catEdBuf/catUser/catSSlot".
- **Unblocks:** closes a real hole in the one function
  `.maister/docs/standards/global/validation.md:12` cites as the project's exemplary pre-scan.
- **Source rank:** `outputs/research-report.md` section 9 rank 3.

### T4 - `get_matrix` labels its own rows and columns

- **Status:** built in this pass as F9 (`eagan_mcp/matrix_map.py` `preset_labels`,
  `eagan_mcp/setup.py` `MASTER_COL_TARGETS`). Read side only; the write side is `T21`/`T22`.
- **Kind:** labelling fix inside a shipped tool, no new tool surface.
- **Device:** offline
- **Name:** `get_matrix`.
- **Signature:** `get_matrix(seconds: float = 4.0) -> dict` (unchanged)
- **Returns:**
  ```python
  {"cells": [{"row": 9, "col": 30, "row_name": "Tap 1", "col_name": "Bank A 4 (bandwidth)",
              "value": "C"}]}
  ```
- **Write scope:** read-only.
- **Wire ids:** `idRowTyp1` 106 and `idRowTyp2` 107 for rows 9-12; `idMastCol1..6` 27-32 for
  columns 2-7; `idBankA/B/C` 91/92/93 for the bank column blocks.
- **ValueError:** none - labelling never rejects a cell.
- **Citation:** `[G]` `docs/HakenMidi.h:1634-1643`, header comment: "matrix row type (AudioLR
  rows)".
- **Unblocks:** a correctness fix - `[D-cap]` 3 of 18 captured presets switch rows 9-12 to delay
  taps, including `microdelay_wg_v1`, the preset the Sitar work was built on. It also reveals that
  convolution and the Recirculator are already modulatable from columns 2-7.
- **Source rank:** `outputs/research-report.md` section 9 rank 4;
  `analysis/findings/modules-mcp-reachability.md` section 5 rank 4 and rank 6.

**`T4` is the read side only.** Ten entries across
`eagan_mcp/knowledge/modules/microdelay.md`, `summeddelay.md` and `voicedelay.md` infer `[I]`
that `T4` is "the stream-20 labelling-and-write rank" and file the **writes** for `idTimeSel`
105 and `idAliasDelay` 108 under it. The inference was reasonable when written, because no rank
covered an arbitrary `s_Mat_Poke` write; now one does. Labelling is `T4`; writing id 105 or id
108 is `T22`, which lists both.

### T5 - persistence, interpolation and reluctance

- **Status:** not built. Decoded only (`eagan_mcp/formula.py` `PERSISTENCE_IDS`,
  `INTERPOLATION_IDS`, `RELUCTANCE_IDS`); no write path. Reason: the sane default for
  interpolation is unknown until `DT8` runs, and writing an unknown default over 44 shared
  formula letters is the error this project most wants to avoid.
- **Kind:** new argument group on the shipped `set_formula` tool.
- **Device:** one read
- **Name:** `set_formula(..., persistence=, interpolation=, reluctance=)`
- **Signature:** `set_formula(row: int, col: int, ..., persistence: int | None = None,
  interpolation: int | None = None, reluctance: int | None = None) -> dict`
- **Returns:**
  ```python
  {"row": 13, "col": 27, "letter": "A",
   "requested": {"persistence": 90},
   "device_value": {"persistence": 90, "interpolation": 40, "reluctance": 0},
   "verified": True, "warning": None}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"persistence must be 0..127, got {persistence}"`
- **Wire ids:** `idPersist` 63, `idInterp` 48 (`interpDef` 40), `idReluct` 96; secondaries
  `idPersist2` 81, `idInterp2` 82, `idReluct2` 97.
- **Citation:** `[G]` `docs/HakenMidi.h:1321-1324`, header comment: "interpolation value 0..127".
- **Unblocks:** the **only** way to build an envelope release, a sustain tail, finger-lift noise
  or a slow-start attack on an instrument with no ADSR; and the interpolation default of 40 may
  mean every formula the project has written so far is unsmoothed.
- **Source rank:** `outputs/research-report.md` section 9 rank 5;
  `analysis/findings/formulas-mcp-gaps.md` section 6 rank 3.

### T6 - `allocate_formula_letter()`

- **Status:** not built. Reason: it needs a decoder for stream 18, which does not exist, plus one
  device read to confirm the response shape.
- **Kind:** new tool, read-only.
- **Device:** one read
- **Name:** `allocate_formula_letter`
- **Signature:** `allocate_formula_letter(macro: int | None = None, seconds: float = 4.0) -> dict`
- **Returns:**
  ```python
  {"free": ["K", "L", "M'"], "in_use": ["A", "B", "C"],
   "pool": 44, "source": "s_MacrUses", "verified": True}
  ```
- **Write scope:** read-only.
- **ValueError:** `f"macro must be 0..95 or None, got {macro}"`
- **Wire ids:** `ccMacrUses` 36 (request) -> `s_MacrUses` stream 18 (response);
  `ccFormSel` 34 as the fallback probe.
- **Citation:** `[G]` `docs/HakenMidi.h:617`, header comment: "request list of formulas using
  specified macro (via s_MacrUses)".
- **Unblocks:** the one resource that must be allocated correctly. Letters are shared device-wide
  **and** the matrix dump under-reports them, because an all-zero formula's cell is omitted, so a
  wrong pick silently rewrites unrelated cells. The pool is **44**, not 22.
- **Source rank:** `outputs/research-report.md` section 9 rank 6;
  `analysis/findings/formulas-mcp-gaps.md` section 6 rank 9.

### T7 - the three skills carry the constraint rules, not only the recipes

- **Status:** built in this pass, as the three `.claude/skills/eagan-*/SKILL.md` files.
- **Kind:** documentation, no tool surface.
- **Device:** offline
- **Name:** n/a - no tool surface.
- **Signature:** n/a - no tool surface.
- **Returns:** n/a - no tool surface.
- **Write scope:** n/a - the skills must themselves state every tool's write scope.
- **ValueError:** n/a - no tool surface.
- **Wire ids:** none.
- **Citation:** `[G]` `outputs/research-report.md` section 6.6, the five rules the acceptance test
  measures.
- **Unblocks:** this is what the acceptance test actually measures. A skill that knows the recipes
  and not the constraints produces confident wrong patches.
- **Source rank:** `outputs/research-report.md` section 9 rank 7.

### T8 - the preset index comes from a table, and the device reports its own slot

- **Status:** half built. `eagan_mcp/knowledge/preset_index_1081.json` ships; having
  `load_and_capture_preset` report the device's own slot trailer does not. Reason: the trailer's
  position is `[D-cap]` evidence from 18 captures and wants one confirming load (`DT2`, `DT3`).
- **Kind:** new return field on a shipped tool.
- **Device:** one read
- **Name:** `load_and_capture_preset(..., )` return field `device_slot`.
- **Signature:** `load_and_capture_preset(category: int, index: int, seconds: float = 6.0) -> dict`
- **Returns:**
  ```python
  {"requested": {"category": 6, "index": 0}, "name": "Acrylic Clock 2",
   "device_slot": {"category": 6, "program": 0}, "verified": True}
  ```
- **Write scope:** read-only on flash; **loading destroys the unsaved edit slot**.
- **ValueError:** `f"category must be 0..127, got {category}"`
- **Wire ids:** `ccBankH` 0 + `ccBankL` 32 + program change; the loaded slot is in the dump's last
  three messages `[D-cap]`.
- **Citation:** `[G]` `docs/HakenMidi.h:380`, header comment: "category select; ccBankL and
  progChg follow".
- **Unblocks:** no arithmetic on a printed list is safe `[D]` `CLAUDE.md:155-157`, 2026-10-25,
  fw 10.81; the device reports the exact slot in every dump, so the index stops being a guess.
- **Source rank:** `outputs/research-report.md` section 9 rank 8.

### T9 - raise `set_polyphony`'s ceiling to 14

- **Status:** not built, and deliberately gated. Reason: it is a device write whose clamp
  behaviour is unknown - a clamp to 8 and a clamp to the DSP budget look identical in a setup read
  alone - so `DT9` must run first. The shipped `ValueError` names the ceiling, the 24 presets and
  the test.
- **Kind:** range widening on a shipped tool argument.
- **Device:** one write (edit slot)
- **Name:** `set_polyphony`
- **Signature:** `set_polyphony(voices: int, expanded: bool | None = None,
  double_computation_rate: bool | None = None) -> dict`
- **Returns:**
  ```python
  {"base": {"id": 39, "requested": 14, "device_value": 14, "verified": True},
   "dsp_polyphony": 7, "warning": None}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"voices must be 1..14 (maxNonMpePoly, HakenMidi.h:1360), got {voices}"`
- **Wire ids:** `idPoly` 39; `maxNonMpePoly` 14; `maxMpePoly` 15.
- **Citation:** `[G]` `docs/HakenMidi.h:1360`, header comment: "max poly arbitrary Yencode and
  Zencode: no notes ch 1&16".
- **Unblocks:** `[C]` 24 factory presets of 668 store 10, 12 or 14 voices and cannot be reproduced
  at their shipped voice count - long-decay percussion patches where the voice count is the point.
- **Source rank:** `outputs/research-report.md` section 9 rank 9.

### T10 - `idTransX`'s default is kHz, not Octaves

- **Status:** built in this pass as F5 (`eagan_mcp/formula.py` `TRANSFER_DEFAULT`).
- **Kind:** codec default fix inside a shipped tool, no new tool surface.
- **Device:** offline
- **Name:** `formula.decode`, reached through `get_formula`.
- **Signature:** `TRANSFER_DEFAULT = {"X": 1, "Y": 0, "Z": 0}`
- **Returns:**
  ```python
  {"X": {"transfer": "kHz", "begin": 0.0, "end": 1.0}}
  ```
- **Write scope:** read-only.
- **ValueError:** none.
- **Wire ids:** `idTransX` 85, values `xOctaves` 0, `xKHz` 1, `xLinear` 2 and on.
- **Citation:** `[G]` `docs/HakenMidi.h:1234`, header comment: "X transfer function".
- **Unblocks:** `[C]` 334 factory formulas were labelled "Octaves" when they are kHz, so every
  mined pitch recipe inherited the wrong unit.
- **Source rank:** `outputs/research-report.md` section 9 rank 10.

### T11 - the documentation repairs

- **Status:** built in this pass, as the Wave 10 repair sequence.
- **Kind:** documentation, no tool surface.
- **Device:** offline
- **Name:** n/a - no tool surface.
- **Signature:** n/a - no tool surface.
- **Returns:** n/a - no tool surface.
- **Write scope:** n/a - no tool surface.
- **ValueError:** n/a - no tool surface.
- **Wire ids:** none.
- **Citation:** `[G]` `analysis/findings/provenance-citation-repairs.md`, which carries exact
  old-to-new text for each site.
- **Unblocks:** the project's own "cite the header" rule, which currently points at a stale header
  - `CLAUDE.md:30` names `ref/cohem/include/HakenMidi.h` the source of truth while `CLAUDE.md:5`
  names `docs/HakenMidi.h`, and citations drift by up to 18 lines between the two.
- **Source rank:** `outputs/research-report.md` section 9 rank 11.

**Do not confuse this with the Recirculator.** `eagan_mcp/knowledge/modules/recirculator.md`
assigns `T11` to `idReciType` 62, `idCompOpt` 16 and `idNoRecirc` 15, inferring the number from
`analysis/findings/modules-mcp-reachability.md` section 5 rank 11, which does group those three.
But `T<n>` is `outputs/research-report.md` section 9 rank n, and that rank 11 is the documentation
repairs. The card's `[I]` is wrong on the label; the three ids are real and unranked, and `T22`
covers writing all three.

### T12 - a read-only patch lint

- **Status:** not built. Reason: the lint's whole value is that it listens for the Module's own
  distress reports while the port is held, which is a live session.
- **Kind:** new tool, read-only.
- **Device:** one read
- **Name:** `lint_patch`
- **Signature:** `lint_patch(seconds: float = 4.0) -> dict`
- **Returns:**
  ```python
  {"findings": [{"rule": "sg-no-t-column", "severity": "error",
                 "where": "SG 2", "fix": "drive SG 2 T from Direct +"}],
   "dsp_percent": 96, "dsp_polyphony": 3,
   "device_reports": ["reduceGain"], "verified": True}
  ```
- **Write scope:** read-only.
- **ValueError:** `f"seconds must be 0.1..30.0, got {seconds}"`
- **Wire ids:** `ccTask` 109 values `reduceGain` 9, `reducePoly` 10, `nanErr` 69; plus
  `get_matrix`, `get_setup` and `get_status` as inputs.
- **Citation:** `[G]` `docs/HakenMidi.h:288`, verbatim: "reduceGain reducePoly inFactCalib
  eraseMessage aesSyncFail matToLog".
- **Unblocks:** every rule in `eagan_mcp/knowledge/pitfalls.md` already has a source, and **the
  Module announces its own trouble while nothing listens** - overload and NaN errors currently
  pass unnoticed with no Reduce Gain safety net.
- **Source rank:** `outputs/research-report.md` section 9 rank 12;
  `analysis/findings/mcp-capability-gaps.md` G9.

### T13 - the ancillary set

- **Status:** not built. Decoded only (`eagan_mcp/formula.py` `ANC_OPS`, `ANC_VALUES`,
  `ANC_DOMAINS`, `ANC_LOOKUPS`); no write path. Reason: the neutral wire value is **3**, not 0,
  and amount 0 means a literal 0.0, so a write tool that defaults wrongly silences a formula.
- **Kind:** new argument group on the shipped `set_formula` tool.
- **Device:** one write (edit slot)
- **Name:** `set_formula(..., anc_op=, anc_value=, anc_domain=, anc_op2=, anc_value2=)`
- **Signature:** `set_formula(row: int, col: int, ..., anc_op: str | None = None,
  anc_value: str | None = None, anc_domain: str | None = None, anc_op2: str | None = None,
  anc_value2: str | None = None, anc_lookup: str | None = None, anc_to_nn: bool | None = None,
  anc_limit: bool | None = None, anc_touch_area: bool | None = None) -> dict`
- **Returns:**
  ```python
  {"row": 13, "col": 27, "letter": "A",
   "requested": {"anc_op": "^", "anc_value": "2.0"},
   "device_value": {"op": "^", "value": "2.0", "domain": "WXYZ"},
   "verified": True, "warning": "amount 0 is a literal 0.0, not neutral; neutral is 3"}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"unknown ancillary operation {anc_op!r}; options: {ANC_OPS}"`
- **Wire ids:** `idAncOp` 56, `idAncOp2` 100, `idAncVal` 57, `idAncVal2` 101, `idAncDom` 7,
  `idAncLookup` 8, `idAncLimit` 9, `idAncNN` 10, `idAncTAorAll` 11.
- **Citation:** `[G]` `docs/HakenMidi.h:1275`, header comment: "first ancillary operation, values
  listed below".
- **Unblocks:** the largest number of named techniques per id - quantize, crossing-detect
  triggers, MIDI-clock LFOs, the Via Limiter and the note-sequence generator; `[C]` 19.2% of all
  7,259 factory formulas use an ancillary operation.
- **Source rank:** `outputs/research-report.md` section 9 rank 13;
  `analysis/findings/formulas-mcp-gaps.md` section 6 rank 4.

### T14 - blend and the secondary value set

- **Status:** not built. Decoded only (`eagan_mcp/formula.py` `BLEND_CONTROLS`); no write path.
  Reason: it is the largest formula write surface - 5 ids, 10 values and the whole secondary
  slider bank - and its encoding is only *claimed* identical to the primaries.
- **Kind:** new argument group on the shipped `set_formula` tool.
- **Device:** one write (edit slot)
- **Name:** `set_formula(..., blend=, blend_macro_or_formula=, blend_transfer=)`
- **Signature:** `set_formula(row: int, col: int, ..., blend: str | None = None,
  blend_macro_or_formula: int | None = None, blend_begin: int | None = None,
  blend_end: int | None = None, blend_transfer: str | None = None,
  secondary: dict | None = None) -> dict`
- **Returns:**
  ```python
  {"row": 13, "col": 27, "letter": "A",
   "requested": {"blend": "ch1 note"},
   "device_value": {"blend": "ch1 note", "blend_macro_or_formula": 0,
                    "secondary": {"W": {"height_begin": 0.5}}},
   "verified": True, "warning": None}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"unknown blend control {blend!r}; options: {BLEND_CONTROLS}"`
- **Wire ids:** `idBlend` 39 (values `ps0` 0 .. `psSos2` 8), `idBlMacForm` 68, `idHBegBl` 121,
  `idHEndBl` 123, `idTransBl` 12, plus the secondary sliders 73-80 with sign ids 14-26 even.
- **Citation:** `[G]` `docs/HakenMidi.h:1326`, header comment: "blend control for
  primary/secondary formula values".
- **Unblocks:** `psCh1Note`, the firmware's own keyboard-safety switch, aimed squarely at this
  project's main use case - a plain MIDI keyboard - plus the Release-knob pattern the guide says
  is used in numerous presets.
- **Source rank:** `outputs/research-report.md` section 9 rank 14;
  `analysis/findings/formulas-mcp-gaps.md` section 6 rank 5.

### T15 - `set_osc_option` for `idOscFilOpt1..5`

- **Status:** not built. The decode side ships (`eagan_mcp/setup.py` `OSC_OPTIONS`,
  `osc_option_name`); the write does not. Reason: the meaning of the value depends on the slot's
  current type, so the tool must read the type first, and `DT21` is its acceptance test.
- **Kind:** new tool.
- **Device:** one write (edit slot)
- **Name:** `set_osc_option`
- **Signature:** `set_osc_option(slot: int, option: str, confirm_type: str | None = None) -> dict`
- **Returns:**
  ```python
  {"slot": 2, "slot_type": "Jenny Oscillator", "requested": "Hann decay",
   "id": 78, "value": 2, "device_value": 2, "verified": True}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"unknown option {option!r} for a {slot_type} in slot {slot}; options:
  {OSC_OPTIONS[slot_type]}"`
- **Wire ids:** `idOscFilOpt1` 77 .. `idOscFilOpt5` 81, one per oscillator slot.
- **Citation:** `[G]` `docs/HakenMidi.h:1535`, header comment:
  "filterCascade/oscillatorOption/ladderVariant, see values below".
- **Unblocks:** the only path to PWM linear-versus-exponential, the four Phase Generator modes,
  Jenny's four decay contours and transistor-versus-diode Ladder; `[C]` it is the most common
  non-default oscillator-slot setting in the corpus.
- **Source rank:** `outputs/research-report.md` section 9 rank 15;
  `analysis/findings/modules-mcp-reachability.md` section 5 rank 3.

### T16 - codecs for streams 11/12/14 (read) and 24/25/26 (write)

- **Status:** not built. Reason: three new codecs, ~126 ids in total. All three streams
  **already arrive and are discarded** `[D-cap]`, so the reader half is offline-testable against
  `tests/fixtures/`, but the writer half needs the device.
- **Kind:** new codecs plus two new tools.
- **Device:** mixed
- **Name:** `get_bank_properties`, `set_bank_property`.
- **Signature:** `get_bank_properties(seconds: float = 4.0) -> dict` and
  `set_bank_property(bank: str, name: str, value: int) -> dict`
- **Returns:**
  ```python
  {"A": {"type": "BiqBank", "sF": 40, "qF": 90,
         "columns": {3: "sF", 4: "B", 5: "R"}},
   "convolution": {"1": {"ir": "Plate", "interp": 12, "mix": 40}},
   "verified": True}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"unknown bank property {name!r} for a {type_name}; options: {options}"`
- **Wire ids:** read `s_Kinet` 11, `s_BiqSin` 12, `s_Conv` 14; write `s_Kinet_Poke` 24,
  `s_BiqSin_Poke` 25, `s_Conv_Poke` 26. Bank A occupies ids 0-23, bank B/C ids 24-47.
- **Citation:** `[G]` `docs/HakenMidi.h:1137-1141`, header comment: "BiqBank/SineBank property
  poke".
- **Unblocks:** the data behind "blank is not neutral", the Kinetic friction settings a bow needs,
  and `id_q_Sel3..Sel8` - the only way to know what an assignable bank column means. Without it
  the MCP cannot explain a BiqBank, SineBank, Kinetic or convolution patch at all.
- **Source rank:** `outputs/research-report.md` section 9 rank 16;
  `analysis/findings/modules-mcp-reachability.md` section 5 rank 8, rank 9 and rank 10.

### T17 - the two defects in the research's own output

- **Status:** built in this pass - the census fix shipped in
  `eagan_mcp/knowledge/census.json`.
- **Kind:** data fix, no tool surface.
- **Device:** offline
- **Name:** n/a - no tool surface.
- **Signature:** n/a - no tool surface.
- **Returns:** n/a - no tool surface.
- **Write scope:** n/a - no tool surface.
- **ValueError:** n/a - no tool surface.
- **Wire ids:** none.
- **Citation:** `[G]` `outputs/research-report.md` section 8.3.
- **Unblocks:** a deliverable that disagrees with itself teaches the wrong number; the DSP-cost
  statistic would otherwise have shipped as a point estimate that is wrong under one of two
  counting scripts.
- **Source rank:** `outputs/research-report.md` section 9 rank 17.

### T18 - version control before the write pass

- **Status:** built - the repository exists and the pass began from a baseline commit.
- **Kind:** process, no tool surface.
- **Device:** offline
- **Name:** n/a - no tool surface.
- **Signature:** n/a - no tool surface.
- **Returns:** n/a - no tool surface.
- **Write scope:** n/a - no tool surface.
- **ValueError:** n/a - no tool surface.
- **Wire ids:** none.
- **Citation:** `[I]` inferred from the repository state: the pass's first commit predates every
  deliverable, so a bad write pass is recoverable.
- **Unblocks:** rollback for a pass that writes ten deliverables at once.
- **Source rank:** `outputs/research-report.md` section 9 rank 18.

### T19 - end-detecting reads instead of fixed sleeps

- **Status:** not built. Reason: every boundary marker is known from captures, but the change
  rewrites the timing of every read tool, and the one recorded mid-session disconnect is still
  unexplained - so it wants a device session, not an offline rewrite.
- **Kind:** behaviour change to every shipped read tool.
- **Device:** one read
- **Name:** the `seconds` parameter on `get_matrix`, `get_formula`, `get_setup`, `listen` and
  `load_and_capture_preset` becomes an upper bound rather than a fixed wait.
- **Signature:** `get_matrix(seconds: float = 4.0) -> dict` (unchanged signature, new semantics)
- **Returns:**
  ```python
  {"cells": [...], "waited": 0.9, "ended_on": "cc45=125", "timed_out": False}
  ```
- **Write scope:** read-only.
- **ValueError:** `f"seconds must be 0.1..30.0, got {seconds}"`
- **Wire ids:** `ccStream` 56 value 127 (`s_StreamEnd`) and `cc45` value 125 as the matrix-dump
  terminator.
- **Citation:** `[G]` `docs/HakenMidi.h:1149`, header comment: "Marks end of sData stream (not
  required with stream_Poke)".
- **Unblocks:** `get_matrix` can block 6.8 s and `save_to_user_slot` 7.5 s; `[I]` the inference
  from those two numbers and the single recorded disconnect is that the fixed sleeps are the most
  plausible cause, so this is also the only lead on `ROADMAP.md`'s open disconnect question.
- **Source rank:** `outputs/research-report.md` section 9 rank 19.

### T20 - `set_preset_name`'s description argument stays prohibited

- **Status:** not built, and deliberately so. This is F14, a **prohibition**, and `synthesis.md`
  section 7.6 defect #10 - `set_preset_name`'s unverified write - is blocked behind it, because
  fixing verification while the argument is prohibited would invite its use.
- **Kind:** prohibition on a shipped tool argument.
- **Device:** one read
- **Name:** `set_preset_name(name, description=...)` - do not pass `description`.
- **Signature:** `set_preset_name(name: str, description: str | None = None) -> dict`
- **Returns:**
  ```python
  {"name": "Harkonnen Voice", "description": None,
   "device_value": None, "verified": None,
   "warning": "description is prohibited until DT7 resolves stream 1 (s_ConText)"}
  ```
- **Write scope:** edit slot only; **not verified today** - `verified` is `None`, not `True`.
- **ValueError:** `"description is prohibited: stream 1 is s_ConText and may be the panel macro
  labels, not the description (DT7)"`
- **Wire ids:** `s_Name` stream 0 for the name; `s_ConText` stream 1 for whatever the second text
  stream is.
- **Citation:** `[G]` `docs/HakenMidi.h:1082`, header comment: "Ascii Preset Control Text". The
  header calls stream 1 *control text*, not a description, which is the strongest single reason
  the prohibition stands.
- **Unblocks:** nothing - it **prevents** the silent, invisible loss of a preset's macro names.
  `outputs/research-report.md` section 9 ranks it "high as a prohibition".
- **Source rank:** `outputs/research-report.md` section 9 rank 20.

### T21 - `set_master_column`, the write side of the assignable Master columns

- **Status:** not built. Originated in this development pass from
  `eagan_mcp/knowledge/patterns.md` P17; **it has no rank in any of the research's ranked lists**.
  Reason it was not built: it is a device write, and this pass is offline.
- **Kind:** new tool.
- **Device:** one write (edit slot)
- **Name:** `set_master_column`
- **Signature:** `set_master_column(column: int, target: str) -> dict`
- **Returns:**
  ```python
  {"column": 4, "id": 29, "requested": "Conv 1 Mix", "value": 17,
   "device_value": 17, "verified": True}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"unknown Master column target {target!r}; options:
  {sorted(setup.MASTER_COL_TARGETS.values())}"` and
  `f"column must be 2..7 (the six assignable Master columns), got {column}"`
- **Wire ids:** `idMastCol1` 27 .. `idMastCol6` 32, for matrix columns 2..7; 20 target values,
  `Recirc R1` 0 .. `Conv 2 Mix` 19.
- **Citation:** `[G]` `docs/HakenMidi.h:1488-1493`, header comment: "1st of 6 assignable Master
  columns; values below".
- **Unblocks:** `eagan_mcp/knowledge/patterns.md` P17, reverb and ambience. The read side ships as
  `eagan_mcp/setup.py` `MASTER_COL_TARGETS`, so a recipe can drive whatever a preset has already
  assigned but cannot choose a different Recirculator parameter - which is why P17 says an
  ambience recipe must currently start from a preset whose assignments already suit it. `[C]`
  `Direct +` drives Master column 1 in 149 presets of 668, column 3 in 96 and column 2 in 96.
- **Source rank:** none. Unranked in `outputs/research-report.md` section 9, in
  `analysis/findings/formulas-mcp-gaps.md` section 6 and in
  `analysis/findings/modules-mcp-reachability.md` section 5; raised by
  `eagan_mcp/knowledge/patterns.md` P17 and by section 5 of
  `analysis/findings/mcp-capability-gaps.md` G3, which calls it "a half-hour of work, not a
  research gap".

### T22 - `set_module_option`, a validated write for any `s_Mat_Poke` id

- **Status:** not built. Originated in this development pass from seven module cards; **it has no
  rank in any of the research's ranked lists**. Reason it was not built: it is a device write, and
  this pass is offline. `DT21` is its acceptance test.
- **Kind:** new tool.
- **Device:** one write (edit slot)
- **Name:** `set_module_option`
- **Signature:** `set_module_option(option: str, value: int | str, bank: str | None = None) -> dict`
- **Returns:**
  ```python
  {"option": "BankParamA", "id": 99, "bank": "A",
   "requested": "triangle", "value": 2,
   "device_value": 2, "verified": True,
   "note": "bank A is a WaveBank, so id 99 selects the waveform"}
  ```
- **Write scope:** edit slot only, verified by a separate read-back.
- **ValueError:** `f"unknown setup option {option!r}; options:
  {sorted(setup.MAT_POKE_NAMES.values())}"` and, for a type-dependent id,
  `f"{option} on a {type_name} bank takes one of {options}, got {value!r}"`
- **Wire ids:** any id in `eagan_mcp/setup.py` `MAT_POKE_NAMES`, written as `s_Mat_Poke` stream 20
  id/value pairs. The ids the cards actually ask for: `idBankParamA` 99 and `idBankParamB` 98
  (WaveBank waveform, biquad deflation/IIT), `idSSetA` 64 and `idSSetB` 65 (the 38-entry spectral
  set, or the 5-entry Additive decade), `idBqExtA` 70 and `idBqExtB` 71 (biquad size, 0..5 = 8..48
  modes, 6 = variable), `idBankAcm1/2` 95/97 and `idBankBcm1/2` 94/96 (the four column-mode
  toggles), `idCvcCfg` 63, `idReciType` 62, `idCompOpt` 16, `idNoRecirc` 15, `idTimeSel` 105,
  `idRowTyp1/2` 106/107, `idAliasDelay` 108.
- **Citation:** `[G]` `docs/HakenMidi.h:1132`, header comment: "Matrix Configuration poke".
- **Unblocks:** `eagan_mcp/knowledge/modules/wavebank.md` calls the waveform selector "the
  highest-value single-id gap on this card: one `s_Mat_Poke` value separates four instruments";
  `biqbank.md` says four of its seven unreachable surfaces are one id apiece; `harman.md`,
  `modman.md` and `additive.md` need the spectral set and the column-mode toggles before a matrix
  dump of those banks can be interpreted at all; `cvc.md` needs `idCvcCfg`;
  `recirculator.md` needs the three Master-effect ids. `[I]` The inference that one validated tool
  covers all of them, rather than one tool per id, is the cards' own: `_write_setup` already
  exists in `eagan_mcp/server.py` and already writes these ids privately, so only the validated,
  type-aware entry point is missing.
- **Source rank:** none in `outputs/research-report.md` section 9. The nearest ranked lists are
  `analysis/findings/modules-mcp-reachability.md` section 5 rank 1 (`idBankParamA/B`), rank 2
  (`idSSetA/B`), rank 6 (the column-mode selectors), rank 7 (`idBqExtA/B`) and rank 11 (the three
  Master-effect ids) - five of that document's twelve, none of which has a `T` number, which is
  why seven cards asked this document to fold them in.

---

## 7. The device tests that are blocked by tool, and double as acceptance tests

`DT21` is the merged plan's row for every test that needs an MCP capability the project does not
have `[G]` `analysis/synthesis.md:1011`. Each of them validates **the very id its new tool would
write**, so each is the acceptance test for the specification that would unblock it. Schedule them
after the `T` work, not before.

| Blocked on | Spec that unblocks it | What the test would establish |
|---|---|---|
| `idBqExtA/B` 70/71 | `T22` | biquad mode count; `bqVar` 6 means variable |
| `s_Kinet_Poke` stream 24 | `T16` | Kinetic gravity, stiction, elasticity - the card is unusable without them |
| `idBankParamA` 99 | `T22` | the WaveBank default waveform (`DT15`), and the header-versus-menu conflict |
| `idOscFilOpt1..5` 77-81 | `T15` | Jenny decay contours, Phase Generator modes, PWM linear/exp, ladder variant |
| `idBankAcm2` 97 | `T22` | what Additive column 5 and column 7 mean; `modules-devicetests.md:76` |
| `idSSetA/B` 64/65 | `T22` | the HarMan and ModMan spectral set, and the Additive decade |
| `s_BiqSin_Poke` stream 25 | `T16` | `id_q_Sel3..Sel8`, the only way to name a BiqBank or SineBank column |
| `s_Conv_Poke` stream 26 | `T16` | convolution character and the 19 impulse responses |
| `idReciType` 62 | `T22` | the Recirculator type, read-only today |
| `idCompOpt` 16 | `T22` | compressor-versus-masterTanh |
| `idNoRecirc` 15 | `T22` | the Recirculator disable flag, neither read nor written today |

**A count conflict, recorded.** `outputs/research-report.md` Appendix A says "Eleven tests are
BLOCKED BY TOOL"; `analysis/findings/modules-devicetests.md:220` marks **four** of its own tests
blocked, and `analysis/synthesis.md:1011` names **four** id groups. The eleven rows above are this
document's enumeration, reached by expanding the four groups to the individual ids and streams the
cards name. `[I]` The inference is that the report counted ids while the findings counted test
blocks; the number eleven is reproducible either way only by the expansion above, so the table,
not the number, is the locator.

---

## 8. Dispositions for the remaining 7.6 defects

`analysis/synthesis.md` section 7.6 lists 20 defects in the project's own code, all offline
fixable. This pass scoped itself to 15 of them. The rest are **not silently dropped**: each gets a
disposition below, so a later reader can tell "out of scope" from "overlooked". Rows #13 and #18
appear here because the earlier draft of this table filed them as not fixed; they were **fixed in
this pass as F15 and F16**.

| 7.6 # | Defect | Disposition |
|---|---|---|
| #4 | `set_polyphony` caps base polyphony at 8 while `[C]` 24 factory presets of 668 store 10, 12 or 14 | **Stays gated.** It is a device write against `docs/HakenMidi.h:1357` and the clamp behaviour is unknown until `DT9` runs. The `ValueError` and docstring name `maxNonMpePoly` 14, the 24 presets and the test. Spec: `T9` |
| #6 | `idOscFilOpt1..5` reported as `cascade_raw` when it is a type-dependent variant selector | Spec: `T15`. `eagan_mcp/knowledge/modules/oscillator-slots.md` states the mislabel explicitly, so no card quotes the wrong label |
| #9 | `describe_matrix_layout` promises verification markers it does not return; they exist only as source comments in `eagan_mcp/matrix_map.py` | Recorded in `eagan_mcp/knowledge/modules/index.md`, plus the preset-independence note in the tool's docstring, so no card cites a marker the tool will not show. The tool fix itself is a `T` item with no rank of its own |
| #10 | `set_preset_name` writes unverified - no `device_value`, no `verified`, not even a tri-state `None` - although a read-back exists two functions later | **Blocked behind F14**, which is `T20`. Fixing verification while the `description` argument is prohibited would invite its use. Deferred with F14, not closed |
| #11 | `write_formula_raw` validates `framing` inside the per-pair send loop, after the device has been pinged and a cell selected | **Open, not resolved.** It is already `.maister/docs/standards/global/validation.md:14`'s own `KNOWN VIOLATION` and is left as recorded, because moving it is a behaviour change to a tool with no test. A test for it is a `T` item with no rank of its own |
| #13 | `CC_TRANSMIT_UPDATES = 55` is unused **and wrong for 10.81** - ch16 cc55 is `ccCreaArchFin` | **Fixed in this pass as F15.** `minimal-implementation.md:24`'s unused-constant carve-out protects a constant that is *correct*; a wrong one is not documentation |
| #16 | `get_status` reports `dsp_polyphony: null` because cc72 arrives in the config dump, not the ping reply | Out of scope. The code change is offline - send `ccTask configToMidi`, cc109 value 16 - but its verification needs the device, so it stays out of an offline pass. It closes the `get_status` item in `ROADMAP.md` when it lands |
| #17 | `read_docs` passes an unvalidated caller path, so `"../../x"` escapes `docs/` | Recorded. **`get_knowledge` does not reproduce it** - its topic allowlist closes the class by construction for the new tool. Repairing `read_docs` itself is a `T` item with no rank of its own |
| #18 | `save_to_user_slot`'s guard is off by one: `len(names) > slot` should be `>= slot` | **Fixed in this pass as F16.** One character, latent, and it sits in the flash-writing path |
| - | Return-shape deviations: `disconnect -> str`, `get_recipes -> str`, `search_docs -> list[dict]`, `read_docs -> str`, `load_preset -> dict with nothing from the device` | Recorded against `.maister/docs/standards/global/conventions.md:60` as **convention, not defect**, for the read-only knowledge tools. `get_knowledge` deliberately joins the existing `str` / `list[dict]` precedent rather than inventing a third shape |

### Accepted debt, with its owner named

**21 of 30 shipped tool docstrings do not open with a write scope.**
`.maister/docs/standards/global/commenting.md:11-14` and
`.maister/docs/standards/protocol/device-safety.md:13-15` both require it in the first lines. The
docstring test added in this pass covers **six**; the other ~17 are a `T` item with no rank of its
own. **Deferred, not closed** - repairing them would touch more than half the shipped tool
surface in a pass whose scope is the knowledge base, and a sweeping edit to the tool surface is
exactly the change this pass agreed not to make. Owner: the next pass that touches
`eagan_mcp/server.py` for any other reason.

### Two standards conflicts recorded here as open

1. **`.maister/docs/standards/global/validation.md:14`'s `KNOWN VIOLATION`** - `write_formula_raw`
   validating `framing` inside the send loop - is **open**. 7.6 #11 above is the same defect; this
   document records it, it does not resolve it.
2. **`.maister/docs/standards/global/conventions.md:27`'s `UNRESOLVED CONFLICT`** - `.gitignore`
   excludes `docs/`, while `CLAUDE.md` names `docs/HakenMidi.h` the protocol source of truth - is
   **open**, and this document inherits it. Every `[G]` header citation above points at an
   **untracked** file that must be re-extracted from the Haken Editor install on each machine.
   The same applies to the guide citation in this file's own header.
