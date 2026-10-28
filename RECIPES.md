# EaganMatrix recipes (firmware 10.81)

Synth vocabulary -> matrix cells and formulas. Every recipe here was tested by ear on
the EM Module. Untested ideas go in the "Candidates" section at the end.

Notation: `Row -> Column = value`. Rows/columns as in `describe_matrix_layout`.
Formula letters are shared: 44 available (A..V plus A'..V'), A..V preferred - pick an
unused letter for each new job. Check with `get_matrix` which letters are already in use.

## Pitfalls on the EM Module (read first)

Moved: `get_knowledge("pitfalls")` / `eagan_mcp/knowledge/pitfalls.md` is canonical for
standalone pitfalls. A pitfall inseparable from a recipe's steps stays with that recipe, below.

## Basics

### Pitch follows the keyboard
- `Direct + -> Osc n F = X` for every oscillator that should play the note.
- X is the predefined pitch formula.

### Volume from pressure
- `Osc n -> Master SL = Z` and `Osc n -> Master SR = Z`.
- Z is the predefined squared-pressure formula. With a MIDI keyboard, Z follows velocity/aftertouch.

## Modulation

### Shape generator (LFO / envelope) - ALWAYS set its trigger
An SG does nothing until its T column goes positive.
- Frequency: `Direct + -> SG n F = <Hz>` (column 51 + 2(n-1)). Constants 1..9 or decimals like .8.
- Trigger: `Direct + -> SG n T = W` (column 52 + 2(n-1)). W = gated while a note is held.
- Type: `set_shape_generator(n, "Continuous Cycle")` for an LFO, `"Single Cycle"` for an envelope.
- Tested 2026-10-25: forgetting T was the reason a pitch LFO was silent.

### Pitch LFO (vibrato)
- SG1: Continuous Cycle, F = .8 Hz (slow) to 5 Hz (classic vibrato), T = W.
- New formula C: W mode SG1, sg_shape Sine, value 0.18, magnitude 0.01.
  That is +-1.8 Hz, about +-7 cents at A4.
- `Direct + (2) -> Osc n F = C` for each oscillator.
- Caveat: depth is absolute Hz, so it is deeper (in cents) on low notes and shallower on high
  notes. Pitch-proportional depth needs X in the formula (not tested yet).

### FM (osc B modulates osc A's frequency)
- `Osc B -> Osc A F = <formula>`. Osc B should not go to the Master if it is only a modulator.
- The formula value is the deviation in kHz (F columns are kHz).

### FM with its own envelope
- SG2: Single Cycle, F = 2 Hz (one Hann cycle ~0.5 s), T = W.
- Formula B: W mode SG2, sg_shape Hann, value 0.5..1.0, magnitude 1.
- `Osc 3 -> Osc 1 F = B`.
- Lower SG F = longer swell. Caveat: depth is absolute kHz, brightness varies across the keyboard.

### Envelope (or any formula) scaled by the mod wheel
- MIDI CC 1 (mod wheel) arrives as Y.
- In the formula: keep W as the envelope, turn Y on (height_begin 0, height_end 1),
  set operator "W x (X + Y + Z)". Result = envelope x mod wheel.
- With the default operator "W + X + Y + Z" the wheel would add a constant amount instead.
- Tested 2026-10-25 on formula B (FM amount on the mod wheel).

### Formula scaled by a macro
- `set_formula(..., component="W", modifier="x Macro", macro="i")`.
- Macros i..iv arrive as MIDI CC 12..15 on channel 1, or via the Module's CV inputs.
- Put macro formulas on level, filter or FM-depth cells, not directly on osc F columns (Pitfalls).

## Detune, filters, constants (tested 2026-10-25, "Saw Swarm Warm")

### Sawtooth-like oscillator
- Exact: Integrated DSF with S = 0.8 has the same harmonic amplitudes as a sawtooth
  (EaganMatrix User Guide 10.81, Oscillator notes 4).
- Also used: DSF Oscillator with S = 0.6 (Preset Cookbook combination example), brighter/different.
- Leaving S blank (no formula) is the cheapest: pure sine, optimized.

### Fixed detune (cheap, recommended default)
- Small decimal constant on another Direct row into the osc F column, e.g. `.004` (+4 Hz).
  Depth in cents varies across the keyboard.

### Pitch-proportional detune (cents, same width everywhere)
- User formula on Direct + (2) (or Direct - for the opposite direction) -> Osc n F:
  operator "(W x X) + (Y x Z)", X = Continuous -1..1, X transfer "X kHz",
  W = fraction, e.g. 0.12 x 0.1 = +1.2% = about +21 cents.
- Costs some panel knob responsiveness (see Pitfalls).

### Filter slot
- Filter column order: ▲ = audio input, F = cutoff in kHz, B = bandwidth (lower = more resonance).
- Ladder filters: B is limited to 0..1 (0 = max resonance), cannot be cascaded, DSP heavy.
- Other filters can cascade 1-4x (12/24/36/48 dB/oct): s_Mat_Poke OscFilOpt (not a tool yet).
- Oscillators -> filter ▲ with a level formula; filter -> Master SL/SR.
- Cutoff floor: a component with equal begin/end heights acts as a constant, e.g. Z 0.1 -> 0.1
  (x magnitude) as an offset. Safe on a filter column.
- Filter envelope: SG Single Cycle (e.g. Gentle Down shape) formula into the filter F column.
- Velocity on cutoff: Z mode "Initial" = velocity only, ignores aftertouch.

### Direct x row
- Direct x is the column's multiply row: column value = (sum of other rows) x f(Direct x).
  Source: EaganMatrix Preset Cookbook p.17 (Column Limiter note). Avoid on osc F (Pitfalls).

### Formula value resolution
- Heights have 0.01 resolution (raw = height x 100). For finer steps use a smaller
  multiplier/magnitude, e.g. multiplier 0.1 and heights 0..0.2 for 0..0.02.
- Magnitude/multiplier are powers of ten only: 0.001, 0.01, 0.1, 1, 10, 100, 1000.

## Strings and plucks (tested 2026-10-25, "Sitar Modal Pluck", user slot 4)

### Bendable string = excitation into a BiqBank (modal string)
Delay loops (Karplus, waveguide) ignore pitch bend on a ringing note (Pitfalls). Not known yet
whether delay time is latched at note-on or not modulatable at all. BiqBank modes are filters
and follow X live, so bends work, also after release.

BiqBank columns (default picklist, Preset Cookbook "The BiqBank", p.43-44). Matrix values are
added to the Properties panel values.

| Column | Param | Meaning |
|---|---|---|
| Bank A col 1 (27) | input | audio in |
| Bank A col 2 (28) | F | first mode frequency, kHz. Use predefined `X` |
| Bank A col 3 (29) | sF | frequency spread. 1 = harmonic, >1 stretched, <1 compressed |
| Bank A col 4 (30) | B | mode bandwidth. Smaller = longer ring |
| Bank A col 5 (31) | sB | bandwidth spread. >0 = far modes decay faster |
| Bank A col 6 (32) | C | center of focus. 0 = 1st mode |
| Bank A col 7 (33) | sA | amplitude spread. >0 = far modes quieter |

Wiring that works:
- `Direct + -> Bank A F (28) = X`, `Direct + -> Bank A sF (29) = 1`.
- Excitation into Bank A input (27): Noise -> LPF (osc slot 5) -> `Osc 5 -> Bank A in = .1`.
  Optional FM carrier: `Osc 1 -> Bank A in` = SG ramp-down x 0.05 x Macro ii x Z.
  Resonators need much less input than a delay loop (0.05 vs 0.2).
- `Bank A -> Master SL/SR` = constant level (no continuous Z, so no level drop on release).
- DSP 72% at 7+ voices with FM pair + BiqBank + SGs.

### Ring length / palm mute on a macro AND the mod wheel
- B column: operator `W + X + Y + Z`, W = Constant 0.4 x Macro i, Y = Continuous Linear
  0.02 -> 0.42. Base 0.02 rings long; macro or wheel shorten it.
- sB column: W = Constant 0.5 x Macro i, Y = Continuous Linear 0.3 -> 0.8 (highs die faster).
- Trick "constant + macro + wheel" in one formula: the constant goes into Y's height_begin
  (Y = wheel), the macro is W with modifier "x Macro". Negative W = subtractive macro.

### Excitation burst should follow pitch
A fixed-length burst pumps high notes much more than low ones (energy builds up per period).
Make the burst a fixed number of periods:
- SG1 F (col 51): operator `W x (X + Y + Z)`, W = Constant 0.25 x 1000, X = Continuous 0..1,
  transfer "X kHz" -> SG F = 250 x f_kHz Hz, about 4 periods.
- FM burst SG2 F (col 53): W = 0.25 x 100, about 40 periods.
- X on an SG F column is fine (the osc F pitfall does not apply).

### Pitch bend range (preset setting)
- Tool: `set_bend_range(2)` = "96:2" (MPE +-96, channel-1 keyboard +-2 st).
  `set_bend_range(12, all_channels=True)` = +-12 everywhere. Raw: s_Mat_Poke id 40 via stream 20.
- 97 = "96:2": MPE channels keep +-96, channel-1 MIDI bend = +-2 st. Others: 96:5=100,
  96:7=102, 96:12=107 (HakenMidi.h ~line 1370, Overlay Developer Guide). Plain 2 = +-2 everywhere.
- Not readable without reloading the preset. Verify with `listen`: the Module's MIDI out shows
  voice bends at 96 st scale, so +-2 st appears as about +-170 (of 8192).
- Saved with the preset.

## Candidates (not tested yet)

- Detune: second oscillator gets `Direct + -> Osc 2 F = X` plus a small constant on Direct + (2).
- Pitch-proportional LFO/FM depth: X in the formula, like the cents detune above. Expect the
  same knob-responsiveness cost.

## Vocal formants: BiqMouth (learned 2026-10-25 from factory "BiqMouth - Basic", Utility index 7 on 10.81)
- Columns (Bank A 27-33, Bank B 35-41): input, Sh mouth shape (0..4.8), sF formant freq multiplier,
  oF formant freq offset, sB bandwidth multiplier, C center, sA amplitude spread.
- NEVER leave sB empty: blank = 0 = razor-thin formants. They ring as fixed pitches that do not follow
  the keys and no vowel is heard (tested). Factory base: sB 0.5 (up to 2.5 on macro iv).
- Factory base values: sF 0.5 (+2 x macro ii), sB 0.5 (+2 x macro iv), Sh = 4.8 x macro i.
  Constants are written as a Y component with equal heights (0.5 -> 0.5).
- Source in the factory preset: Bank A WaveBank (4 detuned saws, f = X + small offsets),
  amplitude Z, into Bank B BiqMouth at .25, Bank B -> Master SL/SR .5.
