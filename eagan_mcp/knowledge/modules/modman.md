# Module card - ModMan (modal manipulator)

Bank wire value **7**, bank A or bank B only - there is no bank C value for it `[G]`
`docs/HakenMidi.h:1567`. Guide section 6.10, "Multipurpose Banks: ModMan (Modal Manipulator)"
`[G]` `docs/EaganMatrixUserGuide.txt:3428`. Card schema, shared facts and the module-name
spelling: `index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle; this card writes `In`
`[G]` `docs/EaganMatrixUserGuide.txt:3432`.

## TL;DR

HarMan's modal sibling. It takes the same 150 ms spectral sets but runs a short-time Fourier
transform at load and uses the result to drive **biquad mode amplitudes** instead of grains
`[G]` `docs/EaganMatrixUserGuide.txt:3466-3472`. So it inherits BiqBank-shaped columns plus
HarMan's index and dilation `[G]` `docs/EaganMatrixUserGuide.txt:3432-3460`.

Two of its eight columns are mode-switched, one of them three ways, and the switch is invisible
in a matrix dump `[G]` `docs/HakenMidi.h:1581`, `:1589` (`index.md`, shared fact 3 owns the
value tables). This card's own count is that **three of eight columns have a non-zero
neutral**, the highest trap density of any bank here.

The guide says the Live path "has not been explored to any great extent" `[G]`
`docs/EaganMatrixUserGuide.txt:3473-3475`.

`[C]` 45 of the 668 factory presets run a ModMan (`census.json`,
`modules_used_including_defaults`).

## Key Decisions

- Carded as "BiqBank columns plus a spectral index", because that is the mental model the
   column list supports `[G]` `docs/EaganMatrixUserGuide.txt:3432-3460` and it keeps the
   deflation guidance shared with the other biquad banks `[G]`
   `docs/EaganMatrixUserGuide.txt:3481-3486`.
- The three-way column select on column 3 is called out explicitly, because it is the only
   column-mode toggle in the whole bank family with three values `[G]`
   `docs/HakenMidi.h:1589` (`index.md`, shared fact 3 owns the table).

## Open Questions / Risks

- `[G]` `docs/EaganMatrixUserGuide.txt:3454-3456` says of the dilation column "Normally the S
   and H columns differ only by a scale factor", but ModMan's documented column list contains
   **no `H` column**. Either the sentence is carried over from HarMan or an undocumented `H`
   exists; nothing local settles it.
- `[G]` `docs/EaganMatrixUserGuide.txt:3477-3479` gives ModMan's Live period as 620.69 Hz while
   HarMan's equivalent sentence says 312.5 Hz `[G]`
   `docs/EaganMatrixUserGuide.txt:3399-3400`; neither is explained.
- `[C]` The blank-`S` device test is **retired**, not answered: the corpus writes the dilation
   column in 42 of 44 bank slots and `Harmonic Viol` writes it as the bare constant 2, which
   makes the non-zero neutral evident without a listen
   (`analysis/findings/modules-unfilled-checklist.md` gap 4).

---

## 1. What every column means

The guide gives ModMan's eight columns in order, which is why this card does not need the
corpus to place them `[G]` `docs/EaganMatrixUserGuide.txt:3432-3458`; `[C]` the corpus confirms
the map (`analysis/findings/corpus-module-wiring.md` S10).

| Col (bank A / bank B) | Label | Meaning | Source |
|---|---|---|---|
| 1 (27 / 35) | `In` | "Excitation input for all modes of the ModMan" | `[G]` `docs/EaganMatrixUserGuide.txt:3432` |
| 2 (28 / 36) | `F` | "Frequency (in kHz) for the first mode in the ModMan" | `[G]` `docs/EaganMatrixUserGuide.txt:3434` |
| 3 (29 / 37) | `sF` **or** `qF` **or** `sA` | **Three-way**, selected by clicking the heading. `sF` = 1 for harmonic spacing, >1 stretched, <1 compressed; `qF` times mode-number-squared is each mode's frequency offset; `sA` above 0 reduces the amplitude of modes farther from Centre | `[G]` `docs/EaganMatrixUserGuide.txt:3436-3440` |
| 4 (30 / 38) | `B` | "Mode bandwidth control, smaller values increase resonance" | `[G]` `docs/EaganMatrixUserGuide.txt:3442` |
| 5 (31 / 39) | `sB` **or** `qB` | **Two-way.** `sB` above 0 increases bandwidth farther from Centre, below 0 decreases it; `qB` times distance-from-Centre-squared is the bandwidth offset | `[G]` `docs/EaganMatrixUserGuide.txt:3444-3446` |
| 6 (32 / 40) | `C` | "0 means first mode is Center, 1 means the 8th mode is Center" | `[G]` `docs/EaganMatrixUserGuide.txt:3448` |
| 7 (33 / 41) | `I` | Interpolation index: "The interpolated spectrum determines the amplitude of each mode. Value 0 to 1; 0 is first spectrum in the Set, 1 is the last spectrum." | `[G]` `docs/EaganMatrixUserGuide.txt:3450-3452` |
| 8 (34 / 42) | `S` | Spectral dilation: "1 for unchanged spectral envelope, >1 stretched spectrum, <1 compressed" | `[G]` `docs/EaganMatrixUserGuide.txt:3454-3455` |

Which value columns 3 and 5 carry is set by the two column-mode toggles; the id and the value
tables are `index.md`, shared fact 3 `[G]` `docs/HakenMidi.h:1581`, `:1589`. A second ModMan is
available in bank B `[G]` `docs/EaganMatrixUserGuide.txt:3458`.

## 2. Units, useful ranges, blank-column behaviour

| Column | Units and neutral | What blank (= 0) does | Source |
|---|---|---|---|
| `In` | audio rate | no excitation, therefore silence `[I]`, the inference being that a filter bank with no input has nothing to filter |
| `F` | **kHz** | silence `[I]`, the inference being that a zero first-mode frequency leaves nothing to resonate |
| `sF` | **neutral = 1** | **not neutral**: zero is inharmonic | `[G]` `docs/EaganMatrixUserGuide.txt:3437-3438` |
| `qF` | neutral = 0 | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:3439` |
| `sA` | neutral = 0 | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:3440` |
| `B` | smaller means more resonance | **not neutral**: zero is maximum resonance, the same class of trap as a BiqBank's bandwidth column | `[G]` `docs/EaganMatrixUserGuide.txt:3442` |
| `sB` / `qB` | bipolar, neutral = 0 | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:3444-3446` |
| `C` | 0 = mode 1 | neutral | `[G]` `docs/EaganMatrixUserGuide.txt:3448` |
| `I` | 0..1 | the first spectrum in the set: valid but static | `[G]` `docs/EaganMatrixUserGuide.txt:3450-3452` |
| `S` | **neutral = 1** | **not neutral**: zero is a zero step rate, the same trap as HarMan's dilation | `[G]` `docs/EaganMatrixUserGuide.txt:3454-3455` |

**Blank-column verdict.** Three of eight columns have a non-zero neutral - `sF`, `B` and `S` -
and four are safe `[G]` `docs/EaganMatrixUserGuide.txt:3437-3455`. `[I]` No Properties-panel
defaults are documented for ModMan, so unlike a BiqBank there is no stated
"falls back to the Property" safety net - the inference is that a bank whose guide section
lists no properties has none to fall back to, and that inference is all the local sources
support.

`[C]` Measured column occupancy over 44 ModMan bank slots: c1 95%, c2 95%, c3 86%, c4 95%,
c5 70%, c6 18%, c7 93%, c8 95% (`analysis/findings/corpus-module-wiring.md` S10). `[C]` The
three trap columns are the three the factory almost always writes: `B` 42 of 44, the index 41
of 44, the dilation 42 of 44.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankA/B`, value 7 | **yes** - `set_bank_type("A", "ModMan")` `[G]` `eagan_mcp/setup.py:227` |
| All eight columns | matrix cells 27-34 / 35-42 | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| **Spectral set, or Live** | the spectral-set id (`index.md`, shared fact 6) | **read-only, decoded by name** as `bank_params.A.spectral_set` `[G]` `eagan_mcp/setup.py:186-195`. **No tool writes it** |
| The three-way select on column 3 | the second column-mode toggle (`index.md`, shared fact 3) | **read-only and undecoded** as `column_mode_2_raw`, a bare number `[G]` `eagan_mcp/setup.py:192`. No write tool |
| The two-way select on column 5 | the first column-mode toggle (`index.md`, shared fact 3) | **read-only and undecoded** as `column_mode_1_raw` `[G]` `eagan_mcp/setup.py:191`. No write tool |
| RBJ deflation 0..7 or IIT | the bank-param id (`index.md`, shared fact 4) | **read-only, decoded by name** as `bank_params.A.param` `[G]` `eagan_mcp/setup.py:190`. No write tool |
| Mode count | the biquad-size id (`index.md`, shared fact 5) | **read-only and undecoded** as `biquad_size_raw` `[G]` `eagan_mcp/setup.py:193`; `[I]` ModMan is a biquad bank so this plausibly applies, but the guide never says so for ModMan - the inference is from the shared engine, not from a statement |

`[I]` The column-mode toggles are the load-bearing gap here, because a matrix dump cannot be
read without them: the same cell is a frequency spread, a quadratic spread or an amplitude
spread depending on a number `get_setup` reports raw - the inference is a direct reading of the
decoder against the header. `T4` is the rank that would join the decoded toggles into
`get_matrix`'s labels. **`tools_spec.md` `T22` (`set_module_option`) covers writing them**,
and the `T` scheme runs to twenty-two ranks, not twenty; the ranked list that names them is
`analysis/findings/modules-mcp-reachability.md` section 5 rank 6, which `T22` folds into the
`T` namespace.

## 4. DSP cost class

**Medium to heavy** - it is a biquad mode bank, so `biqbank.md`'s profile applies `[G]`
`docs/EaganMatrixUserGuide.txt:2647-2648`, which names BiqBank, BiqGraph, BiqMouth and ModMan
as four ways to control one set of biquad bandpass filters.

On top of that there is a short-time Fourier transform performed **once at load**, not per
sample `[G]` `docs/EaganMatrixUserGuide.txt:3466-3472`, verbatim: "When ModMan is loaded, it
performs a short-time Fourier transform of the selected 150ms sample and uses the results to
manipulate mode amplitudes under EaganMatrix control."

The guide gives no explicit cost warning for ModMan `[I]` - the inference from its absence,
where the guide does warn for two oscillator types and for Additive, is that ModMan is not in
the heavy class, and that is weak evidence. The gap is filed as corpus-owned
(`analysis/findings/modules-unfilled-checklist.md` gap 19).

## 5. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`Koto` - a plucked ModMan, and the signature index sweep `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: A = ModMan param=deflate 1   (bank B resolves to ModMan but is not wired)
Bank A 1 <- Noise = F
Bank A 2 <- Direct + = X        Bank A 5 <- Direct + = D
Bank A 3 <- Direct + = G        Bank A 7 <- Direct + = A
Bank A 4 <- Direct + = E        Bank A 8 <- Direct + = B
Master SL/SR <- Bank A = K
  A = W SG3 1.0                     (the index swept by the pluck envelope)
  B = W Constant 0.32 [Ramp Down] ; X = 0 -> 0.5 Octaves ; Z = 0 -> 0.5   (dilation)
  E = W SG2 1.0 x0.1 ; Z = 0.37 -> 0.25 ; blend macro                     (bandwidth)
  D = Y = 1.0 -> 0.4 x0.1           (the column-5 value on the wheel)
  G = Z = 0 -> -0.3                 (the column-3 value from pressure)
```

`[C]` The index column driven by a bare shape-generator envelope is the ModMan signature: the
pluck sweeps **through** the spectral set, which is what makes it sound like a struck string
rather than a filtered one. Which value column 3 carries here is **not in the shipped data**: the catalog's wiring block
records the bank type and the deflation setting but no column-mode toggle, so the cell marked
`G` could be a frequency spread, a quadratic spread or an amplitude spread.

`Harmonic Viol` - a sustained ModMan with a delay body, and the clearest evidence for the
dilation neutral `[C]` (`factory_catalog.json`, `wiring`):

```
bank: A = ModMan param=deflate 1 ; C = SummedDelay ; osc 1 = Phase Generator
Bank A 1 <- Osc 1 = A, Osc 5 = G, Direct x = 0.2
Bank A 2 <- Direct + = X        Bank A 4 <- Direct + = D, Direct + (2) = B
Bank A 3 <- Direct + = F        Bank A 7 <- Direct + = C
Bank A 8 <- Direct + = 2        <-- the dilation as the bare constant 2
```

`[C]` A bare `2` in the dilation column is the single clearest piece of corpus evidence that
the neutral is 1 and that the factory deliberately stretches past it.

Factory leads the guide names: `Harp` and `Koto` `[G]`
`docs/EaganMatrixUserGuide.txt:3496-3498`. `[C]` `Harp` is in the corpus as `Chromatic Harp`
and `Wind Harp Wbl`; `Koto` is present as spelled.

## 6. Known traps

1. **Three columns have a non-zero neutral**: the frequency spread is 1, the bandwidth is not
   0, and the dilation is 1 `[G]` `docs/EaganMatrixUserGuide.txt:3437-3438`, `:3442`,
   `:3454-3455`.
2. **Columns 3 and 5 are mode-switched and the switch is invisible in a matrix dump.** Writing
   a frequency spread into a bank whose toggle selects the amplitude spread writes an amplitude
   spread instead `[G]` `docs/HakenMidi.h:1589`.
3. **ModMan is bank A or B only**; the header lists no bank C value for it `[G]`
   `docs/HakenMidi.h:1567`.
4. **Two manipulators plus a bank C delay are forced onto one spectral set**, and bank C "will
   operate using half its normal memory" `[G]` `docs/EaganMatrixUserGuide.txt:3491-3493`;
   `index.md` shared fact 6 owns the rule.
5. **Live mode is barely explored by the vendor** and reads the **SummedDelay** specifically
   `[G]` `docs/EaganMatrixUserGuide.txt:3473-3479`.
6. **Deflation guidance applies**: "0 [none], 1...7 [min to max narrowband protection]", set to
   the largest value that does not change the timbre, or use the always-stable Impulse
   Invariant Transform `[G]` `docs/EaganMatrixUserGuide.txt:3481-3486`.
7. **The index interpolates between spectra; it does not scrub time.** 0 is the first spectrum
   in the set and 1 the last, which is a different gesture from HarMan's index into grain data
   `[G]` `docs/EaganMatrixUserGuide.txt:3450-3452`.
8. **ModMan shares the one delay memory** with the delays, WaveBank and HarMan `[G]`
   `docs/EaganMatrixUserGuide.txt:4157`; `index.md` shared fact 7 owns the budget.
