# Module card - CVC (Continuum Voltage Converter control voltages)

Bank wire value **8**, **bank B or bank C only - never bank A** `[G]`
`docs/HakenMidi.h:1571`, whose own comment reads "for idBankB,idBankC (B+C for dual CVC)".
Device-corroborated: "bank values 8 = CVC" `[D]` `CLAUDE.md:14`, 2026-10-25, fw 10.81. Guide
section 6.13, "Multipurpose Banks: CVC Control Voltages (Continuum Voltage Converter)" `[G]`
`docs/EaganMatrixUserGuide.txt:3915`. Card schema, shared facts, the module-name spelling and
what the alias form means: `index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

## TL;DR

Not a sound generator. Eight matrix columns whose formula outputs are interpreted as **volts**
and sent to a CVC hardware converter `[G]` `docs/EaganMatrixUserGuide.txt:4021-4022`,
verbatim: "The columns in the EaganMatrix CVC bank specify voltage values."

The column map is the simplest in the set: columns 1..8 are CV outputs 1..8 `[G]`
`docs/EaganMatrixUserGuide.txt:3921-3942`. The complexity is not in the columns but in how the
base channel and the Layer option fan those outputs across up to 16 CVC channels - and in the
fact that writing **any** formula into columns 5..8 halves the number of CV voices `[G]`
`docs/EaganMatrixUserGuide.txt:3976-3980`.

`[C]` 15 of the 668 factory presets run a CVC (`census.json`,
`modules_used_including_defaults`).

## Key Decisions

- Carded on the voice-allocation rules rather than on the columns, because the columns are
   trivial and the allocation is where a patch goes wrong `[G]`
   `docs/EaganMatrixUserGuide.txt:3971-3980`.
- The tool's existing bank-A refusal is recorded as **correct**, so that nobody "fixes" it
   `[G]` `eagan_mcp/setup.py:231-232` against `[G]` `docs/HakenMidi.h:1571`.

## Open Questions / Risks

- `[G]` `docs/EaganMatrixUserGuide.txt:4019-4020` says "Don't set more than 10V, though the CVC
   should limit to 10V if you set higher", but how a formula's output maps to volts is shown
   only by example, never stated as a rule.
- `[I]` Whether the 1 V per octave scaling comes from the column or from the formula's own
   transfer is ambiguous in the guide's worked set; the inference from the worked example, which
   puts the minimum and maximum volts **inside the pitch formula's transfer**, is that the
   column only routes `[G]` `docs/EaganMatrixUserGuide.txt:4003-4008`.
- `[G]` `docs/EaganMatrixUserGuide.txt:4018` defers the rest to a separate guide,
   `docs/CVCUserGuide.txt`, which this card does not own.

---

## 1. What every column means

| Col (bank B / bank C) | Conventional label | Meaning | Source |
|---|---|---|---|
| 1 (35 / 43) | `W` | CVC control voltage output 1 | `[G]` `docs/EaganMatrixUserGuide.txt:3921` |
| 2 (36 / 44) | `X` | CVC control voltage output 2 | `[G]` `docs/EaganMatrixUserGuide.txt:3924` |
| 3 (37 / 45) | `Y` | CVC control voltage output 3 | `[G]` `docs/EaganMatrixUserGuide.txt:3927` |
| 4 (38 / 46) | `Z` | CVC control voltage output 4 | `[G]` `docs/EaganMatrixUserGuide.txt:3930` |
| 5 (39 / 47) | `W` | CVC control voltage output 5 | `[G]` `docs/EaganMatrixUserGuide.txt:3933` |
| 6 (40 / 48) | `X` | CVC control voltage output 6 | `[G]` `docs/EaganMatrixUserGuide.txt:3936` |
| 7 (41 / 49) | `Y` | CVC control voltage output 7 | `[G]` `docs/EaganMatrixUserGuide.txt:3939` |
| 8 (42 / 50) | `Z` | CVC control voltage output 8 | `[G]` `docs/EaganMatrixUserGuide.txt:3942` |

The `W X Y Z` labels are a **convention, not a constraint** `[G]`
`docs/EaganMatrixUserGuide.txt:3990-3991`, verbatim: "Typically, each of the formulas applied
to one of the CVC columns will map to its related CVC fingerboard mapping: W, X, Y or Z." Any
formula can go in any column.

Bank B and bank C together are a **dual CVC** `[G]` `docs/HakenMidi.h:1571`.

## 2. Voice allocation - the part that actually bites

Three different lists, and the guide separates them by context. The first describes the CVC
**without** the matrix, through the CVC preset menu `[G]`
`docs/EaganMatrixUserGuide.txt:3946-3953`:

| Base channel | Voices and their outputs | Source |
|---|---|---|
| 1 | 1 voice on outputs 1-4 | `[G]` `docs/EaganMatrixUserGuide.txt:3950` |
| 2 | 2 voices: 1-4 and 5-8 | `[G]` `docs/EaganMatrixUserGuide.txt:3951` |
| 3 | 3 voices: 1-4, 5-8, 9-12 | `[G]` `docs/EaganMatrixUserGuide.txt:3952` |
| 4 or higher | 4 voices: 1-4, 5-8, 9-12, 13-16 | `[G]` `docs/EaganMatrixUserGuide.txt:3953` |

With the matrix driving the CVC and only columns 1..4 used, the same list applies with one
addition `[G]` `docs/EaganMatrixUserGuide.txt:3971-3974`, verbatim: "Same as behavior above,
except with polyphony higher than 4 only first four voices are used, and the additional voices
are ignored."

**Writing a formula into any of columns 5..8 halves the voice count** `[G]`
`docs/EaganMatrixUserGuide.txt:3976-3980`:

| Base channel | Voices and their outputs | Source |
|---|---|---|
| 1 | 1 voice on outputs **1-8**; with Layer on, 1-8 is echoed to 9-16 | `[G]` `docs/EaganMatrixUserGuide.txt:3977-3978` |
| 2 | 2 voices: 1-8 and 9-16 | `[G]` `docs/EaganMatrixUserGuide.txt:3979` |
| 3 or higher | first voice 1-8, second 9-16, **additional voices ignored** | `[G]` `docs/EaganMatrixUserGuide.txt:3980` |

Layer mode instead of Normal Outputs echoes each group of four `[G]`
`docs/EaganMatrixUserGuide.txt:3955-3962`: base channel 1 echoes 1-4 to 5-8, 9-12 and 13-16;
base channel 2 echoes 1-4 to 9-12 and 5-8 to 13-16; base channel 3 echoes only the first voice
to 13-16; base channel 4 or higher behaves as Normal, "as layering has no additional effect".

`[I]` So writing a single formula into CVC column 5 silently cuts the number of CV voices in
half - the inference is a direct reading of the two lists above against each other.

## 3. Units, useful ranges, blank-column behaviour

| Column | Units | What blank does | Source |
|---|---|---|---|
| any of the eight | **volts**: "Don't set more than 10V, though the CVC should limit to 10V if you set higher" | 0 V on that output - and, for columns 5..8, blank is what keeps the bank at four voices. Blank is meaningful configuration here, not just silence | `[G]` `docs/EaganMatrixUserGuide.txt:4019-4020`, with the voice consequence `[G]` `docs/EaganMatrixUserGuide.txt:3976-3980` |

The guide's worked formula set, which is the only statement of how a formula becomes a voltage
`[G]` `docs/EaganMatrixUserGuide.txt:4002-4011`:

| Formula | What it produces | Source |
|---|---|---|
| A | "a W gate of 10V. You could change this to a lower value." | `[G]` `docs/EaganMatrixUserGuide.txt:4002` |
| B | pitch CV: "If this is set Octave, Min V = -1.0 and Max V = + 1.0, the voltage will scale 1 Volt per octave (a normal setting for Eurorack and many synths)". The example instead uses -1.1 V to +1.1 V with a -0.15 cents trim for a Moog; Buchla's 1.2 V per octave needs -1.2 and +1.2 | `[G]` `docs/EaganMatrixUserGuide.txt:4003-4008` |
| C | "a linear Y CV scaling of 0 to 10V with beginning and ending shelving" | `[G]` `docs/EaganMatrixUserGuide.txt:4009` |
| D | "a linear pressure scaling of 0 to 10 V" | `[G]` `docs/EaganMatrixUserGuide.txt:4011` |

`[I]` Pitch CV is therefore produced by the pitch component's **transfer** in Octave mode, not
by the column: the column only routes it - the inference is from the worked example setting
the minimum and maximum volts inside the formula `[G]`
`docs/EaganMatrixUserGuide.txt:4003-4008`.

`[C]` The corpus confirms the mapping arithmetically: the family `CVC 5v C0 / C2 / C4` differs
from `CVC 10v Linear Z` only in the pitch-zero note number and in halving the heights to 0.50,
which is exactly what a 10 V to 5 V change predicts
(`analysis/findings/corpus-module-wiring.md` S11).

## 4. Properties-panel settings and MCP reachability

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankB/C`, value 8 | **yes** - `set_bank_type("B", "CVC")`, and the tool **correctly refuses bank A** with `ValueError("CVC is only available in bank B/C")` `[G]` `eagan_mcp/setup.py:231-232`. Do not remove that refusal |
| All eight columns | matrix cells 35-42 / 43-50 | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| **Standard CV configuration**, used only when no CVC bank is in the matrix | `idCvcCfg = 63`, with bitfields for the voltage range, Z-squared, **Layer** and the **base voice** | **unreachable**: nothing decodes or writes it, and the Layer bit and the base-voice bits live here, so the allocation rules in section 2 are governed by an id no tool can set `[G]` `docs/HakenMidi.h:1447-1451` |
| Surface and MIDI-in routing to the CVC | `idRouting = 36`, with a surface bit and a MIDI-in bit | **unreachable** `[G]` `docs/HakenMidi.h:1452-1458` |
| Column-mode toggles, bank-param | **no CVC entry** | not applicable `[G]` `docs/HakenMidi.h:1579-1597` |

`[I]` Both unreachable ids are single `s_Mat_Poke` values and `_write_setup` already exists in
`eagan_mcp/server.py`, so the inference is that only a tool entry is missing.
**`tools_spec.md` `T22` (`set_module_option`) covers writing an arbitrary `s_Mat_Poke` id**,
and the `T` scheme runs to twenty-two ranks, not twenty. Neither id appears in
`analysis/findings/modules-mcp-reachability.md` section 5's twelve ranks, so `T22` carries
them on its own authority rather than inheriting a rank. `T4` is the nearest existing rank
and covers only labelling what is already read.

A CVC bank in the matrix **overrides** the standard configuration `[G]`
`docs/EaganMatrixUserGuide.txt:4017-4018`, verbatim: "If the EaganMatrix is supplying CV
voltages, the Editor will display `CVC via Matrix` in the Editor. Otherwise, the Editor will
display the Standard CV Definition being used."

## 5. DSP cost class

**Negligible** `[I]` - no audio is synthesised; the eight columns are formula evaluations
routed to a hardware converter `[G]` `docs/EaganMatrixUserGuide.txt:4021-4022`, and the
inference from that is that the cost is the cost of eight formulas. The guide gives no cost
statement, and the gap is filed as corpus-owned with `get_status` as the measurement
(`analysis/findings/modules-unfilled-checklist.md` gap 21).

## 6. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`CVC Four Shape Generators` - all eight outputs, one formula each `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: B = CVC
Bank B 1..8 <- Direct + = A, B, C, D, E, F, G, H     (one formula per CV output)
SG 1 F <- Direct + = I               SG 1 T <- Direct + = W
SG 2 F <- Direct + = I, Direct x = 0.5   SG 2 T <- Direct + = W
SG 3 F <- Direct + = 0.5             SG 3 T <- Direct + = 1   (free-running)
SG 4 F <- Direct + = 5               SG 4 T <- Direct + = 1   (free-running)
```

`[C]` Note what writing columns 5..8 costs this preset: it is a one-voice CV source by
construction, which is exactly the halving described in section 2. Note also the two
free-running shape generators, whose trigger column holds a bare constant rather than the
gate code.

`CVC 10v Linear Z` - the calibration reference, and the only four-column example `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: B = CVC
Bank B 1 <- Direct + = A      A = W Gated 1.00 x10                      (gate -> 10 V)
Bank B 2 <- Direct + = B      B = X Below -1.00 -> Above +1.00, Octaves (1 V per octave)
Bank B 3 <- Direct + = C      C = Y 0 -> 1.00 x10, with a begin shelf
Bank B 4 <- Direct + = D      D = Z 0 -> 1.00 x10, Linear
```

`[C]` This is the guide's four worked formulas realised cell for cell: gate, pitch, a shelved
wheel ramp and a linear pressure ramp, on outputs 1 to 4 and nothing else - so the bank stays
at four CV voices.

The guide points at two whole factory categories rather than at single presets `[G]`
`docs/EaganMatrixUserGuide.txt:3983-3985`, verbatim: "A set of CVC programming examples are
available in the Utilities/CVC Category that can be used as starting points for additional
changes if desired", and `[G]` `docs/EaganMatrixUserGuide.txt:4023-4024`, verbatim: "A set of
predefined CVC presets are available in the CVC System Preset category". `[C]` The corpus
holds 15 of them.

## 7. Known traps

1. **CVC cannot go in bank A**, and the tool's refusal is correct `[G]`
   `docs/HakenMidi.h:1571`.
2. **Writing anything into columns 5..8 halves the CV voice count** `[G]`
   `docs/EaganMatrixUserGuide.txt:3976-3980`.
3. **Base channel, not polyphony, decides the CV voice count**, and voices past the limit are
   silently ignored rather than wrapped `[G]` `docs/EaganMatrixUserGuide.txt:3971-3980`.
4. **Two Continuum split modes override EaganMatrix control of the CVC entirely** `[G]`
   `docs/EaganMatrixUserGuide.txt:4027-4037`: internal sound below the split hands the CVC
   above it to the Standard CV Definition, and internal sound above the split is the mirror.
   Those are two values of the split-mode id `[G]` `docs/HakenMidi.h:1427`, `:1432`.
5. **Split modes do not apply to the ContinuuMini**, which exposes only two WXYZ channels and
   gives unpredictable values played duo-tactically `[G]`
   `docs/EaganMatrixUserGuide.txt:4040-4043`, verbatim: "It is best to play the ContinuuMini
   monophonically for most predictable CVC output."
6. **Pitch scaling is per-synth** - 1 V per octave for Eurorack, about 1.1 V with a cents trim
   for a Moog, 1.2 V per octave for Buchla - and it is set in the pitch formula's transfer, not
   in the column `[G]` `docs/EaganMatrixUserGuide.txt:4003-4008`.
7. **A 10 V ceiling** `[G]` `docs/EaganMatrixUserGuide.txt:4019-4020`.
8. **Routing questions belong to the CVC guide, not this card** `[G]`
   `docs/EaganMatrixUserGuide.txt:4018`.
