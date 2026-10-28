"""D9.1: `_grep`'s hit path is relative to a caller-supplied root.

`_grep` keyed its hit dicts on `fp.name` alone. That is lossless for the two existing
callers - `search_docs` globs `docs/*.txt` plus `docs/HakenMidi.h`, and
`search_preset_descriptions` globs `Descriptions/*.txt`, both FLAT directories - but
`get_knowledge` serves a nested tree (`knowledge/model.md` beside
`knowledge/modules/biqbank.md`), where `fp.name` makes `modules/biqbank.md`
indistinguishable from any same-named file elsewhere.

Three earlier artifacts framed the `root` parameter as a breaking return-shape change to
`search_docs` and `search_preset_descriptions`. It is not: for a flat directory
`fp.relative_to(root).as_posix() == fp.name`, so those hit dicts come out byte-identical.
`test_flat_directory_hit_paths_are_unchanged` is what keeps that true - it asserts the
whole dict, not merely that a hit was returned.

Both silent failure modes of the path expression are pinned too:
`relative_to()` returns a `Path`, which is not JSON-serialisable through MCP, and `str()`
on a Windows `Path` yields `modules\\biqbank.md`, which would not match
`get_knowledge`'s forward-slash topic keys. Hence `as_posix()`, asserted on both counts.

SCOPE OF THIS SUITE
-------------------
Pure filesystem behaviour on `tmp_path`. Nothing here touches the Module, needs
`HAKEN_EDITOR_DIR`, or says anything about what the firmware does.
"""

from pathlib import Path

from eagan_mcp import server


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_flat_directory_hit_paths_are_unchanged(tmp_path):
    """For a flat directory the hit dicts are byte-identical to the pre-root ones."""
    first = _write(tmp_path / "guide.txt", "intro\nthe sF column is throat\noutro\n")
    second = _write(tmp_path / "other.txt", "sF column again\n")
    files = [first, second]

    hits = server._grep(files, "sF column", max_hits=10, context=1, root=tmp_path)

    # The pre-root implementation keyed on `fp.name`; reconstruct that exact shape.
    assert hits == [
        {"file": "guide.txt", "line": 2, "snippet": "intro\nthe sF column is throat\noutro"},
        {"file": "other.txt", "line": 1, "snippet": "sF column again"},
    ]
    for fp, hit in zip(files, hits):
        assert hit["file"] == fp.name
        assert fp.relative_to(tmp_path).as_posix() == fp.name


def test_nested_tree_paths_are_distinguishable(tmp_path):
    """`knowledge/modules/x.md` and `knowledge/x.md` must not collapse."""
    root = tmp_path / "knowledge"
    top = _write(root / "biqbank.md", "sF is the throat formant\n")
    nested = _write(root / "modules" / "biqbank.md", "sF is the throat formant\n")

    hits = server._grep([top, nested], "sF", max_hits=10, context=0, root=root)

    assert [h["file"] for h in hits] == ["biqbank.md", "modules/biqbank.md"]
    assert len({h["file"] for h in hits}) == 2, "same-named files collapsed into one key"


def test_hit_file_value_is_a_str_not_a_path(tmp_path):
    """The value must be a `str` with forward slashes, not a `Path` and not `modules\\x.md`."""
    root = tmp_path / "knowledge"
    nested = _write(root / "modules" / "biqbank.md", "sF is the throat formant\n")

    hits = server._grep([nested], "sF", max_hits=10, context=0, root=root)

    assert len(hits) == 1
    value = hits[0]["file"]
    assert isinstance(value, str), f"{type(value).__name__} is not JSON-serialisable through MCP"
    assert not isinstance(value, Path)
    assert value == "modules/biqbank.md"
    assert "\\" not in value, "a backslash separator would not match the topic keys"
