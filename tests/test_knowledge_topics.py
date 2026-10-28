"""D9.2 / A2.11: `get_knowledge`'s topic table is an allowlist, not a path join.

`read_docs` resolves its caller's string straight into the filesystem - `(DOCS_DIR / file)`
at `server.py:694` - so `read_docs("../eagan_mcp/server.py", 1)` reads whatever the caller
names. Repairing that tool is a `tools_spec.md` item; what this suite pins is that the new
tool does not reproduce the hole. `KNOWLEDGE_TOPICS` is one module-level dict consulted for
**both** the lookup and the refusal message, so a string that is not already a key cannot
reach the filesystem at all (`validation.md:26`, allowlists over blocklists; `validation.md:19`,
the message interpolates from the same table the check consults, so it cannot drift).

The allowlist is also pinned in the other direction. `minimal-implementation.md:12` forbids a
topic entry with no file behind it, and a knowledge document with no topic in front of it is
unreachable through the MCP - a shipped file nothing can read. Both directions are asserted,
so adding a card without a topic, or a topic without a card, fails here.

SCOPE OF THIS SUITE
-------------------
Pure filesystem and table behaviour over the committed package data. Nothing here touches the
Module, opens a MIDI port or needs `HAKEN_EDITOR_DIR`, which is the property that makes the
knowledge tools answerable on a phone with nothing installed but the package.
"""

import pytest

from eagan_mcp import server

# The knowledge base as shipped: `model`, `modules` (the index), 18 module cards, `patterns`,
# `pitfalls`, `worked-examples`. Spelled out rather than derived, so a card that silently
# disappears from the package fails here instead of shrinking the expectation with it.
EXPECTED_TOPIC_COUNT = 23


def test_every_topic_value_resolves_to_an_existing_file_under_knowledge_dir():
    """Criterion 8: 23 topics, each one a real file, and no card left unreachable."""
    topics = server.KNOWLEDGE_TOPICS
    assert len(topics) == EXPECTED_TOPIC_COUNT, (
        f"the allowlist holds {len(topics)} topics, expected {EXPECTED_TOPIC_COUNT}: "
        f"{sorted(topics)}")

    for topic, relative in topics.items():
        path = server.KNOWLEDGE_DIR / relative
        assert path.is_file(), (
            f"topic {topic!r} points at {relative!r}, which is not a file under "
            f"{server.KNOWLEDGE_DIR}; minimal-implementation.md:12 forbids a topic entry "
            "with nothing behind it")

    # The other direction: every shipped document is reachable through some topic.
    shipped = {fp.relative_to(server.KNOWLEDGE_DIR).as_posix()
               for fp in server.KNOWLEDGE_DIR.rglob("*.md")}
    unreachable = shipped - set(topics.values())
    assert not unreachable, (
        f"these knowledge documents ship but no topic serves them, so nothing can read "
        f"them through the MCP: {sorted(unreachable)}")

    # Index mode returns the flat envelope A2.11 fixes (`conventions.md:40`).
    index = server.get_knowledge()
    assert set(index) == {"topics", "index", "count"}
    assert index["count"] == EXPECTED_TOPIC_COUNT == len(index["topics"])
    assert sorted(index["topics"]) == sorted(topics)
    assert index["index"] == (server.KNOWLEDGE_DIR / "modules" / "index.md").read_text(
        encoding="utf-8")

    # One topic, no query: the whole document as `str`, exactly as `get_recipes` does.
    body = server.get_knowledge("model")
    assert isinstance(body, str)
    assert body == (server.KNOWLEDGE_DIR / "model.md").read_text(encoding="utf-8")

    # One topic plus a query: `_grep` hits, paths rooted at KNOWLEDGE_DIR.
    hits = server.get_knowledge("modules/biqmouth", query="sF")
    assert isinstance(hits, list)
    assert hits, "'sF' should hit somewhere in the BiqMouth card"
    assert all(hit["file"] == "modules/biqmouth.md" for hit in hits), (
        f"a query scoped to one topic must only return hits from that topic's file, got "
        f"{sorted({hit['file'] for hit in hits})}")


def test_unknown_topic_raises_with_the_full_topic_list():
    """`validation.md:19`: the refusal interpolates from the table the check consults."""
    with pytest.raises(ValueError) as excinfo:
        server.get_knowledge("biqbank")       # a real card, but not a real topic key
    message = str(excinfo.value)

    assert "biqbank" in message, "the refusal does not quote the rejected topic back"
    for topic in server.KNOWLEDGE_TOPICS:
        assert topic in message, (
            f"the refusal does not list the accepted topic {topic!r}; it must carry the "
            "full live list so the caller can correct the call without a second round trip")


def test_query_without_a_topic_raises():
    """A query needs a topic to be scoped to; index mode has nothing to grep."""
    with pytest.raises(ValueError) as excinfo:
        server.get_knowledge(query="sF")
    assert "topic" in str(excinfo.value).lower(), (
        f"the refusal must say a topic is required, got {str(excinfo.value)!r}")


def test_no_topic_value_escapes_knowledge_dir():
    """The traversal `read_docs` allows must be unreachable here, by construction."""
    for relative in server.KNOWLEDGE_TOPICS.values():
        resolved = (server.KNOWLEDGE_DIR / relative).resolve()
        assert resolved.is_relative_to(server.KNOWLEDGE_DIR.resolve()), (
            f"topic value {relative!r} resolves to {resolved}, outside KNOWLEDGE_DIR")
        assert ".." not in relative, f"topic value {relative!r} contains a parent reference"

    # The escapes a path join would honour are rejected as unknown topics instead: the
    # argument is a dict key, never a path fragment.
    escapes = ("../server.py", "..\\server.py", "../../RECIPES.md", "/etc/passwd",
               "model.md", "modules/../../server.py")
    for attempt in escapes:
        with pytest.raises(ValueError):
            server.get_knowledge(attempt)
        with pytest.raises(ValueError):
            server.get_knowledge(attempt, query="the")
