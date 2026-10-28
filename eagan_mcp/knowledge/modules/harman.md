# Module card - HarMan (granular harmonic manipulator)

Bank wire value **6**: bank A, bank B, or bank C as `HarMan (alias of B)` `[G]`
`docs/HakenMidi.h:1568`. Guide section 6.9, "Multipurpose Banks: HarMan (Granular Harmonic
Manipulator)" `[G]` `docs/EaganMatrixUserGuide.txt:3323`. Card schema, shared facts, the
module-name spelling and what the alias form means: `index.md`, which this card references and
never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

## TL;DR

A pitch-synchronous granulator over a very short sample - 150 ms, "so short that it only
provides 12 different `raw` grains" `[G]` `docs/EaganMatrixUserGuide.txt:3358-3362` - or over
live audio recorded into a delay. The columns are fixed (`index.md`, shared fact 2).

Which sample it plays is the spectral-set selector (`index.md`, shared fact 6), and a preset's
whole character is tied to it `[G]` `docs/EaganMatrixUserGuide.txt:3366-3368`.

`H` and `S` must be scaled together or the grain length desynchronises from the dilation `[G]`
`docs/EaganMatrixUserGuide.txt:3336-3340`, `:3351-3352`, and the index column has special
negative values that only apply in Live mode `[G]`
`docs/EaganMatrixUserGuide.txt:3343-3346`.

`[C]` 105 of the 668 factory presets run a HarMan, plus 5 more whose bank C mirrors bank B's
(`census.json`, `modules_used_including_defaults`) - the largest manipulator population in the
corpus.

## Key Decisions

- The column **positions** are taken from the corpus, not from the guide's table order, which
   gives no column numbers at all - see section 1 `[C]`
   (`analysis/findings/corpus-module-wiring.md` S9).
- Live-from-delay is carded as a distinct operating mode, because three things change with it:
   the index column's meaning `[G]` `docs/EaganMatrixUserGuide.txt:3343-3346`, the dependency on
   delay memory `[G]` `docs/EaganMatrixUserGuide.txt:3389-3390`, and a save-and-reload failure
   `[G]` `docs/EaganMatrixUserGuide.txt:3404-3412`.

## Open Questions / Risks

- `[C]` Columns 4, 5 and 6 are written in 4%, 3% and 0% of 120 measured bank slots, and the
   guide describes no column past the fifth parameter, so what they do is unknown
   (`analysis/findings/corpus-module-wiring.md` S9). The merged device plan covers them as DT14.
- `[G]` `docs/EaganMatrixUserGuide.txt:3399-3400` gives Live mode a 312.5 Hz fundamental for
   data recorded into the SummedDelay; whether the same figure applies to a VoiceDelay source is
   not stated, and ModMan's equivalent sentence names a different frequency entirely `[G]`
   `docs/EaganMatrixUserGuide.txt:3477-3479`.
- `[C]` The blank-`H` device test still stands, because the guide defines grain duration as
   inversely proportional to `H` and gives no behaviour at zero
   (`analysis/findings/modules-unfilled-checklist.md` gap 3); it is re-aimed at **column 3**,
   which is where `H` actually is.

---

## 1. What every column means

**The column positions below are the corpus's.** The guide lists five parameters in sequence
with no column numbers `[G]` `docs/EaganMatrixUserGuide.txt:3328-3352`; the corpus shows the
index and dilation parameters on **columns 7 and 8**, not 4 and 5 `[C]` - occupancy is c1 100%,
c2 100%, c3 100%, c4 4%, c5 3%, c6 0%, **c7 100%, c8 100%** over 120 bank slots, and ModMan,
whose numbering the guide does give, puts the same two parameters at 7 and 8
(`analysis/findings/corpus-module-wiring.md` S9).

| Col (A / B / C) | Label | Meaning | Source |
|---|---|---|---|
| 1 (27 / 35 / 43) | `A` | "Amplitude of the HarMan. If a new grain is triggered, this determines its amplitude. If the amplitude is 0, no grains are generated (conserves DSP processing)." | `[G]` `docs/EaganMatrixUserGuide.txt:3328-3330` |
| 2 (28 / 36 / 44) | `F` | "Frequency of HarMan's fundamental, in kHz. This is the frequency at which new grains are triggered." | `[G]` `docs/EaganMatrixUserGuide.txt:3332-3334` |
| 3 (29 / 37 / 45) | `H` | Harmonic truncation, in kHz: "the grain's duration will be inversely proportional to this value. As H increases, low harmonics are truncated, and high harmonics intensify. Try .16 times the S column value." | `[G]` `docs/EaganMatrixUserGuide.txt:3336-3340` |
| 7 (33 / 41 / 49) | `I` | Index into the selected data, 0 to 1. In Live mode: "If I is from 0 to 1, I is relative to the write-index point of the circular delay buffer. -1 aligns to most recent grain positions with 2*H, and -2 aligns to most recent grains only when S>1." | `[G]` `docs/EaganMatrixUserGuide.txt:3342-3346`, position `[C]` (`analysis/findings/corpus-module-wiring.md` S9) |
| 8 (34 / 42 / 50) | `S` | Spectral dilation: "1 means no change to spectral envelope (i.e. step through grain data normally), >1 stretches spectral envelope (i.e. increased step rate through grain data), <1 compresses spectral envelope. Usually scale the H column value by the same amount." | `[G]` `docs/EaganMatrixUserGuide.txt:3348-3352`, position `[C]` (`analysis/findings/corpus-module-wiring.md` S9) |
| 4, 5, 6 | - | Not described, and almost never written | `[C]` 4%, 3% and 0% of 120 bank slots (`analysis/findings/corpus-module-wiring.md` S9) |

A second HarMan is available in bank B or bank C `[G]`
`docs/EaganMatrixUserGuide.txt:3354`.

What HarMan is, in the guide's own words `[G]` `docs/EaganMatrixUserGuide.txt:3358-3362`,
verbatim: "HarMan uses precision granular techniques to traverse and manipulate a very short
(150ms) sample... The sample is so short that it only provides 12 different `raw` grains; each
grain has its own unique spectrum." Users cannot load their own sets `[G]`
`docs/EaganMatrixUserGuide.txt:3359-3360`.

## 2. Units, useful ranges, blank-column behaviour

| Column | Units and neutral | What blank (= 0) does | Source |
|---|---|---|---|
| `A` | linear amplitude | **silent and free** - no grains are computed | `[G]` `docs/EaganMatrixUserGuide.txt:3328-3330` |
| `F` | **kHz** | no grain triggering, therefore silence | `[G]` `docs/EaganMatrixUserGuide.txt:3332-3334` |
| `H` | **kHz** | **not neutral and not defined**: grain duration is inversely proportional to `H`, so zero implies an unbounded duration and the guide says nothing about it | `[G]` `docs/EaganMatrixUserGuide.txt:3336-3338` |
| `I` | 0..1, plus -1 and -2 in Live mode | index 0, the start of the set: valid, but static - a constant index does not evolve `[I]`, the inference being that an index column that never moves never traverses |
| `S` | multiplier, **neutral = 1** | **not neutral**: zero is a zero step rate through the grain data, not "no dilation" | `[G]` `docs/EaganMatrixUserGuide.txt:3348-3350` |

**Blank-column verdict.** `S` blank is a trap because its neutral is 1, `H` blank is undefined,
`A` and `F` blank are silent, and only `I` is safely blank `[G]`
`docs/EaganMatrixUserGuide.txt:3328-3352`.

`[C]` The corpus writes all five of `A`, `F`, `H`, `I` and `S` in 120 of 120 bank slots, with
no exception (`analysis/findings/corpus-module-wiring.md` S9). `[I]` The inference is that the
factory treats every one of them as mandatory, which is the strongest available statement about
blank behaviour short of a device test.

## 3. Spectral sets and Live mode

Which source a HarMan plays is the spectral-set selector `[G]` `docs/HakenMidi.h:1603-1604`;
the 38 values and the id are `index.md`, shared fact 6. This card states only what the choice
does to a HarMan.

- The flash sets are 150 ms instrument samples, and a well-built preset is bound to the one it
   uses `[G]` `docs/EaganMatrixUserGuide.txt:3366-3368`, verbatim: "the intricacies of a
   well-designed HarMan preset is tied to the particular Spectral Set it uses; it won't be
   possible to get the same results with a different Spectral Set."
- Live mode granulates what a VoiceDelay or SummedDelay recorded `[G]`
   `docs/HakenMidi.h:1605`. The practical recipe the guide gives: left audio input into a
   VoiceDelay with a 50 ms delay, the HarMan set to Live, HarMan output to the stereo sum, and
   each HarMan parameter on a macro `[G]` `docs/EaganMatrixUserGuide.txt:3389-3392`.
- Live mode is silent unless the input level is up `[G]`
   `docs/EaganMatrixUserGuide.txt:3393-3394`, verbatim: "When using Live From Delay acting on an
   audio input, remember to bring up the Audio Input Level Control of the Live From Delay
   function will have no effect."

## 4. Properties-panel settings and MCP reachability

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type, including bank C | `idBankA/B/C`, value 6 | **yes** - `set_bank_type` `[G]` `eagan_mcp/setup.py:227` |
| All five columns | matrix cells | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| **Spectral set, or Live** | the spectral-set id (`index.md`, shared fact 6) | **read-only, decoded by name**: `get_setup` returns `bank_params.A.spectral_set` as the set's name `[G]` `eagan_mcp/setup.py:186-195`. **No tool writes it**, so a HarMan preset can be explained but not re-aimed |
| Delay maximum time, which Live mode depends on | the delay time-select id (`index.md`, shared fact 7) | **read-only and undecoded** as `delay_time_select_raw` `[G]` `eagan_mcp/setup.py:216`. No write tool |
| Hold on the feeding delay | that delay's own matrix column | **yes**, it is a matrix cell `[G]` `docs/EaganMatrixUserGuide.txt:3404-3405` |
| Column-mode toggles | **no HarMan entry** | not applicable `[G]` `docs/HakenMidi.h:1579-1589` |

`[I]` The read side of the spectral set closed when `get_setup` gained its name table, so the
older statement that a HarMan preset is unexplainable no longer holds - the inference is from
reading the shipped decoder, not from the device. The write side is now ranked:
**`tools_spec.md` `T22` (`set_module_option`) covers writing an arbitrary `s_Mat_Poke` id**,
and the `T` scheme runs to twenty-two ranks, not twenty; the ranked list that puts the
spectral-set id second is `analysis/findings/modules-mcp-reachability.md` section 5 rank 2,
which `T22` folds into the `T` namespace. `T4` is the rank that would carry the decoded set
into `get_matrix`'s own labels.

## 5. DSP cost class

**Heavy relative to the other granulators, and gated by `A`.** The guide's own comparison puts
HarMan at "a variable number up to 64 or more" grains per voice with raised-cosine windows,
sub-sample-accurate start times and interpolation between neighbouring periods, against the
delay-tap shifter's "only two grains per voice", triangle-shaped, "always 50% overlapped", with
uninterpolated grain data, "so it is a very unrefined but processor efficient" option `[G]`
`docs/EaganMatrixUserGuide.txt:2209-2213`.

`[I]` The documented cost ladder for granular work is therefore shifter, then SineSpray, then
HarMan - the inference combines that comparison with the guide's remark that SineSpray is the
right module for randomised-grain effects `[G]` `docs/EaganMatrixUserGuide.txt:3370`.

## 6. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`Touch Reed T` - the decisive `H`-to-`S` ratio, and a wheel crossfade between two banks `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: A = HarMan ; B = HarMan ; osc 5 = Shelving High Pass
Bank A 1 (A) <- Direct + = 0.33, Direct x = F
Bank A 2 (F) <- Direct + = X,    Direct x = Q
Bank A 3 (H) <- Direct + (2) = 0.08, Direct x = G     <-- 0.08 x G
Bank A 7 (I) <- Noise = M, Direct + = A, Direct + (2) = B
Bank A 8 (S) <- Direct + (2) = 0.64, Direct x = G     <-- 0.64 x G
   (bank B identical except Bank B 3 uses 0.05; the spectral set each bank plays is
    not carried in the shipped wiring block)
Master SL/SR <- Osc 5 = z^2, Bank A = O, Bank B = N, Direct x = K
  G = W Constant 0.25 x macro i ; anc + formula H       (the shared H/S scaler)
  N = Y = 0 -> 1.0 SqRoot    O = Y = 1.0 -> 0 Squared   (the wheel crossfades the two banks)
```

`[C]` 0.08 divided by 0.64 is 0.125, against the guide's "Try .16 times the S column value"
`[G]` `docs/EaganMatrixUserGuide.txt:3339-3340`. Both columns multiply the same letter `G`, so
one macro moves the pair together exactly as the guide instructs `[G]`
`docs/EaganMatrixUserGuide.txt:3351-3352`. Sharing a letter between columns 3 and 8 is the
second most common shared-letter pair in the library at 88 presets (`index.md` pattern 2
covers the generic form).

`Bell Rub` and `Cycle Kalimba` - the same ratio, simpler, and the pattern to recommend `[C]`
(`factory_catalog.json`, `wiring`):

```
Bell Rub:      Bank A 3 <- Direct + = G, Direct x = 0.12 ; Bank A 8 <- Direct + = G
Cycle Kalimba: Bank A 3 <- Direct + = C, Direct x = 0.10 ; Bank A 8 <- Direct + = C
```

`[C]` One letter in both columns, with the ratio as a bare constant on the multiply row of
column 3. `Bell Rub` also shows the index column driven from two letters at once, an envelope
and an LFO, on two different Direct rows.

Factory leads the guide names: `Bell Rub`, `Cycle Kalimba`, `GrainSilo Woodwind`,
`SiloString Pizz`, `Spinning Duet` `[G]` `docs/EaganMatrixUserGuide.txt:3416-3420`; also
`Tibetan Throat Stick`, a HarMan of VoiceDelay data into a BiqMouth `[G]`
`docs/EaganMatrixUserGuide.txt:2878-2879`. `[C]` `VlaVlaCelBass` is in the corpus as
`VlnVlaCelBass` and `Vln Vla Cel Bass *`.

## 7. Known traps

1. **`S` neutral is 1, not 0.** A blank dilation column is a zero step rate, not "no change"
   `[G]` `docs/EaganMatrixUserGuide.txt:3348-3350`.
2. **`H` must track `S`** - "Try .16 times the S column value" and "Usually scale the H column
   value by the same amount" `[G]` `docs/EaganMatrixUserGuide.txt:3339-3340`, `:3351-3352`.
   Changing one without the other breaks the grain-to-dilation relationship.
3. **HarMan's ratio is about 0.16; SineSpray's is 0.5.** Same column letter, different constant
   `[G]` `docs/EaganMatrixUserGuide.txt:3339-3340` against `[G]`
   `docs/EaganMatrixUserGuide.txt:3200`.
4. **Saving with Hold active silences the preset on reload** `[G]`
   `docs/EaganMatrixUserGuide.txt:3411-3412`, verbatim: "save the preset in this state (Hold
   active) and reload it, the HarMan will make no sound as there is no initial data in the
   delay buffer to work on." The guide's own remedy is to put Hold on a pedal through a macro
   `[G]` `docs/EaganMatrixUserGuide.txt:3412-3413`.
5. **A HarMan preset is tied to its spectral set** `[G]`
   `docs/EaganMatrixUserGuide.txt:3366-3368`, so changing the set is not a variation, it is a
   different instrument.
6. **Live mode needs the audio input level raised** or it is silent `[G]`
   `docs/EaganMatrixUserGuide.txt:3393-3394`.
7. **Two manipulators plus a bank C delay are forced onto one spectral set**; `index.md` shared
   fact 6 owns the rule `[G]` `docs/EaganMatrixUserGuide.txt:3491-3493`.
8. **Do not expect classic granular randomness** `[G]`
   `docs/EaganMatrixUserGuide.txt:3368-3370`, verbatim: "you will not hear the traditional sonic
   effects of randomized grains with HarMan... and the SineSpray is better suited for that
   sonic purpose."
9. **The negative index values only work in Live mode**, and -2 only when the dilation is above
   1 `[G]` `docs/EaganMatrixUserGuide.txt:3343-3346`.
10. **HarMan shares the one delay memory** with the delays, WaveBank and ModMan `[G]`
    `docs/EaganMatrixUserGuide.txt:4157`; `index.md` shared fact 7 owns the budget.
11. **Aim a blank-column or wiring question at column 3, 7 or 8, not 4 and 5.** The guide's
    table order is not the column order `[C]`
    (`analysis/findings/corpus-module-wiring.md` S9).
