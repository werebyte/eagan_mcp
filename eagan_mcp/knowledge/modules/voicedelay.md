# VoiceDelay

Bank C, card 13 of 18. A multi-tap audio delay buffer, **separate for each voice**. Its wire value
is shared fact 9's; the one spelling of the name is `index.md`'s. Everything cross-cutting -
the one delay memory and its budget (shared fact 7), the tap row alternates (shared fact 8), the
matrix column budget (shared fact 1) and the six cross-module wiring patterns - lives in
`index.md` and is referenced here, never restated.

`[G]` `docs/EaganMatrixUserGuide.txt:4095-4096`, verbatim: "The VoiceDelay provides a multi-tap
audio delay buffer, separate for each voice. VoiceDelay is suitable for creating chorus and
flanging effects, can be used for fast slap delays. VoiceDelay is available in Bank C."

`[C]` 110 of 668 factory presets run a VoiceDelay (`census.json:modules_used_including_defaults`).
It is the Bank C **default**, so most of those 110 never write `idBankC` at all - `index.md`'s
implicit-default note covers how that count is resolved.

Guide section 6.14, `docs/EaganMatrixUserGuide.txt:4052-4113`.

---

## 1. Columns

Eight Bank C columns, matrix columns 43-50 (shared fact 1). The input column's heading is an
up-pointing triangle in the Editor; written `In` here under the ASCII rule.

| Bank C col | Matrix col | Label | What it does |
|---|---|---|---|
| 1 | 43 | `In` | `[G]` `docs/EaganMatrixUserGuide.txt:4056-4058`, verbatim: "Audio input into the VoiceDelay. If the VoiceDelay is operating at reduced sample rate, this input passes through an optional anti-aliasing filter." |
| 2 | 44 | `D` | `[G]` `docs/EaganMatrixUserGuide.txt:4060-4062`, verbatim: "Delay time. 0 = no delay, 1 = delay by max amount selected in the Delay menu. The primary output of the VoiceDelay is available on the Bank C row of the EaganMatrix." |
| 3 | 45 | `T1` | `[G]` `docs/EaganMatrixUserGuide.txt:4063-4065`, verbatim: "Delay time for Tap 1. This is a multiplier on the D column value. 0 = no delay, 1 = delay by D value. The Tap 1 and 2 outputs are available as an alternative on the AesIn matrix rows." |
| 4 | 46 | `T2` | `[G]` `docs/EaganMatrixUserGuide.txt:4067`, verbatim: "Delay time for Tap 2, values 0 to 1. 0 = no delay, 1 = delay by D value." |
| 5 | 47 | `T3` | `[G]` `docs/EaganMatrixUserGuide.txt:4069-4071`, verbatim: "Delay time for Tap 3. 0 = no delay, 1 = delay by D value. The Tap 3 and 4 outputs are available as an alternative on the Sub matrix rows." |
| 6 | 48 | `T4` | `[G]` `docs/EaganMatrixUserGuide.txt:4073`, verbatim: "Delay time for Tap 4. 0 = no delay, 1 = delay by D value." |
| 7 | 49 | `H` | `[G]` `docs/EaganMatrixUserGuide.txt:4075`, verbatim: "Greater than zero stops recording new data into the VoiceDelay." |
| 8 | 50 | - | `[I]` Undocumented. The guide's VoiceDelay table has seven rows for eight columns; the inference is that column 8 is unused rather than secret, because `[C]` 2% of the 110 VoiceDelay slots carry anything in it (`corpus-module-wiring.md` S14) and no decoded preset gives it a meaning. |

`[C]` Column occupancy over the 110 VoiceDelay slots: c1 98%, c2 94%, c3 30%, c4 23%, c5 4%,
c6 3%, **c7 0%**, c8 2% (`corpus-module-wiring.md` S14). The `H` column is used by **no** factory
preset.

## 2. Units, useful ranges and blank-column behaviour

| Column | Units | Useful range | Blank (= 0) |
|---|---|---|---|
| `D` | `[G]` `docs/EaganMatrixUserGuide.txt:4060-4061`: **normalised 0..1 against the Delay menu maximum**, not milliseconds | 0..1 | **0 = no delay**, so a VoiceDelay with a blank `D` is a bypass. Benign. |
| `T1`-`T4` | `[G]` `docs/EaganMatrixUserGuide.txt:4063-4064`: a **multiplier on `D`**, not an independent time | 0..1 | 0 = no delay on that tap, i.e. the tap is off. Benign. |
| `H` | `[G]` `docs/EaganMatrixUserGuide.txt:4075`: a trigger, "Greater than zero stops recording" | <= 0 to record | 0 is normal operation. Benign - and `[C]` the factory agrees, 0% of 110 slots write it. |
| `In` | audio | - | `[I]` no input means the buffer records silence; the inference is that there is no fallback source, since the guide names exactly one audio input. |

**Blank-column verdict: VoiceDelay is blank-safe.** `[I]` Every column's zero is a documented,
musically sensible state, so the inference is that the hazards here are configuration
(the Delay menu maximum, the row-type selectors) rather than empty cells. This is the field the
completeness matrix marks `Y` for VoiceDelay (`modules-unfilled-checklist.md` S1).

`[I]` **The `D` column alone never tells you the delay time.** The inference is arithmetic: `D` is
a fraction of a maximum set by `idTimeSel` (shared fact 7), so the same `D = 0.5` is tens of
milliseconds or seconds depending on a value `D` does not carry.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | MCP today |
|---|---|---|
| Bank C type | `idBankC = 93`, value per shared fact 9 | **write + read**: `set_bank_type("C", "VoiceDelay")`, `get_setup()["banks"]["C"]` `[I]` - the inference is from the tool surface, which accepts the `setup.py:BANK_C_TYPES` string |
| All eight columns | matrix cells 43-50 | **write + read**: `set_matrix_point` / `get_matrix` `[I]`, same inference |
| Maximum delay time (the Delay menu) | `idTimeSel = 105` `[G]` `docs/HakenMidi.h:1632`, header comment "select time delay 50 ms * 2^n" | **raw read only.** `get_setup` returns `delay_time_select_raw` and no name table; nothing writes it. Rank `T22` `[I]` - the inference is that the validated `s_Mat_Poke` write rank is where this id lands; `T4` is the labelling rank and is read-only |
| Anti-aliasing (Nyquist) filter on the delay | `idAliasDelay = 108` `[G]` `docs/HakenMidi.h:1599`, header comment "true to disable nyquist filtering on delay" | **neither read nor written** - `setup.py` does not decode it. Rank `T22` `[I]`, same inference. `[C]` 4 of 668 presets write it (`census.json:setup_id_frequency`, key `AliasDelay`) |
| Audio L/R and Sub L/R rows as Tap 1-4 | `idRowTyp1 = 106` / `idRowTyp2 = 107`, shared fact 8 | **read and decoded** (`get_setup()["row_types"]`), and `get_matrix` / `set_matrix_point` now label rows 9-12 from them `[D-cap]` `tests/fixtures/microdelay_wg_v1_20261025_192903.mid`. **No write tool**: labelling is `T4`, which ships, and writing the selectors is `T22` `[I]` |

`[C]` How often the factory touches these: `TimeSel` 73 of 668, `RowTyp1` 61 of 668, `RowTyp2`
26 of 668, `AliasDelay` 4 of 668 (`census.json:setup_id_frequency`). So a VoiceDelay preset
usually runs on the device defaults for all four.

## 4. DSP cost class

**Memory-bound, not DSP-bound, and the memory is shared.** The budget itself is shared fact 7's
and is not restated here; what is specific to VoiceDelay is which two variables spend it:

`[G]` `docs/EaganMatrixUserGuide.txt:4098-4099`, verbatim: "The sample rate of the VoiceDelay
memory is limited by two variables: maximum delay and polyphony. Longer delays or higher polyphony
may result in reduced sample rate for the delay memory."

`[G]` `docs/EaganMatrixUserGuide.txt:4099-4101`, verbatim: "The Anti-Aliasing Low Pass Filter
indicator above the first Bank C column will light up when the delay memory is at reduced sample
rate. If you do not want an Anti-Aliasing filter at reduced sample rates, click on the indicator
to disable the filter."

`[I]` The practical rule: long maximum delay times polyphony gives a reduced sample rate, and the
choice is then between the anti-aliasing filter and audible aliasing. The inference is that
`idAliasDelay` exists precisely to make that choice, and no tool offers it.

`[I]` **Not measured on this device.** The checklist marks VoiceDelay's DSP cost `Y` from the two
guide passages above, not from a `get_status` reading; the inference is that "memory-bound" is a
documented property and a DSP percentage is a separate, unmeasured number.

## 5. Typical wiring

Both examples ship decoded in `factory_catalog.json`; cell orientation is
`column <- row = value`, which is `set_matrix_point(row, col, value)` read from the column side.

**`Ping Pong`** (legacy, fw 9.55) - stereo ping-pong echo with a filter per side. `[C]` from the
shipped `wiring` block (one of the 49 presets in `preset_file.WIRING_PRESETS`):

```
Bank C 1 (43)            <- Osc 2 = F, Bank C = J        (input, plus the feedback tap)
Bank C 2 (44)            <- Direct + = K                 (delay time)
Osc/Filter 4 input (21)  <- Osc 1 = 0.3, Bank C = 1
Osc/Filter 5 input (24)  <- Osc 1 = 0.3, Bank C = 1
Master SL (0)            <- Osc 4 = F
Master SR (1)            <- Osc 5 = F
  J = [W+X+Y+Z] Z = Continuous 1.0->0.5 x 1              (feedback falls with pressure)
  K = [(W+X+Y) x Z] Y = Continuous 0.18->1.0 ; Z = Continuous 0.12->1.0
  F = [W+X+Y+Z] Z = Continuous None->0.2 x 10
```

`[C]` The delay output returns on the **`Bank C` row** into two filter inputs, and each filter
feeds one Master side - that is the ping-pong. The alternative tap rows are not used.

**`BuzzStrings`** (modern, fw 10.50) - the densest VoiceDelay in the corpus, 28 matrix cells,
and the one that uses the taps. `[C]` from the shipped `wiring` block:

```
Bank C 1 (43)            <- Osc 4 = S, Bank C = D        (input + feedback)
Bank C 2 (44)            <- Osc 4 = G, Direct + = A, Direct + (2) = O, Direct x = C
Bank C 3 (45)            <- Noise = V, Direct + = F      (T1)
Bank C 4 (46)            <- Direct + = Q                 (T2)
Bank C 5 (47)            <- Noise = V, Direct + = H      (T3)
Bank C 6 (48)            <- Direct + = R                 (T4)
Osc/Filter 3 input (18)  <- Tap 1+2 (mono) = P, Tap 3+4 (mono) = P
Osc/Filter 5 input (24)  <- Tap 1+2 (mono) = 1, Tap 3+4 (mono) = 1
```

`[C]` Rows 9-12 read as **mono tap mixes**, not as audio inputs: `BuzzStrings` sets both row-type
selectors to their `AudTap` values, so the taps come back into two filters while the audio rows
stay available as a mono mix. This is shared fact 8 in use; the row names above are the ones
`get_matrix` returns today, not the static table's.

## 6. Known traps

1. **A VoiceDelay string does not follow pitch bend on a ringing note.** The construction, the
   reason to build a bendable string as a BiqBank instead, and the open question about whether
   the delay time is latched at note-on are `pitfalls.md` section 6's; this card points there
   rather than repeating the recipe `[D]` `RECIPES.md:26 (moved to pitfalls.md section 6, item 49)`, 2026-10-25, fw 10.81.
2. **`D` is a fraction, not a time** - see section 2. `[G]` `docs/EaganMatrixUserGuide.txt:4060-4061`
   plus `docs/HakenMidi.h:1632`.
3. **Taps are row *alternatives*, not additions.** Setting `rt1Tap` removes the Audio In L/R rows;
   `rt1AudTap` exists to give a mono mix of both instead `[G]` `docs/HakenMidi.h:1634-1643`.
   Shared fact 8 owns the id table; the trap is that a patch wanting both audio input *and*
   Tap 1/2 on rows 9/10 cannot have them separately.
4. **Saving a preset with `H` active breaks it on reload when a HarMan reads the buffer.**
   `[G]` `docs/EaganMatrixUserGuide.txt:3411-3412`, verbatim: "save the preset in this state (Hold
   active) and reload it, the HarMan will make no sound as there is no initial data in the delay
   buffer to work on. In this case you may want to put a Pedal on the Hold function with a Macro".
   The same warning is printed in the `H` column's own table entry `[G]`
   `docs/EaganMatrixUserGuide.txt:4079-4081`, verbatim: "and you save the preset with Hold Active.
   When the preset is loaded, no sound will be output from the HarMan as delay input data has been
   stopped before any has been loaded into the delay for the HarMan to process."
5. **HarMan `Live` reads a delay, and which delay matters.** `[G]`
   `docs/EaganMatrixUserGuide.txt:3399-3400`, verbatim: "For HarMan, a popup menu allows you to
   select a predefined Spectral Set to load into the Delay memory, or Live to manipulate
   time-domain data (312.5 Hz fundamental) you record into the SummedDelay." The header is wider
   and allows either delay `[G]` `docs/HakenMidi.h:1605`, header comment "HarMan: granulate data
   recorded by VDelay/SDelay, or flash items below".

```
CONFLICT: which delay a HarMan set to Live reads - VoiceDelay allowed vs SummedDelay only
  docs   [G]: "or Live to manipulate time-domain data (312.5 Hz fundamental) you record into
              the SummedDelay."
              - docs/EaganMatrixUserGuide.txt:3399-3400
  docs   [G]: "HarMan: granulate data recorded by VDelay/SDelay, or flash items below"
              - docs/HakenMidi.h:1605
  follows: the header, under the resolution order ([G] header > [G] guide). A VoiceDelay feeding
           a Live HarMan is therefore expected to work, but it is not device-verified and the
           guide's narrower wording stands as the warning.
```

6. **A Manipulator in Bank A or B halves this delay's memory.** `[G]`
   `docs/EaganMatrixUserGuide.txt:3491`, verbatim: "SummedDelay, MicroDelay, and FormulaDelay in
   Bank C (which will operate using half its normal memory)." `[I]` The line begins mid-sentence -
   its opening is lost across the extraction's page break at `:3487-3490` - so the apparent
   omission of VoiceDelay is a truncation artifact, not an exemption; the inference is supported
   by shared fact 7, which puts all four delays on the one memory. The missing clause is **not**
   recoverable from this file, so the exact condition stands unquoted.
