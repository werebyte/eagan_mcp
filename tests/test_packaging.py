"""The wheel boundary: what an install that is NOT a checkout can actually answer.

The knowledge base lives inside the package (`eagan_mcp/knowledge/`) specifically so that
`pip install eagan_mcp` answers every knowledge query with no repository on disk, no Haken
Editor installed and no build step - the operator's stated requirement is that this server
should one day run on an Android phone.

Verification found that goal enforced in one place and merely assumed in two others:

  * `get_recipes` read `PROJECT_DIR / "RECIPES.md"`, where `PROJECT_DIR` is `site-packages/`
    on a wheel. It raised `FileNotFoundError`, and all three shipped skills call it.
  * `search_docs` globbed `DOCS_DIR`, which is gitignored and not in the wheel, while `_grep`
    swallows `OSError` - so it returned `[]`, indistinguishable from "the guides say nothing",
    on the one evidence base the knowledge documents cite 1,081 times.

These tests turn the assumption into a guarantee. They are pure packaging and filesystem
checks: no device, no MIDI port, no `HAKEN_EDITOR_DIR`, no network.

SCOPE OF THIS SUITE
-------------------
Packaging and path resolution only. Nothing here touches the Module and a green run says
nothing about what the firmware does.
"""

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
KNOWLEDGE = REPO / "eagan_mcp" / "knowledge"


def _build_wheel(dest: Path) -> Path:
    """Build the wheel with `uv build`. `pip` and `python -m build` are absent from this venv."""
    proc = subprocess.run(["uv", "build", "--wheel", "--out-dir", str(dest)],
                          cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:                      # uv missing, or a locked file on Windows
        pytest.skip(f"uv build unavailable: {proc.stderr.strip()[:200]}")
    wheels = sorted(dest.glob("*.whl"))
    assert wheels, "uv build reported success but produced no wheel"
    return wheels[-1]


def test_wheel_carries_every_knowledge_document_and_artifact(tmp_path):
    """The shipped data must survive packaging, including now that `[tool.hatch.build]` exists.

    `pyproject.toml` gained a `force-include` section so `RECIPES.md` ships inside the
    package. Adding any `[tool.hatch.build]` table can narrow hatchling's default file
    discovery, which would silently drop `eagan_mcp/knowledge/` - the exact failure this
    asserts against. Counted from disk rather than hardcoded, so adding a card cannot make
    this test stale.
    """
    on_disk_md = {p.relative_to(KNOWLEDGE).as_posix() for p in KNOWLEDGE.rglob("*.md")}
    on_disk_json = {p.name for p in KNOWLEDGE.glob("*.json")
                    if p.name != "factory_catalog_full.json"}
    assert len(on_disk_md) == 23, (
        f"expected 23 knowledge documents on disk, found {len(on_disk_md)}; update this "
        "count deliberately if a document was added or removed")

    names = set(zipfile.ZipFile(_build_wheel(tmp_path)).namelist())
    in_wheel = {n[len("eagan_mcp/knowledge/"):] for n in names
                if n.startswith("eagan_mcp/knowledge/")}

    missing_md = on_disk_md - in_wheel
    assert not missing_md, f"the wheel is missing knowledge documents: {sorted(missing_md)}"
    missing_json = on_disk_json - in_wheel
    assert not missing_json, f"the wheel is missing shipped artifacts: {sorted(missing_json)}"
    assert "recipes.md" in in_wheel, (
        "RECIPES.md is not force-included into the package; get_recipes will raise "
        "FileNotFoundError on a wheel install and all three skills call it")
    assert "factory_catalog_full.json" not in in_wheel, (
        "the 5.4 MB regenerable catalog must stay out of the wheel (.gitignore:20)")


def test_read_only_tools_answer_from_a_wheel_with_no_repository(tmp_path):
    """The mobility claim, executed rather than asserted.

    Extracts the wheel somewhere with no checkout, no `docs/` and no `HAKEN_EDITOR_DIR`,
    then calls the read-only tools in a subprocess, because the point is which files the
    INSTALLED package resolves and an already-imported `eagan_mcp` would mask that.

    The `__file__` assertion inside the probe is load-bearing and earned: the first version
    of this test passed `PYTHONPATH` with `-I`, and **isolated mode ignores `PYTHONPATH`** -
    so the probe imported the venv's installed `eagan_mcp` (which resolves to the repo),
    found the real `docs/`, and reported that `search_docs` had not failed. The test was
    measuring the repo while claiming to measure the wheel.
    """
    site = tmp_path / "site"
    zipfile.ZipFile(_build_wheel(tmp_path)).extractall(site)
    assert not (site / "RECIPES.md").exists(), "fixture is wrong: a repo root leaked in"
    assert not (site / "docs").exists(), "fixture is wrong: docs/ leaked in"

    probe = (
        "import json, sys; sys.argv = ['x']\n"
        f"sys.path.insert(0, {str(site)!r})\n"
        "from eagan_mcp import server as s\n"
        f"assert s.__file__.startswith({str(site)!r}), (\n"
        "    'the probe imported %r instead of the extracted wheel; this test proves nothing'\n"
        "    % s.__file__)\n"
        "unwrap = lambda t: getattr(t, 'fn', t)\n"
        "out = {\n"
        "    'recipes': len(unwrap(s.get_recipes)()),\n"
        "    'topics': unwrap(s.get_knowledge)()['count'],\n"
        "    'presets': len(unwrap(s.search_factory_presets)(text='bowed')),\n"
        "    'rtmidi_at_import': 'rtmidi' in sys.modules,\n"
        "    'docs_dir': str(s.DOCS_DIR),\n"
        "}\n"
        "try:\n"
        "    unwrap(s.search_docs)('matrix')\n"
        "    out['docs_failed_loudly'] = False\n"
        "except RuntimeError:\n"
        "    out['docs_failed_loudly'] = True\n"
        "print(json.dumps(out))\n"
    )
    proc = subprocess.run([sys.executable, "-c", probe],
                          capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, (
        f"the read-only tools do not work from a wheel install:\n{proc.stderr[-1500:]}")
    got = json.loads(proc.stdout.strip().splitlines()[-1])

    assert got["docs_dir"].startswith(str(site)), (
        f"DOCS_DIR resolved to {got['docs_dir']!r}, outside the extracted wheel - the probe "
        "is measuring some other installation")
    assert got["recipes"] > 1000, (
        "get_recipes returned almost nothing from a wheel install; the force-included "
        "recipes.md is missing or the fallback in get_recipes was removed")
    assert got["topics"] == 23, f"get_knowledge served {got['topics']} topics, expected 23"
    assert got["presets"] > 0, "search_factory_presets answered nothing from shipped data"
    assert got["docs_failed_loudly"], (
        "search_docs returned instead of raising when docs/ is absent. An empty result must "
        "mean 'the guides do not say that', never 'the guides are not installed' - every [G] "
        "citation in the knowledge base points into docs/")
    assert not got["rtmidi_at_import"], (
        "importing eagan_mcp.server now loads rtmidi. mido defers its backend and "
        "EmConnection.__init__ opens no port, which is what keeps the package importable "
        "on a host with no MIDI backend built")


def test_no_shipped_file_carries_a_developer_path(tmp_path):
    """An absolute path belonging to whoever built the wheel must never ship inside it.

    HAKEN_EDITOR_DIR is the one path-valued setting, it is needed only to REBUILD the shipped
    JSON artifacts, and reading them needs nothing. So it takes its value from the environment
    with no default at all: a default would be correct on exactly one machine, and on every
    other one it would fail pointing somewhere the user has never heard of instead of naming
    the variable to set.
    """
    wheel = _build_wheel(tmp_path)
    with zipfile.ZipFile(wheel) as zf:
        offenders = []
        for name in zf.namelist():
            if not name.endswith((".py", ".md", ".json", ".txt")):
                continue
            blob = zf.read(name)
            # b"\x5c" is a backslash, written as an escape so that no shell, heredoc or sed
            # replacement can mangle it on the way into this file.
            for needle in (b"\x5cUsers", b"/Users/", b"PycharmProjects", b"OneDrive"):
                if needle in blob:
                    offenders.append(f"{name} contains {needle.decode('latin1')!r}")
    assert not offenders, (
        "shipped files carry a developer-specific path: " + "; ".join(offenders) +
        ". Use an environment variable with no default and an error that names it")


def test_haken_audio_is_credited_for_the_shipped_factory_data():
    """Haken Audio's permission (Edmund Eagan, 2026-10-30) came with one request: credit them.

    The credit lives in three places a user or an agent will actually meet: the LICENSE
    carve-out that keeps the data out of the MIT grant, the README, and the docstrings of the
    two tools that serve the data. Losing any of them silently breaks the condition.
    """
    licence = (REPO / "LICENSE").read_text(encoding="utf-8")
    assert "Carve-out 3" in licence and "Haken Audio" in licence
    assert "descriptions.json" in licence and "permission" in licence
    assert "MIT grant above does not extend to these files" in licence

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "## Credits" in readme and "Haken Audio" in readme

    from eagan_mcp import server
    for tool in (server.search_preset_descriptions, server.search_factory_presets):
        doc = getattr(tool, "fn", tool).__doc__
        assert "Haken Audio" in doc and "permission" in doc, tool
