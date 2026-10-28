# Module card - BiqMouth (vocal formants)

Bank wire value **2**, bank A or bank B `[G]` `docs/HakenMidi.h:1563`. Guide section 6.5,
"Multipurpose Banks: BiqMouth (Vocal Formants)" `[G]`
`docs/EaganMatrixUserGuide.txt:2767`. Card schema, shared facts and the module-name spelling:
`index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle and the vowel symbols with
diacritics; this card writes `In` for the input and uses the ASCII vowel key in section 3
`[G]` `docs/EaganMatrixUserGuide.txt:2772`, `:2831`.

## TL;DR

Five biquad formant filters over an audio input, with one `Sh` column morphing through a table
of male and female mouth shapes `[G]` `docs/EaganMatrixUserGuide.txt:2771-2777`. The columns
are fixed; there is no assignable-column list here (`index.md`, shared fact 2).

This is the card that carries the project's canonical blank-is-not-neutral case: `sB` is a
**multiplier** whose neutral is 1.0, so a blank column multiplies every formant bandwidth by
zero `[G]` `docs/EaganMatrixUserGuide.txt:2788-2789`, and the device finding says the same
`[D]` `RECIPES.md:162-163`, 2026-10-25, fw 10.81.

Almost all of BiqMouth's sound is in matrix cells, which makes it the **most tool-complete
bank** `[I]` - the inference is that a module whose only non-matrix control is one deflation
limit is as reachable as the matrix itself.

`[C]` 45 of the 668 factory presets run a BiqMouth (`census.json`,
`modules_used_including_defaults`).

## Key Decisions

- The `sB` trap is recorded with both a device citation and a guide citation, because the guide
   states it independently - it is not a surprise, it is an unread line `[G]`
   `docs/EaganMatrixUserGuide.txt:2788-2792`.
- The full mouth-shape selection chart is reproduced here, because adjacent-value morphing is
   the whole point of the `Sh` column and the chart is the only way to choose a morph path `[G]`
   `docs/EaganMatrixUserGuide.txt:2849-2853`.

## Open Questions / Risks

- `[G]` `docs/EaganMatrixUserGuide.txt:2775-2776` gives `Sh` as 0 to 4.5; device practice
   reaches 4.8. Both stand - see the conflict block in section 2.
- `[G]` `docs/EaganMatrixUserGuide.txt:2823-2825` documents no BiqMouth Properties panel beyond
   the Deflation Limit, and the header's property block is mode-shaped and partial-shaped rather
   than formant-shaped `[G]` `docs/HakenMidi.h:1726-1747`, so whether any of it applies to
   BiqMouth is **not stated**.
- `[C]` The blank-`sF` device test is **retired**, not answered: the factory preset's `sF`
   column evaluates near 1.0 rather than sitting at the formula constant 0.5, so the apparent
   disagreement was a category mismatch rather than a device question
   (`analysis/findings/modules-unfilled-checklist.md` gap 1).

---

## 1. What every column means

| Col (bank A / bank B) | Label | Meaning | Source |
|---|---|---|---|
| 1 (27 / 35) | `In` | "Audio input into the vocal formant filter bank, a series of five biquad formant filters" | `[G]` `docs/EaganMatrixUserGuide.txt:2771-2773` |
| 2 (28 / 36) | `Sh` | "A series of mouth shapes, selectable 0 to 4.5 at 0.1 intervals with smooth morphing between adjacent shapes" | `[G]` `docs/EaganMatrixUserGuide.txt:2775-2777` |
| 3 (29 / 37) | `sF` | Frequency spread: "Multiplier on formant frequencies, 1.0 = normal" | `[G]` `docs/EaganMatrixUserGuide.txt:2780` |
| 4 (30 / 38) | `oF` | Frequency offset: "Offset on formant frequencies, 0.0 (blank column) = normal" | `[G]` `docs/EaganMatrixUserGuide.txt:2784` |
| 5 (31 / 39) | `sB` | Bandwidth spread: "Formant bandwidth multiplier, 1.0 means each formant has default bandwidth, > 1.0 means formants farther from Center have increased bandwidth, < 1.0 means formants farther from Center have decreased bandwidth" | `[G]` `docs/EaganMatrixUserGuide.txt:2788-2792` |
| 6 (32 / 40) | `C` | Centre: "0 means first formant is center, 0.625 means last (5th) formant is center" | `[G]` `docs/EaganMatrixUserGuide.txt:2794-2796` |
| 7 (33 / 41) | `sA` | Amplitude spread: 0 = no amplitude scaling, >0 = formants farther from Centre are quieter | `[G]` `docs/EaganMatrixUserGuide.txt:2798-2802` |
| 8 (34 / 42) | - | Not used by BiqMouth; the guide's table stops at seven | `[C]` written in 0% of 36 measured bank slots (`analysis/findings/corpus-module-wiring.md` S4) |

The column list is independently device-verified as "input, Sh mouth shape, sF formant
frequency multiplier, oF formant frequency offset, sB bandwidth multiplier, C center, sA
amplitude spread" at bank A 27-33 and bank B 35-41 `[D]` `RECIPES.md:160-161`, 2026-10-25,
fw 10.81. A second BiqMouth is available in bank B `[G]`
`docs/EaganMatrixUserGuide.txt:2804`.

## 2. Units, useful ranges, blank-column behaviour

| Column | Neutral value | What blank (= 0) means | Source |
|---|---|---|---|
| `Sh` | none - it is an index | shape index 0, a valid vowel, so blank is harmless here | `[G]` `docs/EaganMatrixUserGuide.txt:2834` |
| `sF` | **1.0** | multiplies every formant frequency by zero - **not neutral** | `[G]` `docs/EaganMatrixUserGuide.txt:2780` |
| `oF` | **0.0** | neutral, and the guide says so in the column text itself | `[G]` `docs/EaganMatrixUserGuide.txt:2784` |
| `sB` | **1.0** | multiplies every formant bandwidth by zero - razor-thin formants | `[G]` `docs/EaganMatrixUserGuide.txt:2788-2789` and `[D]` `RECIPES.md:162-163`, 2026-10-25, fw 10.81 |
| `C` | 0 = the first formant is centre | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:2794-2796` |
| `sA` | 0 | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:2798-2800` |

The device statement of the `sB` trap, verbatim: "NEVER leave sB empty: blank = 0 = razor-thin
formants. They ring as fixed pitches that do not follow the keys and no vowel is heard
(tested)." `[D]` `RECIPES.md:162-163`, 2026-10-25, fw 10.81.

**Never leave bank B column 37 (`sF`) or column 39 (`sB`) blank** - the two trap columns in the
bank where BiqMouth most often sits `[C]`: both are written in 36 of 36 measured BiqMouth bank
slots, alongside `Sh`, with no exception in the corpus
(`analysis/findings/corpus-module-wiring.md` S4).

`[C]` Measured column occupancy over 36 BiqMouth bank slots: c1 94%, **c2 100%, c3 100%**,
c4 72%, **c5 100%**, c6 16%, c7 16%, c8 0%
(`analysis/findings/corpus-module-wiring.md` S4).

```
RESOLVED, not a conflict: what the factory sB value actually is
  device [D]: "Factory base: sB 0.5 (up to 2.5 on macro iv)" - RECIPES.md:162-164,
              2026-10-25, fw 10.81
  docs   [G]: "1.0 means each formant has default bandwidth"
              - docs/EaganMatrixUserGuide.txt:2788-2789
  corpus [C]: in `BiqMouth - Basic` the sB cell holds one letter whose W is a constant 0.2
              scaled x10 by macro iv and whose Y heights are both 0.5, so the EVALUATED
              column is 0.5 + 2 x macro, not 0.5. With the preset's stored macro iv the
              column sits near 1.26.
  resolution: the two never disagreed. The device note's 0.5 is a formula constant; the
              guide's 1.0 is an evaluated column value. Aim the EVALUATED sB near 1.0..1.3.
              The filed device test is struck.
```

```
CONFLICT: the Sh range
  docs   [G]: "selectable 0 to 4.5 at 0.1 intervals" and a chart whose last row stops at 4.5
              - docs/EaganMatrixUserGuide.txt:2775-2776, :2867
  device [D]: "Sh mouth shape (0..4.8)", with a factory formula reaching 4.8
              - RECIPES.md:160, :164, 2026-10-25, fw 10.81
  effect: a formula scaled to reach 4.8 goes past the published chart. It works on the
          device, but which vowel appears between 4.6 and 4.8 is undefined, so an agent
          cannot predict what it gets there.
  resolution: both stand. Use 0..4.5 for predictable vowels. The merged device plan covers
          it as DT12, which walks Sh in steps and has the owner name the vowels.
```

## 3. Mouth shapes

ASCII vowel key for this card, since the guide prints the symbols with diacritics `[G]`
`docs/EaganMatrixUserGuide.txt:2831-2846`: `a:` = Father, `a-` = Made, `oo` = Food, `o-` = Go,
`a` = Pad, `e` = Merry, `uh` = Mud. `M:` is a male shape, `F:` a female one.

Primary values `[G]` `docs/EaganMatrixUserGuide.txt:2831-2846`:

| Shape | ASCII symbol | Male primary `Sh` | Female primary `Sh` | Source |
|---|---|---|---|---|
| Father | `a:` | 0 | 3.5 | `[G]` `docs/EaganMatrixUserGuide.txt:2834` |
| Made | `a-` | 0.1 | 3.6 | `[G]` `docs/EaganMatrixUserGuide.txt:2836` |
| Food | `oo` | 0.2 | 3.7 | `[G]` `docs/EaganMatrixUserGuide.txt:2838` |
| Go | `o-` | 0.3 | 3.8 | `[G]` `docs/EaganMatrixUserGuide.txt:2840` |
| Pad | `a` | 0.4 | none | `[G]` `docs/EaganMatrixUserGuide.txt:2842` |
| Merry | `e` | 0.5 | 3.9 | `[G]` `docs/EaganMatrixUserGuide.txt:2844` |
| Mud | `uh` | 0.6 | none | `[G]` `docs/EaganMatrixUserGuide.txt:2846` |

Full selection chart. Shapes are repeated at different `Sh` values so that any two you want to
morph between can be made adjacent `[G]` `docs/EaganMatrixUserGuide.txt:2849-2853`, verbatim:
"Mouth shapes have been repeated in different combinations to allow for a maximum of adjacent
morphing possibilities."

| `Sh` | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **0** | M:a: | M:a- | M:oo | M:o- | M:a | M:e | M:uh | M:a: | M:oo | M:a | `[G]` `docs/EaganMatrixUserGuide.txt:2859` |
| **1** | M:uh | M:a- | M:o- | M:e | M:a: | M:o- | M:uh | M:a | M:a: | M:e | `[G]` `docs/EaganMatrixUserGuide.txt:2861` |
| **2** | M:a- | M:a | M:uh | M:oo | M:e | F:a: | M:a: | F:a- | M:a- | F:oo | `[G]` `docs/EaganMatrixUserGuide.txt:2863` |
| **3** | M:oo | F:o- | M:o- | F:e | M:a | F:a: | F:a- | F:oo | F:o- | F:e | `[G]` `docs/EaganMatrixUserGuide.txt:2865` |
| **4** | F:a: | F:oo | F:e | F:a- | F:o- | F:a: | - | - | - | - | `[G]` `docs/EaganMatrixUserGuide.txt:2867` |

To build a vowel wah, pick a start and an end that are adjacent in the chart. The
device-verified build uses `Sh = 2.3` (`M:oo` at row 2, column .3) plus a mod-wheel term
running 0 to -0.2, walking downwards through `2.2 M:uh` and `2.1 M:a` `[D]` `CLAUDE.md:131-133`,
2026-10-25, fw 10.81.

## 4. Properties-panel settings and MCP reachability

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankA/B` | **yes** - `set_bank_type("B", "BiqMouth")` `[G]` `eagan_mcp/setup.py:227` |
| Matrix cells 27-34 / 35-42 | the matrix | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| Deflation Limit 0..7 or IIT | the bank-param id (`index.md`, shared fact 4) | **read-only, decoded by name** as `bank_params.B.param` `[G]` `eagan_mcp/setup.py:190`. No tool writes it; **`tools_spec.md` `T22` (`set_module_option`) covers writing it**, and the ranked list that names it is `analysis/findings/modules-mcp-reachability.md` section 5 rank 1, which `T22` folds into the `T` namespace |
| Anything else | - | the guide documents no further Properties panel for BiqMouth `[G]` `docs/EaganMatrixUserGuide.txt:2823-2825` |

`[I]` BiqMouth is therefore the most tool-complete bank: its sound is almost entirely in matrix
cells that `set_matrix_point` already writes - the inference is that the one unreachable
control, the Deflation Limit, "has no effect under normal playing conditions" `[G]`
`docs/EaganMatrixUserGuide.txt:2823-2824`, so nothing audible is out of reach.

## 5. DSP cost class

**Not documented.** The guide states no cost for BiqMouth and gives it no Reduce Polyphony
warning `[I]` - the inference from the shared engine, which the guide names as four ways to
control one set of biquad bandpass filters `[G]` `docs/EaganMatrixUserGuide.txt:2810-2811`, is
that five formant biquads cost about five modes of a BiqBank, i.e. the light end of that
module's range. That is an inference, not a figure, and the gap is filed as corpus-owned with
`get_status` as the measurement (`analysis/findings/modules-unfilled-checklist.md` gap 18).

## 6. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`BiqMouth - Basic` - one macro per parameter column, and the trap avoided twice `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: A = WaveBank ; B = BiqMouth
Bank A 1 <- Direct + = z^2
Bank A 2..5 <- Direct + = X, Direct + (2) = A / B / C / D, Direct - = 0.001..0.004
Bank B 1       <- Bank A = 0.25
Bank B 2 (Sh)  <- Direct + = E       Bank B 5 (sB) <- Direct + = H
Bank B 3 (sF)  <- Direct + = F       Bank B 6 (C)  <- Direct + = I
Bank B 4 (oF)  <- Direct + = G       Bank B 7 (sA) <- Direct + = J
Master SL/SR   <- Bank B = 0.5
  E = W Constant 0.48 x10 x macro i ; anc quantize by formula L    (Sh, quantised vowels)
  F = W Constant 0.20 x10 x macro ii ; Y = 0.5 -> 0.5              (sF, about 1.02)
  H = W Constant 0.20 x10 x macro iv ; Y = 0.5 -> 0.5              (sB, about 1.26)
```

`[C]` Two things to copy. The equal non-zero `Y` heights on `sF` and `sB` are how the factory
holds both columns near their neutral 1.0 (`index.md` pattern 4 covers the generic form), and
every one of the six parameter columns is on its own macro, which is why this preset is the
project's tutorial case.

`[C]` This preset's matrix decodes cell-for-cell identically from its legacy file and from a
10.81 live capture, which makes it the highest-confidence wiring block in the set.

`Choir and Ext` - vowel on the mod wheel `[C]` (`factory_catalog.json`, `wiring`):

```
bank: A = WaveBank cm1=1 ; B = BiqMouth cm2=1 ; C = SummedDelay
Bank B 1 <- Osc 4 = S, Bank A = S, Audio In L = T, Audio In R = T
Bank B 2 (Sh) <- Direct + = B, Direct + (2) = P
Bank B 3 (sF) <- Direct + = 1        Bank B 5 (sB) <- Direct + = A
Bank B 4 (oF) <- Direct + = I, Direct - = 0.5
  P = Y = 0 -> 1.0 x0.1 ; anc + formula Q     (the wheel's own contribution to Sh)
  A = Z = 0.23 -> 0.40 x10                    (sB from pressure - never blank)
```

`[C]` `Sh` takes two contributions on two different Direct rows: a pitch-tracked macro letter
on `Direct +` and a wheel-only letter on `Direct + (2)`. That is the factory answer to
"vowel on the wheel" - a second letter on a second row rather than a `Y` term inside the main
letter. Here `sF` is held at the bare constant `1`.

`Electric Guitar` is the third BiqMouth preset with a shipped wiring block, using the bank as a
cabinet-and-formant colour with `Sh` on a macro-only constant `[C]`
(`factory_catalog.json`, `wiring`).

Device-verified chain already on record: bank A WaveBank with four detuned saws feeding
**bank B BiqMouth input at .25**, then `Bank B -> Master SL/SR = .5` `[D]` `RECIPES.md:166-167`
and `CLAUDE.md:129-130`, 2026-10-25, fw 10.81.

Factory leads the guide names: `Larynx Horn`, `Mantra Voice`, `Tibetan Throat Stick` `[G]`
`docs/EaganMatrixUserGuide.txt:2875-2879`. `BiqMouth - Basic` is Utility index **7** on 10.81,
not 8 `[D]` `CLAUDE.md:122-124`, 2026-10-25, fw 10.81.

## 7. Known traps

1. **`sB` blank is zero bandwidth: razor-thin formants that ring at fixed pitches and follow no
   key.** This is the canonical blank-is-not-neutral case for the whole knowledge base
   `[D]` `RECIPES.md:162-163`, 2026-10-25, fw 10.81, with the guide agreeing `[G]`
   `docs/EaganMatrixUserGuide.txt:2788-2789`.
2. **`sF` blank is the same class of problem** - it is a multiplier whose neutral is 1.0 `[G]`
   `docs/EaganMatrixUserGuide.txt:2780`.
3. **`oF` blank is the one safe blank here**, and the guide says so in the column text; do not
   "fix" it by writing 1 `[G]` `docs/EaganMatrixUserGuide.txt:2784`.
4. **`C` tops out at 0.625, not 1**, so a formula sweeping `C` from 0 to 1 overshoots `[G]`
   `docs/EaganMatrixUserGuide.txt:2794-2796`.
5. **Morph paths must be chart-adjacent.** Sweeping `Sh` from 0 to 4 does not walk the vowels in
   any ordered way; it walks the chart's deliberately shuffled rows `[G]`
   `docs/EaganMatrixUserGuide.txt:2849-2853`.
6. **Row 4 of the chart ends at `Sh` 4.5**; above that is undefined by the chart `[G]`
   `docs/EaganMatrixUserGuide.txt:2867`.
7. `[C]` **No factory BiqMouth leaves `Sh`, `sF` or `sB` blank** - 36 of 36 bank slots write all
   three (`analysis/findings/corpus-module-wiring.md` S4). Treat that as the house rule.
