---
name: eagan-factory-mining
description: Mines the shipped Haken factory preset catalog for presets that already do a named technique, module or sound, and returns the best candidate as a build template. Use when the user asks which EaganMatrix Module presets do X, wants a worked example of a technique or module, or needs a starting preset before a patch is built.
argument-hint: "[technique, module or sound]"
---

# EaganMatrix Factory Mining

This skill is the procedure for finding a factory preset that already solves the user's problem,
so a patch starts from working wiring instead of an empty matrix. It holds no catalog facts of
its own: the preset records, their filter vocabularies and their counts all come from
`search_factory_presets`, and the device knowledge behind them from `get_knowledge` and
`get_recipes`. The tool has two exclusive modes, and the whole workflow is getting from the
first to the second.

## Workflow

1. **Turn the request into filter terms** - separate the user's words into a plain-words phrase
   for `text`, a module name, a technique tag, a category and a bank. Decide which of them you
   actually believe; a wrong filter silently narrows the result to nothing.
2. **Filter to a shortlist first** - call `search_factory_presets` with any combination of the
   search arguments, which combine with AND. It returns summaries only, never full records.
3. **Read `count` and `truncated`, not the page length** - `count` is the total number of
   matches and `truncated` says the page left some out. Reporting the page length as the number
   of matching presets is the easiest mistake to make here.
4. **Let the tool teach you its vocabulary** - an unknown `category`, `module` or `technique`
   raises an error that lists every accepted value. Read that list rather than guessing a
   spelling, and do not hard-code one into your answer.
5. **Widen and narrow deliberately** - drop one filter at a time when nothing matches, and add
   one at a time when too much does. Plain-words `text` searches the preset names and their long
   descriptions, so it reaches requests that no tag covers.
6. **Prefer a candidate that carries wiring** - each summary says whether that preset has a
   decoded wiring block. A candidate with wiring is a readable template; one without is only a
   name and a module list.
7. **Pull the full record for the finalists** - call `search_factory_presets` again with the
   exact preset name and no filters, which is the only route to the full record and its wiring.
   Name plus a filter is rejected, so search first and look up second.
8. **Confirm the preset by capture, never by the printed list** - `load_and_capture_preset`
   returns the preset's actual name, and the printed index is known to be off by one in places.
   Correct the index from what came back before building on it.
9. **Read the card for every module the record names** - `get_knowledge("modules/<card>")`
   explains what the wiring is doing. A wiring block without its cards is a list of numbers.
10. **Hand it over as a template, not as an answer** - say what the preset does, what in it
    matches the request and what does not, and then continue in the `eagan-patch-design` skill.

## The Known Limit

The catalog carries no join to the cookbook: there is no page or line reference from a preset to
where it is written up, so "where is this preset explained" is **not answerable from this tool**.
Say so rather than inventing a citation. Search the documentation separately with `search_docs`,
and treat any answer you get that way as a separate finding about the documentation rather than
as a field of the preset record. The join is specified in `tools_spec.md` as a tool that does not
exist yet, so it must never be offered as a shipped capability.

## The Five Safety Rules

These bind every session, in this skill and in the other two. Mining is read-only, but it ends
by handing a template to someone who will write.

1. **Negative formula heights are safe to plan.** The split sign encoding is fixed and
   `set_formula` writes proceed, so a factory wiring block with a negative height can be copied.
   State the caveat once to the user and afterwards surface the `warning` the tool returns rather
   than repeating it; this is not a refusal. **H6:** the fix repairs what is written from now on
   and does not repair heights already stored in user slots 4 and 5, which must be rewritten on
   the device before either preset is trusted.
2. **The keyboard contract decides what can drive the patch.** On a plain MIDI keyboard on
   channel 1: Z is frozen at note-on and does not move for the life of the note; pitch bend is
   global and its bend range defaults to the maximum, +-96 semitones, unless the patch sets it
   explicitly; Y is global, arrives on the mod wheel, and may not fall at release, so a Y-scaled
   output can leave notes that never end; and Y and Z must stay pinned to MPE/MPE+ or channel 1
   collapses to mono. Read it in full with `get_knowledge("model", query="keyboard contract")`
   before recommending a preset whose expression comes from an input this rig does not have.
3. **Blank is not neutral, and it is not neutral in one way.** The mechanism has two halves: a
   module with a Properties panel reads a matrix value as an offset to its panel value, so blank
   means no offset rather than zero; a module without a panel reads blank as that column's own
   zero, and zero means a different thing in every column. So a factory wiring block is not the
   whole preset: the columns it leaves out still have values. Ask per column with
   `get_knowledge("modules/<card>")`, and never carry a neutral value from one module to another.
4. **The loudness rules N1-N5, and a kill switch you can reach.** Read
   `get_knowledge("model", query="N1")` for the five rules in full and `get_knowledge("pitfalls")`
   section 1 for the safe starting amplitudes before copying any output level out of a factory
   preset, and tell the user to turn the gain down and take the headphones off. Prefer N5's macro
   form - a free macro multiplying an output column down to zero - because it is an ordinary
   verified matrix write that restores exactly. N5's CC form has **no typed tool**: it is a
   `send_raw` of ch1 cc18 with nothing validating or verifying it, and you must say that plainly
   before using it. The conflict there is already resolved: the guide calls that CC a mute with
   1 = Unmute, the header makes it the post-Master output level, and the header wins, so 1 is
   1/127 of full level and not unmute. `get_knowledge("model")` carries both sides; reference it
   rather than re-arguing it.
5. **Know the holes before promising a template will transfer.** No typed tool writes an
   envelope release (release is persistence), ancillary anything, blend or a secondary formula,
   the mute bit, or bank properties; and a matrix cell holds only a whole 1..9 or a .nnnn
   decimal, so "1.25" is unrepresentable and must be decomposed across cells.
   `get_knowledge("model", query="cannot")` is the list. A factory preset may well use a feature
   from that list, which makes it a thing to read rather than a thing to reproduce. The two
   escape hatches, `write_formula_raw` and `send_raw`, are untyped and unverified; name them as
   such whenever you reach for one.

## Operating Rules

- **Writes go to the edit slot only.** Everything lands in the edit buffer. A store needs the
  user to name the slot and an explicit confirmation, and is verified by comparing that slot's
  name against the current edit-slot name through the read-only `list_user_presets` - never by
  loading the slot, which destroys the unsaved edit. **H2:** never send the system-slot store
  path, `ch16 cc0=127`. **H7:** never pass `set_preset_name`'s `description` argument, because
  that stream's identity is unresolved and writing it may destroy a preset's panel macro labels.
- **Pick a formula letter that is genuinely free.** Letters are shared device-wide, so redefining
  one rewrites every cell using it, and a factory letter copied into a live patch collides with
  whatever already holds it. The pool is 44 - A..V plus A'..V' - with A..V preferred. Check
  `get_matrix` first and treat the dump as a lower bound: the Module omits cells whose formula is
  all zero, so a letter missing from the dump may still be taken.
- **Check the budget after a substantial change.** Call `get_status`, then apply the documented
  fixes in their documented order, which `get_knowledge("pitfalls")` gives under the structural
  change section. **Never turn Double Computation Rate on as a performance fix:** it is a
  frequency-response setting and was measured cutting a patch to three voices at a saturated DSP
  budget.
- **Disable, never clear.** A formula removed from the matrix is deleted on save. Park a formula
  you want to keep on a cell that reaches no output and disable it there.
- **User slots 1 to 5 are in use.** Never offer one of them as a free slot.
- **`tools_spec.md` specifies tools that do not exist yet.** Never promise one of its T<n> ranks
  as a shipped capability.

If a question about the catalog is not answerable from this skill, that is by design - put it to
`search_factory_presets` or `get_knowledge()`, and if neither answers it, say so plainly instead
of guessing.
