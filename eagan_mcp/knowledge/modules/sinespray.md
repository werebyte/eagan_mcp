# Module card - SineSpray (sine grains)

Bank wire value **4**: bank A, bank B, or bank C as `SineSpray (alias of B)` `[G]`
`docs/HakenMidi.h:1570`. Guide section 6.7, "Multipurpose Banks: SineSpray (Sine Grains)"
`[G]` `docs/EaganMatrixUserGuide.txt:3182`. Card schema, shared facts, the module-name
spelling and what the alias form means: `index.md`, which this card references and never
restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

## TL;DR

The shortest bank in the guide: five described columns, no Properties panel, no assignable
columns `[G]` `docs/EaganMatrixUserGuide.txt:3186-3211`. Grains are triggered at the rate of
column `F`, and the perceived **pitch is `F`, not the sine frequency inside the grain** `[G]`
`docs/EaganMatrixUserGuide.txt:3214-3215` - the single most counter-intuitive fact about this
module.

Column `A` at zero stops grain generation entirely and conserves DSP `[G]`
`docs/EaganMatrixUserGuide.txt:3187-3189`, which makes it the cheapest gate in the bank family.

`[I]` Everything here is tool-reachable, because there is nothing but matrix cells: no property
stream, no column-mode toggle and no bank-param entry names SineSpray `[G]`
`docs/HakenMidi.h:1579-1597`.

`[C]` 18 of the 668 factory presets run a SineSpray (`census.json`,
`modules_used_including_defaults`).

## Key Decisions

- Carded as fully reachable, since no property stream, column-mode toggle or bank-param value
   applies to this bank type `[G]` `docs/HakenMidi.h:1579-1597`.
- The physical column positions are taken from the corpus, not from the guide's table order,
   because the two disagree and the corpus is cell-level evidence - see section 1 `[C]`
   (`analysis/findings/corpus-module-wiring.md` S6).

## Open Questions / Risks

- `[C]` Columns 5, 6 and 7 are written by **no preset of the 19 measured bank slots**, so
   whether they are inert or merely unused is unknown; the guide describes no column 6..8 at all
   (`analysis/findings/corpus-module-wiring.md` S6). The merged device plan covers it as DT15,
   one of the absence-means-default reads.
- `[G]` `docs/EaganMatrixUserGuide.txt:3203-3205` gives an explicit range only for `P`; the
   other four columns are given units but no bounds.

---

## 1. What every column means

**The column positions below are the corpus's, not the guide's table order.** The guide lists
five parameters in sequence and gives no column numbers `[G]`
`docs/EaganMatrixUserGuide.txt:3186-3209`; the corpus puts the sine-frequency parameter on
**column 8**, not column 5 `[C]` - occupancy pairs as c1 100%, c2 100%, c3 100%, c4 42%,
**c5 0%, c6 0%**, c7 10%, **c8 100%** over 19 bank slots, which is only consistent with the
layout `1 A, 2 F, 3 H, 4 P, 8 S` (`analysis/findings/corpus-module-wiring.md` S6). Writing the
sine frequency into column 5 is a silent no-op.

| Col (A / B / C) | Label | Meaning | Source |
|---|---|---|---|
| 1 (27 / 35 / 43) | `A` | Amplitude: "If a new grain is triggered, this determines its amplitude. If the amplitude is 0, no grains are generated (conserves DSP processing)." | `[G]` `docs/EaganMatrixUserGuide.txt:3187-3189` |
| 2 (28 / 36 / 44) | `F` | "Frequency of SineSpray's fundamental, in kHz. This is the frequency at which new grains are triggered. It is common to add randomness to this value to create audible clusters within the SineSpray." | `[G]` `docs/EaganMatrixUserGuide.txt:3191-3193` |
| 3 (29 / 37 / 45) | `H` | Harmonic truncation, in kHz: "Small H creates long sine grains within the spray. Larger H shortens grains and adds harmonics. As H increases, high harmonics increase, and low harmonics are truncated. Try half the S column value." | `[G]` `docs/EaganMatrixUserGuide.txt:3196-3200` |
| 4 (30 / 38 / 46) | `P` | Phase of the sinusoid in a newly triggered grain, "Values: 0..0.9999 (0 to 359.9) degrees" | `[G]` `docs/EaganMatrixUserGuide.txt:3203-3205` |
| 8 (34 / 42 / 50) | `S` | Sine frequency in kHz - the frequency of the sinusoid **inside** the grain | `[G]` `docs/EaganMatrixUserGuide.txt:3207-3209`, position `[C]` (`analysis/findings/corpus-module-wiring.md` S6) |
| 5, 6, 7 | - | Not described, and written by no factory preset | `[C]` 0%, 0% and 10% of 19 bank slots (`analysis/findings/corpus-module-wiring.md` S6) |

A second SineSpray is available in bank B or bank C `[G]`
`docs/EaganMatrixUserGuide.txt:3211`.

## 2. Units, useful ranges, blank-column behaviour

| Column | Units | What blank (= 0) does | Source |
|---|---|---|---|
| `A` | linear amplitude | **silence, and zero DSP cost** - documented as a deliberate optimisation, so `A` is the right place for an amplitude envelope | `[G]` `docs/EaganMatrixUserGuide.txt:3187-3189` |
| `F` | **kHz** | no grain triggering, therefore silence | `[G]` `docs/EaganMatrixUserGuide.txt:3191-3192` |
| `H` | **kHz** | long grains with few harmonics - the guide's "small H" end, not a broken state | `[G]` `docs/EaganMatrixUserGuide.txt:3196-3198` |
| `P` | 0..0.9999 = 0..360 degrees | 0 degrees, benign | `[G]` `docs/EaganMatrixUserGuide.txt:3203-3205` |
| `S` | **kHz** | DC inside the grain `[I]` - the inference is that a sinusoid at zero frequency is a constant, so a blank `S` is degenerate rather than neutral |

**Blank-column verdict.** `A` blank is silent and free, `F` blank is silent, `S` blank is
degenerate, and `H` and `P` blank are musically valid `[G]`
`docs/EaganMatrixUserGuide.txt:3187-3209`. SineSpray has no blank-is-destructive column.

**The pitch rule**, which is this card's most important line `[G]`
`docs/EaganMatrixUserGuide.txt:3214-3215`, verbatim: "Typically, the frequency of the resulting
sound is the frequency of Sine Spray's fundamental (sine grain triggering frequency), not the
frequency of the sinusoid within the grain." `[I]` So pitch tracking goes on `F` and `S` is a
timbre control - the direct inference from the quoted rule is that a builder who puts the pitch
code on `S` gets a drone at whatever `F` happens to be.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type, including bank C | `idBankA/B/C`, value 4 | **yes** - `set_bank_type` accepts `"SineSpray"` for A and B and the alias form for C `[G]` `eagan_mcp/setup.py:227-234` |
| All five columns | matrix cells 27-34 / 35-42 / 43-50 | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| Properties panel | none documented | not applicable `[G]` `docs/EaganMatrixUserGuide.txt:3186-3211` |
| Column-mode toggles | **no SineSpray entry** | not applicable `[G]` `docs/HakenMidi.h:1579-1589` |
| Bank-param id | **no SineSpray entry**; its two documented meanings are biquad deflation and a WaveBank waveform | not applicable `[G]` `docs/HakenMidi.h:1591-1597` |

`[I]` SineSpray is therefore fully reachable, and with BiqMouth it is the easiest bank for an
agent to drive end to end today - the inference is that a module with no non-matrix state
puts nothing out of a tool's reach. **This card states no tool limit**, because there is nothing here that a
`T<n>` rank would unblock.

## 4. DSP cost class

**Light to medium, and explicitly gated by `A`**: at `A` = 0 no grains are generated at all
`[G]` `docs/EaganMatrixUserGuide.txt:3187-3189`. The guide gives no per-grain figure `[I]` -
the inference available is only a relative one.

The guide's own comparison puts SineSpray between the two other granulators: the delay-tap
shifter has "only two grains per voice" and is "very unrefined but processor efficient" `[G]`
`docs/EaganMatrixUserGuide.txt:2209`, `:2213`, while HarMan has "a variable number up to 64 or
more" `[G]` `docs/EaganMatrixUserGuide.txt:2209-2210`. For randomised-grain textures the guide
says outright that "the SineSpray is better suited for that sonic purpose" `[G]`
`docs/EaganMatrixUserGuide.txt:3370`.

## 5. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`Bird Echoer` - the cleanest template for the module `[C]` (`factory_catalog.json`, `wiring`):

```
bank: A = SineSpray ; C = SummedDelay ; recirc = Modulated Delay
Bank A 1 (A) <- Direct + = F
Bank A 2 (F) <- Direct + = 1,    Direct x = E
Bank A 3 (H) <- Direct + = 0.25, Direct x = E
Bank A 8 (S) <- Direct + = A, Direct - = C, Direct x = E
Dry L / Dry R <- Bank A = 1 ;  Master/Dry mix <- Direct + = 0.5
Master SL <- Tap 1 = 1 ;  Master SR <- Tap 2 = 1   (rows 9/10 are delay taps here)
  E = X = -1.00 -> 1.00 x1 kHz      (pitch, multiplied into F, H and S alike)
  F = Z = 0 -> 1.0 x0.1             (amplitude from pressure)
  C = W*(X+Y+Z), W = SG1 -0.2 x10 [Ramp Down] ; Y = 0 -> 1.0 Squared  (S dips on attack)
```

`[C]` All three pitch-dependent columns take the **same** pitch letter on `Direct x`, with
the ratios set by the constants on `Direct +`: `F` at 1 x E and `H` at 0.25 x E. That
realises the guide's "Try half the S column value" rule for `H` `[G]`
`docs/EaganMatrixUserGuide.txt:3200` and is the construction to copy (`index.md` pattern 2
covers the generic form). Note also that this preset writes column 8, not column 5, for the
sine frequency.

`Bird Whistler Wbl` is the richest SineSpray in the corpus at nine cells, and `Space Jaw` is
the only preset with a SineSpray in **both** bank A and bank B `[C]`
(`factory_catalog.json`, `wiring`).

Factory leads the guide names, all present in the 668: `Bird Echoer`, `Bird Whistler`,
`Harmonic Break`, `Sonogram`, `SpaceJaw`, `Three Cycles` `[G]`
`docs/EaganMatrixUserGuide.txt:3218-3227`. `[C]` In the corpus they are spelled
`Bird Whistler Wbl` and `Space Jaw`.

## 6. Known traps

1. **Pitch lives on `F`, not `S`** `[G]` `docs/EaganMatrixUserGuide.txt:3214-3215`.
2. **`S` is on column 8, not column 5.** A write aimed at column 5 lands on a column no factory
   preset uses and changes nothing audible `[C]` (`analysis/findings/corpus-module-wiring.md`
   S6).
3. **`H` should track `S`** - "Try half the S column value" `[G]`
   `docs/EaganMatrixUserGuide.txt:3200`. Changing `S` without changing `H` changes the grain
   length and so the whole texture.
4. **`A` = 0 is a true bypass, not just silence**: grains stop being computed, so a SineSpray
   can look broken purely because `A` carries no formula `[G]`
   `docs/EaganMatrixUserGuide.txt:3187-3189`.
5. **Randomness on `F` is the idiom, not a hack** `[G]`
   `docs/EaganMatrixUserGuide.txt:3192-3193`, verbatim: "It is common to add randomness to this
   value to create audible clusters within the SineSpray."
6. **A bank C SineSpray is an alias of bank B's, not an independent third one** `[G]`
   `docs/HakenMidi.h:1570`; `index.md` owns what the alias form means.
7. **Do not assume columns 5..7 are inert.** They are undescribed and unused, which is not the
   same as harmless `[C]` (`analysis/findings/corpus-module-wiring.md` S6).
