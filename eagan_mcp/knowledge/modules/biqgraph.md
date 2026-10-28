# Module card - BiqGraph (modal graphs)

Bank wire value **1**, bank A or bank B `[G]` `docs/HakenMidi.h:1562`. Guide section 6.4,
"Multipurpose Banks: BiqGraph" `[G]` `docs/EaganMatrixUserGuide.txt:2593`. Card schema, shared
facts and the module-name spelling: `index.md`, which this card references and never restates.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

Rendering: the guide prints column 1's heading as a filled triangle; this card writes `In`
`[G]` `docs/EaganMatrixUserGuide.txt:2599`.

## TL;DR

The same biquad engine as BiqBank, but mode amplitudes come from three 48-slider **graphs**
instead of spread-and-centre arithmetic `[G]` `docs/EaganMatrixUserGuide.txt:2666-2667`. Its
columns are fixed, not assignable (`index.md`, shared fact 2).

Selecting `2T` on column 7 silently remaps three other columns at once - `B` becomes `T`, `sB`
becomes `P`, and a negative `sF` becomes a string inharmonicity coefficient `[G]`
`docs/EaganMatrixUserGuide.txt:2679-2702`. That is the single most surprising behaviour in the
bank family.

The graphs live in three streams nothing in this project decodes `[G]`
`docs/HakenMidi.h:1084-1088`, `:1134-1136`, so a BiqGraph preset's timbre is invisible to every
tool here.

`[C]` 44 of the 668 factory presets run a BiqGraph (`census.json`,
`modules_used_including_defaults`).

## Key Decisions

- `2T` is carded as a **mode switch**, not as a column, because three columns change meaning
   together `[G]` `docs/EaganMatrixUserGuide.txt:2679-2702`.
- The graphs are carded as a first-class unreachable surface with their own stream numbers,
   since without them a BiqGraph has no timbre at all `[G]`
   `docs/EaganMatrixUserGuide.txt:2650-2653`.

## Open Questions / Risks

- `[G]` `docs/EaganMatrixUserGuide.txt:2679` says only "If the 2T column is selected" and does
   not say what selects it; the header's BiqGraph column-mode values cover graph-2-to-amplitude
   against graph-2-to-bandwidth and graph-1-to-amplitude against graph-1-to-frequency, with no
   `2T` value `[G]` `docs/HakenMidi.h:1579`, `:1587`. Which wire id selects `2T` is **not
   identified**.
- `[C]` Column 4 is written in 41 of 41 measured BiqGraph bank slots, so the corpus offers no
   example of a blank `B` to reason from
   (`analysis/findings/corpus-module-wiring.md` S3).

---

## 1. What every column means

Normal mode, with no `2T` selected `[G]` `docs/EaganMatrixUserGuide.txt:2596-2632`:

| Col (bank A / bank B) | Label | Meaning | Source |
|---|---|---|---|
| 1 (27 / 35) | `In` | Excitation input for all modes; the mode count is set above this column | `[G]` `docs/EaganMatrixUserGuide.txt:2597-2601` |
| 2 (28 / 36) | `F` | "Frequency (in kHz) for the first mode (first resonance)" | `[G]` `docs/EaganMatrixUserGuide.txt:2603` |
| 3 (29 / 37) | `sF` | Frequency spread: "1 for harmonic spacing of modes, >1 stretched harmonics, <1 compressed" | `[G]` `docs/EaganMatrixUserGuide.txt:2605` |
| 4 (30 / 38) | `B` | Bandwidth: value 1 = bandwidth 0 dB down, i.e. the bandwidth equals the mode frequency; value 0 = bandwidth **-100 dB down** | `[G]` `docs/EaganMatrixUserGuide.txt:2607-2609` |
| 5 (31 / 39) | `sB` | Bandwidth spread: 0 = all modes the same, >0 = higher modes wider, <0 = narrower | `[G]` `docs/EaganMatrixUserGuide.txt:2617-2618` |
| 6 (32 / 40) | `1A` or `1F` | Scale factor for the 1 Graph: `1A` offsets mode dB amplitudes, `1F` offsets mode percentage frequencies | `[G]` `docs/EaganMatrixUserGuide.txt:2624-2626` |
| 7 (33 / 41) | `2A`, `2B` or `2T` | Scale factor for the 2 Graph: `2A` offsets dB amplitudes, `2B` offsets dB bandwidths, `2T` switches the whole bank to decay-time constants | `[G]` `docs/EaganMatrixUserGuide.txt:2627-2631` |
| 8 (34 / 42) | - | Not described for BiqGraph | `[C]` written in 4% of 41 bank slots (`analysis/findings/corpus-module-wiring.md` S3) |

With `2T` selected, three columns change meaning simultaneously `[G]`
`docs/EaganMatrixUserGuide.txt:2679-2702`:

| Column | Normal | With `2T` | Source |
|---|---|---|---|
| 7 | `2A` or `2B` | `2T`, an overall scale factor for the offset-2 graph, normally 0.0..1.0 | `[G]` `docs/EaganMatrixUserGuide.txt:2680-2683` |
| 4 | `B` bandwidth | `T`, a decay time constant, usually 0.0..1.0 | `[G]` `docs/EaganMatrixUserGuide.txt:2696-2698` |
| 5 | `sB` bandwidth spread | `P`, the position of excitation along the string; 0..0.5 mirrors 0.5..1 because a string is symmetric | `[G]` `docs/EaganMatrixUserGuide.txt:2699-2702` |
| 3 | `sF` spread | a negative `sF` becomes a **string inharmonicity coefficient**, `Fk = F0 x k x sqrt(1 - sF x k x k)` | `[G]` `docs/EaganMatrixUserGuide.txt:2684-2695` |

The `2T` path is new in 10.50 and exists for string modelling `[G]`
`docs/EaganMatrixUserGuide.txt:2672-2674`.

```
CONFLICT: where string excitation position lives - VOID, not filled
  docs   [G]: under 2T, "sB column becomes P (position specifier). If you are modelling a
              string with the BiqGraph, then P is the position of the excitement along the
              string" - docs/EaganMatrixUserGuide.txt:2699-2700
  header [G]: the BiqBank/SineBank property block attaches inharmonicity to a negative sF
              AND excitation position to a negative qF, in the same two comments
              - docs/HakenMidi.h:1727-1730
  agreement: both sources put string INHARMONICITY on a negative sF.
  disagreement: the guide puts excitation POSITION on the sB column under 2T; the header puts
              it on a negative qF. BiqGraph has no qF column at all, and the header's ids are
              the BiqBank/SineBank property block, which may simply be a different mechanism -
              so both may be true of different banks.
  effect: an agent writing "pluck position" into the wrong place gets a bandwidth spread or a
              quadratic frequency offset instead - audible, wrong, and hard to diagnose.
  resolution: UNRESOLVED, and left unresolved. No local source settles it, so a guess would be
              indistinguishable from a fact. It is the merged device plan's DT13, which writes
              a negative qF into a 2T BiqGraph and listens for a pluck-position change
              (analysis/findings/modules-unfilled-checklist.md gap 10).
```

## 2. Units, useful ranges, blank-column behaviour

| Column | Range | What blank (= 0) does | Source |
|---|---|---|---|
| `F` | kHz | silence `[I]`, the inference being that a zero first-mode frequency leaves nothing to resonate |
| `sF` | 1 = harmonic | **not neutral**: 0 is inharmonic, since 1 is the harmonic value | `[G]` `docs/EaganMatrixUserGuide.txt:2605` |
| `B` | 0..1, where 1 = 0 dB down and 0 = -100 dB down | **not neutral**: blank is a bandwidth 100 dB down, i.e. extreme resonance | `[G]` `docs/EaganMatrixUserGuide.txt:2607-2609` |
| `sB` | bipolar | benign: 0 = all modes the same bandwidth | `[G]` `docs/EaganMatrixUserGuide.txt:2617-2618` |
| `1A` / `1F` / `2A` / `2B` | graph scale factors | that offset graph contributes nothing and the A graph alone sets amplitudes | `[G]` `docs/EaganMatrixUserGuide.txt:2710-2712` |
| `2T` | 0.0..1.0 typical; larger works but has no reason to | - | `[G]` `docs/EaganMatrixUserGuide.txt:2680-2683` |
| `T` under `2T` | 0.0..1.0 | no decay time `[I]`, the inference being that a decay-time column reading zero sets no decay time |
| `P` under `2T` | 0..0.5 is the same as 0.5..1 | excitation at the string end `[I]`, the inference being that position 0 is one end of a symmetric string |

The amplitude rule `[G]` `docs/EaganMatrixUserGuide.txt:2710-2712`, verbatim: "amplitude of
each of the modes is computed from the Mode Amplitude A graph, plus matrix column 1A times the
1 Graph, plus matrix column 2A times the 2 Graph" (the guide's PDF extraction splits the "dB"
before this phrase).

`[C]` Measured column occupancy over 41 BiqGraph bank slots: c1 100%, c2 100%, c3 97%,
**c4 100%**, c5 56%, c6 78%, c7 65%, c8 4%. The `B` column is never blank in the corpus
(`analysis/findings/corpus-module-wiring.md` S3).

## 3. Properties-panel settings and MCP reachability

| Surface | Wire | Reachable today |
|---|---|---|
| Bank type | `idBankA/B` | **yes** - `set_bank_type("A", "BiqGraph")` `[G]` `eagan_mcp/setup.py:227` |
| Matrix cells 27-34 / 35-42 | the matrix | **yes** - `set_matrix_point` `[G]` `eagan_mcp/server.py:255` |
| **A graph**, 48 mode amplitudes 0..96, with 96 as the 0 dB value | read stream 2, write stream 21, id 0..47 | **unreachable**: no codec `[G]` `docs/HakenMidi.h:1084-1085`, `:1134` |
| **1 Graph**, 48 offsets, with 48 as the 0 dB value | read stream 3, write stream 22 | **unreachable** `[G]` `docs/HakenMidi.h:1086`, `:1088`, `:1135` |
| **2 Graph**, the second offset set | read stream 4, write stream 23 | **unreachable** `[G]` `docs/HakenMidi.h:1087`, `:1136` |
| Graph 2 to amplitude or bandwidth; graph 1 to amplitude or frequency | the two column-mode toggles (`index.md`, shared fact 3) | **read-only and undecoded**: `get_setup` returns `column_mode_1_raw` and `column_mode_2_raw` as bare numbers `[G]` `eagan_mcp/setup.py:191-192`. No write tool |
| Mode count, 8 / 16 / 24 / 32 / 40 / 48 | `idBqExt` (`index.md`, shared fact 5) | **read-only and undecoded** as `biquad_size_raw` `[G]` `eagan_mcp/setup.py:193`. No write tool |
| Deflation Limit 0..7 or IIT | the bank-param id (`index.md`, shared fact 4) | **read-only, decoded by name** as `bank_params.A.param` `[G]` `eagan_mcp/setup.py:190`. No write tool |
| `2T` selection | **not identified in the header** | unreachable, and not even nameable - see the Open Questions above `[G]` `docs/HakenMidi.h:1579` |

`[I]` BiqGraph is the **least** MCP-complete bank: its three graphs hold the timbre and none of
them is read or written, so a matrix dump plus a setup dump cannot explain how a BiqGraph
preset sounds - the inference is that a module whose amplitudes live outside the matrix cannot
be described by reading the matrix. `T16` is the nearest rank and it does **not** cover the
graph streams; the ranked list that names streams 2/3/4 and pokes 21/22/23 is
`analysis/findings/modules-mcp-reachability.md` section 5 rank 12, which `tools_spec.md` has
still to fold into the `T` namespace.

## 4. DSP cost class

**Medium to heavy, scaling with the mode count**, which is 8, 16, 24, 32, 40 or 48 `[G]`
`docs/EaganMatrixUserGuide.txt:2657-2659`. The guide gives no separate figure for BiqGraph
`[I]` - the inference from the shared engine (`docs/EaganMatrixUserGuide.txt:2647-2648` names
BiqBank, BiqGraph, BiqMouth and ModMan as four ways to control one set of biquad bandpass
filters) is that `biqbank.md`'s cost profile applies, and that inference is all the local
sources support.

## 5. Typical wiring

Cell orientation is `column <- row = value`, the orientation `set_matrix_point(row, col,
value)` takes `[G]` `eagan_mcp/server.py:255`.

`Silver Bar` - twin BiqGraph with a symmetric detune that is also the stereo width `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: A = BiqGraph param=IIT ; B = BiqGraph param=IIT ; C = MicroDelay ; recirc = Long Reverb
Bank A 1 <- Noise = A, Osc 5 = 1, Direct x = R    (identical for Bank B 1)
Bank A 2 <- Direct + = X                Bank B 2 <- Direct + = X
Bank A 3 <- Direct + = D, Direct + (2) = C      <-- detuned up by C
Bank B 3 <- Direct + = D, Direct -   = C      <-- detuned down by C
Bank A 4 / B 4 <- Direct + = B, Direct x = M
Bank A 6 / B 6 <- 1 ;  Bank A 7 / B 7 <- 0.9 ;  Bank A 8 / B 8 <- 0.2
Master SL <- Bank A = F, Tap 1 = Q, Direct x = 3
Master SR <- Bank B = F, Tap 2 = Q, Direct x = 3
  B = W Constant 0.16 ; blend macro          (bandwidth, about 0.16 x M = 4.2 -> 0.67)
  C = W*(X+Y+Z), Z = 0 -> 0.5 ; blend macro  (the detune, opens with pressure)
```

`[C]` One letter `C` arriving on `Direct + (2)` in bank A and `Direct -` in bank B is the
two-bank detune construction; 41 presets share a letter between the two banks' column 3
(`index.md` pattern 2 covers the generic form).

`Underwater Ceramics` - a single BiqGraph with three shape generators on one speed macro `[C]`
(`factory_catalog.json`, `wiring`):

```
bank: A = BiqGraph ; recirc = Modulated Delay ; master col 3 drives Recirc R3
Bank A 1 <- Noise = A
Bank A 2 <- Direct + = X        Bank A 3 <- Direct - = E
Bank A 4 <- Direct + = F, Direct + (2) = 0.2
Bank A 5 <- Direct + = C, Direct + (2) = 0.25
Bank A 6 <- Direct + = G        Bank A 7 <- Direct + = B
SG 2 F <- 0.47, Direct x = J      SG 3 F <- 0.97, Direct x = J
  F = (W+X)*(Y+Z), X = 1.0 -> 0.78 Linear ; Z = 0.72 -> 0.64     (bandwidth, 0.64..0.72)
  J = W Constant 0.5 x10 x macro i                               (one speed macro, 3 LFOs)
```

`[C]` Note `Bank A 4` never sits at a bare zero: both presets build the bandwidth from a letter
plus a constant, which is what a column whose zero is -100 dB down forces.

## 6. Known traps

1. **A blank `B` is a bandwidth 100 dB down**, i.e. near-infinite resonance, not a neutral
   filter `[G]` `docs/EaganMatrixUserGuide.txt:2607-2609`.
2. **Selecting `2T` remaps `B` to `T` and `sB` to `P` and arms a negative `sF` as
   inharmonicity.** A builder writing "bandwidth" into a `2T` BiqGraph is writing a decay time
   `[G]` `docs/EaganMatrixUserGuide.txt:2679-2702`.
3. **Two BiqGraphs share one set of graphs** `[G]`
   `docs/EaganMatrixUserGuide.txt:2641`, verbatim: "When two BiqGraphs are in use, they share
   the same graph data." Editing bank A's graphs changes bank B's timbre - the same
   shared-resource hazard as formula letters.
4. **A BiqGraph with no graph content has no timbre, and no tool can see the graphs**, so a
   matrix read cannot explain the sound `[G]` `docs/HakenMidi.h:1084-1088`.
5. **Graph sliders beyond the active mode count do nothing** and "should be left in their
   default positions" `[G]` `docs/EaganMatrixUserGuide.txt:2713-2714`.
6. **Deflation guidance is the same as BiqBank's**: the largest value between 0 and 7 that does
   not affect the timbre `[G]` `docs/EaganMatrixUserGuide.txt:2660-2662`.
7. **Where pluck position lives is a void, not a detail.** See the conflict block in section 1;
   do not pick a side from this card `[G]` `docs/EaganMatrixUserGuide.txt:2699-2700` against
   `[G]` `docs/HakenMidi.h:1729-1730`.
8. `[C]` **The corpus cannot help with blank columns here**: columns 1, 2 and 4 are written in
   41 of 41 bank slots, so every factory BiqGraph avoids the blank cases entirely
   (`analysis/findings/corpus-module-wiring.md` S3).
