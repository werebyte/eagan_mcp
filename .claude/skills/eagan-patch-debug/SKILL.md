---
name: eagan-patch-debug
description: Diagnoses an EaganMatrix Module patch that sounds wrong by working the documented pitfall order, checking the setup and the DSP budget before any matrix rewrite. Use when the user reports that a patch on the EaganMatrix Module sounds wrong, lags, breaks up, drops voices, is silent, is too loud, or stopped behaving after an edit.
argument-hint: "[what sounds wrong]"
---

# EaganMatrix Patch Debugging

This skill is the diagnostic order for a patch on the EaganMatrix Module that is not doing what
it should, and it holds no device facts of its own: the symptom-to-cause knowledge lives in the
shipped knowledge base and the factory catalog, reached through `get_knowledge`, `get_recipes`
and `search_factory_presets`. The order matters more than the cleverness, because the cheapest
causes are also the commonest and a matrix rewrite destroys the evidence for the others.

## Workflow

1. **Take the symptom in the user's own words** - lag, break-up, silence, too loud, a note that
   never ends, pitch stepping, a tail that gets cut off. Do not translate it into a hypothesis
   yet; the same words point at different causes depending on what changed last.
2. **Read the pitfall order before forming a theory** - `get_knowledge("pitfalls")` is organised
   in the order a build can hit its failures, and that order is the diagnostic order. Work it as
   given rather than jumping to the part of the patch you happen to find interesting.
3. **Check the setup and the DSP budget before touching the matrix** - `get_status` reports the
   DSP usage and the voice count the Module is actually running, and `get_setup` says whether
   Double Computation Rate is on. A patch running fewer voices than its
   polyphony asks for is over budget, not miswired. Never turn Double Computation Rate on as a
   performance fix: it is a frequency-response setting, it was measured cutting a patch to three
   voices at a saturated DSP budget, and finding it already on is often the whole diagnosis.
4. **Apply the documented fixes in their documented order** - the order is given by
   `get_knowledge("pitfalls", query="fix order")`. Work down that list, and do not improvise a
   different one.
5. **Rule out a silent patch being routed away from the engine** - a preset can be routed so
   that nothing reaches the internal sound engine, which looks exactly like a broken matrix.
   `get_knowledge("pitfalls", query="silent")` has the check.
6. **Rule out the keyboard contract before blaming the patch** - a note that never ends, a
   velocity that does nothing, a bend that goes nowhere and a sudden drop to one voice are all
   contract symptoms, not matrix bugs. Safety rule 2 below has the six elements.
7. **Read the patch without changing it** - `get_matrix` for the cells, `get_formula` for the
   letters behind them, `get_setup` for what the matrix values are offsets to. Retry an empty
   read with a longer listen window before concluding anything; the first read after a load can
   come back empty.
8. **Read the card for each module in the signal path** - `get_knowledge("modules/<card>")`. A
   column that looks wrong is often a column whose neutral value you assumed from another module;
   safety rule 3 below is the mechanism.
9. **Remove one construction at a time, and disable rather than clear** - take out a single
   construction, listen, put it back. A formula removed from the matrix is deleted on save, so
   park it on a cell that reaches no output and disable it there instead of clearing the cell.
10. **Ask the user to test very fast knob turns** - encoder and macro lag shows up under fast
    turns and not under slow ones, so a patch that feels fine at a normal pace can still be the
    one at fault. Message the user before a long listen, make one change, ask one yes/no
    question.
11. **Re-check the budget and only then save** - `get_status` after the fix, then name and store
    only when the user asks, through `set_preset_name` and `save_to_user_slot`, verified with
    `list_user_presets`.

## The Five Safety Rules

These bind every session, in this skill and in the other two.

1. **Negative formula heights are safe to plan.** The split sign encoding is fixed and
   `set_formula` writes proceed, so a negative height is not itself a bug to hunt. State the
   caveat once to the user and afterwards surface the `warning` the tool returns rather than
   repeating it; this is not a refusal. **H6:** the fix repairs what is written from now on and
   does not repair heights already stored in user slots 4 and 5, which must be rewritten on the
   device before either preset is trusted - so a wrong-sounding height in one of those two slots
   is an expected finding, not a new fault.
2. **The keyboard contract decides what can drive the patch.** On a plain MIDI keyboard on
   channel 1: Z is frozen at note-on and does not move for the life of the note; pitch bend is
   global and its bend range defaults to the maximum, +-96 semitones, unless the patch sets it
   explicitly; Y is global, arrives on the mod wheel, and may not fall at release, so a Y-scaled
   output can leave notes that never end; and Y and Z must stay pinned to MPE/MPE+ or channel 1
   collapses to mono. Read it in full with `get_knowledge("model", query="keyboard contract")`
   before blaming a cell.
3. **Blank is not neutral, and it is not neutral in one way.** The mechanism has two halves: a
   module with a Properties panel reads a matrix value as an offset to its panel value, so blank
   means no offset rather than zero; a module without a panel reads blank as that column's own
   zero, and zero means a different thing in every column. The question about an empty column is
   therefore never "is blank safe" but "what is this column's neutral value", and that is
   answered per column by `get_knowledge("modules/<card>")`. Never carry a neutral value from one
   module to another.
4. **The loudness rules N1-N5, and a kill switch you can reach.** Read
   `get_knowledge("model", query="N1")` for the five rules in full and `get_knowledge("pitfalls")`
   section 1 for the safe starting amplitudes before changing any output level, and tell the user
   to turn the gain down and take the headphones off - a debugging session changes levels more
   often than a build does. Prefer N5's macro form - a free macro multiplying an output column
   down to zero - because it is an ordinary verified matrix write that restores exactly. N5's CC
   form has **no typed tool**: it is a `send_raw` of ch1 cc18 with nothing validating or
   verifying it, and you must say that plainly before using it. The conflict there is already
   resolved: the guide calls that CC a mute with 1 = Unmute, the header makes it the post-Master
   output level, and the header wins, so 1 is 1/127 of full level and not unmute.
   `get_knowledge("model")` carries both sides; reference it rather than re-arguing it.
5. **Know the holes before promising a fix.** No typed tool writes an envelope release
   (release is persistence), ancillary anything, blend or a secondary formula, the mute bit, or
   bank properties; and a matrix cell holds only a whole 1..9 or a .nnnn decimal, so "1.25" is
   unrepresentable and must be decomposed across cells.
   `get_knowledge("model", query="cannot")` is the list, and it is also the list of symptoms this
   MCP cannot repair. The two escape hatches, `write_formula_raw` and `send_raw`, are untyped and
   unverified; name them as such whenever you reach for one.

## Operating Rules

- **Writes go to the edit slot only.** Everything lands in the edit buffer. A store needs the
  user to name the slot and an explicit confirmation, and is verified by comparing that slot's
  name against the current edit-slot name through the read-only `list_user_presets` - never by
  loading the slot, which destroys the unsaved edit and with it the patch you were debugging.
  **H2:** never send the system-slot store path, `ch16 cc0=127`. **H7:** never pass
  `set_preset_name`'s `description` argument, because that stream's identity is unresolved and
  writing it may destroy a preset's panel macro labels.
- **Pick a formula letter that is genuinely free.** Letters are shared device-wide, so redefining
  one rewrites every cell using it - which is itself a common cause of "I changed one thing and
  something else broke". The pool is 44 - A..V plus A'..V' - with A..V preferred. Check
  `get_matrix` first and treat the dump as a lower bound: the Module omits cells whose formula is
  all zero, so a letter missing from the dump may still be taken.
- **Check the budget after a substantial change.** Call `get_status`, then apply the documented
  fixes in their documented order, which `get_knowledge("pitfalls", query="fix order")` gives.
  **Never turn Double Computation Rate on as a performance fix:** it is a frequency-response
  setting and was measured cutting a patch to three voices at a saturated DSP budget.
- **Disable, never clear.** A formula removed from the matrix is deleted on save. Park a formula
  you want to keep on a cell that reaches no output and disable it there.
- **User slots 1 to 5 are in use.** Never offer one of them as a free slot.
- **`tools_spec.md` specifies tools that do not exist yet.** Never promise one of its T<n> ranks
  as a shipped capability.

If a cause you suspect is not described in this skill, that is by design - call
`get_knowledge("pitfalls")` or the module card for it, and if the knowledge base is silent too,
say so plainly instead of guessing.
