# Recirculator

Card 17 of 18. The Master section's reverb/echo engine, with **7 selectable algorithms**.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

**The Recirculator is not a bank type.** It is not a value of `idBankA`, `idBankB` or `idBankC`
and it is not an oscillator/filter slot mode; it is selected by its own setup id, `idReciType =
62` `[G]` `docs/HakenMidi.h:1479-1487`. `[C]` It is not one of the 37 module keys in
`census.json:modules_used_including_defaults`, so it has no row in `index.md`'s frequency table -
the corpus counts it separately, under `census.json:recirculator`.

Its only matrix surface is the **assignable Master columns**, whose selector table, "adds into the
dial" semantics and capture-verified stock assignment belong to `index.md`'s Master-chain section
and are referenced here, not restated. The Master chain itself - what feeds the Recirculator and
what it feeds - is `index.md`'s and `model.md`'s.

Guide section 6.1, `docs/EaganMatrixUserGuide.txt:1375-1530`. Header: `idReciType`, `idNoRecirc`.

---

## 1. Columns

The Recirculator has **no columns of its own**. It is reachable only when one of the six
assignable Master columns (matrix columns 2-7) is pointed at it, which `index.md` documents.
Seven of the twenty assignable values reach this module:

| Assignable value | Target |
|---|---|
| 0-5 | `R1` .. `R6`, the six Recirculator parameters `[G]` `docs/HakenMidi.h:1494`, header comment "column adds into recirculator parameter" |
| 6 | the Recirculator **Mix** `[G]` `docs/HakenMidi.h:1495`, header comment "column adds into recirculator mix" |

`[G]` `eagan_mcp/setup.py:92-93` reproduces the names as `MASTER_COL_TARGETS`: `Recirc R1` ..
`Recirc R6` and `Recirc Mix`.

> **This card cannot say what any Recirculator parameter does.** `MASTER_COL_TARGETS` gives the
> reachable *targets* without saying what they control, and that distinction is this card's most
> important sentence: knowing that column 4 drives `R3` is not knowing what `R3` is.

**The void, stated as a void.** `[G]` `docs/EaganMatrixUserGuide.txt:1411-1414`, verbatim: "Each
of the two Recirc matrix columns contributes to a Recirculator (reverb/echo) control: R1, R2, R3,
R4, or Mix. The control is selectable by clicking on the column's heading. The column value
(scaled 0..1) will be added to the corresponding Recirculator Control Dial value (cc20..cc24
scaled 0..127; see Continuum User Guide)." The only parameter the EaganMatrix guide names is
`R4`: `[G]` `docs/EaganMatrixUserGuide.txt:1416-1417`, verbatim: "The first Recirc column defaults
to 'R4', which is the time control for all the Recirculator algorithms."

`[I]` **`R1`, `R2`, `R3`, `R5` and `R6` have no meaning recorded anywhere in this knowledge base.**
The inference is that the guide deliberately defers them: it points at the Continuum User Guide's
cc20-cc24, those meanings differ per algorithm, and no local source fills the gap - so a guess
here would be indistinguishable from a fact. This is checklist gap #23 and #24,
`owner: voicemodel`, source `docs/ContinuumUserGuide.txt`
(`modules-unfilled-checklist.md` S2), and it is one of the three voids `index.md` says must be
stated rather than filled.

`[I]` The Haken Editor 1044's own column menu reads "Offset for Recirculator Control R1, R2, R3,
R4, R5, R6, Mix" (`modules-conflicts.md`, non-conflicts section). The inference is that it
corroborates the **target list** and the word "offset" - and that it says nothing about meaning
either, so a third independent source names the same seven labels and still does not define them.

**Where the answer would come from**: `docs/ContinuumUserGuide.txt`, the cc20-cc24 section. That
file ships in `docs/` and is readable through `search_docs` / `read_docs`, but it is outside this
knowledge base's scope and has not been read into it. Until it is, an agent asked to "make the
reverb longer" can set `R4` - the one named control - and must say it does not know which of
`R1`, `R2`, `R3`, `R5` or `R6` is damping, size, diffusion or anything else.

**The seven algorithms**, which the guide never lists `[G]` `docs/HakenMidi.h:1479-1487`, carried
verbatim in `eagan_mcp/setup.py:71-74` as `RECI_TYPE_ID = 62` and `RECI_TYPES`:

| Value | Header constant | Algorithm |
|---|---|---|
| 0 | `R_shortRev` | Short Reverb `[G]` `docs/HakenMidi.h:1480` |
| 1 | `R_modDel` | Modulated Delay `[G]` `docs/HakenMidi.h:1481` |
| 2 | `R_swepEcho` | Swept Echo `[G]` `docs/HakenMidi.h:1482` |
| 3 | `R_anaEcho` | Analog Echo `[G]` `docs/HakenMidi.h:1483` |
| 4 | `R_digEchoLPF` | Digital Echo LPF `[G]` `docs/HakenMidi.h:1484` |
| 5 | `R_digEchoHPF` | Digital Echo HPF `[G]` `docs/HakenMidi.h:1485` |
| 6 | `R_longRev` | Long Reverb `[G]` `docs/HakenMidi.h:1486` |

`[G]` `docs/HakenMidi.h:1487`: `R_mask = 0x7` - the type occupies the low three bits of the id's
value, which is why `setup.py` masks before naming.

`[C]` What the factory picks, over 668 presets (`census.json:recirculator`): 304 presets set
`idReciType` explicitly and 364 leave it at the default. Among the explicit ones, Modulated Delay
74, Analog Echo 64, Long Reverb 46, Digital Echo LPF 44, Short Reverb 41, Swept Echo 19, Digital
Echo HPF 16. `[I]` Adding the 364 defaults to the 41 explicit gives Short Reverb 405 of 668; the
inference is that value 0 is the device default, the same resolution `index.md` applies to bank
and slot types.

## 2. Units, ranges and blank-column behaviour

**Blank-column behaviour: `-`, not applicable.** The Recirculator has no bank columns, so there is
no blank-cell question to answer `[I]`; the inference is structural, from section 1. This is why
the completeness matrix marks the field `-` for this module
(`modules-unfilled-checklist.md` S1).

**Units and ranges: `N`, absent - a second face of the same void.** The completeness matrix marks
this field `N` `[I]`. What *is* known:

| Quantity | Units / range | Source |
|---|---|---|
| A Master column driving `R1`..`R6` or Mix | the column value scaled 0..1, **added** to a dial value scaled 0..127 | `[G]` `docs/EaganMatrixUserGuide.txt:1413-1414` (quoted in section 1) |
| The Mix dial's default | 0 | `[G]` `docs/EaganMatrixUserGuide.txt:1419-1421`, verbatim: "The second Recirc column defaults to 'M', the dry/wet mix of the Recirculator output (0 = dry, 1 = 100% wet, .5 = 50% wet/dry, etc.). The Default is 0 (100% dry = Recirculator Off)" |
| `R1`..`R6` ranges and units | **unknown** | `[I]` the void of section 1; checklist gap #24, `owner: voicemodel`, owed to `docs/ContinuumUserGuide.txt` cc20-cc24 plus a header re-read |

`[I]` The practical consequence: a column value of 0.5 on `R4` is "add half the dial's full range
to whatever the dial is set to", and the dial's own setting is not in the preset's matrix. The
inference is that Recirculator values are **relative**, so a patch cannot specify an absolute
reverb time from the matrix alone.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | MCP today |
|---|---|---|
| **Recirculator algorithm** | `idReciType = 62` `[G]` `docs/HakenMidi.h:1479` | **read only.** `get_setup()["recirculator"]` names it through `setup.py:RECI_TYPES`; **no tool writes it** `[I]` - the inference is from the tool surface, where `set_bank_type` and `set_osc_type` have no Recirculator counterpart. Rank `T22` `[I]`: the inference is that the three Master-effect ids rank together under the one validated `s_Mat_Poke` write. `T<n>` is `outputs/research-report.md` section 9 rank *n*, whose rank 11 is the documentation repairs; `analysis/findings/modules-mcp-reachability.md` section 5 rank 11, which does group these three ids, has no `T` number of its own |
| Recirculator disable | `idNoRecirc = 15` `[G]` `docs/HakenMidi.h:1478`, header comment "true to disable recirculator" | **neither read nor written** - `setup.py` does not decode it. Rank `T22` `[I]`, same inference |
| What each assignable Master column drives | `idMastCol1..6 = 27..32`, `index.md`'s table | **read only**: `get_setup()["master_columns"]` names all six. No write tool: labelling is `T4`, which ships, and writing the assignment is `T21`, `set_master_column` `[I]` - the inference is that the one rank specified for the assignable Master columns' write side carries their selectors, as `T4` already carries the row-type labelling |
| The six assignable Master columns as matrix cells | matrix cells 2-7 | **write + read**: `set_matrix_point` / `get_matrix` `[I]`, from the tool surface |
| The Recirculator Control Dials themselves | cc20..cc24 `[G]` `docs/EaganMatrixUserGuide.txt:1413-1414` | `send_raw` only `[I]` - the inference is that no named tool sends them, so a caller must build the CC by hand and gets no verification |
| Any per-algorithm parameter meaning | - | **not a tool gap at all.** `[I]` The inference is that the missing piece is documentation, not protocol: the ids are reachable and labelled; what is absent is what they *mean*, which no tool can supply |

`[I]` **Nothing in the Recirculator's configuration is MCP-writable today.** This is one of the
two tool limits `index.md` records for all cards; it is referenced here, with the ranks named
above, rather than re-argued.

`[C]` How often the factory touches these (`census.json:setup_id_frequency`): `ReciType` 304 of
668 - the sixth most-written setup id - against `MastCol3` 5, `MastCol2` 2, `MastCol5` 2,
`MastCol6` 2, `MastCol1` 1 and `MastCol4` 0, i.e. **12 explicit column assignments across all 668
presets**. `[I]` The inference: presets choose a reverb character constantly and re-point a Master
column almost never, so the six columns usually sit at defaults the corpus cannot identify.

## 4. DSP cost class

**`N` in the completeness matrix - the guide states no cost for this module**
(`modules-unfilled-checklist.md` S1). Two structural facts stand in for a figure:

`[G]` `docs/EaganMatrixUserGuide.txt:1379-1381`, verbatim: "Audio input into the left channel of
the Master Section, to be processed by the Master's soft saturation, Convolution, Recirculator,
and second Convolution. The Master Section processes the stereo audio sum of all voices."

`[I]` Because the Master processes the sum of all voices, the Recirculator's cost is
**per-preset, not per-voice** - the inference is directly from that sentence, and it means
raising polyphony does not multiply the reverb's cost the way it multiplies a bank's.

`[I]` A reverb algorithm is still not free, and the only way to find out what it costs on this
device is `get_status`, which reports DSP usage. No such measurement is on record here, so the
figure is genuinely absent rather than omitted.

## 5. Typical wiring

All three examples ship decoded in `factory_catalog.json`; cell orientation is
`column <- row = value`, which is `set_matrix_point(row, col, value)` read from the column side.
Matrix columns 2-7 are "Master col 1".."Master col 6" in the tools' naming.

**`Resonant Drum 2`** (modern, fw 10.40) - the cheapest ambience in the corpus: two constants,
no formulas. `[C]` from the shipped `wiring` block (one of the 49 presets in
`preset_file.WIRING_PRESETS`):

```
recirculator = Short Reverb
Master col 5 (matrix col 6) <- Direct + = 0.7, Direct x = 3
Master col 6 (matrix col 7) <- Direct + = 0.3
Master SL (0) / SR (1)      <- Bank A = J, Bank B = M
```

`[C]` Neither column names its target: `Resonant Drum 2`'s `master_columns` is empty, so both sit
at the device default assignment. `[I]` Under the guide's stated defaults - first Recirc column
`R4` (time), second `M` (mix) - this reads as a fixed reverb time and a 0.3 wet mix, but the
inference is only as good as the assumption that the defaults have not moved, which the preset
file does not record.

**`Underwater Ceramics`** (modern, fw 10.80) - **the only one of the 49 presets with a shipped
wiring block that names a Master column at all.** `[C]`:

```
recirculator = Modulated Delay ; master_columns = {matrix col 4: "Recirc R3"}
Master col 1 (matrix col 2) <- Direct + = M = [W+X+Y+Z] W = Constant 0.2 x 10 x Macro (ii)
Master col 2 (matrix col 3) <- Direct + = 1
Master col 3 (matrix col 4) <- Direct + = I        <-- the named one: Recirc R3
Master col 4 (matrix col 5) <- Direct + = H = [W+X+Y+Z] W = Constant 1.0 x 1 x Macro (iv)
Master SL (0) / SR (1)      <- Bank A = 1
```

`[C]` The preset's macro labels are `i Speed_O_1x_2x_3x_4x_5x`, `ii Depth_Bottom_Surface`,
`iii Amb.Fdbk`, `iv Amb.Lvl`. `[I]` So macro ii drives Master column 1 and macro iv drives Master
column 4, and their names suggest a depth and an ambience level - but the inference stops there:
**only column 3 is identified, as `R3`, and what `R3` means is the void of section 1.** A reader
who concludes "column 1 is the reverb's depth" is reading a macro label, not a parameter.

**`Bird Echoer`** (modern, fw 10.39) - how a preset keeps a dry signal out of the Recirculator.
`[C]`:

```
recirculator = Modulated Delay
Dry L (9) / Dry R (10)      <- Bank A = 1          (the bank bypasses the Master chain)
Master SL (0) <- Tap 1 = 1 ; Master SR (1) <- Tap 2 = 1   (only the delay return is processed)
Master/Dry mix (8)          <- Direct + = 0.5
Master col 3 (4) <- Direct + = N ; Master col 4 (5) <- Direct + = N
Master col 6 (7) <- Direct + = 1
  N = [W+X+Y+Z] W = Constant 1.0 x 1 x Macro (i)   (macro i = "Distance_Close_Far")
```

`[C]` 30 of 668 presets drive the Master/Dry mix column and a handful drive `Dry L`/`Dry R`
(`corpus-module-wiring.md` S18c). `[I]` One letter `N` on two Master columns is the
single-knob-distance idiom: the inference is that whichever two parameters those columns drive,
they are meant to move together.

## 6. Known traps

1. **Nothing here says what `R1`..`R6` do.** Section 1's void is the first trap, because the
   labels `Recirc R1`..`Recirc R6` look like an answer `[I]`; the inference is that a name
   returned by `get_setup` is a target, not a semantic, and `MASTER_COL_TARGETS` was built from
   the header's own constant names.
2. **The Recirculator mix defaults to 0, which is off.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1419-1421`, verbatim: "The Default is 0 (100% dry = Recirculator
   Off)". A preset with a reverb algorithm selected makes no reverb until a column or the dial
   raises the mix.
3. **X, Y and Z do not reach the Recirculator directly.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1432-1437`, verbatim: "Note: Formulas affecting the recirculator
   do not consider the playing surface (X, Y and Z components) with the exception of the Touch
   Control Area when that is used to control recirculator parameters, however if you set formulas
   using XYZ on master section parameters and then set 'Use Touch Area (or all fingers averaged)',
   the formula will have the expected operation even outside the touch area - though use of Y may
   be somewhat jumpy." Stated generally too `[G]`
   `docs/EaganMatrixUserGuide.txt:1515-1516`, verbatim: "Note: Formulas affecting the Master
   Section, with the exception of SL/SR and L/R columns do not consider the playing surface (X, Y
   and Z components) with the exception of the Touch Control Area."
   **But the Recirculator is modulatable today.** `[D-cap]`
   `tests/fixtures/microdelay_wg_v1_20261025_192903.mid` decodes a stock `idMastCol1..6` that
   ships convolution 1's index and mix on Master columns 2 and 3, the Recirculator on columns 4
   and 5, and convolution 2's index and mix on columns 6 and 7 - `index.md`'s Master-chain section
   carries the full decode. `[I]` The inference: no protocol work is needed to modulate the
   Recirculator, only the Touch-Control-Area setting that makes a surface formula evaluate, and
   this project's plain-MIDI-keyboard case is exactly the one that setting is awkward for.
4. **Only SL, SR, L and R are evaluated per voice.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1471-1472`, verbatim: "In the Master Section, columns SL, SR, L,
   and R are evaluated independently for each voice. The formulaic output for all other Master
   Section columns is based on the Touch Control Area and constants." `[I]` So a per-voice
   Recirculator parameter does not exist; the inference is that any `R` modulation is global to
   the preset.
5. **Formulas on the `M` columns need a Touch Control Area.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1458-1459`, verbatim: "Formulas that use the M column require
   'Use Touch Control Area' or 'All Fingers' (in Ancillary menu). Note: Sustain pedal operation
   does not apply if you use this option." The same requirement is printed on the `SR` column
   `[G]` `docs/EaganMatrixUserGuide.txt:1392-1393`, verbatim: "Formulas in M column require use of
   Touch Control Area or 'All Fingers' in Ancillary menu."
6. **The algorithm is a wire value, not a menu position** `[G]` `docs/HakenMidi.h:1479-1487`.
   `[I]` The inference is the same one `index.md` records twice for bank types: an Editor menu's
   order has already been wrong about this device's wire values, so `RECI_TYPES`' order comes from
   the header's constants.
7. **A column adds to a dial you cannot see.** `[G]` `docs/EaganMatrixUserGuide.txt:1413-1414`
   (quoted in section 1). `[I]` The inference for an agent: reading a Master column's matrix value
   does not tell you the resulting reverb setting, and `get_setup` does not report the dials -
   only `send_raw` on cc20-cc24 touches them, blind.
