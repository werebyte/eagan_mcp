# Worked examples - two plain-words requests, built end to end

Two patch requests, each decomposed into the MCP calls that build it, and each followed by an
honest list of what the project does **not** know about the result.

These two are the project's acceptance test. The thing being tested is whether a fresh chat
holding only this MCP and its skills can take a sentence of plain words and reach a patch that
makes the requested sound. The two sentences are:

1. "deep Harkonnen (Dune) chant voice, didgeridoo-style vowel wah on the mod wheel" `[I]` - the
   inference from the request is that it needs a formant bank, a sub-octave, and the wheel moving
   a vowel.
2. "3-osc poly synth with FM from osc 3 to osc 1 with its own envelope and a slight pitch LFO"
   `[I]` - the inference from the request is that it needs three oscillator slots, an audio-rate
   modulation path, a one-shot shape generator and a continuous one.

## What this file is, and what it is not

- **Neither plan has been played.** They are assembled from parts, and the parts carry different
   evidence grades. Where a step is device-recorded it says so; where it is corpus-attested or
   inferred it says that instead. A step with no tag is a defect `[I]` - the inference is the
   project's own rule in `.maister/docs/standards/protocol/protocol-sources.md`, "The Five Bracket
   Tags".
- **Plan 1 is a rebuild, not a new idea.** Its chain was built on the Module on 2026-10-25 and
   stored to user slot 5, and the parts of it that were never heard are listed as such `[D]`
   `CLAUDE.md:165-166`, 2026-10-25, fw 10.81.
- **Plan 2 has never existed in any form.** No findings file describes a three-oscillator layout;
   its FM pair and its LFO are each recorded separately and are joined here for the first time
   `[C]` (`RECIPES.md` records a two-oscillator FM pair at `:86-94` and a pitch LFO at `:78-83`,
   and nothing in `CLAUDE.md`, `RECIPES.md` or `patterns.md` joins them).
- **The construction vocabulary is not restated here.** Patterns are cited by number from
   `patterns.md`, module columns from `modules/<name>.md`, shared facts from `modules/index.md`
   and the voice model from `model.md` `[I]` - the inference is the project's no-duplication rule,
   `.maister/docs/standards/global/conventions.md:10`.

A citation written `RECIPES.md:<n> (moved to pitfalls.md)` points at a device finding that lived
at that line of `RECIPES.md` when it was recorded and now lives in `eagan_mcp/knowledge/pitfalls.md`.
The original line is kept as the anchor because it is the stable one, and `pitfalls.md` carries the
same `RECIPES.md:<n> (moved)` marker at the finding itself.

Cell orientation throughout is `column <- row = value`, the orientation
`set_matrix_point(row, col, value)` takes `[G]` `eagan_mcp/server.py:255`.

---

## Plan 1 - "deep Harkonnen (Dune) chant voice, didgeridoo-style vowel wah on the mod wheel"

### 1.1 What the request decomposes into

| Words | What they mean on this device | Source |
|---|---|---|
| "chant voice" | a formant filter bank: BiqMouth, five biquad formants over an audio input | `[G]` `docs/EaganMatrixUserGuide.txt:2771-2773` |
| "deep" | a sub-octave partial under the main cluster, not a transposition of everything | `[D]` `CLAUDE.md:161-162`, 2026-10-25, fw 10.81 |
| "didgeridoo-style vowel wah" | a short morph between two chart-adjacent mouth shapes, not a sweep | `[G]` `docs/EaganMatrixUserGuide.txt:2849-2853` |
| "on the mod wheel" | MIDI CC 1 arrives as the formula component **Y** | `[D]` `CLAUDE.md:119`, 2026-10-25, fw 10.81 |
| the drone body | four detuned saws from a WaveBank feeding the formant bank | `[D]` `RECIPES.md:166-167`, 2026-10-25, fw 10.81 |

### 1.2 Step 0 - confirm the template by capture, never by the printed list

The template is the factory preset `BiqMouth - Basic`, in the Utility category.

- `[D]` `CLAUDE.md:155-157`, 2026-10-25, fw 10.81: its index on 10.81 is **7**, the 10.81 Quick
   Start list says 8, and index 8 is a different preset, `Comb Filter Basics`.
- `[G]` `.maister/docs/standards/protocol/protocol-sources.md:43-49` makes that a rule rather
   than a one-off: confirm an index with `load_and_capture_preset`, which returns the loaded
   preset's name, and correct by plus or minus one when the name does not match.

```
load_and_capture_preset(13, 7)      # category 13 = UT (Utility), index 7.
                                    # BOTH arguments are required: the signature is
                                    # (category: int, index: int, save_as="", seconds=3.0).
                                    # expect name == "BiqMouth - Basic"
                                    # if it returns "Comb Filter Basics", the index is 6 or 8:
                                    # try the neighbours and read the name, do not assume
get_matrix()                        # retry with a longer listen if the first read is empty
get_setup()
```

- `[D]` `CLAUDE.md:137`, 2026-10-25, fw 10.81 records why the second read matters: the first
   matrix read after a connect or a load can come back empty, and the tool retries with a 4 s
   window.

### 1.3 What the template already gives you

`[C]` `BiqMouth - Basic` is one of the 49 factory presets whose decoded wiring ships in
`eagan_mcp/knowledge/factory_catalog.json`, so every cell below is read out of the shipped data
rather than remembered:

```
bank: A = WaveBank ; B = BiqMouth ; C = VoiceDelay (unused)
polyphony: base 4, expanded on, double computation rate off
recirculator: Short Reverb

Bank A 1  (col 27) <- Direct + = z^2                       amplitude from pressure
Bank A 2  (col 28) <- Direct + = X, Direct + (2) = A, Direct - = 0.001     F1
Bank A 3  (col 29) <- Direct + = X, Direct + (2) = B, Direct - = 0.002     F2
Bank A 4  (col 30) <- Direct + = X, Direct + (2) = C, Direct - = 0.003     F3
Bank A 5  (col 31) <- Direct + = X, Direct + (2) = D, Direct - = 0.004     F4
Bank A 6  (col 32) <- Direct x (multiply) = 0.5   *** MUTED, and no pitch on the column ***
Bank B 1  (col 35) <- Bank A = 0.25                        the formant bank's input
Bank B 2  (Sh, col 36) <- Direct + = E      Bank B 5 (sB, col 39) <- Direct + = H
Bank B 3  (sF, col 37) <- Direct + = F      Bank B 6 (C,  col 40) <- Direct + = I
Bank B 4  (oF, col 38) <- Direct + = G      Bank B 7 (sA, col 41) <- Direct + = J
Master SL/SR (cols 0/1) <- Bank B = 0.5
SG 1 F (col 51) <- Direct + = K             SG 1 T (col 52) <- Direct + = W

  A..D = W SG1 Sine 0.11..0.15 x 0.01, phases Off / 0.25 / 0.5 / 0.75   (the saw detune)
  E = W Constant 0.48 x 10 x Macro (i)                                  (Sh)
  F = W Constant 0.20 x 10 x Macro (ii) ; Y = 0.5 -> 0.5                (sF)
  H = W Constant 0.20 x 10 x Macro (iv) ; Y = 0.5 -> 0.5                (sB)
  letters in use: A B C D E F G H I J K      free: L..V
```

Three things in that block decide the whole plan:

- `[C]` **The sub-octave is already half-built and switched off.** Bank A column 6 is WaveBank
   `F5`, and the preset ships a `Direct x (multiply) = 0.5` on it that is **muted**, with no pitch
   on the column at all (`factory_catalog.json`, `wiring`). `[G]`
   `docs/EaganMatrixUserGuide.txt:3241-3243`: a blank WaveBank frequency column simply generates
   one wave fewer, so the preset is a four-saw cluster with a disabled fifth.
- `[C]` **Eleven of the 44 formula letters are taken** (`factory_catalog.json`, `wiring`), which
   leaves `L`..`V` free among the preferred `A`..`V` half. `[D]` `CLAUDE.md:94`, 2026-10-25,
   fw 10.81 is the reason to re-check rather than trust that list: "The Module omits matrix cells
   whose formula is all zero from the matrix dump", so a letter can be defined and invisible.
- `[C]` **Every one of the six BiqMouth parameter columns is on its own macro** (`i`..`vi`), which
   is what makes this preset the tutorial case and also what you must undo on `Sh`
   (`factory_catalog.json`, `wiring`, macro labels `Mouth_0g`, `FreqMult_Min_Max`,
   `Offset_Min_Max`, `BandMult_Min_Max`, `Center`, `AmpSprd`).

### 1.4 The build, call by call

**Step 1 - turn on the sub-octave.** Two writes to Bank A column 6.

```
set_matrix_point(row=13, col=32, value="X")      # Direct +  -> WaveBank F5 = key pitch
set_matrix_point(row=16, col=32, value="0.5")    # Direct x  -> F5 = one octave down
```

- `[D]` `CLAUDE.md:161-162`, 2026-10-25, fw 10.81 is the device record of exactly this: "Bank A
   WaveBank (4 detuned saws + f5 = X x .5 sub-octave via Direct+ X and Direct x .5 on col 32)".
- `[G]` `docs/EaganMatrixUserGuide.txt:5206-5211` is why the second write produces an octave
   rather than a mix: `Direct x` multiplies the column's whole sum, it does not add a term.
- `[I]` **The second write also clears the mute.** `eagan_mcp/haken.py:143` records that the mute
   lives in bit 6 of the value byte and `eagan_mcp/haken.py:211-213` shows `encode_value` emitting
   the bare code; the inference is that re-writing a muted cell sends it unmuted, which is the only
   route the typed tools have, since no tool sends `matTogMute` (`model.md` section 8).
- `[I]` Prefer the partial column over the pitch column. `patterns.md` P7 records both placements;
   the inference stated there is that on `Bank A 2` the whole cluster drops an octave, while on
   `F5` only the fifth wave does - which is what "deep" means here, a sub under the voice rather
   than a transposed voice.

**Step 2 - the vowel wah on `Sh`.** The cell already holds letter `E`; only the formula changes.

```
set_formula(row=13, col=36, component="W", mode="Constant",
            value=0.23, magnitude=10, modifier="x 1")        # Sh = 2.3, a fixed starting vowel
set_formula(row=13, col=36, component="Y",
            height_begin=0.0, height_end=-0.2, multiplier=1) # the wheel walks Sh down to 2.1
```

- `[D]` `CLAUDE.md:163`, 2026-10-25, fw 10.81 is the device build: "Bank B Sh (col 36, formula E):
   W = 2.3 (M:oo) + Y wheel 0 -> -0.2".
- `[G]` `docs/EaganMatrixUserGuide.txt:2863` places those values on the published chart: row 2 of
   the Mouth Shape Selection Chart reads `.1 M:a`, `.2 M:uh`, `.3 M:oo`, so the wheel walks
   **`M:oo` (Food) -> `M:uh` (Mud) -> `M:a` (Pad)**, three chart-adjacent shapes.
- `[I]` **`modifier="x 1"` is not optional.** The factory `E` is `W = Constant 0.48 x 10 x
   Macro (i)`; setting only the value leaves the macro multiplier in place and `Sh` becomes
   `2.3 x macro i` rather than 2.3. The inference is from the formula summary in
   `factory_catalog.json`, where the modifier is a separate field from the value.
- `[D]` Macro `i` is freed by this edit and the request names nothing to put on it:
   `CLAUDE.md:164`, 2026-10-25, fw 10.81, "Macro i is now unused."
- `[I]` **This is a negative height**, so `set_formula` returns a `warning` naming the open device
   test; the inference is read off `eagan_mcp/server.py:454-459`, which raises the warning whenever
   `value`, `height_begin` or `height_end` is below zero. Section 1.6 carries what that means.

**Step 3 - leave the two trap columns exactly as the factory left them.** No call.

- `[D]` `RECIPES.md:162-163`, 2026-10-25, fw 10.81, verbatim: "NEVER leave sB empty: blank = 0 =
   razor-thin formants. They ring as fixed pitches that do not follow the keys and no vowel is
   heard (tested)."
- `[C]` The house rule is stronger than one test: `sF` and `sB` are written in **36 of 36**
   measured BiqMouth bank slots, with no exception in the corpus
   (`modules/biqmouth.md` section 2, from `corpus-module-wiring.md` S4). Their neutrals and the
   arithmetic behind the factory's values are `modules/biqmouth.md`'s subject and are not restated
   here.

**Step 4 - voices, bend and the budget.**

```
set_polyphony(voices=4, expanded=True, double_computation_rate=False)
set_bend_range(2)
get_status()
```

- `[D]` `CLAUDE.md:153-154`, 2026-10-25, fw 10.81 is why the third argument is `False`: "Double
   rate was the cause of 3 voices + 100% DSP; user confirmed no lag after the change." `[C]` The
   factory agrees - it is set explicitly in only 41 of 668 presets
   (`census.json:double_computation_rate`).
- `[C]` Base 4 with "+" is what the template already stores, so this call is a confirmation
   rather than a change (`factory_catalog.json`, `polyphony`). A chant voice is close to
   monophonic, so there is no reason to raise it.
- `[D]` `CLAUDE.md:147`, 2026-10-25, fw 10.81: bend range is `s_Mat_Poke` id 40 and is **not
   readable back**, so `set_bend_range` returns `verified: None` and the check is by ear.
- `[D]` `RECIPES.md:47 (moved to pitfalls.md)`, 2026-10-25, fw 10.81: "Check with get_status (dsp_usage_percent,
   dsp_polyphony) after every big change", with the fixes in the order given at `RECIPES.md:48-49 (moved to pitfalls.md)`.

**Step 5 - name it and store it.**

```
set_preset_name("Harkonnen Voice")        # name only - never pass the description argument
save_to_user_slot(5, confirm=True)
list_user_presets()                       # the verification: slot 5's name == the edit slot's
```

- `[I]` `set_preset_name`'s description argument writes stream 1, whose identity is unresolved -
   the device note calls it a description and the header plus the corpus read it as the panel macro
   labels - so writing it may destroy the preset's six macro labels (`model.md` section 11). The
   inference is that an unresolved identity on a destructive write is a reason not to write.
- `[D]` `CLAUDE.md:138-139`, 2026-10-25, fw 10.81: the store echo varies between saves, so the
   tool verifies through `list_user_presets` instead. `[D]` `CLAUDE.md:129-130`, 2026-10-25,
   fw 10.81 is the rule behind it: never verify a store by loading the slot, because loading
   replaces the unsaved edit slot.

### 1.5 What to listen for

- `[I]` Three questions, one change at a time, each answerable yes or no - the inference is the
   project's listening-test discipline in
   `.maister/docs/standards/testing/test-writing.md`: is there an octave under the voice; does the
   wheel at rest sound like "oo"; does pushing the wheel open the vowel rather than close it.
- `[D]` `CLAUDE.md:165-166`, 2026-10-25, fw 10.81 says all three are still open: "NOT TESTED by
   the user yet: default 'oo', wheel opening to 'ah' (= first test of a NEGATIVE formula height),
   sub-octave audible."

### 1.6 Plan 1 - what is unresolved

Four open parts. None of them stops the build; each one changes what you should believe about the
result.

**PLAN 1 OPEN PART 1 - CLOSED 2026-10-28. Negative heights ARE now device-verified.**
The encoding is an OFFSET (`raw = (v+1)*100`), confirmed by a pitch probe on the Module: a
constant of `-0.2` on an oscillator's F column broke notes below A3, which is where `-0.2`
predicts the crossover, while the old mirror reading (`-0.8`) would have broken every note
up to G5. `[D]` 2026-10-28, fw 10.81. The wah below is therefore sound, and the warning
`set_formula` still returns on a negative value is now over-cautious rather than a real
doubt. Historical note worth keeping: slot 5's stored height was `-0.8` where `-0.2` was
intended - one wrong byte, and the vowel wah never worked until it was rewritten.

- `[D]` `ROADMAP.md`, 2026-10-25, fw 10.81 is the open item itself: "Verify a NEGATIVE formula
   height on the device (header sign semantics)". This patch's wheel term **is** that test.
- `[C]` The encoding the codec writes is corpus-derived, not device-confirmed: a height with its
   Neg flag set is an offset, `r/100 - 1.00`, measured over all 668 factory presets
   (`patterns.md` section 1). `[G]` `docs/HakenMidi.h:1201-1202` gives the range and never the
   magnitude formula, so the offset reading fills a gap in the header rather than contradicting it.
- `[I]` **The failure mode is specific, which makes the listening test easy.** If the sign
   convention is the mirror of what the codec writes, the wheel moves `Sh` **up** from 2.3 towards
   2.5 instead of down towards 2.1 - which on the chart is `M:e` then `F:a:`, a brighter and
   female vowel rather than a darker male one. The inference is read off the chart at `[G]`
   `docs/EaganMatrixUserGuide.txt:2863`: the direction is audible, so one listen settles it.
- `[I]` **H6: the stored copy in user slot 5 is still wrong.** The codec fix repairs what is
   written from now on and cannot reach a height already saved to flash (`model.md` section 11), so
   re-saving slot 5 does not repair it - only re-entering the value does. The inference is that a
   stored preset holds the raw wire value. This plan therefore **rewrites the cell**; it does not
   load slot 5 and re-save it.

**PLAN 1 OPEN PART 2 - the vowel knob is approximate by construction, though not for the reason
the planning notes assumed.**

- `[G]` `docs/EaganMatrixUserGuide.txt:2831-2846` and `:2855-2867` - **the mouth-shape tables are
   present in the extracted guide and are reproduced in full in `modules/biqmouth.md` section 3.**
   They are not graphics-only. What the extraction loses is the diacritics (the guide prints the
   symbols as combining marks) and the yellow/purple male-female shading, and the `M:`/`F:`
   prefixes carry the shading's information anyway.
- `[G]` `docs/EaganMatrixUserGuide.txt:2775-2777` is the whole of what is documented about what
   happens *between* two chart entries: shapes are "selectable 0 to 4.5 at 0.1 intervals with
   smooth morphing between adjacent shapes". There is no description of the intermediate timbres,
   so the shape of the wah across its travel is undocumented.
- `[D]` `CLAUDE.md:163`, 2026-10-25, fw 10.81 names this patch's endpoint "ah", while `[G]`
   `docs/EaganMatrixUserGuide.txt:2863` gives `Sh` 2.1 as `M:a`, which the guide's own key at
   `:2842` calls **Pad**, not Father. Both sides stand and they may be the same vowel described
   loosely; the chart is the predictor to use.
- `[D]` `CLAUDE.md:165-166`, 2026-10-25, fw 10.81: **both chosen points are untested by ear.**
   Neither the 2.3 default nor the 2.1 endpoint has been heard, so the two numbers are a reading of
   a chart, not a measurement.
- `[C]` The conflict over the top of the range does not touch this patch but will touch any wider
   wah: the chart stops at `Sh` 4.5 and the device reaches 4.8, and what sounds between them is
   undefined (the CONFLICT block in `modules/biqmouth.md` section 2). Staying inside 0..4.5 is the
   predictable choice, and 2.1..2.3 is well inside it.

**PLAN 1 OPEN PART 3 - `sB`, and why this plan does not carry a conflict block for it.**

```
RESOLVED upstream, carried here by reference, not restated:
  modules/biqmouth.md section 2 holds a RESOLVED block showing that the guide's "1.0 means
  each formant has default bandwidth" (docs/EaganMatrixUserGuide.txt:2788-2789) and the
  device note's "Factory base: sB 0.5" (RECIPES.md:162-165, 2026-10-25, fw 10.81) were never
  in conflict: 0.5 is the FORMULA CONSTANT inside letter H and 1.0 is the EVALUATED COLUMN.
  In this very preset H = W Constant 0.2 x 10 x Macro (iv) ; Y = 0.5 -> 0.5, so the column
  evaluates to 0.5 + 2 x macro iv and sits near 1.26, not 0.5.
  The rule for this plan: aim the EVALUATED sB near 1.0..1.3, and never blank. Step 3 does
  that by leaving letter H untouched.
```

- `[I]` This plan therefore **does not** open a `sB` conflict block. The inference is the
   project's own resolution rule in
   `.maister/docs/standards/global/conventions.md:10`: a question settled in the module card is
   cross-referenced, never duplicated, and reprinting a resolved disagreement as an open one would
   mislead the reader this file exists to inform.
- `[G]` **What is genuinely open about `sB` here is a different thing: the macro.**
   `docs/HakenMidi.h:533-535`, verbatim: "On the EaganMatrix Module (E2x) only, macros i..iv are a
   special case. The E2x receives ccI..ccIV to provide offsets for the E2x i..iv CV inputs (like
   rotary)." `[I]` The inference is that on this device an incoming CC 14 does not *set* macro iv,
   it *offsets* a panel CV input, so the evaluated `sB` on this rig is not predictable from the
   stored preset alone. This has not been measured. It applies equally to `sF` on macro ii.

**PLAN 1 OPEN PART 4 - Y behaviour at note-off is unknown.**

- `[I]` `model.md` section 7, element 5: a mod wheel holds its position through note-off because
   nothing in the note-off path writes CC 1, so Y may simply not fall when the note ends. The
   inference is mechanical and **has never been checked on the Module**.
- `[I]` **For this patch the consequence is mild, and that is worth saying rather than leaving the
   warning generic.** Y here drives `Sh`, a filter shape, not a level - a formant bank with no
   input makes no sound whatever its vowel. The inference is that the vowel simply stays where the
   wheel left it between notes, which is the behaviour a player would expect from a wheel anyway.
- `[G]` `docs/ContinuumUserGuide.txt:12045` is the general remedy if it ever does matter, verbatim
   and including the extraction's own corruption: "For most presets, Z alone will not have any
   effect ules you also gate with W." The word is "unless"; the PDF extraction drops three
   characters. Note that `model.md` section 7 prints the same sentence as "[unl]ess", which is a
   repair rather than a transcription - the file as extracted reads "ules".
   `[I]` Generalised in `model.md` section 7: wrap in a gated W any component that
   must fall at note-off. The inference is that W is the only component the note-off path drives to
   zero. **Do not apply it to `Sh`** - gating the vowel would snap it back to shape 0 on every
   release.
- `[I]` The patch's amplitude is already safe without it: the template drives WaveBank amplitude
   from `z^2` on `Direct +` (section 1.3), and Z is frozen at note-on rather than held by a wheel,
   so the note's level is not hostage to this question. The inference is from the keyboard contract
   in `model.md` section 7, element 1.

---

## Plan 2 - "3-osc poly synth with FM from osc 3 to osc 1 with its own envelope and a slight pitch LFO"

### 2.1 What the request decomposes into

| Words | What they mean on this device | Source |
|---|---|---|
| "3-osc" | three of the five oscillator/filter slots set to an oscillator type | `[G]` `docs/HakenMidi.h:1507-1511` (`idOscFilTyp1..5 = 72..76`) |
| "poly" | base polyphony with "+" on and double computation rate off | `[D]` `CLAUDE.md:153-154`, 2026-10-25, fw 10.81 |
| "FM from osc 3 to osc 1" | the `Osc 3` matrix **row** into the `Osc/Filter 1 F` **column** | `[D]` `CLAUDE.md:141-142`, 2026-10-25, fw 10.81 |
| "with its own envelope" | a Single Cycle shape generator shaping the FM index - attack and shape only, see 2.4 | `[D]` `RECIPES.md:46-50`, 2026-10-25, fw 10.81 |
| "a slight pitch LFO" | one Continuous Cycle shape generator shared by all three frequency columns | `[D]` `RECIPES.md:18-19 (moved to pitfalls.md)`, 2026-10-25, fw 10.81 |

### 2.2 Step 0 - there is no template, and that is the first honest statement

- `[D]` Only one preset index in this whole project has been confirmed by capture:
   `BiqMouth - Basic` at Utility 7 (`CLAUDE.md:155-157`, 2026-10-25, fw 10.81). `[I]` The inference
   is that plan 2 cannot name a starting preset without breaking the project's own rule against
   trusting a printed index, so it starts from **whatever is in the edit slot** and writes every
   cell it needs.
- `[C]` `FM Bells` is the nearest shipped worked example and is still not a template: it is a
   legacy 9.55 file whose seven letters carry ancillary exponents, a blend and a secondary formula,
   none of which any tool writes (`factory_catalog.json`, `wiring`). `[I]` The inference is to read
   it for its shape and build fresh rather than edit it.
- `[I]` So the first call is a survey, not an edit; the inference is that without it the letter
   choices below are guesses:

```
get_matrix()        # which cells and which letters are already in use
get_setup()         # which slots are oscillators, which are filters, bank and SG types
```

`[C]` What `FM Bells` is worth reading for - the carrier-only output rule, drawn straight from the
shipped wiring (`factory_catalog.json`, `wiring`):

```
Osc/Filter 1 F (col 13) <- Osc 2 = A, Osc 3 = A, Direct + = F, Direct x (multiply) = 2
Master SL/SR  (cols 0/1) <- Osc 1 = D
   A = [W x (X + Y + Z)] W = SG3 0.32 x 1 [shape Ramp Down] x Macro (iii)
                         ; Z = Initial 0.14->0.25 x 10
```

`[C]` Two modulators land on the carrier's frequency column through one shared letter, and **only
the carrier reaches the Master** - neither `Osc 2` nor `Osc 3` has a Master cell in the whole
preset (`factory_catalog.json`, `wiring`, 25 cells).

### 2.3 The build, call by call

**Step 1 - the three slots.** Columns are fixed by the slot number: slot `n` owns input, `F` and
`B/S` at `12 + 3(n-1)`, `13 + 3(n-1)`, `14 + 3(n-1)` `[G]` `eagan_mcp/matrix_map.py:30-35`.

```
set_osc_type(slot=1, type_name="DSF Oscillator")     # carrier   : cols 12 / 13 / 14
set_osc_type(slot=2, type_name="DSF Oscillator")     # unison    : cols 15 / 16 / 17
set_osc_type(slot=3, type_name="DSF Oscillator")     # modulator : cols 18 / 19 / 20
```

- `[C]` `DSF Oscillator` is wire value 0 and the default, so it is also the safe choice
   (`eagan_mcp/setup.py:10-11`). `[G]` `docs/EaganMatrixUserGuide.txt` names Ladder Low Pass and
   PWM Oscillator as the computationally intensive slot types; `[D]` `RECIPES.md:46 (moved to pitfalls.md)`, 2026-10-25,
   fw 10.81 repeats that and makes swapping them out the first DSP fix.

**Step 2 - pitch onto all three frequency columns, and the modulator's ratio.**

```
set_matrix_point(row=13, col=13, value="X")      # Osc 1 F = key pitch
set_matrix_point(row=13, col=16, value="X")      # Osc 2 F = key pitch
set_matrix_point(row=13, col=19, value="X")      # Osc 3 F = key pitch
set_matrix_point(row=16, col=19, value="2")      # Direct x -> Osc 3 F : a 2:1 FM ratio
```

- `[C]` The predefined `X` code onto a frequency column is `modules/index.md` cross-module
   pattern 1, and the bare constant on `Direct x` to ratio one column against another is
   cross-module pattern 2, measured at 46 of 668 presets for the `Osc 1 F` / `Osc 2 F` pair.
- `[C]` `FM Bells` ratios all three of its frequency columns the same way, with a `2` on
   `Direct x` into columns 13, 16 and 19 (`factory_catalog.json`, `wiring`).
- `[D]` `RECIPES.md:31-32 (moved to pitfalls.md)`, 2026-10-25, fw 10.81 is the restriction on this column: "Keep macros
   off oscillator F columns." A ratio knob therefore does not go here; change the constant instead.

**Step 3 - the two audible oscillators to the Master, and the modulator nowhere near it.**

```
set_matrix_point(row=1, col=0, value="L")        # Osc 1 -> Master SL   pick L..V after get_matrix
set_matrix_point(row=1, col=1, value="L")        # Osc 1 -> Master SR   same letter = the stereo idiom
set_matrix_point(row=2, col=0, value="L")        # Osc 2 -> Master SL
set_matrix_point(row=2, col=1, value="L")        # Osc 2 -> Master SR
set_formula(row=1, col=0, component="W", mode="Gated", value=0.1, magnitude=1,
            operator="W x (X + Y + Z)")
set_formula(row=1, col=0, component="Z", mode="Initial",
            height_begin=0.3, height_end=1.0, multiplier=1)
```

- `[D]` `RECIPES.md:43`, 2026-10-25, fw 10.81, verbatim: "Osc B should not go to the Master if it
   is only a modulator." `[C]` `FM Bells` obeys it absolutely (section 2.2).
- `[D]` **CORRECTED 2026-10-28: `W` is `Gated`, not `Constant`.** This plan said
   `W = Constant 0.3 x Macro (i)` under `(W + X + Y) x Z`, and a patch built from it **never
   released** - nothing in that formula falls at note-off, so every note hung. `model.md`
   section 7 states the remedy in the other direction: W is the only component the note-off path
   drives to zero, so wrap anything that does not self-zero in a W gate. Built on the device and
   confirmed by ear: with `W = Gated` the note stops cleanly when the key comes up. The `Z`
   height also gains a `0.3` floor so a soft keystroke is still audible.
- `[D]` **The `x Macro (i)` is removed, and do not put it back without setting the macro.** On
   this rig macro i reads **0**, and multiplying the output by zero makes the patch silent and
   look broken. `docs/HakenMidi.h:533-535` makes macros i..iv CV *offsets* rather than plain
   values, so the stored number does not predict the level. If you want the documented mute path
   (`docs/EaganMatrixUserGuide.txt:8450-8452`, "Put a free macro as a Multiplier (down to zero)
   on the SL/SR columns to mute sound"), add `modifier="x Macro"` deliberately AND set that macro
   non-zero first - it is a performance control, not a default.
- `[C]` `Z = Initial` is velocity on a plain keyboard, and is the output idiom `patterns.md` P8
   reads off `Dueling BiqBanks` - `[(W + X + Y) x Z] W = Constant -0.31 x 1 x Macro (i) ; ...
   Z = Initial None->1.0 x 1`. Note that corpus idiom carries the same non-releasing shape, so
   it is a template for the LEVEL, not for the gate.
- `[G]` `docs/EaganMatrixUserGuide.txt:8428-8430`, verbatim: "Never use constants in output
   formulas - and unless you know what you are doing never ever use them past unity (1) anywhere
   else". `Gated` is not a constant - it follows the note gate - so the corrected formula above
   satisfies this rule as well as the release one, which the `Constant` form did not. `[G]`
   `docs/EaganMatrixUserGuide.txt:8450-8452` makes the macro do double duty as the mute path: "Put
   a free macro as a Multiplier (down to zero) on the SL/SR columns to mute sound".
- `[I]` The macro caveat from plan 1 applies here too: `docs/HakenMidi.h:533-535` makes macros
   i..iv CV **offsets** on this device, so the inference is that the level is not fully predictable
   from the stored value and must be set by ear on the panel.

**Step 4 - FM with its own envelope.** One shape generator, one letter, on the `Osc 3` row.

```
set_shape_generator(sg=2, type_name="Single Cycle")
set_matrix_point(row=13, col=53, value="2")      # SG 2 F = 2 Hz -> one Hann cycle ~0.5 s
set_matrix_point(row=13, col=54, value="W")      # SG 2 T = gated note   <-- NEVER SKIP
set_matrix_point(row=3,  col=13, value="M")      # Osc 3 row -> Osc 1 F = the FM index
set_formula(row=3, col=13, component="W", mode="SG2", sg_shape="Hann",
            value=0.6, magnitude=1)              # deviation in kHz
```

- `[D]` `RECIPES.md:46-50`, 2026-10-25, fw 10.81 is this construction verbatim: "SG2: Single
   Cycle, F = 2 Hz (one Hann cycle ~0.5 s), T = W" / "Formula B: W mode SG2, sg_shape Hann,
   value 0.5..1.0, magnitude 1" / "`Osc 3 -> Osc 1 F = B`" / "Lower SG F = longer swell."
- `[D]` `RECIPES.md:44`, 2026-10-25, fw 10.81: "The formula value is the deviation in kHz (F
   columns are kHz)." `[I]` The inference is that the FM depth is absolute, not an interval, so the
   brightness of the result changes across the keyboard - the same caveat `RECIPES.md:50` records.
- `[D]` `RECIPES.md:24 (moved to pitfalls.md)`, 2026-10-25, fw 10.81 and `CLAUDE.md:141-142`, 2026-10-25, fw 10.81 are
   the reason this construction is safe to reach for: FM through an audio row into an oscillator
   `F` column was played and found free of knob lag, because the pitfall is specific to
   **Direct-row** constructions.
- `[D]` `CLAUDE.md:116`, 2026-10-25, fw 10.81, verbatim: "Gotcha: a Continuous/Single Cycle SG
   needs its T column (e.g. Direct+ -> SG n T = W) or it never starts." `[C]` 530 of the 539
   presets that wire an SG column feed its trigger (`census.json:techniques`).
- `[I]` Note the citation correction: `modules/index.md` cross-module pattern 6 attributes that
   gotcha to `CLAUDE.md:91`; the line is **116**. The inference is a transcription slip, not a
   disagreement - the quoted text is identical.

**Step 5 - the slight pitch LFO, as one shared shape generator.**

```
set_shape_generator(sg=1, type_name="Continuous Cycle")
set_matrix_point(row=13, col=51, value="5")      # SG 1 F = 5 Hz
set_matrix_point(row=13, col=52, value="W")      # SG 1 T = gated note, so it restarts per note
set_matrix_point(row=14, col=13, value="N")      # Direct + (2) -> Osc 1 F : ADDS to the pitch
set_matrix_point(row=14, col=16, value="N")      # Direct + (2) -> Osc 2 F : the SAME letter
set_matrix_point(row=14, col=19, value="N")      # Direct + (2) -> Osc 3 F : the SAME letter
set_formula(row=14, col=13, component="W", mode="SG1", sg_shape="Sine",
            value=0.18, magnitude=0.01)          # +-1.8 Hz, about +-7 cents at A4
```

- `[D]` `RECIPES.md:35-38`, 2026-10-25, fw 10.81 is the whole recipe: "SG1: Continuous Cycle,
   F = .8 Hz (slow) to 5 Hz (classic vibrato), T = W" / "New formula C: W mode SG1, sg_shape Sine,
   value 0.18, magnitude 0.01. That is +-1.8 Hz, about +-7 cents at A4" / "`Direct + (2) ->
   Osc n F = C` for each oscillator." Seven cents is "slight".
- `[D]` `RECIPES.md:18-19 (moved to pitfalls.md)`, 2026-10-25, fw 10.81 is why it must be **one** shape generator read by
   **one** letter on three columns and not three shape generators: several continuous SGs on
   different oscillator `F` columns make the panel knobs unusable, while one shared SG does not.
   `[D]` `RECIPES.md:29-30 (moved to pitfalls.md)`, 2026-10-25, fw 10.81 states it as rule 1, "One shared drift/vibrato
   LFO, not one per oscillator."
- `[C]` If the three oscillators should drift against each other rather than together, the
   factory's answer is still one SG: `patterns.md` P5b reads four `sg_phase` offsets off one SG in
   `BiqMouth - Basic` (`A`..`D`, phases Off / 0.25 / 0.5 / 0.75). `[I]` That costs three extra
   letters instead of three extra shape generators, and the inference from `RECIPES.md:18-19 (moved to pitfalls.md)` is
   that only the latter is expensive.
- `[D]` `RECIPES.md:39-40`, 2026-10-25, fw 10.81 is the caveat to tell the user: depth is absolute
   Hz, so the vibrato is deeper in cents on low notes than on high ones, and pitch-proportional
   depth costs knob responsiveness.

**Step 6 - voices and the budget.**

```
set_polyphony(voices=6, expanded=True, double_computation_rate=False)
set_bend_range(2)
get_status()
```

- `[D]` `CLAUDE.md:153-154`, 2026-10-25, fw 10.81: base 6 with "+" and double computation rate
   **off** is the configuration that took a heavy patch from 100% DSP and 3 actual voices to no
   lag. `[I]` The inference recorded in `patterns.md` section 2.3 is that double rate is a
   frequency-response setting and never a performance fix.
- `[D]` `RECIPES.md:127`, 2026-10-25, fw 10.81 is the one comparable measurement: "DSP 72% at 7+
   voices with FM pair + BiqBank + SGs". `[I]` This patch has no bank at all, so the inference is
   that 6 to 8 voices should fit - but `get_status` is the measurement, not the inference.
- `[G]` `docs/HakenMidi.h:1357` caps `set_polyphony` at 1..8; `[C]` 24 factory presets of 668
   store 10, 12 or 14 and cannot be reproduced at their shipped voice count (`patterns.md`
   section 2.3).

**Step 7 - store it.** Identical to plan 1 step 5: name only, `save_to_user_slot(..., confirm=True)`,
then `list_user_presets()` to compare the slot's name against the edit slot's.

- `[D]` `CLAUDE.md:123-125`, 2026-10-25, fw 10.81: a user store is `cc0=0` plus `cc32`/`cc112`.
   **Never `cc0=127`** - that is the system-slot path used by firmware updates.

### 2.4 The release problem, stated plainly

**"Its own envelope" gets an attack and a shape, and NO RELEASE.** Step 4's Hann
one-shot rises and falls over roughly half a second; what it cannot do is continue after the key
comes up.

- `[G]` The firmware's documentation says there is no envelope generator to ask for:
   `docs/EaganMatrix Preset Cookbook.txt:3069-3072`, verbatim: "Note: There is no generic ADSR
   envelope control for EaganMatrix. It all must be programmed and to large extent, your finger
   envelope controls the dynamic profile of most presets."
- `[G]` Release specifically is **persistence**, which the header names as formula id 63:
   `docs/HakenMidi.h:1323`, header comment: "idPersist = 63".
- `[G]` What persistence does, from `docs/EaganMatrix Preset Cookbook.txt:1026-1029`, verbatim:
   "Use Persistence. Persistence will delay the time a function takes to end, which often results
   in creating a sustain if for example you put it on an output function."
- `[G]` **Id 63 is decode-only.** `eagan_mcp/formula.py:121` holds
   `PERSISTENCE_IDS = (63, 81)` and `eagan_mcp/formula.py:181` keeps them in `DECODE_ONLY_IDS`, so
   a captured preset's persistence is **readable** and no typed tool writes it;
   `eagan_mcp/formula.py` `encode_changes` says so in the codec's own docstring: "nothing here writes them".
- `[I]` **A skill that promises this patch a "release" is over-claiming.** The inference is direct
   from the two facts above: the only mechanism the firmware names for release is one the MCP
   cannot write, so any release in this patch is a substitute with different behaviour, and saying
   otherwise would leave the operator listening for something that is not there.

**THE SUBSTITUTE USED: a second Single Cycle shape generator (SG 4) ramping down on the Master
output, release-triggered with `0.5` on `Direct +` against `W` on `Direct -` so that it fires when
the key is let go - and NOT the Recirculator tail.**

Why that one, in two reasons:

- `[I]` **The Recirculator tail cannot be built by these tools at all.** No tool writes the
   Recirculator's configuration (`model.md` section 8; `patterns.md` section 2.5), so choosing it
   would mean inheriting whatever decay and mix the loaded preset happens to carry - and plan 2
   starts from an unknown edit slot (section 2.2). The inference is that an unwritable control
   cannot be part of a plan, only part of an accident.
- `[G]` **The ramp-down is the documented substitute**, named by the firmware's own Cookbook:
   `docs/EaganMatrix Preset Cookbook.txt:1005-1013`, verbatim: "Use a slow Ramping Function on
   Output. ... this example that uses a very single cycle slow ramp down (SG4 F=0.01) of 100
   seconds on the output. When Z is released that ramp down of output will continue until value
   reaches zero."

```
set_shape_generator(sg=4, type_name="Single Cycle")
set_matrix_point(row=13, col=58, value="0.5")    # SG 4 T <- Direct +  = 0.5
set_matrix_point(row=15, col=58, value="W")      # SG 4 T <- Direct -  = gate
                                                 #   trigger = 0.5 - gate -> fires at NOTE-OFF
set_matrix_point(row=13, col=57, value=".2")     # SG 4 F = 0.2 Hz -> a 5 s ramp
set_formula(row=1, col=0, component="W", mode="SG4", sg_shape="Ramp Down",
            value=0.3, magnitude=1, modifier="x Macro", macro="i",
            operator="(W + X + Y) x Z")          # replaces step 3's constant W in letter L
```

- `[C]` The release trigger is a factory idiom, not an invention: 44 `SG n T` cells across the 668
   presets sit on the `Direct -` row, and `The Long Goodbye` builds exactly this -
   `col 54 <- Direct + = 0.5, Direct - = W` (`patterns.md` P1, release-triggered variant).
- `[C]` It is the nearest thing to a release the matrix offers without persistence, and it is
   corpus-attested only - **nobody on this project has played it** (`patterns.md` P1; `[C]` can
   never upgrade to `[D]`).

Three things about this substitute that a plan must not hide:

1. `[G]` **The Cookbook's own version starts at note-on, not note-off.** Its SG 4 runs for 100
   seconds precisely so the in-note droop is inaudible, and the sentence "When Z is released that
   ramp down of output will continue" describes a ramp that was already running
   (`docs/EaganMatrix Preset Cookbook.txt:1009-1013`). `[I]` The inference is the trade-off this
   plan cannot escape: a note-on ramp slow enough not to fade the held note is too slow to be a
   release, and one fast enough to be a release fades the held note. The `0.5 - W` trigger above
   is what breaks the trade-off, and it is the part the Cookbook does not cover.
2. `[I]` **Whether the voice survives note-off at all is unmeasured.** A ramp on the output can
   only be heard if the Module is still computing that voice after the key comes up, and nothing
   in `CLAUDE.md`, `RECIPES.md` or the guides states how long it does. The inference is that at
   base polyphony 6 with "+" on, voice stealing by oldest note `[G]`
   `docs/ContinuumUserGuide.txt:5393-5394` will cut a 5 s tail during ordinary playing - so the
   tail is a decoration, not a dependable release.
3. `[I]` **It is a level ramp, not an envelope release**, so it fades the whole voice uniformly
   including the FM brightness, rather than letting the timbre decay the way a real release stage
   would. The inference is from where it sits: inside letter `L` on the Master columns, downstream
   of everything.

`[G]` Two further documented routes were rejected and are recorded so the choice can be
re-examined: the sustain pedal on CC 64 and reducing a filter's bandwidth
(`docs/EaganMatrix Preset Cookbook.txt:1003-1044`). `[I]` The inference is that the first is a
player action rather than a patch property, and the second needs a filter this patch does not
have - adding one to get a release would change the requested sound.

### 2.5 Plan 2 - what is unresolved

**PLAN 2 OPEN PART 1 - there is no release, and the SUBSTITUTE above has never been heard.**
(Not to be confused with the negative-height question, which was separate and is now closed
- see Plan 1 open part 1. This one is still open: the ramp-down release substitute is
corpus-only.) When Plan 2 was actually built on the device on 2026-10-28, the builder
declined this substitute for exactly the reasons listed below and shipped attack-and-shape
with no release - notes stop at key-up. That is the honest reading of the request.
Section 2.4 is the full statement; it is repeated in this list so that a reader skimming the
unresolved section does not miss it.

- `[G]` Persistence (id 63) is the mechanism and is decode-only `[G]` `eagan_mcp/formula.py:181`.
   Writing it is the open tool item; until it exists, every release in this project is a
   substitute.

**PLAN 2 OPEN PART 2 - the third oscillator is not planned anywhere in the findings.**

- `[D]` What the project has actually played is a **two**-oscillator FM pair: `CLAUDE.md:141-142`,
   2026-10-25, fw 10.81, "FM Wheel Vibrato", Osc 3 -> Osc 1 F. `[C]` Nothing in `patterns.md`,
   `RECIPES.md` or `CLAUDE.md` describes a three-oscillator layout.
- `[I]` **So the request is ambiguous and this plan resolves it by choice, not by evidence.** "FM
   from osc 3 to osc 1" makes osc 3 a modulator, and a modulator must not reach the Master
   (`RECIPES.md:43`) - which leaves two audible oscillators out of three. The inference is that
   "3-osc" either means three slots of which one is a modulator, which is what section 2.3 builds,
   or three *audible* oscillators plus a fourth as modulator, which would need a fourth
   `set_osc_type` and a fourth pitch cell. **Ask the user which.**
- `[I]` **Osc 2's role is entirely unspecified** - the request says nothing about what the second
   audible oscillator contributes. Section 2.3 leaves it in unison with osc 1, which is the
   neutral choice and also an audible one, since two identical DSF oscillators at the same pitch
   sum to 6 dB rather than thickening. The inference is that this needs either a detune
   (`patterns.md` P5c, small constants on `Direct -`) or an octave
   (`patterns.md` P7, a constant on `Direct x`) to earn its slot - and the request does not say
   which.

**PLAN 2 OPEN PART 3 - formula-letter allocation is not solved.**

- `[C]` The pool is **44** letters, `A`..`V` and `A'`..`V'` `[G]` `docs/HakenMidi.h:749-754`, and
   the honest working rule is *44 available, `A`..`V` preferred*, because the Cookbook's worked
   examples never leave `A`..`V` (`model.md` section 4).
- `[D]` `CLAUDE.md:93`, 2026-10-25, fw 10.81: "Formula letters are shared: editing a cell's
   formula changes all cells using that letter." `[D]` `CLAUDE.md:94`, 2026-10-25, fw 10.81: "The
   Module omits matrix cells whose formula is all zero from the matrix dump" - so `get_matrix`
   **under-reports** which letters are taken.
- `[I]` The three letters this plan names, `L`, `M` and `N`, are therefore **placeholders, not
   choices**: no tool allocates a letter, and the inference from the two facts above is that an
   unchecked collision silently rewrites another part of the patch. Read `get_matrix` first, pick
   from what is free, and verify after writing. Plan 1 does not have this problem only because its
   template's letter usage ships in `factory_catalog.json`.

**PLAN 2 OPEN PART 4 - three smaller unknowns, each of which can be listened for.**

- `[I]` **The FM ratio is a guess.** Section 2.3 writes `2` on `Direct x` into `Osc 3 F` because
   `FM Bells` does (`factory_catalog.json`, `wiring`), and the inference is only that a simple
   integer ratio gives a harmonic result; which ratio suits this patch is a listening question.
- `[D]` **The FM depth is in absolute kHz**, so brightness changes across the keyboard
   (`RECIPES.md:44`, `:50`, 2026-10-25, fw 10.81). `[I]` The inference is that the patch will sound
   right in one register and wrong in another until someone plays the range; pitch-proportional
   depth needs `X` in the formula and is listed as untested in `RECIPES.md:156-157`.
- `[G]` **Macros i..iv are CV offsets on this device**, not values
   (`docs/HakenMidi.h:533-535`), so the level macro in step 3 and the release macro in section 2.4
   may not behave as a plain MIDI CC would. `[I]` The inference is that this is unmeasured on the
   Module and applies to every macro in both plans.

---

## What both plans share

- `[D]` **Build around Y, because Y is the only continuous input a plain keyboard can move
   mid-note**: `RECIPES.md:38-39 (moved to pitfalls.md)`, 2026-10-25, fw 10.81, "Mod wheel: CC 1 arrives as Y. Build the
   patch to use Y. Do not suggest remapping the user's keyboard as the default fix." The keyboard
   contract behind it, including why Z is frozen at note-on, is `model.md` section 7.
- `[D]` **Verify a write with a separate read, never with the echo**: the echo right after a
   write is a partial matrix that can stop before the changed cell (`CLAUDE.md:114-115`,
   2026-10-25, fw 10.81; `eagan_mcp/server.py:262-264`).
- `[I]` **Disable a cell, never clear it.** Removing a letter from the matrix deletes the formula
   on save, because the preset stores only non-blank cells; the inference is in `model.md`
   section 3. Set the heights to zero instead.
- `[C]` **A matrix cell holds a whole `1`..`9` or a `.nnnn` decimal and nothing else**, so a value
   like "1.25" has no cell encoding - build it across two `Direct` rows or inside a formula's `W`
   constant (`model.md` section 3, from `docs/EaganMatrix Preset Cookbook.txt:221-224`).
- `[D]` **Both plans write to the edit slot only until the user confirms a store**, and a store
   goes to a USER slot through `cc0=0` plus `cc32`/`cc112` - never the `cc0=127` system path
   (`CLAUDE.md:123-125`, 2026-10-25, fw 10.81).
- `[I]` **Neither plan has been played, and both are therefore proposals.** The inference from
   `.maister/docs/standards/testing/test-writing.md` is that this file is not a peer of
   `RECIPES.md`: a construction here earns a `RECIPES.md` entry only after someone hears it, one
   change at a time, with a single yes-or-no question after each.

## Where to go next

- `[I]` `patterns.md` for the construction each step lifts, by number - P1, P5b, P5c, P6, P7, P8,
   P11 and P12 are the ones these two plans use.
- `[I]` `modules/biqmouth.md` for plan 1's column map, its trap columns and the resolved `sB`
   arithmetic; `modules/wavebank.md` for the `F1`..`F5` cluster; `modules/oscillator-slots.md` for
   plan 2's slot types.
- `[I]` `model.md` for the voice model, the keyboard contract and the honest table of what the
   MCP cannot do.
- `[I]` `modules/index.md` for the six cross-module patterns both plans cite by number.
