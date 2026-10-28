# Module card - SineBank (sine oscillators)

Bank wire value **3**, bank A or bank B `[G]` `docs/HakenMidi.h:1564`. Guide section 6.6,
"Multipurpose Banks: SineBank (Sine Oscillators)" `[G]`
`docs/EaganMatrixUserGuide.txt:2882`. Card schema, shared facts and the module-name spelling:
`index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle; this card writes `In`
`[G]` `docs/EaganMatrixUserGuide.txt:2894`.

## TL;DR

Structurally BiqBank's twin - the same eight-column layout, the same property stream, the same
assignable columns 3..8 (`index.md`, shared fact 2) - but it **generates** sine partials rather
than filtering an input, so column 1 is a phase offset `[G]`
`docs/EaganMatrixUserGuide.txt:2888-2890` and `B` means noise modulation depth rather than
filter bandwidth `[G]` `docs/EaganMatrixUserGuide.txt:2941-2945`.

One assignable slot carries a different meaning on the same wire id: value 7 is partial phase
spread `sP` here where a BiqBank reads it as non-linear bandwidth spread `qB` `[G]`
`docs/HakenMidi.h:1736-1737`.

The maximum partial count is a **void**: the guide says 32 `[G]`
`docs/EaganMatrixUserGuide.txt:2891-2892`, the biquad-size id implies 48 `[G]`
`docs/HakenMidi.h:1602`, and nothing local settles it - see the conflict block in section 2.

`[C]` 16 of the 668 factory presets run a SineBank (`census.json`,
`modules_used_including_defaults`).

## Key Decisions

- Carded against BiqBank by difference, since the two share one property stream and one
   assignable-value table `[G]` `docs/HakenMidi.h:1723`, so a reader who has `biqbank.md` needs
   only the deltas.
- The guide's `E` label for the even/odd column is recorded as a legacy alias of the header's
   `R`; the same column text calls it `E` in its last sentence and `Amp Ratio (R)` in its
   heading `[G]` `docs/EaganMatrixUserGuide.txt:2982-2986`, `:3073-3077`.

## Open Questions / Risks

- The maximum partial count is unresolved: 32 against 48. Stated as a void in section 2, not
   filled `[G]` `docs/EaganMatrixUserGuide.txt:2891-2892` against `[G]`
   `docs/HakenMidi.h:1602`.
- `[I]` The guide documents no deflation control for SineBank, and the bank-param id's
   documented meanings are a biquad deflation level or a WaveBank waveform (`index.md`, shared
   fact 4) - the inference is that a generating bank has nothing to deflate, but the header does
   not exclude SineBank, so this is an inference and not a fact.

---

## 1. What every column means

| Col (bank A / bank B) | Fixed? | Label | Meaning | Source |
|---|---|---|---|---|
| 1 (27 / 35) | fixed | `In` | Phase offset for all partials: "Leave this column blank for normal operation. Other values can be used for phase modulation effects." The partial count is set by the text control above this column | `[G]` `docs/EaganMatrixUserGuide.txt:2888-2892` |
| 2 (28 / 36) | fixed | `F` | "Frequency (in kHz) for the first sine oscillator (fundamental partial) in the SineBank" | `[G]` `docs/EaganMatrixUserGuide.txt:2899-2901` |
| 3..8 (29-34 / 37-42) | assignable | preset data | Up to six parameters, chosen per column by clicking the heading | `[G]` `docs/EaganMatrixUserGuide.txt:2903-2906` |

Guide-stated default picklist for columns 3..7 `[G]`
`docs/EaganMatrixUserGuide.txt:2906-2907`, verbatim: "Columns default to sF, E, sP, C, sA (and
an unused column that can also be selected - red dot)". `[C]` The corpus agrees, which is the
difference from BiqBank: 12 of 12 measured blocks put the phase-spread value on column 5 and
10 of 12 put the even/odd value on column 4
(`analysis/findings/corpus-module-wiring.md` S5).

The 18-value assignable table lives in `index.md`, shared fact 2 `[G]`
`docs/HakenMidi.h:1726-1747`. What those values **do in a SineBank**, and only where they
differ from a BiqBank:

| Value | Meaning in a SineBank | Same as BiqBank? | Source |
|---|---|---|---|
| `sF` | Linear frequency spread: 1 = harmonic, >1 stretched, <1 compressed | same | `[G]` `docs/EaganMatrixUserGuide.txt:2915-2919` |
| `qF` | Non-linear spread, offsets proportional to partial number squared | same | `[G]` `docs/EaganMatrixUserGuide.txt:2921-2923`, `:2935-2936` |
| `B` | **Partial bandwidth as noise**: 0 = pure sine waves, >0 = each partial is amplitude-modulated by low-frequency noise, creating a noise band around its frequency | **different** - a BiqBank's `B` is filter bandwidth | `[G]` `docs/EaganMatrixUserGuide.txt:2941-2945` |
| `R`, printed `E` | Even/odd partial amplitude: <0 suppresses odd partials, >0 suppresses even | same | `[G]` `docs/EaganMatrixUserGuide.txt:2982-2986` |
| `C` | Centre of focus: 0 = partial 1, 1 = partial 8, 1.5 = partial 12, 4 = partial 32 | same shape | `[G]` `docs/EaganMatrixUserGuide.txt:2972-2980` |
| `sB` | **Noise-modulation spread**: >0 = partials farther from Centre get more noise modulation, <0 less | **different sense** - depth of noise, not filter width | `[G]` `docs/EaganMatrixUserGuide.txt:2956-2962` |
| `sP` | **Phase spread between partials**: 0 = every partial uses column 1's offset, >0 scales the offset per partial | **different** - the same wire id is `qB` in a BiqBank | `[G]` `docs/EaganMatrixUserGuide.txt:2947-2951` and `[G]` `docs/HakenMidi.h:1736-1737` |
| `sA` | Amplitude spread from Centre, as dB/Octave or **dB/Partial** | same shape | `[G]` `docs/EaganMatrixUserGuide.txt:2964-2970` |
| `1F 2F 3F`, `1B 2B 3B`, `1A 2A 3A` | the three spectral peaks | same | `[G]` `docs/EaganMatrixUserGuide.txt:2988-2990` |

The add-not-replace rule holds here too `[G]` `docs/EaganMatrixUserGuide.txt:2907-2910`,
verbatim: "These values when defined as matrix columns are added to identical Properties set in
the BiqBank Properties panel (except Spectral Peak Resonance Frequency which is multiplied by
the associated property). If not defined as a SineBank matrix column, the fixed value defined
in the property control is used as is."

## 2. Units, useful ranges, blank-column behaviour

| Parameter | Property range and default | What a blank matrix column does | Source |
|---|---|---|---|
| column 1 phase offset | 0..1 | **blank is the documented normal state** | `[G]` `docs/EaganMatrixUserGuide.txt:2888-2889` |
| `F` | kHz, no property | silence `[I]`, the inference being that a zero fundamental leaves nothing to sound |
| `sF` | 0.0..2.0, default **0.0** | falls back to 0.0, which is **not harmonic**; 1 is harmonic | `[G]` `docs/EaganMatrixUserGuide.txt:3058-3061` |
| `B` | 0.0..2.0, default 0.0 / Narrow | 0 = pure sines, no noise modulation - **benign here**, unlike BiqBank | `[G]` `docs/EaganMatrixUserGuide.txt:3069-3072` |
| `R` | -1.0..1.0, default 0.0 / Neutral | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:3073-3077` |
| `C` | 0.0..1.0, default 0.0; the control caps at partial 8 | partial 1 is centre | `[G]` `docs/EaganMatrixUserGuide.txt:3081-3087` |
| `sB` | **0.0..1.0** - narrower than BiqBank's 0..2 - default 0.0, minimum 0 | equal noise modulation for every partial | `[G]` `docs/EaganMatrixUserGuide.txt:3088-3094` |
| `sP` | the phase-spread control sits **above** the bandwidth-delta property | 0 = every partial shares column 1's phase | `[G]` `docs/EaganMatrixUserGuide.txt:3095-3096` |
| `sA` | 0.0..5.0 = 0 dB..**-12 dB** - BiqBank's is -30 dB - default 0.0 | Centre does not affect amplitudes | `[G]` `docs/EaganMatrixUserGuide.txt:3101-3104` |

**Blank-column verdict.** Blank falls back to the Property, as in a BiqBank `[G]`
`docs/EaganMatrixUserGuide.txt:2907-2910`, and here the `B` default of 0 is also the musically
neutral choice: this is the one bank where a blank bandwidth column is correct `[G]`
`docs/EaganMatrixUserGuide.txt:3069-3070`. The `sF` default of 0.0 is still inharmonic `[G]`
`docs/EaganMatrixUserGuide.txt:3058-3059`.

`[C]` Measured column occupancy over 15 SineBank bank slots: c1 86%, c2 100%, c3 73%, c4 60%,
c5 46%, c6 40%, c7 33%, c8 6% (`analysis/findings/corpus-module-wiring.md` S5).

```
CONFLICT: the maximum partial count - VOID, not filled
  docs   [G]: "The number of Sinebank partials can be changed with the text control above this
              column from a default of 8 to 32 in steps of 8"
              - docs/EaganMatrixUserGuide.txt:2891-2892. Internally corroborated by the Centre
              text: "A value of 4 means the 32nd partial (maximum) is the center"
              - docs/EaganMatrixUserGuide.txt:3086
  header [G]: the biquad-size id's own comment is "0..5 means 8..48 modes; 6 means variable",
              with no SineBank carve-out - docs/HakenMidi.h:1602
  effect: an agent setting a SineBank to 48 partials may get 32, or an invalid state. It also
              decides the useful maximum of the C column - 4 for 32 partials, 6 for 48 - so a
              Centre sweep scaled for the wrong bound overshoots or under-reaches.
  resolution: UNRESOLVED, and left unresolved. The guide is internally consistent at 32 and is
              specific to SineBank; the header's comment is written for the biquad banks. No
              local source can tell which governs, so a guess would be indistinguishable from
              a fact. It is the merged device plan's DT13
              (analysis/findings/modules-unfilled-checklist.md gap 8), and the corpus has no
              leverage because the partial count is an absence-means-default field.
```

## 3. Properties-panel settings and MCP reachability

The Properties panel is the same stream as BiqBank's: write `s_BiqSin_Poke` = stream 25, read
back `s_BiqSin` = stream 12, 24 ids per bank `[G]` `docs/HakenMidi.h:1103`, `:1139`,
`:1726-1782`.

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankA/B` | **yes** - `set_bank_type("A", "SineBank")` `[G]` `eagan_mcp/setup.py:227` |
| Matrix cells 27-34 / 35-42 | the matrix | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| Spread, BW, Amp Ratio, Centre, bandwidth delta, phase spread, amplitude delta, the nine spectral-peak ids | the property stream's ids 1..17 (bank A) / 25..41 (bank B) | **unreachable**: no codec reads or writes stream 12 or 25 `[G]` `docs/HakenMidi.h:1726-1747`. `T16` is the rank that would unblock it |
| **Which function each of columns 3..8 carries** | the column selects (`index.md`, shared fact 2) | **unreachable**, and without it no tool can name a SineBank column `[G]` `docs/HakenMidi.h:1748-1753`. `T16` unblocks the read, `T4` then joins it into `get_matrix`'s labels |
| Partial count | the biquad-size id (`index.md`, shared fact 5) | **read-only and undecoded** as `bank_params.A.biquad_size_raw` `[G]` `eagan_mcp/setup.py:193`. No write tool |
| dB/Partial against dB/Octave for `sA`; Amp Headroom | the two column-mode toggles (`index.md`, shared fact 3) | **read-only and undecoded** as `column_mode_1_raw` and `column_mode_2_raw` `[G]` `eagan_mcp/setup.py:191-192`. No write tool |

`[I]` **A decoder that hardcodes the BiqBank label set mislabels every SineBank preset**, since
value 7 is `sP` here and `qB` there on one wire id `[G]` `docs/HakenMidi.h:1736-1737` - the
inference is that any future column-select decode must take the bank type as an argument, not
assume one table.

## 4. DSP cost class

**Medium, scaling with the partial count**, 8 to 32 in steps of 8 `[G]`
`docs/EaganMatrixUserGuide.txt:2891-2892`. `[I]` The inference is the same as BiqBank's: a bank
of independent generators costs in proportion to how many it runs.

The guide's one performance remark is a quality caveat rather than a cost one `[G]`
`docs/EaganMatrixUserGuide.txt:3170-3173`, verbatim: "Unlike other oscillators in the
EaganMatrix, SineBank oscillators use simple table lookup for sine values. As a result, the
SineBank may have audible table lookup noise at very low frequencies."

## 5. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`SineBank - Basic` - one macro per column, and the minimal output `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: A = SineBank param=deflate 1
Bank A 1 <- Direct + (2) = D      Bank A 5 <- Direct + (2) = E
Bank A 2 <- Direct + (2) = B      Bank A 6 <- Direct + (2) = F
Bank A 3 <- Direct + (2) = C      Bank A 7 <- Direct + (2) = G
Bank A 4 <- Direct + (2) = A
Master SL/SR <- Bank A = z^2
  B = X = -1.00 -> 1.00 x1 kHz                 (exact pitch on the F column)
  D = W SG1 0.2 [Sine] ; Y = 0.11 -> 0.11      (an LFO on the phase-offset column)
  C = W Constant 0.2 x10 x macro ii ; Y = -1.00 -> -0.99
```

`[C]` Every column sits on `Direct + (2)`, not `Direct +`: the tutorial presets use the
second additive row so the first stays free. `Master SL/SR <- Bank A = z^2` is the minimal
output, pressure squared with no formula at all. Note column 1 carrying a slow LFO - the
documented "phase modulation effects" use of the phase-offset column.

`Bells of Digul` - the only preset in the 668 that puts the even/odd value on SineBank's column
8, and one of two that write a spectral-peak property at all `[C]`
(`factory_catalog.json`, `wiring`).

`Harmonoid Spark` routes `Bank A -> Osc 1 F`, i.e. a SineBank used as an FM modulator rather
than as an output `[C]` (`factory_catalog.json`, `wiring`).

`[C]` Guide-named lead spellings corrected against the 668 filenames: `SinebankFM String` is
`SineBank FM String` and `Sinebank Horn` is `SineBank Horn`; `SinePhases` is spelled as the
guide has it `[G]` `docs/EaganMatrixUserGuide.txt:3176-3179`.

## 6. Known traps

1. **The `sF` Property default is 0.0, which is inharmonic.** Write 1 for harmonic partials
   `[G]` `docs/EaganMatrixUserGuide.txt:3058-3059`.
2. **`B` means noise, not filtering.** An agent carrying BiqBank intuition and writing a small
   `B` "for resonance" gets noise-band amplitude modulation instead `[G]`
   `docs/EaganMatrixUserGuide.txt:3069-3072`.
3. **Value 7 is `sP`, not `qB`** - one wire id, two meanings `[G]` `docs/HakenMidi.h:1736-1737`.
4. **Audible table-lookup noise at very low frequencies**; the guide's own workarounds are
   phase modulation, masking, or a different sine source `[G]`
   `docs/EaganMatrixUserGuide.txt:3170-3173`.
5. **Spectral peaks need Amp Headroom at 24 dB**, as in a BiqBank `[G]`
   `docs/EaganMatrixUserGuide.txt:3165-3166`. The toggle is a column-mode toggle no tool writes.
6. **A negative `sB`, and a Centre past partial 8, can only come from the matrix** - the
   property floors at 0 and the Centre control caps at partial 8 `[G]`
   `docs/EaganMatrixUserGuide.txt:3083-3084`, `:3092-3093`.
7. **`sA` maxes at -12 dB here but -30 dB in a BiqBank**, so the same numeric column value
   means a different amount of rolloff between the two banks `[G]`
   `docs/EaganMatrixUserGuide.txt:3101` against `[G]` `docs/EaganMatrixUserGuide.txt:2450`.
8. **Do not promise 48 partials.** The partial-count bound is the void in section 2 `[G]`
   `docs/EaganMatrixUserGuide.txt:2891-2892`.
