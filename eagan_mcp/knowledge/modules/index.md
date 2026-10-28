# Module reference cards - index and shared facts

This file is the index for `eagan_mcp/knowledge/modules/`. It is written before the 18 module
cards and everything below `## Research-pass citations are not shipped

References of the form `analysis/findings/...`, `analysis/synthesis.md` and
`outputs/research-report.md` are the 2026-10-26 research pass's working files. **They are NOT
shipped with this package** - `.gitignore` excludes `.maister/tasks/`, which is where they live -
so on a fresh clone or a `pip install` those paths resolve to nothing. They are kept because
removing them would erase the provenance of claims that were genuinely derived there, but they are
a record of *where a finding came from*, not somewhere you can go and read it.

What to use instead, by the job the citation was doing:

| The citation supports | Use this instead, and it ships |
|---|---|
| A `[C]` corpus statistic | `factory_catalog.json` and `census.json` - the actual decoded data. `search_factory_presets` queries them; 49 presets carry cell-level `wiring` |
| A named gap, or "nobody owns this" | `RESEARCH_REPORT.md`, which carries the four gap classes and the `DT1`..`DT21` device-test plan |
| A `T<n>` tool rank | `tools_spec.md`, 22 ranked specifications |
| A device finding | `CLAUDE.md`, which is the authoritative protocol record and is tracked |

A `[C]` claim is therefore still checkable - just against the shipped data rather than against the
analysis that first spotted it. Where a claim cannot be checked that way, treat it as the research
pass's inference and weigh it accordingly: `[C]` never becomes `[D]`.

## Card inventory` is **binding** on them: a card *references* what is
here and never restates it.

Evidence tags follow `.maister/docs/standards/protocol/protocol-sources.md`, "The Five Bracket
Tags": `[D]` device-verified, `[D-cap]` recorded in a capture under `captures/` or
`tests/fixtures/`, `[G]` from the docs, `[C]` corpus statistic, `[I]` inferred. Resolution order is
`[G]` header > `[D]` > `[D-cap]` > `[G]` guide > `[C]` > `[I]`. A `[G]` header citation is
fw 10.81; a `[G]` guide citation is fw 10.80 at best, because `docs/EaganMatrixUserGuide.txt:3-4`
is stamped "Firmware Version 10.61 to 10.80". Guide line numbers drift inside a section, so every
guide claim here quotes verbatim: the quote, not the line number, is the locator.

ASCII only. `->` is an arrow, `+-` plus-or-minus, `x` multiply, and `S<n>` is a section number
(the research findings print it as a section sign).

## What this file owns, and what a card must not restate

This file owns, for all 18 cards:

- the card inventory and the one spelling of every module name;
- the nine shared facts (the matrix column budget, assignable bank columns, the `cm1`/`cm2`
  toggles, `idBankParamA/B`, biquad bank size, spectral set selection, the shared delay memory,
  the delay-tap row alternates, and the bank type wire values);
- the corpus frequency of every module across the 668 factory presets;
- the six cross-module wiring patterns;
- the Master chain, which has no card of its own;
- the tool limits, voids and preset-name corrections that apply to more than one card.

A **module card** owns only what is specific to its module: what each of its columns means, units
and useful ranges, blank-column behaviour, properties-panel settings and MCP reachability, DSP
cost class, typical wiring, and known traps.

`patterns.md` owns reusable constructions **across** modules - how to build a thing, not what a
module's columns are. A card describes a module; `patterns.md` describes a construction; this
index describes what is true of all of them. The three never duplicate each other; they
cross-reference. This is the same non-overlapping-roles rule the root documents already follow
(`.maister/docs/standards/global/conventions.md:10`).

## Card inventory

Eighteen cards, exactly. Filenames are the kebab-cased module name; the module name is
`setup.py`'s spelling (see the next section). **There is no 19th card** `[I]`: the
field-completeness matrix in `analysis/findings/modules-unfilled-checklist.md` S1 has exactly 18
rows and the Master chain has none, so the inference is that the card set is that row set and the
Master chain folds into this file and `model.md` instead.

| # | Card file | Module | Wire value | Card source | Wiring source |
|---|---|---|---|---|---|
| 1 | `oscillator-slots.md` | the 20 `idOscFilTyp` slot modes | `idOscFilTyp1..5 = 72..76` `[G]` `docs/HakenMidi.h:1507-1511` | `analysis/findings/modules-oscillator-slots.md` | `corpus-module-wiring.md` S1 |
| 2 | `biqbank.md` | BiqBank | A/B `= 0` `[G]` `docs/HakenMidi.h:1561` | `analysis/findings/modules-biqbank.md` | `corpus-module-wiring.md` S2 |
| 3 | `biqgraph.md` | BiqGraph | A/B `= 1` `[G]` `docs/HakenMidi.h:1562` | `analysis/findings/modules-biqgraph.md` | `corpus-module-wiring.md` S3 |
| 4 | `biqmouth.md` | BiqMouth | A/B `= 2` `[G]` `docs/HakenMidi.h:1563` | `analysis/findings/modules-biqmouth.md` | `corpus-module-wiring.md` S4 |
| 5 | `sinebank.md` | SineBank | A/B `= 3` `[G]` `docs/HakenMidi.h:1564` | `analysis/findings/modules-sinebank.md` | `corpus-module-wiring.md` S5 |
| 6 | `sinespray.md` | SineSpray | A/B `= 4`, C `= 4` as `SineSpray (alias of B)` `[G]` `docs/HakenMidi.h:1570` | `analysis/findings/modules-sinespray.md` | `corpus-module-wiring.md` S6 |
| 7 | `wavebank.md` | WaveBank | A/B `= 5`, C `= 5` as `WaveBank (alias of B)` `[G]` `docs/HakenMidi.h:1569` | `analysis/findings/modules-wavebank.md` | `corpus-module-wiring.md` S7 and S8 (LeCaine) |
| 8 | `harman.md` | HarMan | A/B `= 6`, C `= 6` as `HarMan (alias of B)` `[G]` `docs/HakenMidi.h:1568` | `analysis/findings/modules-harman.md` | `corpus-module-wiring.md` S9 |
| 9 | `modman.md` | ModMan | A/B `= 7` `[G]` `docs/HakenMidi.h:1567` | `analysis/findings/modules-modman.md` | `corpus-module-wiring.md` S10 |
| 10 | `cvc.md` | CVC | B `= 8`, C `= 8` as `CVC (alias of B)`; **not available on bank A** `[G]` `docs/HakenMidi.h:1571` | `analysis/findings/modules-cvc.md` | `corpus-module-wiring.md` S11 |
| 11 | `kinetic.md` | Kinetic | A/B `= 9` `[G]` `docs/HakenMidi.h:1566` | `analysis/findings/modules-kinetic.md` | `corpus-module-wiring.md` S12 |
| 12 | `additive.md` | Additive | A/B `= 10` `[G]` `docs/HakenMidi.h:1565` | `analysis/findings/modules-additive.md` | `corpus-module-wiring.md` S13 |
| 13 | `voicedelay.md` | VoiceDelay | C `= 0` `[G]` `docs/HakenMidi.h:1572` | `analysis/findings/modules-delays.md` S1 | `corpus-module-wiring.md` S14 |
| 14 | `summeddelay.md` | SummedDelay | C `= 1` `[G]` `docs/HakenMidi.h:1573` | `analysis/findings/modules-delays.md` S2 | `corpus-module-wiring.md` S15 |
| 15 | `microdelay.md` | MicroDelay | C `= 2` `[G]` `docs/HakenMidi.h:1574` | `analysis/findings/modules-delays.md` S3 | `corpus-module-wiring.md` S16 |
| 16 | `formuladelay.md` | FormulaDelay | C `= 3` `[G]` `docs/HakenMidi.h:1575` | `analysis/findings/modules-delays.md` S4 | `corpus-module-wiring.md` S17 |
| 17 | `recirculator.md` | Recirculator | **not a bank type**: `idReciType = 62`, 7 algorithms `[G]` `docs/HakenMidi.h:1479-1487` | `analysis/findings/modules-master-recirculator-convolution.md` S3 | `corpus-module-wiring.md` S18 |
| 18 | `convolution.md` | Convolution | **not a bank type**: the `s_Conv_Poke` stream (stream 26), two convolutions in the Master section, `id_c_dat0 = 4` selecting the first IR `[G]` `docs/HakenMidi.h:1141`, `:1785-1793` | `analysis/findings/modules-master-recirculator-convolution.md` S5 | `corpus-module-wiring.md` S18d |

`[I]` Cards 17 and 18 are the two modules that are **not** selectable as a bank or an oscillator
slot type, so they do not appear in the module space at all - the inference is that their only
matrix surface is the assignable Master columns, which is why they are carded separately from the
chain itself. Neither `Recirculator` nor `Convolution` is a key in `census.json`'s
`modules_used_including_defaults` `[C]` (0 of the 37 module keys measured over 668 presets).

**Which presets a card's "Typical wiring" may name.** `eagan_mcp/preset_file.py:WIRING_PRESETS` is
the 49 factory presets whose decoded `wiring` block ships in `factory_catalog.json` `[C]` (49 of
668). A card's section 5 may cite only those, so prose and data agree by construction. Every card
has at least one except **`convolution.md`**: `corpus-module-wiring.md` S18d names no preset, so
card 18 states the absence instead of citing an example.

## Module-type spelling, fixed project-wide

The one spelling of every module name is `setup.py`'s, because those exact strings are the enum
values `set_osc_type` and `set_bank_type` accept and the values the shipped catalog and
`census.json` carry `[G]` `eagan_mcp/setup.py:10-42`. Card filenames are the kebab-cased form.
The three tables, each header-cited at its definition:

- Oscillator/filter slot modes: `setup.py:OSC_TYPES`, 20 values `[G]` `docs/HakenMidi.h:1512-1535`.
- Bank A/B types: `setup.py:BANK_AB_TYPES`, 11 values `[G]` `docs/HakenMidi.h:1561-1571`.
- Bank C types: `setup.py:BANK_C_TYPES`, 8 values `[G]` `docs/HakenMidi.h:1568-1575`.

**Eight names differ from the research findings' decoder and `setup.py` wins in all eight**, since
its string is the accepted enum value: `CVC`, `Bitcrusher`, `Noise from Seed`,
`Shelving High Pass` / `Shelving Low Pass`, `Band Reject (Notch)`,
`Single Pole High Pass` / `Single Pole Low Pass`, `Low Pass Filter`, and wire value 17, which the
research decoder called `Granulate Delay Tap` and `setup.py` calls **`Pitch Shifter using Delay`**
`[G]` `eagan_mcp/setup.py:16`. Both readings come from one header comment - `GDEL = 17`,
"granulate delay tap (pitch shift)" `[G]` `docs/HakenMidi.h:1535` - and `setup.py` wins because
its string is the enum value `set_osc_type` accepts. A card writing "Granulate Delay Tap" is
writing a name no tool accepts.

**The `(alias of B)` suffix stays.** `SineSpray (alias of B)`, `WaveBank (alias of B)`,
`HarMan (alias of B)` and `CVC (alias of B)` are **distinct wire values** (Bank C 4, 5, 6, 8)
meaning Bank C is mirroring Bank B's module - "C is alias for B" `[G]` `docs/HakenMidi.h:1568-1571`.
They are not duplicate names and must not be collapsed; stripping the suffix would discard a real
structural fact about a preset. A card covers both forms of its module and says which bank each
form can sit in.

## How many of the 668 factory presets use each module

One source: `eagan_mcp/knowledge/census.json`, key `modules_used_including_defaults`. A card states
its own row and nothing else; it does not recount. "Including defaults" matters because wire value
0 of `idBankA/B/C` and `idOscFilTyp*` is the device default, so a compressed preset file never
writes it - these counts resolve that default and count the preset if its matrix region is wired
`[C]` (`census.json:implicit_default_modules`, over the same 668 presets).

`[C]` All 37 rows, 668 presets, from `census.json:modules_used_including_defaults`:

| Module | Presets of 668 |
|---|---|
| DSF Oscillator | 466 |
| BiqBank | 151 |
| VoiceDelay | 110 |
| HarMan | 105 |
| SummedDelay | 98 |
| WaveBank | 97 |
| Kinetic | 68 |
| High Pass | 52 |
| BiqMouth | 45 |
| ModMan | 45 |
| BiqGraph | 44 |
| MicroDelay | 37 |
| Tanh | 36 |
| Single Pole High Pass | 36 |
| Band Pass | 35 |
| Single Pole Low Pass | 34 |
| Integrated DSF | 32 |
| Shelving High Pass | 23 |
| Low Pass Filter | 19 |
| Phase Generator | 19 |
| SineSpray | 18 |
| SineBank | 16 |
| CVC | 15 |
| Additive | 12 |
| Band Reject (Notch) | 12 |
| Signal Multiplier | 10 |
| FormulaDelay | 9 |
| Shelving Low Pass | 8 |
| Bitcrusher | 7 |
| Ladder Low Pass | 6 |
| HarMan (alias of B) | 5 |
| Jenny Oscillator | 4 |
| All Pass | 4 |
| Noise from Seed | 3 |
| Pitch Shifter using Delay | 3 |
| WaveBank (alias of B) | 1 |
| PWM Oscillator | 1 |

`[C]` Two counts changed from the figures in the research findings, both because of codec fixes,
and the corrected numbers are the ones above: the `wavetable` technique is **98 of 668** (Bank C
aliases were never matched before), and the new `formula_delay_buffer` tag covers **8 of 668**
(the old check compared against `"FormulaDelay"` while the table said `"FDelay tap"`, so it never
fired). The technique space is **52 tags**, not 51.

`[C]` A bank or slot carrying no explicit type id is the device default and is resolved, not
dropped: 151 presets of 668 run an implicit BiqBank, 110 an implicit VoiceDelay and 461 an
implicit DSF Oscillator (`census.json:implicit_default_modules`).

## Cross-module patterns that belong on every card

`[I]` These six recur across so many modules that this index owns them and each card
**references** them by number rather than restating them - restating them on 18 cards is exactly
the duplication this structure exists to prevent. Source:
`analysis/findings/corpus-module-wiring.md` S19.

1. **Pitch onto a frequency column.** Use the predefined `X` code
   (`set_matrix_point(row=13, col=<F>, value="X")`) unless you need to add something inside one
   letter - then use one of the two pitch idioms in `patterns.md` (P3). `[I]` as S19.
2. **Ratio a second column to the first.** Put the same letter in both and a bare constant on
   `Direct x (multiply)` of the one you want scaled. `[C]` 88 of 668 presets do it for HarMan `H`/`S`,
   45 of 668 for `Bank C 2`/`Bank C 4`, 46 of 668 for `Osc 1 F`/`Osc 2 F`.
3. **Expose a control.** `W = Constant k` with modifier `x Macro`. `[C]` 1,842 of 7,254 formulas
   (25.4%) do this.
4. **Constant offset without the wheel.** Equal non-zero `Y` heights
   (`height_begin == height_end`). `[C]` `BiqMouth - Basic`, `Basic LeCaine` and
   `Dueling BiqBanks` all use it (3 named of the 49 presets with a shipped wiring block); it is
   the factory's way to add a fixed number inside a formula.
5. **Crossfade two banks on the wheel.** Two letters with mirrored `Y` ramps. `[C]`
   `Touch Reed T`'s `N`/`O`, `Cascade`'s `C`/`H` and `Dueling BiqBanks`'s `D`/`E` (3 of the 49).
6. **Always feed both `SG n F` and `SG n T`.** `[C]` 433 of 433 modern shape-generator uses do.
   A Continuous or Single Cycle SG with no `T` column never starts `[D]` `CLAUDE.md:116`,
   2026-10-25, fw 10.81.

## The Master chain - folded in here, not a 19th card

The Master section is a fixed serial chain `[G]` `docs/EaganMatrixUserGuide.txt:1475`, verbatim:
"The Master produces a stereo submix as follows:". It has no field-completeness row and therefore
no card; its detail lives here and in `model.md`.

`[G]` `docs/EaganMatrixUserGuide.txt:1476-1478`, verbatim: "Stereo sum (SL, SR) from all voices ->
Pre-Level -> Compressor/TanH -> Limiter -> DC Filter -> Pre-Recirculator Convolution ->
Recirculator -> Post-Recirculator Convolution -> Submix -> Final Mix (add in L/R from all voices
to submix) -> Tilt EQ -> Post Level -> Attenuation" (the guide prints the arrows as a right-arrow
glyph; rendered here as `->` under the ASCII rule).

Two structural paths:

- `[G]` `docs/EaganMatrixUserGuide.txt:1480-1481`, verbatim: "The Master's submix is fed back into
  the matrix on the Sub L and Sub R matrix rows, for optional further processing."
- `[G]` `docs/EaganMatrixUserGuide.txt:1499`, verbatim: "Also, no waveshaping is done on the
  Master L and R columns." The column table says the same of the inputs themselves `[G]`
  `docs/EaganMatrixUserGuide.txt:1461-1465`, verbatim: "This input is not processed by saturation,
  Convolutions, and Recirculator."

Master column layout: columns 0/1 are `SL`/`SR`, **columns 2..7 are the six assignable columns**,
column 8 is the Master/Dry mix `M`, 9/10 are dry `L`/`R`, 11 is the separator `[D]`
`CLAUDE.md:15-17`, 2026-10-25, fw 10.81.

What each assignable column drives is selected by `idMastCol1..6 = 27..32`, values
`mReci1..mReci6 = 0..5`, `mReciMix = 6`, `mPre = 7`, `mThrDrv/mAtkCut/mRatMkp/mCoThMix = 8..11`,
`mPost = 12`, `mEqTilt/mEqFreq/mEqMix = 13..15`, `mConvI1/mConvM1/mConvI2/mConvM2 = 16..19` `[G]`
`docs/HakenMidi.h:1488-1500`. `eagan_mcp/setup.py:MASTER_COL_TARGETS` reproduces this table
exactly - confirmed against the header, not re-derived.

Columns **add into** the dial value rather than replacing it `[G]`
`docs/EaganMatrixUserGuide.txt:1412-1413`, verbatim: "The column value (scaled 0..1) will be added
to the corresponding Recirculator Control Dial value (cc20..cc24 scaled 0..127; see Continuum User
Guide)."

`idCompOpt = 16` picks `masComp = 0` (compressor) or `masTanh = 1` (master Tanh), which is why
assignable values 8 and 10 carry two names each `[G]` `docs/HakenMidi.h:1501-1502`.

**Convolution and the Recirculator are already matrix-modulatable today.** Decoding
`tests/fixtures/microdelay_wg_v1_20261025_192903.mid`'s stream 20 gives ids 27-32 =
16, 17, 3, 6, 18, 19, i.e. Master columns 2-7 drive Conv 1 Interp, Conv 1 Mix, Recirc R4, Recirc
Mix, Conv 2 Interp and Conv 2 Mix `[D-cap]` `tests/fixtures/microdelay_wg_v1_20261025_192903.mid`.
So no tool or protocol work is needed to modulate them - only labelling, which
`setup.MASTER_COL_TARGETS` now provides. The reachable set is 7 Recirculator targets (`R1`..`R6`
plus Mix) and 4 convolution targets out of the 20 assignable values `[G]`
`docs/HakenMidi.h:1494-1500`.

`[G]` `docs/EaganMatrixUserGuide.txt:1504-1505`, verbatim: "Tilt Eq and Compressor functions
available in the Editor and through Midi control are not programmed directly into the EaganMatrix
Master section."

## Tool limits that bind every card

Two limits are recorded here so no card has to rediscover them, and so no card promises something
the tools do not do:

1. `[I]` **Nothing in the Recirculator or Convolution configuration is MCP-writable.** The
   inference is from the tool surface: `setup.py` decodes `RECI_TYPES` and
   `MASTER_COL_TARGETS` for reading, and no tool writes `idReciType`, `idNoRecirc` or any
   `s_Conv_Poke` id. Cards 17 and 18 must state the limit and name the `tools_spec.md` rank that
   would unblock it rather than implying a write path exists.
2. `[I]` **`describe_matrix_layout` promises verification markers it does not return.** Its
   docstring says entries marked "guide" in `matrix_map.py` are unverified, but those markers
   exist only as source comments at `eagan_mcp/matrix_map.py:7-16`; the returned dict carries
   names only. The inference is that a card citing a per-row or per-column verification marker
   would be citing something the caller never sees - **so no card cites a marker the tool will not
   show.**

## Unfilled fields, voids and name corrections every card inherits

`[I]` The field-completeness matrix in
`analysis/findings/modules-unfilled-checklist.md` S1 has exactly **18 rows**, one per card, and
lists **32** individual gaps. **13** gaps are `owner: device` and cannot be closed offline, so
those fields ship as `[I]` with the gating device test named; **11** are `owner: corpus` and
**none of them is blocked** - C1, the preset-file format crack, passed 668/668. DSP cost class is
filled for **8 of 16** applicable modules and blank-column behaviour needs a device test for **7**.
Recirculator and Convolution have no bank columns, so their blank-column field is `-`.

`[I]` **Three real voids must be stated as voids, not filled.** The inference in each case is that
no local source answers the question, so a guess would be indistinguishable from a fact:

- `sinebank.md`: the maximum partial count, 32 (guide) against 48 (`idBqExt`). State it as a
  CONFLICT block with both sides standing.
- `biqgraph.md`: the string-excitation column, `sB`-under-`2T` (guide) against negative `qF`
  (header). State it as a CONFLICT block.
- `recirculator.md`: **what `R1`..`R6` mean.** The guide gives only `R4` and defers to
  `docs/ContinuumUserGuide.txt` cc20-cc24, which is outside this knowledge base, so card 17
  **cannot say what any Recirculator parameter does** and says so.

`[C]` Three preset-name corrections, measured against the 668 factory filenames, carry onto the
cards that name them: `Kinetic Evil Ball` is **`Kinetic Evil Bell`**; `Left Hand Filter Echo` has
**no match** under any spelling (use `Underwater Ceramics`, `Resonant Drum 2` or `Bird Echoer`);
and `Bouncer` exists but its bank A is a BiqGraph, so the lead is **filed on the wrong card**.

---

## Shared fact 1 - the matrix column budget

- `[D]` `CLAUDE.md:15-17`, 2026-10-25, fw 10.81: columns 0/1 are Master SL/SR; columns 2..7 are
  **6 assignable Master columns**, selected by `s_Mat_Poke` ids 27-32; column 8 is the Master/Dry
  mix; 9/10 are dry L/R; 11 is the separator. Banks have **8 columns each**: A = 27-34,
  B = 35-42, C = 43-50.
- `[G]` `docs/HakenMidi.h:696`, `:704`, `:712`: `cA1 = 27` ("BankA first column"),
  `cB1 = 35` ("BankB first column"), `cC1 = 43` ("BankC first column") - the header's own column
  numbering, which is what `eagan_mcp/matrix_map.py:COLS` follows.
- `[G]` `docs/EaganMatrixUserGuide.txt:1617-1618`, verbatim: "The EaganMatrix has five 3-column
  Oscillator/Filter/Multiplier slots; each of the five is configurable as a number of different
  types of Oscillator". So each slot occupies **3 matrix columns**.
- `[D]` `CLAUDE.md:17`, 2026-10-25, fw 10.81: the oscillator slot's third column is **B
  (bandwidth) or spectral balance**, depending on slot type.

## Shared fact 2 - which bank columns are assignable, and by what id

This is the most load-bearing structural fact for the cards, and it comes from the header's
property streams rather than from the guide `[G]` `docs/HakenMidi.h:1671-1687`, `:1726-1753`. A
card states which of its columns are fixed and which are assignable; it does not re-list the value
tables below.

`[G]` `docs/HakenMidi.h:1748-1753` (`id_q_Sel3..Sel8` = 18..23, bank A), `:1777` onward
(`id_q2_Sel3..` = 42.., bank B), `:1684-1687` (`id_k_Sel5..Sel8` = 13..16, bank A), `:1709-1712`
(`id_k2_Sel5..Sel8` = 37..40, bank B), `:1576-1587` (the `cm1`/`cm2` selects):

| Bank type | Fixed columns | Assignable columns | Selector ids |
|---|---|---|---|
| BiqBank, SineBank | 1 (amplitude), 2 (F) | **3..8** | `id_q_Sel3..Sel8` = 18..23 (A) / `id_q2_Sel3..Sel8` = 42..47 (B) |
| Kinetic | 1 (amplitude), 2 (B bow), 3 (stiction), 4 (F) | **5..8** | `id_k_Sel5..Sel8` = 13..16 (A) / `id_k2_Sel5..Sel8` = 37..40 (B) |
| BiqGraph, BiqMouth, SineSpray, WaveBank, HarMan, ModMan, Additive, CVC, all delays | all | none individually; one or two **column-mode toggles** instead | `idBankAcm1 = 95`, `idBankAcm2 = 97`, `idBankBcm1 = 94`, `idBankBcm2 = 96` |

**Assignable-column values for BiqBank / SineBank**, `id_q_NOP = 0` .. `id_q_A3 = 17` `[G]`
`docs/HakenMidi.h:1726-1747`:

| Value | BiqBank | SineBank | Meaning |
|---|---|---|---|
| 0 | (blank) | (blank) | `id_q_NOP`, unused column |
| 1 | `sF` | `sF` | linear freq spread from the fundamental (matrix value < 0 = String Inharmonicity Coefficient) |
| 2 | `qF` | `qF` | non-linear freq spread (matrix value < 0 = String Excitation Position) |
| 3 | `B` | `B` | mode / partial bandwidth |
| 4 | `R` | `R` | even/odd amplitude ratio |
| 5 | `C` | `C` | centre of focus |
| 6 | `sB` | `sB` | BiqBank: bandwidth linear increase from centre. SineBank: partial noise-amp spread |
| 7 | `qB` | `sP` | `id_q_qBsP` - BiqBank: bandwidth non-linear increase. SineBank: partial phase spread. **Same id, different meaning** |
| 8 | `sA` | `sA` | amplitude decrease from centre |
| 9-11 | `1F 2F 3F` | same | spectral peak 1/2/3 frequency (`nToHz` **x** optional matrix column - multiplied, not added) |
| 12-14 | `1B 2B 3B` | same | spectral peak 1/2/3 bandwidth (+ optional matrix column) |
| 15-17 | `1A 2A 3A` | same | spectral peak 1/2/3 amplitude (+ optional matrix column) |

**Assignable-column values for Kinetic**, `id_k_NOP = 0` .. `id_k_Q = 10` `[G]`
`docs/HakenMidi.h:1671-1681`:

| Value | Label | Meaning |
|---|---|---|
| 0 | (blank) | `id_k_NOP`, unused column |
| 1 | `A` | anchor position |
| 2 | `K` | spring constant |
| 3 | `M` | mass |
| 4 | `G` | gravity |
| 5 | `H` | height |
| 6 | `V` | viscosity |
| 7 | `E` | elasticity |
| 8 | `P` | padding |
| 9 | `S` | slipping friction |
| 10 | `Q` | quit-slipping friction |

`[G]` `docs/EaganMatrixUserGuide.txt:3785-3794` lists only `A K M G V P S Q` as selectable and
omits `H` and `E`; the header is the resolution order's higher source and the `kinetic.md` card
carries the conflict.

## Shared fact 3 - the cm1 / cm2 column-mode toggles

One `s_Mat_Poke` value each; the meaning depends on the bank type. `idBankAcm1 = 95` /
`idBankBcm1 = 94`, `idBankAcm2 = 97` / `idBankBcm2 = 96`; bank C shares bank B's set, because a
Bank C "alias of B" value means C is mirroring B's module. `[G]` `docs/HakenMidi.h:1576-1591`:

| Toggle | Bank type | Values |
|---|---|---|
| `cm1` | BiqGraph | `cm1_g2Amp = 0` (graph 2 -> amplitude), `cm1_g2Band = 1` (graph 2 -> bandwidth) |
| `cm1` | Additive | `cm1_aSF = 0` (sF), `cm1_aQF = 1` (qF) |
| `cm1` | ModMan | `cm1_mmSB = 0` (sB), `cm1_mmQB = 1` (qB) |
| `cm1` | WaveBank | `cm1_wbOD = 0` (offset duty cycle), `cm1_wbEO = 1` (even/odd) |
| `cm1` | BiqBank | `cm1_bbDBP = 0` (dB/partial), `cm1_bbDBO = 1` (dB/octave) |
| `cm2` | BiqGraph | `cm2_g1Amp = 0` (graph 1 -> amplitude), `cm2_g1Frq = 1` (graph 1 -> frequency) |
| `cm2` | Additive | `cm2_aIP = 0` (I'), `cm2_aDF = 1` (dF), `cm2_aPA = 2` (pA), `cm2_aN = 3` (N) |
| `cm2` | ModMan | `cm2_mmSF = 0` (sF), `cm2_mmQF = 1` (qF), `cm2_mmSA = 2` (sA) |
| `cm2` | BiqBank | `cm2_bbFull = 0` (modes full scale), `cm2_bbHead = 1` (leave headroom, the 24 dB Amp Headroom toggle) |

## Shared fact 4 - idBankParamA/B (99 / 98): deflation or waveform

One id, two unrelated meanings depending on the bank type. `idBankParamA = 99` (bank A),
`idBankParamB = 98` (bank B and C). `[G]` `docs/HakenMidi.h:1591-1598`:

- biquad banks (BiqBank, BiqGraph, BiqMouth, ModMan): `0..7` = RBJ deflation level,
  `bq_iit = 8` = Impulse Invariant Transform, which is always stable and needs no deflation.
- WaveBank: `wave_saw = 0`, `wave_square = 1`, `wave_triangle = 2`, `wave_LeCaine = 3`.
- `defBankParam = 1`, the header's own comment: "default deflate 1 (biqBank) or square
  (waveBank)".

`[I]` Consequence for `wavebank.md`: the waveform choice is a single `s_Mat_Poke` id that no MCP
tool exposes, so the card states the tool limit - the inference is that a parameter with a wire id
and no tool is unreachable rather than absent.

## Shared fact 5 - biquad bank size

`idBqExtA = 70` (bank A), `idBqExtB = 71` (bank B); values `0..5` mean **8, 16, 24, 32, 40, 48**
modes, and `bqVar = 6` means the variable option. `[G]` `docs/HakenMidi.h:1600-1602`, header
comment: "idBqExtA/B 0..5 means 8..48 modes; 6 means variable".

`[G]` `docs/EaganMatrixUserGuide.txt:2264-2269`, verbatim: "Note: The ("Variable 8..96 Modes") option to
the biqbank is a variable mode usage bank (instead of the fixed 8,16,32,48). This setting
dynamically decides how many biquads to synthesize based on the pitch of the note that is playing
from the surface. The lower the note, the more biquads that will be implemented."

`[I]` The guide's parenthetical lists four fixed sizes and the header six - the inference is that
the guide is naming the common menu entries, not contradicting the header, but `sinebank.md`'s
32-vs-48 void (above) is the part that is genuinely unresolved.

## Shared fact 6 - spectral set selection (HarMan / ModMan / Additive)

`idSSetA = 64` (bank A), `idSSetB = 65` (bank B and C). `[G]` `docs/HakenMidi.h:1603-1621`.

- HarMan / ModMan: `Live = 0` (granulate what VoiceDelay or SummedDelay recorded), then 37 flash
  sets, `ss_Bell = 1` .. `ss_Crystal = 37`. The full ordered list ships as
  `eagan_mcp/setup.py:SPECTRAL_SETS`, 38 entries; a card references it rather than reprinting it.
- Additive: the same ids select an analysis decade, `addM = 0` (Mahling phrase),
  `add1stDecade = 1` .. `add4thDecade = 4`, shipped as `setup.py:ADDITIVE_SETS`.
- `[G]` `docs/EaganMatrixUserGuide.txt:3490-3492`, verbatim: "If you have two Manipulators (both
  Bank A and Bank B) as well as a Delay in Bank C, both Manipulators must specify the same
  Spectral Set."

## Shared fact 7 - one delay memory, four views, shared with three banks

`[G]` `docs/EaganMatrixUserGuide.txt:4155-4156`, verbatim: "VoiceDelay, SummedDelay, MicroDelay,
and FormulaDelay are four different ways to use the one underlying delay memory. This delay memory
is also used by the WaveBank, HarMan, and ModMan." The same two sentences are repeated at `:4213`
and `:4278`.

`[G]` `docs/HakenMidi.h:1632`: `idTimeSel = 105` selects the maximum delay time, header comment
"select time delay 50 ms * 2^n".

`[G]` `docs/HakenMidi.h:1599`: `idAliasDelay = 108`, header comment "true to disable nyquist
filtering on delay".

`[G]` `docs/EaganMatrixUserGuide.txt:4219-4221`, verbatim: "The sample rate of the delay memory is
limited by two variables: maximum delay and polyphony. The Anti-Aliasing Low Pass Filter indicator
above the first Bank C column will light up when the delay memory is at reduced sample rate."

`[I]` All four delay cards and the WaveBank, HarMan and ModMan cards therefore share one budget -
the inference is that a long `idTimeSel` in Bank C costs the Manipulator banks their sample rate,
which is a cross-card trap and belongs here, not restated four times.

## Shared fact 8 - matrix row alternates for delay taps

`idRowTyp1 = 106` reassigns the Audio L/R rows: `rt1Aud = 0` (Audio L and R), `rt1Tap = 1` (Tap 1
and Tap 2), `rt1AudTap = 2` (mono-mix audio, mono-mix Tap 1+2). `idRowTyp2 = 107` reassigns the
Sub L/R rows: `rt2Sub = 0`, `rt2Tap = 1` (Tap 3 and Tap 4), `rt2SubTap = 2`, `rt2Aud = 3`,
`rt2AudTap = 4`. `[G]` `docs/HakenMidi.h:1634-1643`.

`[I]` **This is how the delay taps reach the matrix at all.** The inference is that without these
two selectors there are no "Tap 1..4" rows to wire, which is why `eagan_mcp/matrix_map.py:ROWS`
labelling rows 9-12 unconditionally as Audio In L/R and Sub L/R is correct only for `rt1Aud` and
`rt2Sub`; `eagan_mcp/setup.py:ROW_TYPES1` / `ROW_TYPES2` carry the alternates.

## Shared fact 9 - bank type wire values (header, authoritative)

`idBankA = 91`, `idBankB = 92`, `idBankC = 93`. `[G]` `docs/HakenMidi.h:1558-1560`.

| Value | Bank A | Bank B | Bank C |
|---|---|---|---|
| 0 | BiqBank | BiqBank | **VoiceDelay** |
| 1 | BiqGraph | BiqGraph | **SummedDelay** |
| 2 | BiqMouth | BiqMouth | **MicroDelay** |
| 3 | SineBank | SineBank | **FormulaDelay** |
| 4 | SineSpray | SineSpray | SineSpray (alias of B) |
| 5 | WaveBank | WaveBank | WaveBank (alias of B) |
| 6 | HarMan | HarMan | HarMan (alias of B) |
| 7 | ModMan | ModMan | - |
| 8 | - (CVC is bank B/C only) | CVC | CVC (alias of B; B+C = dual CVC) |
| 9 | Kinetic | Kinetic | - |
| 10 | Additive | Additive | - |

`[G]` `docs/HakenMidi.h:1561-1575`. This matches `eagan_mcp/setup.py:BANK_AB_TYPES` and
`BANK_C_TYPES` exactly, and matches `[D]` `CLAUDE.md:14`, 2026-10-25, fw 10.81 ("bank values
8 = CVC, 10 = Additive"). `[I]` The Bank C values are settled by the header but remain **not
device-verified** - the inference is that a header constant plus an agreeing decoder is not a
hardware observation, and `[C]` the corpus agrees (`census.json:bank_C`) without upgrading it:
a corpus statistic can never become `[D]`.

`[I]` **Trap, and the reason menu order is never a wire value.** The 1044 Editor's Bank A/B menu,
with separators removed, reads
`BiqBank, BiqGraph, BiqMouth, SineBank, SineSpray, WaveBank, HarMan, ModMan, Additive, Kinetic, CVC`,
which would give Additive 8, Kinetic 9 and CVC 10 - exactly the wrong guess `[D]` `CLAUDE.md:14`,
2026-10-25, fw 10.81 records as fixed. For Bank C the same menu gives CVC 7 where the header says
8. The inference, now demonstrated twice, is that menu position is not the wire value.
`[G]` **Confirmed against the 1081 Editor on 2026-10-28**, so it is not a 1044 artefact: that
install's own `Menuitems.txt` carries `$BankA`, `$BankB` and `$BankC`, and they list the same
order the header contradicts - Additive ninth in A/B, CVC seventh in C. The menus are a
display order and an excellent source of parameter NAMES and option text; they are not a
source of wire values, and `setup.py`'s tables, which follow the header, are the ones to
trust.
