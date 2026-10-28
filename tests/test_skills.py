"""The three shipped skills under `.claude/skills/eagan-*/SKILL.md`.

WHY THIS FILE EXISTS (the G24 gap analysis, `test-writing.md:33-34`)
-------------------------------------------------------------------
The skills are a shipped artifact with no regression protection. The group that wrote them
built these structural checks in a scratchpad script that does not survive the session and
flagged `tests/` as their natural home; this is that home. The checks are pure text - no
device, no `HAKEN_EDITOR_DIR`, no new dependency, and no YAML parser, since the frontmatter
this project writes is flat `key: value` lines and adding a parser would breach the
no-new-dependencies constraint to read three files.

WHAT THESE TESTS DO AND DO NOT ESTABLISH
----------------------------------------
They pin the skills' *structure* and their *restraint*: that each one is loadable, that it
carries the device-safety rules `device-safety.md` requires any patch-building procedure to
state, and that it does not restate a device fact the tools serve. They are **not** device
verification and say nothing about what the firmware does - nothing here opens a MIDI port,
touches the Module, or reads `HAKEN_EDITOR_DIR`, `docs/` or `captures/`. Nor do they judge
whether a skill's procedure is *good*; that is a reading task, not an assertion.

CRITERION 21 IS TESTED AS AN ABSENCE OF WIRE NUMBERS
----------------------------------------------------
"No skill restates a device fact the tools serve" is not directly computable, but its
commonest and most damaging form is: a wire number pasted into a skill body - a matrix
column, a stream id, a stream-19/20 poke id, a controller - which then rots while
`get_knowledge`, `get_recipes` and `search_factory_presets` stay current. A remembered fact
that has gone stale is worse than no fact, which is why all three skills open by saying they
hold no device facts of their own. Two controllers are allowlisted below because no tool
serves them and a skill that omitted them would be less safe, not more disciplined.
"""

import re
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "skills"
SKILLS = sorted(SKILLS_DIR.glob("eagan-*/SKILL.md"))

# The two wire facts a skill is allowed to name, each because no typed tool serves it:
#   ch16 cc0=127  the system-slot store path. device-safety.md requires it be named and
#                 forbidden outright (H2); `send_raw` is the only tool that can reach it.
#   ch1 cc18      N5's kill-switch CC. It has no typed tool, so the skill must spell out
#                 that a `send_raw` of it is unvalidated and unverified.
# They are matched and removed as whole phrases, channel included, rather than exempting
# the whole line: a line is allowed to carry one of these, not to carry anything else
# under their cover.
ALLOWED_WIRE_PHRASES = ("ch16 cc0=127", "ch1 cc18")

# A wire number in a skill body: a controller, a channel, a stream, a poke id, a matrix
# row or column. Anything matching that is not allowlisted is a device fact the tools serve.
WIRE_FACT = re.compile(r"\bcc\d+|\bch1[56]\b|\bstream \d+|\b(?:id|row|col|column)s? \d+",
                       re.IGNORECASE)

# Each skill must carry all three. device-safety.md:6-12 (edit slot, the store path that is
# never sent, and the read-only name comparison that verifies a store). The patterns treat
# any run of whitespace as a space, because these sentences are prose wrapped at ~100
# columns and a phrase may straddle a line break - matching the markdown's line breaks
# would make the test fail on a reflow, which is not a safety change.
REQUIRED_SAFETY_CONTENT = {
    "the edit-slot write scope": re.compile(r"edit\s+slot\s+only", re.IGNORECASE),
    "the forbidden system-slot store path": re.compile(
        r"never\s+send\s+the\s+system-slot\s+store\s+path", re.IGNORECASE),
    "store verification via list_user_presets": re.compile(r"list_user_presets"),
}


def _frontmatter(text: str) -> dict[str, str]:
    """The flat `key: value` block between the opening and closing `---` fences."""
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", (
        "a SKILL.md must open with a `---` frontmatter fence on its first line, or the "
        "harness will not register the skill at all")
    end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    fields = {}
    for line in lines[1:end]:
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def test_three_eagan_skills_are_present_and_each_names_itself_in_its_frontmatter():
    """The frontmatter is what makes a skill discoverable; a wrong `name` makes it dead.

    `name` has to equal the directory, because that is how the skill is invoked, and
    `description` is the only text the model sees when deciding whether to load the skill -
    an empty one means the skill exists and is never chosen.
    """
    assert len(SKILLS) == 3, (
        f"expected the three eagan-* skills under {SKILLS_DIR}; found "
        f"{[p.parent.name for p in SKILLS]}")

    for path in SKILLS:
        fields = _frontmatter(path.read_text(encoding="utf-8"))
        assert fields.get("name") == path.parent.name, (
            f"{path.parent.name}/SKILL.md declares name {fields.get('name')!r}; it must "
            "equal the directory name, which is how the skill is invoked")
        assert len(fields.get("description", "")) > 80, (
            f"{path.parent.name} has a description of "
            f"{len(fields.get('description', ''))} characters. It is the only text the "
            "model reads when deciding to load the skill, so it must say both what the "
            "skill does and when to use it")


def test_every_skill_states_the_three_device_safety_rules():
    """`device-safety.md:6-12` is not optional in a procedure that writes the Module.

    A skill is a procedure an agent follows instead of reading the standards, so a rule the
    skill omits is a rule that does not reach the device. These three are the ones whose
    omission costs either the user's flash or their unsaved edit.
    """
    for path in SKILLS:
        text = path.read_text(encoding="utf-8")
        for what, pattern in REQUIRED_SAFETY_CONTENT.items():
            assert pattern.search(text), (
                f"{path.parent.name}/SKILL.md does not state {what}. device-safety.md:6-12 "
                "requires it, and an agent following this skill will not read the standard")


def test_no_skill_restates_a_device_fact_the_tools_serve():
    """Criterion 21, in its computable form: no un-allowlisted wire number in a skill.

    All three skills open by declaring they hold no device facts of their own. A pasted
    column map, stream id or poke id breaks that promise silently: it reads as authoritative
    and goes stale while the tools that serve the same fact stay current.
    """
    offenders = []
    for path in SKILLS:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            remainder = line
            for allowed in ALLOWED_WIRE_PHRASES:
                remainder = remainder.replace(allowed, "")
            for hit in WIRE_FACT.findall(remainder):
                offenders.append(f"{path.parent.name}:{lineno} {hit!r} in {line.strip()!r}")

    assert not offenders, (
        "a skill names a wire number instead of routing the fact through get_knowledge, "
        "get_recipes or search_factory_presets (criterion 21). The only allowed phrases are "
        f"{ALLOWED_WIRE_PHRASES}, each because no typed tool serves it:\n  "
        + "\n  ".join(offenders))


def test_skills_are_ascii_and_carry_no_hardcoded_date():
    """Two text properties that rot a skill rather than break it.

    Non-ASCII first: `coding-style.md` keeps this project ASCII throughout, and a smart
    quote or an em dash arrives invisibly through a copy-paste. A hardcoded date second: a
    skill is a standing procedure, so a date in it is either a device-test tag that belongs
    in `RECIPES.md` or a claim about currency that stops being true without anything
    failing.
    """
    for path in SKILLS:
        raw = path.read_bytes()
        non_ascii = sorted({byte for byte in raw if byte > 127})
        assert not non_ascii, (
            f"{path.parent.name}/SKILL.md carries non-ASCII bytes {non_ascii}; this "
            "project is ASCII throughout and these arrive invisibly through a paste")

        dates = re.findall(r"\b20\d\d-\d\d-\d\d\b", raw.decode("ascii"))
        assert not dates, (
            f"{path.parent.name}/SKILL.md hardcodes the date(s) {dates}. A skill is a "
            "standing procedure; a dated device observation belongs in RECIPES.md, where "
            "test-writing.md:14-16 requires the date and the preset together")
