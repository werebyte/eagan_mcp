# Protocol Sources and Evidence

How wire-format knowledge enters this project: where it must come from, how it is cited,
and how its confidence is recorded so a later reader can tell fact from guess.

### Cite the Protocol Source, Never Guess

Take message formats from the official Haken protocol header (`docs/HakenMidi.h`, fw
10.81, 1870 lines, shipped with the Haken Editor) and cite the header line. The snapshots
under `ref/` are older (`ref/cohem/include/HakenMidi.h` 1852 lines,
`ref/pachde-CHEM/src/em/HakenMidi.h` 1864) and are never a citation. Never infer
a wire format from menu order or UI behaviour. Where the header is insufficient, use, in
order: the firmware guides in `docs/`, the Haken Editor's own MIDI logic, and pachde CHEM
for live device handling. Re-check anything derived from the 10.44 Max patches against
the header. Put the citation at the definition — module docstrings open with the source,
constant blocks carry a `# Source: ...` line including the raw menu value table, local
names cross-reference the header's own symbol, and tool docstrings name the wire detail
they use.

```python
CC_POLY_DSP = 72         # tx: actual DSP polyphony (HakenMidi.h ccPolyDsp)
# Source: HE Formula SG Display.maxpat menu value table "0 1 2 3 4 5 999 6 7 ..."
```

Source: `CLAUDE.md` ("Don't guess message formats; cite the header line"); `haken.py:3-4`, `formula.py:2-7`, `matrix_map.py:12-16`

### Mark Findings Verified or Unverified, With Date and Firmware

Label every device finding with how it was established, using the project's fixed
vocabulary: "verified on the Module <ISO date>" for hardware observation, "guide" or "not
verified yet" for something read from a guide or an Editor menu, "unverified"/"observed"
for a guess from a capture, and `EXPERIMENTAL` in the docstring of a tool whose framing is
still unknown. Carry the firmware version, because a firmware change can retire a
finding. Surface uncertainty to the caller instead of hiding it, keep the raw value next
to an interpretation whose scale is unknown, and when two sources disagree record the
conflict and which one the code follows.

```python
0: "Noise",   # verified (Noise - Pink)
# Guide = order taken from the guide / Editor layout, not tested yet
```

**This prose vocabulary stays where it already lives: in source-code comments.** It is not
replaced by the bracket tags below, and no existing code comment changes because of them.

Source: `CLAUDE.md` (dated section headings), `RECIPES.md` (Confidence column); `matrix_map.py:5`, `formula.py:54-57`, `setup.py:24-28`

### The Five Bracket Tags

Prose documents — every file under `eagan_mcp/knowledge/`, `tools_spec.md`,
`RESEARCH_REPORT.md` and the research findings they are built from — grade each claim with
**exactly one** bracket tag, inline, at the claim. A claim with no tag is a defect, and so is
mixing graded and ungraded claims in one paragraph. The tags carry strictly more than the
prose vocabulary: `[D-cap]` and `[C]` have no prose equivalent, and "`[C]` can never upgrade
to `[D]`" is a rule the prose form cannot express at all.

| Tag | Meaning | What it must carry |
|---|---|---|
| `[D]` | Device-verified | the `CLAUDE.md` or `RECIPES.md` line, the ISO date, and `fw 10.81` |
| `[D-cap]` | Device-recorded in `captures/`, offline-reproducible | the capture filename |
| `[G]` | From the docs | `file:line` |
| `[C]` | Corpus statistic | the count and the denominator (668 presets / 14,147 height writes / ...) |
| `[I]` | Inferred | the inference stated in the same sentence |

Rules:

- **Resolution order: `[G]` header > `[D]` > `[D-cap]` > `[G]` guide > `[C]` > `[I]`.**
- **`[C]` can never upgrade to `[D]`.** A corpus statistic is evidence about Haken's
  convention, never about what this project has heard on the device. No amount of corpus
  agreement makes a claim device-verified.
- Firmware is carried on every behavioural claim.
- A `[G]` with no citation is a defect.
- **A `[G]` *header* citation is fw 10.81. A `[G]` *guide* citation is fw 10.80 at best**,
  because `docs/EaganMatrixUserGuide.txt:3-4` is stamped "Firmware Version 10.61 to 10.80".
  A guide claim about 10.81-only behaviour therefore does not exist and must not be invented.
- **Guide line numbers are accurate to the section and within roughly 30 lines inside it**,
  because the file is a PDF extraction carrying 208 form feeds. **Quote verbatim: the quote,
  not the line number, is the locator.**

When two sources disagree, both sides stand, in this fixed block, fenced:

```
CONFLICT: <subject> - <side A> vs <side B>
  docs   [G]: "<verbatim quote>"
              - <file:line>
  device [D]: "<verbatim quote>"
              - <CLAUDE.md:line>, <ISO date>, fw 10.81
  corpus [C]: <statistic with denominator>
  follows: <which one the code/doc follows, and why>
```

### Confirm Preset Indices by Capture, Not by the Printed List

Published preset index numbers do not reliably match the device on fw 10.81. Confirm an
index with `load_and_capture_preset`, which returns the loaded preset's name, and correct
by plus or minus one when it does not match.

Source: `CLAUDE.md` ("Preset index on 10.81 does NOT always match the Quick Start list")
