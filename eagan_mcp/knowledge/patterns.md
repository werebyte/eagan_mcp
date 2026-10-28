# Reusable constructions, frequency-ranked

Twenty-three constructions that recur across the 668 factory presets of Haken Editor 1081, each
with the MCP calls that build it or an explicit statement that no tool writes it.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

## What this chapter is, and what it is not

**This chapter is corpus-attested and explicitly NOT ear-tested.** Almost everything below was
measured by decoding 668 factory preset files; it is evidence about what Haken does, not about
what this project has heard come out of the Module. Of the twenty-three patterns, **nine** carry
a `[D]` device-verified claim at their core rule - P1, P3, P4, P5b, P6, P7, P9, P11 and P12 - and
in those nine it is the rule that is device-verified, never the whole construction. The other
fourteen have never been played.

`RECIPES.md` holds the opposite discipline: `ROADMAP.md`, "Each recipe tested on the Module by
ear before it goes in", with anything untested confined to its `## Candidates (not tested yet)`
section (`RECIPES.md:153`). **This chapter is not a peer of `RECIPES.md` and does not inherit that
bar.** Nor does it belong under "Candidates": twenty constructions attested across 668 presets are
not speculation. They are a third thing - a measured description of Haken's own house style - and
the per-claim tags below say which is which. A pattern here becomes a `RECIPES.md` recipe only
after someone plays it.

`[C]` can never upgrade to `[D]`. No amount of corpus agreement makes a construction
device-verified (`.maister/docs/standards/protocol/protocol-sources.md`, "The Five Bracket Tags").

## How to read a recipe

Cells are written the way the shipped catalog writes them, `column <- row = value`, which is the
order `set_matrix_point(row, col, value)` takes. Row and column numbers are the MCP's own
(`eagan_mcp/matrix_map.py`): rows 0 Noise, 1-5 Osc 1-5, 6/7/8 Bank A/B/C, 9/10 Audio In L/R,
11/12 Sub L/R, 13 `Direct +`, 14 `Direct + (2)`, 15 `Direct -`, 16 `Direct x (multiply)`; columns
0/1 Master SL/SR, 2-7 the six assignable Master columns, 8 Master/Dry mix, 9/10 Dry L/R,
11 separator, 12-26 Osc/Filter n input/F/B, 27-34 Bank A 1-8, 35-42 Bank B, 43-50 Bank C,
51-60 SG n F/T.

Worked examples name only the **49** factory presets whose decoded `wiring` block ships in
`eagan_mcp/knowledge/factory_catalog.json` (`eagan_mcp/preset_file.py:WIRING_PRESETS`), so prose
and data agree by construction. A quoted formula reads "preset-name slash letter equals summary"
and the summary is the catalog's own string, character for character; a quoted cell names the
column and lists the rows feeding it, in the catalog's own row names.

A module's columns are described by its card in `eagan_mcp/knowledge/modules/`; what is true of
every module is in `eagan_mcp/knowledge/modules/index.md`. This chapter describes constructions
**across** modules and never restates either - the three cross-reference
(`.maister/docs/standards/global/conventions.md:10`). In particular `modules/index.md` owns the
six cross-module patterns and they are cited here by number, never repeated.

---

## 1. Negative heights, stated once

- `[C]` A height written with its Neg flag set is an **offset**, not a sign-and-magnitude
  magnitude: flag-set raw `r` means `r/100 - 1.00`. Measured over all 668 factory presets, flag-set
  writes span raw 1..99 and never reach 100 while flag-clear writes run to 127, and 564 writes set
  the flag with the height id absent, which is -1.00 under this reading and a pointless -0.00 under
  the mirror reading.
- `[G]` The header gives the range but never the magnitude formula, so the offset reading is not a
  misread spec: `docs/HakenMidi.h:1201-1202`, verbatim, "true for -idHeightW; no effect until
  idHeightW received" and "height for W with idNegW -1.00..1.27 in 0.01 steps". The same pair
  repeats per component at `:1227-1230`, `:1242-1246` and `:1265-1268`.
- `[I]` **The codec already does this**, so every recipe below may be written as it reads:
  `eagan_mcp/formula.py:204-215` encodes and decodes the offset form, and
  `eagan_mcp/formula.py:222-231` reads an orphan Neg flag as -1.00. The inference for a recipe
  author is that no manual correction is needed any more - pass the value you want.
- `[I]` The companion default is settled the same way: `eagan_mcp/formula.py:41` sets
  `TRANSFER_DEFAULT["X"] = 1`, kHz, because a compressed preset omits only defaults and
  `idTransX = 1` is never written. The inference is that an X component with no transfer id is in
  kHz, not Octaves, so a pitch recipe that leaves `transfer` unset lands in the right unit.
- `[D]` Still open, and the one thing that would turn all of this into device evidence: no negative
  height has yet been confirmed by ear - `ROADMAP.md`, "Verify a NEGATIVE formula height on the
  device (header sign semantics)", 2026-10-25, fw 10.81.
- `[I]` **H6**: the codec fix does not reach heights already stored. User slots 4 and 5 were saved
  with the mirrored encoding and stay wrong on the device until those cells are rewritten; the
  inference is that re-saving the slot does not repair them, only re-entering the value does.

---

## 2. The statistics worth internalising

`[C]` The per-preset counts in section 2.1 were measured over the raw 668 preset files and are not
recomputable from the shipped catalog, which carries 49 wiring blocks; their source is
`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/corpus-patterns.md`
section 2.1. Sections 2.2 to 2.4 re-measure against `eagan_mcp/knowledge/factory_catalog_full.json`
and `eagan_mcp/knowledge/census.json`, both of which ship.

### 2.1 The twenty most-used matrix edges

`[C]` Count = presets of 668 holding at least one cell on that edge.

| presets | % | edge | what it is |
|---:|---:|---|---|
| 515 | 77% | `Direct +` -> `SG 1 F` | SG1 rate `[C]` |
| 512 | 76% | `Direct +` -> `SG 1 T` | SG1 trigger, paired with the row above `[C]` |
| 394 | 58% | `Direct +` -> `Bank A col 2` | bank A fundamental frequency `[C]` |
| 355 | 53% | `Direct +` -> `Bank A col 3` | bank A third column `[C]` |
| 353 | 52% | `Direct +` -> `SG 2 F` | SG2 rate `[C]` |
| 351 | 52% | `Direct +` -> `SG 2 T` | SG2 trigger, paired again `[C]` |
| 337 | 50% | `Direct +` -> `Osc/Filter 1 F` | osc 1 frequency `[C]` |
| 307 | 45% | `Direct +` -> `Osc/Filter 4 F` | osc/filter 4 frequency `[C]` |
| 306 | 45% | `Direct +` -> `Bank A col 4` | bank A fourth column `[C]` |
| 277 | 41% | `Direct +` -> `Bank A col 7` | bank A seventh column `[C]` |
| 259 | 38% | `Bank A` -> `Master SL` | bank A to the left output `[C]` |
| 257 | 38% | `Direct +` -> `Osc/Filter 5 F` | osc/filter 5 frequency `[C]` |
| 252 | 37% | `Direct +` -> `Osc/Filter 4 B` | filter 4 bandwidth `[C]` |
| 244 | 36% | `Bank A` -> `Master SR` | bank A to the right output `[C]` |
| 233 | 34% | `Direct +` -> `Bank C col 2` | delay time `[C]` |
| 224 / 222 | 33% | `Direct +` -> `SG 3 T` / `SG 3 F` | paired a third time `[C]` |
| 179 | 26% | `Osc/Filter 4` -> `Master SL` | filter output straight to the master `[C]` |
| 152 | 22% | `Direct x (multiply)` -> `Master SL` / `SR` | overall output gain trim `[C]` |
| 149 | 22% | `Direct +` -> `Master col 1` | an assignable master column `[C]` |
| 97 | 14% | `Bank C` -> `Bank C col 1` | delay feedback loop `[C]` |

`[I]` Two structural facts fall out, and the inference is about which row to reach for: `Direct +`
is the row for a control value - it is the "+" accumulator - and `Direct x (multiply)` is the row
for scaling whatever the `+` rows produced. `[C]` Of the 1,313 `SG n T` cells in the corpus, 1,246
sit on `Direct +` and 44 on `Direct -`.

### 2.2 Formula anatomy over all 7,259 formulas

`[C]` All four tables below are re-measured from `eagan_mcp/knowledge/factory_catalog_full.json`
over its 7,259 formulas; a share with no explicit id written is the device default.

| W source (`idSgW`) | formulas of 7,259 | share |
|---|---:|---:|
| Constant (default, id absent) | 5,030 | 69.3% `[C]` |
| SG1 | 813 | 11.2% `[C]` |
| SG2 | 500 | 6.9% `[C]` |
| Gated | 380 | 5.2% `[C]` |
| SG3 / SG4 / SG5 | 264 / 133 / 71 | 3.6% / 1.8% / 1.0% `[C]` |
| RMS of row | 34 | 0.5% `[C]` |
| FormulaDelay tap | 20 | 0.3% `[C]` |
| SG1b..SG5b | 14 | 0.2% `[C]` |

| W shape (`idShapeW`) | formulas of 7,259 | share |
|---|---:|---:|
| Ramp Up (default, id absent) | 5,589 | 77.0% `[C]` |
| Ramp Down | 425 | 5.9% `[C]` |
| Triangle | 359 | 4.9% `[C]` |
| Sine | 272 | 3.7% `[C]` |
| Hann | 242 | 3.3% `[C]` |
| Pulse | 143 | 2.0% `[C]` |
| S+H row | 84 | 1.2% `[C]` |
| Square | 58 | 0.8% `[C]` |
| per-letter S+H (`S+H A`..`S+H V`) | 44 | 0.6% `[C]` |

`[C]` The per-letter sample-and-hold total of 44 breaks down as `S+H B` 13, `S+H A` 11, `S+H H` 7,
`S+H O` 4 and nine single or double uses of seven further letters, all of 7,259 formulas.

| operator (`idFormOp`) | formulas of 7,259 | share |
|---|---:|---:|
| `W + X + Y + Z` (default, id absent) | 5,671 | 78.1% `[C]` |
| `W x (X + Y + Z)` | 940 | 12.9% `[C]` |
| `(W + X + Y) x Z` | 407 | 5.6% `[C]` |
| `(W + X) x (Y + Z)` | 223 | 3.1% `[C]` |
| `(W x X) + (Y x Z)` | 18 | 0.2% `[C]` |

| component carrying a non-zero height | share of 7,259 |
|---|---:|
| W | 69.0% `[C]` (5,006 formulas write `idHeightW`) |
| Z | 36.5% `[C]` (`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/corpus-patterns.md` section 2.2) |
| X | 19.7% `[C]` (`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/corpus-patterns.md` section 2.2) |
| ancillary operation | 19.2% `[C]` (1,392 formulas write `idAncOp`) |
| Y | 17.5% `[C]` (`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/corpus-patterns.md` section 2.2) |
| blend | 11.9% `[C]` (863 formulas write `idBlend`) |

- `[C]` 1,903 of 7,259 formulas (26.2%) write `idScaleW` at all, and 1,842 of those select
  `x macro` - the standard way the factory exposes a control on a knob.
- `[I]` **Z is used twice as often as X or Y**, which says the EaganMatrix is a pressure
  instrument first; the inference for this project is uncomfortable, because `[G]`
  `docs/HakenMidi.h:1256` `cInitial = 1` holds a component at its note-on value and a plain MIDI
  keyboard sends no continuous pressure, so a third of the factory's expressive content arrives
  frozen. Any pattern below that leans on Z says so in its own entry.
- `[C]` Per-component modes and transfers, over the formulas that use each component
  (`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/corpus-patterns.md` section 2.2): X - Continuous 1,374, Derivative 20,
  Initial 16, Relative 16; Y - Continuous 1,182, Initial 81, Derivative 4; Z - Continuous 2,550,
  Initial 71, Derivative 20, Release F 6.

### 2.3 Polyphony, and Double Computation Rate

- `[C]` Base polyphony over 668 presets, from `eagan_mcp/knowledge/census.json:polyphony_base`:
  1 - 86, 2 - 75, 3 - 131, 4 - 142, 5 - 43, 6 - 58, 7 - 17, 8 - 61, 10 - 14, 12 - 7, 14 - 3, and
  31 presets leave the id absent.
- `[G]` `set_polyphony` is capped at 1..8 and keeps the header's own ceiling,
  `docs/HakenMidi.h:1357`, verbatim, "base polyphony (lowest common denominator 2x dsp), values
  1..8". `[C]` 24 factory presets of 668 nevertheless store 10, 12 or 14, so those cannot be
  reproduced at their shipped voice count; raising the cap is `tools_spec.md` `T9`.
- `[C]` **Double Computation Rate is set explicitly in 41 presets of 668 (6.1%)**
  (`eagan_mcp/knowledge/census.json:double_computation_rate`, `explicit_true` 41,
  `absent_so_default` 627). Their base polyphony is distributed
  `{1: 4, 2: 16, 3: 11, 4: 6, 5: 1, 8: 1, absent: 2}` - not uniform, and not all at base 2.
- `[D]` The factory's restraint matches the one measurement this project has:
  `CLAUDE.md:153-154`, 2026-10-25, fw 10.81, "'Saw Swarm Warm' (slot 3) re-saved: base polyphony 6,
  '+' on, Double Computation Rate off. Double rate was the cause of 3 voices + 100% DSP; user
  confirmed no lag after the change." Treat it as a last resort.
- `[C]` Recirculator type over 668 presets, from `eagan_mcp/knowledge/census.json:recirculator`:
  Short Reverb 405 (41 written plus 364 taking the default), Modulated Delay 74, Analog Echo 64,
  Long Reverb 46, Digital Echo LPF 44, Swept Echo 19, Digital Echo HPF 16.

### 2.4 What macros are conventionally for

- `[C]` Most common first word of a macro label, harvested from the 668 description strings:
  Speed 77, Body 61, Release 57, Tone 52, Feedback 31, Ambience 30, Depth 21, Mute 21, Damp 20,
  Noise 20, Pitch 19, Size 17, Detune 16, Reverb 16, Balance 14, Spring 13, Echo 12, Delay 12,
  Tuning 12, Spread 11, Filter 10, Mod 10, Height 10
  (`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/corpus-patterns.md` section 2.4).
- `[I]` A patch that puts Speed, Tone, Body and Release on macros i-iv is following the house
  style; the inference is only that the labels are conventional, not that the device enforces
  anything.
- `[C]` There is no "Release" the MCP can write. Decay and release are **persistence**, id 63 -
  `eagan_mcp/formula.py:121` `PERSISTENCE_IDS = (63, 81)` sits in `DECODE_ONLY_IDS` at
  `eagan_mcp/formula.py:181`, and `eagan_mcp/formula.py` `encode_changes` states "nothing here writes them". So a
  pattern below can give a sound its own attack and shape but **not a release**, except as a second
  slow ramp-down SG or a Recirculator tail; writing persistence is `tools_spec.md` `T5`.
- `[C]` **The formula-letter pool is 44** - `A`..`V` and `A'`..`V'` - and every letter is shared
  device-wide, so changing one cell's formula changes every cell using that letter
  (`eagan_mcp/formula.py:ANC_VALUES`, 22 plain plus 22 primed). `[I]` Prefer `A`..`V`, because the
  factory corpus and this project's own recipes use only those and a primed letter has never been
  written from the MCP; allocation is unsolved and is `tools_spec.md` `T6`.
- `[C]` A matrix cell holds a whole digit `1`..`9` or a `.nnnn` decimal, so a value such as "1.25"
  has no cell encoding at all (`eagan_mcp/haken.py` matrix value codes: 50..58 are `1`..`9` and the
  decimal path sends its digits separately). Build the fractional part as a formula instead.
- `[I]` Removing a formula's letter from the matrix deletes the formula on save, because the
  Module omits an unreferenced all-zero formula from its dump; the inference is to **disable a
  formula, never clear it** - set its heights to zero or mute the cell, and leave the letter in
  place.

### 2.5 What substitutes for an ADSR

- `[G]` There is none, and the firmware's own documentation says so:
  `docs/EaganMatrix Preset Cookbook.txt:3069-3072`, verbatim, "Note: There is no generic ADSR
  envelope control for EaganMatrix. It all must be programmed and to large extent, your finger
  envelope controls the dynamic profile of most presets."
- `[G]` The `Analog ADSR` preset's own macro mapping is the canonical substitution, verbatim from
  `docs/EaganMatrix Preset Cookbook.txt:3053-3067`: attack is "Cutoff Ramp up time", decay is
  "Cutoff ramp up persistence", "Sustain produced by holding note", release is "SL/SR Persistence
  Control" and envelope depth is "Cutoff ramp range". Four of the five are a shape generator on a
  filter cutoff; only sustain is free.
- `[G]` Five named ways to make a sound ring on after the finger leaves, from
  `docs/EaganMatrix Preset Cookbook.txt:1003-1044`: the sustain pedal on CC 64; the Recirculator's
  decay and mix; **persistence**, which "will delay the time a function takes to end"; reducing a
  filter's bandwidth, which "often has the side effect of letting a sound ring out for longer";
  and "a very single cycle slow ramp down (SG4 F=0.01) of 100 seconds on the output".
- `[I]` Only two of those five are MCP-writable today. Persistence is decode-only (section 2.4)
  and no tool writes the Recirculator's configuration, so the reachable release is the **slow
  ramp-down SG** and the **bandwidth reduction** - which is why P1's release-triggered variant and
  P9's filter envelope carry more weight here than they do in the factory. The inference for a
  recipe author is to build the tail out of a second SG from the start rather than to expect to add
  it later. The persistence write surface is `tools_spec.md` `T5`.
- `[I]` The Cookbook is a weaker guide citation than the rest of `docs/`: it is written by a user,
  R. Kram, not by Haken, so it describes what presets do rather than what the firmware guarantees.
  The inference is to treat it as the strongest available statement of intent and still below any
  device measurement, per the resolution order in
  `.maister/docs/standards/protocol/protocol-sources.md`.

---

## 3. The twenty-three patterns

`[C]` Every quoted cell and every quoted formula summary below is read out of
`eagan_mcp/knowledge/factory_catalog.json` and agrees with it character for character. The
per-preset and per-cell **counts** are not recomputable from that file, which carries 49 wiring
blocks of the 668 presets; they come from
`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/corpus-patterns.md`
section 3, which measured the raw files, and each carries its denominator where it is used.

### P1. Envelope - a one-shot shape generator

- `[C]` The most-used construction in the corpus. In the 246 modern presets, 433 shape-generator
  instances are read by a formula with a non-zero W height, and **all 433 have both their `F` and
  their `T` column fed**; 193 of those are Single Cycle SGs, and 178 of the Single Cycle `T` cells
  hold the predefined `W` gated-note code.
- `[D]` The rule behind it is device-verified: `CLAUDE.md:116`, 2026-10-25, fw 10.81, "Gotcha: a
  Continuous/Single Cycle SG needs its T column (e.g. Direct+ -> SG n T = W) or it never starts."
- `[C]` **Scope it to those two SG types.** Over all 668 presets,
  `eagan_mcp/knowledge/census.json:techniques` counts `shape_generator_wired` 539 and
  `shape_generator_triggered` 530, so 530 of the 539 presets that wire an SG column feed its
  trigger. A Dual or Phase-from-Matrix-Row SG uses its second column differently and demanding `T`
  of it would be a false alarm - see `modules/index.md` cross-module pattern 6 for the general
  form of the rule.
- `[C]` Shape choice for a Single Cycle SG: absent/Ramp Up 93, Ramp Down 83, Pulse 28, Triangle 20,
  Steep Down 7, of the 193 Single Cycle uses in the 246 modern presets. Ramp Down is the decay
  envelope.
- `[C]` `Dueling BiqBanks` runs SG1 and SG2 as Single Cycle with `Steep Down`:
  `Dueling BiqBanks`: `col 52 <- Direct + = W` is the trigger, `Dueling BiqBanks`: `col 27 <- Noise
  = A` places the envelope, and `Dueling BiqBanks`/`A` =
  `[W + X + Y + Z] W = SG1 0.1 x 0.1 [shape Steep Down]`.
- `[C]` The rate column takes a formula just as often as a constant:
  `Dueling BiqBanks`/`G` =
  `[W + X + Y + Z] W = Constant 0.99 x 100 x Macro (v) ; Y = Continuous 1.0->1.0 x 1` drives
  `SG 1 F`, which puts envelope speed on a macro.

```
set_shape_generator(sg=1, type_name="Single Cycle")
set_matrix_point(row=13, col=52, value="W")        # SG 1 T = gated note  <-- NEVER SKIP
set_matrix_point(row=13, col=51, value="G")        # SG 1 F = the rate
set_formula(row=13, col=51, component="W", mode="Constant", value=0.99, magnitude=100)
set_matrix_point(row=0, col=27, value="A")         # where the envelope is used
set_formula(row=0, col=27, component="W", mode="SG1",
            sg_shape="Ramp Down", value=1.0, magnitude=1)
```

- `[C]` **Variant, release-triggered.** 44 `SG n T` cells sit on the `Direct -` row.
  `The Long Goodbye`: `col 54 <- Direct + = 0.5, Direct - = W` makes the trigger `0.5 - gate`, so
  the SG fires when the note is released. This is the nearest thing to a release the matrix offers
  without persistence.
- `[C]` **Variant, SG chained from another SG.** 118 `SG n T` cells hold a formula letter.
  `Underwater Ceramics`: `col 52 <- Direct + = D` with `Underwater Ceramics`/`D` =
  `[W + X + Y + Z] W = SG4 1.0 x 1 [shape Pulse]`, so SG4's pulse retriggers SG1.

### P2. Output level into the Master

- `[C]` Of the 2,797 cells in `Master SL` and `Master SR` across 668 presets, 1,819 hold a formula
  letter, 411 the constant `1`, 207 the predefined `z^2` and 113 the constant `0.5`. Driving both
  Master columns from the **same** letter is the most common shared-letter pair in the corpus by a
  factor of eight, 753 presets against 88 for the runner-up.
- `[C]` The cheapest version is two predefined codes and no formula:
  `SineBank - Basic`: `col 0 <- Bank A = z^2`.
- `[C]` The usual version is one letter, gated and wheel-trimmable:
  `Resonant Drum 2`/`J` = `[W x (X + Y + Z)] W = Gated 0.5 x 10 ; Y = Continuous 1.0->0.5 x 1`
  drives both `Master SL` and `Master SR`.
- `[C]` Overall gain trim: 152 presets of 668 (22%) drive `Direct x (multiply)` into both Master
  columns. `Soundboard 2`: `col 0 <- Tap 1 = B, Tap 3 = B, Direct x (multiply) = 0.7` trims down;
  `Dueling BiqBanks` uses the constant `2` on the same cell to trim up.

```
set_matrix_point(row=6, col=0, value="z^2")        # Bank A -> Master SL, pressure squared
set_matrix_point(row=6, col=1, value="z^2")
# or, one shared letter instead:
set_matrix_point(row=6, col=0, value="J")
set_matrix_point(row=6, col=1, value="J")
set_formula(row=6, col=0, component="W", mode="Gated", value=0.5, magnitude=10,
            operator="W x (X + Y + Z)")
set_formula(row=6, col=0, component="Y", height_begin=1.0, height_end=0.5)
```

- `[I]` `z^2` is continuous pressure squared, so on a plain MIDI keyboard it freezes at its
  note-on value; the inference is that `z^2` behaves as a velocity curve there, not as an
  expression control. See P8.

### P3. Pitch tracking on a frequency column

- `[D]` The cheapest route is not a formula at all: `RECIPES.md:122`, 2026-10-25, fw 10.81,
  "`Direct + -> Bank A F (28) = X`, `Direct + -> Bank A sF (29) = 1`." The predefined `X` matrix
  code is concert pitch.
- `[C]` The factory agrees: `Boson Particles Wbl`: `col 28 <- Direct + = X`,
  `Model String Wind`: `col 28 <- Direct + = X` and `Resonant Drum 2`: `col 36 <- Direct + = X`
  all take it, among hundreds of presets.

```
set_matrix_point(row=13, col=28, value="X")        # Bank A col 2 = concert pitch, no formula
```

- `[C]` **Idiom A, exact pitch as a formula - 216 formulas.** Needed only when something must be
  added to the pitch inside one letter. `SineBank - Basic`/`B` =
  `[W + X + Y + Z] X = Continuous -1.0->1.0 x 1` with transfer `X kHz`, and the same shape in
  `Bird Echoer`/`E` = `[W + X + Y + Z] X = Continuous -1.0->1.0 x 1`,
  `FM Bells`/`F` = `[W + X + Y + Z] X = Continuous -1.0->1.0 x 1` and
  `The Long Goodbye`/`F` =
  `[W x (X + Y + Z)] W = Gated 1.0 x 1 ; X = Continuous -1.0->1.0 x 1`.
- `[G]` The arithmetic is the guide's own, `docs/EaganMatrixUserGuide.txt:4660-4664`, verbatim:
  "when kHz is selected: nnToKHz (60.0 + quant (nn - nn0) x (X Slider + X Fine) x Multiplier)"
  with "X Slider = X Above Slider when nn > nn 0, otherwise negative of X Below Slider". With
  X Below -1.00 and X Above +1.00 the slider is +1.00 on both sides of the zero point and the
  expression collapses to `nnToKHz(nn)`.

```
set_formula(row=13, col=28, component="X",
            height_begin=-1.0, height_end=1.0, multiplier=1, transfer="X kHz")
```

- `[C]` **Idiom B, pitch in semitones plus a transpose - 197 formulas, a third of all factory pitch
  formulas.** `Cascade`/`A` = `[W + X + Y + Z] X = Continuous -0.12->0.12 x 100` with transfer
  `X Oct`, and the same in `Additive Vocal 1 Transform`/`A` =
  `[W + X + Y + Z] X = Continuous -0.12->0.12 x 100 ; Y = Continuous -0.19->-0.14 x 1` and
  `Additive Gnilham`/`A` =
  `[W + X + Y + Z] X = Continuous -0.12->0.12 x 100 ; Y = Continuous -0.2->0.02 x 1`. Under the
  Octaves equation `(nn - nn0) x 12 / 12` is the pitch in semitones relative to the zero point,
  which is then handed to `idAncNN` to become a note number again.
- `[I]` **Idiom B cannot be built with `set_formula` at all.** Its second half is `idAncNN = 1`
  (id 10), and no tool writes it: `eagan_mcp/server.py:set_formula` exposes no ancillary parameter,
  so the only route is `write_formula_raw`. The inference is that a third of the factory's pitch
  formulas are out of reach of the typed tool; the ancillary write surface is `tools_spec.md`
  `T13`.

```
# the MCP-reachable half:
set_formula(row=13, col=28, component="X",
            height_begin=-0.12, height_end=0.12, multiplier=100, transfer="X Oct")
# the rest is raw - idAncNN = 1 at id 10:
write_formula_raw(row=13, col=28, pairs=[[10, 1]])
```

### P4. Vibrato and LFO - a continuous-cycle shape generator

- `[C]` In the 246 modern presets, 240 SG instances read by a formula are Continuous Cycle, which
  is the `idSgTyp` default and therefore never written to the file. Their `T` column holds the
  gated `W` in 160 cases, restarting the LFO on each note, and the constant `1` in 89, leaving it
  free-running.
- `[C]` Shapes used by Continuous Cycle formulas: Triangle 122, Sine 69, Hann 52, absent/Ramp Up
  36, Ramp Down 20, S+H row 16, Square 15, Pulse 11, of those 240 uses.
- `[C]` Depth scale is the thing to get right. On a frequency column the factory reaches for
  magnitude 0.01: `BiqMouth - Basic`/`A` =
  `[W + X + Y + Z] W = SG1 0.14 x 0.01 [shape Sine]`, i.e. 0.0014. Into an excitation column it
  uses ten times more, `Dueling BiqBanks`/`A` =
  `[W + X + Y + Z] W = SG1 0.1 x 0.1 [shape Steep Down]`.
- `[C]` Slower, coarser modulation on a non-pitch column: `Underwater Ceramics`/`B` =
  `[W + X + Y + Z] W = SG2 1.0 x 1 [shape Triangle]`.
- `[D]` Putting the depth on the wheel is a change of operator, not of component:
  `CLAUDE.md:117-118`, 2026-10-25, fw 10.81, "Formula operator: id 38 (0 W+X+Y+Z, 1 Wx(X+Y+Z), ...)
  ... Envelope scaled by mod wheel = W SGn + Y on + operator 1."

```
set_matrix_point(row=13, col=52, value="1")        # SG 1 T = 1 -> free-running
set_matrix_point(row=13, col=51, value="K")        # SG 1 F = the rate
set_formula(row=13, col=51, component="W", mode="Constant", value=0.5, magnitude=10)
set_matrix_point(row=13, col=28, value="A")        # onto a frequency column
set_formula(row=13, col=28, component="W", mode="SG1", sg_shape="Sine",
            value=0.14, magnitude=0.01, operator="W x (X + Y + Z)")
set_formula(row=13, col=28, component="Y", height_begin=0.0, height_end=1.0)
```

### P5a. Harmonic stack - integer constants on `Direct x (multiply)`

- `[C]` The WaveBank and SineBank idiom: one pitch cell per partial column, then a whole-number
  multiplier beside it. `Boson Particles Wbl`: `col 28 <- Direct + = X`, then
  `Boson Particles Wbl`: `col 29 <- Direct + = X, Direct x (multiply) = 2`,
  `Boson Particles Wbl`: `col 30 <- Direct + = X, Direct x (multiply) = 3`,
  `Boson Particles Wbl`: `col 31 <- Direct + = X, Direct x (multiply) = 4` and
  `Boson Particles Wbl`: `col 32 <- Direct + = X, Direct x (multiply) = 5`.
- `[C]` The same trick on oscillator slots: 46 presets of 668 share a formula letter between
  `Osc/Filter 1 F` and `Osc/Filter 2 F`, 45 between `2 F` and `3 F`.
- `[I]` This is the concrete form of `modules/index.md` cross-module pattern 2; the inference here
  is only that whole integers give a harmonic series while anything else detunes, which is P5c.

```
for n, ratio in enumerate(["2", "3", "4", "5"], start=1):
    set_matrix_point(row=13, col=28 + n, value="X")          # Bank A col 3..6 = pitch
    set_matrix_point(row=16, col=28 + n, value=ratio)        # Direct x -> the partial number
```

### P5b. Chorus detune - one SG read at several phases

- `[C]` The factory's chorus: one shape generator, read by several formulas that differ only in
  phase, each landing on a different partial's frequency column. `BiqMouth - Basic` is the clean
  case, with `BiqMouth - Basic`/`A` = `[W + X + Y + Z] W = SG1 0.14 x 0.01 [shape Sine]`,
  `BiqMouth - Basic`/`B` =
  `[W + X + Y + Z] W = SG1 0.15 x 0.01 [shape Sine, phase 0.25]`,
  `BiqMouth - Basic`/`C` =
  `[W + X + Y + Z] W = SG1 0.13 x 0.01 [shape Sine, phase 0.5]` and
  `BiqMouth - Basic`/`D` =
  `[W + X + Y + Z] W = SG1 0.11 x 0.01 [shape Sine, phase 0.75]`.
- `[C]` They sit on `Direct + (2)`, not `Direct +`, so the detune **adds** to the pitch already on
  `Direct +`: `BiqMouth - Basic`: `col 28 <- Direct + = X, Direct + (2) = A` through
  `BiqMouth - Basic`: `col 31 <- Direct + = X, Direct + (2) = D`.
- `[C]` `Choir and Ext` builds the same chorus with only two phase offsets and flips the sign of
  the other two instead, all four scaled by one macro: `Choir and Ext`/`C` =
  `[W + X + Y + Z] W = SG1 0.42 x 1 [shape Sine] x Macro (iii) ; X = Continuous None->0.12 x 100`,
  `Choir and Ext`/`D` =
  `[W + X + Y + Z] W = SG1 -0.34 x 1 [shape Sine] x Macro (iii) ; X = Continuous None->0.12 x 100`,
  `Choir and Ext`/`E` =
  `[W + X + Y + Z] W = SG1 0.19 x 1 [shape Sine, phase 0.25] ; X = Continuous None->0.12 x 100`
  and `Choir and Ext`/`F` =
  `[W + X + Y + Z] W = SG1 -0.28 x 1 [shape Sine, phase 0.75] x Macro (iii) ; X = Continuous None->0.12 x 100`.
- `[D]` One SG at several phases rather than several SGs is also the performance-safe choice:
  `RECIPES.md:18-19 (moved to pitfalls.md section 5, item 42)`, 2026-10-25, fw 10.81, several continuous SGs on different oscillator F
  columns make the panel knobs unusable while one shared SG does not.

```
set_matrix_point(row=13, col=52, value="1")                  # SG 1 T = free-running
set_matrix_point(row=13, col=51, value="K")                  # SG 1 F = chorus rate
set_formula(row=13, col=51, component="W", mode="Constant", value=0.5, magnitude=1)
for n, (letter, phase, depth) in enumerate(
        [("A", "Off", 0.14), ("B", "0.25", 0.15), ("C", "0.5", 0.13), ("D", "0.75", 0.11)]):
    set_matrix_point(row=14, col=28 + n, value=letter)       # Direct + (2), so it ADDS to X
    set_formula(row=14, col=28 + n, component="W", mode="SG1",
                sg_shape="Sine", sg_phase=phase, value=depth, magnitude=0.01)
```

### P5c. Static detune spread - small constants on `Direct -`

- `[C]` A fixed, increasing downward offset per partial, independent of any LFO.
  `BiqMouth - Basic` puts it on the same four WaveBank frequency columns that already carry the
  chorus: `BiqMouth - Basic`: `col 28 <- Direct - = 0.001`,
  `BiqMouth - Basic`: `col 29 <- Direct - = 0.002`,
  `BiqMouth - Basic`: `col 30 <- Direct - = 0.003` and
  `BiqMouth - Basic`: `col 31 <- Direct - = 0.004`.
- `[C]` It is a bare constant on a third row, so it stacks with P5a's multiplier and P5b's phase
  spread on one column without a formula letter: that one cell already carries
  `BiqMouth - Basic`: `col 28 <- Direct + = X, Direct + (2) = A, Direct - = 0.001`.
- `[I]` The spread is sub-cent at these values, because the frequency columns are in kHz and 0.001
  is one hertz; the inference is that a detune audible as beating wants a ramp of this order and
  not more, and that four slightly different values beat against each other rather than drifting
  together.

```
for n, offset in enumerate(["0.001", "0.002", "0.003", "0.004"]):
    set_matrix_point(row=13, col=28 + n, value="X")          # pitch on Direct +
    set_matrix_point(row=15, col=28 + n, value=offset)       # Direct - = a fixed flat offset
```

### P5d. Symmetric two-bank detune - `Direct + (2)` against `Direct -`

- `[C]` One letter detunes two identical banks in opposite directions. `Silver Bar` runs two
  BiqGraph banks and spreads them with `C`: `Silver Bar`: `col 29 <- Direct + = D, Direct + (2) =
  C` sharpens bank A while `Silver Bar`: `col 37 <- Direct + = D, Direct - = C` flattens bank B by
  the same amount.
- `[C]` The spread opens with pressure rather than sitting fixed: `Silver Bar`/`C` =
  `[W x (X + Y + Z)] Z = Continuous None->0.5 x 1`.
- `[C]` 41 presets of 668 share a formula letter between `Bank A col 3` and `Bank B col 3`, so the
  two-bank construction is the ordinary way to use a second bank of the same type.
- `[I]` Because it is **one** letter on two rows, the two banks can never drift apart; the
  inference is that this is the construction to choose when a stereo pair must stay symmetric, and
  P5b's independent letters the one to choose when it must not. On a plain MIDI keyboard the `Z`
  here is frozen at note-on, so the spread is set by velocity and does not open under the finger.

```
set_matrix_point(row=13, col=29, value="D")        # Bank A col 3 = the shared pitch letter
set_matrix_point(row=14, col=29, value="C")        # Direct + (2) -> bank A sharp by C
set_matrix_point(row=13, col=37, value="D")        # Bank B col 3 = the same letter
set_matrix_point(row=15, col=37, value="C")        # Direct -    -> bank B flat by C
set_formula(row=14, col=29, component="W", mode="Constant", value=1.0, magnitude=1,
            operator="W x (X + Y + Z)")
set_formula(row=14, col=29, component="Z", height_begin=0.0, height_end=0.5)
```

### P6. FM and cross-modulation - an audio row into a frequency column

- `[C]` 131 cells across the 668 presets put an audio row onto an oscillator frequency column:
  `Osc/Filter 2` -> `Osc 1 F` 19, `Osc/Filter 3` -> `Osc 1 F` 11, `Osc/Filter 2` -> `Osc 3 F` 9,
  `Noise` -> `Osc 1 F` 9, `Osc/Filter 5` -> `Osc 3 F` 7, then a long tail.
- `[C]` `FM Bells` is the shipped worked example, with two modulators on one carrier and the pitch
  beside them: `FM Bells`: `col 13 <- Osc 2 = A, Osc 3 = A, Direct + = F, Direct x (multiply) = 2`.
- `[C]` The modulation index carries its own envelope and its own velocity scaling:
  `FM Bells`/`A` =
  `[W x (X + Y + Z)] W = SG3 0.32 x 1 [shape Ramp Down] x Macro (iii) ; Z = Initial 0.14->0.25 x 10`.
- `[D]` This is the construction the user has already played and found safe: `CLAUDE.md:141-142`,
  2026-10-25, fw 10.81, "Tested by the user: FM via an audio row into osc F ('FM Wheel Vibrato',
  Osc 3 -> Osc 1 F, SG x Y) does NOT cause knob lag. The pitfalls are specific to Direct-row
  constructions."
- `[C]` The corpus agrees with the restriction: no factory preset delivers an FM index on a
  `Direct` row. `[C]` 9 presets of 668 route `Noise` -> `Osc 1 F` and 5 `Noise` -> `Osc 2 F`, which
  is random frequency modulation rather than FM.

```
set_osc_type(slot=3, type_name="DSF Oscillator")
set_matrix_point(row=13, col=19, value="X")        # Osc/Filter 3 F = the modulator's pitch
set_matrix_point(row=3,  col=13, value="A")        # Osc 3 row -> Osc/Filter 1 F = the index
set_formula(row=3, col=13, component="W", mode="SG3", sg_shape="Ramp Down",
            value=0.32, magnitude=1, modifier="x Macro", macro="iii",
            operator="W x (X + Y + Z)")
set_formula(row=3, col=13, component="Z", mode="Initial",
            height_begin=0.14, height_end=0.25, multiplier=10)
```

### P7. Sub-oscillator - `Direct x (multiply)` below 1

- `[C]` The whole bank drops an octave when the multiplier sits on the same column as the pitch:
  `Dueling BiqBanks`: `col 28 <- Direct + = X, Direct x (multiply) = 0.5`. The constant `0.5` on
  `Direct x (multiply)` into `Bank A col 2` appears in 83 presets of 668.
- `[C]` Two octaves down and one octave up are the same move with a different constant:
  `The Long Goodbye`: `col 28 <- Direct + = X, Direct x (multiply) = 0.25` and
  `The Long Goodbye`: `col 13 <- Direct + = X, Direct x (multiply) = 2`.
- `[D]` The user's own variant puts the halved copy on a separate partial column instead:
  `CLAUDE.md:161-162`, 2026-10-25, fw 10.81, "Bank A WaveBank (4 detuned saws + f5 = X x .5
  sub-octave via Direct+ X and Direct x .5 on col 32) -> Bank B BiqMouth -> Master."
- `[I]` The two placements differ in what survives: on the pitch column the whole bank moves, on
  one partial column only that partial does. The inference is to choose by whether the sub should
  be a separate voice in the spectrum or a transposition of everything.

```
set_matrix_point(row=13, col=28, value="X")        # Bank A col 2 = pitch
set_matrix_point(row=16, col=28, value="0.5")      # Direct x -> one octave down
```

### P8. Velocity - `Z` or `Y` in `Initial` mode

- `[C]` 71 formulas set `Z` to `Initial` with a non-zero height and 81 set `Y`, 152 in all over
  7,259 formulas. Of the `Z` ones, 35 keep the default operator while 16 use `(W + X) x (Y + Z)`,
  14 `W x (X + Y + Z)` and 6 `(W + X + Y) x Z` - roughly half are multiplicative, which is what
  "velocity scales this" means.
- `[G]` `Initial` samples the component at note-on and holds it: `docs/HakenMidi.h:1256`
  `cInitial = 1`.
- `[D]` **"Holds it" is a trap on an output column: a formula whose only live component is
  `Initial` NEVER RELEASES.** Device-confirmed 2026-10-28. `worked_examples.md`'s Plan 2 shipped
  `[(W + X + Y) x Z] W = Constant ; Z = Initial` as its output level, and a patch built from it
  hung every note - the Constant does not fall and the `Initial` Z is held for the life of the
  note, so nothing in the product ever reaches zero. `model.md` section 7 gives the rule: **W is
  the only component the note-off path drives to zero**, so pair `Initial` velocity with
  `W = Gated` rather than `W = Constant`. With that one change the same patch stopped cleanly on
  key-up. Note the corpus idiom this pattern is read off (`Dueling BiqBanks`) carries the
  non-releasing shape too, so treat it as a template for the LEVEL, not for the gate.
- `[I]` On a plain MIDI keyboard that sampled value **is** the note velocity, which makes this the
  single most important pattern for this project's main use case; the inference is that `Initial`
  is the only mode that behaves identically on a Continuum and on a keyboard, because the others
  need continuous finger data the keyboard never sends.
- `[C]` `Dueling BiqBanks` uses it as the final multiplier on the output level:
  `Dueling BiqBanks`/`D` =
  `[(W + X + Y) x Z] W = Constant -0.31 x 1 x Macro (i) ; Y = Continuous 1.0->None x 1 ; Z = Initial None->1.0 x 1`.
  A `None` end height means the id is absent, i.e. zero, so `Z` ramps 0 -> 1.0.
- `[C]` `FM Bells` scales the FM index the same way, with a floor so that a soft note still speaks:
  `FM Bells`/`A` =
  `[W x (X + Y + Z)] W = SG3 0.32 x 1 [shape Ramp Down] x Macro (iii) ; Z = Initial 0.14->0.25 x 10`.

```
set_matrix_point(row=6, col=0, value="D")
set_formula(row=6, col=0, component="W", mode="Constant", value=1.0, magnitude=1,
            operator="(W + X + Y) x Z")
set_formula(row=6, col=0, component="Z", mode="Initial",
            height_begin=0.0, height_end=1.0, multiplier=1)
```

### P9. Filter envelope and filter sweep

- `[C]` `Direct +` -> `Osc/Filter 4 B` appears in 252 presets of 668 (37%), `Osc/Filter 1 B` in
  217, `Osc/Filter 5 B` in 210, `Osc/Filter 2 B` in 166 - the bandwidth column is the second most
  driven thing on a filter slot after its frequency.
- `[C]` 41 presets of 668 drive `Osc/Filter 1 B` and `2 B` from the same letter and 40 share
  `2 B` and `3 B`, i.e. one envelope across a filter cascade.
- `[C]` `Kinetic SatPad` takes it to the limit: all five bandwidth columns hold the same letter,
  `Kinetic SatPad`: `col 14 <- Direct + = D` through the matching cells on columns 17, 20, 23
  and 26, with `Kinetic SatPad`/`D` = `[W + X + Y + Z] Y = Continuous None->0.65 x 1`, so the mod
  wheel opens all five filters together.
- `[D]` `Y` is the wheel: `CLAUDE.md:119`, 2026-10-25, fw 10.81, "MIDI in: CC 1 (mod wheel) is read
  as Y (Continuum guide). Macros i..iv = ch1 CC 12..15 (guide sec. 15/ch1 table)."
- `[C]` Slot-type conventions worth copying: slot 1 is most often an oscillator (`Integrated DSF`
  25, `Phase Generator` 14 of 668) and slots 4 and 5 most often filters (`High Pass` 29 and 20,
  `Low Pass 1-pole` 27, `Band Pass` 16 and 16, `High Shelf` 19 on slot 5).
- `[I]` **The cascade option is not MCP-writable.** Cascade depth lives in `idOscFilOpt`
  (`s_Mat_Poke` ids 77-81) and no tool writes it, so a four-pole filter cannot be built from the
  MCP even though `cascade 4` is the most common non-default option in the corpus; the inference
  is that a filter recipe here is always one pole deep unless the preset it starts from already
  cascades. The write surface is `tools_spec.md` `T15`.
- `[C]` `extreme_rate` (`idFilExtrm`) is set in 1 preset of 668 - exotic, not a knob to reach for.

```
set_osc_type(slot=4, type_name="Low Pass")         # the "cascade 4" option is out of reach
set_matrix_point(row=13, col=22, value="X")        # Osc/Filter 4 F = track pitch
set_matrix_point(row=13, col=23, value="D")        # Osc/Filter 4 B = the envelope
set_formula(row=13, col=23, component="W", mode="SG1", sg_shape="Ramp Down",
            value=0.6, magnitude=1)
set_formula(row=13, col=23, component="Y", height_begin=0.0, height_end=0.65)
```

### P10. Delay feedback loop

- `[C]` `Bank C` -> `Bank C col 1` appears in 97 presets of 668: 55 with a SummedDelay and 42 with
  a VoiceDelay. That is the delay's own output fed back into its input.
- `[C]` The dry send and the feedback share the cell: `Boson Particles Wbl`: `col 43 <- Bank A =
  0.25, Bank C = E` and `Choir and Ext`: `col 43 <- Osc 5 = 1, Bank C = 0.5, Direct x (multiply) =
  R`.
- `[C]` Feedback amount on a macro is the convention: `Cascade`: `col 43 <- Osc 1 = C, Osc 2 = C,
  Osc 4 = H, Osc 5 = H, Bank C = G, Direct x (multiply) = V` with `Cascade`/`G` =
  `[W + X + Y + Z] W = Constant 0.99 x 1 x Macro (iv)`.
- `[G]` **The PScaler rule, and it is rare, so here is why it matters.**
  `docs/EaganMatrixUserGuide.txt:4166-4170`, verbatim: "When using the PScaler as a multiplier in
  the input column to the Summed delay, changes to the polyphony will properly compensate for how
  many voices are being fed into the delay at a time. This is critical if one is using a feedback
  system, like when designing repeating echoes."
- `[C]` Only 27 presets of 668 use `idScaleW = 1/dspPoly`, but **eight of the 49 presets with a
  shipped wiring block are among them**, so the construction is well attested where it can be read
  in full: `Cascade`/`V` = `[W + X + Y + Z] W = Constant 1.0 x 1 x Polyphony scaler`,
  `Choir and Ext`/`R` = `[W + X + Y + Z] W = Constant 1.0 x 1 x Polyphony scaler`,
  `Harmonic Viol`/`K` = `[W + X + Y + Z] W = Constant 1.0 x 1 x Polyphony scaler`,
  `Additive Horn 1 Wbl`/`K` = `[W + X + Y + Z] W = Constant 1.0 x 1 x Polyphony scaler`,
  `Additive Vocal 1 Transform`/`I` = `[W + X + Y + Z] W = Constant 1.0 x 1 x Polyphony scaler`,
  `Shimmer Wbl`/`A` = `[W + X + Y + Z] W = Constant 0.85 x 1 x Polyphony scaler`, and
  `Bird Echoer`/`G` = `[W + X + Y + Z] W = Constant 0.5 x 1 x Polyphony scaler`, which is the
  feedback coefficient itself on `Bird Echoer`: `col 43 <- Bank A = z^2, Bank C = G`.
- `[C]` The eighth is a trap worth naming: `Boson Particles Wbl`/`E` =
  `[W + X + Y + Z] no active component, but W.modifier=x Polyphony scaler, blend.control=macro, blend.macro_or_formula_raw=4, secondary.W.value=1.0`.
  A summary that opens "no active component" has not said the letter does nothing - the scaler and
  the whole blended secondary formula are still there, in the `blend` and `secondary` keys.
- `[C]` The guide names a preset for this that the shipped data contradicts, so both sides stand:

```
CONFLICT: which preset demonstrates the PScaler - Instant Reich vs eight others
  docs   [G]: "Instant Reich: See formula D for use of the PScaler function."
              - docs/EaganMatrixUserGuide.txt:4176
  corpus [C]: Instant Reich's decoded formula D is
              "[W + X + Y + Z] W = Constant 1.0 x 1 x Macro (i)" - no polyphony scaler at all;
              8 of the 49 presets with a shipped wiring block do carry one (list above)
  follows: the corpus. The recipe below is built from Cascade/V and Bird Echoer/G, which are
           readable in eagan_mcp/knowledge/factory_catalog.json. The guide's pointer is left
           standing: it may name a formula letter from an earlier firmware's version of the
           preset, which this project cannot check offline.
```
- `[I]` So the honest statement is "required for a SummedDelay feedback loop", not "common
  practice": 4% of presets use it, and the inference from the guide's "critical" plus the two
  placements observed is that either placement works as long as the scaler multiplies something
  entering the delay.

```
set_bank_type(bank="C", type_name="SummedDelay")
set_matrix_point(row=6, col=43, value="0.25")      # Bank A -> Bank C col 1 : the dry send
set_matrix_point(row=8, col=43, value="G")         # Bank C -> Bank C col 1 : the feedback
set_formula(row=8, col=43, component="W", mode="Constant", value=0.99, magnitude=1,
            modifier="x Macro", macro="iv")
set_matrix_point(row=16, col=43, value="V")        # Direct x -> Bank C col 1 : the PScaler
set_formula(row=16, col=43, component="W", mode="Constant", value=1.0, magnitude=1,
            modifier="x Polyphony scaler")
set_matrix_point(row=13, col=44, value="1")        # Bank C col 2 = delay time
```

### P11. Mouth and vowel control

- `[C]` The `Sh` mouth-shape column is driven in 36 of 36 BiqMouth slots across the corpus. Of the
  48 formulas that drive it, 9 are `W = Constant x macro` only, 6 are Y-only, 5 are
  `W = Constant x macro` with all of X, Y and Z, 4 are `W = SG1` plus `Y`, 4 are X-only, 3 are
  `W = Constant` plus `Y` and 3 are `W = SG2` alone.
- `[D]` `CLAUDE.md:119`, 2026-10-25, fw 10.81, "MIDI in: CC 1 (mod wheel) is read as Y (Continuum
  guide)." `[C]` So "vowel on the wheel" is the Y-only or `W + Y` construction, which 13 of the 48
  factory `Sh` formulas use.
- `[C]` A static vowel on a macro is the other half: `Electric Guitar`: `col 28 <- Direct + = G`
  with `Electric Guitar`/`G` = `[W + X + Y + Z] W = Constant 0.48 x 10 x Macro (i)`, and
  `BiqMouth - Basic`: `col 36 <- Direct + = E` with `BiqMouth - Basic`/`E` =
  `[W + X + Y + Z] W = Constant 0.48 x 10 x Macro (i)`.
- `[C]` `Choir and Ext` puts the wheel on a second row of the same column rather than inside the
  macro formula: `Choir and Ext`: `col 36 <- Direct + = B, Direct + (2) = P` with
  `Choir and Ext`/`P` = `[W + X + Y + Z] Y = Continuous None->1.0 x 0.1`.
- `[C]` **Never leave `sF` and `sB` blank.** `BiqMouth - Basic`: `col 37 <- Direct + = F` parks the
  formant columns with `BiqMouth - Basic`/`F` =
  `[W + X + Y + Z] W = Constant 0.2 x 10 x Macro (ii) ; Y = Continuous 0.5->0.5 x 1`, and the same
  shape sits on column 39. The equal non-zero `Y` heights are `modules/index.md` cross-module
  pattern 4.

```
set_bank_type(bank="B", type_name="BiqMouth")
set_matrix_point(row=13, col=36, value="E")        # Bank B col 2 = Sh, the mouth shape
set_formula(row=13, col=36, component="W", mode="Constant", value=0.48, magnitude=10,
            modifier="x Macro", macro="i")
set_matrix_point(row=14, col=36, value="P")        # Direct + (2) = the wheel, added on top
set_formula(row=14, col=36, component="Y", height_begin=0.0, height_end=1.0, multiplier=0.1)
set_matrix_point(row=13, col=37, value="F")        # sF - never blank
set_formula(row=13, col=37, component="W", mode="Constant", value=0.2, magnitude=10,
            modifier="x Macro", macro="ii")
set_formula(row=13, col=37, component="Y", height_begin=0.5, height_end=0.5)
set_matrix_point(row=13, col=39, value="H")        # sB - never blank either
```

### P12. Plucks - a single-cycle SG into an excitation column

- `[C]` A pluck is P1's envelope with a short shape, placed on the bank's column 1 and fed from the
  `Noise` row or an oscillator row. `Noise` -> `Bank A col 1` appears in 96 presets of 668 (14%)
  and `Noise` -> `Osc/Filter 5 input` in 89.
- `[C]` `Dueling BiqBanks`: `col 27 <- Noise = A` with `Dueling BiqBanks`/`A` =
  `[W + X + Y + Z] W = SG1 0.1 x 0.1 [shape Steep Down]` is the plain form.
- `[C]` `Resonant Drum 2`: `col 27 <- Noise = A, Direct x (multiply) = z^2` adds the amplitude
  scaler, with `Resonant Drum 2`/`A` =
  `[(W x X) + (Y x Z)] W = SG1 1.0 x 1 [shape Pulse] ; X = Continuous 0.42->None x 1 ; Y = Continuous 0.1->None x 0.01`.
- `[C]` `Underwater Ceramics`: `col 27 <- Noise = A` folds the pressure in through the operator
  instead: `Underwater Ceramics`/`A` =
  `[(W + X + Y) x Z] W = SG1 1.0 x 0.01 [shape Pulse] ; Z = Continuous None->1.0 x 10`, whose `Z`
  transfer is `Steep S`.
- `[C]` `Bell Rub`: `col 35 <- Noise = L, Bank A = 1` shows the same excitation fed by a second
  bank as well as the noise row.
- `[C]` The `F`-column constant `9` is the corpus's most common SG rate constant, 175 of the
  `SG n F` constant cells, with `1` (112), `0.1` (77), `5` (66) and `2` (57) next: a short pluck
  wants a high rate.
- `[D]` The whole pluck-and-resonator family carries a device-verified constraint:
  `CLAUDE.md:145-146`, 2026-10-25, fw 10.81, "Delay-based strings do not follow pitch bend on a
  ringing note; use a BiqBank modal string." `[C]` The corpus is consistent: of 177 BiqBank slots,
  173 drive the excitation column and 171 the frequency column, while the 97 delay-feedback presets
  are echoes and ambiences, not pitched strings.

```
set_shape_generator(sg=1, type_name="Single Cycle")
set_bank_type(bank="A", type_name="BiqBank")
set_matrix_point(row=13, col=52, value="W")        # SG 1 T
set_matrix_point(row=13, col=51, value="9")        # SG 1 F = fast
set_matrix_point(row=0, col=27, value="A")         # Noise -> Bank A col 1, the excitation
set_formula(row=0, col=27, component="W", mode="SG1", sg_shape="Pulse",
            value=1.0, magnitude=0.01, operator="(W + X + Y) x Z")
set_formula(row=0, col=27, component="Z", height_begin=0.0, height_end=1.0, multiplier=10)
set_matrix_point(row=13, col=28, value="X")        # Bank A col 2 = pitch
set_matrix_point(row=13, col=30, value="C")        # Bank A col 4 = bandwidth, never blank
```

### P13. Bowed sounds

- `[C]` Two distinct factory routes, and they do not mix. The Kinetic bow uses that module's own
  columns, driven in only 23 and 38 of 77 Kinetic slots, so only the bowed subset touches them.
- `[G]` Both columns must be fed or neither does anything.
  `docs/EaganMatrixUserGuide.txt:3882-3884`, verbatim, "Bow Speed (B) must be set from the matrix.
  It is the speed of the contact surface from which the static friction", and the same sentence
  ends "has no effect if Static Friction is zero".
- `[G]` The stiction column carries the same requirement, `docs/EaganMatrixUserGuide.txt:3874`,
  verbatim, "or stiction) must be set from the matrix." The guide prints its column label as a
  Greek mu, rendered `mu` here under the ASCII rule.
- `[C]` `Bowed BiqBank` is the full construction: a **Kinetic bank is the bow and a BiqBank is the
  string**. Bow speed is driven from three rows at once,
  `Bowed BiqBank`: `col 28 <- Direct + = E, Direct + (2) = 0.01, Direct x (multiply) = G`, with
  `Bowed BiqBank`/`E` =
  `[W + X + Y + Z] W = Constant 1.0 x 1 x Macro (i) ; Z = Continuous None->1.0 x 0.1` as the
  macro-plus-pressure bow pressure and `Bowed BiqBank`/`G` =
  `[W + X + Y + Z] W = SG1 0.18 x 0.1 [shape Sine]` as a slow scrape on top.
- `[C]` Stiction is fed from a plain constant on the next column,
  `Bowed BiqBank`: `col 29 <- Direct + = D`, which is what satisfies the guide's "no effect if
  Static Friction is zero".
- `[C]` The Kinetic model's position output then drives the BiqBank's excitation column, so the
  friction cycle is what excites the modal bank: `Bowed BiqBank`: `col 35 <- Bank A = H` with
  `Bowed BiqBank`/`H` = `[W + X + Y + Z] Z = Continuous None->0.5 x 0.01`, and the string's own
  pitch sits beside it at `Bowed BiqBank`: `col 36 <- Direct + = X`.
- `[C]` The second route is a sustained noise excitation into a resonator, which needs no Kinetic
  bank at all: `Model String Wind`: `col 12 <- Noise = A, Bank A = B, Direct + = 0.25, Direct - =
  D, Direct x (multiply) = 2` feeds an oscillator slot from the noise row and from the bank's own
  output, with `Model String Wind`/`A` =
  `[W + X + Y + Z] W = Constant 1.0 x 0.1 x Macro (i)` as a macro-controlled air level and
  `Model String Wind`/`D` = `[W + X + Y + Z] W = SG1 0.25 x 1 [shape Ramp Up]` subtracting an
  attack transient on the `Direct -` row.
- `[C]` 41 of 120 HarMan slots and 23 of 41 BiqGraph slots are built the second way, so sustained
  noise is the broader idiom and the Kinetic bow the specialised one.
- `[I]` **The Kinetic properties that make the bow behave are not MCP-writable.** Slipping Friction
  and Quit-slipping Speed live in the `s_Kinet_Poke` stream, which has no codec in this project, so
  the bow can be driven but not tuned; the inference is that a Kinetic bow recipe must start from a
  factory preset whose properties are already right. The read and write surface for those streams
  is `tools_spec.md` `T16`.

```
# route 1 - Kinetic bows a BiqBank. Both bow columns must be fed or neither does anything.
set_bank_type(bank="A", type_name="Kinetic")
set_bank_type(bank="B", type_name="BiqBank")
set_matrix_point(row=13, col=28, value="E")        # Bank A col 2 = B, bow speed
set_formula(row=13, col=28, component="W", mode="Constant", value=1.0, magnitude=1,
            modifier="x Macro", macro="i")
set_formula(row=13, col=28, component="Z", height_begin=0.0, height_end=1.0, multiplier=0.1)
set_matrix_point(row=14, col=28, value="0.01")     # Direct + (2) = a floor so the bow never stops
set_matrix_point(row=16, col=28, value="G")        # Direct x = a slow wobble on the bow
set_formula(row=16, col=28, component="W", mode="SG1", sg_shape="Sine",
            value=0.18, magnitude=0.1)
set_matrix_point(row=13, col=29, value="D")        # Bank A col 3 = mu, stiction - NEVER ZERO
set_formula(row=13, col=29, component="W", mode="Constant", value=0.13, magnitude=1)
set_matrix_point(row=6,  col=35, value="H")        # Bank A position -> Bank B col 1, the string
set_formula(row=6, col=35, component="Z", height_begin=0.0, height_end=0.5, multiplier=0.01)
set_matrix_point(row=13, col=36, value="X")        # Bank B col 2 = the string's pitch
```

```
# route 2 - sustained noise into a resonator, which needs no Kinetic properties at all
set_bank_type(bank="A", type_name="BiqBank")
set_matrix_point(row=0,  col=12, value="A")        # Noise -> Osc/Filter 1 input = the air
set_formula(row=0, col=12, component="W", mode="Constant", value=1.0, magnitude=0.1,
            modifier="x Macro", macro="i")
set_matrix_point(row=6,  col=12, value="B")        # Bank A -> the same input = the feedback
set_formula(row=6, col=12, component="W", mode="Constant", value=0.25, magnitude=1)
set_matrix_point(row=15, col=12, value="D")        # Direct - = subtract an attack transient
set_formula(row=15, col=12, component="W", mode="SG1", sg_shape="Ramp Up",
            value=0.25, magnitude=1)
set_matrix_point(row=1,  col=27, value="E")        # Osc 1 -> Bank A col 1, the excitation
set_matrix_point(row=13, col=28, value="X")        # Bank A col 2 = pitch
```

### P14. Drones - `W = Gated` or `W = Constant`

- `[C]` 380 formulas of 7,259 (5.2%) use `W = Gated`, which holds 1 for as long as the note is
  held. A drone is the pluck of P12 with `W = Gated` where the SG would be.
- `[C]` The minimal case runs straight onto both Master columns:
  `Soundboard 2`/`B` = `[W + X + Y + Z] W = Gated 1.0 x 1`.
- `[C]` `The Long Goodbye`/`F` =
  `[W x (X + Y + Z)] W = Gated 1.0 x 1 ; X = Continuous -1.0->1.0 x 1` is the same gate used as a
  multiplier, so the pitch only speaks while the note is held.
- `[C]` For a drone that ignores the note gate entirely, use a Constant: 5,030 formulas of 7,259
  (69.3%) are `W = Constant`, and that is also how a free-running LFO's depth is written.
- `[I]` A drone is the one family here that genuinely needs no envelope, which means it is also the
  one family unaffected by the absence of a writable release (section 2.4); the inference is that
  a drone's decay has to come from the Recirculator tail or from a delay, not from the voice.

```
set_bank_type(bank="A", type_name="BiqBank")
set_matrix_point(row=0,  col=27, value="A")        # Noise -> Bank A col 1, continuous
set_formula(row=0, col=27, component="W", mode="Gated", value=1.0, magnitude=1)
set_matrix_point(row=13, col=28, value="X")        # Bank A col 2 = pitch
set_matrix_point(row=13, col=30, value="0.65")     # Bank A col 4 = bandwidth, never blank
set_matrix_point(row=6,  col=0,  value="B")        # Bank A -> Master SL
set_matrix_point(row=6,  col=1,  value="B")
set_formula(row=6, col=0, component="W", mode="Gated", value=1.0, magnitude=1)
```

### P15. Percussion

- `[C]` The percussion family is P12 with three marks of its own: the `Pulse` shape, used by 143
  formulas of 7,259; the predefined `z^2` code in an amplitude column; and an `anc ^` exponent.
- `[C]` `Resonant Drum 2` has all three: `Resonant Drum 2`: `col 27 <- Noise = A, Direct x
  (multiply) = z^2` with `Resonant Drum 2`/`A` =
  `[(W x X) + (Y x Z)] W = SG1 1.0 x 1 [shape Pulse] ; X = Continuous 0.42->None x 1 ; Y = Continuous 0.1->None x 0.01`.
- `[C]` `Boson Particles Wbl` shows the amplitude idiom on its own, one predefined code driving
  both the level and a duty cycle: `Boson Particles Wbl`: `col 27 <- Direct + = z^2` and
  `Boson Particles Wbl`: `col 33 <- Direct + = z^2, Direct x (multiply) = 0.9`.
- `[C]` The exponent recurs across percussive presets: `Kinetic SatPad`/`B` =
  `[W + X + Y + Z] W = Constant 1.0 x 1 x Macro (i)` carries an ancillary `^ 2.0` that the summary
  line does not show, and so does `Kinetic SatPad`/`F` =
  `[W + X + Y + Z] W = Constant 0.2 x 10 x Macro (iv) ; Y = Continuous 1.0->1.0 x 0.1`.
- `[I]` **The exponent is not MCP-writable**, so a recipe can only approximate it by steepening the
  `Z` transfer to `Squared`; the inference is that the audible job of `anc ^ 2.0` - making soft
  strikes much quieter than hard ones - is reachable by transfer even though the operator is not.
  The ancillary write surface is `tools_spec.md` `T13`.
- `[I]` On a plain MIDI keyboard `z^2` and a `Z` transfer both freeze at note-on, so both become
  velocity curves; the inference is that a percussion patch built this way behaves correctly on a
  keyboard, which is not true of most of the chapter.

```
set_shape_generator(sg=1, type_name="Single Cycle")
set_bank_type(bank="A", type_name="BiqBank")
set_matrix_point(row=13, col=52, value="W")        # SG 1 T
set_matrix_point(row=13, col=51, value="9")        # SG 1 F = a very short pulse
set_matrix_point(row=0,  col=27, value="A")        # Noise -> Bank A col 1
set_formula(row=0, col=27, component="W", mode="SG1", sg_shape="Pulse",
            value=1.0, magnitude=1, operator="(W + X + Y) x Z")
set_formula(row=0, col=27, component="Z", mode="Initial",
            height_begin=0.0, height_end=1.0, transfer="Squared")
set_matrix_point(row=16, col=27, value="z^2")      # Direct x = pressure-squared amplitude
set_matrix_point(row=13, col=28, value="X")        # Bank A col 2 = pitch
set_matrix_point(row=13, col=30, value="0.14")     # Bank A col 4 = bandwidth, never blank
```

### P16. Waveguide and multi-tap delay networks

- `[C]` 36 MicroDelay slots in the corpus, and the construction is remarkably uniform: odd columns
  are the four audio inputs, even columns the four tap times, one letter sets the base delay and
  four `Direct x (multiply)` constants make the ratios.
- `[C]` `Soundboard 2` is the clean case. The inputs are
  `Soundboard 2`: `col 43 <- Osc 5 = D, Tap 4 = C`, with the same shape on columns 45, 47 and 49,
  and the times are `Soundboard 2`: `col 44 <- Direct + = A, Direct x (multiply) = 0.97` through
  `Soundboard 2`: `col 50 <- Direct + = A, Direct x (multiply) = 0.11`, the four ratios being
  0.97, 0.67, 0.41 and 0.11.
- `[C]` The one letter that sets the base delay tracks pitch **inversely**, which is what makes the
  network behave as a waveguide: `Soundboard 2`/`A` =
  `[W + X + Y + Z] W = Constant 0.12 x 0.1 ; X = Continuous 0.12->-0.12 x 1 ; Z = Continuous 0.55->0.5 x 1`,
  whose `X` transfer is `X Oct` - the falling height is the inversion.
- `[C]` The taps come back in on the delay's alternative output rows rather than through the bank
  row: in `Soundboard 2` those rows decode as `Tap 1`..`Tap 4`, while `MicroDelay WaveGuide v1`
  reaches them as `Audio In L`, `Audio In R`, `Sub L` and `Sub R`. Which name a row carries depends
  on the preset's delay selection - `modules/index.md` shared fact 8 owns that mapping.
- `[C]` `MicroDelay WaveGuide v1` is the same network with the feedback coefficients on W rather
  than on bare constants: `MicroDelay WaveGuide v1`/`D` =
  `[W x (X + Y + Z)] W = Constant 1.27 x 1 ; X = Continuous 0.13->-0.03 x 0.1`, a W above 1.0,
  which only W can reach.
- `[I]` The ratios are deliberately not simple fractions; the inference is that near-irrational
  tap ratios keep the taps from reinforcing into a pitched comb, which is the difference between a
  soundboard and a resonator.

```
set_bank_type(bank="C", type_name="MicroDelay")
set_matrix_point(row=13, col=44, value="A")        # Bank C col 2 = the base delay time
set_formula(row=13, col=44, component="W", mode="Constant", value=0.12, magnitude=0.1)
set_formula(row=13, col=44, component="X", height_begin=0.12, height_end=-0.12,
            multiplier=1, transfer="X Oct")        # inverse pitch tracking
for col, ratio in ((44, "0.97"), (46, "0.67"), (48, "0.41"), (50, "0.11")):
    set_matrix_point(row=13, col=col, value="A")   # one letter, four columns
    set_matrix_point(row=16, col=col, value=ratio) # Direct x = this tap's ratio
for col in (43, 45, 47, 49):
    set_matrix_point(row=5, col=col, value="D")    # Osc 5 -> each audio input
```

### P17. Reverb and ambience through the assignable Master columns

- `[C]` `Direct +` -> `Master col 1` appears in 149 presets of 668, `col 3` in 96, `col 2` in 96
  and `col 5` in 81; `Master/Dry mix` is driven in 30 presets and `Dry L` / `Dry R` in a handful.
- `[C]` The cheapest factory reverb is two constants and a mix, with no formula at all:
  `Resonant Drum 2`: `col 6 <- Direct + = 0.7, Direct x (multiply) = 3` and
  `Resonant Drum 2`: `col 7 <- Direct + = 0.3`.
- `[C]` Putting the amount on a macro costs one letter: `Underwater Ceramics`: `col 5 <- Direct + =
  H` with `Underwater Ceramics`/`H` = `[W + X + Y + Z] W = Constant 1.0 x 1 x Macro (iv)`, and
  `Underwater Ceramics`: `col 4 <- Direct + = I` on the column this preset assigns to `Recirc R3`.
- `[C]` Routing the bank around the master chain is the other half of an ambience:
  `Bird Echoer`: `col 8 <- Direct + = 0.5` sets the Master/Dry mix while
  `Bird Echoer`: `col 9 <- Bank A = 1` sends the bank straight to the dry output.
- `[C]` Short Reverb is the Recirculator type in 405 presets of 668, so it is the default-ish
  choice; which parameter each assignable column drives is read back by
  `eagan_mcp/setup.py:MASTER_COL_TARGETS`.
- `[I]` **No tool writes the assignment itself.** `idMastCol1..6` are `s_Mat_Poke` ids 27-32 `[G]`
  `docs/HakenMidi.h:1488-1500`, and the MCP decodes them for reading only, so a recipe can drive
  whatever the preset already assigns but cannot choose a different Recirculator parameter. The
  inference is that an ambience recipe must start from a preset whose column assignments suit it.
  `tools_spec.md` `T4` covers the read side, which already ships; the **write** side is `T21`,
  `set_master_column`.

```
# drive whatever this preset has already assigned to the first two Master columns
set_matrix_point(row=13, col=2, value="H")         # Master col 1
set_formula(row=13, col=2, component="W", mode="Constant", value=1.0, magnitude=1,
            modifier="x Macro", macro="iv")
set_matrix_point(row=13, col=3, value="0.3")       # Master col 2, a bare constant
set_matrix_point(row=13, col=8, value="0.5")       # Master/Dry mix
```

### P18. Gain compensation for resonator bandwidth - one preset, not an idiom

- `[C]` Of the **187** bank slots across the corpus whose bandwidth column is driven by a formula -
  BiqBank 97, ModMan 39, BiqGraph 34, BiqMouth 11, SineBank 6 - exactly **two cells, both in
  `Dueling BiqBanks`**, share a macro between the bandwidth column and that bank's output cell. No
  preset in the corpus shares a formula **letter** between a bandwidth column and an output column.
- `[C]` The two cells are `Dueling BiqBanks`/`C` =
  `[W + X + Y + Z] W = Constant -0.33 x 1 x Macro (i) ; Y = Continuous 0.64->0.64 x 1` on the bank
  A bandwidth column and `Dueling BiqBanks`/`D` =
  `[(W + X + Y) x Z] W = Constant -0.31 x 1 x Macro (i) ; Y = Continuous 1.0->None x 1 ; Z = Initial None->1.0 x 1`
  on the bank A output. Bank B is the mirror image on macro ii, letters `F` and `E`.
- `[C]` Macro i is labelled `RingBiqA_Short_Medium_Long`. As the macro rises the bandwidth falls,
  so the bank rings longer and louder, and the same macro subtracts up to 0.31 from the output
  level; the compensation coefficient -0.31 is deliberately close to the bandwidth coefficient
  -0.33.
- `[I]` **Verdict: this is one knob tying bandwidth and output level together on one named preset.
  It is not an idiom and must not be generalised.** The inference from 2 cells in 187 slots and
  zero shared letters is that the factory does not routinely compensate gain for bandwidth; a
  knowledge base that presented it as a technique would be inventing a convention out of a single
  example.

```
# reproduces Dueling BiqBanks' bank A only - not a general recipe
set_matrix_point(row=13, col=30, value="C")        # Bank A col 4 = bandwidth
set_formula(row=13, col=30, component="W", mode="Constant", value=-0.33, magnitude=1,
            modifier="x Macro", macro="i")
set_formula(row=13, col=30, component="Y", height_begin=0.64, height_end=0.64)
set_matrix_point(row=6, col=0, value="D")          # Bank A -> Master SL, the same macro
set_formula(row=6, col=0, component="W", mode="Constant", value=-0.31, magnitude=1,
            modifier="x Macro", macro="i", operator="(W + X + Y) x Z")
set_formula(row=6, col=0, component="Z", mode="Initial", height_begin=0.0, height_end=1.0)
```

### P19. Sample-and-hold randomisation

- `[C]` `idShapeW = 12`, `S+H row`, appears in 84 formulas of 7,259 and the per-letter variants in
  a further 44, so random stepping is a real if minority technique.
- `[C]` `Kinetic SatPad` is the "random cloud" template. Two S+H sources run off SG1 at different
  depths, `Kinetic SatPad`/`C` = `[W + X + Y + Z] W = SG1 0.18 x 0.1 [shape S+H row]` and
  `Kinetic SatPad`/`G` = `[W + X + Y + Z] W = SG1 1.0 x 0.01 [shape S+H row]`, both placed on
  shape-generator rate columns from the noise row:
  `Kinetic SatPad`: `col 51 <- Noise = G, Direct + = 9`.
- `[C]` Four further letters then each add or subtract one of those sources through an ancillary
  operation and land on a different oscillator's frequency multiplier:
  `Kinetic SatPad`/`H` = `[W + X + Y + Z] W = Constant 1.0 x 1` adds formula `C`, while
  `Kinetic SatPad`/`I` = `[W + X + Y + Z] W = Constant 0.3 x 10` and two more letters subtract
  formula `G`. The cells are `Kinetic SatPad`: `col 16 <- Direct + = X, Direct x (multiply) = H`
  and its siblings on columns 19, 22 and 25.
- `[I]` **The combining step is not MCP-writable.** The `anc +` and `anc -` operations that mix the
  S+H source into each multiplier are `idAncOp` and `idAncVal`, which no tool writes, so only the
  S+H source itself can be built from the MCP; the inference is that one shared S+H can be read by
  several columns directly, but the decorrelation that makes it a cloud cannot. The ancillary write
  surface is `tools_spec.md` `T13`.
- `[C]` Sample-and-hold needs a Continuous or Single Cycle SG and is unavailable on a Dual SG
  (`eagan_mcp/formula.py:SG_SHAPES`, sourced to `docs/HakenMidi.h:1179-1198`).

```
set_matrix_point(row=13, col=52, value="1")        # SG 1 T = 1 -> free-running
set_matrix_point(row=13, col=51, value="9")        # SG 1 F = how often it re-samples
set_matrix_point(row=16, col=16, value="H")        # Direct x -> Osc/Filter 2 F
set_formula(row=16, col=16, component="W", mode="SG1", sg_shape="S+H row",
            value=0.18, magnitude=0.1)
set_matrix_point(row=16, col=19, value="I")        # a second column, a second letter
set_formula(row=16, col=19, component="W", mode="SG1", sg_shape="S+H row",
            value=1.0, magnitude=0.01)
```

### P20. Voice-number spreading

- `[C]` `idScaleW = 4`, `x voice number`, appears in 15 formulas of 7,259 - the rarest construction
  in this chapter and the only one that makes a polyphonic patch sound different from a stack of
  identical monophonic ones.
- `[C]` `The Long Goodbye` puts it on the two Master columns, with the right channel inverted:
  `The Long Goodbye`/`A` = `[W + X + Y + Z] W = Constant 1.0 x 1 x Voice number` on `Master SL`
  and `The Long Goodbye`/`B` =
  `[W + X + Y + Z] W = Constant 1.0 x 1 x Voice number ; Z = Continuous -1.0->-1.0 x 1` on
  `Master SR`, reached by `The Long Goodbye`: `col 0 <- Osc 2 = z^2, Bank A = A`.
- `[C]` Both letters carry a `Triangle` shape and an ancillary `mod 2.0` over the W domain, which
  the summary line does not print.
- `[I]` That is per-voice stereo panning: voice number times a triangle, wrapped modulo 2, so
  successive voices land at alternating positions. The inference from the two mirrored letters is
  that the wrap, not the multiplication, is what keeps high voice numbers from running off the
  edge.
- `[I]` **The wrap is not MCP-writable.** `x Voice number` is reachable as a `set_formula`
  modifier, but the `anc mod 2.0` that bounds it is not, so an MCP-built version drifts
  monotonically with voice number instead of alternating; the inference is to keep the base
  polyphony low so the drift stays inside a usable range, or to accept a one-sided spread. The
  ancillary write surface is `tools_spec.md` `T13`.

```
set_matrix_point(row=6, col=0, value="A")          # Bank A -> Master SL
set_matrix_point(row=6, col=1, value="B")          # Bank A -> Master SR
set_formula(row=6, col=0, component="W", mode="Constant", value=1.0, magnitude=1,
            modifier="x Voice number", sg_shape="Triangle")
set_formula(row=6, col=1, component="W", mode="Constant", value=1.0, magnitude=1,
            modifier="x Voice number", sg_shape="Triangle")
set_formula(row=6, col=1, component="Z", height_begin=-1.0, height_end=-1.0)
```

---

## 4. Patterns the corpus does NOT support

`[I]` These are negative results, recorded so that nothing in the table gets invented later; the
inference in each row is that absence of corpus evidence is not evidence of a convention.

| asked-for pattern | corpus verdict |
|---|---|
| Gain compensation as a general idiom | `[C]` 1 preset of 668 (P18). The single documented example, never a technique. |
| Timing of any envelope or LFO | `[I]` Impossible: `eagan_mcp/server.py:102` zeroes every delta time when a capture is saved, and an SG rate is a column value whose kHz mapping the corpus cannot calibrate, so no measured period exists to infer from. |
| Additive `S` column position | `[I]` Unresolvable: 8 columns against 9 documented labels, and column 5's four-way mode select is never varied beyond one value in one preset, so no assignment can be inferred. |
| `pA` blank behaviour | `[C]` No factory preset of 668 selects pruned-additive mode at all, so the corpus says nothing about what its blank columns do. |
| WaveBank default waveform | `[I]` Square against sawtooth is pure absence-means-default and the corpus has no leverage either way; filed as a conflict, both sides standing. |
| Kinetic silence thresholds | `[I]` The property distributions show the ranges the factory uses for gravity, stiction and elasticity, but no preset sits on a boundary, so no threshold can be inferred. |

---

## 5. What no tool writes

Each rank is `tools_spec.md`'s, under the `T1..T22` scheme; a bare "rank n" is never used.

| rank | what it would unblock here |
|---|---|
| `T4` | Reading which Recirculator or convolution parameter each assignable Master column drives - the read side ships today in `eagan_mcp/setup.py:MASTER_COL_TARGETS`, the write side is `T21` (P17) `[I]` |
| `T5` | Persistence, interpolation and reluctance: the only route to a real release or sustain tail, decode-only today at `eagan_mcp/formula.py:121` (section 2.4, P14) `[C]` |
| `T6` | Formula-letter allocation over the pool of 44, which is a guess today (section 2.4) `[I]` |
| `T9` | Base polyphony above 8, needed by 24 factory presets of 668 (section 2.3) `[C]` |
| `T13` | The ancillary set: `idAncNN` for P3 idiom B, `anc ^` for P15, `anc +`/`anc -` for P19, `anc mod` for P20 - 19.2% of all 7,259 factory formulas use an ancillary operation `[C]` |
| `T15` | `idOscFilOpt`, the filter cascade option, the most common non-default oscillator-slot setting in the corpus (P9) `[C]` |
| `T16` | The bank-property streams, including the Kinetic friction settings a bow needs (P13) `[I]` |
