# Module card - Additive (additive synthesis from Loris analysis data)

Bank wire value **10**, bank A or bank B only `[G]` `docs/HakenMidi.h:1565`.
Device-corroborated: "bank values 8 = CVC, 10 = Additive (old menu-order guess was wrong)"
`[D]` `CLAUDE.md:14`, 2026-10-25, fw 10.81. Guide section 6.11, "Multipurpose Banks: Additive
Synth" `[G]` `docs/EaganMatrixUserGuide.txt:3503`. Card schema, shared facts and the
module-name spelling: `index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle; this card writes `In`
`[G]` `docs/EaganMatrixUserGuide.txt:3510`.

## TL;DR

Up to 96 sine components driven by pre-analysed data - a resynthesis engine, not a sampler
`[G]` `docs/EaganMatrixUserGuide.txt:3635-3636`. The columns are fixed, but **two of them are
mode-switched** (`index.md`, shared fact 3), one of them four ways, and selecting the
second-index mode changes what the Centre column means `[G]`
`docs/EaganMatrixUserGuide.txt:3573-3578`.

Which analysis buffer it plays is the spectral-set selector reading its Additive value set
`[G]` `docs/HakenMidi.h:1617-1621` (`index.md`, shared fact 6 owns the table).

It is the **only bank with a documented hard polyphony cap** - and the cap for this device is
not among the named systems `[G]` `docs/EaganMatrixUserGuide.txt:3657-3661`.

`[C]` 12 of the 668 factory presets run an Additive (`census.json`,
`modules_used_including_defaults`), the smallest bank population in the corpus.

## Key Decisions

- The second-index mode is carded as a **mode switch that rewrites another column**, by
   analogy to BiqGraph's decay-time switch - the same class of hidden remap `[G]`
   `docs/EaganMatrixUserGuide.txt:3573-3578`.
- The polyphony caps are quoted verbatim with their hardware names, because they are the only
   numeric DSP limits the guide states for any bank `[G]`
   `docs/EaganMatrixUserGuide.txt:3657-3661`.

## Open Questions / Risks

- The caps name C1x, L1x, "2x DSP instruments", L6x and LX8. **The EaganMatrix Module is not
   among them**, so which cap applies here is unknown, and it is the difference between 2 and 12
   voices `[G]` `docs/EaganMatrixUserGuide.txt:3657-3661`. It is the merged device plan's DT13
   in the original module filing (`analysis/findings/modules-unfilled-checklist.md` gap 17).
- `[G]` `docs/EaganMatrixUserGuide.txt:3621-3622` writes the formant-correction switch twice
   with different signs - "As long as the S value is not set to -1" and then "If S = 01" - and
   the second is plainly a typesetting error for -1.
- `[G]` `docs/EaganMatrixUserGuide.txt:3755-3756` says the Loris analysis and download tool "is
   not yet available at time of this writing. Until that is available only the Mahling phrase
   option should be used", while the same section describes forty user slots `[G]`
   `docs/EaganMatrixUserGuide.txt:3664-3666`. Current availability on 10.81 is unresolved, and
   a guide stamped for 10.80 at best cannot settle it.

---

## 1. What every column means

| Col (bank A / bank B) | Label | Meaning | Source |
|---|---|---|---|
| 1 (27 / 35) | `In` | Modulation input, normally low-pass-filtered noise: it "Modulates sine wave components that are below the N column threshold (if set), thereby creating bandwidth for low-amplitude components... To disable all modulation (pure additive sine-wave synthesis) leave this column and the B column blank (or 0)." | `[G]` `docs/EaganMatrixUserGuide.txt:3507-3513` |
| 2 (28 / 36) | `F` | "Frequency (in kHz) of the fundamental sine wave component of the Additive Synthesis (1st partial)" | `[G]` `docs/EaganMatrixUserGuide.txt:3515-3517` |
| 3 (29 / 37) | spread, **two-way** | A frequency spread or a quadratic frequency spread, chosen by a column-mode toggle. Range "-1 to 1: 0 normal spacing of sine wave components (harmonic modes), >0 stretched spacing, <0 compressed spacing" | `[G]` `docs/EaganMatrixUserGuide.txt:3519-3523` |
| 4 (30 / 38) | `B` | Noise modulation threshold: "When a sine wave component's amplitude envelope drops below this threshold, it will be amplitude modulated by Additive's first column. 0 prevents modulation, 1 modulates all components, <0 reverses the sense of the threshold" | `[G]` `docs/EaganMatrixUserGuide.txt:3537-3542` |
| 5 (31 / 39) | **four-way** | A second index, a deviation frequency, a pruned-partial count or a noise threshold - see the table below | `[G]` `docs/EaganMatrixUserGuide.txt:3545-3564` |
| 6 (32 / 40) | `sA` | Spread amplitude: ">0: Reduces amplitude of partials farther from the Center (C column)" | `[G]` `docs/EaganMatrixUserGuide.txt:3566-3567` |
| 7 (33 / 41) | `C` | Centre, 0 to 1: "0.00 means first partial (sine wave component) is center, 0.01 means 2nd sine wave is center, 0.95 means last (96th) sine wave component is center." **Special meaning when the second index is in use**: it becomes the crossfade between the two indices | `[G]` `docs/EaganMatrixUserGuide.txt:3570-3578` |
| 8 (34 / 42) | `I` | Analysis data index | `[G]` `docs/EaganMatrixUserGuide.txt:3582`, `:3599-3605` |
| - | `S` | Spectral dilation and formant control: "0 means no change to spectral envelope, >0 stretches spectrum, <0 compresses. Special value of -1 neglects spectral envelope when changing pitch (chipmunk effect)." **Listed with no column position** | `[G]` `docs/EaganMatrixUserGuide.txt:3617-3619` |

**Where the spectral dilation parameter sits is unresolvable from the local sources.** The
guide lists **nine** labelled parameters against **eight** bank columns and gives the dilation
no position `[G]` `docs/EaganMatrixUserGuide.txt:3507-3623`. The corpus cannot close it either:
column 5's four-way mode is written by exactly **one** preset of the 668, and that preset
selects the noise threshold, so no factory preset ever varies the mode far enough to expose a
ninth slot `[C]` (`analysis/findings/corpus-module-wiring.md` S13). State the position as
**unknown**; do not place it.

Column 5's four modes `[G]` `docs/EaganMatrixUserGuide.txt:3545-3564`:

| Mode | Meaning | Source |
|---|---|---|
| second index | "Optional second index into the Analysis data for interpolating between non-adjacent/sequential (I and I') index values", with the same range as the main index. The pair is crossfaded by the Centre column | `[G]` `docs/EaganMatrixUserGuide.txt:3546-3553` |
| deviation frequency | "Deviation from reference frequency (1=Normal). (Used to be qA)" | `[G]` `docs/EaganMatrixUserGuide.txt:3555` |
| pruned additive | "Controls the number of partials to play (0.0=1 partial, 0.1= 2 partials to 0.95 = max 96 partials (though the resynthesis tool only allows a max of 64 partials to be defined)" | `[G]` `docs/EaganMatrixUserGuide.txt:3557-3559` |
| noise threshold | "Sets a noise threshold for modulation input (see Modulation input above)" | `[G]` `docs/EaganMatrixUserGuide.txt:3563-3564` |

The wire values for both toggles are `index.md`, shared fact 3 `[G]`
`docs/HakenMidi.h:1580`, `:1588`.

## 2. The index column and the analysis decades

The index traverses the selected buffer `[G]` `docs/EaganMatrixUserGuide.txt:3599-3605`:
0.0 to 1.0 traverses the Mahling phrase if that is selected, otherwise the first additive set
in the selected buffer; 1.0 to 2.0 the second set; 2.0 to 3.0 the third; up to 9.0 to 10.0 for
the tenth.

Which buffer - the Mahling phrase or one of four decades - is the spectral-set id reading its
Additive value table (`index.md`, shared fact 6) `[G]` `docs/HakenMidi.h:1617-1621`.

The guide's own hint `[G]` `docs/EaganMatrixUserGuide.txt:3611-3612`, verbatim: "Use a constant
in the Direct+ row to select and Analysis within the current decade." And the caution `[G]`
`docs/EaganMatrixUserGuide.txt:3606-3610`, verbatim: "Not all sets may be installed... It is up
to the user to determine what sets are in what slots if programming in the Matrix." Since
10.45, selecting one Additive bank sets a second displayed Additive bank to the same decade
`[G]` `docs/EaganMatrixUserGuide.txt:3700-3701`.

## 3. Units, useful ranges, blank-column behaviour

| Column | Range and neutral | What blank (= 0) does | Source |
|---|---|---|---|
| `In` | audio, normally low-pass-filtered noise | **documented as the correct way to get pure additive synthesis**, together with a blank `B` | `[G]` `docs/EaganMatrixUserGuide.txt:3512-3513` |
| `F` | kHz | silence `[I]` - the inference is that a zero fundamental leaves no partials to place |
| spread (column 3) | **-1 .. 1, neutral 0** | **neutral**: 0 is "normal spacing", unlike every other bank's spread column where 1 is harmonic | `[G]` `docs/EaganMatrixUserGuide.txt:3521-3523` |
| `B` | 0 prevents modulation, 1 modulates all, <0 reverses the sense | neutral, giving pure sines | `[G]` `docs/EaganMatrixUserGuide.txt:3539-3542` |
| pruned partials (column 5 mode) | 0.0 = 1 partial, 0.95 = 96 partials | **one partial.** A blank pruning column reduces the bank to a single sine | `[G]` `docs/EaganMatrixUserGuide.txt:3557-3558` |
| deviation frequency (column 5 mode) | **neutral = 1** | **not neutral**: zero is not "no deviation" | `[G]` `docs/EaganMatrixUserGuide.txt:3555` |
| noise threshold (column 5 mode) | threshold | no noise threshold | `[G]` `docs/EaganMatrixUserGuide.txt:3563-3564` |
| `sA` | neutral 0 | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:3566-3567` |
| `C` | 0..1, or the index crossfade | the first partial is centre, or fully at the main index | `[G]` `docs/EaganMatrixUserGuide.txt:3570-3578` |
| `I` | 0..10 | the start of the first set: valid but static | `[G]` `docs/EaganMatrixUserGuide.txt:3599-3605` |
| `S` | **0 = no change**, -1 = formant correction off | neutral at 0 | `[G]` `docs/EaganMatrixUserGuide.txt:3617-3619` |

**Blank-column verdict.** Additive is the one bank where a blank spread column is correct,
because its neutral is 0 rather than 1 `[G]` `docs/EaganMatrixUserGuide.txt:3521-3523`, and a
blank input plus a blank threshold is the documented pure-sine configuration `[G]`
`docs/EaganMatrixUserGuide.txt:3512-3513`. The two traps are both on column 5: the pruning mode
reads blank as one partial, and the deviation mode's neutral is 1.

**No factory preset selects the pruning mode at all** `[C]`: column 5's mode is written by one
preset of the 668 and that preset selects the noise threshold, so the corpus gives the pruning
behaviour no evidence either way (`analysis/findings/corpus-module-wiring.md` S13). The gap is
the merged device plan's DT13 (`analysis/findings/modules-unfilled-checklist.md` gap 5).

`[C]` Measured column occupancy over 12 Additive bank slots: c1 25%, **c2 100%**, c3 66%,
c4 41%, c5 25%, c6 66%, **c7 100%, c8 100%**
(`analysis/findings/corpus-module-wiring.md` S13). `[C]` Columns 1 and 4 are the two the guide
tells you to blank for pure additive synthesis, and they are the two the corpus writes least.

## 4. Formant correction and the 64-against-96 partial count

- With formant correction **off**, the engine "always synthesizes 64 partials, because that is
   how many partials are in the analysis files" `[G]`
   `docs/EaganMatrixUserGuide.txt:3713-3714`.
- With it **on**, "it synthesizes up to 96 partials", drawing a spectral envelope from all 64
   analysis partials and re-deriving each partial's amplitude for the pitch actually being
   played `[G]` `docs/EaganMatrixUserGuide.txt:3721-3725`.
- The switch is the dilation value `[G]` `docs/EaganMatrixUserGuide.txt:3621-3623`, verbatim:
   "As long as the S value is not set to -1, Formant correction as discussed below will be
   turned on."
- Why it matters `[G]` `docs/EaganMatrixUserGuide.txt:3750-3752`, verbatim: "Ignoring this is
   what results in the so-called "Chipmunk Effect" and many other artifacts, so formant
   correction is important unless you want it to sound like the resonating body is shrinking as
   pitch goes up".
- Partials 65 to 96 are computed only when the note is low enough that the formant range
   extends past the 64th analysed partial; the guide's worked example runs a 140.9 Hz analysis,
   with data to 9.017 kHz, down to 84.8 Hz, where 64 partials would reach only 5.427 kHz `[G]`
   `docs/EaganMatrixUserGuide.txt:3730-3747`.

## 5. Properties-panel settings and MCP reachability

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankA/B`, value 10 | **yes** - `set_bank_type("A", "Additive")` `[G]` `eagan_mcp/setup.py:227` |
| All matrix columns | cells 27-34 / 35-42 | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| **Analysis buffer**: Mahling phrase or one of four decades | the spectral-set id (`index.md`, shared fact 6) | **read-only, decoded by name**: `get_setup` picks the Additive value table when the bank is an Additive and returns `bank_params.A.spectral_set` `[G]` `eagan_mcp/setup.py:186-195`. **No tool writes it** |
| The two-way toggle on column 3 | the first column-mode toggle (`index.md`, shared fact 3) | **read-only and undecoded** as `column_mode_1_raw` `[G]` `eagan_mcp/setup.py:191`. No write tool |
| The **four-way** toggle on column 5 | the second column-mode toggle (`index.md`, shared fact 3) | **read-only and undecoded** as `column_mode_2_raw` `[G]` `eagan_mcp/setup.py:192`. No write tool - **and this one also changes what the Centre column means** |
| Copy an analysis slot to another slot | the two analysis-slot ids | **unreachable** `[G]` `docs/HakenMidi.h:1663-1664` |
| Analysis set names | `s_AnlysName` = stream 27, requested by a task code | **unreachable**; note that `list_user_presets` already uses that task code's wire form for preset names, so the request path is half built `[G]` `docs/HakenMidi.h:1143`, `:905` |

`[I]` Column 5's toggle is the load-bearing gap here, because it decides both what column 5
means and what column 7 means: a matrix dump of an Additive bank cannot be interpreted without
it - the inference is a direct reading of the guide's Centre text against the decoder. `T4` is
the rank that would join the decoded toggles into `get_matrix`'s labels. The write side is
`T22`, `set_module_option` - the `T` scheme runs to twenty-two ranks, not twenty; the ranked
list that names them is `analysis/findings/modules-mcp-reachability.md` section 5 rank 6,
which `T22` folds into the `T` namespace.

## 6. DSP cost class

**Heavy, with a hard polyphony cap.** This is the only bank for which the guide states a
numeric limit `[G]` `docs/EaganMatrixUserGuide.txt:3657-3661`, verbatim: "When Additive banks
are in use, maximum polyphony is limited due to the inherent high memory requirements. C1x and
L1x systems will have max polyphony 2... 2x DSP instruments will support a max polyphony of 4
using the additive engine and L6x and LX8 instruments a max polyphony of 12."

The EaganMatrix Module is not among the named systems, so **the applicable cap is unknown** -
a 2-against-12 question, filed as a device-owned gap
(`analysis/findings/modules-unfilled-checklist.md` gap 17) and covered by the merged device
plan's DT13. Related device lesson: Double Computation Rate was the cause of a
three-voices-at-100%-DSP situation on this Module `[D]` `CLAUDE.md:117-119`, 2026-10-25,
fw 10.81.

The guide's other sizing statements: the engine "has limited Analysis Data Memory, the Analysis
Data must be prepared ahead of time, and it provides only a few options for manipulating the
data" `[G]` `docs/EaganMatrixUserGuide.txt:3652-3653`, and each additive set contains "512 sets
(slices) of 64 partials" `[G]` `docs/EaganMatrixUserGuide.txt:3674-3675`.

## 7. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`Additive Vocal 1 Transform` - the Additive signature, and the only mode-select evidence in
the corpus `[C]` (`factory_catalog.json`, `wiring`):

```
bank: A = Additive param=deflate 1 ; C = SummedDelay ; osc 5 = DSF Oscillator
Bank A 1 <- Osc 5 = 9                        (noise through slot 5 as the modulation input)
Bank A 2 (F) <- Direct + = A
Bank A 3     <- Direct + = G         Bank A 6 (sA) <- Direct + = D
Bank A 4 (B) <- Direct + = H         Bank A 7 (C)  <- Direct + = F, Direct + (2) = E,
Bank A 5     <- Direct + = 0.96,                      Direct x = 0.1
                Direct + (2) = 1     Bank A 8 (I)  <- Direct + = C
Master SL/SR <- Bank A = z^2, Audio In L/R = J, Direct x = 9
  A = X = -0.12 -> 0.12 x100 Octaves ; Y = -0.19 -> -0.14   (pitch plus a wheel detune)
  C = X = 0.17 -> -0.21 Gentle S                            (the index tracks pitch)
  F = W SG3 0.12 ; Z = 0 -> 0.21                            (the Centre column swept)
```

`[C]` The signature is columns 7 and 8 both driven, the Centre control and the analysis
index, because that is where the module's sound comes from; the corpus writes both in 12 of 12
bank slots. `[C]` This is also the **only** preset in the 668 that writes column 5's mode
select at all, and it selects the noise threshold, which is why the pruning mode has no corpus
evidence.

`Should I Stay or Should I Go` - the densest Additive in the corpus at eleven cells, and the
one that drives the index from the noise row `[C]` (`factory_catalog.json`, `wiring`):

```
bank: A = Additive param=deflate 1 ; osc 4 = Band Reject (Notch)
Bank A 2 (F) <- Direct + = E
Bank A 4 (B) <- Noise = H, Direct + = A, Direct + (2) = C, Direct x = 0.1
Bank A 6     <- Direct + = G
Bank A 7 (C) <- Noise = H, Direct + = A, Direct + (2) = B, Direct x = 0.1
Bank A 8 (I) <- Direct + = F
```

`[C]` One letter `H` arriving on the noise row of two different columns is how this preset
randomises the threshold and the Centre together. Note columns 1, 3 and 5 left blank, which is
the documented pure-sine configuration plus a neutral spread.

`Additive Gnilham`, `Additive Horn 1 Wbl` and `Instant Reich` are the other three Additive
presets with a shipped wiring block `[C]` (`factory_catalog.json`, `wiring`).

Factory leads the guide names `[G]` `docs/EaganMatrixUserGuide.txt:3759-3760`:
`Additive Vocal 1 Transform`, `Additive 1`, `Instant Reich`, `Shall I Stay or Shall I Go`.
`[C]` Two of those four need correcting against the 668 filenames: `Additive 1` matches no
file, and the fourth is spelled `Should I Stay or Should I Go`.

Creative uses the guide suggests `[G]` `docs/EaganMatrixUserGuide.txt:3654-3656`, verbatim:
"it is possible to make percussion-like sounds by artfully traversing certain parts of the
Mahling phrase (a bit like beatboxing) or make creepy voices by playing very low notes while
silencing (pruning out) the first 20 sine wave components."

## 8. Known traps

1. **The pruning mode reads blank as one partial**, not as all partials `[G]`
   `docs/EaganMatrixUserGuide.txt:3557-3558`.
2. **The deviation-frequency mode's neutral is 1**, not 0 `[G]`
   `docs/EaganMatrixUserGuide.txt:3555`.
3. **The spread column's neutral is 0 here**, unlike BiqBank, SineBank and ModMan where
   harmonic spacing is 1. An agent carrying a spread of 1 across from a BiqBank gets stretched
   partials `[G]` `docs/EaganMatrixUserGuide.txt:3521-3523`.
4. **Selecting the second index rewrites the Centre column** from centre-of-focus to a
   crossfade, so a matrix dump cannot be read without the column-5 toggle `[G]`
   `docs/EaganMatrixUserGuide.txt:3573-3578`.
5. **A dilation of -1 turns formant correction off** and caps the engine at 64 partials - easy
   to hit by accident with a bipolar formula `[G]`
   `docs/EaganMatrixUserGuide.txt:3621-3623`.
6. **The second index must stay within the same decade** as the main one `[G]`
   `docs/EaganMatrixUserGuide.txt:3575-3577`.
7. **Partials 65 to 96 exist only with formant correction on** `[G]`
   `docs/EaganMatrixUserGuide.txt:3713-3714`, `:3721`.
8. **Not all analysis slots are installed**, so a preset programmed against an empty slot has
   nothing to play `[G]` `docs/EaganMatrixUserGuide.txt:3606-3610`.
9. **The polyphony cap is hard, and the cap for this Module is undocumented** `[G]`
   `docs/EaganMatrixUserGuide.txt:3657-3661`.
10. **It is not a sampler** `[G]` `docs/EaganMatrixUserGuide.txt:3635`, verbatim: "The Additive
    Synth is not a sampler." A plain-words request for "a sampled voice" should not be routed
    here without explaining the constraint.
11. **Mahling data can be corrupted and needs a reformat** `[G]`
    `docs/EaganMatrixUserGuide.txt:3671-3672`, verbatim: "if that does not play correctly
    reload the Mahling data in Midi and Global Section/Utilities/Reformat Mahling Data".
12. **Do not state where the dilation parameter's column is.** Nine labels, eight columns, and
    no corpus leverage - see section 1 `[G]` `docs/EaganMatrixUserGuide.txt:3617-3619`.
