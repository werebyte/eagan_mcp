# What goes wrong, in the order you can hit it

Seventy-six ways to break a patch, a preset or your ears, ordered by the point in patch
construction where you need the warning - not by which document they came from. Read section 1
before the first write of a session; read each later section at the moment its heading describes.

> Citations of the form `analysis/findings/...` are the 2026-10-26 research pass's
> working files and are **not shipped**; the data behind a `[C]` claim is
> `factory_catalog.json`. See `index.md`, "Research-pass citations are not shipped".

## What this file owns, and where everything else lives

| File | Owns |
|---|---|
| `model.md` | How a voice is computed, the five loudness rules N1-N5 with their citations, what the MCP cannot do, and the standing hazards that outlive a session |
| `modules/index.md` | The nine shared module facts and the Master chain's parameter tables |
| `modules/<type>.md` | One module, including its own numbered "Known traps" list |
| `patterns.md` | Reusable constructions across modules - how to build a thing |
| `pitfalls.md` (this file) | What goes wrong, in the order you can hit it |
| `RECIPES.md` (repository root) | Recipes tested on the Module by ear, each carrying the pitfalls inseparable from its own steps |

This file is the canonical home of **standalone** pitfalls. A pitfall that cannot be separated
from a recipe's steps stays with that recipe in `RECIPES.md`; nine such items moved here and eight
stayed there
(`.maister/docs/standards/global/conventions.md:10`). Where a module card already owns a trap in
its own "Known traps" section, this file names it and points at the card rather than restating it;
the same holds for `model.md` section 8 (the N1-N5 rules), `model.md` section 9 (the three
obstacles a plain reading of the guide hides) and `model.md` section 11 (the standing hazards).

## The count, and its scope

**76 items**, which is the merged, action-ordered set: the device findings this project made, the
module cards' traps, and the literature sweep, de-duplicated and re-ordered. A different number
appears in the research findings -
`.maister/tasks/research/2026-10-26-eagan-matrix-knowledge-base/analysis/findings/cookbook-traps.md:416-418`
counts "8 of 8 handoff traps confirmed; 19 new traps found" = 27. That is **that file's**
granularity, where a whole table of safe amplitudes counts as one trap and the controller-specific
set is not counted at all. Neither number contradicts the other; they count different things.

## How to read the evidence tags

Tags, resolution order and the CONFLICT block are defined once, in
`.maister/docs/standards/protocol/protocol-sources.md`, "The Five Bracket Tags". This file follows
them and does not restate them. Two points bear on the citations below: a `[G]` *header* citation
is fw 10.81 while a `[G]` *guide* citation is fw 10.80 at best, because
`docs/EaganMatrixUserGuide.txt:3-4` is stamped "Firmware Version 10.61 to 10.80"; and guide line
numbers drift inside a section, so every guide claim quotes verbatim - the quote, not the line
number, is the locator.

Every item is marked `known` (it was already in `RECIPES.md` or `CLAUDE.md` before the knowledge
base existed) or `new` (it was not).

**A note on the `[D]` citations marked `(moved)`.** Forty-eight lines of `RECIPES.md` - its old
"Pitfalls on the EM Module" section - are the source of several items here, and they are now in
this file rather than in `RECIPES.md`. Those citations keep the original `RECIPES.md` line so the
provenance of the device test survives, and carry `(moved)` to say the line no longer resolves in
the current `RECIPES.md`. The date and firmware are the original test's.

ASCII only: `->` is an arrow, `+-` plus-or-minus, `x` multiply. The guides print arrows, curly
quotes, en dashes and a plus-minus glyph; quotations here are transliterated under that rule and
are otherwise verbatim.

---

## 1. Before writing any output level

The one section to read before touching anything. An EaganMatrix output explosion is loud enough
to damage hearing and equipment, and the firmware's own protection is not running while this MCP
holds the port (item 4).

1. **Read the five numbered rules before the first output write.** `new` - N1 to N5 are guide
   section 13, "How to Protect For and Avoid Sonic Booms!" `[G]`
   `docs/EaganMatrixUserGuide.txt:8411-8454`. They are quoted with per-rule citations in
   `model.md` section 8 and are **not** restated here. In short: no constants in output formulas,
   nothing past 0.1 into noise or biquad inputs, cap `Z` at 30-50%, do not experiment freely with
   noise plus biquads, and know your attenuation point before you need it.
2. **The three physical precautions are not optional.** `new` - `[G]`
   `docs/EaganMatrixUserGuide.txt:8419-8422`, verbatim: "1. Don't use headphones. 2. Put a limiter
   in your audio processing chain. Some mixers have this feature. 3. Keep the volume very low
   while making changes. Any of Attenuator, Post Level, outboard level (mixer, computer system
   volume, amp volume etc.)."
3. **The Cookbook opens with the same warning, before any content.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:20-26`, verbatim: "Programming Note: Always turn down
   your gain / attenuation when experimenting making changes in the EaganMatrix. Never use
   headphones while experimenting with preset changes - especially those involving Biquad banks,
   noise and anything you make bandwidth changes on. You can (and will at times) create very loud
   and sometimes suddenly explosive output. Also take special care when putting constants on the
   SL/SR or L/R columns unless the output is controlled by Z somewhere else in the formula."
4. **There is no automatic gain protection while the MCP is connected.** `new` - the Reduce Gain
   detection runs only while the Editor is running, and Windows MIDI ports are exclusive, so the
   Editor cannot be running `[I]`; the inference is immediate from those two facts together. Stated
   with its citation in `model.md` section 8, "No automatic gain protection". An agent that reasons
   from the feature's existence will assume protection that is not there.
5. **Prefer N5's macro form, not its CC form, as the kill switch.** `known` - put a free macro as a
   multiplier down to zero on the SL/SR columns, which is an ordinary matrix write and restores
   exactly. The guide's other half, `ch1 cc18 0 = Mute, 1 = Unmute`, conflicts with the header's
   `ccPost = 18` post-Master output level: the header wins, so 0 mutes but 1 is 1/127 of full
   level, not unmute `[I]`. The inference and both sides of the conflict are in `model.md`
   section 10, "ch1 cc18 - mute button vs post level"; no typed tool reaches the CC path in any
   case.
6. **Start a new output at `.1`, not at `.5`.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:1674-1676`, verbatim: "Now on the A row in the SL/SR
   column set a constant of .1. This will insure you don't create an explosion if you do something
   wrong." The same worked example raises it to `.5` only once the patch is known good.
7. **The safe starting amplitudes the docs actually use.** `new` - default to these `[G]` guide
   values rather than deriving one:

| Target | Safe value | Citation |
|---|---|---|
| Noise into a BiqBank excitation column | `.001` on the chart page, `.01` to `.02` in the percussion recipe | `[G]` `docs/EaganMatrix Preset Cookbook.txt:2197`, `:1658`, `:1692` |
| Noise straight into the SubMix | `0.04`, and "be careful outputting high level of noise directly to the SubMix" | `[G]` `docs/EaganMatrix Preset Cookbook.txt:885` |
| Noise into a ModMan | `.01` multiplied by `.1` - "look at how little is used" | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1936-1938` |
| Any SL/SR output in a new patch | `.1` first, then `.5` | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1674-1676`, `:1685` |
| Delay feedback | "almost always a fraction", never past unity | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1473`, `:11882-11885` |
| Audio into a delay network | "BE CAREFUL SENDING HIGH AMPLITUDE INPUT TO A DELAY NETWORK" - the capitals are the Cookbook's | `[G]` `docs/EaganMatrix Preset Cookbook.txt:11872-11875` |
| Cross-modulation input | `0.1` gives a complex tone; at `0.5` "Noise starts to become main component" | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1425-1441` |
| Unity on an output | never, unless `Z` controls that output elsewhere in the design | `[G]` `docs/EaganMatrix Preset Cookbook.txt:5934-5937` |

8. **Delay feedback past unity is a runaway, not a long tail.** `new` - the feedback coefficient is
   "almost always a fraction", and the Cookbook's instruction is to make "sure it never goes past
   unity which can cause the feedback loop to go out of control" `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:1473`. A feedback formula driven by a macro needs its own
   ceiling, because a macro reaches 1.
9. **Changing a HarMan spectral set can explode a working preset.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:1877-1884`, verbatim: "Take Care Note: Turn down your
   gain / attenuation if you try and change spectral sets on a preset using the Harman. Some of
   them have higher amplitude profiles and different envelopes that can create very loud output on
   some presets if you just change between them." Swapping a spectral set is a loudness hazard, not
   a neutral change of timbre.
10. **Ramp Up on an amplitude column, and sample-and-hold on noise, are the two shape choices that
   get loud suddenly.** `new` - `[G]` `docs/EaganMatrixUserGuide.txt:4452-4454`, verbatim:
   "Warning: Because using Ramp Up shapes applied to amplitude functions as you can increase to a
   very high value suddenly. Always turn down your gain when experimenting with ramp shapes. The
   same can be said when applying sample and hold to noise as that can also create some very loud
   sounds."
11. **Negative control: a macro or mod-wheel formula on a level column is fine.** `known` - `[D]`
   `RECIPES.md:25 (moved)`, 2026-10-25, fw 10.81, verbatim: "Macro / mod wheel formulas on level
   columns (osc -> filter input) or filter cutoff | fine | high". This is the counterweight to
   section 5: the osc F restriction is about frequency columns, and generalising it to "keep macros
   out of the matrix" would be a false rule. Level, filter-cutoff and FM-depth cells are the right
   home for a macro.
12. **A resonator's Master level should be a constant, not a continuous `Z`.** `known` - `[D]`
   `RECIPES.md:126`, 2026-10-25, fw 10.81: "`Bank A -> Master SL/SR` = constant level (no
   continuous Z, so no level drop on release)." A ringing resonator whose output level tracks
   pressure fades as the finger lifts, which is audible as the tail being cut off. Note the tension
   with N1 and N3 and resolve it the way the tested recipe does: a small constant, well under
   unity.

---

## 2. Before leaving a column blank

Blank is not neutral, and it is not neutral in two different ways depending on whether the module
has a Properties panel. Items 13 and 14 are the mechanism; everything after is where it bites.

13. **Half one of the mechanism: a module with a Properties panel reads the matrix value as an
   offset.** `new` - `[G]` `docs/EaganMatrix Preset Cookbook.txt:1520-1521`, verbatim: "The values
   set in the Matrix for each property column get added as offsets to the values set in the
   Properties display panel." Stated again on the `Earthquake` page `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:5341-5349`. So for BiqBank, SineBank and Kinetic a blank
   column means "no offset" - the panel value, which is usually not zero.
14. **Half two: a module without a panel reads blank as the column's own zero, and zero means
   something different in every column.** `new` - BiqGraph, BiqMouth, WaveBank, SineSpray, HarMan,
   ModMan, Additive and the four delays have no panel `[I]`; the inference is from the card set,
   where only the three panel modules document a Properties display. The question to ask before
   blanking anything is therefore not "is blank safe" but "what is *this* column's neutral value".
15. **`sF`, `sB` and `S` are the three letters whose neutral value flips between modules.** `new` -
   the same letter, the opposite convention, each row `[G]` except where marked:

| Column | Neutral | Citation |
|---|---|---|
| BiqBank `sF`, BiqMouth `sF` | `1` - harmonic / normal spacing; `0` collapses the spread | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1526-1527`, `:1705-1706` |
| Additive `sF` | `0` - normal spacing, the opposite convention | `[G]` `docs/EaganMatrix Preset Cookbook.txt:2238-2239` |
| BiqBank `sB` | `0` - every mode gets the same bandwidth, and it is genuinely neutral | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1534` |
| BiqMouth `sB` | not `0` - see item 19; the factory writes `0.5` and the guide's unity is `1.0` | `[D]` `RECIPES.md:162`, 2026-10-25, fw 10.81 |
| HarMan `S` | `1` - a blank dilation column is a zero step rate, not "no change" | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1842-1844` |
| Additive `S` | `0` - again the opposite convention | `[G]` `docs/EaganMatrix Preset Cookbook.txt:2284-2285` |
| ModMan `S` | `1` | `[G]` `eagan_mcp/knowledge/modules/modman.md` trap 1 |

16. **Blank-safe, measured against the factory corpus.** `new` - `[C]` WaveBank is blank-safe
   throughout; all four delays are blank-safe (VoiceDelay `H` occupied in 0 of 110 slots,
   SummedDelay's in 1 of 87); SineBank `B` is blank-safe; BiqMouth `oF` is blank in 10 of 36 slots
   and `C` and `sA` in 30 of 36; a CVC blank column is simply an unused output (columns 5-8
   occupied in 1 of 15 slots). Source:
   `analysis/findings/corpus-blank-columns.md` sections 3.3, 3.4, 3.13, 3.14, 3.15, 3.18. **The
   knowledge base must not warn about these**, or the real warnings stop being read.
17. **Blanking WaveBank `F2`..`F5` is the documented way to use fewer waves.** `new` - `[G]`
   `docs/EaganMatrixUserGuide.txt:3243`: "If a column is left blank, fewer waves will be
   generated by the WaveBank." `[C]` 47 of 98 WaveBank slots do exactly that
   (`analysis/findings/corpus-blank-columns.md` section 3.13). Blank here is a feature.
18. **The columns the factory never leaves blank.** `new` - `[C]` BiqMouth `Sh`, `sF` and `sB` are
   occupied in 36 of 36 BiqMouth slots; BiqGraph `B` in 41 of 41; HarMan `A`, `F` and `H` in 120 of
   120; Kinetic `F` in 77 of 77
   (`analysis/findings/corpus-blank-columns.md` sections 3.1, 3.5, 3.9, 3.17). A column that 100%
   of the factory writes is a column you must write.
19. **BiqMouth `sB` blank is the flagship trap.** `known` - `[D]` `RECIPES.md:162`, 2026-10-25,
   fw 10.81: "NEVER leave sB empty: blank = 0 = razor-thin formants. They ring as fixed pitches
   that do not follow the keys and no vowel is heard (tested)." Write `0.5` to match the factory;
   the module's own unity is `1.0`. Both sides stand - the guide describes the multiplier's unity
   point and `0.5` is a voicing choice. Card: `modules/biqmouth.md` traps 1 and 2.
20. **BiqGraph blank `B` is a bandwidth 100 dB down, i.e. near-infinite resonance.** `new` - the
   strongest single corpus result and a loudness hazard as well as a blank-column one `[G]`
   `eagan_mcp/knowledge/modules/biqgraph.md` trap 1. Aim `B` at 0.5 to 0.7.
21. **On an oscillator slot, blank `F` is a mode switch and blank Ladder `B` is maximum
   resonance.** `new` - a DSF oscillator with blank `F` and audio in behaves as a different object,
   and the Ladder's `B` runs 0..1 with 0 as maximum resonance `[G]`
   `eagan_mcp/knowledge/modules/oscillator-slots.md` traps 1 and 3.
22. **Three amplitude columns are silent-on-blank, and the silence is deliberate.** `new` -
   WaveBank `A`, SineSpray `A` and HarMan `A` at 0 generate nothing at all, "to save processing" /
   "to conserve processing" `[G]` `docs/EaganMatrix Preset Cookbook.txt:1753-1754`, `:1793-1794`,
   `:1829-1830`. A module that makes no sound and has a blank `A` is not broken, it is switched
   off.
23. **ModMan has no amplitude column at all.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:1908-1911`, verbatim: "The ModMan does not have a
   statically controllable Amplitude like the HarMan. It is excited by an external audio signal."
   Nothing written on the module itself will make a silent ModMan sound; the fault is always its
   excitation input.
24. **The Signal Multiplier needs both inputs or there is no sound.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:871`, verbatim: "You must supply inputs to both columns or
   there will be no sound." One blank input is silence, not pass-through.
25. **Kinetic: `F` is the one column never to blank, and two zeros silently disable features.**
   `new` - zero stiction kills bowing although the bow column is fully written, and a zero spring
   constant disables the spring and the anchor position together `[G]`
   `eagan_mcp/knowledge/modules/kinetic.md` traps 1 and 4. `[C]` 71% of Kinetic presets are not
   bowed and correctly leave `B` and the stiction column blank
   (`analysis/findings/corpus-blank-columns.md` section 3.17).
26. **The inverse trap: on a delay, a *non-blank* `H` is the hazard.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:1488`: `H > 0` "stops data recording" in the delay. Blank
   is the normal recording state; writing a value here silently freezes the buffer, and saving a
   preset with `H` active breaks it on reload when a Manipulator reads that buffer
   (`modules/voicedelay.md` trap 4, `modules/summeddelay.md` trap 6).
27. **Do not over-apply the rule - some blanks are documented and deliberate.** `known` - Additive's
   modulation input column is explicitly safe: "To disable all modulation (pure sine-wave additive
   synthesis) set to 0 or leave the column blank" `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:2256-2257`, and Additive `N` behaves the same way. An
   oscillator's `S` left blank is a pure sine and is the **cheapest** option, because it is the
   optimised path `[D]` `RECIPES.md:70`, 2026-10-25, fw 10.81: "Leaving S blank (no formula) is the
   cheapest: pure sine, optimized."

---

## 3. Before assigning banks

**First look at what you inherited.** There is no init preset: the edit slot holds whatever
was last loaded, and building "from scratch" means building on top of it. `[D]` 2026-10-28.
A patch built this way hit three problems at once, none of them documented: the inherited
voice had **letters A..M already taken**, leaving only N..V of the preferred pool (and the
dump omits all-zero formulas, so `get_matrix` under-reports which letters are free - park a
candidate on a scratch cell and read it back instead); two banks were still assigned and
burning DSP with nothing routed to the output; and the preset NAME stays until you change
it, so the panel keeps showing the old patch's name. Clear the audio path first, then the
bank chain, then the orphaned parameter cells - and remember that removing a formula from
the matrix deletes it on save, so disable rather than clear anything you may want back.
Loading an empty user slot is the closest thing to a blank slate.

Bank assignment is the one structural decision that cannot be fixed later by editing a formula.
Items 28 to 30 are a single hard constraint with three consequences.

28. **There is one delay memory, and six modules share it.** `new` - `[G]`
   `docs/EaganMatrixUserGuide.txt:4156-4157`, verbatim: "VoiceDelay, SummedDelay, MicroDelay, and
   FormulaDelay are four different ways to use the one underlying delay memory. This delay memory
   is also used by the WaveBank, HarMan, and ModMan." A WaveBank and a long Bank C delay are
   competing for the same bytes, not coexisting.
29. **A spectral set takes half that memory, so a delay beside a Manipulator runs short.** `new` -
   `[G]` `docs/EaganMatrix Preset Cookbook.txt:1871-1875`, verbatim: "Note: When you select a
   Spectral Set, it occupies half the memory of the VoiceDelay, SummedDelay, MicroDelay, and
   FormulaDelay. If you have one Manipulator with Spectral Set (in Bank A or Bank B), you can also
   have a VoiceDelay, SummedDelay, MicroDelay, and FormulaDelay in Bank C (which will operate using
   half its normal memory)." The delay times silently halve; nothing reports it.
30. **Two Manipulators plus a Bank C delay force both Manipulators onto the same spectral set.**
   `new` - `[G]` `docs/EaganMatrixUserGuide.txt:3491-3493`, verbatim: "If you have two Manipulators
   (both Bank A and Bank B) as well as a Delay in Bank C, both Manipulators must specify the same
   Spectral Set." A request for two different granular textures plus a delay is not satisfiable;
   drop one of the three.
31. **Which module may sit in which bank.** `new` - `[G]` for every rule but the last:

| Rule | Citation |
|---|---|
| CVC cannot go in Bank A, and the tool's refusal is correct | `[G]` `eagan_mcp/knowledge/modules/cvc.md` trap 1 |
| Kinetic is Bank A or B only - the header lists no Bank C value | `[G]` `docs/HakenMidi.h:1565` |
| ModMan is Bank A or B only, same reason | `[G]` `eagan_mcp/knowledge/modules/modman.md` trap 3 |
| WaveBank may go in Bank C only if no delay is used | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1742-1743` |
| SineSpray / HarMan / ModMan may go in Bank C if Bank B is used for another purpose | `[G]` `docs/EaganMatrix Preset Cookbook.txt:1791`, `:1876` |
| A Bank C SineSpray is an alias of Bank B's, not an independent third one | `[G]` `eagan_mcp/knowledge/modules/sinespray.md` trap 6 |
| CVC may go in Bank B or Bank C if Bank B is not already the CVC | `[G]` `docs/EaganMatrix Preset Cookbook.txt:2487-2490` |
| Bank C values 0-3 are the four delays | `[D]` `CLAUDE.md:14`, 2026-10-25, fw 10.81 |

32. **Two modules are computationally expensive and have cheap substitutes.** `known` - `[D]`
   `RECIPES.md:46 (moved)`, 2026-10-25, fw 10.81: "Computationally intensive per the guide: Ladder
   Low Pass (both variants), PWM Oscillator." Substitute a plain Low Pass Filter for the Ladder and
   a DSF for the PWM when the budget is tight. The Ladder additionally cannot be cascaded `[D]`
   `RECIPES.md:84`.
33. **A Kinetic is normally one bank, not two.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:2391`, verbatim: "it typically is used in either one or
   the other due its processing requirements." Two Kinetic banks is a budget decision, not a free
   one.
34. **Recirculator `Extended` doubles the buffer at the cost of resources.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:1021`, which describes it as basically doubling the buffer
   "at expense of limiting resources". Choose it deliberately, not as a default.
35. **An Additive bank caps polyphony, and the cap for this Module is undocumented.** `new` - the
   guide names 2 for C1x/L1x, 4 for 2x DSP instruments and 12 for L6x/LX8, and the EaganMatrix
   Module is not among the named systems `[G]`
   `eagan_mcp/knowledge/modules/additive.md` section 6 and trap 9. Treat the cap as unknown and
   check `get_status` rather than promising a voice count.

---

## 4. Before adding an SG

36. **A Continuous or Single Cycle SG with a blank `T` column never starts.** `known` - `[D]`
   `RECIPES.md:28-32`, 2026-10-25, fw 10.81: "An SG does nothing until its T column goes positive
   ... Tested 2026-10-25: forgetting T was the reason a pitch LFO was silent." This is the single
   most common reason a modulation that looks correct in the matrix does nothing.
37. **The literature never states the prohibition, which is why a guides-only agent omits the
   trigger.** `new` - the Cookbook shows only the two trigger *choices* and never says what happens
   with neither `[G]` `docs/EaganMatrix Preset Cookbook.txt:212`. This is a documentation gap, not
   a conflict (`analysis/findings/cookbook-techniques.md` section 2.2).
38. **The two trigger choices, and what each means.** `new` - a constant `1` sets the SG always on;
   `W` gates it from the fingerboard or the W input `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:212`, and with the Gated option "when fingerboard pressed,
   W value will be generated as long as you press" `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:249-252`. An LFO that should free-run wants `1`; an
   envelope wants `W`.
39. **Negative control: one shared SG driving several columns is fine.** `known` - `[D]`
   `RECIPES.md:19 (moved)`, 2026-10-25, fw 10.81, verbatim: "One continuous SG shared by several
   osc F columns (same formula) | fine | high". It is several
   *separate* continuous SGs that make the panel unusable, not the fact of modulating several
   columns. See item 42's table row and item 43's remedy; the distinction is the whole point of
   section 5.
40. **The SG shape is a property of the formula, not of the SG.** `known` - `[D]` `CLAUDE.md:110-112`,
   2026-10-25, fw 10.81: shape is formula id 50 (0 Ramp Up, 1 Ramp Down, 2 Pulse, ... 11 Sine), and
   "Same id 50 = buffer select when W mode is FormulaDelay". Two cells sharing a formula letter
   share its shape; changing one changes both.
41. **There is no ADSR, and release is the part you cannot write.** `known` - release is
   persistence, formula id 63, which `eagan_mcp/formula.py` decodes and no typed tool writes `[I]`;
   the inference is from the tool surface. The five documented substitutes and which two are
   reachable today are in `patterns.md` section 2.5, "What substitutes for an ADSR" - build the
   tail out of a second slow ramp-down SG from the start rather than expecting to add it later.

---

## 5. Before adding anything to an osc F column

The project's own hardest-won section. Found 2026-10-25 while building "Saw Swarm Warm" (user slot
3), by removing one construction at a time and testing fast macro-knob turns after each step.
Symptom: panel macro knobs lose clicks on fast turns, plus pops/clicks/late notes. Factory presets
do not show it.

42. **The construction table, as tested.** `known` - `[D]` `RECIPES.md:16-26 (moved)`, 2026-10-25,
   fw 10.81. The three `fine` rows are **negative controls** and carry as much weight as the
   failures: without them, "always write every column" and "never put anything on an F column"
   become false rules.

| Construction | Effect | Confidence |
|---|---|---|
| Several continuous SGs, each on a different osc F column (e.g. 3 drift LFOs) | knobs unusable | high `[D]` |
| One continuous SG shared by several osc F columns (same formula) | fine | high `[D]` |
| Direct x (multiply row) formula on an osc F column | slightly sluggish knob | high `[D]` |
| User formula with an X component on an osc F column (cents detune) | slightly sluggish knob | high `[D]` |
| W x Macro formula on an osc F column | pops, late notes | medium (was confounded by the LFOs) `[D]` |
| Plain decimal constants on osc F (e.g. `.004`) | fine | high `[D]` |
| FM via an audio row into osc F, formula SG x Y ("FM Wheel Vibrato", user slot 7) | fine (fast macro turns OK) | high `[D]` |
| Macro / mod wheel formulas on level columns (osc -> filter input) or filter cutoff | fine | high `[D]` |
| Pitch bend on delay-based strings (VoiceDelay Karplus loop, factory "MicroDelay WaveGuide v1") | held/ringing note does NOT bend; live delay-time changes ignored | high ("Sitar Modal Pluck", slot 4) `[D]` |

43. **Rule 1, with its remedy.** `known` - `[D]` `RECIPES.md:29-30 (moved)`, 2026-10-25, fw 10.81:
   "One shared drift/vibrato LFO, not one per oscillator. For opposite movement, put the same
   formula on Direct + for one oscillator and Direct - for another." The remedy is the half a naive
   merge loses: it is what makes the rule usable rather than merely prohibitive.
44. **Rule 2, with its remedy.** `known` - `[D]` `RECIPES.md:31-32 (moved)`, 2026-10-25, fw 10.81:
   "Keep macros off oscillator F columns. A 'detune width' macro: keep the detune fixed and put the
   macro on the level of the detuned oscillators (like a supersaw mix knob)." The user still gets a
   detune-width knob; it is wired somewhere else.
45. **Rule 3.** `known` - `[D]` `RECIPES.md:33 (moved)`, 2026-10-25, fw 10.81: "Avoid Direct x on
   oscillator F columns if the panel must stay responsive." `Direct x` is the column's multiply row
   and is fine elsewhere; `RECIPES.md` keeps the semantics with the recipe that uses it.
46. **Rule 4 - and tell the user the trade-off instead of deciding for them.** `known` - `[D]`
   `RECIPES.md:34-35 (moved)`, 2026-10-25, fw 10.81: "Pitch-proportional detune costs a little knob
   responsiveness; fixed-Hz detune is free. Tell the user the trade-off and let them choose."
   Fixed-Hz detune varies in cents across the keyboard, which is the price of the free option.
47. **The cause is total DSP load, not the constructions as such.** `known` - `[D]`
   `RECIPES.md:50-51 (moved)`, 2026-10-25, fw 10.81: "The construction table above is still useful:
   those constructions cost DSP. The cause is the total load, not the constructions as such."
   Corroborated from the other side: FM via an audio row into osc F does **not** cause knob lag, so
   the pitfall is specific to Direct-row constructions `[D]` `CLAUDE.md:141-142`, 2026-10-25,
   fw 10.81. This is a working hypothesis about the cause, not something Haken has confirmed.
48. **The debugging method that found all of it.** `known` - `[D]` `RECIPES.md:53-54 (moved)`,
   2026-10-25, fw 10.81: "Debugging method that worked: remove one construction at a time; after
   each step the user tests VERY fast knob turns ('quick' and 'very quick' gave different
   answers)." Use the same method for any new responsiveness complaint: one change, then one yes/no
   question, and ask for *very* fast turns specifically.

---

## 6. Before building a string

49. **A delay-based string does not follow pitch bend on a ringing note.** `known` - `[D]`
   `RECIPES.md:26 (moved)`, 2026-10-25, fw 10.81: a held/ringing note does NOT bend and live
   delay-time changes are ignored, tested on a VoiceDelay Karplus loop and on factory "MicroDelay
   WaveGuide v1". It is not known whether the delay time is latched at note-on or not modulatable
   at all. Cards: `modules/voicedelay.md` trap 1, `modules/summeddelay.md` trap 3,
   `modules/microdelay.md` trap 1.
50. **The remedy: a bendable string is a tuned resonator bank, not a delay loop.** `known` - `[D]`
   `RECIPES.md:36-37 (moved)` and `RECIPES.md:103-106`, 2026-10-25, fw 10.81: "Strings that must
   bend: build them as a tuned resonator bank (BiqBank), not a delay loop." BiqBank modes are
   filters and follow `X` live, so bends work, also after release. The wiring and the column map
   are in `RECIPES.md`, "Strings and plucks", and in `modules/biqbank.md` trap 9.
51. **A resonator needs far less input than a delay loop.** `known` - `[D]` `RECIPES.md:123-125`,
   2026-10-25, fw 10.81: 0.05 into a BiqBank against 0.2 into a delay loop. Carrying a delay-loop
   excitation level over to a resonator is both too loud and, per N2, the explosive direction.
52. **A fixed-length excitation burst pumps high notes far more than low ones.** `known` - `[D]`
   `RECIPES.md:136-142`, 2026-10-25, fw 10.81: energy builds up per period, so make the burst a
   fixed number of *periods* - `W x (X + Y + Z)` on the SG `F` column with `X` as the pitch. Note
   that `X` on an SG `F` column is fine; the osc F pitfall of section 5 does not apply there. Card:
   `modules/biqbank.md` trap 10.
53. **Bend range is a preset setting, it is not readable back, and the default is unusable from a
   keyboard.** `known` - `[D]` `RECIPES.md:144-151`, 2026-10-25, fw 10.81: `set_bend_range(2)`
   writes "96:2", it is saved with the preset, and verification needs a `listen` (+-2 st shows as
   about +-170 of 8192). `[I]` A preset left at the default 96 gives a channel-1 wheel +-96
   semitones, an unusable +-8 octaves; the inference is from the guide's own `96:N` rule applied to
   `N = 96`, and any keyboard patch must therefore set `96:N` explicitly
   (`analysis/findings/voicemodel-keyboard.md:240-243`).

---

## 7. After every structural change

54. **Check the budget, every time.** `known` - `[D]` `RECIPES.md:47 (moved)`, 2026-10-25,
   fw 10.81: "Check with get_status (dsp_usage_percent, dsp_polyphony) after every big change."
   `get_status` reads DSP usage from cc114 and the actual DSP polyphony from cc72.
55. **The Module runs fewer voices than the base polyphony when the patch is too heavy.** `known` -
   `[D]` `RECIPES.md:44-45 (moved)`, 2026-10-25, fw 10.81: "The Module also runs fewer voices than
   the base polyphony when the patch is too heavy." and "'Saw Swarm Warm' showed DSP Usage 100% and
   ran only 3 voices on 10.81." A polyphony number in the setup is a request, not a guarantee.
56. **The guide's own rule: reduce by one and keep the "+".** `known` - guide section 8.5 is
   headed "Reduce Polyphony": heavy patches exceed the DSP budget, and excessive polyphony
   turns the sound off until it is reduced.
   `[G]`
   `docs/EaganMatrixUserGuide.txt:6578-6583`, verbatim: "This automatic detection may not catch
   borderline situations. If you notice sluggish behavior - such as sluggish response to pedal
   changes as you play - try reducing the polyphony by 1 or try simplifying your design. Keep the
   '+' expanded polyphony if it is there to start (that is if Polyphony 8+ is asked to be reduced,
   reduce it to 7+, not 7)." Polyphony is `s_Mat_Poke` id 39, with `+` as id 11 `[D]`
   `CLAUDE.md:12`, 2026-10-25, fw 10.81.
57. **The fix order, as tested on this project's own patch.** `known` - `[D]`
   `RECIPES.md:48-49 (moved)`, 2026-10-25, fw 10.81: "Fixes, in order: drop a heavy module (Ladder
   -> Low Pass Filter, PWM -> DSF), lower base polyphony by 1 (keep '+'), simplify formulas on osc
   F columns." Work down the list; do not reach for item 58.
58. **Never turn Double Computation Rate on as a performance fix.** `known` - `[D]`
   `CLAUDE.md:153-154`, 2026-10-25, fw 10.81, against `[G]`
   `docs/EaganMatrixUserGuide.txt:6636-6639`, both standing in the block below. It is a
   frequency-response setting. Check it **first** when diagnosing low polyphony; the Polyphony
   display shows a caret for a preset that uses it.

```
CONFLICT: Double Computation Rate - a fix for break-up, or a cause of it?
  device [D]: "'Saw Swarm Warm' (slot 3) re-saved: base polyphony 6, '+' on, Double
              Computation Rate off. Double rate was the cause of 3 voices + 100% DSP;
              user confirmed no lag after the change."
              - CLAUDE.md:153-154, 2026-10-25, fw 10.81
  docs   [G]: "Another reason you may want to use 'Double Computation Rate' is if you are
              working on a complex preset and it starts breaking up. In that case you can
              try reducing polyphony (which is also reduce DSP usage) or try Double
              Computation Rate if a simply Polyphony reduction does not fix the problem."
              - docs/EaganMatrixUserGuide.txt:6636-6639
  docs   [G]: "will decrease your Polyphony/DSP resources by half"
              - docs/EaganMatrixUserGuide.txt:6613-6615
  follows: both stand, because they are about different symptoms. The guide's offer is
           conditional and secondary - it applies only after a polyphony reduction has
           failed, and the feature's stated purpose is frequency response, reaching 20 kHz
           instead of 14-18 kHz. The device finding is about the DSP budget. The rule that
           satisfies both: a frequency-response setting, never a performance fix; turn it
           on only for missing high harmonics measured on a scope, and expect half the
           voices. A device A/B test on a breaking-up patch is still open.
```

59. **The factory is as sparing with it as this project is.** `new` - `[C]` Double Computation Rate
   is set explicitly in **41 of 668** presets (6.1%), with base polyphony distributed
   `{1: 4, 2: 16, 3: 11, 4: 6, 5: 1, 8: 1, absent: 2}`
   (`eagan_mcp/knowledge/census.json`, `double_computation_rate`; `explicit_true` 41,
   `absent_so_default` 627). Also in `patterns.md` section 2.3. A corpus statistic can never
   upgrade to a device finding, but it does say the house style agrees.

---

## 8. Before saving

60. **A formula removed from the matrix is deleted on save.** `new` - `[G]`
   `docs/EaganMatrixUserGuide.txt:6116-6119`, verbatim: "Remember to save your work often. If you
   save a preset with formulas that you have removed from the matrix, they will be lost on saving
   even if they are defined on the right-hand side formula list."
61. **The remedy: disable, never clear.** `new` - `[G]`
   `docs/EaganMatrixUserGuide.txt:6119-6121`, verbatim: "To retain a formula, you have created but
   are not using in the matrix, place it on a matrix point that is not being used that is not
   affecting an output and disable it. These formulas will be retained on saving." And `[G]`
   `docs/EaganMatrixUserGuide.txt:6181-6182`, verbatim: "Disabled formulas are retained when a
   formula is saved."
62. **The device face of the same mechanism.** `known` - `[D]` `CLAUDE.md:94-95`, 2026-10-25,
   fw 10.81: "The Module omits matrix cells whose formula is all zero from the matrix dump." A
   formula's existence is tied to a live matrix cell, which is why `get_matrix` under-reports which
   of the 44 shared letters are in use and why `set_matrix_point` falls back to reading the cell's
   formula number. Never clear a cell whose formula you intend to re-use.
63. **Save before switching presets, and never verify a store by loading the slot.** `known` - the
   literature's version is "Always save your preset before going to another preset if you are in
   the middle of creating it" `[G]` `docs/EaganMatrix Preset Cookbook.txt:545-546`. The project's
   harder version is `[D]` `CLAUDE.md:129-130`, 2026-10-25, fw 10.81: "LESSON: do not verify a store
   by loading the slot before the list shows the name there; loading replaces the unsaved edit
   slot." Verify with the read-only `list_user_presets` instead - the save echo varies between
   saves.
64. **Writes go to the edit slot only.** `known` - `[D]` `CLAUDE.md:32`, 2026-10-25, fw 10.81:
   "Writes go to the edit slot only, unless the user explicitly confirms." A tool that stores
   without an explicit confirmation is a defect, not a convenience.
65. **Never the system-slot store path.** `known` - `[D]` `CLAUDE.md:125-126`, 2026-10-25, fw 10.81:
   "NEVER cc0=127: that is the SYSTEM slot path (factory updates)." A user store is `ch16 cc0=0`
   plus `cc32`/`cc112`. The header restricts `ccBankH 127` to Update File 2 `[G]`
   `docs/HakenMidi.h`, `ccBankH` - the two agree. The literature does not describe the store
   protocol at all, so there is no doc-level warning to find.
66. **Do not pass `set_preset_name`'s `description` argument.** `known` - stream 1 is unresolved:
   the device note calls it the description and the header plus the corpus read it as the panel
   macro labels, so writing it may destroy a preset's macro labels `[I]`; the inference is that an
   unresolved identity on a destructive write is a reason not to write. Name only, until stream 1
   is settled. Stated with its reasoning in `model.md` section 11.

---

## 9. While debugging

**Before you distrust a reading, know how a read works.** `[D]` 2026-10-27, fw 10.81. On
10.81 selecting a cell does NOT make the Module dump its state - it returns an echo and
nothing else. The trigger is `ccMatOp 124` (matRefresh), and the sequence that works is
**state change -> matRefresh -> listen**. `get_matrix` and `get_setup` do this for you. Two
consequences when a read looks wrong: a refresh with no intervening state change returns
almost nothing, so an "empty" read often means "nothing has changed", not "the patch is
empty"; and one listen window can catch two dumps, so a cell can arrive twice (the decoder
de-duplicates, keeping the later value). Also `get_status`' `dsp_polyphony` is ALWAYS null -
cc72 arrives after a matRefresh, not after a plain ping - and its `dsp_usage_percent` is
allocated DSP, not instantaneous load, so it does not move when you hold a note.

67. **Turn Formula Display off before judging anything.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:2558-2565`, verbatim: "The most useful tool for debugging
   is the Formula Display on right hand of Matrix. This should be turned off when not debugging as
   certain functions do not work if this is on (Touch Area). When Formula Display is on, the Touch
   area will not be active. Also, when on, only DSP1 processing will be used for certain operations
   like Voice Number ('VNum') processing. The maximum number of internal synth (not Midi) voices
   generated will be 8 if formula display is on as expanded polyphony is not considered (DSP1 can
   process up to 8 voices). For this reason, always turn Formula Display off for performance."
   Anything VNum-based, or above 8 voices, behaves differently while you are looking at it.
68. **"Why is my pitch stepping" has two causes, and the Editor shows only one.** `new` - `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:1350-1352`, verbatim: "If you are playing a preset and it
   does not appear to have rounding on in the editor and yet it is quantized, check formulas with X
   that may have set programmed Quantization." Check the global Round Rate *and* every `X`
   formula's `Q` setting.
69. **A resonator that gets brighter and shorter when driven hard is deflation, not a bug.** `new` -
   `[G]` `docs/EaganMatrix Preset Cookbook.txt:1513-1516`: if internal state values exceed the
   deflation limit "the EaganMatrix will automatically increase the bandwidth on the biquad". The
   limit is also a sound parameter: `[G]` `docs/EaganMatrix Preset Cookbook.txt:1928-1930` says to
   set a ModMan's "Deflation Limit to the largest value (between 0 and 7) that does not affect the
   timbre of the sound", so a low limit audibly changes the timbre.
70. **Reading the matrix does not tell you what a Properties-panel module sounds like.** `new` -
   two modules whose matrix columns look identical can sound different, because the matrix values
   are offsets to per-bank panels and each bank has its own `[G]`
   `docs/EaganMatrix Preset Cookbook.txt:5341-5349`, `:1520-1521`. `[I]` The consequence for the
   MCP is that `get_matrix` is not enough; the inference is that `get_setup` (stream 20) and the
   bank-property pokes carry the rest, and the bank-property streams have no codec at all
   (`model.md` section 8).
71. **A matrix cell cannot hold "1.25", and the display shortens what it can hold.** `new` - `[G]`
   `docs/EaganMatrixUserGuide.txt:6144`: "Note: Constants containing whole and fractional parts"
   are not allowed - they must be formula constants or built from several `Direct +` entries. And
   `[G]` `docs/EaganMatrixUserGuide.txt:6198-6200`, verbatim: "Four-digit constants will be
   displayed in a shortened form within the matrix, due to display space constraints. Only the
   first digit followed by a + will be displayed. For example, '.562' and '.5623' will show '5+'."
   The MCP reads the wire and is immune, but a user reporting "it says 5+" is reporting four
   digits, not one.
72. **A silent preset may be routed away from the internal sound engine.** `new` - surface routing
   and MIDI-In routing are separate bitfields on `ch16 cc36`, bits 0-2 for the surface and bits 3-5
   for MIDI In `[G]` `docs/ContinuumUserGuide.txt:8292-8300`. A preset can therefore send MIDI In
   anywhere but the engine, which looks exactly like a broken patch
   (`analysis/findings/voicemodel-controllers.md:443-445`).
73. **Heights already saved on the device are still wrong, and no code change repairs them.**
   `known` - the formula sign-encoding fix repairs what is written from now on; it does **not**
   repair heights already stored in user slots `[I]`, the inference being that a stored preset
   holds the raw wire value. `[D]` `CLAUDE.md:163`, 2026-10-25, fw 10.81 records "Harkonnen Voice"
   (user slot 5) with a negative height, and `CLAUDE.md:168-169` records "Sitar Modal Pluck" (user
   slot 4). Both must be **rewritten on the device** in a session with the Module before either
   preset is trusted; that session is out of scope here. Also in `model.md` section 11.

---

## 10. Controller scope

Most of the literature is written for the Continuum. A trap that applies only to an Osmose, a
Warbl, a Micro or a Continuum is **not** an EaganMatrix Module trap, and promoting one to a Module
fact is how a knowledge base starts lying. The qualifiers below are part of each claim.

74. **The scope table - the qualifier is part of the trap.** `new` - every row `[G]`:

| Trap | Scope | Citation |
|---|---|---|
| The Touch Area is not supported on the EaganMatrix Module or the ContinuuMini | `(not a Module feature at all)` | `[G]` `docs/EaganMatrix Preset Cookbook.txt:665` |
| Touch Area formulas rely on Continuum-only Ancillary sources | `(continuum)` | `[G]` `docs/EaganMatrix Preset Cookbook.txt:490-492`, `:665-703` |
| Combination Preset Programming is Continuum only and needs AES/SPDIF I/O | `(continuum)` | `[G]` `docs/EaganMatrix Preset Cookbook.txt:801-805`, `:824-828` |
| `Y` does not return to zero on lifting the finger, so a Y-scaled output keeps sounding | `(continuum)` | `[G]` `docs/EaganMatrix Preset Cookbook.txt:2676-2690` |
| `Y` is 0 until the Aftertouch area, where `Z` also maxes out | `(osmose)` | `[G]` `docs/EaganMatrixUserGuide.txt:6902-6916`, `docs/EaganMatrix Preset Cookbook.txt:2611-2620` |
| Runs 10.09 DSP firmware - "DO NOT TRY AND LOAD 10.4X CONTINUUM PRESETS ON OSMOSE" | `(osmose)` | `[G]` `docs/EaganMatrixUserGuide.txt:6845-6850` |
| Changing presets on the instrument while editing loses the edit | `(osmose)` | `[G]` `docs/EaganMatrixUserGuide.txt:6860-6866` |
| Cannot process audio input; the `Processor` preset category is empty | `(mini)` | `[G]` `docs/EaganMatrix Preset Cookbook.txt:616-618`, `:755-757` |
| No attenuation rotary, so a runaway is harder to kill | `(micro, mini)` | `[G]` `docs/EaganMatrixUserGuide.txt:8453-8454` |
| 2X DSP, 8 max voices; plays Continuum presets "with 2X DSP polyphony limitations" | `(micro)` | `[G]` `docs/EaganMatrix Micro Cookbook.txt:46-52` |
| Slim / 6x models allocate 6x the DSP, so a 4+ preset becomes 24 DSP | `(continuum)` | `[G]` `docs/EaganMatrixUserGuide.txt:6591-6593` |
| Maps Elevation to CC74/Y, Roll to CC16 and Yaw to CC17, colliding with macros v and vi | `(warbl)` | `[G]` `docs/EaganMatrix Preset Cookbook.txt:2369-2371`, `docs/EaganMatrixUserGuide.txt:7680-7688` |

75. **The project's own controller facts, which the literature does not state.** `known` - all
   `[D]`, 2026-10-25, fw 10.81:
   - "Mod wheel: CC 1 arrives as Y. Build the patch to use Y. Do not suggest remapping the
     user's keyboard as the default fix." `RECIPES.md:38-39 (moved)`.
   - Macros i..iv are ch1 CC 12..15. `CLAUDE.md:119`. The header extends the range to vi on cc17
     and those two are untested here (`model.md` section 10).
   - **Panel encoder**: the Module's encoder has **no acceleration, about one value step per
     click**, and **127 clicks for the full range**. `RECIPES.md:56-57 (moved)`. If a few clicks
     should cover a wide range, raise the macro gain - the resolution is in the macro, not in the
     knob.
76. **Windows grabs the USB device exclusively.** `new` - the Editor and this MCP cannot both hold
   the port `[G]` `docs/EaganMatrix Preset Cookbook.txt:2716-2718` and
   `docs/EaganMatrix Micro Cookbook.txt:605`. `[I]` Two consequences follow immediately: the
   Editor's Reduce Gain protection is off while the MCP is connected (item 4), and
   `HAKEN_EDITOR_DIR` is only a path to the reference tree, never a live connection.

---

## Where to go next

- How a voice is computed, the N1-N5 rules in full, and the standing hazards: `model.md`.
- A module's own traps, in its own terms: `modules/index.md`, then the card.
- How to build a thing rather than how it breaks: `patterns.md`.
- Recipes tested by ear, each with the pitfalls that belong to its own steps: `RECIPES.md`.
- `get_recipes` will point here for the pitfalls half once `get_knowledge` exists; until then this
  file is reached through the package path `eagan_mcp/knowledge/pitfalls.md`.
