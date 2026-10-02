"""Keep this laptop cool (it overheated and crashed on 2026-09-24 at about 18:50).

Signals (governor.state): Windows' thermal-zone passive limit (below 100 = throttling), GPU hardware slowdown, and
the GPU temperature (this GPU holds itself at 87 C in P0 even when idle, so only >= 93 C counts as hot).
Use in a loop: sys.path.insert(0, 'scripts'); from heat_guard import cool_down; cool_down()  (between work units).
From a shell: python scripts/heat_guard.py   (prints the current state).
Rule (SESSIONS.md): pause while the machine is hot or throttling (governor.state), resume when cool.
"""
import subprocess
import sys
import time

HOT, COOL = 84, 78          # GPU C, as governor.py (corrected after the second crash: 67 idle, ~90 was too hot)


def temperature():
    """GPU temperature in degrees C, or None: the machine-wide shared reading (governor, 2026-09-25)."""
    import governor
    return governor.temperature()


def cool_down(log=print):
    """Return at once unless the machine is hot or throttling (governor.state); otherwise wait until it is cool."""
    import governor
    s, t, p = governor.state()
    if s in ('cool', 'ok'):
        return 0.0
    started = time.monotonic()
    while s not in ('cool', 'ok'):
        log(f'heat guard: {s} (GPU {t} C, passive limit {p}%), pausing 60 s')
        time.sleep(60)
        s, t, p = governor.state()
    return time.monotonic() - started


if __name__ == '__main__':
    import governor
    print(governor.state())
    sys.exit(0)
