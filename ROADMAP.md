# eagan_mcp roadmap

Goal: describe a patch in plain words ("3 osc poly, FM with its own envelope,
slight pitch LFO") and the agent builds it on the EaganMatrix Module.

Protocol details and findings live in CLAUDE.md. This file is the plan.

## Done (2026-10-25)

- [x] Connect, Editor ping (ch16 cc116), load presets
- [x] Capture a preset dump: name, description, raw streams, saved as .mid
- [x] Search the user guides and factory preset descriptions
- [x] Read and write matrix cells, with row/column names (`get_matrix`, `set_matrix_point`)
- [x] Read formulas (`get_formula`) and change W/X/Y/Z basics (`set_formula`)
- [x] Read setup and set osc slot / bank / shape generator types (`get_setup`, `set_osc_type`,
      `set_bank_type`, `set_shape_generator`)

## 1. Formula editor (mostly done)

- [x] Decode formula stream: W/X/Y/Z, modes, magnitudes, macro modifiers
- [x] Read tool with plain-words summary (`get_formula`)
- [x] Write tool for the basics (`set_formula`), verified by read-back
- [x] Define a fresh, unused formula letter from scratch (tested: A = constant 0.5)
- [x] Operator: how W/X/Y/Z combine (`set_formula` operator), tested: envelope x mod wheel
- [ ] X/Y/Z begin/end range scale, transfer functions, macros on X/Y/Z
- [ ] Persistence (s_Form_Poke id 63): decay and release - there is no ADSR (tools_spec.md T5)
- [ ] Ancillary options, blend, interpolation

## 2. Building blocks (mostly done)

- [x] Shape generator type (continuous, single cycle, phase from row, dual)
- [x] SG waveform shape and phase per formula (`set_formula` sg_shape, sg_phase)
- [x] Oscillator slot type: DSF, Jenny, phase generator, filter types, noise, multiplier...
- [ ] Filter cascade and extreme-rate options (ids known, values not mapped)
- [x] Bank A/B type (values verified for BiqBank and Kinetic)
- [ ] Bank C type values (delays) - verify on the device
- [x] What each bank parameter column means per bank type (guide sections 6.3-6.17): one card per module in `eagan_mcp/knowledge/modules/`, served by `get_knowledge`

## 3. Recipes

- [x] Doc that maps synth vocabulary to EaganMatrix cells and formulas (RECIPES.md, `get_recipes` tool)
- [ ] Each recipe tested on the Module by ear before it goes in
- [x] First tested recipes: pitch, volume, SG trigger, pitch LFO, FM with envelope, mod wheel, macro
- [ ] More: filter envelope, detune, pitch-proportional depth (listed as candidates in RECIPES.md)
- [ ] Pitch-proportional depths (LFO and FM are absolute Hz now; needs X in the formula)

## 4. Full patch flow

- [ ] Prompt -> working patch in one go (all pieces exist; needs an end-to-end test from a fresh chat)
- [x] Save to a user slot (only with explicit confirmation) - verified: "FM Wheel Vibrato" in user slot 7
- [x] Name and description (`set_preset_name`)
- [ ] Export the result as .mid

## 10.81 follow-up

- [x] Guides refreshed to 10.81 (docs/), HakenMidi.h added, code checked against the header
- [x] Verified on the device: get_status (cc114 usage, LED) and set_polyphony (id 39 base + id 5 double rate, read back OK; turning off double rate took Saw Swarm Warm from 100% to 72% DSP)
- [x] Verify a NEGATIVE formula height on the device (header sign semantics): OFFSET confirmed 2026-10-27, osc-1 pitch probe, mirror ruled out by the A3 vs G5 crossover
- [ ] get_status: dsp_polyphony (cc72) never arrives after a ping, so find out when the Module sends it
- [ ] Rebuild "FM Wheel Vibrato" (user slots were cleared by the update)
- [ ] Optional: write formulas by letter via cc34 (ccFormSel) instead of selecting a cell
- [x] set_bend_range tool (s_Mat_Poke id 40, 96:n = 95+n) + get_setup shows bend_range when sent
- [ ] Test set_bend_range on the device (needs a Claude restart to load the tool)
- [x] Bank parameter column names per bank type: the maps are in `eagan_mcp/knowledge/modules/`. In get_matrix a bank column carries its bank type ("Bank A col 1 (BiqBank)"), not the parameter name - naming the parameter needs the per-bank column selectors, which the MCP does not decode into names yet
- [ ] Open: is delay time latched at note-on (new note after a bend comes out bent)?
- [ ] Optional: filter cascade / ladder variant (OscFilOpt ids 77-81), master column assignment

## On the side

- [x] Performance pitfalls: confirmed by the 10.81 guide (sec. 8.5): DSP overload
- [ ] Find why the MCP server disconnected once mid-session

- [ ] Release the MIDI port after each tool call, so switching to the Haken Editor is easier
- [ ] Check if Windows MIDI Services (multi-client) is active; test Editor + agent together
- [ ] Verify guide-only rows/columns: Sub L/R, Direct -, Conv 2, Out Mix, dry L/R (Direct + (2) verified)
- [ ] Retry when a preset load returns no dump
- [x] set_matrix_point false 'not verified' (fixed: separate full read after write)

RESEARCH_REPORT.md at the repository root is the dated record of the 2026-10-26 research pass - one research pass's findings and their provenance, never a plan - and it carries the unrun device test plan DT1-DT21.
