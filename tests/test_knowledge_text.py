"""The 23 shipped knowledge documents as text, not as a topic table.

WHY THIS FILE EXISTS (the G24 gap analysis)
-------------------------------------------
`tests/test_knowledge_topics.py` owns the `KNOWLEDGE_TOPICS` allowlist and the bijection
between a topic and a file; `tests/test_shipped_data.py` owns the shipped JSON. The
markdown *content* was unowned, and it is about to be edited: the citation repairs rewrite
roughly thirty `RECIPES.md:<line>` references across these documents, and a repair pass over
23 files is exactly where a smart quote or an em dash arrives invisibly through a paste.
These documents are served verbatim to a calling agent by `get_knowledge` and are shipped
inside the wheel, so a byte that breaks an ASCII read breaks the tool, not a rendering.

WHAT THESE TESTS DO AND DO NOT ESTABLISH
----------------------------------------
Text properties of committed package data, nothing more. Nothing here opens a MIDI port,
touches the Module, or reads `HAKEN_EDITOR_DIR`, `docs/` or `captures/`, and a green run
says nothing about what the firmware does or about whether any sentence in these documents
is *true* - the device claims in them are corpus-derived or header-derived and carry their
own evidence markers, which no offline test can check.
"""

import re
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "eagan_mcp" / "knowledge"
DOCUMENTS = sorted(KNOWLEDGE_DIR.rglob("*.md"))


def test_every_knowledge_document_is_ascii():
    """`get_knowledge` serves these bytes to an agent; a non-ASCII one is a defect.

    Reported per file with the offending byte values and the first line each appears on, so
    a failure after an editing pass names the file to fix rather than the directory.
    """
    assert DOCUMENTS, f"no markdown documents found under {KNOWLEDGE_DIR}"

    offenders = []
    for path in DOCUMENTS:
        raw = path.read_bytes()
        bad = sorted({byte for byte in raw if byte > 127})
        if not bad:
            continue
        lineno = next(i for i, line in enumerate(raw.splitlines(), 1)
                      if any(byte > 127 for byte in line))
        offenders.append(f"{path.relative_to(KNOWLEDGE_DIR).as_posix()}: "
                         f"bytes {bad}, first at line {lineno}")

    assert not offenders, (
        "a shipped knowledge document carries non-ASCII bytes. This project is ASCII "
        "throughout and these documents are served verbatim through get_knowledge:\n  "
        + "\n  ".join(offenders))


def test_every_knowledge_document_opens_with_a_heading_and_has_a_body():
    """A document with no title or no body is a shipped file an agent cannot use.

    `get_knowledge` returns the document - or, with a query, its matching sections - so the
    heading is the only thing telling the caller what it just received. An empty or
    untitled card passes the topic-table bijection in `tests/test_knowledge_topics.py`
    because the file exists; only its content shows the hole.
    """
    offenders = []
    for path in DOCUMENTS:
        lines = [line for line in path.read_text(encoding="ascii").splitlines() if line.strip()]
        name = path.relative_to(KNOWLEDGE_DIR).as_posix()
        if not lines:
            offenders.append(f"{name}: empty")
        elif not lines[0].startswith("# "):
            offenders.append(f"{name}: first non-blank line is {lines[0][:60]!r}, not an H1")
        elif len(lines) < 5:
            offenders.append(f"{name}: {len(lines)} non-blank lines - a title and no body")

    assert not offenders, (
        "a shipped knowledge document has no usable title or no body:\n  "
        + "\n  ".join(offenders))


RESEARCH_PATH = re.compile(
    r"analysis/findings/[\w.-]+|analysis/synthesis\.md|outputs/research-report\.md"
    r"|analysis/research-[\w./-]+")


def test_every_doc_citing_the_research_tree_says_it_is_not_shipped():
    """102 citations point into `.maister/tasks/`, which `.gitignore` excludes.

    They are kept deliberately - deleting them would erase the provenance of claims genuinely
    derived there - but on a fresh clone or a pip install those paths resolve to nothing, and an
    agent reading `patterns.md` was being sent to a file it cannot open. The acceptance test
    found this class of defect in the read mechanism; this is the same shape.

    So the rule is: a document may cite the research pass, but it must also tell the reader the
    citation is unresolvable and what ships instead. The full explanation lives once in
    `modules/index.md`; everything else carries a pointer to it.
    """
    docs = sorted(KNOWLEDGE_DIR.rglob("*.md"))
    assert docs, "no knowledge documents found"
    offenders = []
    for path in docs:
        text = path.read_text(encoding="utf-8")
        if not RESEARCH_PATH.search(text):
            continue
        if "not shipped" not in text:
            offenders.append(path.relative_to(KNOWLEDGE_DIR).as_posix())
    assert not offenders, (
        "these shipped documents cite the research tree without saying it is unresolvable: "
        f"{offenders}. Add the pointer used by the other cards, or cite the shipped data "
        "(factory_catalog.json / census.json / tools_spec.md / RESEARCH_REPORT.md) instead")


def test_the_explanation_itself_exists_and_names_the_shipped_alternatives():
    """A pointer is only useful if its target says something. Pins the content, not the heading."""
    index = (KNOWLEDGE_DIR / "modules" / "index.md").read_text(encoding="utf-8")
    assert "Research-pass citations are not shipped" in index
    for alternative in ("factory_catalog.json", "census.json", "RESEARCH_REPORT.md",
                        "tools_spec.md", "CLAUDE.md"):
        assert alternative in index, (
            f"the explanation must name {alternative} as what to use instead of an "
            "unresolvable research path")
