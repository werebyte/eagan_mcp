---
name: eagan-patch-design
description: Builds a patch on the Haken EaganMatrix Module from a plain-words sound description, routing every device fact through the eagan_mcp knowledge, recipe and factory-catalog tools. Use when the user describes a timbre, instrument, character or modulation they want on the EaganMatrix Module and asks for it to be designed, built or patched.
---

# EaganMatrix Patch Design

This skill is the procedure for turning a plain-words sound request into matrix cells and
formulas on the EaganMatrix Module, and it deliberately holds no device facts of its own. Column
maps, neutral values, module behaviour, wire details and corpus figures all live in the shipped
knowledge base and the factory catalog, reached through `get_knowledge`, `get_recipes` and
`search_factory_presets`. Read them from the tools on every build, because the tools are kept
current and a remembered fact is not.

## Workflow

1. **Orient before deciding anything** - call `get_knowledge()` with no argument. It returns the
   topic list and the whole module index, which names the shared module facts and the Master
   chain, so one call tells you what is knowable.
2. **Decompose the request into layers** - name the excitation, the resonator or filter, the
   modulation and the output stage separately. A plain-words request almost never maps onto one
   module, and a decomposition is what makes the rest of this workflow searchable.
3. **Look for a template before building from nothing** - `search_factory_presets` with the
   user's own words as `text`, or with a `module` or `technique` filter. Starting from a factory
   preset is cheaper and safer than an empty matrix. Use the `eagan-factory-mining` skill when
   the search needs more than one pass.
4. **Read the two assembled plans** - `get_knowledge("worked-examples")` carries two plain-words
   requests built end to end, with their unresolved parts stated. Follow their shape rather than
   re-deriving it, and read what each one says it could not settle.
5. **Read the card for every module you will touch** - `get_knowledge("modules/<card>")`. The
   card owns that module's column meanings, neutral values and traps. Reading the matrix is not
   a substitute: two modules whose columns look alike can behave differently.
6. **Read the pattern rather than your memory of it** - `get_knowledge("patterns", query="...")`
   for the construction you need, such as an envelope, a detune spread, cross-modulation or a
   feedback loop. The patterns chapter also records what the corpus does not support.
7. **Check the tested recipe book** - `get_recipes()` returns the recipes verified by ear on this
   Module, each with the pitfalls that belong to its own steps. A tested recipe outranks a
   pattern you assembled yourself.
8. **Confirm the template by capture, never by the printed list** - `load_and_capture_preset`
   returns the preset's actual name, and the printed index is known to be off by one in places.
   Correct the index from what came back before building on it.
9. **Pick formula letters that are free** - read `get_matrix` first and apply the letter rule in
   Operating Rules below. A reused letter silently rewrites another cell.
10. **Build one cell at a time and verify each** - but the two writes report differently.
    `set_matrix_point` returns `device_value` and `verified` from a separate read; treat
    `verified` false or unknown as a stop, not as noise. `set_formula` returns NO
    `verified` field: check its `summary_after`, which is the formula as the device reports
    it back, and re-read with `get_formula` if you need more. An `applied: true` with an
    empty `changed_ids` means the formula was ALREADY what you asked for, not that nothing
    landed. Either way, do not batch several unverified writes.
11. **Re-check the budget after every structural change** - `get_status`, then the fixes in
    Operating Rules below.
12. **Listen-test one change at a time** - message the user before a long listen so they can
    play during it, make exactly one change, then ask one yes/no question about it. Two changes
    at once make the answer useless.
13. **Name and store only when asked** - `set_preset_name` with the name argument only, then
    `save_to_user_slot` with the slot the user named and an explicit confirmation, verified
    through `list_user_presets`.

## The Five Safety Rules

These bind every session, in this skill and in the other two.

1. **Negative formula heights are safe to plan.** The split sign encoding is fixed and
   `set_formula` writes proceed, so design with negative heights freely. State the caveat once
   to the user and afterwards surface the `warning` the tool returns rather than repeating it;
   this is not a refusal. **H6:** the fix repairs what is written from now on and does not repair
   heights already stored in user slots 4 and 5, which must be rewritten on the device before
   either preset is trusted.
2. **The keyboard contract decides what can drive the patch.** On a plain MIDI keyboard on
   channel 1: Z is frozen at note-on and does not move for the life of the note; pitch bend is
   global and its bend range defaults to the maximum, +-96 semitones, unless the patch sets it
   explicitly; Y is global, arrives on the mod wheel, and may not fall at release, so a Y-scaled
   output can leave notes that never end; and Y and Z must stay pinned to MPE/MPE+ or channel 1
   collapses to mono. Read it in full with `get_knowledge("model", query="keyboard contract")`
   before choosing a modulation source.
3. **Blank is not neutral, and it is not neutral in one way.** The mechanism has two halves: a
   module with a Properties panel reads a matrix value as an offset to its panel value, so blank
   means no offset rather than zero; a module without a panel reads blank as that column's own
   zero, and zero means a different thing in every column. The question before leaving a column
   empty is therefore never "is blank safe" but "what is this column's neutral value", and that
   is answered per column by `get_knowledge("modules/<card>")`. Never carry a neutral value from
   one module to another.
4. **The loudness rules N1-N5, and a kill switch you can reach.** Read
   `get_knowledge("model", query="N1")` for the five rules in full and `get_knowledge("pitfalls")`
   section 1 for the safe starting amplitudes before the first output write, and tell the user to
   turn the gain down and take the headphones off. Prefer N5's macro form - a free macro
   multiplying an output column down to zero - because it is an ordinary verified matrix write
   that restores exactly. N5's CC form has **no typed tool**: it is a `send_raw` of ch1 cc18 with
   nothing validating or verifying it, and you must say that plainly before using it. The
   conflict there is already resolved: the guide calls that CC a mute with 1 = Unmute, the header
   makes it the post-Master output level, and the header wins, so 1 is 1/127 of full level and
   not unmute. `get_knowledge("model")` carries both sides; reference it rather than re-arguing
   it.
5. **Know the holes before promising anything.** No typed tool writes an envelope release
   (release is persistence), ancillary anything, blend or a secondary formula, the mute bit, or
   bank properties; and a matrix cell holds only a whole 1..9 or a .nnnn decimal, so "1.25" is
   unrepresentable and must be decomposed across cells. `get_knowledge("model", query="cannot")`
   is the list. The two escape hatches, `write_formula_raw` and `send_raw`, are untyped and
   unverified; name them as such whenever you reach for one.

## Operating Rules

- **Writes go to the edit slot only.** Everything lands in the edit buffer. A store needs the
  user to name the slot and an explicit confirmation, and is verified by comparing that slot's
  name against the current edit-slot name through the read-only `list_user_presets` - never by
  loading the slot, which destroys the unsaved edit, and never from the save echo, which varies.
  **H2:** never send the system-slot store path, `ch16 cc0=127`. **H7:** never pass
  `set_preset_name`'s `description` argument, because that stream's identity is unresolved and
  writing it may destroy a preset's panel macro labels.
- **Pick a formula letter that is genuinely free.** Letters are shared device-wide, so redefining
  one rewrites every cell using it. The pool is 44 - A..V plus A'..V' - with A..V preferred.
  Check `get_matrix` first and treat the dump as a lower bound: the Module omits cells whose
  formula is all zero, so a letter missing from the dump may still be taken.
- **Check the budget after a substantial change.** Call `get_status`, then apply the documented
  fixes in their documented order, which `get_knowledge("pitfalls", query="fix order")` gives.
  **Never turn Double Computation Rate on as a performance fix:** it is a frequency-response
  setting, it was measured cutting a patch to three voices at a saturated DSP budget, and the
  useful move is to check whether it is already on.
- **Disable, never clear.** A formula removed from the matrix is deleted on save. Park a formula
  you want to keep on a cell that reaches no output and disable it there.
- **User slots 1 to 5 are in use.** Never offer one of them as a free slot.
- **`tools_spec.md` specifies tools that do not exist yet.** Never promise one of its T<n> ranks
  as a shipped capability.

If a fact you need is not in this skill, that is by design - call `get_knowledge()` for it, and
if the knowledge base is silent too, say so plainly instead of guessing.
