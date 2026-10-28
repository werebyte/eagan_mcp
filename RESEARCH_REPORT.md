# Research report: how the EaganMatrix is actually programmed

The dated record of one research pass (research 2026-10-26, build 2026-10-27) on the Haken
EaganMatrix Module at firmware 10.81, and of what that pass shipped into this repository.

## 0. What this document is, and is not

Under `.maister/docs/standards/global/conventions.md:10` this file has one fixed role: **one
research pass's findings and their provenance, never a standard**. It is a dated research record.
It is not a plan - `ROADMAP.md` is the plan and its completion tracking. It is not protocol
findings - `CLAUDE.md` carries those. It is not a recipe book - `RECIPES.md` carries recipes tested
by ear, and `eagan_mcp/knowledge/` carries the knowledge base an agent reads before building a
patch. It is not a tool specification - `tools_spec.md` specifies tools that do not exist yet.

It is **cross-referenced from** those documents rather than duplicated into them. Where a fact
here also belongs in one of them, the fact lives there and this file points at it.

Evidence tags are the five defined in `.maister/docs/standards/protocol/protocol-sources.md`:
`[D]` device-verified, `[D-cap]` recorded in `captures/`, `[G]` from the docs with `file:line`,
`[C]` a corpus statistic with its denominator, `[I]` inferred. The resolution order and the rule
that **`[C]` can never upgrade to `[D]`** are stated there and are not restated here.

Repository measurements in this document (line counts, byte sizes, tool and test counts) were
taken on 2026-10-27 with `wc -l`, `ls -l`, `grep -c "@mcp.tool"` and
`.venv/Scripts/python.exe -m pytest`. They are measurements of this repository, not graded claims
about the device, and carry no evidence tag.

**No device test was run in this pass.** Everything below is offline work: the header, the guides,
the 668-preset factory corpus, the 18 existing captures, and reads of this project's own code. The
device test plan in section 4 is therefore entirely unrun, `DT1` included.

## 1. The three label namespaces

Three sequences are in use across this pass's documents, and they are disjoint. A bare "rank n"
is never written.

| Namespace | Meaning | In use | Reserved to |
|---|---|---|---|
| `RF<n>` | a research finding in this document | `RF1`..`RF15` | `RF15` |
| `T<n>` | a tool-gap rank in `tools_spec.md` | `T1`..`T22` | `T22` |
| `DT<n>` | a device-test rank in the merged plan, section 4 | `DT1`..`DT21` | `DT45` |

**Why the findings are `RF`, not a bare letter.** In the code-fix namespace `F1` is the
negative-height offset encoding, `F9` the matrix labelling join and `F14` a prohibition rather than
an edit, and that namespace is used throughout the implementation record. A finding numbered the
same way would be unreadable against that record, so findings carry the `RF` prefix everywhere.

**Why `T` runs to 22 and not 20.** `T1`..`T20` are `tools_spec.md`'s one-for-one restatement of
this pass's ranked recommendations. `T21` (`set_master_column`, the write side of `idMastCol1..6`)
and `T22` (`set_module_option`, a validated write for an arbitrary `s_Mat_Poke` id) **originated in
the build pass, not in the research**: seven module cards and `patterns.md` P17 each named a
capability gap that no research rank covered, cited the finding and flagged it upward rather than
inventing a label. See `tools_spec.md` section 2.

**Why `DT1`..`DT21` are in use while the namespace is reserved to `DT45`.** 79 test blocks were
filed across nine findings files; merging duplicates and striking retired tests leaves about **45
distinct tests**, grouped into **21 ranked rows**. A `DT<n>` is a *row*, so only 21 labels are live;
the namespace is held open to 45 so that splitting a row later does not renumber the others. The
gap between 21 and 45 is this grouping, not a missing twenty-four.

## 2. Deliverable coverage

Fifteen deliverables were specified. This document is D10. The other fourteen and their shipped
state:

| # | Deliverable | Shipped state |
|---|---|---|
| D1 | `eagan_mcp/knowledge/model.md`, the voice model | Shipped. 540 lines, every claim tagged |
| D2 | `eagan_mcp/knowledge/modules/` | Shipped. `index.md` plus 18 module cards |
| D3 | `eagan_mcp/knowledge/patterns.md` | Shipped. 1,106 lines, plus `worked_examples.md` at 696 lines |
| D4 | `eagan_mcp/knowledge/pitfalls.md` | Shipped. 610 lines; standalone pitfalls moved out of `RECIPES.md`, which keeps only those inseparable from a recipe's steps |
| D5 | The trimmed factory catalog and `eagan_mcp/preset_file.py` | Shipped. `preset_file.py` 2,347 lines; `factory_catalog.json` 1,292,509 bytes (1.233 MiB, inside the 1.5 MiB budget) beside `census.json` and `descriptions.json`; the 42-field `factory_catalog_full.json` is regenerable and deliberately not committed. A rebuild is byte-identical on all five artifacts |
| D6 | `eagan_mcp/knowledge/preset_index_1081.json` | Shipped. 45,964 bytes, category -> index -> name, both candidate collations |
| D7 | `tools_spec.md` | Shipped. 826 lines, 22 ranks, with its own label scheme made normative |
| D8 | Three skills | Shipped. `.claude/skills/eagan-patch-design`, `-debug`, `-factory-mining` |
| D9 | `get_knowledge` and `search_factory_presets` | Shipped. `eagan_mcp/server.py` now carries 32 `@mcp.tool()` entries, up from 30 |
| D10 | This document | Shipped. The last group of the pass |
| D11 | The code fixes | Shipped. Specified as ten, raised to twelve, then one more inserted mid-pass: sixteen code-fix changes in all (F1 to F17, of which F14 is a prohibition rather than an edit) |
| D12 | The documentation repair sites | Shipped. About 40 sites across `.maister/docs/`, `CLAUDE.md`, `README.md`, `ROADMAP.md` and `RECIPES.md`; roughly 150 citations were corrected across eleven task groups |
| D13 | The three standards amendments | Shipped. `conventions.md:10` carries the document role split including this file; `protocol-sources.md` adopts the five bracket tags project-wide; `ROADMAP.md:26` splits persistence out as its own item and names `tools_spec.md` `T5` |
| D14 | `LICENSE` | Shipped. MIT, 66 lines, with `license = "MIT"` in `pyproject.toml` |
| D15 | The pytest suite | Shipped. 16 test files, 106 tests, 106 passed and 0 skipped |

Freshly measured counts that supersede every earlier figure in the research material and in the
plan:

| Quantity | Value |
|---|---|
| MCP tools | 32 |
| `eagan_mcp/*.py` | 4,556 lines across 8 non-empty modules |
| Test suite | 106 passed, 0 skipped, 16 files |
| Knowledge documents | 23 markdown files |
| Committed JSON artifacts | 4, totalling 1,965,551 bytes |
| Wheel | 568,100 bytes, 41 entries, carrying all 23 documents and all 4 artifacts |
| Tool docstrings stating a write scope | 13 of 32 |

That last row is the one coverage number that is not good news, and it is recorded rather than
smoothed: 19 of the 32 tool docstrings do not state their write scope, although
`.maister/docs/standards/protocol/device-safety.md` asks for it in the first docstring lines.

## 3. The fifteen findings

Confidence letters are the research's own convergence tiers: **A** three or four independent
sources agree, **B** two independent sources, **C** a single source or an inference, **D**
contested with both sides standing. They are orthogonal to the bracket tags, which grade
individual claims.

### RF1 - the preset file format is cracked, and the gate passed - confidence A

All 668 shipped factory presets decode with zero failures (422 legacy, 246 modern), yielding 17,591
matrix cells and `[C]` 7,259 formulas, with no stray MIDI messages. The decisive evidence is a
paired check: a 9.55-era legacy archive and a 10.81 live dump of the same preset agree on **25 of
25** matrix cells, which can only happen if the legacy ch15 mapping, the 22-code value shift, the
decimal-digit order and the mute bit are all simultaneously right `[D-cap]` (the two paired
captures in `captures/`). One correction must travel with the result: `[G]`
`docs/HakenMidi.h:478-480` says a store writes only the parameters that differ from default,
archives included, so the gate could never have been "file and dump agree on everything" - the live
capture carried 92 setup ids against the file's 5. The applied criterion is that only ids present in
both are compared. The honest caveat is that the **formula** field has no live leg at all, because
`[D]` `CLAUDE.md:95-96` formulas are streamed on cell selection and not on preset load, so no
acceptance capture can contain one; the substitute is a same-corpus differential over 7 non-trivial
legacy/modern twins in which `[C]` 64 of 80 shared formulas normalise identically and all 16
residuals are traced.

### RF2 - the negative-height mirror, the single most important finding - confidence B (strong)

The project's formula codec encoded and decoded **every negative formula height mirrored**, and two
independent methods converged on it. Tracing the 10.44 Editor's slider chain shows transmit as an
offset (`value - 100` above 100, with `< 100` as the flag) and an internal range of 0..227 for
-1.00..1.27, with **no sign test anywhere in the chain** - the machinery sign-and-magnitude would
require is structurally absent. The corpus proves the same thing over `[C]` 14,147 height writes:
a set negative flag takes raw 1..99 in all 1,055 occurrences and raw 100 - the documented floor
under sign-and-magnitude - occurs zero times, while `[C]` 564 formulas set a negative flag with the
height id absent, which is a no-op under sign-and-magnitude and exactly -1.00 under the offset
reading. `[G]` `docs/HakenMidi.h:1201-1202` is silent on the magnitude formula and both readings
satisfy every sentence of it, so this was not a misread specification. The consequence was a 4x
overshoot on every negative height; `[C]` 493 of 668 factory presets set a non-zero negative flag.
The encoding is fixed in this pass, **but it is not device-verified**: `DT1` is unrun, and
`ROADMAP.md` keeps the negative-height device test open. Two saved user presets written under the
old encoding are not repaired by the code fix, which `CLAUDE.md` records.

### RF3 - how a voice is computed - confidence A

A matrix column evaluates as `clip(+/-0.25, sum of Via-Limiter formulas x row) + sum of other
formulas x row`, all multiplied by the formula in the column's Multiply row `[G]`
`docs/EaganMatrixUserGuide.txt:5206-5211`, with `[D]` `RECIPES.md:137-138` stating the multiply-row
half independently and agreeing exactly. Three consequences shape every patch: the clip happens
*before* the unlimited formulas are added, so Via Limiter is a soft-clip stage and not a safety net;
`Direct (x)` multiplies the whole sum rather than contributing a term; and a `Direct +` row has a
constant value of 1, so a formula placed there contributes itself. The device has 17 rows and 61
columns `[G]` `docs/HakenMidi.h:649-730`, of which columns 2-7 are six assignable Master columns.
A hard constraint on any patch-writing tool: a matrix cell takes a whole 1..9 or a decimal only
`[G]` `docs/EaganMatrix Preset Cookbook.txt:206-209`, so "1.22" and "12" are not expressible and
larger or mixed values are composed across the `Direct` rows.

### RF4 - compression has two different answers, and they are consistent - confidence A

Setup-id absence means **default**, not zero `[G]` `docs/HakenMidi.h:478-480`, and because wire
value 0 of each bank and oscillator type id is a real module, this inverts the naive census: an
explicit `BankA/B/C = 0` occurs in `[C]` 0 of 668 files, yet BiqBank credited through wired
defaults rises to 151 users and the DSF Oscillator to 466. Matrix-cell absence is the opposite case
and is **not** compressed: every one of the 668 files opens its matrix block with an explicit clear
`[C]`, so the cells that follow are the complete non-blank set. The two answers are not in tension,
because the matrix is an exception by construction. The working rule is therefore: **column
occupancy is sound evidence, while setup-id absence can never show that a value is zero or that a
module is unused.** The same rule makes "Single Cycle dominates the library" a pure artifact -
Continuous Cycle is value 0 and never appears explicitly.

### RF5 - blank columns follow a two-branch mechanism, not a list - confidence A

Modules with a Properties panel (BiqBank, SineBank, Kinetic) add the matrix column to the panel
value `[G]` `docs/EaganMatrixUserGuide.txt:3789-3792`, so blank means "no offset" - the panel value,
not zero. Modules without one (BiqGraph, BiqMouth, WaveBank, SineSpray, HarMan, ModMan, Additive and
all four delays) take the column's own zero, whose meaning varies per column. `[I]` "Blank is not
neutral" is therefore precisely the case where a non-panel column's zero is not that parameter's
neutral value, or where a panel column's property default is itself zero - two sentences that
predict the whole trap list, predict the safe list and generalise to columns nobody has tested. The
footgun that follows is new and is worth more than the list: three parameter letters **flip their
neutral value between modules**, so carrying a value across is wrong rather than suboptimal. The
decisive artifact is a factory preset that spends a whole formula component on a constant purely to
supply the neutral a blank column would not have supplied.

### RF6 - the plain-MIDI-keyboard contract, and the Z tension - confidence A / B

The whole contract for a plain keyboard is one paragraph `[G]`
`docs/ContinuumUserGuide.txt:5384-5394`: notes on channel 1, channel-1 pitch bend reassigned
globally to every sounding note, **velocity interpreted as an initial one-shot Z**, Y usually from
channel-1 CC 1, up to 8 voices on an EaganMatrix Module, with oldest-note voice stealing. Two
refinements are specific to this device: the Touch Control Area is not supported on the Module,
which removes a whole technique page and leaves only All Fingers Averaged of the one ancillary pair;
and the two jack inputs have no physical jacks here, so they are MIDI-only - two spare continuous
inputs on a rig that has almost no expression. The tension at the centre is Z. `[C]` Z dominates the
factory library - `VEndZ` appears in **2,462** of **7,259** factory formulas against `VEndY` 1,135
and `VEndX` 1,130, and `z_modulation` fires in 602 of 668 presets against 531 and 510 - while on
this rig Z arrives once, at note-on, as velocity. The library's expressive idiom and the user's
controller disagree, and a patch built for one is dead on the other.

### RF7 - there is no ADSR, and the release is unreachable - confidence A

`[G]` `docs/EaganMatrix Preset Cookbook.txt:3069-3072` says plainly that there is no generic ADSR
envelope control and that shape-generator-driven filter control is used to create most envelope
actions. The factory `Analog ADSR` preset builds attack from a shape generator's ramp time, decay
from the **persistence** of that ramp, sustain from holding the note, and release from persistence
on the output columns. Persistence is `s_Form_Poke` id 63, one of the ids no tool writes, so `[I]`
an agent can build an envelope's attack and shape today and cannot build its release, except
through a second slow ramp-down generator on the output or the Recirculator tail. Interpolation
compounds it: that id is the only formula parameter with a documented non-zero default, the guide
says zero produces noise or aliasing, and the project's standard workflow builds a formula from an
unused letter and never writes it.

### RF8 - what the MCP cannot reach, quantified - confidence A

Four independent surveys converged on the same shape. Of the 92 `s_Mat_Poke` setup ids the device
carries at firmware 10.81 `[D-cap]`, 33 are surfaced and 11 are written; of the 79 assigned
`s_Form_Poke` formula ids `[G]`, 39 are decoded and 33 written, splitting as 33 writable, 6
decode-only and 46 unreachable. The 46 are the whole ancillary mechanism, the whole blend and
secondary formula, the W zone, persistence, interpolation and reluctance. Three further parameter
streams - convolution, Kinetic properties, and the biquad and sine bank properties - **arrive in
this project's own captures and are discarded**, along with all 90 macro values and the entire
Master section. This is not theoretical: `[C]` ancillary mathematics fires in 513 of 668 presets and
a blend or secondary formula in 362. Two surfaces change what is *possible* rather than merely
convenient: the oscillator option ids are a type-dependent variant selector and the only path to
four families of timbre, and the bank-property column selectors are the only way to know what
"Bank A column 3" means, because for three bank types that is preset data rather than a static
table.

### RF9 - the preset index must be a generated table - confidence B

The rule "index equals the printed number minus one" fits all four recorded device observations and
is **not universal**: over the 608 presets present in both sources the offset is 0 in five
categories, takes 1 or 2 in one category with 0 never occurring, and ranges over four values in
others. The mechanism is accumulating insertions and deletions ahead of a position, so no
arithmetic on any printed number is safe. The winning account is a generated table - category from
the first category tag in the header's own name list `[G]` `docs/HakenMidi.h:408`, index from the
zero-based position in filename order within the category - with zero disagreements across 608
presets on the category axis and the firmware flash manifest's order reproduced for all 668 slots.
The dispute is also sidesteppable: every dump ends with the device's own slot trailer `[G]`
`docs/HakenMidi.h:454-463` `[D-cap]`, so a load can report the true slot rather than echo the
request. One gate remains open and is scored **D**: what `load_preset`'s category argument actually
addresses, since the project reproduces a 14-entry **menu order** while the documented value space
is a 91-tag list, and sending the wrong one is not an off-by-one but an unrelated category.

### RF10 - the guides are firmware 10.80, and the drift has three live traps - confidence A

`docs/` is stamped "Firmware Version 10.61 to 10.80" `[G]`
`docs/EaganMatrixUserGuide.txt:3-4`, corroborated by every published guide on the vendor's site.
The consequence is sharper than a label: features added in 10.81 are documented in no guide at all,
only in the header, so an agent told the guides are current will conclude that a missing feature
does not exist rather than that it is header-only. `CLAUDE.md` said 10.81 and is corrected in this
pass. The 10.44 drift audit found 28 confirmed carry-overs, 3 contradicted and 2 unresolved, and the
three contradictions are traps: matrix value code 48 is **z squared**, not linear Z, and codes 45-48
are four built-in formulas rather than raw inputs `[G]` `docs/HakenMidi.h:755-758`; the matrix-select
opcode this project uses on every write is the Alt-modified variant, with the plain select being a
different value; and the formula id once called "trim" does not exist at 10.81. Two gaps closed from
the header offline: the begin/end scales are two distinct axes that `CLAUDE.md` conflated, and the
formula letter pool is **44** (A..V plus A'..V'), not 22, with A..V preferred. Three header
snapshots exist in a strict superset chain, and the divergence is concentrated in the live protocol
and absent from every region a file decoder reads.

### RF11 - four documented traps became measured conventions, and four were narrowed - confidence B

The Cookbook's trap list scored 8 of 8 confirmed with 19 new traps found, and the corpus then turned
four of them from warnings into measurements: `[C]` 530 of the 539 presets that wire any
shape-generator column feed at least one trigger column, and 433 of 433 generator uses in the modern
presets feed both frequency and trigger; Double Computation Rate is explicitly on in a minority of
668 and the factory convention is off; FM through an audio row into an oscillator frequency column
appears as `[C]` 131 cells and is `[D]` device-verified **not** to cause knob lag, so that pitfall is
specific to Direct-row constructions; and Master SL and SR share one formula letter in `[C]` 753
presets, the most common shared-letter pair in the library by a factor of eight. One scoping
correction matters: only Continuous Cycle and Single Cycle generators are trigger-driven, so a lint
rule demanding a trigger on all four types would produce false alarms. The narrowings make the
knowledge more useful than a longer warning list would: resonator gain compensation turns out to be
one preset rather than an idiom, three blank-column traps are settled by occupancy without a device
test, and one documented conflict dissolves entirely once a formula constant is distinguished from
an evaluated column value.

### RF12 - there is no automatic gain protection, and the replacement was not in the notes - confidence A

Reduce Gain is deprecated at 10.81 and acts only while the Editor is running `[G]`
`docs/EaganMatrixUserGuide.txt:6566-6570`. Windows MIDI ports are exclusive and the MCP holds the
port, so **during all MCP patch-building there is no gain protection whatsoever** - and an agent
reasoning from the feature's existence, or from 10.44-era material where it was live, will assume
the Module protects itself. The replacement was recovered from the guide's own loudness section
`[G]` `docs/EaganMatrixUserGuide.txt:8411-8462` as five numbered rules, none of which had appeared
in this project's documents: no constants past unity in an output formula unless amplitude is
controlled elsewhere; nothing past roughly 0.1 into noise or biquad inputs; raw Z capped at 30 to 50
per cent; no free experimentation with noise plus biquads; and always keep a known mute path. The
guide offers a continuous controller as that mute path and the header disagrees about what the
controller is - see section 7, item 3. `[I]` A free macro multiplying the output columns to zero,
plus `get_status`, is this project's actual overload safety net. The Module also announces its own
trouble through task messages for reduced gain, reduced polyphony and NaN errors, and nothing in
`eagan_mcp` listens.

### RF13 - every module type has a card, and four column maps were corrected - confidence B / C

All 18 module entries now carry column meanings, units and MCP reachability; 32 fields could not be
filled offline, of which 9 are device-only and ship as `[I]`. Four column maps were corrected by the
corpus **against the guides**, which matters because a device test aimed at the wrong column is
wasted device time: HarMan's five labelled columns are not columns 1 to 5 but 1, 2, 3, 7 and 8, with
occupancy at 100 per cent on three of them and under 5 per cent on the two the guide implies;
SineSpray's last label sits at column 8 with columns 5 to 7 inert in all 19 users; MicroDelay's taps
are interleaved rather than grouped, under which reading one factory preset becomes a textbook
four-tap waveguide; and SineBank does not reuse BiqBank's picklist. Two structural constraints that
no matrix read reveals must be checked before banks are assigned: a spectral set occupies half of a
memory shared by all four delays, so two manipulators and a Bank C delay must specify the same set;
and removing a formula from the matrix **deletes it on save** `[G]`, which yields a hard agent rule
- never clear a cell whose formula you intend to reuse, mute it instead, and the MCP cannot set the
mute bit today.

### RF14 - stream 1 is probably macro labels, not the description, and it is open - confidence D

The header names stream 1 as preset control text `[G]` `docs/HakenMidi.h:1082` and the guide gives
its grammar as the macro naming area, which would make this project's description argument a
possible overwrite of the panel macro labels - the names a human reads on the Module. But the
project's contrary reading is recorded as `[D]` device-verified on 2026-10-25 at firmware 10.81.
Both cannot be right as stated and **this report does not adjudicate it**. The corpus adds a third
voice that leans toward the header without settling it: `[C]` all 668 presets carry an embedded
control text whose content is a flat macro key-value list, with 538 presets labelling the first
macro, while per-preset prose lives in separate description files. `[I]` The most likely
reconciliation is that the device accepts arbitrary text in the stream and the project's test
observed that acceptance rather than its meaning. The risk to act on is narrow and already
recorded: do not call the description argument again until `DT7` has run. A corollary holds either
way - `[C]` the corpus proves two label keys are exactly the fifth and sixth macros, in 0 of 668
counter-examples, so the MCP may already possess an unrecognised ability to name macros.

### RF15 - twenty defects in the project's own code - confidence A

All twenty are fixable offline, and the five that matter most are the mirrored negative height
(`RF2`), a preset-file pre-scan that screened two controllers which store nothing while missing the
two that write flash, the same wrong facts repeated in the raw-send docstring that is the only
defence on the one tool that can reach the store controller, a polyphony ceiling of 8 against `[C]`
24 factory presets that store 10, 12 or 14, and a transfer default labelled in the wrong unit which
mislabels `[C]` 334 factory formulas. The rest range from a missing matrix column name through a
shape table that stops where the header continues to a read tool that silently omits 40 ids and
reports no indication they were present. This pass shipped sixteen code-fix changes against this
list and `tools_spec.md` section 8 carries a named disposition for each one it did not take, so a
later reader can tell "out of scope" from "overlooked". Eight documentation repairs were specified
with exact replacement text, led by this project's own protocol-source citation pointing at a
**stale** vendored header copy - the "do not guess, cite the header" rule aimed at the wrong file.

## 4. The device test plan

Ranked by how many inferred fields each test would promote to evidence. 79 filed blocks merged to
about 45 distinct tests in 21 ranked rows; the namespace is reserved to `DT45`. The full merged
table with per-test notes is `analysis/synthesis.md` section 10 (see section 9, item 1 on where
that file lives).

**Protocol for all of them**, from `.maister/docs/standards/testing/test-writing.md` and `[D]`
`CLAUDE.md`: one change at a time, then a single yes/no question, with the owner messaged
immediately before any long listen. Loading a preset destroys the unsaved edit slot, so sequence
the loads first. Every write goes to the **edit slot**; user slots 1 to 5 are in use; never send the
system-slot store path. Lower Attenuation and the post-Master output before any structural change,
and no headphones.

| Rank | Test | Kind |
|---|---|---|
| DT1 | Negative height: offset or sign-and-magnitude. One audible write of -0.90 on a known vowel column; "did the vowel jump a long way, or barely move?" The two readings predict 0.80 of the column's range apart | listen |
| DT2 | What does `load_preset`'s category argument address? Three captures, record the names. Gates DT3 | read-only |
| DT3 | Within-category collation: does category 6, index 0 return the expected name? | read-only |
| DT4 | Does an absent Bank A really mean BiqBank? Load a preset that sets neither bank, then read the setup | read-only |
| DT5 | Does a cell-select setup stream carry all 92 ids? One read; the cheapest high-yield test in the plan | read-only |
| DT6 | What do Z and Y do at note-off on this keyboard? The most important pair for patch design | listen x2 |
| DT7 | Is stream 1 the description or the macro labels? Run before any further name write | read-only |
| DT8 | Interpolation default: 40 or 0? Then write 127 and see whether it clamps | read-only |
| DT9 | Base polyphony above 8, with a status read in the same breath | write (edit slot) |
| DT10 | Matrix value code 48 is z squared | listen |
| DT11 | The X transfer default is kHz, not octaves | read-only |
| DT12 | The BiqMouth shape column to vowel table, swept in nine steps as one session with the owner naming vowels | listen x9 |
| DT13 | The five surviving blank-column tests | mixed |
| DT14 | HarMan columns, re-aimed per RF13 onto the columns occupancy actually supports | listen |
| DT15 | The defaults the corpus cannot see, by construction | read-only |
| DT16 | Protocol efficiency and the formula-letter allocator: four read-only probes | read-only |
| DT17 | The plain-keyboard contract, remaining - including whether `set_bend_range`, the one untested tool, works at all | listen |
| DT18 | Legacy decode completion; try the offline route first | read-only |
| DT19 | Formula write ordering and latching | mixed |
| DT20 | Double Computation Rate A/B. Deliberately degrades a working patch, so read the status first and listen only if needed | listen |
| DT21 | **BLOCKED BY TOOL** - the tests that need a capability the MCP does not have | write |

### 4.1 The blocked-by-tool tests, and a count conflict recorded rather than resolved

`DT21` is the merged plan's single row for every test that needs an MCP capability the project does
not have. Each of them validates **the very id its new tool would write**, so each is the acceptance
test for the specification that would unblock it, and they are scheduled **after** the `T` work
rather than before.

The enumeration is `tools_spec.md` section 7, which lists eleven rows, each naming the id or stream,
the `T` rank that unblocks it and what the test would establish. It is not repeated here.

**The count conflict.** This pass's research output says "eleven tests are BLOCKED BY TOOL";
`analysis/findings/modules-devicetests.md:220` marks **four** of its own tests blocked, and
`analysis/synthesis.md:1011` names **four** id groups. Nothing in the corpus produces eleven
directly. The eleven rows in `tools_spec.md` are that document's enumeration, reached by expanding
the four groups into the individual ids and streams the module cards name. `[I]` The inference is
that the report counted ids while the findings counted test blocks; eleven is reproducible only by
that expansion, so **the table, not the number, is the locator**, and the number is not asserted
here as a measurement.

### 4.2 Answerable without the device - do not spend a session on these

Each of these was settled offline, and a future session that spends a device slot on one is
spending it twice. The compressor stage is per-preset. The DSP polyphony controller arrives in the
config dump rather than the ping reply. A failed load is detectable as the absence of the
end-of-dump control change and program change, in 18 of 18 real dumps against 0 of 2 failures. The
loaded slot is in the dump's last three messages. Convolution state is in **every** dump. The
assignable Master column defaults are readable as their own setup ids. Matrix rows 9 to 12 are not
always audio in and submix. The hardware id is a known constant. And whether `set_formula` accepts
the fifth and sixth macros is a **code read**, not a device test.

**Keep the two empty captures.** `captures/first_capture_20261025_115208.mid` (0 messages) and
`captures/preset_20261025_123730.mid` (12) are the only recorded instances of the failed-load mode
`[D-cap]`. They are evidence, not noise, and must survive any tidy-up.

## 5. Gaps and uncertainties, in four classes

**Image-only information.** The BiqMouth mouth-shape charts, the X, Y and Z transfer-function
graphs, the Z-function list and the macro display-style code table exist **only as images** in
guides this project reads as PDF-to-text. The transfer-function list was recovered from the header;
the vowel table and the style codes were not, and the vowel table needs the ear (`DT12`). `[C]` One
style code at 257 uses is the house default, whatever it renders as.

**Structurally unrecoverable from the corpus.** Shape-generator types and matrix row types are
recoverable from `[C]` 155 of 246 modern presets and **0 of 422 legacy** ones, so any statistic over
those fields describes the modern third of the library only and must be reported with the
modern-only denominator. Timing, tempo and delta times are not available at all, because this
project's own save path zeroes every delta time.

**No corpus leverage, by construction.** Where a wire value's default *is* the value in question,
the compression rule of `RF4` guarantees silence: the WaveBank default waveform, the assignable
Master column defaults, the Additive bank's second mode id - so no factory preset can be shown to
select that mode at all - and the biquad partial count. These are precisely the tests at `DT15`.

**Owned by nobody.** The overlay and tuning-grid guide, referenced twice from the User Guide, was
assigned to no category and was not read. And the Module's per-module DSP polyphony caps are
unknown; the guide names caps for several other instruments in the family and never names this one,
which leaves "is Additive usable polyphonically here" as a 2-versus-12 question that decides whether
a whole module is worth building on.

## 6. The known-weak-citation note

This is the most load-bearing section of this document, because roughly 150 citations were corrected
across eleven task groups in this pass and the failure modes were systematic rather than careless.

**Header line numbers are exact.** `docs/HakenMidi.h` citations were verified individually and can
be trusted as `file:line`. A header citation is firmware 10.81.

**Guide line numbers are not, and the quote is the locator.** `docs/EaganMatrixUserGuide.txt` line
numbers are accurate to the section and to within roughly 30 lines inside it, because the file is a
PDF extraction carrying 208 form feeds and multi-column bleed. Every guide claim must therefore be
**quoted verbatim**, and the quote, not the line number, is the reliable locator. A guide citation
is firmware 10.80 at best.

**Three extraction failure modes observed in this pass**, all of which break a naive check:

1. The extraction **interleaves a table's label column into a sentence**, so an exact-substring
   check fails on a *correct* quote. The working gate matches an in-order word subsequence instead.
2. It **drops letters** - one observed case turns "unless" into "ules".
3. It **splits words** - one observed case turns a unit abbreviation into two space-separated
   letters.

A verification gate that demands an exact substring will therefore reject correct citations and
teach the next writer to weaken the quote. Match a word subsequence.

**The corpus figures must never be promoted.** The `[C]` statistics this pass leans on - 564 orphan
negative flags, the 775 / 0 / 334 split on the X transfer writes, 14,147 height writes, 187 bank
property blocks, 7,259 formulas - are internally consistent and were produced by the pass's own
scripts, but they **were not re-derived offline in the build pass**. They stay `[C]`. Under
`.maister/docs/standards/protocol/protocol-sources.md` a corpus statistic is evidence about Haken's
convention and never about what this project has heard on the device, and no amount of corpus
agreement changes that.

**A verification tool that lies, measured on this machine on 2026-10-27.** `grep -P` here fails
with `-P supports only unibyte and UTF-8 locales` and **checks no bytes**. Worse, it reports
success: run bare it exits 2, but through a pipe the pipeline exits 0, and in the common
`if grep -qP ...; then fail; fi` shape the failure is indistinguishable from "no match", so the gate
passes vacuously. Two task groups in this pass were caught by exactly that. **Any ASCII or
non-ASCII byte gate must be written in Python**, which is how the gates for this document are
written.

## 7. Where this pass contradicted the research, and the rule it adopted

Three claims in the research output do not reproduce. The shipped knowledge base carries the
corrected versions, and the originals must not be reasserted.

1. **A percentage that does not reproduce.** The research reported that Z carries 36.5 per cent of
   factory formula usage; that figure does not reproduce from the shipped census. The conclusion
   survives intact on figures that do reproduce: `[C]` `VEndZ` appears in **2,462** of **7,259**
   factory formulas against `VEndY` 1,135 and `VEndX` 1,130, and `z_modulation` fires in 602 of 668
   presets against 531 and 510. `eagan_mcp/knowledge/model.md` carries the reproducible form.

2. **Confident, plausible, wrong prose about a real preset - and this is a finding in its own
   right.** The research prose disagrees with the shipped catalog in at least nine measured places.
   The clearest: a named factory preset is cited by the guide *and* by the research as *the*
   polyphony-scaler example, and its decoded formula has **no scaler** - the preset is `Instant
   Reich`, and `eagan_mcp/knowledge/modules/summeddelay.md` records the conflict with both sides
   standing and names the presets whose shipped data actually shows one. Presets carrying a
   polyphony scaler among the 49 with a wiring block number **eight, not two**, and per-letter
   sample-and-hold formulas number **44, not 35**. The rule this pass adopted, and the one a later
   reader should apply: where decoded shipped data and prose disagree, **the catalog wins**. The
   defect class is worth naming because it is not a typo - it is fluent, specific prose about a real
   object, which is exactly the kind of claim a reader does not think to check.

3. **A controller that is not a mute.** The guide offers a continuous controller on channel 1 as the
   mute path of `RF12`, describing it as 0 for Mute and 1 for Unmute - but the header defines that
   same controller as `ccPost`, the post-Master output level `[G]` `docs/HakenMidi.h:577`. By the
   resolution order the header wins: 0 does mute, but **1 is 1/127 of full level**, not full level.
   `eagan_mcp/knowledge/model.md` and `pitfalls.md` both carry the conflict block and the
   correction; the macro-multiplier mute path is the one to use.

## 8. Prior art, credit, and two licence carve-outs recorded rather than resolved

Two vendored reference repositories informed this work: `ref/cohem` and `ref/pachde-CHEM`, both MIT
and both **Copyright Paul Chase Dempsey** - the full legal name belongs in any attribution. cohem's
notes file, with its poke-name list and its table-as-lookup idea, saved substantial time and must be
credited if those ideas are reused.

Two carve-outs, **recorded, not resolved**:

1. cohem's README places all graphics and documentation under **plain copyright**, which covers that
   notes file. Use its *facts*; never its prose.
2. The protocol header is **Lippold Haken's** copyright, not MIT, in all three copies - including
   `docs/HakenMidi.h`, which this project calls its source of truth. That is fine for private use
   and is **a blocker if this repository is ever published**. `.gitignore` already excludes `docs/`,
   which limits the exposure but does not decide the question.

`LICENSE` (MIT) and `license = "MIT"` in `pyproject.toml` shipped in this pass, so the project's own
licence is settled; the two carve-outs above are not, and they are an operator decision.

**Two prior-art defects - do not port.** One reference implementation hardcodes a matrix stride one
less than the header's column count, so its bank-clear walks the wrong cells. And its legacy
generation is unimplemented, with the channel-pressure text path annotated as a *future* firmware
when it is in fact the **older** encoding used by 422 of the 668 files - so anyone leaning on it for
the corpus would silently decode 63 per cent of the library as empty.

## 9. Open items this pass records and does not resolve

1. **About 80 citations point into a gitignored tree.** `tools_spec.md` and the knowledge cards cite
   research-pass documents - `analysis/findings/*.md` and `outputs/research-report.md` - that live
   under `.maister/tasks/`, which `.gitignore` excludes. They resolve on this machine and resolve to
   nothing on a fresh clone. This is an operator decision between committing the research tree and
   re-pointing the citations; no citation was reworded in this pass to hide it.
2. **Nothing from this pass is git-tracked yet.** `tests/`, `eagan_mcp/knowledge/`,
   `eagan_mcp/preset_file.py`, `tools_spec.md`, `.claude/` and this file are all untracked, and
   nothing ignores them, so `git add` picks them up. No commit was made.
3. **`ROADMAP.md` carries no cross-reference to this file.** `CLAUDE.md` now does. The specification
   asked for both; only the `CLAUDE.md` line was in this group's file scope.
4. **`.maister/docs/standards/global/error-handling.md:18` is now false.** It states "No custom
   exception classes"; `eagan_mcp/preset_file.py:309` defines `PresetFileError(ValueError)`.
5. **`.maister/docs/project/tech-stack.md:113` is now false.** It states that the project is not
   currently a git repository.
6. **Several documents instruct `uv run`.** It fails with `os error 32` while the MCP server holds
   `.venv/Scripts/eagan_mcp.exe`. `README.md:37` records this; the instructions elsewhere do not.
7. **The negative-height device test stays open**, as `ROADMAP.md` says. `DT1` is unrun, `RF2`
   remains confidence B, and the two user presets written under the old encoding are still wrong on
   the device.
8. **Nineteen of the 32 tool docstrings do not state their write scope**, against
   `.maister/docs/standards/protocol/device-safety.md`.
