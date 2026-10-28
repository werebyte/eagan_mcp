"""send_preset_file's pre-scan screens the wrong controllers.

What it screens today (server.py:170-175), all on ch16:
  cc109 == 8   CC_COMMAND + CMD_STORE_CONFIG = ccTask curGloToFlash. A true positive, but
               it stores GLOBAL SETTINGS, not a preset - the least relevant of the three.
  cc57         CC_PRESET_LSB. Actually ccAnlysSlot, docs/HakenMidi.h:809, "specify analysis
               slot number, follows s_AnlysName". Stores nothing. FALSE POSITIVE.
  cc58         CC_PRESET_MSB. Actually UNDEFINED, docs/HakenMidi.h:214. FALSE POSITIVE.

What it does NOT screen, and must:
  cc112        ccStore, docs/HakenMidi.h:475, "store flash". The package already carries the
               constant as haken.CC_STORE_LO = 112, and haken.store_user_slot_msgs emits
               exactly cc0 / cc32 / cc112 to write a user slot.
  cc0 == 127   catSSlot, the SYSTEM-slot store path. CLAUDE.md and device-safety.md both
               forbid sending it outright.

So the function blocks two harmless controllers and lets both real store paths through,
while its own docstring promises it "Refuses files containing store-to-flash commands" and
validation.md:12 cites it as the project's exemplary whole-payload pre-scan.

DEVICE SAFETY IN THESE TESTS
----------------------------
conn.send is replaced in every test here. A test must never depend on "no device happens
to be connected" for its safety: send_preset_file currently lets ch16 cc112 through, so on
a connected process the unpatched call would write flash. The spy also makes the real
assertion possible - validation.md:12's claim is that the whole payload is scanned "before
a single byte of MIDI is emitted", which is a statement about what was SENT, not about
which exception surfaced.
"""

import mido
import pytest

from eagan_mcp import haken, server


class SendSpy:
    """Stands in for conn.send and records every message instead of transmitting it."""

    def __init__(self):
        self.sent = []

    def __call__(self, message):
        self.sent.append(message)


@pytest.fixture
def spy(monkeypatch):
    s = SendSpy()
    monkeypatch.setattr(server.conn, "send", s)
    return s


def _write_mid(path, *messages):
    """A one-track .mid carrying the given messages, as _save_mid writes captures."""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    for m in messages:
        track.append(m)
    mid.save(str(path))
    return str(path)


def _cc16(control, value):
    return mido.Message("control_change", channel=haken.CH16, control=control, value=value)


# ---------- must be refused, and nothing may be emitted ----------

def test_prescan_refuses_ccstore(tmp_path, spy):
    """ch16 cc112 is ccStore - the user-slot store path."""
    path = _write_mid(tmp_path / "store.mid", _cc16(haken.CC_STORE_LO, 7))
    with pytest.raises(RuntimeError, match="refus"):
        server.send_preset_file(path)
    assert spy.sent == [], "emitted MIDI before refusing"


def test_prescan_refuses_the_full_user_slot_store_sequence(tmp_path, spy):
    """The exact three messages haken.store_user_slot_msgs emits for user slot 3."""
    path = _write_mid(tmp_path / "slot3.mid", *haken.store_user_slot_msgs(3))
    with pytest.raises(RuntimeError, match="refus"):
        server.send_preset_file(path)
    assert spy.sent == [], "emitted MIDI before refusing"


def test_prescan_refuses_the_system_slot_path(tmp_path, spy):
    """ch16 cc0 = 127 is catSSlot, the system-slot path. Never to be sent."""
    path = _write_mid(tmp_path / "system.mid", _cc16(haken.CC_CATEGORY, 127))
    with pytest.raises(RuntimeError, match="refus"):
        server.send_preset_file(path)
    assert spy.sent == [], "emitted MIDI before refusing"


def test_prescan_refuses_a_store_hidden_after_benign_traffic(tmp_path, spy):
    """The scan must complete over the WHOLE file before the first byte goes out.

    validation.md:12: a multi-part payload is pre-scanned in full "before a single byte of
    MIDI is emitted". A store command in the last message must still stop the first one.
    """
    path = _write_mid(
        tmp_path / "late_store.mid",
        _cc16(haken.CC_CATEGORY, 126),          # edit buffer, harmless
        _cc16(haken.CC_TEXT, 0),                # a text stream, harmless
        _cc16(haken.CC_STORE_LO, 7),            # the store, last
    )
    with pytest.raises(RuntimeError, match="refus"):
        server.send_preset_file(path)
    assert spy.sent == [], "emitted the leading messages before scanning the whole file"


def test_prescan_still_refuses_global_settings_to_flash(tmp_path, spy):
    """Control: cc109 = 8 was already screened and must stay screened."""
    path = _write_mid(tmp_path / "glo.mid", _cc16(haken.CC_COMMAND, haken.CMD_STORE_CONFIG))
    with pytest.raises(RuntimeError, match="refus"):
        server.send_preset_file(path)
    assert spy.sent == []


# ---------- must NOT be refused ----------

def test_prescan_does_not_refuse_the_analysis_slot_controller(tmp_path, spy):
    """ch16 cc57 is ccAnlysSlot. It stores nothing and must not be refused."""
    message = _cc16(57, 4)
    path = _write_mid(tmp_path / "anlys.mid", message)
    result = server.send_preset_file(path, delay_ms=0)
    assert result["sent"] == 1
    assert len(spy.sent) == 1


def test_prescan_does_not_refuse_the_undefined_controller(tmp_path, spy):
    """ch16 cc58 is undefined in 10.81 and must not be refused."""
    path = _write_mid(tmp_path / "undef.mid", _cc16(58, 4))
    result = server.send_preset_file(path, delay_ms=0)
    assert result["sent"] == 1
    assert len(spy.sent) == 1


def test_prescan_allows_an_edit_buffer_select(tmp_path, spy):
    """Control: cc0 = 126 is catEdBuf - the only cc0 value present in the captures."""
    path = _write_mid(tmp_path / "editbuf.mid", _cc16(haken.CC_CATEGORY, 126))
    result = server.send_preset_file(path, delay_ms=0)
    assert result["sent"] == 1
    assert len(spy.sent) == 1
