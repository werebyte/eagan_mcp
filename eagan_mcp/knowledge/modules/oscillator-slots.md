# Module card - Oscillator / filter / multiplier slots (all 20 modes)

Slot type is `idOscFilTyp1..5 = 72..76` `[G]` `docs/HakenMidi.h:1507-1511`; the 20 values are
`[G]` `docs/HakenMidi.h:1513-1534`. Guide section 6.2, "DSF Oscillators" `[G]`
`docs/EaganMatrixUserGuide.txt:1548`. Card schema, shared facts and the module-name spelling:
`index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle; this card writes `In`
`[G]` `docs/EaganMatrixUserGuide.txt:1555`.

## TL;DR

Five three-column slots, each independently set to any of 20 types `[G]`
`docs/EaganMatrixUserGuide.txt:1744-1745`, verbatim: "The EaganMatrix has five 3-column
Oscillator/Filter/Multiplier slots; each of the five is configurable as Oscillator or MultiMode
Filter or Signal Multiplier."

Slot *n* occupies matrix columns `12 + 3(n-1)`, `13 + 3(n-1)`, `14 + 3(n-1)` `[G]`
`eagan_mcp/matrix_map.py:30-34`. The third column is `B` or `S` depending on type `[D]`
`CLAUDE.md:17`, 2026-10-25, fw 10.81.

Blank-column behaviour here is documented and load-bearing: a blank `F` turns a DSF oscillator
into a waveshaper `[G]` `docs/EaganMatrixUserGuide.txt:1576-1578`, and a blank `S` is the
cheapest sine `[G]` `docs/EaganMatrixUserGuide.txt:1632-1633`.

`[C]` The per-mode corpus counts are in `index.md`'s census table; this card does not recount
them.

## Key Decisions

- Carded as one file because all 20 modes share the same three matrix columns and the same two
   configuration ids `[G]` `docs/HakenMidi.h:1507-1556`; splitting them would repeat the slot
   structure 20 times.
- `idOscFilOpt` is documented per type, because it is the single id behind five unrelated
   settings `[G]` `docs/HakenMidi.h:1535-1551`.

## Open Questions / Risks

- `[G]` `docs/EaganMatrixUserGuide.txt:2179` describes the Signal Multiplier's third column
   only as a "successively longer delay" on input 2; the actual delay lengths are not given.
- `[I]` Tanh's Drive / Makeup / Mix mapping onto the three slot columns is not stated
   column-by-column anywhere this card could find - the inference is that the guide treats Tanh
   as a Master-section control that also exists as a slot, and documents it there.
- `[I]` BitCrush's second and third columns are not described; only the crush amount is - the
   inference is that they are inert, but that is a guess and it is filed as such.

---

## 1. What every column means

The slot's type decides all three columns `[G]` `docs/HakenMidi.h:1513-1534`.
Grouped by family:

| Family and types | Column 1 | Column 2 | Column 3 | Source |
|---|---|---|---|---|
| DSF Oscillator, Integrated DSF | phase-modulation input, 0 = 0 radians, 1 = 2 pi radians | frequency, kHz | `S` spectral balance, 0 = pure sine, 1 = max harmonic amplitudes | `[G]` `docs/EaganMatrixUserGuide.txt:1553-1556`, `:1574`, `:1581-1583` |
| PWM Oscillator | **Triangle Control** 0..1, moving the waveform from square towards triangle harmonic content - not phase modulation | frequency, kHz | pulse width | `[G]` `docs/EaganMatrixUserGuide.txt:1568-1572` |
| Jenny Oscillator | does not apply | does not apply | `Bx` bandwidth multiplier and `Fx` frequency multiplier are the Jenny's own columns | `[G]` `docs/EaganMatrixUserGuide.txt:1557`, `:1579`, `:1588-1596` |
| Phase Generator | phase-modulation input | frequency, kHz | `S` = frequency spread **in Hz** for the seven internal phase generators | `[G]` `docs/EaganMatrixUserGuide.txt:1585-1586`, `:1599-1601` |
| Noise from Seed | the **seed value** | leave blank | `T` trigger: a transition from T <= 0 to T > 0 reseeds | `[G]` `docs/EaganMatrixUserGuide.txt:1554-1555`, `:1576-1578`, `:1604-1606` |
| The nine multimode filters | filter audio input | cutoff, kHz | `B` bandwidth; smaller values narrow it and increase resonance | `[G]` `docs/EaganMatrixUserGuide.txt:1725-1726` |
| Single Pole Low / High Pass | filter audio input | cutoff, kHz | **no bandwidth setting**; on the first four slots this column is a MicroDelay tap `T` | `[G]` `docs/EaganMatrixUserGuide.txt:1726-1727`, `:1734-1737` |
| Ladder Low Pass | filter audio input | cutoff, kHz | `B` is **Resonance**, 0 = very small bandwidth / max resonance, 1 = max bandwidth / minimum resonance | `[G]` `docs/EaganMatrixUserGuide.txt:1727-1730` |
| Signal Multiplier | audio input 1 | audio input 2, multiplied by input 1 | a successively longer delay on the second input | `[G]` `docs/EaganMatrixUserGuide.txt:2168`, `:2179` |
| Tanh | audio input | drive / makeup / mix, see the risk above | same | `[I]` from the absence of a column-by-column statement |
| Bitcrusher | audio input | crush amount | undocumented | `[I]` from the absence of a statement |
| Pitch Shifter using Delay | frequency multiplier on the delay data, 0..2.0; 0.5 = octave down, 1.0 = at pitch, 2.0 = octave up | the delay data's original frequency, kHz | the shifter's granulator frequency, kHz | `[G]` `docs/EaganMatrixUserGuide.txt:2227-2233` |

The type names above are `setup.py`'s spellings, which `index.md` fixes project-wide; the wire
value of each is `[G]` `docs/HakenMidi.h:1513-1534`.

## 2. Units, useful ranges, blank-column behaviour

| Column | Units | What blank (= 0) does | Source |
|---|---|---|---|
| `F` on an oscillator | kHz | **not neutral**: blank `F` plus audio into column 1 makes the slot a **waveshaper**, a non-linear filter. Also the required state for Noise from Seed | `[G]` `docs/EaganMatrixUserGuide.txt:1576-1578`, `:1634-1636` |
| `F` on a filter | kHz | 0 Hz cutoff `[I]`, the inference being that a cutoff column with no value is a zero cutoff |
| `S` spectral balance | 0..1 | 0 = pure sine, and **blank is cheaper than writing 0**: "The oscillator is most efficient when the S column is left blank due to optimization of the sine algorithm" | `[G]` `docs/EaganMatrixUserGuide.txt:1632-1633`, also `[D]` `RECIPES.md:70`, 2026-10-25, fw 10.81 |
| `S` on a Phase Generator | **Hz**, not kHz | no spread; unused unless the option is Sum of 7 | `[G]` `docs/EaganMatrixUserGuide.txt:1585-1586` |
| `B` filter bandwidth | about 0..>1 | B = 1 gives no resonance; B > 1 reduces the slope into a gradual filter; below 1 the resonance gets narrower and more pronounced | `[G]` `docs/EaganMatrixUserGuide.txt:1772-1775` |
| `B` ladder resonance | **0..1 only** | **0 = maximum resonance**, not neutral | `[G]` `docs/EaganMatrixUserGuide.txt:1727-1730` |
| `Bx` on a Jenny | 1.0 and up | "has no effect when `No Resonance Decay` is selected"; a zero column disables the decay post-multiply | `[G]` `docs/EaganMatrixUserGuide.txt:1588-1591`, `:1946-1947` |
| `Fx` on a Jenny | 1 = the master oscillator's frequency | "Not applied if set to zero or left blank" | `[G]` `docs/EaganMatrixUserGuide.txt:1958` |
| column 1 phase modulation | 0..1 = 0..2 pi radians | "Leave this blank for an oscillator without modulation"; with column 1 and `S` both zero the slot is a pure sine at `F` | `[G]` `docs/EaganMatrixUserGuide.txt:1556`, `:1631-1633` |
| Pitch Shifter column 2 | kHz | "Leave this column blank if this is unknown" - it only adjusts grain hop size to avoid phase cancellation | `[G]` `docs/EaganMatrixUserGuide.txt:2229-2230` |
| Pitch Shifter column 3 | kHz | "usually leave the column blank for the longest grains allowed by the Delay's length" | `[G]` `docs/EaganMatrixUserGuide.txt:2232-2233` |

`[C]` Slot-type convention over the 668 presets, where an absent id means the default DSF
Oscillator: slot 1 leans oscillator (Integrated DSF 25, Phase Generator 14, Tanh 12), slots 4
and 5 lean filter (High Pass 29 and 20, Single Pole Low Pass 27, Band Pass 16 and 16, Shelving
High Pass 19 on slot 5). Cascade 4 is the most common option. Extreme rate is set in **1**
preset of 668 (`analysis/findings/corpus-module-wiring.md` S1).

## 3. Properties-panel settings and MCP reachability

| Setting | Wire | Reachable today |
|---|---|---|
| Slot type | `idOscFilTyp1..5 = 72..76` | **yes, read and write** - `set_osc_type(slot, type_name)`, and `get_setup` names it `[G]` `eagan_mcp/setup.py:220`, `:173` |
| Matrix cells 12..26 | the matrix | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| Filter cascade **or** oscillator variant | `idOscFilOpt1..5 = 77..81` | **read-only.** `get_setup` now decodes it per slot type as `oscillators[n].option` and still reports the old undecoded `cascade_raw` beside it `[G]` `eagan_mcp/setup.py:174-175`. **No write tool**; `T15` is the rank that would add one |
| Audio-rate coefficient update ("Extreme") | `idFilEx1..5 = 82..86` | **read-only** - `get_setup` returns `extreme_rate` as a boolean `[G]` `eagan_mcp/setup.py:176`. No write tool |

`idOscFilOpt`'s five meanings `[G]` `docs/HakenMidi.h:1535-1551`: for the nine cascading filter
types it is 0 or 1..3 cascade steps; for PWM it is linear or exponential; for the Phase
Generator it is sum of seven, ramp up, ramp down or triangle; for the Jenny it is sharp,
smooth, Hann or no decay; for the Ladder it is transistor or diode.

`[I]` The project's own defect list named `idOscFilOpt`'s `cascade_raw` label as wrong for 11 of
the 20 types; `get_setup` now carries a decoded `option` beside it, so the read-side half is
closed and `T15` is only the write half - the inference is from reading the shipped decoder
against the header, not from the device.

Cascade semantics worth carrying: cascade choices 1..4 give 12, 24, 36 or 48 dB/octave for
2-pole filters and 6, 12, 18 or 24 for 1-pole, and "the bandwidths are adjusted to B1/2, B1/3,
and B1/4 so that the same perceived cutoff frequency is maintained at each cascade value" `[G]`
`docs/EaganMatrixUserGuide.txt:1746-1750`. Normal recomputes filter coefficients once per
millisecond, Extreme every sample interval, and Extreme is required when `F` or `B` carry
audio-rate signals `[G]` `docs/EaganMatrixUserGuide.txt:1763-1765`.

## 4. DSP cost class

| Type | Class | Evidence |
|---|---|---|
| DSF or Integrated DSF with `S` blank | light | "most efficient when the S column is left blank" `[G]` `docs/EaganMatrixUserGuide.txt:1632` |
| DSF or Integrated DSF with `S` active | light to medium | `[I]` implied by the above; the guide gives no second figure |
| Multimode filters at cascade 1 | light | `[I]` from the absence of any warning where the guide does warn for two other types |
| Any filter with Extreme set | heavier | `[I]` from recomputing coefficients every sample instead of every millisecond, `docs/EaganMatrixUserGuide.txt:1763-1765` |
| Signal Multiplier | light to medium | "its multiplication happens at sample rate, instead of control rate" `[G]` `docs/EaganMatrixUserGuide.txt:1877` |
| **PWM Oscillator** | **heavy** | "the PWM oscillator uses about twice the processing" of a bit-crushed sine `[G]` `docs/EaganMatrixUserGuide.txt:2151-2152`; also `[D]` `RECIPES.md:46 (moved to pitfalls.md section 3, item 32)`, 2026-10-25, fw 10.81 |
| **Ladder Low Pass**, both variants | **heavy** | "computationally intensive objects which may produce" Reduce Polyphony messages `[G]` `docs/EaganMatrixUserGuide.txt:7372`; also `[D]` `RECIPES.md:46 (moved to pitfalls.md section 3, item 32)`, 2026-10-25, fw 10.81 |

Fix order when the budget is blown, in this order: drop a heavy module (Ladder -> Low Pass
Filter, PWM -> DSF), then lower base polyphony by one while keeping the expanded flag, then
simplify the oscillator `F` formulas `[D]` `RECIPES.md:48-49 (moved to pitfalls.md section 7, item 57)`, 2026-10-25, fw 10.81.

## 5. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`FM Bells` - an FM pair into a resonant filter `[C]` (`factory_catalog.json`, `wiring`):

```
Osc/Filter 4 In <- Noise = 1
Osc/Filter 4 F  <- Direct + = X      Osc/Filter 4 B <- Direct + = 0.5
Osc/Filter 2 In <- Osc 4 = E      Osc/Filter 3 In <- Osc 4 = E
Osc/Filter 2 F  <- Direct + = B, Direct x = 2
Osc/Filter 3 F  <- Direct + = C, Direct x = 2
Osc/Filter 1 F  <- Osc 2 = A, Osc 3 = A, Direct + = F, Direct x = 2
Master SL/SR    <- Osc 1 = D
  B = W Constant 1.0 x macro i ; X = -0.89 -> 1.00 x1 kHz   (deliberately off exact pitch)
  C = as B with X = -1.00 -> 1.00 x1 kHz                    (the exact-pitch formula)
```

`[C]` Noise through a band filter in slot 4 excites two pitched modulators in slots 2 and 3,
and both land on slot 1's `F` through the **same** FM-index letter `A`: one envelope, two
modulators. The detune is an `X` begin value of -0.89 instead of -1.00.

`Kinetic SatPad` - five oscillators off one random detune source `[C]`
(`factory_catalog.json`, `wiring`):

```
osc: slots 1..5 all Integrated DSF
Osc/Filter n F <- Direct + = X  (all five), plus Direct x = H / I / J / O on 2,3,4,5
Osc/Filter n B <- Direct + = D  (all five, one letter)
  C = W SG1 0.18 x0.1 [S+H row]     G = W SG1 1.0 x0.01 [S+H row]
  H = W Constant 1.0 ; anc + formula C        I = W Constant 0.3 x10 ; anc - formula G
  D = Y = 0 -> 0.65                 (one wheel-controlled bandwidth for all five filters)
```

`[C]` All five slots share the predefined pitch code on `F` with a per-slot scaler on
`Direct x`, and all five scalers are built from a single sample-and-hold shape generator -
one shared generator rather than five, which is also the device-verified way to avoid panel
lag `[D]` `RECIPES.md:18-19 (moved to pitfalls.md section 5, item 42)`, 2026-10-25, fw 10.81.

`Cascade`, `Ping Pong` and `Hal Dreams of Macros` are the other slot-heavy presets with a
shipped wiring block; `Cascade` runs one Phase Generator into two filter pairs `[C]`
(`factory_catalog.json`, `wiring`).

## 6. Known traps

1. **Blank `F` is a mode switch, not a zero.** A DSF oscillator with blank `F` and audio in
   column 1 is a waveshaper, not silence `[G]` `docs/EaganMatrixUserGuide.txt:1576-1578`.
2. **Blank `S` is cheaper than `S` = 0** for the same sound `[G]`
   `docs/EaganMatrixUserGuide.txt:1632-1633`.
3. **A blank Ladder `B` column is maximum resonance** `[G]`
   `docs/EaganMatrixUserGuide.txt:1727-1730`.
4. **A Jenny with no master oscillator to its left makes no sound** `[G]`
   `docs/EaganMatrixUserGuide.txt:1926-1927`, verbatim: "It will produce no sound if defined in
   the matrix and sent directly to outputs without a Master Oscillator present." The master is
   the nearest DSF, Integrated DSF or Phase Generator to the **left** `[G]`
   `docs/EaganMatrixUserGuide.txt:1593-1596`.
5. **A blank Jenny `Bx` or `Fx` silently disables that feature** `[G]`
   `docs/EaganMatrixUserGuide.txt:1946-1947`, `:1958`.
6. **At most four Jenny oscillators**, each needing a non-Jenny master to its left, "though in
   practice only one or two would typically be used" `[G]`
   `docs/EaganMatrixUserGuide.txt:1609-1611`.
7. **The Signal Multiplier needs two inputs** `[G]`
   `docs/EaganMatrixUserGuide.txt:2168`, verbatim: "At least two inputs must be preset to
   generate a sound as a non-preset input will be treated as a zero."
8. **Single-pole filters have no bandwidth column**, so writing `B` there does nothing `[G]`
   `docs/EaganMatrixUserGuide.txt:1726-1727`.
9. **Only four MicroDelay taps exist**, so the filter-slot `T` tap is available in slots 1..4
   only `[G]` `docs/EaganMatrixUserGuide.txt:1734-1737`.
10. **Macros and complex formulas on oscillator `F` columns cost panel responsiveness**:
    several continuous shape generators each on a different oscillator `F` column make the panel
    knobs unusable, while one shared generator is fine, and FM through an audio row into an
    oscillator `F` is fine `[D]` `RECIPES.md:18-19`, `:24` and `:31-33` (all moved to pitfalls.md section 5, items 42-45), 2026-10-25, fw 10.81.
11. **PWM can alias** where the square WaveBank is "strictly alias-free" `[G]`
    `docs/EaganMatrixUserGuide.txt:2149`.
12. **`idOscFilOpt` is the only path to a Jenny decay contour, a Phase Generator mode, PWM
    linear-vs-exponential and transistor-vs-diode ladder**, and nothing writes it `[G]`
    `docs/HakenMidi.h:1535-1551`; `T15` is the rank that would unblock all four at once.
