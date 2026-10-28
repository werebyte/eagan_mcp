"""Thin MIDI layer over mido/rtmidi: ports, threading and buffering only.
Protocol-agnostic on purpose - all Haken-specific encoding lives in haken.py."""

import threading
import time
from collections import deque

import mido

DEFAULT_PORT_HINT = "EaganMatrix"


def list_ports() -> dict:
    return {"inputs": mido.get_input_names(), "outputs": mido.get_output_names()}


def _find(names: list[str], hint: str) -> str | None:
    hint_l = hint.lower()
    for n in names:
        if hint_l in n.lower():
            return n
    return None


class EmConnection:
    def __init__(self):
        self.in_port = None
        self.out_port = None
        self._buffer: deque = deque(maxlen=20000)
        self._lock = threading.Lock()

    @property
    def is_open(self) -> bool:
        return self.in_port is not None and self.out_port is not None

    def open(self, hint: str = DEFAULT_PORT_HINT) -> dict:
        self.close()
        in_name = _find(mido.get_input_names(), hint)
        out_name = _find(mido.get_output_names(), hint)
        if not in_name or not out_name:
            raise RuntimeError(
                f"No in/out port matching '{hint}'. Ports: {list_ports()}. "
                "Is the Haken Editor open? On Windows it may hold the port exclusively."
            )
        self.in_port = mido.open_input(in_name, callback=self._on_msg)
        self.out_port = mido.open_output(out_name)
        return {"input": in_name, "output": out_name}

    def close(self):
        for p in (self.in_port, self.out_port):
            if p is not None:
                p.close()
        self.in_port = self.out_port = None

    def _on_msg(self, msg):
        with self._lock:
            self._buffer.append((time.time(), msg))

    def clear(self):
        with self._lock:
            self._buffer.clear()

    def drain(self) -> list:
        with self._lock:
            items = list(self._buffer)
            self._buffer.clear()
        return items

    def send(self, msg: mido.Message):
        if self.out_port is None:
            raise RuntimeError("Not connected. Call connect first.")
        self.out_port.send(msg)

    def listen(self, seconds: float, skip_realtime: bool = True) -> list:
        """Wait `seconds`, then return everything buffered - WITHOUT clearing first.

        This used to call clear() before sleeping, which raced every request-then-read
        caller in server.py: they do clear() -> send request -> listen(), and the device
        answers in milliseconds, so the reply was discarded by this clear() before the
        sleep even started. Measured on the device 2026-10-27: a ping reply (cc109=12,
        cc111, cc118, cc114) was being thrown away every time, which is why get_status
        reported nothing. Clearing is the CALLER's job, before it sends its request.
        """
        time.sleep(seconds)
        items = self.drain()
        if skip_realtime:
            items = [(t, m) for t, m in items if m.type not in ("clock", "active_sensing")]
        return items


def msg_to_dict(msg: mido.Message) -> dict:
    d = msg.dict()
    if d.get("type") == "sysex":
        d["data"] = list(d["data"])
    return d


def dict_to_msg(d: dict) -> mido.Message:
    d = dict(d)
    t = d.pop("type")
    return mido.Message(t, **d)
