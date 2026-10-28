# SummedDelay

Bank C, card 14 of 18. One multi-tap audio delay buffer **shared by all voices**. Its wire value
is shared fact 9's; the one spelling of the name is `index.md`'s. Everything cross-cutting - the
one delay memory and its budget (shared fact 7), the tap row alternates (shared fact 8), the
matrix column budget (shared fact 1) and the six cross-module wiring patterns - lives in
`index.md` and is referenced here, never restated.

`[G]` `docs/EaganMatrixUserGuide.txt:4158-4159`, verbatim: "The SummedDelay provides a single
multi-tap audio delay buffer shared by all voices. SummedDelay is a summed aggregate of all voices
in one shared delay. The SummedDelay is available in Bank C."

`[C]` 98 of 668 factory presets run a SummedDelay (`census.json:modules_used_including_defaults`);
all 98 set `idBankC` explicitly, because SummedDelay is not the Bank C default
(`census.json:bank_C`).

Guide section 6.15, `docs/EaganMatrixUserGuide.txt:4118-4176`.

---

## 1. Columns

Eight Bank C columns, matrix columns 43-50 (shared fact 1). The column map is the same shape as
VoiceDelay's; what changes is column 1, which is this voice's **contribution** to a buffer every
voice shares. The input column's heading is an up-pointing triangle in the Editor; written `In`
here under the ASCII rule.

| Bank C col | Matrix col | Label | What it does |
|---|---|---|---|
| 1 | 43 | `In` | `[G]` `docs/EaganMatrixUserGuide.txt:4122-4124`, verbatim: "This voice's audio input contribution to the shared SummedDelay. If the SummedDelay is operating at reduced sample rate, this input passes through an optional anti-aliasing filter." |
| 2 | 44 | `D` | `[G]` `docs/EaganMatrixUserGuide.txt:4126-4128`, verbatim: "Delay time. 0 = no delay, 1 = delay by max amount selected in Delay menu. The primary output of the SummedDelay is available on the Bank C row of the EaganMatrix." |
| 3 | 45 | `T1` | `[G]` `docs/EaganMatrixUserGuide.txt:4130-4132`, verbatim: "Delay time for Tap 1. This is a multiplier on the D value. 0 = no delay, 1 = delay by D value. The Tap 1 and 2 outputs are available as an alternative on the AesIn matrix rows." |
| 4 | 46 | `T2` | `[G]` `docs/EaganMatrixUserGuide.txt:4134`, verbatim: "Delay time for Tap 2. 0 = no delay, 1 = delay by D value." |
| 5 | 47 | `T3` | `[G]` `docs/EaganMatrixUserGuide.txt:4136-4138`, verbatim: "Delay time for Tap 3. 0 = no delay, 1 = delay by D value. The Tap 3 and 4 outputs are available as an alternative on the Sub matrix rows." |
| 6 | 48 | `T4` | `[G]` `docs/EaganMatrixUserGuide.txt:4140`, verbatim: "Delay time for Tap 4. 0 = no delay, 1 = delay by D value." |
| 7 | 49 | `H` | `[G]` `docs/EaganMatrixUserGuide.txt:4150`, verbatim: "Greater than zero stops recording new data into the SummedDelay." |
| 8 | 50 | - | `[I]` Undocumented. The guide's SummedDelay table has seven rows for eight columns, and `[C]` 2% of the 87 decoded SummedDelay slots carry anything in it (`corpus-module-wiring.md` S15); the inference is an unused column rather than an undocumented one. |

`[C]` Column occupancy over the 87 decoded SummedDelay slots: c1 100%, c2 95%, c3 66%, c4 62%,
c5 22%, c6 22%, c7 1%, c8 2% (`corpus-module-wiring.md` S15). The taps are used far more here
than on the VoiceDelay, and `Bank C -> Bank C 1` feedback appears in 55 of the 87.

## 2. Units, useful ranges and blank-column behaviour

| Column | Units | Useful range | Blank (= 0) |
|---|---|---|---|
| `D` | `[G]` `docs/EaganMatrixUserGuide.txt:4126-4127`: **normalised 0..1 against the Delay menu maximum**, not milliseconds | 0..1 | **0 = no delay**, so a blank `D` is a bypass. Benign. |
| `T1`-`T4` | `[G]` `docs/EaganMatrixUserGuide.txt:4130-4131`: a **multiplier on `D`** | 0..1 | 0 = that tap is off. Benign. |
| `H` | `[G]` `docs/EaganMatrixUserGuide.txt:4150`: a trigger, "Greater than zero stops recording" | <= 0 to record | 0 is normal operation. Benign. |
| `In` | audio, and **the one place the PScaler belongs** | see trap 1 | `[I]` no input means the buffer records silence; the inference is that there is no fallback source, since the guide names one input column. |

**Blank-column verdict: SummedDelay is blank-safe.** `[I]` Every column's zero is a documented,
musically sensible state; the inference is that the hazards are configuration and polyphony
scaling, not empty cells. This is the field the completeness matrix marks `Y` for SummedDelay
(`modules-unfilled-checklist.md` S1).

`[I]` **`D` alone never tells you the delay time** - it is a fraction of the maximum `idTimeSel`
selects (shared fact 7), so the inference is that a `D` value is only interpretable together with
a stream-20 read.

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | MCP today |
|---|---|---|
| Bank C type | `idBankC = 93`, value per shared fact 9 | **write + read**: `set_bank_type("C", "SummedDelay")`, `get_setup()["banks"]["C"]` `[I]` - the inference is from the tool surface, which accepts the `setup.py:BANK_C_TYPES` string |
| All eight columns | matrix cells 43-50 | **write + read**: `set_matrix_point` / `get_matrix` `[I]`, same inference |
| Maximum delay time | `idTimeSel = 105` `[G]` `docs/HakenMidi.h:1632`, header comment "select time delay 50 ms * 2^n" | **raw read only** (`get_setup()["delay_time_select_raw"]`); no name table and no write. Rank `T22` `[I]` - the inference is that the validated `s_Mat_Poke` write rank carries the delay setup ids; `T4` is the labelling rank and is read-only |
| Anti-aliasing (Nyquist) filter | `idAliasDelay = 108` `[G]` `docs/HakenMidi.h:1599`, header comment "true to disable nyquist filtering on delay" | **neither read nor written**. Rank `T22` `[I]`, same inference. `[C]` 4 of 668 presets write it (`census.json:setup_id_frequency`, `AliasDelay`) |
| Tap rows | `idRowTyp1 = 106` / `idRowTyp2 = 107`, shared fact 8 | **read and decoded** (`get_setup()["row_types"]`), and the matrix tools label rows 9-12 from them `[D-cap]` `tests/fixtures/microdelay_wg_v1_20261025_192903.mid`. No write tool: labelling is `T4`, which ships, and writing the selectors is `T22` `[I]` |
| **PScaler on the input column** | a matrix cell value, not a setup id | **writable today** - it is the `Direct x (multiply)` cell's formula, reachable through `set_formula` `[I]`; the inference is that a polyphony scaler is a formula modifier, so no new wire semantics are needed |

## 4. DSP cost class

**Memory-bound, and cheaper per voice than the VoiceDelay** because there is one buffer rather
than one per voice. The shared budget is shared fact 7's and is not restated; what is specific to
SummedDelay is that **polyphony drops out of the sample-rate equation**:

`[G]` `docs/EaganMatrixUserGuide.txt:4161`, verbatim: "The sample rate of the SummedDelay memory
is limited by the maximum delay selected in the Delay menu."

`[I]` Compare the VoiceDelay, whose sample rate is limited by maximum delay **and** polyphony.
The inference is that a long delay is affordable here at a voice count where a VoiceDelay would
already be running reduced - which is why echo and reverb-tail constructions in the corpus reach
for the SummedDelay.

`[G]` `docs/EaganMatrixUserGuide.txt:4162-4164`, verbatim: "The Anti-Aliasing Low Pass Filter
indicator above the first Bank C column will light up when the delay memory is at reduced sample
rate. If you do not want an Anti-Aliasing filter at reduced sample rates, click on the indicator
to disable the filter."

`[I]` **Not measured on this device.** The checklist marks SummedDelay's DSP cost `Y` from the
passage above; the inference is that "limited by maximum delay only" is a documented property,
not a `get_status` reading.

## 5. Typical wiring

Both examples ship decoded in `factory_catalog.json`; cell orientation is
`column <- row = value`, which is `set_matrix_point(row, col, value)` read from the column side.

**`Cascade`** (modern, fw 10.39) - the PScaler template the guide asks for. `[C]` from the shipped
`wiring` block (one of the 49 presets in `preset_file.WIRING_PRESETS`):

```
Bank C 1 (43)   <- Osc 1 = C, Osc 2 = C, Osc 4 = H, Osc 5 = H, Bank C = G, Direct x = V
Bank C 2 (44)   <- Direct + = 1          (D at maximum; delay_time_select_raw = 4)
Bank C 3 (45)   <- Direct + = 1          (T1 = full D)
Bank C 4 (46)   <- Direct + = 0.66       (T2 = two thirds of D)
Master SL (0)   <- Osc 1 = C, Osc 4 = H, Tap 1 = F
Master SR (1)   <- Osc 2 = C, Osc 5 = H, Tap 2 = F
  V = [W+X+Y+Z] W = Constant 1.0 x 1 x Polyphony scaler     (the PScaler, on Direct x)
  G = [W+X+Y+Z] W = Constant 0.99 x 1 x Macro (iv)          (feedback, macro iv = "Delay")
  F = [W+X+Y+Z] W = Constant 0.75 x 1 x Macro (iv)          (return level, same macro)
```

`[C]` The feedback letter `G` and the tap return letter `F` sit on the **same macro**, so one knob
controls the whole echo depth; the PScaler is a `Direct x (multiply)` cell on the input column.

**`Bird Echoer`** (modern, fw 10.39) - a PScaler feedback echo kept out of the Master chain.
`[C]` from the shipped `wiring` block:

```
Dry L (9) / Dry R (10)   <- Bank A = 1          (the bank bypasses the Master chain entirely)
Bank C 1 (43)            <- Bank A = z^2, Bank C = G
Bank C 2 (44)            <- Direct + = 1        (D at maximum; delay_time_select_raw = 4)
Bank C 3 (45)            <- Direct + = O        (T1)
Bank C 4 (46)            <- Direct + = O, Direct x = 0.5   (T2 = half of T1's value)
Master SL (0)            <- Tap 1 = 1 ; Master SR (1) <- Tap 2 = 1
Master/Dry mix (8)       <- Direct + = 0.5
  G = [W+X+Y+Z] W = Constant 0.5 x 1 x Polyphony scaler     (PScaler inside the feedback letter)
```

`[C]` Rows 9/10 read as `Tap 1` / `Tap 2`: `Bird Echoer` sets `idRowTyp1` to its tap value, so the
two taps go straight to the Master while the dry bank goes to `Dry L`/`Dry R`. Shared fact 8 in
use again.

`[C]` **A preset-lead correction.** The guide names `Instant Reich` for the PScaler -
`docs/EaganMatrixUserGuide.txt:4176`, verbatim: "Instant Reich: See formula D for use of the
PScaler function." `Instant Reich` **is** in the 49-preset wiring set, and its decoded formula
`D` is `W = Constant 1.0 x 1 x Macro (i)` - a macro modifier, **not** a polyphony scaler. The two
presets cited above are the ones whose shipped data actually shows a PScaler.

```
CONFLICT: which factory preset demonstrates the PScaler - Instant Reich vs Cascade/Bird Echoer
  docs   [G]: "Instant Reich: See formula D for use of the PScaler function."
              - docs/EaganMatrixUserGuide.txt:4176
  corpus [C]: Instant Reich's decoded letter D carries modifier "x Macro (i)", not the polyphony
              scaler; 8 of the 49 presets with a shipped wiring block do carry a PScaler letter
              (Cascade V, Bird Echoer G, Shimmer Wbl A, Choir and Ext R, Harmonic Viol K,
              Additive Horn 1 Wbl K, Additive Vocal 1 Transform I, Boson Particles Wbl E),
              and 27 of 668 presets use a PScaler at all (corpus-module-wiring.md S15b)
  follows: the corpus, for the worked example, because the shipped catalog and this card must
           agree cell for cell. The guide's sentence is not contradicted as advice - it may
           describe an older revision of that preset - so both stand.
```

## 6. Known traps

1. **Feedback without a PScaler changes level with polyphony.** `[G]`
   `docs/EaganMatrixUserGuide.txt:4167-4170`, verbatim: "When using the PScaler as a multiplier in
   the input column to the Summed delay, changes to the polyphony will properly compensate for how
   many voices are being fed into the delay at a time. This is critical if one is using a feedback
   system, like when designing repeating echoes. Without the PScaler a change in polyphony would
   change the levels of feedback input." This is the trap that makes SummedDelay different from
   every other bank: **the input column sums across voices**, so its level is a function of how
   many notes are held.
2. **"Summed" means summed per DSP, then combined.** `[G]`
   `docs/EaganMatrixUserGuide.txt:4166-4167`, verbatim: "The SummedDelay is not a sum of all
   available delay modules in a multi DSP system, but instead the sum in each DSP individually,
   that are then combined together acting as a single unit."
3. **A delay-based string does not follow pitch bend on a ringing note.** The construction and the
   BiqBank alternative are `pitfalls.md` section 6's; this card points there rather than repeating
   the recipe `[D]` `RECIPES.md:26 (moved to pitfalls.md section 6, item 49)`, 2026-10-25, fw 10.81.
4. **`D` is a fraction, not a time** - see section 2 `[G]`
   `docs/EaganMatrixUserGuide.txt:4126-4127` plus `docs/HakenMidi.h:1632`.
5. **Taps are row *alternatives*, not additions** `[G]` `docs/HakenMidi.h:1634-1643`. Shared fact
   8 owns the id table; the trap is that `rt1Tap` costs you the Audio In L/R rows.
6. **Saving with `H` active breaks a Live HarMan on reload.** `[G]`
   `docs/EaganMatrixUserGuide.txt:3411-3412`, verbatim: "save the preset in this state (Hold
   active) and reload it, the HarMan will make no sound as there is no initial data in the delay
   buffer to work on. In this case you may want to put a Pedal on the Hold function with a Macro".
7. **A Live Manipulator reads *this* delay specifically.** `[G]`
   `docs/EaganMatrixUserGuide.txt:3477-3479`, verbatim: "For ModMan, a popup menu allows you to
   select a predefined Spectral Set to load into the Delay memory, or Live to manipulate spectral
   envelope data (period 620.69 Hz, the data within each period are the spectral amplitudes) you
   record into the SummedDelay." The HarMan sentence names the SummedDelay too `[G]`
   `docs/EaganMatrixUserGuide.txt:3399-3400`. `[I]` The inference for a patch builder: a Live
   Manipulator with a VoiceDelay in Bank C is at best unverified and at worst silent, and the
   `voicedelay.md` card records the header-versus-guide conflict behind that.
8. **A Manipulator in Bank A or B halves this delay's memory** `[G]`
   `docs/EaganMatrixUserGuide.txt:3491`, verbatim: "SummedDelay, MicroDelay, and FormulaDelay in
   Bank C (which will operate using half its normal memory)." `[G]`
   `docs/EaganMatrixUserGuide.txt:3492-3493`, verbatim: "If you have two Manipulators (both Bank A
   and Bank B) as well as a Delay in Bank C, both Manipulators must specify the same Spectral Set."
