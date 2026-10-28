# The voice model - how the EaganMatrix computes a sound

This is the first file to read before building a patch. It answers one question - *how is a voice
computed?* - well enough that the module cards and `patterns.md` can be used without re-deriving
the architecture underneath them.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

The one-sentence answer, and almost everything below follows from it: **the EaganMatrix is an
additive matrix with a limiter stage, over a shared 44-letter formula namespace, persisted as a
diff against defaults.**

## What this file owns, and where everything else lives

| File | Owns |
|---|---|
| `model.md` (this file) | How a voice is computed: the matrix, the column equation, the Direct rows, the formula namespace, the Master chain, the keyboard contract, and what the MCP cannot do |
| `modules/index.md` | The nine shared module facts, the six cross-module wiring patterns, the module census, the card inventory, and the Master chain's parameter tables |
| `modules/<type>.md` | One module: its columns, units, ranges, blank-column behaviour, DSP cost, traps |
| `patterns.md` | Reusable constructions *across* modules - how to build a thing |
| `pitfalls.md` | What goes wrong, in the order you can hit it |

`model.md` and `modules/index.md` **overlap on the Master chain by design** - the chain is folded
into both rather than given a 19th module card. This file states the chain and what it means for a
voice; `index.md` owns the `idMastCol` value table, and this file cites it rather than reprinting
it. Everything else is referenced, never duplicated
(`.maister/docs/standards/global/conventions.md:10`).

## How to read the evidence tags

Tags, resolution order and the CONFLICT block are defined once, in
`.maister/docs/standards/protocol/protocol-sources.md`, "The Five Bracket Tags", and restated for
the module cards in `modules/index.md`; this file follows both and does not restate them. Two
points bear on reading the citations below: a `[G]` *header* citation is fw 10.81 while a `[G]`
*guide* citation is fw 10.80 at best, because `docs/EaganMatrixUserGuide.txt:3-4` is stamped
"Firmware Version 10.61 to 10.80"; and guide line numbers drift inside a section, so every guide
claim quotes verbatim - the quote, not the line number, is the locator.

ASCII only: `->` is an arrow, `+-` plus-or-minus, `x` multiply. The guides print arrows, curly
quotes and a plus-minus glyph; quotations here are transliterated under that rule and are otherwise
verbatim.

---

## 1. The three layers an agent must hold

Three layers, and a patch-building agent needs all three at once:

1. **Wire layer** - streams and ids. 30 streams defined, of which the MCP reaches 7; 92
   `s_Mat_Poke` configuration ids on fw 1081, 79 `s_Form_Poke` formula ids, 30 convolution ids,
   96 bank-property ids, 90 macros `[D-cap]` `tests/fixtures/microdelay_wg_v1_20261025_192903.mid`
   and the sibling captures. Fully documented by `docs/HakenMidi.h`; only partly reachable.
2. **Structure layer** - the 17 x 61 matrix, its row and column semantics (some of which are
   *preset data*, not constants), the 44-letter formula namespace, and the five shape generators
   whose *type* lives in one stream and whose *shape and phase* live in another, per formula. This
   file is the structure layer `[I]`, and the inference is simply that a document cannot be read in
   three places at once, so the layers are split across files.
3. **Convention layer** - what Haken's own authors actually do. `[C]` 646 of 668 factory presets
   use a Direct additive row, 602 of 668 modulate with Z, 553 of 668 use the multiply row, and
   493 of 668 set a negative formula height (`census.json:techniques`).

`[I]` A skill that knows only layer 1 emits valid messages that sound wrong; a skill that knows
only layer 3 cannot explain itself or recover from an error. That is the inference behind the whole
knowledge base being split the way it is.

---

## 2. The matrix: 17 rows by 61 columns

A **row** is a signal or a constant, a **column** is a destination parameter, and a **cell** holds
a formula letter or a constant that scales the row into the column `[G]`
`docs/HakenMidi.h:649-667` (`ccRow`) and `docs/HakenMidi.h:668-730` (`ccCol`).

`[G]` `docs/HakenMidi.h:649-667` - 17 rows, `ccRow = 40`:

| Row | Meaning |
|---|---|
| 0 | `rNoise`, noise samples source |
| 1-5 | `rOscFil1..5`, the five oscillator/filter slot outputs |
| 6-8 | `rA`, `rB`, `rC`, the Bank A/B/C outputs |
| 9-10 | `rAudioL`, `rAudioR`, external audio in - **or delay taps, see section 5** |
| 11-12 | `rSubL`, `rSubR`, the Master submix fed back - **or delay taps, see section 5** |
| 13-14 | `rDirect1`, `rDirect2`, the two Direct + rows |
| 15 | `rNegDirect`, the Direct - row |
| 16 | `rMultiply`, the Direct x row |

`[G]` `docs/HakenMidi.h:668-730` - 61 columns, `ccCol = 41`: 0-1 Master `SL`/`SR`; 2-7 the six
assignable Master columns; 8 the Master/Dry mix `M`; 9-10 dry `L`/`R`; 11 separator; 12-26 the five
oscillator/filter slots as In/Frequency/Bandwidth triples; 27-34 Bank A; 35-42 Bank B; 43-50
Bank C; 51-60 the five shape generators as Frequency/Trigger pairs.

`[D]` `CLAUDE.md:15-17`, 2026-10-25, fw 10.81 confirms the Master half on the device: columns 2..7
are 6 assignable Master columns, 8 = Master/Dry mix, 9/10 dry L/R, 11 separator; banks have 8
columns each.

`[G]` `docs/EaganMatrixUserGuide.txt:1617-1618`, verbatim: "The EaganMatrix has five 3-column
Oscillator/Filter/Multiplier slots; each of the five is configurable as a number of different types
of Oscillator" - which is why 15 columns cover five slots.

`[C]` The corpus fills very little of that space: 17,591 non-blank cells in 668 presets - an
average of 26 of the 1,037 available - at most 68 in any one preset, and 19 presets with an empty
matrix (`census.json:matrix_cells`). A patch is a sparse object; do not try to fill the grid.

---

## 3. How a column is computed - the one equation

This is the generative rule; everything about blank columns, Via Limiter and the Direct rows
follows from it:

`[G]` `docs/EaganMatrixUserGuide.txt:5206-5211`, verbatim: "Technical details about evaluating each
column in a matrix: First, each formula in the column that has 'Via Limiter' is multiplied by its
matrix row; the sum of these is clipped to the range -1/4..1/4; then other formulas in the column
are multiplied by their matrix rows; the sum of these is added to the Limiter result; finally, that
result is multiplied by the formula (if any) in the column's Multiply row."

```
columnValue = ( clip(-0.25..0.25)( sum of Via-Limiter formula x row )
                + sum of other formula x row )
              x f(Direct x)
```

`[D]` `RECIPES.md:93-94`, 2026-10-25, fw 10.81 states the multiply half independently - "Direct x
is the column's multiply row: column value = (sum of other rows) x f(Direct x)" - and the two
agree exactly.

Three consequences, each of which changes how you wire:

- **Via Limiter is a stage, not a safety net.** The `+-0.25` clip happens *before* the unlimited
  formulas are added, so an unlimited formula in the same column passes the limiter untouched
  `[I]`; the inference is read directly off the order of operations in the quoted sentence.
- **`Direct x` multiplies the whole sum**, it does not contribute a term. A blank multiply row is
  not a zero `[I]` - the inference is that a factor of zero would silence every column without one,
  and `[C]` 553 of 668 presets use the row while the other 115 still make sound.
- **`Direct +` is a constant 1.** `[G]` `docs/EaganMatrixUserGuide.txt:716`, verbatim: "A Direct+
  row has a constant value of 1, instead of a variable value like Osc3's output." So a formula
  placed on a Direct row contributes itself, unscaled - which is how a patch gets a bare number or
  a wheel-driven offset into a column. `[C]` 646 of 668 presets do this
  (`census.json:techniques:direct_additive_row`).

`[G]` `docs/EaganMatrixUserGuide.txt:5200-5204`, verbatim: "A special use for Via Limiter is in the
first two matrix columns, which feed into the Master Section's saturation waveshaper. The limiter
together with this waveshaper results in soft clipping, with a sine -pi/2..pi/2 transfer function."
That is the deliberate-overdrive idiom; `-pi/2..pi/2` is the guide's glyph transliterated.

### What a matrix cell can actually hold

A cell is **not** a number field. `[G]` `docs/EaganMatrix Preset Cookbook.txt:221-224`, verbatim:
"Whole number (1-9) or fractional constant can be used (.nnnn). 1.22 is not allowed. 12 is not
allowed." The User Guide says the same from the editing side `[G]`
`docs/EaganMatrixUserGuide.txt:6143-6146`, verbatim: "Constants containing whole and fractional
parts are not allowed - 1.25, 3.5, etc. - they must be input as formula constants or built up with
multiple Direct + entries if applicable".

So: **whole 1..9, or a decimal `.n` to `.nnnn`, and nothing else.** A value like 1.25 is composed
across rows - a `1` on one `Direct +` row and `.25` on the other - or moved into a formula's W
constant. Going past 9 on a shape-generator rate column uses the same trick `[G]`
`docs/EaganMatrix Preset Cookbook.txt:221-224`, verbatim: "Using whole multipliers to create a
large whole number < 100 is common for SG Frequency Specification."

`[I]` **No validation guard for this exists in `set_matrix_point`** - the inference is from the
tool surface: the value argument is passed to the matrix-code encoder with no composite-number
check, so an impossible constant fails at the device rather than at the call.

The wire codes behind a cell: `[D]` `CLAUDE.md:63`, 2026-10-25, fw 10.81 - "codes: 0 blank,
1..22 A..V, 23..44 A'..V', 45..48 W..Z, 49 decimal, 50..58 = 1..9, 59/60 squared/cubed", with the
decimal digits carried on `cc43`/`cc42`.

### Disable a cell, never clear it

`[G]` `docs/HakenMidi.h:764`: `matDisBit = 64`, "bit set if matrix point disabled" - a disabled
cell is still a cell. `[G]` `docs/EaganMatrixUserGuide.txt:6133`, verbatim: "To disable a formula
select it in the matrix and then press the space bar. To reenable press the space bar again."

`[I]` **Removing a formula from the matrix deletes the formula on save.** The inference is from the
file format: the preset stores the matrix as a cleared grid plus its non-blank cells, so a letter
with no remaining cell has nothing to be written from. Disable the cell to silence a formula you
want to keep.

---

## 4. The formula namespace - 44 letters, shared device-wide

`[G]` `docs/HakenMidi.h:749-754`: `matA = 1` ("A = first formula") through `matV_ = 44`
("V' = last user-defined formula"), with `nUForms` the count. The header says the same from the
other direction at `docs/HakenMidi.h:1329`: `idBlMacForm = 68`, "accessory for idBlend: macro 0..95
or formula 0..44".

**The pool is 44, not 22.** Several project documents still say 22; they predate the `A'..V'` half.
The honest working rule is **44 available, A..V preferred** `[I]` - the inference is that the
Cookbook's worked examples never leave A..V, so a patch that stays there is the one a human reader
will recognise.

Three properties make letter allocation a correctness problem, not a style choice:

- **Letters are shared.** `[D]` `CLAUDE.md:93`, 2026-10-25, fw 10.81: "Formula letters are shared:
  editing a cell's formula changes all cells using that letter." This is used deliberately - one
  letter in both `Master SL` and `Master SR` is the standard stereo idiom.
- **The dump under-reports which letters are taken.** `[D]` `CLAUDE.md:94`, 2026-10-25, fw 10.81:
  "The Module omits matrix cells whose formula is all zero from the matrix dump." A letter can be
  defined and invisible.
- **So pick a letter by checking `get_matrix` first, and verify after writing** `[I]`; the
  inference is that an unchecked letter collision silently rewrites another part of the patch, and
  the two facts above make the check cheap and the collision expensive.

A formula is built from four components - W, X, Y, Z - combined by one of five operators `[D]`
`CLAUDE.md:117-118`, 2026-10-25, fw 10.81: "Formula operator: id 38 (0 W+X+Y+Z, 1 Wx(X+Y+Z),
2 (W+X+Y)xZ, 3 (W+X)x(Y+Z), 4 (WxX)+(YxZ))."

---

## 5. Rows 9-12 are not always Audio In and Sub

`[I]` This is the row-semantics fact most likely to produce a wrong patch, and the inference is
that the row *labels* are preset data rather than constants, so a label read from a static table
can be wrong for the preset actually loaded.

`[G]` `docs/HakenMidi.h:1634-1643`: `idRowTyp1 = 106` reassigns the Audio L/R rows
(`rt1Aud = 0` Audio L and R, `rt1Tap = 1` Tap 1 and Tap 2, `rt1AudTap = 2` mono-mix audio plus
mono-mix taps), and `idRowTyp2 = 107` reassigns the Sub L/R rows (`rt2Sub = 0`, `rt2Tap = 1`
Tap 3 and Tap 4, `rt2SubTap = 2`, `rt2Aud = 3`, `rt2AudTap = 4`).

`[D-cap]` Decoding stream 20 of `tests/fixtures/microdelay_wg_v1_20261025_192903.mid` gives
`idRowTyp1 = 1` and `idRowTyp2 = 1`: in that preset rows 9-12 are Tap 1, Tap 2, Tap 3 and Tap 4,
not Audio In and Sub. `[C]` 61 of 668 factory presets write `RowTyp1` explicitly and 26 of 668
write `RowTyp2` (`census.json:setup_id_frequency`), so the alternates are not exotic.

`[I]` **This is how delay taps reach the matrix at all** - the inference is that without these two
selectors there are no Tap rows to wire. `eagan_mcp/setup.py:80-84` carries the two value tables,
and `get_matrix` and `set_matrix_point` now label rows 9-12 from the preset's own decoded setup
rather than unconditionally, so the labels and the cells agree.

---

## 6. The Master chain

The Master section is a fixed serial chain and the one part of the instrument that is not the
matrix `[G]` `docs/EaganMatrixUserGuide.txt:1475`, verbatim: "The Master produces a stereo submix
as follows:".

`[G]` `docs/EaganMatrixUserGuide.txt:1476-1478`, verbatim: "Stereo sum (SL, SR) from all voices ->
Pre-Level -> Compressor/TanH -> Limiter -> DC Filter -> Pre-Recirculator Convolution ->
Recirculator -> Post-Recirculator Convolution -> Submix -> Final Mix (add in L/R from all voices to
submix) -> Tilt EQ -> Post Level -> Attenuation".

What a patch-builder must take from the chain:

- **SL/SR go through everything; L/R bypass it.** `[G]` `docs/EaganMatrixUserGuide.txt:1461-1462`,
  verbatim: "Input into left channel of the Master. This input is not processed by saturation,
  Convolutions, and Recirculator." And again of the output side `[G]`
  `docs/EaganMatrixUserGuide.txt:1499`, verbatim: "Also, no waveshaping is done on the Master L and
  R columns." So `L`/`R` is the dry path, `SL`/`SR` the processed one.
- **The submix is the only global feedback path.** `[G]`
  `docs/EaganMatrixUserGuide.txt:1481-1482`, verbatim: "The Master's submix is fed back into the
  matrix on the Sub L and Sub R matrix rows, for optional further processing." `[I]` Switching
  `idRowTyp2` to a tap alternate (section 5) removes that path - the inference is that one pair of
  rows cannot be two things at once.
- **The assignable Master columns add into a dial, they do not replace it.** `[G]`
  `docs/EaganMatrixUserGuide.txt:1413-1414`, verbatim: "The column value (scaled 0..1) will be
  added to the corresponding Recirculator Control Dial value (cc20..cc24 scaled 0..127; see
  Continuum User Guide)."
- **What each assignable column drives is selected by `idMastCol1..6 = 27..32`** `[G]`
  `docs/HakenMidi.h:1488-1500`. The 20-value table is owned by `modules/index.md` and reproduced in
  `eagan_mcp/setup.py:92-96`; this file does not restate it.

`[C]` The corpus barely touches the selectors: the most-written of them, `MastCol3`, is explicit in
5 of 668 presets and all six together account for 12 explicit writes
(`census.json:setup_id_frequency`), so nearly every preset runs the stock assignment.

---

## 7. The keyboard contract - a plain MIDI keyboard on channel 1

`[I]` This is the contract to understand before any other; the inference is that the factory
library and a plain MIDI keyboard disagree about where expression comes from, which the corpus
figures at the end of this section make concrete.

`[G]` `docs/ContinuumUserGuide.txt:5384-5394` names the whole thing in one paragraph, verbatim in
part: "midi notes received on channel 1 (The MPE Master Channel for the Lower Zone) is treated in a
special fashion so that single channel Midi devices can be interpreted by the EaganMatrix
polyphonically ... Ch 01 pitch bend (which is on a per note basis in MPE) is globally reassigned to
each of these notes. Ch 01 velocity for each note is interpreted as an initial state (one value) Z.
Y, like pitch bend, is usually mapped to receive from Ch01 CC01 (modulation) ... up to the maximum
polyphony (8 on an EaganMatrix module). Voice stealing (by oldest note) will occur once the
polyphony limit is reached."

Decoded into the six elements of the contract:

1. **Z is frozen at note-on.** Channel-1 velocity becomes Z as "an initial state (one value)" and
   does not move for the life of the note `[G]` `docs/ContinuumUserGuide.txt:5392-5393`.
2. **Bend range defaults to +-96 semitones.** `[G]` `docs/HakenMidi.h:1370-1372`:
   `idBendRange = 40`, `defBendRange = 96`, "default bend range is max". `[C]` the id is written
   explicitly in only 18 of 668 factory presets (`census.json:setup_id_frequency:BendRange`), so
   nearly the whole library sits at the default. `[D]` `CLAUDE.md:147`, 2026-10-25, fw 10.81
   records the write path and that it is not readable back: "Bend range = s_Mat_Poke id 40
   (97 = 96:2). Not readable back; verify with listen". **Set it explicitly on every patch.**
3. **Pitch bend is global**, reassigned to every sounding note at once `[G]`
   `docs/ContinuumUserGuide.txt:5391-5392` - so bend is not a per-note gesture on this rig.
4. **Y is global and arrives on CC 1.** `[D]` `CLAUDE.md:119`, 2026-10-25, fw 10.81: "MIDI in:
   CC 1 (mod wheel) is read as Y (Continuum guide). Macros i..iv = ch1 CC 12..15". `[D]`
   `RECIPES.md:38-39 (moved to pitfalls.md section 10, item 75)`, 2026-10-25, fw 10.81 makes it the design rule: "Mod wheel: CC 1 arrives as
   Y. Build the patch to use Y. Do not suggest remapping the user's keyboard as the default fix."
5. **Y may not fall at release.** A mod wheel holds its position through note-off `[I]`, and the
   inference is mechanical: nothing in the note-off path writes CC 1. So a patch where Y scales
   output level has notes that never end. This is unresolved on the device (section 10).
6. **Z must stay on MPE/MPE+ or channel 1 collapses to mono.** `[G]`
   `docs/ContinuumUserGuide.txt:12047-12049`, verbatim: "Note: Z is normally set to MPE in Midi I/O
   on control panel 3 in the Haken Editor. Setting Z to any other CC or channel-pressure will cause
   the module only accept polyphony 1 monophonic input when played with standard Midi on
   Channel 1." `[I]` The same pinning is usually stated for Y as well; the inference here is
   narrower than the research's - the guide states the mono consequence for **Z only**, and Y's
   channel-1 mapping is the "usually mapped to receive from Ch01 CC01" sentence above, which is a
   default, not a constraint.

### Why this matters: the factory library leans on the one input that cannot move

`[C]` Z dominates the corpus. `VEndZ` appears in 2,462 of 7,259 factory formulas against `VEndY`
1,135 and `VEndX` 1,130 (`census.json:formula_id_frequency_by_formula`), and `z_modulation` fires
in 602 of 668 presets against 531 for Y and 510 for X (`census.json:techniques`). Z is used in
roughly twice as many formulas as either of the other two.

`[I]` So the majority of factory expressivity lands on the one input that is frozen at note-on on a
plain keyboard. Three consequences, each inferred from that single fact:

- A ported factory patch will feel **static**, not broken `[I]` - the inference is that Z is
  present in the patch and simply never moves.
- **Build continuous control around Y** and then handle its release problem `[I]`, the inference
  being that Y is the only continuous input a plain keyboard can still move mid-note.
- **The general remedy is a gated W.** `[G]` `docs/ContinuumUserGuide.txt:12045`, verbatim: "For
  most presets, Z alone will not have any effect ules you also gate with W." The PDF extraction
  drops letters: read "ules" as "unless". The emendation is stated here rather than written into
  the quote, because the quote is the locator. `[I]` Generalised: wrap any component that does
  not self-zero at note-off in a W gate - the inference is that W is the only component the
  note-off path drives to zero, which makes it the one safe fix whichever way the Y-at-release
  question resolves.

### The firmware's own answer exists and is unreachable

`[G]` `docs/HakenMidi.h:1326-1328`: `idBlend = 39` with value `psCh1Note` (value 4), the switch that
lets a formula use one value from the playing surface and another from channel 1 - exactly this
project's problem. `[I]` **No MCP tool sets it**; the inference is from the tool surface, where
`set_formula` exposes no blend argument and id 39 is not in its writable set.

### Macros

`[D]` `CLAUDE.md:119`, 2026-10-25, fw 10.81: macros i..iv arrive as **ch1 CC 12..15**. `[G]`
`docs/HakenMidi.h:540` shows six, not four: `ccI=12,ccII=13,ccIII=14,ccIV=15,ccV=16,ccVI=17`. On
this device they behave unusually `[G]` `docs/HakenMidi.h:533-535`, verbatim: "On the EaganMatrix
Module (E2x) only, macros i..iv are a special case. The E2x receives ccI..ccIV to provide offsets
for the E2x i..iv CV inputs (like rotary)." - an **offset**, not the value.

---

## 8. What the MCP cannot do

Honest limits - each one is something a plain-words request can ask for and the tools cannot
deliver:

| Wanted | Why not |
|---|---|
| An envelope **release** | There is no ADSR; release is *persistence*, formula id 63 - `idPersist = 63` `[G]` `docs/HakenMidi.h:1323`. `eagan_mcp/formula.py:121` decodes it (`PERSISTENCE_IDS`), so id 63 is now readable and still not writable by any typed tool |
| **Ancillary** anything | The whole ancillary mechanism is unreachable from the typed tools `[G]` `docs/HakenMidi.h:1315` (`idAncTAorAll = 11`) and the ids around it. `[C]` `ancillary_math` fires in 513 of 668 presets, so this is a real hole, not a corner |
| **Blend** / a secondary formula | `idBlend = 39` and the whole secondary id set `[G]` `docs/HakenMidi.h:1326-1335`. `[C]` `blend_secondary_formula` fires in 362 of 668 presets |
| **Mute a cell** | The device accepts `matTogMute = 121`, `matSetMute = 122`, `matClrMute = 123` `[G]` `docs/HakenMidi.h:788-790`, and the disable bit is `matDisBit = 64` `[G]` `docs/HakenMidi.h:764`. `[I]` No typed tool sends any of them - the inference is from the tool surface, where `set_matrix_point` writes a value code and never a mute operation |
| **Bank properties** | The Kinetic and biquad/sine bank property streams have no codec at all `[I]`; the inference is that `eagan_mcp/setup.py` decodes `s_Mat_Poke` only, so those ids arrive in captures and are discarded |
| **An arbitrary constant in a cell** | "1.25" is not expressible (section 3); decompose it across Direct rows, and note there is **no validation guard** for it `[I]` |

Two escape hatches, and they are untyped: `write_formula_raw` (marked `EXPERIMENTAL`) sends
arbitrary `(id, value)` pairs into stream 19, and `send_raw` sends arbitrary MIDI `[I]`. The
inference is that anything in the table above is physically reachable through one of those two and
unreachable through a checked, verified tool - which is the difference that matters when an agent
is building unattended.

### No automatic gain protection

`[G]` `docs/EaganMatrixUserGuide.txt:6566-6570`, verbatim: "Reduce Gain Message (deprecated) ...
Detection and suppression are only performed while the Editor is running, and only when the
Overload Protect indicator is lit." `[I]` Windows MIDI ports are exclusive and the MCP holds the
port, so during MCP patch-building there is **no gain protection at all** - the inference is
immediate from the two facts together, and an agent reasoning from the feature's existence will
assume protection that is not there.

The replacement is guide section 13 `[G]` `docs/EaganMatrixUserGuide.txt:8411-8452`, five numbered
rules, quoted in brief:

| # | Rule | Line |
|---|---|---|
| N1 | "Never use constants in output formulas - and unless you know what you are doing never ever use them past unity (1) anywhere else" | `[G]` `docs/EaganMatrixUserGuide.txt:8428-8430` |
| N2 | "Never use large values (that would be past 0.1 in most cases and in many cases 0.05) when programming noise output or Bi-quad inputs" | `[G]` `docs/EaganMatrixUserGuide.txt:8438-8440` |
| N3 | "Don't just plug in default 'Z' everywhere ... Use a formula that caps Z at maybe 30-50%" | `[G]` `docs/EaganMatrixUserGuide.txt:8442-8444` |
| N4 | "Starting out don't just experiment willy nilly with noise and Bi-quads ... Start with existing presets" | `[G]` `docs/EaganMatrixUserGuide.txt:8446-8448` |
| N5 | "Put a free macro as a Multiplier (down to zero) on the SL/SR columns to mute sound or if using a controller you can create a mute button (ch1 cc18 0 =Mute, 1=Unmute)" | `[G]` `docs/EaganMatrixUserGuide.txt:8450-8452` |

`[I]` **No typed tool reaches the N5 mute path** - only `send_raw`. The inference is from the tool
surface: no tool emits a bare channel-1 CC. The macro-multiplier half of N5 *is* reachable, through
an ordinary matrix write, and is the form to prefer.

And check the budget after every change `[D]` `RECIPES.md:47 (moved to pitfalls.md section 7, item 54)`, 2026-10-25, fw 10.81: "Check with
get_status (dsp_usage_percent, dsp_polyphony) after every big change."

---

## 9. Three obstacles that a plain reading of the guide hides

1. **X/Y/Z do not reach the Recirculator or the Convolutions directly - but they do reach them.**
   The guide says the first three times that the Master effects are driven by dials and the Touch
   Control Area. `[D-cap]` Decoding stream 20 of
   `tests/fixtures/microdelay_wg_v1_20261025_192903.mid` gives ids 27-32 = 16, 17, 3, 6, 18, 19,
   i.e. Master columns 2-7 are driving Conv 1 Interp, Conv 1 Mix, Recirc R4, Recirc Mix, Conv 2
   Interp and Conv 2 Mix in a stock preset. So "put the reverb on the wheel" works **today**, with
   no tool or protocol work - only labelling, which `eagan_mcp/setup.py:92-96` now provides. `[G]`
   `docs/HakenMidi.h:1494-1500` gives the reachable set: 7 Recirculator targets and 4 convolution
   targets out of 20 assignable values.
2. **A Master `M`-column formula costs the sustain-pedal gesture.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1458-1459`, verbatim: "Formulas that use the M column require
   'Use Touch Control Area' or 'All Fingers' (in Ancillary menu). Note: Sustain pedal operation
   does not apply if you use this option." And the escape is narrower than it looks `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:665`, verbatim: "The Touch Area (Not Supported on
   ContinuuMini or EaganMatrix Module)" - leaving only All Fingers Averaged. On a plain keyboard
   that trades the one pedal gesture available for a master-mix gesture.
3. **A matrix cell cannot hold an arbitrary number** (section 3), and nothing checks it `[I]`.

---

## 10. Conflicts - both sides standing

Four conflicts are owned by this document's subject area. `[I]` The category's own conflict files
are not present in the repository, so ownership was re-derived from the merged register in
`analysis/research-context/synthesis.md` section 9 by subject - the inference is that a conflict
about the matrix codes, the keyboard, Z's modes or the Touch Area is voice-model material wherever
it was originally filed. Both sides of each were re-measured against the cited files.

```
CONFLICT: matrix value code 48 - W..Z letter vs z-squared
  docs   [G]: "matZZ = 48, // z squared"
              - docs/HakenMidi.h:758
  device [D]: "codes: 0 blank, 1..22 A..V, 23..44 A'..V', 45..48 W..Z, 49 decimal"
              - CLAUDE.md:63, 2026-10-25, fw 10.81
  follows: the header, by resolution order. Code 48 is Z *squared*, not plain Z - there is
           no plain-Z code. A pressure mapping written as "Z" through code 48 is squared,
           which is also why velocity lands near 0.25 of full amplitude at mid velocity.
           The device note is right about the span 45..48 and loose about the last member.
```

```
CONFLICT: Z release mode - cReleaseF = 3 vs the 1044 Editor's 4/5
  docs   [G]: "cRelative = 3, // for formula's X and Y components only" then
              "cReleaseF = 3, // for formula's Z component only" and "cReleaseP = 4"
              - docs/HakenMidi.h:1256-1260
  docs   [G]: the 10.44 Editor's live transmit table numbers Z release 4/5 with 3 = Relative,
              and contradicts itself elsewhere in the same patch
              - analysis/research-context/synthesis.md:887
  follows: the header, by resolution order - id 6 value 3 is Release F on a Z component and
           Relative on an X or Y component, i.e. the number is component-dependent. Writing
           the Editor's numbering would select Relative and the release pulse would never
           fire. Not device-tested.
```

```
CONFLICT: idAncTAorAll - one boolean vs two distinct choices
  docs   [G]: "idAncTAorAll = 11, // false = normal, true = Touch Area / All Fingers;
              required in Master"
              - docs/HakenMidi.h:1315
  docs   [G]: "Formulas that use the M column require 'Use Touch Control Area' or
              'All Fingers' (in Ancillary menu)."
              - docs/EaganMatrixUserGuide.txt:1458
  follows: both stand. The header carries one bit where the Editor offers two options, so the
           choice between Touch Area and All Fingers may be unreachable over MIDI. On this
           device it may not matter: Touch Area is unsupported here
           (docs/EaganMatrix Preset Cookbook.txt:665), leaving All Fingers as the only
           meaning the bit can have. Unresolved; device-gated.
```

```
CONFLICT: Midi Note Processing mode numbering - six modes vs eight
  docs   [G]: "idNoteMode = 2" with six values MStatic 0, MVeloc 1, MFormula 2, MNoNote 3,
              MMidC 4 (Moog Theremin), MAnnounce 5 - no External Note Mode, no Kyma
              - docs/HakenMidi.h:1412-1418
  docs   [G]: "cc 43 Selects note processing mode: 0 constant 127, 1 velocity, 2 formula,
              3 No note output, 4 Ethervox mode, 5 Kyma mode"
              - docs/ContinuumUserGuide.txt:8232-8237
  docs   [G]: eight modes, with External Note Mode = 5, Ethervox = 6, Kyma = 7
              - docs/ContinuumUserGuide.txt:5325-5374
  follows: the header, by resolution order - and it supersedes both guides. The practical
           consequence for this project is the useful one: External Note Mode is not a
           selectable idNoteMode value at all, so channel-1 polyphonic handling is not
           something a patch turns on. Do not try to select it.
```

Two further conflicts were measured against the cited files while writing this file, and are
recorded here because they bear directly on the sections above:

```
CONFLICT: ch1 cc18 - mute button vs post level
  docs   [G]: "you can create a mute button (ch1 cc18 0 =Mute, 1=Unmute)"
              - docs/EaganMatrixUserGuide.txt:8451-8452
  docs   [G]: "ccPost = 18, // samples generation output level after Master Section"
              - docs/HakenMidi.h:577
  follows: the header, by resolution order - cc18 is a continuous post level, so 0 mutes and
           1 is 1/127 of full level, not "unmute". The guide's mute half is correct and its
           unmute half is not. Prefer N5's other form, a free macro multiplying SL/SR, which
           is an ordinary matrix write and restores exactly.
```

```
CONFLICT: how many macros - i..iv vs i..vi
  docs   [G]: "ccI=12,ccII=13,ccIII=14,ccIV=15,ccV=16,ccVI=17"
              - docs/HakenMidi.h:540
  device [D]: "Macros i..iv = ch1 CC 12..15"
              - CLAUDE.md:119, 2026-10-25, fw 10.81
  follows: the header, by resolution order - six macros exist on cc12..cc17 and the project's
           note stops at four because only four were tested. Treat v and vi as available but
           untested; the device note is not wrong, only incomplete.
```

---

## 11. Standing hazards recorded here because they outlive a session

- **Negative formula heights already stored on the device are still wrong.** The codec fix repairs
  what is written from now on; it does **not** repair heights already saved into user slots. `[D]`
  `CLAUDE.md:163`, 2026-10-25, fw 10.81 records "Harkonnen Voice" (user slot 5) as Bank B `Sh`
  formula E with "Y wheel 0 -> -0.2", and `CLAUDE.md:168-169` records "Sitar Modal Pluck"
  (user slot 4) re-saved with a volume fix. `[I]` Those cells must be **rewritten on the device**
  before either preset is trusted - the inference is that a stored preset holds the raw wire value,
  which no code change can reach.
- **Do not pass `set_preset_name`'s description argument.** `[I]` Stream 1 is unresolved - the
  device note calls it the description and the header plus the corpus read it as the panel macro
  labels - so writing it may destroy a preset's macro labels. The inference is that an unresolved
  identity on a destructive write is a reason not to write. Name only, until stream 1 is settled.
- **Y at release is the open question that shapes every mod-wheel patch** (section 7, element 5)
  `[I]`; the inference is that if Y holds its value through note-off, "build around Y" without a
  gated W multiplier is a trap rather than a recipe.

---

## Where to go next

- Module columns, units and traps: `modules/index.md`, then the card for the module.
- Reusable constructions: `patterns.md`.
- What goes wrong and in what order: `pitfalls.md`, and `RECIPES.md` at the repository root.
- Wire formats: `docs/HakenMidi.h`, which is the source of truth for every message in this file.
