# FormulaDelay

Bank C, card 16 of 18. Four **control-rate** delay buffers per voice, read back from inside a
formula rather than from a matrix row. Its wire value is shared fact 9's; the one spelling of the
name is `index.md`'s. Everything cross-cutting - the one delay memory and its budget (shared
fact 7), the tap row alternates (shared fact 8), the matrix column budget (shared fact 1) and the
six cross-module wiring patterns - lives in `index.md` and is referenced here, never restated.

`[G]` `docs/EaganMatrixUserGuide.txt:4279-4282`, verbatim: "The FormulaDelay provides four delay
buffers for each voice, for delaying control data used in Matrix formulas. Typical values to feed
through a FormulaDelay might be X, Y, Z, or a pedal. The FormulaDelay is available in Bank C. No
output from FormulaDelay appears directly on matrix rows; instead, the delay buffer outputs are
available by selecting Buffer 1..4 in the W component of formulas."

`[C]` 9 of 668 factory presets run a FormulaDelay
(`census.json:modules_used_including_defaults`), the rarest of the four delays; all 9 set
`idBankC` explicitly (`census.json:bank_C`). `[C]` 8 of 668 presets carry a formula that actually
reads a buffer back (`census.json:techniques`, `formula_delay_buffer`) - the corrected count
`index.md` records.

Guide section 6.17, `docs/EaganMatrixUserGuide.txt:4231-4292`.

---

## 1. Columns

Eight Bank C columns, matrix columns 43-50 (shared fact 1), as **four buffer inputs, three delay
times and one Hold**. The input columns' heading is an up-pointing triangle in the Editor; written
`In` here under the ASCII rule.

| Bank C col | Matrix col | Label | What it does |
|---|---|---|---|
| 1 | 43 | `In1` | `[G]` `docs/EaganMatrixUserGuide.txt:4236-4238`, verbatim: "Input to FormulaDelay's first delay buffer. This buffer's output is available by selecting Buffer 1 in the W component of a formula." |
| 2 | 44 | `D1` | `[G]` `docs/EaganMatrixUserGuide.txt:4240-4242`, verbatim: "Delay time for FormulaDelay's delay buffer 1. 0 = no delay, 1 = max delay (selected in the Delay menu)." |
| 3 | 45 | `In2` | `[G]` `docs/EaganMatrixUserGuide.txt:4244-4246`, verbatim: "Input to FormulaDelay's first delay buffer. This buffer's output is available by selecting Buffer 2 in the W component of a formula." (the guide prints "first" where it means the second buffer - see trap 5) |
| 4 | 46 | `D2` | `[G]` `docs/EaganMatrixUserGuide.txt:4248-4250`, verbatim: "Delay time for FormulaDelay's delay buffer 2. 0 = no delay, 1 = max delay (selected in the Delay menu)." |
| 5 | 47 | `In3` | `[G]` `docs/EaganMatrixUserGuide.txt:4252-4254`, verbatim: "Input to FormulaDelay's third delay buffer. This buffer's output is available by selecting Buffer 3 in the W component of a formula." |
| 6 | 48 | `D3` | `[G]` `docs/EaganMatrixUserGuide.txt:4256-4258`, verbatim (the guide's column spacing collapsed): "Delay time for FormulaDelay's delay buffers 3 & 4. 0 = no delay, 1 = max delay (selected in the Delay menu)." **One control for two buffers**; there is no `D4`. |
| 7 | 49 | `In4` | `[G]` `docs/EaganMatrixUserGuide.txt:4260-4262`, verbatim: "Input to FormulaDelay's third delay buffer. This buffer's output is available by selecting Buffer 4 in the W component of a formula." (again "third" where it means the fourth - see trap 5) |
| 8 | 50 | `H` | `[G]` `docs/EaganMatrixUserGuide.txt:4264-4266`, verbatim: "H <= 0 is normal operation. H > 0 stops recording new data into buffers. Transition from H >= 0 to H < 0 clears all four buffers." (the guide prints the comparisons as single glyphs; rendered here under the ASCII rule) |

`[C]` Column occupancy over the 7 decoded FormulaDelay slots: c1 100%, c2 100%, c3 71%, c4 42%,
c5 14%, c6 14%, c7 0%, c8 28% (`corpus-module-wiring.md` S17). Buffers 3 and 4 are barely used;
the Hold column, unused on every other delay, is used here.

## 2. Units, useful ranges and blank-column behaviour

| Column | Units | Useful range | Blank (= 0) |
|---|---|---|---|
| `D1`-`D3` | `[G]` `docs/EaganMatrixUserGuide.txt:4240-4242`: **normalised 0..1 against the Delay menu maximum**, not milliseconds | 0..1 | **0 = no delay**, so the buffer passes its input straight through. Benign. |
| `In1`-`In4` | control-rate values, nominally 0..1 | `[G]` `docs/EaganMatrixUserGuide.txt:4280`, verbatim: "Typical values to feed through a FormulaDelay might be X, Y, Z, or a pedal." | `[I]` no input means the buffer records zero; the inference is that a `W = Buffer n` formula then reads a constant zero, which is silent failure rather than an error. |
| `H` | a trigger with **two** thresholds `[G]` `docs/EaganMatrixUserGuide.txt:4264-4266` | `<= 0` normal, `> 0` freeze, a downward crossing clears | **0 is normal operation** - but see the conflict below, which is why this is the one FormulaDelay field the completeness matrix marks `P` rather than `Y`. |

**Blank-column verdict: blank-safe except for `H`.** `[I]` Seven of the eight columns have a
documented, benign zero; the inference for `H` is that its printed condition makes "normal
operation" and "clear the buffers" overlap, so a formula that merely dips negative may wipe the
buffers. That is checklist gap #7, `owner: device` - the 16th test in
`modules-devicetests.md`, "FormulaDelay Hold clear condition - does a slightly negative H wipe the
buffers?", which the merged scheme labels `DT16` `[I]`; the inference is that the merged list
keeps the source order, and `tools_spec.md` is where that is reconciled
(`modules-unfilled-checklist.md` S2).

```
CONFLICT: FormulaDelay's H clear condition - the literal reading vs the likely intent
  docs   [G]: "H <= 0 is normal operation. H > 0 stops recording new data into buffers.
              Transition from H >= 0 to H < 0 clears all four buffers."
              - docs/EaganMatrixUserGuide.txt:4264-4266
  corpus [C]: The Long Goodbye drives H with letter D = "W = SG4 -1.0 [shape Pulse]" - a
              deliberately NEGATIVE pulse, which only makes sense if a downward zero-crossing
              is the clear (1 of the 49 presets with a shipped wiring block)
  follows: neither, pending the device test. The literal reading (normal operation and the clear
           trigger overlap, so any dip below zero wipes) and the intended reading (a downward
           zero-crossing is the clear) both stand. Do not write a bipolar formula into H until
           DT16 settles it.
```

`[I]` **A delay value alone never tells you the delay time** - it is a fraction of the maximum
`idTimeSel` selects (shared fact 7); the inference is the same arithmetic as on the other three
delay cards.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | MCP today |
|---|---|---|
| Bank C type | `idBankC = 93`, value per shared fact 9 | **write + read**: `set_bank_type("C", "FormulaDelay")`, `get_setup()["banks"]["C"]` `[I]` - the inference is from the tool surface, which accepts the `setup.py:BANK_C_TYPES` string |
| All eight columns | matrix cells 43-50 | **write + read**: `set_matrix_point` / `get_matrix` `[I]`, same inference |
| **`W = FormulaDelay`, the read-back side** | formula stream 19, W mode id 40 **value 12** | **write + read**: `get_formula` decodes it and `set_formula` writes it `[D]` `CLAUDE.md:82`, 2026-10-25, fw 10.81 ("40 mode (0 Const, 1 Gated, 2-6 SG1-5, 7-11 SG1b-5b, 12 FormulaDelay; RMS unverified)"). `eagan_mcp/formula.py:11` carries the table |
| **Which buffer that W reads** | formula stream 19, **id 50** | **write + read**, but under a name that hides it: id 50 is the SG waveform shape for every other W mode and the **buffer select** when the mode is FormulaDelay `[D]` `CLAUDE.md:112`, 2026-10-25, fw 10.81 ("Same id 50 = buffer select when W mode is FormulaDelay"), recorded at `eagan_mcp/formula.py:55`. `[I]` The inference for a caller: `get_formula` on a FormulaDelay W reports a shape name where the buffer number belongs, so read the raw id-50 value, not the label |
| Maximum delay time | `idTimeSel = 105` `[G]` `docs/HakenMidi.h:1632`, header comment "select time delay 50 ms * 2^n" | **raw read only** (`get_setup()["delay_time_select_raw"]`); no name table and no write. Rank `T22` `[I]` - the inference is that the validated `s_Mat_Poke` write rank carries the delay setup ids; `T4` is the labelling rank and is read-only |
| Anti-aliasing (Nyquist) filter | `idAliasDelay = 108` `[G]` `docs/HakenMidi.h:1599` | **neither read nor written**. Rank `T22` `[I]`, same inference. `[I]` It is also the wrong lever here: the inference is that a control-rate buffer aliases control signals, which the guide says to fix by filtering the input (section 4), not by the delay's own Nyquist filter |
| Tap rows | `idRowTyp1 = 106` / `idRowTyp2 = 107`, shared fact 8 | irrelevant to this module `[G]` `docs/EaganMatrixUserGuide.txt:4281-4282`: FormulaDelay has no matrix-row output at all |

## 4. DSP cost class

**Cheap in DSP, expensive in the shared delay memory, and the only delay whose sample rate starts
below audio.** The shared budget is shared fact 7's and is not restated; what is specific to
FormulaDelay is its base rate:

`[G]` `docs/EaganMatrixUserGuide.txt:4284-4288`, verbatim: "The sample rate of FormulaDelay's
delay memory is normally at the formula evaluation rate (1 kHz), but it can be limited by two
variables: maximum delay and polyphony. Very long delays or high polyphony may result in reduced
sample rate for the delay memory. Consider filtering or slewing the data inputs to FormulaDelay
when using long delay times in the Delay popup menu, to avoid aliasing the control signals being
delayed through FormulaDelay."

`[I]` The practical rule: 1 kHz is already low enough that a fast control signal through a long
delay aliases, and the fix is upstream. The inference is that this is the one delay where the
remedy is a slew on the *input formula* rather than a setting on the delay.

`[I]` **Not measured on this device.** The checklist marks FormulaDelay's DSP cost `Y` from the
passage above; the inference is that "1 kHz, limited by delay times polyphony" is a documented
property and a DSP percentage is a separate, unmeasured number.

## 5. Typical wiring

Both examples ship decoded in `factory_catalog.json`; cell orientation is
`column <- row = value`, which is `set_matrix_point(row, col, value)` read from the column side.

**`The Long Goodbye`** (modern, fw 10.39) - two control-rate buffers plus the buffer wipe. `[C]`
from the shipped `wiring` block (one of the 49 presets in `preset_file.WIRING_PRESETS`):

```
Bank C 1 (43) In1 <- Direct + = F, Direct + (2) = J     (buffer 1 records, and J reads back)
Bank C 2 (44) D1  <- Direct + = M
Bank C 3 (45) In2 <- Direct + = G, Direct + (2) = K     (buffer 2 records, K reads back)
Bank C 4 (46) D2  <- Direct + = M                       (the SAME letter: one time, two buffers)
Bank C 8 (50) H   <- Direct + = D
Osc/Filter 3 F (19) <- Direct + = H, Direct x = O       (the delayed pitch drives a third oscillator)
  F = [W x (X+Y+Z)] W = Gated 1.0 ; X = Continuous -1.0->1.0 kHz   (buffer 1 records pitch)
  G = [W x (X+Y+Z)] W = Gated 1.0 ; Z = Continuous None->0.5       (buffer 2 records pressure)
  H = [W+X+Y+Z] W = FormulaDelay 1.0        J = [W+X+Y+Z] W = FormulaDelay 1.0   (the read-backs)
  D = [W+X+Y+Z] W = SG4 -1.0 x 1 [shape Pulse]          (a NEGATIVE pulse into H: the buffer wipe)
  M = (blend-controlled, secondary W = 1.0)             (delay_time_select_raw = 3)
```

`[C]` This is the only preset in the corpus that uses a negative `H` as a deliberate buffer clear,
and the only one in the 49 that reads a FormulaDelay buffer back from two separate letters. Note
`D1` and `D2` both carry `M`, which is how two buffers share one delay time without `D3`'s
built-in pairing.

**`Drum-Machine`** (modern, fw 10.40) - three buffer inputs, no read-back in the matrix. `[C]`
from the shipped `wiring` block:

```
Bank C 1 (43) In1 <- Direct + = E         (E = W SG2 0.52 [Ramp Down])
Bank C 2 (44) D1  <- Direct + = Q
Bank C 3 (45) In2 <- Direct + = O
SG 2 T (54) <- Direct + = A ; SG 3 T (56) <- Direct + = B ; SG 4 T (58) <- Direct + = D
  (delay_time_select_raw = 1 - the shortest setting of the four presets cited across these cards)
```

`[C]` A shape-generator chain feeding the buffers, with the read-back happening inside formulas
rather than on a matrix row - the normal FormulaDelay shape, and why its wiring looks sparse even
in a dense preset.

`[C]` **The guide's other two leads check out, against a research finding that said otherwise.**
The guide names three examples `[G]` `docs/EaganMatrixUserGuide.txt:4291-4292`, verbatim:
"Examples of FormulaDelay usage in EaganMatrix System Presets: Synth Lead 4, The Long Goodbye,
Seasons Ch1". All three are in the 668-preset corpus and all three carry
`banks["C"] == "FormulaDelay"` in `factory_catalog.json`. `corpus-module-wiring.md` S17b states
that `Synth Lead 4` and `Seasons Ch1` do not; re-measured against the shipped catalog, that is
wrong and is not propagated here. Neither has a shipped `wiring` block, so neither can be a
worked example above - only `The Long Goodbye` and `Drum-Machine` are in the 49.

## 6. Known traps

1. **FormulaDelay has no matrix-row output.** `[G]` `docs/EaganMatrixUserGuide.txt:4281-4282`,
   verbatim: "No output from FormulaDelay appears directly on matrix rows; instead, the delay
   buffer outputs are available by selecting Buffer 1..4 in the W component of formulas." A patch
   that wires `Bank C` as a row and expects the delayed signal gets nothing.
2. **`W` mode 12 and formula id 50 together are the read-back**, and id 50 is named for something
   else. `[D]` `CLAUDE.md:112`, 2026-10-25, fw 10.81. `[I]` The inference for an agent: setting
   `W = FormulaDelay` without also setting id 50 leaves the buffer selection at whatever the
   shape-generator shape happened to be.
3. **`D3` controls buffers 3 and 4 together**; there is no `D4` `[G]`
   `docs/EaganMatrixUserGuide.txt:4256-4258`.
4. **`H`'s clear condition is ambiguous as printed** - see the CONFLICT block in section 2
   `[G]` `docs/EaganMatrixUserGuide.txt:4264-4266`.
5. **The guide's buffer 2 and buffer 4 input rows say "first" and "third".** `[G]`
   `docs/EaganMatrixUserGuide.txt:4244` and `:4260` both misname the buffer in the description
   while the "selecting Buffer n" clause in the same sentence is correct. `[I]` The inference is a
   copy-paste error in the guide's table, not four buffers wired to two inputs, because the
   read-back clause and the delay-time rows both count to four.
6. **1 kHz control rate aliases on long delays**; filter or slew the input `[G]`
   `docs/EaganMatrixUserGuide.txt:4284-4288`.
7. **A delay value is a fraction, not a time** - see section 2 `[G]`
   `docs/EaganMatrixUserGuide.txt:4240-4242` plus `docs/HakenMidi.h:1632`.
8. **A Manipulator in Bank A or B halves this delay's memory** `[G]`
   `docs/EaganMatrixUserGuide.txt:3491`, verbatim: "SummedDelay, MicroDelay, and FormulaDelay in
   Bank C (which will operate using half its normal memory)."
9. **The pitch-bend trap does not apply here, and that is worth saying.** `pitfalls.md` section 6
   is about *audio* delay lines used as strings; a FormulaDelay carries control data, so it is not
   the module that makes an unbendable string `[I]` - the inference is from the module's own
   definition at `docs/EaganMatrixUserGuide.txt:4279-4280`, which names control data as its
   content. Reaching for a FormulaDelay to fix a bend problem is the wrong move; the fix is a
   BiqBank modal string.
