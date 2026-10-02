"""Run one command while holding machine-wide slots (scripts/governor.py), at below-normal priority:

  python scripts/slot_run.py --name t1-tests --slots 1 -- python -m pytest tests/core/test_curve_size_bound.py
Waits until the slots are free; holds them for the command's whole life; frees them when it ends (a crashed wrapper's
slots are reclaimed by the next taker, because their process is gone). Every one-off job of either session (probes,
tests, reports) goes through this, so the machine never runs more busy processes than the limit.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import governor  # noqa: E402


POLL = 30                        # seconds between machine checks while the command runs


def run(cmd, name='one-off', slots=1, poll=POLL, state=None, max_pause=None):
    """Hold the slots, run the command, and keep checking the machine (independent review, C1). On a critical reading or on
    battery the command's whole process tree is PAUSED by its exact id (2026-09-25, the author: no lost progress) and
    resumed once the machine is below HOT; only a pause longer than max_pause (governor.MAX_PAUSE) stops it, and the
    exit code then says so (-9). Returns the command's exit code."""
    max_pause = governor.MAX_PAUSE if max_pause is None else max_pause
    state = state or governor.state
    held = []
    try:
        for _ in range(slots):
            held.append(governor.take_slot(name))
        flags = 0x4000 if sys.platform == 'win32' else 0                   # below-normal priority
        child = subprocess.Popen(cmd, creationflags=flags)
        while True:
            try:
                return child.wait(timeout=poll)
            except subprocess.TimeoutExpired:
                pass
            s = state()[0]
            if s == 'critical':
                pids = governor.suspend_tree(child.pid)
                print(f'slot_run {name}: machine critical (heat or battery), pausing pid {child.pid} and '
                      f'{len(pids) - 1} children where they stand', flush=True)
                t0 = time.monotonic()
                s, temp = state()[:2]
                while not governor.paused_ok(s, temp) and time.monotonic() - t0 < max_pause:
                    time.sleep(poll)
                    s, temp = state()[:2]
                if not governor.paused_ok(s, temp):
                    print(f'slot_run {name}: still too hot after {max_pause} s, stopping pid {child.pid}', flush=True)
                    governor.kill_tree(child.pid)
                    child.wait()
                    return -9
                governor.resume_tree(pids)
                print(f'slot_run {name}: resumed', flush=True)
    finally:
        for path in held:
            governor.free_slot(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='one-off')
    ap.add_argument('--slots', type=int, default=1)
    a, rest = ap.parse_known_args()
    cmd = rest[1:] if rest and rest[0] == '--' else rest
    if not cmd:
        ap.error('no command')
    sys.exit(run(cmd, a.name, a.slots))


if __name__ == '__main__':
    main()
