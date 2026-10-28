# Module card - BiqBank (modal physical model)

Bank wire value **0**, bank A or bank B `[G]` `docs/HakenMidi.h:1561`. Guide section 6.3,
"Multipurpose Banks: BiqBank (Modal Physical Model)" `[G]`
`docs/EaganMatrixUserGuide.txt:2247`. Card schema, shared facts and the module-name spelling:
`index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle; this card writes `In`
`[G]` `docs/EaganMatrixUserGuide.txt:2260`.

## TL;DR

A bank of biquad bandpass filters excited by an audio-rate input. Only columns 1 and 2 are
fixed; columns 3..8 are assignable (`index.md`, shared fact 2), and what each one means is
**preset data**, not a static table `[G]` `docs/EaganMatrixUserGuide.txt:2275-2277`.

Every matrix value is **added** to the matching Properties-panel value, except the three
spectral-peak frequencies, which are **multiplied** `[G]`
`docs/EaganMatrixUserGuide.txt:2278-2281`. So a blank column here means "use the Property",
not "use zero" - BiqBank is the exception among the banks. The trap is one level up: several
Property defaults are themselves not musically neutral `[G]`
`docs/EaganMatrixUserGuide.txt:2403` and `:2417`.

`[C]` 151 of the 668 factory presets run a BiqBank (`census.json`,
`modules_used_including_defaults`), the largest bank population in the corpus.

## Key Decisions

- Carded on the add-not-replace semantics first, because the MCP sees only the offset and
   cannot read the Property it is added to `[I]` - the inference is that an offset whose base is
   invisible cannot be turned into an absolute value by any amount of matrix reading.
- The device-verified default picklist is preferred over the guide's, which lists `sF` twice and
   omits `sB`; both are recorded in section 1 as a conflict rather than one being deleted
   `[D]` `RECIPES.md:111-119`, 2026-10-25, fw 10.81.

## Open Questions / Risks

- `[G]` `docs/EaganMatrixUserGuide.txt:2486-2489` gives the spectral-peak bandwidths only as a
   dB/octave reading (1 -> 6 dB/oct, 2 -> 3 dB/oct, 0.5 -> 12 dB/oct) and no kHz unit.
- `[I]` Which deflation setting a 10.81 preset starts from is only inferable from the header's
   own default comment, not observed - the inference is that a documented default is not a
   measurement.
- `[C]` Blank `B` was filed as a device test and is now **downgraded, not answered**: the `B`
   Property is itself 0 in 33 of 44 measured BiqBank blocks, so both candidate answers give zero
   bandwidth and the safe rule follows either way
   (`analysis/findings/modules-unfilled-checklist.md` gap 2).

---

## 1. What every column means

| Col (bank A / bank B) | Fixed? | Label | Meaning and source |
|---|---|---|---|
| 1 (27 / 35) | fixed | `In` | Excitation input for all modes, audio rate; the mode count is set by the red text above this column `[G]` `docs/EaganMatrixUserGuide.txt:2252-2255` |
| 2 (28 / 36) | fixed | `F` | "Frequency (in kHz) for the first mode (first resonance)" `[G]` `docs/EaganMatrixUserGuide.txt:2273` |
| 3..8 (29-34 / 37-42) | assignable | preset data | Up to six parameters, chosen per column by clicking the heading `[G]` `docs/EaganMatrixUserGuide.txt:2275-2277` |

Which assignable value each column carries is selected by the `id_q` column-select ids `[G]`
`docs/HakenMidi.h:1748-1753`
(`index.md`, shared fact 2), and the 18-value table lives there. This card states only what
those values **do in a BiqBank**:

| Value | Meaning in a BiqBank | Source |
|---|---|---|
| `sF` | Linear Mode Spacing: 1 = harmonic, >1 stretched, <1 compressed; added to the Spread property `[G]` `docs/EaganMatrixUserGuide.txt:2287-2290` |
| `qF` | Squared Mode Spacing: 0 = no non-linearity, >0 = offsets proportional to mode-number squared `[G]` `docs/EaganMatrixUserGuide.txt:2293-2296` |
| `B` | Mode bandwidth; smaller values increase resonance `[G]` `docs/EaganMatrixUserGuide.txt:2417-2419` |
| `R` | Even/odd mode amplitude ratio: <0 suppresses odd modes, >0 suppresses even `[G]` `docs/EaganMatrixUserGuide.txt:2423-2426` |
| `C` | Centre of Focus: 0 = mode 1, 1 = mode 8, 1.5 = mode 12, 6 = mode 48 `[G]` `docs/EaganMatrixUserGuide.txt:2430-2435` |
| `sB` | Bandwidth spread: >0 widens modes farther from Centre, <0 narrows them `[G]` `docs/EaganMatrixUserGuide.txt:2437-2440` |
| `qB` | Non-linear bandwidth spread, offset proportional to distance-from-Centre squared `[G]` `docs/EaganMatrixUserGuide.txt:2441-2444` |
| `sA` | Mode amplitude spread from Centre, as dB/Octave or dB/Mode `[G]` `docs/EaganMatrixUserGuide.txt:2450-2453` |
| `1F 2F 3F` | Spectral peak 1/2/3 centre frequency, **multiplied** by the property `[G]` `docs/EaganMatrixUserGuide.txt:2478-2483` |
| `1B 2B 3B` | Spectral peak 1/2/3 bandwidth `[G]` `docs/EaganMatrixUserGuide.txt:2486-2489` |
| `1A 2A 3A` | Spectral peak 1/2/3 amplitude `[G]` `docs/EaganMatrixUserGuide.txt:2492-2495` |

The add-not-replace rule in the guide's own words `[G]`
`docs/EaganMatrixUserGuide.txt:2278-2281`, verbatim: "Any column can be set to any of the values
which when defined are added to the identical Properties set in the BiqBank Properties panel
(except Spectral Peak Resonance Frequency which is multiplied by the associated property). If
not defined as a BiqBank matrix column, the fixed value defined in the property control is used
as is."

```
CONFLICT: the default assignable picklist for columns 3..7
  device [D]: columns 3-7 default to sF, B, sB, C, sA, column 8 unused
              - RECIPES.md:111-119, 2026-10-25, fw 10.81
  docs   [G]: "Columns default to sF, sF, B, C, sA (and an unused column that can also be
              selected - red dot)" - docs/EaganMatrixUserGuide.txt:2277-2278
  effect: the guide's list names sF twice and omits sB, so an agent following it writes a
          bandwidth-spread formula into what is really a second frequency-spread column -
          detuning the modes instead of changing their decay.
  corpus [C]: 43 of 44 measured bank blocks have the column-4 select set to B, which agrees
          with the device reading, not the guide's.
  resolution: both stand. Use the device picklist. Low risk once the column selects are
          readable, which is `T16`.
```

## 2. Units, useful ranges, blank-column behaviour

| Parameter | Property range and default | What a blank matrix column does | Source |
|---|---|---|---|
| `F` | kHz, no property | 0 kHz, silence `[G]` `docs/EaganMatrixUserGuide.txt:2273` |
| `sF` | 0.0..2.0, default **0.0** | falls back to 0.0, which is **not harmonic**; 1 is harmonic `[G]` `docs/EaganMatrixUserGuide.txt:2403-2405` |
| `B` | 0.0..2.0, default **0.0 / Narrow**; "A total bandwidth value of 1 is most common" | falls back to 0.0 = narrowest bandwidth, maximum resonance `[G]` `docs/EaganMatrixUserGuide.txt:2417-2420` |
| `R` | -1.0..1.0, default 0.0 / Neutral | neutral `[G]` `docs/EaganMatrixUserGuide.txt:2423-2426` |
| `C` | 0.0..1.0, default 0.0 / Mode 1; the control caps at mode 8 | mode 1 is centre `[G]` `docs/EaganMatrixUserGuide.txt:2430-2436` |
| `sB` | 0.0..2.0, default 0.0 / Same; the control's minimum is 0 | all modes the same bandwidth `[G]` `docs/EaganMatrixUserGuide.txt:2437-2444` |
| `sA` | 0.0..5.0 = 0 dB..-30 dB, default 0.0 | Centre does not affect amplitudes `[G]` `docs/EaganMatrixUserGuide.txt:2450-2453` |
| `1F 2F 3F` | 1 kHz, or 8.7 Hz..12543.9 Hz, default 0.0 / 1 kHz | with the default 1 kHz still set, **no spectral peak is defined at all** `[G]` `docs/EaganMatrixUserGuide.txt:2478-2485` |
| `1B 2B 3B` | 0.0..2.0, default 1.0 / Median | 1 -> 6 dB/oct from the peak centre, 2 -> 3 dB/oct, 0.5 -> 12 dB/oct `[G]` `docs/EaganMatrixUserGuide.txt:2486-2489` |
| `1A 2A 3A` | 0.0..5.0, default 0.0 | the peak contributes nothing `[G]` `docs/EaganMatrixUserGuide.txt:2492-2495` |

**Blank-column verdict.** Blank means "use the Property", so blank is structurally safe here
`[G]` `docs/EaganMatrixUserGuide.txt:2279-2281`. The danger is that two Property defaults are
not musically neutral: `sF` 0.0 is inharmonic and `B` 0.0 is maximum resonance `[G]`
`docs/EaganMatrixUserGuide.txt:2403` and `:2417`. The device-verified counter-practice is to
write the neutral explicitly - `Direct + -> Bank A sF = 1` `[D]` `RECIPES.md:122`, 2026-10-25,
fw 10.81.

`[C]` Measured column occupancy over 177 BiqBank bank slots: c1 97%, c2 96%, c3 91%, c4 94%,
c5 77%, c6 28%, c7 43%, c8 5% (`analysis/findings/corpus-module-wiring.md` S2).

## 3. Properties-panel settings and MCP reachability

The whole Properties panel lives in the BiqBank/SineBank property stream: write
`s_BiqSin_Poke` = stream 25, read back `s_BiqSin` = stream 12, 24 ids per bank `[G]`
`docs/HakenMidi.h:1103`, `:1139`, `:1726-1782`.

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankA/B` | **yes** - `set_bank_type("A", "BiqBank")` `[G]` `eagan_mcp/setup.py:227` |
| Matrix cells 27-34 / 35-42 | the matrix | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| Spread, BW, Amp Ratio, Centre, BW delta, Amp delta, the nine spectral-peak ids | `s_BiqSin_Poke` ids 1..17 (bank A) / 25..41 (bank B) | **unreachable**: no codec reads or writes stream 12 or 25 `[G]` `docs/HakenMidi.h:1726-1747`. `T16` is the rank that would unblock it |
| **Which function each of columns 3..8 carries** | the `id_q` column selects (`index.md`, shared fact 2) | **unreachable, and this is the worst gap on this card**: without it no tool can name a BiqBank column `[G]` `docs/HakenMidi.h:1748-1753`. `T16` unblocks the read, `T4` then joins it into `get_matrix`'s labels |
| Mode count | `idBqExtA/B` (`index.md`, shared fact 5) | **read-only and undecoded**: `get_setup` returns `bank_params.A.biquad_size_raw`, a bare number with no table `[G]` `eagan_mcp/setup.py:193`. No tool writes it |
| dB/Mode vs dB/Octave for `sA`; Amp Headroom 0 dB / 24 dB | the two column-mode toggles (`index.md`, shared fact 3) | **read-only and undecoded**: `column_mode_1_raw` / `column_mode_2_raw` `[G]` `eagan_mcp/setup.py:191-192`. No tool writes either |
| RBJ deflation 0..7 / IIT | the bank-param id (`index.md`, shared fact 4) | **read-only, decoded by name** as `bank_params.A.param` `[G]` `eagan_mcp/setup.py:190`. No tool writes it |

`[I]` Four of those seven surfaces are a single `s_Mat_Poke` id apiece and `_write_setup`
already exists in `eagan_mcp/server.py`, so the inference is that the missing piece is a
tool entry, not protocol knowledge. **`tools_spec.md` `T22` (`set_module_option`) covers
writing an arbitrary `s_Mat_Poke` id**, and the `T` scheme runs to twenty-two ranks, not
twenty; the ranked list that names these four is
`analysis/findings/modules-mcp-reachability.md` section 5 rank 1, 6 and 7, which `T22` folds
into the `T` namespace.

## 4. DSP cost class

**Medium to heavy, and directly scalable with the mode count** `[I]` - the inference is that a
bank of independent biquads costs in proportion to how many it runs, which the preset chooses.
The variable option makes the count pitch-dependent `[G]`
`docs/EaganMatrixUserGuide.txt:2264-2268`, verbatim: "This setting dynamically decides how many
biquads to synthesize based on the pitch of the note that is playing from the surface. The
lower the note, the more biquads that will be implemented."

Device data point: an FM oscillator pair plus one BiqBank plus shape generators ran DSP 72% at
7+ voices `[D]` `RECIPES.md:127`, 2026-10-25, fw 10.81.

## 5. Typical wiring

Cell orientation below is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`Dueling BiqBanks` - two banks, macro-controlled ring time, with output-level compensation
`[C]` (`factory_catalog.json`, `wiring`):

```
Bank A 1 <- Noise = A              Bank B 1 <- Noise = K
Bank A 2 <- Direct + = X, Direct x = 0.5      (sub-octave)
Bank A 3 <- Direct + = H       Bank B 2 <- Direct + = X
Bank A 4 <- Direct + = C       Bank B 3 <- Direct + = I, Direct x = 0.5
Bank A 5 <- Direct + = 0.5     Bank B 4 <- Direct + = F
Master SL/SR <- Bank A = D, Bank B = E, Direct x = 2
  C = W Constant -0.33 x macro i   ; Y = 0.64 -> 0.64     (bank A bandwidth)
  D = (W+X+Y)*Z, W = Constant -0.31 x macro i ; Z[Initial] 0 -> 1.0   (bank A level)
```

`[C]` The same macro drives the bandwidth coefficient (-0.33) **and** the output-level
coefficient (-0.31): widening a resonator's bandwidth makes it quieter, and this is the only
preset in the 668 that compensates for it.

`Model String Wind` - a closed loop between a filter slot and the bank, which is the string
model `[C]` (`factory_catalog.json`, `wiring`):

```
Osc/Filter 1 In <- Noise = A, Bank A = B, Direct + = 0.25, Direct - = D, Direct x = 2
Bank A 1 <- Osc 1 = E, Direct x = 0.13
Bank A 2 <- Direct + = X       Bank A 3 <- Direct + = 1
Bank A 4 <- Direct + = F, Direct + (2) = 1, Direct - = W
Osc/Filter 4 In <- Bank A = 1 ;  Master SL/SR <- Osc 4 = J, Direct x = K
```

`[C]` Note `Bank A 3 = 1`: the bare constant that supplies the harmonic `sF` the Property
default does not. `Bank A 4` takes the gated `W` on `Direct -`, so holding a note narrows
the bandwidth.

`Resonant Drum 2` and `Bowed BiqBank` are the other two BiqBank presets with a shipped wiring
block; `Bowed BiqBank` drives the bank's excitation column from a Kinetic model's position
output `[C]` (`factory_catalog.json`, `wiring`).

Device-verified starting point, to reproduce rather than re-derive: noise -> low-pass filter in
oscillator slot 5 -> `Osc 5 -> Bank A in = .1`; `Direct + -> Bank A F = X`;
`Direct + -> Bank A sF = 1`; `Bank A -> Master SL/SR` at a constant level, so the level does not
drop on release. A resonator needs far less input than a delay loop, 0.05 against 0.2
`[D]` `RECIPES.md:121-127`, 2026-10-25, fw 10.81.

`[C]` Guide-named lead correction: `Bouncer` exists in the corpus but its bank A is a BiqGraph,
so that lead belongs on `biqgraph.md`, not here (`index.md`, name corrections).

## 6. Known traps

1. **Property defaults are not neutral.** `sF` 0.0 is inharmonic and `B` 0.0 is the narrowest
   bandwidth, i.e. maximum resonance `[G]` `docs/EaganMatrixUserGuide.txt:2403-2405`,
   `:2417-2420`.
2. **Spectral peaks need Amp Headroom at 24 dB**, stated three times `[G]`
   `docs/EaganMatrixUserGuide.txt:2281-2282`, `:2475`, `:2514-2515`, the last verbatim: "You
   must set Amp Headroom to 24dB if you are using the Spectral Peak controls and/or associated
   or matrix programming." The toggle is the second column-mode toggle, which no tool writes.
3. **A spectral peak can silently do nothing**: if its frequency Property is still at the 1 kHz
   default and no `1F` column is present or that column evaluates to zero, no peak is created at
   all `[G]` `docs/EaganMatrixUserGuide.txt:2478-2485`.
4. **The three peak frequencies multiply; everything else adds** `[G]`
   `docs/EaganMatrixUserGuide.txt:2278-2281`.
5. **Do not pair `sF` with `qF`, or `sB` with `qB`,** in one bank `[G]`
   `docs/EaganMatrixUserGuide.txt:2288-2292`, verbatim: "If you select sF as a column, it is
   recommended not to also add a qF column (though it is possible and the two will be added
   together for the final output)."
6. **A negative `sB`, and a Centre past mode 8, can only come from the matrix** - the Property
   range floors at 0 and the Centre control caps at mode 8 `[G]`
   `docs/EaganMatrixUserGuide.txt:2432-2434`, `:2442-2443`.
7. **Deflation is a last resort, not a design tool** `[G]`
   `docs/EaganMatrixUserGuide.txt:2543-2544`, verbatim: "in most situations it is best if the
   preset can be designed to avoid too-narrow bandwidth and not require deflation".
8. **Resonator banks get quieter as bandwidth widens**, so a bandwidth macro usually needs a
   matching output-level term `[C]` (`Dueling BiqBanks`, the one example in the 668).
9. **BiqBank is the right module for a bendable string, not a delay loop**: its modes are
   filters and follow `X` live, so bends work after release, which delay-based strings do not
   `[D]` `RECIPES.md:103-106`, 2026-10-25, fw 10.81.
10. **Excitation bursts should be a fixed number of periods, not a fixed duration**, or low
    notes are under-excited relative to high ones `[D]` `RECIPES.md:136-142`, 2026-10-25,
    fw 10.81.
