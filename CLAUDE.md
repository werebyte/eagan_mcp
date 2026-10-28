# eagan_mcp, notes for the agent

## FIRMWARE 10.81 (since 2026-10-25) - READ FIRST
- The Module runs 10.81. The official protocol header ships with the Editor:
  docs/HakenMidi.h (copied from Haken Editor 1081/User Guides). It is the source of truth.
  The 10.81 Editor is JUCE (no .maxpat any more); the older findings below came from the
  1044 Max patches and were checked against the header.
- docs/ = the user guides as text, stamped "Firmware Version 10.61 to 10.80" (docs/EaganMatrixUserGuide.txt:3-4), NOT 10.81. Only docs/HakenMidi.h is 10.81, so 10.81-only behaviour is documented in no guide at all and a guide citation is fw 10.80 at best. docs_1044/ = the old 10.44 guides, kept for diffing.
- Header confirms: ping cc116/pong cc118, matrix cc40-45 + values, streams 0/1/19/20,
  ccStore 112 with ccBankH 0 (user) / 126 (edit buffer); ccBankH 127 = system slots, only
  during Update File 2. Preset numbers on the wire are slot-1.
- FIXED: polyphony is s_Mat_Poke id 39 (1..8), +id 11 expanded, +id 5 double rate.
  ch16 cc39 is reserved, the old set_polyphony did nothing.
- FIXED: bank values 8 = CVC, 10 = Additive (old menu-order guess was wrong). Bank C 0-3 delays.
- FIXED: columns 2..7 are 6 assignable Master columns (ids 27-32 say what they drive);
  8 = Master/Dry mix, 9/10 dry L/R, 11 separator; banks have 8 columns each (A 27-34,
  B 35-42, C 43-50); osc slot third column is B (bandwidth / spectral balance).
- FIXED: formula sign semantics are an OFFSET, not sign-and-magnitude: a negative value is written raw = (v+1)*100, read back raw/100 - 1. Decisive evidence = 564 orphan Neg flags (= -1.00 under offset, no-ops under the mirror). [C] corpus, NOT confirmed by ear.
  The 1044 Max-patch formula only agreed for positive values. NOT verified on the device
  for a negative value yet. Formulas written earlier with negative heights may be off.
- NEW: get_status reads DSP usage (cc114 = 32*dsp + 4%-units) and actual DSP polyphony (cc72).
- NEW: X/Y/Z transfer functions incl. Steep S (10.73), per-component macros.
- s_Form_Poke writes apply to the formula selected by ch16 cc34 (ccFormSel). We select by
  clicking a cell (which sets cc34 on the Module); sending cc34 directly is an untested option.
- ccMatOp 124 (matRefresh) asks for matrix/formula/text now and on edits: alternative to
  selecting cell 0,0 for reads (untested).


- Python, snake_case everywhere.
- Protocol source of truth: docs/HakenMidi.h (fw 10.81, Lippold Haken, copied from the Haken Editor install). Don't guess message formats; cite the header line. The older copies under ref/ are never a citation.
- Reference for live device handling: pachde CHEM (Controller for the Haken Eagan Matrix, VCV Rack plugin, C++) in ref/pachde-CHEM/. Not the same project as ref/cohem/, which is pachde cohem, a preset .mid compiler/decompiler.
- Writes go to the edit slot only, unless the user explicitly confirms.
- Device: EaganMatrix Module, Windows host, USB-MIDI.

## Protocol findings (2026-10-25)

- Documented config protocol: docs/ContinuumUserGuide.txt, section 15 (around line 6440).
- Preset .mid files are DECODED: eagan_mcp/preset_file.py owns both generations.
  Modern = ch16 streams; legacy (422 of 668 factory files) puts matrix, setup and formulas
  on ch15 as bare cc. See preset_file.py's module docstring for the tables. [C] corpus.
- Example presets: <Editor>/HE/User Guides/Tutorials/*.mid, SysPresets in <Editor>/HE/Firmware.
- The Haken Editor is a Max patch (.maxpat, JSON). Its MIDI logic is readable there if HakenMidi.h is not enough.
- MCP SDK is pinned to <2 (2.x renamed FastMCP).

## Live USB protocol (tested on the Module, 2026-10-25)

- Port names: "EaganMatrix Module <serial> 3" (in) / "... 4" (out), where <serial> is this
  unit's own number - do not hardcode it. `midi_io.DEFAULT_PORT_HINT` is the substring
  "EaganMatrix", which matches any unit; `connect(port_hint=...)` overrides it.
- Without the Editor ping (ch16 cc116, any value, Editor sends 1/s) the Module
  stays quiet. With it: status reply (cc109=12, cc111, cc118, cc114, cc72).
- ch16 cc109=16 (transmit config) gives nothing over USB; guide says it goes to the 3.5mm jack.
- Preset select after a ping -> Module streams the full preset (~630 msgs):
  ch16 cc56=id starts a stream, ch16 poly pressure (note,value) = 2 data bytes,
  cc56=127 ends it. id 0 = name, id 1 = description, 20/14/5/6/11/12/15 = binary.
  Plus many ch1 CCs (cc40-54, 86, 97) and ch2 RPN/NRPN. Meaning: HakenMidi.h.
- The live USB format differs from the .mid preset file format; preset_file.py handles the latter.

## Matrix protocol (fw 10.x, verified on the Module 2026-10-25)

Source: Haken Editor 1044 (NOT the older HE/ copy), HE MatrixPlotter.maxpat "p FormulaMidi"
and HE Matrix.maxpat "p EditMatrixPoint". All on ch16:
- cc45 control: 126 = start of matrix send, 115 = Editor selects a cell, 121 = toggle mute
- cc40 row, cc41 column, cc44 value (low 6 bits code, +64 muted)
- codes: 0 blank, 1..22 A..V, 23..44 A'..V', 45/46/47 = W/X/Y, 48 = z SQUARED (matZZ, HakenMidi.h:758 - there is no plain Z code), 49 decimal, 50..58 = 1..9, 59/60 square/cube row
- decimal: cc43 digits 1-2, cc42 digits 3-4, then cc44=49
- Write = select (cc41 col, cc40 row, cc45 115) then value. Module echoes the full matrix.
- Selecting any cell makes the Module re-send the whole matrix -> read without reload.
- Row/column names: eagan_mcp/matrix_map.py (verified vs guide-only marked there).
- Formulas themselves (what A, B... compute) are NOT decoded yet. Probably stream 20
  (sent after selecting a cell holding a formula) and cc34 (current formula number).
- Bank parameter columns depend on bank type (BiqBank, SineBank, Kinetic...): see guide sec 6.3-6.17.
- Gotcha: a preset load sometimes returns nothing on the first try; retry with longer listen.

## Formulas (verified on the Module 2026-10-25)

Source: Haken Editor 1044, HE Formula.maxpat (rxFormCfg / txFormCfg) and _Haken_Editor_.maxpat
"p txFormCfg_txMatCfg". Decoder: eagan_mcp/formula.py.
- Selecting a cell that holds a formula: Module sends ch16 cc34 = formula number, then
  stream 19 (cc56=19) = (id, value) pairs as ch16 poly pressure (note = id).
- Write: select the cell FIRST, then for each change: ch16 cc56=19 + poly pressure (id, value).
  No terminator. A ping or other traffic between select and write made the write fail once.
- Stream 20 = matrix config pairs (not formulas). Stream 15 = thumbnails.
- W: 40 mode (0 Const, 1 Gated, 2-6 SG1-5, 7-11 SG1b-5b, 12 FormulaDelay; RMS unverified),
  41 magnitude index (0..6 = .001..1000), 42 slider, 73 secondary slider,
  66 modifier (0 x1, 1 xMacro, 2 x127xMacro, 3 fingers, 4 voice#, 5 1-if-voice-1, 6 poly),
  67 macro (0 = i, 1 = ii, ...).
- X/Y/Z: begin 43/53/60, end 49/54/61 (raw, scale unknown), multiplier 1/2/3,
  mode 4/5/6, heights 45,46 / 51,52 / 58,59, macro 27/28/29 (raw), transfer 85/55/62.
- Sliders: sign-bit id is sent just before its slider (13->42, 14->73, 15->45, 16->75,
  17->46, 18->76, 19->51, 20->77, 21->52, 22->78, 23->58, 24->79, 25->59, 26->80).
  value = (raw + 100*(not sign))/100 - 1, range -1..1.27.
- STALE NOTE CORRECTED 2026-10-28. That list was written before the research pass and is wrong
  now: `eagan_mcp/formula.py` decodes ALL of it from the header - ancillary 7-11/56/57/100/101
  (`ANC_DOMAIN_ID`, `ANC_LOOKUP_ID`, `ANC_LIMIT_ID`, `ANC_TO_NN_ID`, `ANC_TOUCH_AREA_ID`,
  `ANC_OP_IDS`, `ANC_VALUE_IDS`, with `ANC_OPS`/`ANC_VALUES`/`ANC_LOOKUPS`/`ANC_DOMAINS` value
  tables), 121 as a blend shelf, blend 39/68, interpolation 48/82, persistence 63/81,
  reluctance 96/97, wZone 118/119 and the 124/125 flags, and the X/Y/Z begin/end scales.
  **The one id still unnamed is 47**: the id table runs 46 -> 48, the old "trim 47" reading came
  from the 1044 Max patches, and the header's 47s are unrelated (a CC number, a macro index, C5).
  Trim is really in the mode table as the `noTrim` variants `cContinuousNT..cRelativeNT = 4..7`,
  which is why masking a mode with `& 3` would be wrong.
- The 1081 Editor's `Menuitems.txt` INDEPENDENTLY CONFIRMS the ancillary decode, value for value:
  `$Ancillary24` lists the 13 operators in `ANC_OPS`' order (x, absolute-then-multiply,
  invert-then-multiply, /, +, -, Pow, Log, Mod, Qnt, Min, Max, crossing-detect), `$Ancillary35`
  the operand list (0, 1/4, 1/2, 1, 1 1/2, 2, 3, 4, 5, 10, then the formula letters), and
  `$Ancillary1` the domain, the six graph lookups, the note-to-kHz bypass and the limiter.
  Two independent sources, header and Editor menu, agreeing - which is as good as this gets
  without a device test.
- Formula letters are shared: editing a cell's formula changes all cells using that letter.
- The Module omits matrix cells whose formula is all zero from the matrix dump. set_matrix_point
  falls back to reading the cell's formula number to verify formula letters.
- Tested: placing an unused letter (A) and defining it from scratch works.

## Setup / matrix config (stream 20, verified 2026-10-25)

Decoder: eagan_mcp/setup.py. Source: Haken Editor 1044, HE Matrix.maxpat (rxMatCfg/txMatCfg).
- Read: select any cell -> Module sends stream 20 (all ids). Write: ch16 cc56=20 + poly pressure (id, value).
  Write verified on the device (osc 1 type 0 -> 3 -> 0).
- 39 polyphony. 72-76 osc slot type (value table in setup.py), 77-81 filter cascade,
  82-86 extreme rate. 91/92/93 bank A/B/C type. 100-104 SG1-5 type (& 3), 105 delay select.
- Bank A/B/C values: take them from `docs/HakenMidi.h:1561-1575`, NOT from the Editor's menu.
  A/B: 0 BiqBank, 1 BiqGraph, 2 BiqMouth, 3 SineBank, 4 SineSpray, 5 WaveBank, 6 HarMan,
  7 ModMan, **8 CVC, 9 Kinetic, 10 Additive**. C: 0 VoiceDelay, 1 SummedDelay, 2 MicroDelay,
  3 FormulaDelay, then 4/5/6 SineSpray/WaveBank/HarMan and **8 CVC** as aliases of Bank B.
  Bank C is no longer unverified - the header gives it outright `[G]`.
  **MENU ORDER IS NOT THE WIRE VALUE, demonstrated twice.** The Editor's Bank A/B menu lists
  Additive ninth, which would make it 8; the header says 10 and CVC is what is really 8. Bank C's
  menu lists CVC seventh where the header says 8. Checked against the 1081 Editor's own
  `Menuitems.txt` (`$BankA`/`$BankB`/`$BankC`) on 2026-10-28, so this is the CURRENT menu, not a
  1044 artefact. `eagan_mcp/setup.py`'s `BANK_AB_TYPES`/`BANK_C_TYPES` are header-faithful and
  must not be "corrected" from a menu. Longer version: `knowledge/modules/index.md`.
- SG types: 0 Continuous Cycle, 1 Single Cycle, 2 Phase from Matrix Row, 3 Dual. Order from the
  Editor menu; Bowed BiqBank SG1=1 fits (touch-triggered 2 Hz one-shot).
- Bank parameter column meaning per bank type: guide sections 6.3-6.17, not mapped yet.
- SG waveform shape is per formula: id 50 (0 Ramp Up, 1 Ramp Down, 2 Pulse, 3 Pulse at End,
  4 Triangle, 5 Hann, 6-9 S-curves Gentle/Steep Up/Down, 10 Square, 11 Sine, 12+ S+H options).
  Same id 50 = buffer select when W mode is FormulaDelay. Id 117 = SG phase (0 off, 1-3 offsets,
  4+ phase mod by A..). Source: HE Formula SG Display.maxpat. Write+read-back verified (SG1 + Sine).
- set_matrix_point verification: the Module's echo right after a write is a partial matrix that may
  stop before the changed cell. Verify with a separate full read (select 0,0) and listen >= 2.5 s.
- Gotcha: a Continuous/Single Cycle SG needs its T column (e.g. Direct+ -> SG n T = W) or it never starts.
- Formula operator: id 38 (0 W+X+Y+Z, 1 Wx(X+Y+Z), 2 (W+X+Y)xZ, 3 (W+X)x(Y+Z), 4 (WxX)+(YxZ)).
  Source: HE Formula Equation.maxpat. Envelope scaled by mod wheel = W SGn + Y on + operator 1.
- MIDI in: CC 1 (mod wheel) is read as Y (Continuum guide). Macros i..iv = ch1 CC 12..15 (guide sec. 15/ch1 table).

## Saving (works, verified 2026-10-25)
- Name/description: text streams 0/1 (cc56=id, char pairs as ch16 poly pressure, zero pad, cc56=127).
- Store to USER slot N: ch16 cc0=0, cc32=(N-1)>>7, cc112=(N-1)&127. Source: "p BankHiLoPgmOut".
  The Module answers with the name/description streams and cc0/cc32/program change of the new slot.
- NEVER cc0=127: that is the SYSTEM slot path (factory updates). A first attempt used it; checked
  afterwards that the targeted system preset (Ambient Delay, system slot 7) was not changed.
- list_user_presets (cc109=32): 128 user slot names in order (slot 1 first), then the current
  edit-slot name as the last entry. "-" = empty slot. Read-only, use it to verify a store.
- LESSON: do not verify a store by loading the slot before the list shows the name there;
  loading replaces the unsaved edit slot.
- System slot order for the Module: Haken Editor 1044/HE/Firmware/Update File2 1044 EaganMatrixModule.txt

## Handoff 2026-10-25 ("Saw Swarm Warm", user slot 3)
- Performance pitfalls (knob lag, pops) are in RECIPES.md "Pitfalls on the EM Module". Cause is a
  working hypothesis, not confirmed by Haken.
- Panel encoder: no acceleration, ~1 step per click, 127 clicks full range.
- get_matrix: first read after connect/load can be empty; the tool now retries with 4 s.
- save_to_user_slot: the echo varies between saves; the tool now verifies via list_user_presets
  (slot name == current edit-slot name).
- Open: the MCP server disconnected once mid-session (cause unknown).
- Tested by the user: FM via an audio row into osc F ("FM Wheel Vibrato", Osc 3 -> Osc 1 F,
  SG x Y) does NOT cause knob lag. The pitfalls are specific to Direct-row constructions.

## Handoff 2026-10-25 ("Sitar Modal Pluck", user slot 4)
- Delay-based strings do not follow pitch bend on a ringing note; use a BiqBank modal string.
  Details, BiqBank column map, burst-follows-pitch and bend range: RECIPES.md "Strings and plucks".
- Bend range = s_Mat_Poke id 40 (97 = 96:2). Not readable back; verify with listen (~+-170 = +-2 st).
- Preset index for load_preset / load_and_capture_preset = the number in the "EaganMatrix Module
  Quick Start" System Library list (effectively 0-based), e.g. Utility "15. Karplus - 1" = 15,
  Strings "31. MicroDelay WaveGuide v1" = 31. The 10.76 Preset List numbers are one higher.
- Listening tests: one change at a time, then a yes/no question. SendUserMessage right before a
  long listen so the user can act during the recording.
- "Saw Swarm Warm" (slot 3) re-saved: base polyphony 6, "+" on, Double Computation Rate off.
  Double rate was the cause of 3 voices + 100% DSP; user confirmed no lag after the change.
- Preset index on 10.81 does NOT always match the Quick Start list: Utility "BiqMouth - Basic" = 7
  (Quick Start says 8), index 8 = "Comb Filter Basics". Use load_and_capture_preset (returns the name)
  to confirm, and correct by +-1.

## Handoff 2026-10-25 evening ("Harkonnen Voice", user slot 5) - continue here
- Goal: deep Harkonnen (Dune) chant voice, didgeridoo style.
- Built on factory "BiqMouth - Basic" (Utility 7): Bank A WaveBank (4 detuned saws + f5 = X x .5
  sub-octave via Direct+ X and Direct x .5 on col 32) -> Bank B BiqMouth -> Master.
- Bank B Sh (col 36, formula E): W = 2.3 (M:oo) + Y wheel 0 -> -0.2 (oo -> uh -> ah, didgeridoo wah).
  Macro i is now unused. Macros ii/iii/iv = sF / oF / sB (factory).
- NOT TESTED by the user yet: default "oo", wheel opening to "ah" (= first test of a NEGATIVE
  formula height), sub-octave audible.
- Next: growl (vocal fry / rough AM), lower throat (sF), maybe LFO on Sh, chant reverb.
- Sitar Modal Pluck (slot 4) re-saved with the volume fix on Bank A -> Master formula I:
  Y wheel 0 -> 0.6 (user: much better) and X constant 0.6 x Macro i (NOT tested yet).
- User slots now: 1 Sitar Mute Pluck, 2 Sitar FM Pluck, 3 Saw Swarm Warm, 4 Sitar Modal Pluck,
  5 Harkonnen Voice.

## Project Documentation & Standards (Maister)

Before writing or changing any code, read @.maister/docs/INDEX.md - it maps the project's
documented coding standards (global, protocol, testing) and generated project docs. Open the specific
files it points to that are relevant to the task; the index alone is not enough. The protocol
findings above and RECIPES.md remain authoritative for device behaviour.

The shipped knowledge base is eagan_mcp/knowledge/ (model.md, modules/, patterns.md, pitfalls.md,
worked_examples.md), served to an agent by the get_knowledge tool rather than read by a human. Read
it before building a patch: standalone pitfalls are canonical there and no longer in RECIPES.md, and
every claim carries one evidence tag - [D] device, [D-cap] capture, [G] docs, [C] corpus, [I]
inferred - per .maister/docs/standards/protocol/protocol-sources.md.

NOT REPAIRED BY CODE: the formula sign fix corrects what the codec writes from now on. It does NOT
repair heights already stored on the device. "Sitar Modal Pluck" (user slot 4) and "Harkonnen Voice"
(user slot 5) hold negative heights written under the old encoding; only rewriting those cells
corrects them.

RESEARCH_REPORT.md at the repository root is the dated record of the 2026-10-26 research pass - one research pass's findings and their provenance, never a standard - and it carries the unrun device test plan DT1-DT21, the four gap classes and the known-weak-citation note.

## DEVICE SESSION 2026-10-27 (rack powered on, operator present) - 4 findings

- **VERIFIED: the formula sign encoding is an OFFSET.** Device test, not corpus. Probe: a fresh
  letter V on `Direct + (2)` -> `Osc/Filter 1 F`, W = Constant -0.2 x 1, against a positive control
  of +0.2 which audibly detuned osc 1 sharp. With X on that column in kHz, `F = note_kHz + k`, so
  the lowest working note pins k: k = -0.2 breaks below **A3**; k = -0.8 (the old mirror reading)
  breaks **every note up to G5**. Observed: works from C4 up, breaks below. So the device applies
  **-0.2** -> offset confirmed, mirror ruled out. ROADMAP's negative-height test is CLOSED.
- **VERIFIED as a by-product: idTransX default really is kHz, not Octaves.** The same probe made
  the keyboard track "about half an octave per key" above C4 (C4 -> 61.6 Hz, C5 -> 323 Hz, a 5.25x
  jump across one octave of keys). An octaves axis would have stayed in semitones. This is the F5
  fix, independently confirmed by ear.
- **CORRECTED: cc45=115 (select cell) does NOT make the Module dump the matrix on 10.81.** It
  returns an echo and nothing else (13 messages). The read trigger is **ccMatOp 124, matRefresh**
  (`ch16 cc45=124`), which CLAUDE.md previously listed as "untested": it returns the full state -
  ~1,100 messages, 50 matrix cells, stream 20 setup, the text streams, and cc72. The read sequence
  that works is **state change (e.g. preset load) -> matRefresh -> listen**.
  A matRefresh with no intervening change returns almost nothing, which is the real mechanism
  behind the "first read can be empty, retry with a longer listen" gotcha.
- **FIXED (code): `midi_io.listen()` cleared the receive buffer as its first act**, so every
  `clear() -> send request -> listen()` caller in server.py - nine of them - discarded the reply if
  it arrived before Python reached `listen()`. The Module answers in milliseconds, so get_status
  reported nothing at all. Clearing is now the caller's job. get_status went from all-nulls to
  `{dsp_usage_percent: {dsp0: 56}, led: "blue"}`. `dsp_polyphony` (cc72) does arrive, but after
  matRefresh, not after a plain ping.

- **PARTLY VERIFIED, and the earlier wording was too strong: a macro position survives a RELOAD
  but was NOT preserved across a power cycle.** Set macro ii to 20 (ch1 cc13), saved to slot 5,
  reloaded in the same session, and the device reported cc13 = 20 - that much holds. But the next
  day, after a power cycle, slot 5 read back cc13 = **0** (sF 0.5, not the 0.81 that made the patch
  work), with cc14 = 26 and cc15 = 46 that nobody here set. **Confounded**: the operator had controllers
  on the macro CCs, so an external source may have moved them rather than the power cycle losing
  them. Either way, do NOT rely on a macro position being part of the saved sound. If a knob value
  is load-bearing for a patch, bake it into the formula constant. [D] 2026-10-27/28, fw 10.81.
  The matRefresh dump transmits ch1 cc12-17, which is how to READ the macro values back (there is
  no typed tool) - but it reports the LIVE values, which is why a snapshot can disagree with what
  was stored.
- **"Harkonnen Voice" (slot 5) re-saved 2026-10-27 and now actually sounds.** Formula E's Y height
  was stored as -0.8 under the old mirror encoder when the intent was -0.2, so the vowel wah swept
  Sh 2.3 -> 1.5 instead of 2.3 -> 2.1, straight past "ah". One raw byte (20 -> 80) fixed it. This is
  the first measured instance of real damage from the old encoding. Also macro ii lowered to 20
  (sF 2.5 -> 0.81) for a bigger throat. Then a GROWL was added and the whole thing re-saved to
  slot 5. User's verdict: **"buzzy but i like it. not harkonnen 1:1 but its demonic low"** - kept.
- **The growl build (slot 5, 2026-10-27), 3 cells and 2 formulas:**
  `SG 2 F (col 53) <- Direct + = M`, M: `W = Constant 0.3 x 100` -> **30 Hz**;
  `SG 2 T (col 54) <- Direct + = W` (the trigger - a Continuous SG never starts without it);
  `Bank B col 1 (In, col 35) <- Bank A = L`, L: `W = SG2 0.12 x 1 [Ramp Up]` + `Y = 0.25->0.25`.
  So the formant bank's input level is chopped 0.25 -> 0.37 at 30 Hz: ~48% AM, whose sidebands
  read as rasp rather than tremolo at that rate. Ramp Up is what makes it buzzy; "Pulse" is the
  untried alternative if a more glottal fry is wanted.
  **SG 1 was deliberately left alone** - it is a pressure-controlled vibrato
  (`K: Z = Continuous 0.0->0.5 x 10`, so 0..5 Hz rising with Z), which is worth keeping.
- Still open on this patch: the sub-octave is only `Bank A col 6 = X` with
  `Direct x (multiply) = .5`; `.25` would drop it a further octave. Bank C is a VoiceDelay doing
  little for a sustained voice. Chant space untried.
- **The operator had LFOs patched to the macros during part of this session.** They were disconnected
  before the sF conclusion was trusted; macros measured static across three matRefresh samples
  afterwards. If macro-driven LFOs are running, any macro reading or listening test is confounded
  and the external controller (a Faderfox EC4 is on the port list) is NOT visible on the Module's
  own port.
- Macro map on this patch (factory BiqMouth design, inherited): **iii = oF formant offset
  (0..1), iv = sB bandwidth spread (0.5..2.5)**; macros i and ii now unused.
- **sF is BAKED IN as of 2026-10-28 and macro ii no longer drives it.** Formula F was
  `W = Constant 0.2 x 10 x Macro (ii) ; Y = 0.5`, i.e. `2.0 x macro + 0.5`, which gave the
  0.81 that made the patch work only while macro ii sat at 20 - and that position did NOT
  come back after a power cycle. It is now `W = Constant 0.03 x 10 ; Y = 0.5`, a fixed
  sF 0.8, re-saved to slot 5 and confirmed by ear. The general rule this came from: if a
  knob value is load-bearing for a patch, put it in the formula constant, because a macro
  position is not reliably part of the saved sound.

### UNMINED DATA IN THE EDITOR ROOT - found 2026-10-27, HIGH VALUE

Prompted by a YouTube video in which an EaganMatrix author mentions "the help files in the firmware
directory". Our `descriptions.json` already came from `Firmware/Descriptions`, but **three files in
the Editor ROOT were never looked at**, and one of them settles an open question.

- **`SysPresetsColl.462A0C4.txt` - 668 lines, THE authoritative system preset list.**
  Format: `N, <name or "name with spaces"> "TAG TAG TAG";` - note names are quoted ONLY when they
  contain a space, which a naive regex drops (120 of 668 lines).
  **It yields the within-category preset index OFFLINE:**
  `index = alphabetical position among presets whose FIRST tag is that category`.
  Verified against the device on two categories, every position: `FM Bells` -> PT, index 16 and
  `Metal Rainstick` -> PE, index 11, both matching a device scan exactly, including the
  `Dolce Cristallo Space` before `Dolce Cristallo` collation oddity.
  **This supersedes `preset_index_1081.json`'s `collation_status: "unresolved"` and retires DT3.**
  Category number for `load_preset` = the CatsColl group-1 index **+ 1** (slot 0 is UP, user).
- **`CatsColl.txt` - the full tag vocabulary, 8 groups**, 1 = the 13 menu categories, 2 = instrument
  family (FL Flute, RD Double Reed, SU Struck...), 3 = character, 4 = processing, 5 = texture,
  **6 and 7 = MODULE** (AD Additive, BB BiqBank, BH BiqGraph, BM BiqMouth, DF/DM/DS/DV the four
  delays, HM HarMan, KI Kinetic, MM ModMan, OJ/OP/OS the oscillators, SB SineBank, SS SineSpray,
  WB WaveBank), 8 = voice behaviour (PO portamento, SV single voice, SP split...).
  **So every preset is tagged by the designers with the modules it uses** - better metadata than the
  `techniques` we derive from decoded wiring, and it covers all 668, not just the 49 with wiring.
- **`Menuitems.txt` - 2,257 lines of the Editor's own menu text** with inline explanations
  ("* Trim to Finger (requires finger on surface; shortcut '=' ...)"). NOT yet mined. Likely names
  parameters and options in the exact words the Editor shows, which is what several module cards had
  to infer.
- `SysPresetsColl.3DBBCBF.txt` is a 1-line stub; `MidiPorts.txt`, `Menuitems.txt`, `CatsColl.txt`
  and the two SysPresetsColl files all sit in the Editor root, NOT under `Firmware/`.

**Designer claim, now measured.** The video says "a lot of the EaganMatrix presets do [BiqGraph] for
winds". True: across the 26 FL-tagged presets, BiqGraph 11, OscDSF 10, BiqBank 8, HarMan 7. Winds
also pair it with breath noise and breath-controller macros.

**Terminology note, in case it comes up:** feeding manuals and presets into a chat or a Project is
in-context learning, NOT training - no weights change and nothing persists to a fresh session. The
method works; the word is wrong.

### Patches built 2026-10-27 (device session, rack on)

- **Slot 6 "Metal Drum"** - built from factory `Metal Rainstick` (**category 7 PE, index 11**) by
  ONE cell change plus one depth change. The rainstick's secret: `SG 1 T <- Direct + = B` where
  `B = W = SG2 1.0 [Pulse]`, so the Single-Cycle strike SG was being **retriggered by SG 2's pulse
  train** - that is what makes it a shaken rattle. Point SG 1's trigger at `W` instead and it fires
  once per note = a struck drum. Then the strike depth `A: W = SG1 0.79 x 0.01` -> `x 0.1` for body.
  Still rainstick-ish and worth trying: `col 6 = C = SG3 0.25 [Sine] + Z` slowly sweeps which modes
  are emphasised; `col 3 = sF` (`Y = 0.2->0.1 x 10`) is the partial-stretch metal/wood dial;
  `col 4 = B` (decay) is `W = Constant -0.8 x Macro (iii)`, a NEGATIVE constant, so macro iii now
  exercises today's corrected encoding on a factory preset.
- **Slot 7 "FM Wild Wheel"** - built from factory `FM Bells` (**category 8 PT, index 16**) by TWO
  formula edits. `A` is the FM index, shared by BOTH modulators (`Osc 2 -> Osc 1 F` and
  `Osc 3 -> Osc 1 F`), operator `W x (X + Y + Z)` with `W = SG3 [Ramp Down] x Macro (iii)` as the
  decaying index envelope. Y was unused, so adding `Y = 0.0->1.0 x 10` put the mod wheel straight
  on the index: wheel down = the original bell, wheel up = ~5x the FM.
  Then the attack noise was traced to `E` (`Osc 4 Band Pass, noise-fed -> Osc 2/3 INPUT`,
  `[(W + X) x (Y + Z)] W = SG2 [Ramp Down]`): the noise is **FM'd into** the tone rather than
  layered over it, so the wheel was multiplying it too. `W` 1.0 -> 0.35 fixed it.
  Knobs that remain, no edit needed: **macro i = modulator ratio** (formulas B/C, bell vs
  e-piano), **macro iv = index decay speed** (SG 3 rate via G), **macro iii = index amount**.
  DSP 72% idle at base 8 + expanded, LED blue - not an overload.

### Reading preset names and hunting indices (2026-10-27)
- **`load_and_capture_preset` returns name "preset" and no streams**, and `haken.decode_texts` on a
  matRefresh dump returns `[]` - the name does NOT come back that way on 10.81. **What works:
  `list_user_presets`' LAST entry is the current edit slot's name.** Use that to identify what is
  loaded.
- **Factory categories are in ALPHABETICAL order**, so hunting an index is a binary search, not a
  linear scan. Mapped so far: PE(7) 0..11 = Balinese Bedsprings .. Dripaphone with
  **Metal Rainstick = 11**; PT(8) 0..16 = Balinese Bedsprings .. **FM Bells = 16**.
- **FIXED 2026-10-28: the catalog now carries `category_index`**, the number
  `load_preset`'s second argument takes. Derived as the position within a category when the 668
  presets are ordered by `system_slot` - which is the **filename collation**
  (`(name + ".mid").lower()`, so `Acrylic Clock 2` precedes `Acrylic Clock`). Verified on the
  device in **three** categories: `FM Bells` (8, 16), `Metal Rainstick` (7, 11),
  `Windtube Air Reed` (2, 54), plus a 17-position PT scan matching entry for entry.
  `preset_index_1081.json`'s `collation_status` is now `resolved: by_filename_collation` and
  **DT3 is retired**. Pinned by `test_category_index_matches_what_the_device_loaded` and a
  dense-0-based-run check.
  **Then verified in ALL THIRTEEN categories** (2026-10-28): the first and last preset of
  each was loaded by the catalog's numbers and the Module reported the expected name back -
  25 of 26 probes. e.g. ST 0 `Bowed BiqBank` / 99 `xpStrings`, OT 0 `Acrylic Clock 2` /
  166 `Zipper`, UT 0 `Audio Through` / 48 `WaveBank - Basic`.
  **The earlier "UT is suspect" note was WRONG and is withdrawn**: `BiqMouth - Basic` at
  (13, 7) loads correctly. Yesterday's failure was the `listen()` race, fixed AFTER that
  attempt - the load always worked, the read came back empty. The old Quick Start note was
  right all along.
  **One anomaly, 1 of 668, READ-BACK ONLY**: with `The Satur` (PR, index 21) loaded,
  `list_user_presets` returns a truncated or empty list - 3, 2 and 0 entries at 2.2 s, 6 s
  and 10 s settle, sometimes ending on another slot's name. The LOAD is fine (31 cells,
  WaveBank + BiqBank + MicroDelay all decode). The device interleaves that preset's own
  streams (cc56 ids 13, 20, 27, carrying a WaveBank waveform table named `Pulse_Brit...`)
  with the names stream, and `decode_texts`' cc56 marker tracking loses the thread. A LONGER
  settle makes it worse, so it is contention, not timing. Not chased further.

### Device context worth remembering
- **The operator has NO MPE keyboard** (a Q49 on the port list). Factory presets assume per-note X/Y/Z;
  on a plain keyboard the ch1 special handling applies (`model.md:277-279`,
  `docs/ContinuumUserGuide.txt:5384-5394`). Patches whose Master is scaled by `z^2` still sound,
  but per-note expression is not available - prefer the mod wheel (Y) and macros over X/Z when
  building for this rig.
- The mod wheel is already mapped to detune in "Saw Swarm Warm", so it is a poor test axis there;
  a second Y term is masked by the detune sweep.
- A filter-cutoff probe on Osc 5 of that patch was INAUDIBLE between 2.5 and 8 kHz - the warm pad
  has little energy up there and osc 4's Ladder sits upstream. Pitch is the reliable audible probe.
