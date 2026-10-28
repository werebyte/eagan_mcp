# Convolution

Card 18 of 18. Two convolution engines in the Master section - one before the Recirculator, one
after - each interpolating between **four** impulse responses chosen from a fixed set of
**nineteen**.

**Convolution is not a bank type.** It is not a value of `idBankA`, `idBankB` or `idBankC` and it
is not an oscillator/filter slot mode; it has its own property stream, `s_Conv_Poke` = **stream
26** `[G]` `docs/HakenMidi.h:1141`, read back as `s_Conv` = **stream 14** `[G]`
`docs/HakenMidi.h:1113`, header comment "Convolution Parameters (max 30 sData)". `[C]` It is not
one of the 37 module keys in `census.json:modules_used_including_defaults`, so it has no row in
`index.md`'s frequency table; the corpus counts it as a technique instead - `convolution` appears
in **107 of 668** presets (`census.json:techniques`).

Its only matrix surface is the **assignable Master columns**, whose selector table, "adds into the
dial" semantics and capture-verified stock assignment belong to `index.md`'s Master-chain section
and are referenced here, not restated. The Master chain itself - what feeds each convolution and
in what order - is `index.md`'s and `model.md`'s.

Guide section 6.1, `docs/EaganMatrixUserGuide.txt:1375-1530`. Header: the `s_Conv_Poke` id block.

---

## 1. Columns

Convolution has **no columns of its own**. Four of the twenty assignable Master-column values
reach it, two per engine:

| Assignable value | Target | Engine |
|---|---|---|
| 16 | `Conv 1 Interp` | pre-Recirculator `[G]` `docs/HakenMidi.h:1500`, header comment "column adds into conv parameter" |
| 17 | `Conv 1 Mix` | pre-Recirculator `[G]` `docs/HakenMidi.h:1500` |
| 18 | `Conv 2 Interp` | post-Recirculator `[G]` `docs/HakenMidi.h:1500` |
| 19 | `Conv 2 Mix` | post-Recirculator `[G]` `docs/HakenMidi.h:1500` |

`[G]` `eagan_mcp/setup.py:96` reproduces the names as `MASTER_COL_TARGETS`: `Conv 1 Interp`,
`Conv 1 Mix`, `Conv 2 Interp`, `Conv 2 Mix`.

What the two reachable controls do:

| Control | Meaning |
|---|---|
| `I` (Interp) | `[G]` `docs/EaganMatrixUserGuide.txt:1396-1401`, verbatim: "A value in the range 0 to 3. Controls an interpolation between four Convolution responses. Select the responses, as well as a length and tune value (spectral shift) for each response, in the Convolution area below the matrix. Responses available include: Wood, Metal, Fiber, Waterphone, Waterphone2, Autoharp, Autoharp2, Guitar and Snap. Currently the user cannot add Convolutions of their own. This applies to pre-Recirculator Convolution." The post-Recirculator wording is the same `[G]` `docs/EaganMatrixUserGuide.txt:1442-1446` |
| `M` (Mix) | `[G]` `docs/EaganMatrixUserGuide.txt:1407-1409`, verbatim: "Dry/wet mix of the pre-Recirculator Convolution output, 0 = dry, 1 = 100% wet, .5 = 50% wet/dry, etc." For the post engine the guide adds "0 = dry (off)" `[G]` `docs/EaganMatrixUserGuide.txt:1448-1450`, verbatim: "Dry/wet mix of the post-Recirculator Convolution output, 0 = dry (off), 1 = 100% wet, .5 = 50% wet/dry, etc." |

**Everything else about a convolution lives in `s_Conv_Poke`, not in the matrix.** Thirty ids
`[G]` `docs/HakenMidi.h:1789-1823`:

| ids | Parameter |
|---|---|
| `id_c_idx1 = 0`, `id_c_mix1 = 1` | index and mix for the **1st** convolution, which add into its `I` and `M` columns `[G]` `docs/HakenMidi.h:1789-1790` |
| `id_c_idx2 = 2`, `id_c_mix2 = 3` | the same for the **2nd** convolution `[G]` `docs/HakenMidi.h:1791-1792` |
| `id_c_dat0..dat3 = 4..7` | **which IR** sits in each of the four interpolation slots `[G]` `docs/HakenMidi.h:1793-1796` |
| `id_c_lth0..lth3 = 8..11` | length of each IR `[G]` `docs/HakenMidi.h:1802-1805` |
| `id_c_shf0..shf3 = 12..15` | shift, the spectral tune, of each IR `[G]` `docs/HakenMidi.h:1806-1809` |
| `id_c_wid0..wid3 = 16..19` | width of each IR `[G]` `docs/HakenMidi.h:1810-1813` |
| `id_c_atL0..atL3 = 20..23` | left attenuation of each IR `[G]` `docs/HakenMidi.h:1814-1817` |
| `id_c_atR0..atR3 = 24..27` | right attenuation of each IR `[G]` `docs/HakenMidi.h:1818-1821` |
| `id_c_phc = 28` | `[G]` `docs/HakenMidi.h:1822`, header comment "enable phase cancellation compensation (true/false)" |
| `id_c_pad = 29` | `[G]` `docs/HakenMidi.h:1823`, header comment "zero pad to make even number of bytes in s_Conv" |

**The nineteen impulse responses** `[G]` `docs/HakenMidi.h:1797-1801`: `0 Waterphone1`,
`1 Waterphone2`, `2 Autoharp1`, `3 Autoharp2`, `4 GuitarDark`, `5 FingerSnap`, `6 Wood`,
`7 MetalBright`, `8 Fiber`, `9 Leather`, `10 MetalDamped`, `11 Nylon`, `12 Cloth`,
`13 EowaveGongSnapshot`, `14 LVDLPyramidSnapshot`, `15 LVDLGongSnapshot`, `16 LVDLOndeSnapshot`,
`17 White`, `18 Grey`.

```
CONFLICT: how many impulse responses exist - 9 in the guide vs 19 in the header
  docs   [G]: "Responses available include: Wood, Metal, Fiber, Waterphone, Waterphone2,
              Autoharp, Autoharp2, Guitar and Snap. Currently the user cannot add Convolutions
              of their own."
              - docs/EaganMatrixUserGuide.txt:1398-1400
  header [G]: nineteen, cd_Waterphone1 = 0 .. cd_Grey = 18
              - docs/HakenMidi.h:1797-1801
  follows: the header, under the resolution order ([G] header > [G] guide). The guide's list
           would hide ten IRs, among them Leather, Nylon, Cloth, three instrument snapshots and
           the two noise responses; it also prints one "Metal" where the header has MetalBright
           and MetalDamped, so "metal" is ambiguous in guide terms. The guide's separate claim
           that a user cannot add their own responses is NOT contradicted and still stands.
```

## 2. Units, ranges and blank-column behaviour

**Blank-column behaviour: `-`, not applicable.** Convolution has no bank columns, so there is no
blank-cell question to answer `[I]`; the inference is structural, from section 1. This is why the
completeness matrix marks the field `-` for this module (`modules-unfilled-checklist.md` S1).

**Units and ranges: `N`, absent for everything except the two matrix controls.** The completeness
matrix marks the field `N` `[I]`. What is known and what is not:

| Quantity | Units / range | Source |
|---|---|---|
| `I` (Interp) | **0 to 3** - a position along four responses, not an index into nineteen | `[G]` `docs/EaganMatrixUserGuide.txt:1396` (quoted in section 1) |
| `M` (Mix) | 0 = dry, 0.5 = half, 1 = 100% wet | `[G]` `docs/EaganMatrixUserGuide.txt:1407-1409` |
| `id_c_dat0..dat3` | 0..18, the IR table above | `[G]` `docs/HakenMidi.h:1797-1801` |
| `id_c_lth*` (length), `id_c_shf*` (shift), `id_c_wid*` (width), `id_c_atL*`/`atR*` (attenuation) | **unknown** - the header names them and gives no range, scale or unit, and the guide does not mention them at all | `[I]` checklist gap #25, `owner: header`, to be closed by a header re-read or by `ref/pachde-CHEM/src/em/convolution.cpp` (`modules-unfilled-checklist.md` S2) |
| `id_c_phc` (phase cancellation compensation) | true/false, and **what it compensates for is unknown** | `[I]` checklist gap #26, `owner: header`, same sources |

**The void, stated as a void.** `[I]` Twenty-four of the thirty `s_Conv_Poke` ids - every length,
shift, width and attenuation - have a wire id, a name, and **no documented range or meaning**.
The inference is that naming a parameter is not knowing it: writing `id_c_lth0 = 64` would be a
guess about both the scale and the direction. Nothing in `docs/` fills this, so it is not filled
here.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | MCP today |
|---|---|---|
| **All 30 convolution parameters, the four IR selections included** | `s_Conv_Poke` stream 26 (write) / `s_Conv` stream 14 (read) `[G]` `docs/HakenMidi.h:1141`, `:1113` | **neither read nor written** - there is no codec for either stream. Rank `T16` `[I]`: the inference is that the stream-codec rank, which names streams 11/12/14 for reading and 24/25/26 for writing, is the one that unblocks this module whole |
| The same data, **already arriving** | stream 14 in a preset dump | `[D]` `CLAUDE.md:53`, 2026-10-25, fw 10.81 lists streams "20/14/5/6/11/12/15" in a live preset dump, so stream 14 reaches the host today and is discarded. `[I]` The inference: this is a decoding gap, not a protocol gap - no device work is needed to read it |
| What each assignable Master column drives | `idMastCol1..6 = 27..32`, `index.md`'s table | **read only**: `get_setup()["master_columns"]` names all six, `Conv 1 Interp` .. `Conv 2 Mix` included. No write tool: labelling is `T4`, which ships, and writing the assignment is `T21`, `set_master_column` `[I]` - the inference is that the one rank specified for the assignable Master columns' write side carries their selectors, as `T4` already carries the row-type labelling |
| The `I` and `M` columns as matrix cells | matrix cells 2-7, when a selector points there | **write + read**: `set_matrix_point` / `get_matrix` `[I]`, from the tool surface |
| Loading your own impulse response | - | **not possible on the device at all** `[G]` `docs/EaganMatrixUserGuide.txt:1400`, verbatim: "Currently the user cannot add Convolutions of their own." `[I]` The inference: this is the one gap on this card that no tool rank can close |

`[I]` **Nothing in the Convolution configuration is MCP-writable today.** This is one of the two
tool limits `index.md` records for all cards; it is referenced here, with the ranks named above,
rather than re-argued.

`[C]` The corpus shows what a codec would recover: in every modern preset carrying a `s_Conv`
stream, ids 0-3 (`id_c_idx1`, `mix1`, `idx2`, `mix2`) are **0** and only ids 4-7, the IR
selections, carry data - for example `Additive Gnilham` `[3, 7, 8, 6]` = Autoharp2, MetalBright,
Fiber, Wood (`corpus-module-wiring.md` S18d, over the 107 presets with the stream). `[I]` So the
index and mix really do live in the Master columns, and a decoder would recover the factory's
*palette* of responses but nothing about how far along them a preset sits.

## 4. DSP cost class

**`N` in the completeness matrix - the guide states no cost for this module**
(`modules-unfilled-checklist.md` S1). Two structural facts stand in for a figure:

`[G]` `docs/EaganMatrixUserGuide.txt:1379-1381`, verbatim: "Audio input into the left channel of
the Master Section, to be processed by the Master's soft saturation, Convolution, Recirculator,
and second Convolution. The Master Section processes the stereo audio sum of all voices."

`[I]` Because the Master processes the sum of all voices, each convolution's cost is
**per-preset, not per-voice** - the inference is directly from that sentence. A preset pays for
both engines once, whatever the polyphony.

`[I]` The one documented lever on the cost is `id_c_lth*`, the IR length - a shorter impulse
response is less work. The inference is from the parameter's existence and name, not from any
statement in the guide, and since its range is part of section 2's void, the lever cannot be
used quantitatively. `get_status` would report what both engines actually cost on this device;
no such measurement is on record here.

## 5. Typical wiring

**No catalogued preset exercises this module, and this card states the absence rather than
inventing an example.** `[C]` `corpus-module-wiring.md` S18d names no preset whose *matrix*
wiring demonstrates a convolution, and the shipped `factory_catalog.json` carries no convolution
field at all: `s_Conv` is not among the data the preset-file decoder emits, so none of the 49
presets in `preset_file.WIRING_PRESETS` can show a convolution cell. Card 18 is the single
exception to the rule that every card's section 5 names a catalogued preset, exactly as
`index.md` records.

Three further facts, so the absence is not mistaken for ignorance:

- `[C]` The presets S18d names - `Additive Gnilham`, `Bowed KinBanjo`, `Bitty Boop` - are named
  for their **IR selections**, read out of the raw `s_Conv` stream during the corpus pass, not for
  any matrix wiring. Two of them (`Additive Gnilham`, `Bowed KinBanjo`) are in
  `preset_file.WIRING_PRESETS`, and their shipped `wiring` blocks carry **no** convolution data,
  so quoting the IR triples here as a worked example would put prose and shipped data out of step.
  They carry the `convolution` technique tag and nothing more.
- `[C]` One legacy preset, `Bandpass Sweep`, carries `[1,1,1,1,127,96,64,64]` in the stream, which
  does not fit the modern id layout (`corpus-module-wiring.md` S18d). `[I]` The inference is that
  legacy `s_Conv` data uses a different ordering, so it should not be read with the header's
  current ids.
- `[G]` The guide's own named examples are `docs/EaganMatrixUserGuide.txt:1523`, verbatim:
  "Sputnik's Dream: Uses formulas to control the Master Section's Recirculator and
  post-Recirculator Convolution." `[C]` `Sputnik's Dream` is in the 668-preset corpus but has no
  shipped `wiring` block, so it is a lead, not an example.

**What would close this.** Rank `T16`, a codec for streams 14 and 26, plus a rebuild of the
catalog that emits a convolution field. The data is already on hand in 107 presets; the gap is
that nothing decodes it `[I]` - the inference is from the stream being present in dumps and
absent from every shipped record.

## 6. Known traps

1. **The guide's nine responses are not the whole set.** See the CONFLICT block in section 1
   `[G]` `docs/EaganMatrixUserGuide.txt:1398-1400` against `docs/HakenMidi.h:1797-1801`. An agent
   that offers "Wood, Metal, Fiber, Waterphone..." as the menu is hiding ten responses and
   collapsing two kinds of metal into one name.
2. **`I` is 0 to 3, not 0 to 18.** `[G]` `docs/EaganMatrixUserGuide.txt:1396`. It interpolates
   between the four IRs currently loaded into the slots; **which** four is `id_c_dat0..dat3`,
   which no tool writes. `[I]` The inference for a patch builder: you can sweep between the four
   responses a preset already has and you cannot change them, so the preset you start from
   determines your whole timbral palette here.
3. **The post-Recirculator mix defaults to dry.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1448-1450`, verbatim: "Dry/wet mix of the post-Recirculator
   Convolution output, 0 = dry (off), 1 = 100% wet, .5 = 50% wet/dry, etc."
4. **X, Y and Z do not reach the Convolutions directly.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1403-1405`, verbatim: "Note: Formulas affecting convolution do
   not consider the playing surface (X, Y and Z components) with the exception of the Touch
   Control Area when that is used to control convolution parameters." Stated generally too `[G]`
   `docs/EaganMatrixUserGuide.txt:1515-1516`, verbatim: "Note: Formulas affecting the Master
   Section, with the exception of SL/SR and L/R columns do not consider the playing surface (X, Y
   and Z components) with the exception of the Touch Control Area."
   **But both convolutions are modulatable today.** `[D-cap]`
   `tests/fixtures/microdelay_wg_v1_20261025_192903.mid` decodes a stock `idMastCol1..6` that
   ships convolution 1's index and mix on Master columns 2 and 3, the Recirculator on columns 4
   and 5, and convolution 2's index and mix on columns 6 and 7 - `index.md`'s Master-chain
   section carries the full decode. `[I]` The inference: no protocol work is needed to modulate a
   convolution, only the Touch-Control-Area setting that makes a surface formula evaluate.
5. **Formulas on the `M` columns need a Touch Control Area.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1458-1459`, verbatim: "Formulas that use the M column require
   'Use Touch Control Area' or 'All Fingers' (in Ancillary menu). Note: Sustain pedal operation
   does not apply if you use this option." `[I]` This is the keyboard-first trap: with a plain
   MIDI keyboard there are no fingers on a surface, so the inference is that a wheel formula on a
   convolution mix needs "All Fingers" selected and costs the sustain pedal.
6. **The two engines sit on opposite sides of the Recirculator**, so the same IR sounds different
   in each. The chain order is `index.md`'s; the trap is that `Conv 1` colours what the reverb
   hears and `Conv 2` colours the reverb's output `[I]` - the inference is from the chain order
   alone, not from any statement about the sonic difference.
7. **The Master's stereo convolutions bleed SL into SR.** `[G]`
   `docs/EaganMatrixUserGuide.txt:1383-1385`, verbatim: "Note: You might hear some bleed through
   between SL and SR channels due to stereo convolutions applied in the master section. Is this
   is unwanted you can use the L and R outputs that bypass the master section and add your own
   effects." (the typo is the guide's).
8. **Legacy `s_Conv` data does not decode with the current ids** - see `Bandpass Sweep` in
   section 5 `[C]` `corpus-module-wiring.md` S18d.
