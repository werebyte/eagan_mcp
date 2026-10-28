# Module card - Kinetic (kinetic physical model)

Bank wire value **9**, bank A or bank B only `[G]` `docs/HakenMidi.h:1566`.
Device-corroborated: "Kinetic=9 ... match factory presets" `[D]` `CLAUDE.md:81-83`,
2026-10-25, fw 10.81. Guide section 6.12, "Multipurpose Banks: Kinetic (Kinetic Physical
Model)" `[G]` `docs/EaganMatrixUserGuide.txt:3768`. Card schema, shared facts and the
module-name spelling: `index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle and the stiction column as
a Greek mu; this card writes `In` and `mu` `[G]` `docs/EaganMatrixUserGuide.txt:3773`,
`:3780`.

## TL;DR

A state-space model of a mass on a spring, anchored inside a one-dimensional container of
viscous fluid, whose output is the **position of the mass** `[G]`
`docs/EaganMatrixUserGuide.txt:3806-3807`.

Columns 1..4 are fixed and columns 5..8 are assignable (`index.md`, shared fact 2), and what
the assignable columns compute is **added** to the matching Properties value `[G]`
`docs/EaganMatrixUserGuide.txt:3789-3793`.

Two properties are explicitly stated to be **not modulatable from the matrix**, and the
header's selector range independently agrees `[G]` `docs/EaganMatrixUserGuide.txt:3838-3839`,
`:3853-3855`.

`F` here is not absolute pitch: it is only in kHz once the per-preset Step Frequency Trim has
been calibrated, and no tool can set that trim `[G]`
`docs/EaganMatrixUserGuide.txt:3781-3783`, `:3889-3893`.

`[C]` 68 of the 668 factory presets run a Kinetic (`census.json`,
`modules_used_including_defaults`).

## Key Decisions

- The header's assignable range is taken as authoritative, so container height and elasticity
   are carded as **available** assignable columns; the guide's narrower list is recorded as a
   conflict in section 1 rather than dropped `[G]` `docs/HakenMidi.h:1684-1687` against `[G]`
   `docs/EaganMatrixUserGuide.txt:3785-3794`.
- `F` is carded with its trim caveat up front, because it makes Kinetic the one bank whose
   frequency column is not absolutely tuned `[G]` `docs/EaganMatrixUserGuide.txt:3889-3893`.

## Open Questions / Risks

- Several silence modes are documented only qualitatively - ultra-high gravity `[G]`
   `docs/EaganMatrixUserGuide.txt:3840-3842`, high stiction `[G]`
   `docs/EaganMatrixUserGuide.txt:3875-3876`, strongly negative elasticity `[G]`
   `docs/EaganMatrixUserGuide.txt:3859-3864` - with **no thresholds**. See section 2.
- `[G]` `docs/EaganMatrixUserGuide.txt:3893-3894` gives the Step Frequency Trim's note number
   as "+/- 24 increments from the center position which does not imply a specific frequency",
   and says nothing further about the cents range.
- `[I]` Bow speed and stiction are stated to be settable **only** from the matrix `[G]`
   `docs/EaganMatrixUserGuide.txt:3874`, `:3882`, so the inference is that their absence from
   the Properties panel is by design rather than an omission in this card.

---

## 1. What every column means

| Col (bank A) | Fixed? | Label | Meaning | Source |
|---|---|---|---|---|
| 1 (27) | fixed | `In` | Excitation input, "a force on the Kinetic Model's mass, value range -2 to 2. The output of the Kinetic Model will be the position of the mass." | `[G]` `docs/EaganMatrixUserGuide.txt:3772-3774` |
| 2 (28) | fixed | `B` | Bow speed, range -1 to 1. "In the Kinetic Model's Properties, Slipping Friction and Quit-slipping Speed will affect the function of the bow." | `[G]` `docs/EaganMatrixUserGuide.txt:3776-3778` |
| 3 (29) | fixed | `mu` | "Static Friction (Stiction) value range 0 to 1" | `[G]` `docs/EaganMatrixUserGuide.txt:3780` |
| 4 (30) | fixed | `F` | "Frequency, in kHz. In the Kinetic Model's Properties, the Step Frequency Trim adjusts the model to make this column exact kHz units." | `[G]` `docs/EaganMatrixUserGuide.txt:3781-3783` |
| 5..8 (31-34) | assignable | preset data | "Select the function of the last four Kinetic columns by clicking on each column's heading. The value computed in the column will be added to the corresponding value in the Kinetic Model's Properties." | `[G]` `docs/EaganMatrixUserGuide.txt:3789-3793` |

The eleven assignable values and their ids are `index.md`, shared fact 2 `[G]`
`docs/HakenMidi.h:1671-1681`. What each one does in a Kinetic, from the Properties text:

| Value | Meaning | Source |
|---|---|---|
| anchor position | "affects the `resting position` of the mass. A nonzero offset is sonically interesting since it breaks the overall symmetry or the model. Setting the Anchor Position with an audio signal is a useful way to excite the model." Bipolar -1.00 to +1.00, default 0.0, MIDI 0..127 with 64 = 0.00 | `[G]` `docs/EaganMatrixUserGuide.txt:3828-3831` |
| spring constant | "the higher this strength is, the higher frequency you will get. The strength can be zero, in which case the spring and the anchor position have no effect." | `[G]` `docs/EaganMatrixUserGuide.txt:3834-3835` |
| mass | "The higher the mass is, the more difficult it is to start moving, but the longer it will move, due to inertia. High mass also usually results in bass sound." | `[G]` `docs/EaganMatrixUserGuide.txt:3832-3833` |
| gravity | acceleration, independent of the mass; it "breaks the overall symmetry of the model, but ultra-high gravity will result in silence because the mass will stay on the bottom edge of the container" | `[G]` `docs/EaganMatrixUserGuide.txt:3840-3842` |
| height | container size: "If there is no bouncing (see Elasticity), the mass will be quickly stop when it reaches the top or bottom edge of the container; it will be stopped and lose all its kinetic energy, so the effect is quite different from `normal` audio signal clipping." | `[G]` `docs/EaganMatrixUserGuide.txt:3848-3850` |
| viscosity | "friction due to fluid filling the container... A Viscosity of 0 is like vacuum, a viscosity of 1 is like heavy oil." | `[G]` `docs/EaganMatrixUserGuide.txt:3851-3852` |
| elasticity | 0 = the mass loses all its energy at the edges; maximum positive = perfect bounce; intermediate = the percentage of energy kept; **negative values define a sticking force**, and "if the mass stays stuck to the edge, silence results". Bipolar -1.00 to +1.00, default 0.0, MIDI 64 = 0.00 | `[G]` `docs/EaganMatrixUserGuide.txt:3856-3866` |
| padding | container hardness: "For a soft container, a deformation occurs when the mass hits the edges, resulting in a smoother deceleration. To simulate this, Padding defines a deceleration area near the edges." | `[G]` `docs/EaganMatrixUserGuide.txt:3867-3869` |
| slipping friction | "the friction experienced by the mass once it is in motion (once it has overcome stiction). This friction does not depend on the speed of the mass, unlike friction due to viscosity. 0 means no slipping friction, and 1 (maximum) means that the slipping friction is the same value as the static friction." | `[G]` `docs/EaganMatrixUserGuide.txt:3877-3879` |
| quit-slipping speed | "the minimum speed that the mass will move before it stops, and static friction takes over" | `[G]` `docs/EaganMatrixUserGuide.txt:3880-3881` |

A second Kinetic model is available in bank B `[G]`
`docs/EaganMatrixUserGuide.txt:3796`.

```
CONFLICT: the assignable list omits container height and elasticity
  docs   [G]: the guide's column list beside "Select the function of the last four Kinetic
              columns by clicking on each column's heading" names only anchor, spring, mass,
              gravity, viscosity, padding, slipping and quit-slipping - no height, no
              elasticity - docs/EaganMatrixUserGuide.txt:3785-3794
  header [G]: the four column selectors accept the whole property range, which includes
              height and elasticity - docs/HakenMidi.h:1684-1687, with the values at
              :1671-1681
  effect: an agent following the guide believes container height and elasticity are static
              per preset, so it never offers "growing container" or "bounce amount on the
              wheel" although both are reachable from the matrix.
  resolution: the header wins under the project's resolution order, and the guide's list is
              recorded as incomplete rather than wrong. It is the merged device plan's DT21,
              which is blocked by tool: confirming it needs a write to a column selector,
              which lives in a stream nothing encodes (see section 3).
```

## 2. Units, useful ranges, blank-column behaviour

| Column | Range | What blank (= 0) does | Source |
|---|---|---|---|
| `In` | **-2 .. 2** | no external impact force. The model can still be driven by bowing, by moving the anchor, by gravity or by changing the height, so a blank input column is **not** silence | `[G]` `docs/EaganMatrixUserGuide.txt:3772-3774`, `:3808-3811` |
| `B` bow | **-1 .. 1** | "A value of 0 means no bowing" - documented and benign | `[G]` `docs/EaganMatrixUserGuide.txt:3883` |
| `mu` stiction | **0 .. 1** | no stiction, and the consequence is that **bowing stops working**: "This parameter has no effect if Static Friction is zero" | `[G]` `docs/EaganMatrixUserGuide.txt:3883-3884` |
| `F` | kHz **after the trim** | no model time advance `[I]` - the inference is that the frequency column sets how much model time passes per sample, so zero advances none |
| columns 5..8 | each adds to its Property | **the Property value, unchanged** - these are additive offsets | `[G]` `docs/EaganMatrixUserGuide.txt:3789-3793` |

**Blank-column verdict.** Columns 5..8 are genuinely neutral when blank, because they are
offsets onto Properties `[G]` `docs/EaganMatrixUserGuide.txt:3789-3793`. The trap is the
stiction column: blank stiction silently disables the whole bowing mechanism even when the bow
column is fully written `[G]` `docs/EaganMatrixUserGuide.txt:3883-3884`.

**Silence thresholds are not documented.** Three parameter extremes are stated to produce
silence and **none of them has a boundary**: ultra-high gravity pins the mass to the floor
`[G]` `docs/EaganMatrixUserGuide.txt:3840-3842`, high stiction stops it moving `[G]`
`docs/EaganMatrixUserGuide.txt:3875-3876`, and negative elasticity can glue it to an edge
`[G]` `docs/EaganMatrixUserGuide.txt:3859-3864`. `[C]` The usable ranges below are what the
factory actually writes, and they are a **used range, not a boundary**: the corpus shows where
presets sit, not where silence begins.

`[C]` Measured column occupancy over 77 Kinetic bank slots: c1 28%, c2 29%, c3 49%,
**c4 100%**, c5 76%, c6 75%, c7 46%, c8 24%; the modal assignable choices are anchor, spring
constant, viscosity and unused (`analysis/findings/corpus-module-wiring.md` S12). `[C]` The
frequency column is the only one written by every Kinetic slot in the corpus, and the
excitation input column is written by barely a quarter of them.

## 3. Properties-panel settings and MCP reachability

The whole Properties panel lives in the Kinetic property stream: write `s_Kinet_Poke` = stream
24, read back `s_Kinet` = stream 11, 24 ids per bank `[G]` `docs/HakenMidi.h:1101`, `:1137`,
`:1671-1719`.

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankA/B`, value 9 | **yes** - `set_bank_type("A", "Kinetic")` `[G]` `eagan_mcp/setup.py:227` |
| Matrix cells 27-34 / 35-42 | the matrix | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| All ten model properties: anchor, spring, mass, gravity, height, viscosity, elasticity, padding, slipping, quit-slipping | the property stream's ids 1..10 (bank A) / 25..34 (bank B) | **unreachable**: no codec reads or writes stream 11 or 24 `[G]` `docs/HakenMidi.h:1671-1681`. `T16` is the rank that would unblock it |
| **Which function each of columns 5..8 carries** | the four column selectors (`index.md`, shared fact 2) | **unreachable**, and without it no tool can name a Kinetic bank column `[G]` `docs/HakenMidi.h:1684-1687`. `T16` unblocks the read, `T4` then joins it into `get_matrix`'s labels |
| **Spring linearity** and **viscosity linearity** | ids 17 and 18 (bank A) / 41 and 42 | **unreachable**, and also **not modulatable from the matrix at all**: "This property is not modifiable from formulas in the matrix", said once for each `[G]` `docs/EaganMatrixUserGuide.txt:3838-3839`, `:3853-3855`, with the ids at `[G]` `docs/HakenMidi.h:1688-1689` |
| **Step Frequency Trim**: note number and cents | ids 19 and 20 (bank A) / 43 and 44 | **unreachable** `[G]` `docs/HakenMidi.h:1690-1691`. `T16` is the rank that would unblock it - and until then **no tool can tune a Kinetic bank** |
| RBJ deflation or IIT | the bank-param id (`index.md`, shared fact 4) | **read-only, decoded by name** as `bank_params.A.param` `[G]` `eagan_mcp/setup.py:190`. No write tool |

`[I]` The header's selector range stops at the last model property and below the two linearity
ids `[G]` `docs/HakenMidi.h:1684-1687`, `:1688-1689`, which is exactly consistent with the
guide's two "not modifiable from formulas" statements - the inference worth recording is that
two independent sources agreeing makes the selector range a real constraint rather than a
documentation convenience.

`[I]` Kinetic is the bank with the widest gap between what the matrix can express and what a
tool can set: ten properties, four column selectors and the tuning trim are all in one stream
nothing encodes - the inference is that `T16` alone decides whether this module is usable from
a tool at all.

## 4. DSP cost class

**Not documented.** The guide states no cost and gives Kinetic no Reduce Polyphony warning
`[I]` - the inference from that absence, where the guide does warn for two oscillator types
`[G]` `docs/EaganMatrixUserGuide.txt:7372` and for Additive `[G]`
`docs/EaganMatrixUserGuide.txt:3657`, is that Kinetic is not in the heavy class. That is weak
evidence and it is filed as a gap owned by the corpus, with `get_status` as the measurement
(`analysis/findings/modules-unfilled-checklist.md` gap 20).

## 5. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`Kinetic SatPad` - five oscillators exciting one Kinetic model through an **assignable**
column `[C]` (`factory_catalog.json`, `wiring`):

```
bank: A = Kinetic param=deflate 1 ; C = SummedDelay ; osc 1..5 all Integrated DSF
Bank A 4 (F) <- Direct + = F, Direct x = H
Bank A 5     <- Osc 1 = A, Osc 2 = A, Osc 3 = L, Osc 4 = A, Osc 5 = L, Direct x = M
Bank A 6     <- Direct + = B       Bank A 7 <- Direct + = 0.9
Bank A 8     <- Direct + = E
Master SL <- Bank A = 1, Bank C = 1, Direct x = 0.2
  F = W Constant 0.2 x10 x macro iv ; Y = 1.0 x0.1 ; anc ^2
  A = (W+X+Y)*Z, W = Constant 1.0 x macro ii ; Y = 1.0 x0.01 ; Z = 0 -> 1.0 x10
```

`[C]` The audio-rate excitation arrives on **column 5**, an assignable column, not on column
1, which this preset leaves blank. The guide explains why `[G]`
`docs/EaganMatrixUserGuide.txt:3829-3830`, verbatim: "Setting the Anchor Position with an audio
signal is a useful way to excite the model", and anchor position is the modal assignable choice
in the corpus `[C]` (`analysis/findings/corpus-module-wiring.md` S12).

`Bowed BiqBank` - a Kinetic used as a **bow** for a BiqBank `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: A = Kinetic ; B = BiqBank
Bank A 2 (B bow)  <- Direct + = E, Direct + (2) = 0.01, Direct x = G
Bank A 3 (mu)     <- Direct + = D        (D = W Constant 0.13)
Bank A 4 (F)      <- Direct + = K, Direct + (2) = 0.05
Bank A 5          <- Direct + = L
Bank B 1 <- Bank A = H, Direct + = B (MUTED), Direct x = J
Bank B 2 <- Direct + = X ; Bank B 3 <- Direct + = 1 ; Bank B 4 <- Direct + = A
Master SL/SR <- Bank A = V (MUTED), Bank B = 1
  E = W Constant 1.0 [Triangle] x macro i phase 180 ; Z = 0 -> 1.0 x0.1   (bow speed)
  G = W SG1 0.18 x0.1 [Sine]                                             (bow wobble)
  H = Z = 0 -> 0.5 x0.01    (the Kinetic row into the BiqBank excitation column)
```

`[C]` The Kinetic model's **position output** drives the BiqBank's excitation column, so the
bow friction cycle excites the modal bank. Note the stiction column written as a bare constant
0.13 - without it the bow column would do nothing. Note also the two muted cells: the Kinetic's
own output to the master is muted, so only the BiqBank is heard.

`Bowed KinBanjo` and `Bowed OtherMood` are the other two Kinetic presets with a shipped wiring
block, both in the bowed subset that drives the bow and stiction columns `[C]`
(`factory_catalog.json`, `wiring`).

Factory leads the guide names by category `[G]`
`docs/EaganMatrixUserGuide.txt:3907-3910`: drones `Bad Weather`, `Earthquake` and
`Kinetic Evil Ball`; synth `Kinetic SatPad`; and "the Various Kinetic Examples" in Utilities.
`[C]` **`Kinetic Evil Ball` is `Kinetic Evil Bell`** in the 668 filenames; `index.md` owns that
correction.

## 6. Known traps

1. **Zero stiction silently kills bowing.** The bow column can be fully written and the model
   still will not bow `[G]` `docs/EaganMatrixUserGuide.txt:3883-3884`.
2. **`F` is not absolute pitch.** Without a calibrated Step Frequency Trim the usual pitch code
   on the frequency column does not produce the played note, and the trim is out of a tool's
   reach `[G]` `docs/EaganMatrixUserGuide.txt:3889-3893`. The guide adds that this is normal
   `[G]` `docs/EaganMatrixUserGuide.txt:3895-3896`, verbatim: "The Kinetic Frequency (F) column
   does not have to use an X formula. The Kinetic Bank is often used more like a filter in
   terms of the F column".
3. **Three parameter extremes produce silence rather than a sound**, with no threshold given:
   ultra-high gravity `[G]` `docs/EaganMatrixUserGuide.txt:3840-3842`, high stiction `[G]`
   `docs/EaganMatrixUserGuide.txt:3875-3876`, negative elasticity strong enough to glue the
   mass to an edge `[G]` `docs/EaganMatrixUserGuide.txt:3859-3864`.
4. **A zero spring constant disables the spring and the anchor position together** `[G]`
   `docs/EaganMatrixUserGuide.txt:3834-3835`.
5. **Edge collisions are not clipping.** The mass "will be stopped and lose all its kinetic
   energy, so the effect is quite different from `normal` audio signal clipping" - do not reach
   for container height as a limiter `[G]` `docs/EaganMatrixUserGuide.txt:3848-3850`.
6. **Spring linearity and viscosity linearity cannot be modulated from the matrix**, and
   neither is tool-writable, so both are frozen at whatever the loaded preset had `[G]`
   `docs/EaganMatrixUserGuide.txt:3838-3839`, `:3853-3855`.
7. **The guide's assignable list omits height and elasticity** although the header allows them;
   see the conflict in section 1 `[G]` `docs/HakenMidi.h:1684-1687`.
8. **Kinetic is bank A or B only** - no bank C value `[G]` `docs/HakenMidi.h:1566`.
9. **Bipolar properties use MIDI 64 as zero**, so a raw stream value of 64 means 0.00 and not
   "half" `[G]` `docs/EaganMatrixUserGuide.txt:3830-3831`, `:3864-3866`.
10. **10.81 changed how the trim values are entered** `[G]`
    `docs/EaganMatrixUserGuide.txt:3901-3902`, verbatim: "You now enter the actual values you
    expect for the Note and Cent offsets. Previously these were interpreted as Midi range
    entries."
