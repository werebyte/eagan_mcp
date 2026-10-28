"""Log everything arriving on a MIDI input to the console and a file.

Usage:  eagan_sniff [port_hint] [out_file]
Use it to record what the Module sends when you load a preset or change
something on it. To see what the *Editor* sends, you need a MIDI spy
between Editor and Module (see README)."""

import sys
import time

import mido

from .midi_io import _find, list_ports


def main():
    hint = sys.argv[1] if len(sys.argv) > 1 else "EaganMatrix"
    out_path = sys.argv[2] if len(sys.argv) > 2 else f"sniff_{int(time.time())}.log"
    name = _find(mido.get_input_names(), hint)
    if not name:
        print(f"No input matching '{hint}'. Ports: {list_ports()}")
        sys.exit(1)
    print(f"Listening on {name}, writing {out_path}. Ctrl+C to stop.")
    t0 = time.time()
    with mido.open_input(name) as port, open(out_path, "w") as f:
        try:
            for msg in port:
                if msg.type in ("clock", "active_sensing"):
                    continue
                line = f"{time.time() - t0:9.3f}  {msg.hex()}  {msg}"
                print(line)
                f.write(line + "\n")
                f.flush()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
