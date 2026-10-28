# MicroDelay

Bank C, card 15 of 18. **Four single-tap audio delay buffers per voice** - the waveguide and
feedback-delay-network module. Its wire value is shared fact 9's; the one spelling of the name is
`index.md`'s. Everything cross-cutting - the one delay memory and its budget (shared fact 7), the
tap row alternates (shared fact 8), the matrix column budget (shared fact 1) and the six
cross-module wiring patterns - lives in `index.md` and is referenced here, never restated.

`[G]` `docs/EaganMatrixUserGuide.txt:4214-4217`, verbatim: "The MicroDelay provides four
single-tap audio delay buffers for each voice. The MicroDelay is available in Bank C. The outputs
of MicroDelay's four delay buffers are available on the Tap 1..Tap4 matrix rows (alternative
choices for the Sub and AesIn matrix rows). The sum of all four delay buffers outputs (Tap 1 +
Tap 2 + Tap 3 + Tap 4) is available on the Bank C matrix row."

`[C]` 37 of 668 factory presets run a MicroDelay
(`census.json:modules_used_including_defaults`); all 37 set `idBankC` explicitly
(`census.json:bank_C`).

Guide section 6.16, `docs/EaganMatrixUserGuide.txt:4181-4226`.

---

## 1. Columns

Eight Bank C columns, matrix columns 43-50 (shared fact 1), as **four input/tap pairs**. The input
columns' heading is an up-pointing triangle in the Editor; written `In` here under the ASCII rule.

`[C]` **The layout is interleaved, `In1 T1 In2 T2 In3 T3 In4 T4`**, not grouped. The guide's table
prints one input row, one tap row, then "Audio Inputs 2-4" and "Taps 2-4" as two further rows
without giving positions, which reads as `In1, T1, In2-In4, T2-T4`. The corpus settles it: column
occupancy pairs up as c1/c2 97%, c3/c4 94%, c5/c6 66%, c7/c8 61% over the 36 decoded MicroDelay
slots, odd columns are fed from audio-rate rows and even columns from `Direct` rows, and
`Soundboard 2` reads as a textbook four-tap waveguide under the interleaved map and as nonsense
under the grouped one (`corpus-module-wiring.md` S16, `corpus-blank-columns.md` S3.16). This
closes checklist gap #13 (`modules-unfilled-checklist.md` S2, owner `corpus`).

| Bank C col | Matrix col | Label | What it does |
|---|---|---|---|
| 1 | 43 | `In1` | `[G]` `docs/EaganMatrixUserGuide.txt:4186-4188`, verbatim: "Audio input into MicroDelay's first single-tap delay buffer. If the MicroDelay is operating at reduced sample rate, the audio inputs pass through an optional anti-aliasing filter." |
| 2 | 44 | `T1` | `[G]` `docs/EaganMatrixUserGuide.txt:4190-4195`, verbatim: "Delay time for MicroDelay's first delay buffer. 0 = no delay, 1 = delay by max value (selected in the Delay menu). The Tap 1 output is available as an alternative on the Sub matrix rows. The sum of Taps 1..4 are available on the Bank C matrix row." |
| 3, 5, 7 | 45, 47, 49 | `In2`-`In4` | `[G]` `docs/EaganMatrixUserGuide.txt:4197`, verbatim: "Three additional audio inputs like Audio Input 1." Their positions are `[C]` (see the interleaving note above), not the guide's. |
| 4, 6, 8 | 46, 48, 50 | `T2`-`T4` | `[G]` `docs/EaganMatrixUserGuide.txt:4199-4201`, verbatim: "One delay time for each audio input 2 through 4. 0 = no delay, 1 = delay by max value. The Tap 2..4 outputs are available as an alternative on the Sub and AesIn matrix rows." Positions `[C]` as above. |

`[I]` **Unlike the VoiceDelay and SummedDelay, there is no `H` (Hold) column and no `D` master
delay time.** The inference is structural: four independent buffers each need their own time, and
eight columns leave no room for a shared one - so a MicroDelay patch that wants all four taps to
move together must put one letter in all four tap columns and scale it, which is exactly what the
corpus does (see section 5).

## 2. Units, useful ranges and blank-column behaviour

| Column | Units | Useful range | Blank (= 0) |
|---|---|---|---|
| `T1`-`T4` | `[G]` `docs/EaganMatrixUserGuide.txt:4190-4191`: **normalised 0..1 against the Delay menu maximum**. Not a multiplier on anything - unlike the VoiceDelay's taps, each is an absolute fraction of the maximum | 0..1; `[C]` the corpus runs them very short, as waveguide lengths (`Soundboard 2`: one base value times 0.97 / 0.67 / 0.41 / 0.11) | **0 = no delay**, so that buffer is a bypass. Benign. |
| `In1`-`In4` | audio | - | `[I]` no input means that buffer records silence; the inference is that a buffer with a tap time and no input contributes nothing, which is why occupancy pairs up so cleanly. |

**Blank-column verdict: MicroDelay is blank-safe.** `[I]` Every column's zero is a documented,
musically sensible state and there is no Hold to leave in a bad state; the inference is that the
hazards are the shared memory budget and the tap-row routing, not empty cells. This is the field
the completeness matrix marks `Y` for MicroDelay (`modules-unfilled-checklist.md` S1).

`[I]` **A tap value alone never tells you the delay time** - it is a fraction of the maximum
`idTimeSel` selects (shared fact 7). For a waveguide this matters more than for an echo, because
the delay length *is* the pitch: the inference is that the same matrix value transposes the whole
instrument when the Delay menu changes.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | MCP today |
|---|---|---|
| Bank C type | `idBankC = 93`, value per shared fact 9 | **write + read**: `set_bank_type("C", "MicroDelay")`, `get_setup()["banks"]["C"]` `[I]` - the inference is from the tool surface, which accepts the `setup.py:BANK_C_TYPES` string |
| All eight columns | matrix cells 43-50 | **write + read**: `set_matrix_point` / `get_matrix` `[I]`, same inference |
| Maximum delay time | `idTimeSel = 105` `[G]` `docs/HakenMidi.h:1632`, header comment "select time delay 50 ms * 2^n" | **raw read only** (`get_setup()["delay_time_select_raw"]`); no name table and no write. Rank `T22` `[I]` - the inference is that the validated `s_Mat_Poke` write rank carries the delay setup ids; `T4` is the labelling rank and is read-only |
| Anti-aliasing (Nyquist) filter | `idAliasDelay = 108` `[G]` `docs/HakenMidi.h:1599`, header comment "true to disable nyquist filtering on delay" | **neither read nor written**. Rank `T22` `[I]`, same inference |
| **Tap rows 9-12** | `idRowTyp1 = 106` / `idRowTyp2 = 107`, shared fact 8 | **read, decoded, and now used for labelling**: `get_setup()["row_types"]` names them, and `get_matrix` / `set_matrix_point` label rows 9-12 as `Tap 1`..`Tap 4` instead of `Audio In L/R` and `Sub L/R` `[D-cap]` `tests/fixtures/microdelay_wg_v1_20261025_192903.mid`. No write tool: labelling is `T4`, which ships, and writing the selectors is `T22` `[I]` |
| MicroDelay tap inside a filter slot's `T` column | the slot's own `T` column, not a Bank C column | **write + read** as an ordinary matrix cell `[I]`; the inference is that the tap arrives through the slot, so no Bank C wiring reaches it |

**Rows 9-12 are taps, not audio inputs, for a tapped MicroDelay preset.** This is the correctness
fix the matrix tools now carry: the capture
`tests/fixtures/microdelay_wg_v1_20261025_192903.mid` sets `idRowTyp1 = 1` and `idRowTyp2 = 1`, so
its rows 9-12 are the four taps, and a static row table calls them `Audio In L/R` and `Sub L/R`
`[D-cap]` `tests/fixtures/microdelay_wg_v1_20261025_192903.mid`. `[C]` The static table is wrong
for 3 of the 18 captured presets. An agent quoting the old names routes a delay tap as an audio
input.

## 4. DSP cost class

**Memory-bound, and the most expensive of the four delays per voice**, because four buffers are
allocated per voice rather than one. The shared budget is shared fact 7's and is not restated;
what is specific to MicroDelay is that both variables apply:

`[G]` `docs/EaganMatrixUserGuide.txt:4219-4222`, verbatim: "The sample rate of the delay memory is
limited by two variables: maximum delay and polyphony. The Anti-Aliasing Low Pass Filter indicator
above the first Bank C column will light up when the delay memory is at reduced sample rate. If
you do not want an Anti-Aliasing filter at reduced sample rates, click on the indicator to disable
the filter."

`[G]` `docs/EaganMatrixUserGuide.txt:4214`, verbatim: "The MicroDelay provides four single-tap
audio delay buffers for each voice."

`[I]` The practical rule: a MicroDelay waveguide wants short delays, which is also what keeps it
out of trouble - the inference is that the module's natural setting (`idTimeSel` low, so a few
tens of milliseconds) is the one that avoids the reduced-sample-rate regime, unlike an echo
built on a VoiceDelay.

`[I]` **Not measured on this device.** The checklist marks MicroDelay's DSP cost `Y` from the two
guide passages above; the inference is that "four buffers per voice, limited by delay times
polyphony" is a documented property and a DSP percentage is a separate, unmeasured number.

## 5. Typical wiring

Both examples ship decoded in `factory_catalog.json`; cell orientation is
`column <- row = value`, which is `set_matrix_point(row, col, value)` read from the column side.

**`Soundboard 2`** (modern, fw 10.39) - a four-tap waveguide network, and the clearest reading of
the interleaved layout. `[C]` from the shipped `wiring` block (one of the 49 presets in
`preset_file.WIRING_PRESETS`):

```
Bank C 1 (43) In1 <- Osc 5 = D, Tap 4 = C      Bank C 2 (44) T1 <- Direct + = A, Direct x = 0.97
Bank C 3 (45) In2 <- Osc 5 = D, Tap 1 = C      Bank C 4 (46) T2 <- Direct + = A, Direct x = 0.67
Bank C 5 (47) In3 <- Osc 5 = D, Tap 2 = C      Bank C 6 (48) T3 <- Direct + = A, Direct x = 0.41
Bank C 7 (49) In4 <- Osc 5 = D, Tap 3 = C      Bank C 8 (50) T4 <- Direct + = A, Direct x = 0.11
Osc/Filter 5 input (24) <- Noise = 0.5
Master SL (0) <- Tap 1 = B, Tap 3 = B, Direct x = 0.7
Master SR (1) <- Tap 2 = B, Tap 4 = B, Direct x = 0.7
  A = [W+X+Y+Z] W = Constant 0.12 x 0.1 ; X = Continuous 0.12->-0.12 ; Z = Continuous 0.55->0.5
  C = [W+X+Y+Z] W = Constant 0.99 ; X = Continuous -0.02->None x 0.01 ; Z = Continuous 0.83->None x 0.01
  D = [W+X+Y+Z] Z = Continuous None->0.5 x 0.01            (excitation level from pressure)
  B = [W+X+Y+Z] W = Gated 1.0                              (output gate)
```

`[C]` **One letter, four ratios.** `A` is the base delay length; the four `Direct x (multiply)` constants
0.97 / 0.67 / 0.41 / 0.11 make the four lengths relatively prime, which is the waveguide. Each
tap feeds the **next** buffer's input through the feedback letter `C` (`Tap 4 -> In1`,
`Tap 1 -> In2`, `Tap 2 -> In3`, `Tap 3 -> In4`), so the four buffers are coupled in a ring - the
guide's "coupled sequentially" `[G]` `docs/EaganMatrixUserGuide.txt:4226`, verbatim: "SoundBoard:
Uses four audio delay buffers with relatively prime delay lengths, coupled sequentially."
`[C]` The guide's `SoundBoard` is the corpus's `Soundboard` (capitalisation only); the corpus also
carries `Soundboard 2` and `Kinetic Soundboard`, and `Soundboard 2` is the one of the three with a
shipped `wiring` block, which is why it is the example here.

`[C]` `A`'s `X` falls from +0.12 to -0.12 - **inverse** pitch tracking, so a higher note gives a
shorter delay and the waveguide follows the keyboard. Rows 9-12 read as `Tap 1`..`Tap 4` here,
which is shared fact 8 in use.

**`MicroDelay WaveGuide v1`** (legacy, fw 9.55) - the guide's tutorial waveguide, 49 matrix cells
and the preset the project's Sitar work was built on. `[C]` from the shipped `wiring` block:

```
Bank C 1 (43) In1 <- Osc 5 = 1, Audio In R = 1   Bank C 2 (44) T1 <- Direct + = B, Direct + (2) = D, Direct x = J
Bank C 3 (45) In2 <- Osc 2 = N, Osc 4 = O        Bank C 4 (46) T2 <- Direct + = B, Direct + (2) = D, Direct x = K
Bank C 5 (47) In3 <- Osc 5 = 1, Sub R = 1        Bank C 6 (48) T3 <- Direct + = P, Direct + (2) = D, Direct x = L
Bank C 7 (49) In4 <- Osc 2 = O, Osc 4 = N        Bank C 8 (50) T4 <- Direct + = P, Direct + (2) = D, Direct x = M
Master SL (0) / SR (1) <- Audio In L = I, Audio In R = I, Sub L = I, Sub R = I
  B = [W x (X+Y+Z)] W = Constant 0.8 ; X = Continuous -1.0->1.0      (pitch-tracked length, taps 1/2)
  P = [W x (X+Y+Z)] W = Constant 0.8 ; X = Continuous -1.0->1.0      (the same, taps 3/4)
  D = [W x (X+Y+Z)] W = Constant 1.27 ; X = Continuous 0.13->-0.03 x 0.1   (a common offset)
  J/K = Macro iii, +1 and -1      L/M = Macro iv, +1 and -1          (two detune knobs)
```

`[C]` **This preset's rows 9-12 read as `Audio In L/R` and `Sub L/R` in the catalog, and as
`Tap 1`..`Tap 4` on the device.** The shipped file is a legacy export that carries no row-type
selector at all, so the decoder reports the device default `rt1Aud`/`rt2Sub`; the device's own
copy of the same preset sets both to their tap values `[D-cap]`
`tests/fixtures/microdelay_wg_v1_20261025_192903.mid`. Read the four cells above as taps - the
`Direct x` detune pairs make no sense otherwise.

## 6. Known traps

1. **A MicroDelay waveguide does not follow pitch bend on a ringing note.** `[D]` `RECIPES.md:26 (moved to pitfalls.md section 6, item 49)`,
   2026-10-25, fw 10.81: confirmed on the factory `MicroDelay WaveGuide v1` itself. The
   construction, the BiqBank modal-string alternative and the open question about whether the
   delay time is latched at note-on are `pitfalls.md` section 6's; this card points there rather
   than repeating the recipe. `[C]` The corpus is consistent: every MicroDelay waveguide in it
   pitch-tracks its delay time at note-on and none is a bendable-string preset
   (`corpus-module-wiring.md` S16b).
2. **Only four MicroDelay taps exist in the whole voice**, and the filter slots compete for them.
   `[G]` `docs/EaganMatrixUserGuide.txt:1734-1737`, verbatim: "A MicroDelay tap, used in Feedback
   Delay Networks. The first MicroDelay tap is available in the first Multi-Mode filter, the
   second tap in the second filter, etc. up to the fourth filter (as only 4 MicroDelay taps are
   available)."
3. **The column layout is interleaved, and the guide's table does not say so.** Reading it as
   `In1, T1, In2-In4, T2-T4` puts every tap time in an input column. `[C]` as in section 1.
4. **Rows 9-12 are taps.** A static row table is wrong for `3 of 18` captured presets, this
   module's among them `[D-cap]` `tests/fixtures/microdelay_wg_v1_20261025_192903.mid`. Shared
   fact 8 owns the id table; the trap here is that the *file* may not say so even when the device
   does - see the `MicroDelay WaveGuide v1` note in section 5.
5. **A tap value is a fraction, not a time** - see section 2 `[G]`
   `docs/EaganMatrixUserGuide.txt:4190-4191` plus `docs/HakenMidi.h:1632`. For a waveguide this
   means the Delay menu transposes the instrument.
6. **A Manipulator in Bank A or B halves this delay's memory** `[G]`
   `docs/EaganMatrixUserGuide.txt:3491`, verbatim: "SummedDelay, MicroDelay, and FormulaDelay in
   Bank C (which will operate using half its normal memory)."
7. **The tap sum and the individual taps are different signals.** The `Bank C` row carries
   Tap 1 + Tap 2 + Tap 3 + Tap 4; the individual taps are only on rows 9-12, and only when the
   row-type selectors say so `[G]` `docs/EaganMatrixUserGuide.txt:4214-4217`. `[I]` The inference
   for a patch builder: a feedback network needs the individual taps and therefore needs the
   selectors, which no tool writes - so a MicroDelay FDN cannot be built from scratch by this MCP
   today, only edited. Rank `T22` for writing the selectors; `T4` is the labelling side and ships.
