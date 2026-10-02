"""Thermal governor: as much parallel work as this laptop takes while staying cool (it overheated on 2026-09-24).

Machine-wide slots (after the second crash, 2026-09-24 22:02, about ten busy processes across several runs, each with
its own governor, while the AC adapter dropped out): every busy process of either session holds one of SLOTS_LIMIT
slots (D:/ai/tools/slots; `limit.txt` there may lower it). A slot is a lock file created atomically, naming its
process; a slot whose process is gone is reclaimed. Workers take a slot per unit and wait when none is free; one-off
commands run through `scripts/slot_run.py`. On battery (AC offline) the state is critical: all work pauses.

Work is split into small, independent, resumable units (a unit = one output file, skipped if it already exists).
The governor keeps between 1 and --max-workers worker processes, each at below-normal priority:
  - every CHECK seconds it reads two signals readable without admin: the GPU temperature (the CPU and GPU share one
    cooling path; it holds itself at its 87 C target, slowdown at 97 C) and Windows' thermal-zone passive limit
    (100 = no thermal throttling; below 100 the machine is already slowing itself down to cool);
  - hot (GPU >= HOT or passive limit < 100): retire a worker after its current unit; cool (GPU <= COOL and no
    throttling): it may add one;
  - critical (GPU >= CRITICAL, passive limit < 80, or a GPU hardware slowdown): every worker stops until cool.
Memory: the whole process tree stays under MEMORY_BUDGET (2 GiB, the author's design budget): a worker is added only
if the tree's measured memory plus one more worker's fits.
Nothing is lost: units are atomic (written to .tmp, then renamed), so a retired or killed worker costs at most one
unit. Used by scripts/sera_dream.py; any job made of units can use `run_units`.
"""
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time

COOL, HOT, CRITICAL = 78, 84, 88        # GPU C (shares the cooling path): 67 idle after the crash; ~90 sustained preceded it
CHECK = int(os.environ.get('GOVERNOR_CHECK', '20'))
MEMORY_BUDGET = 2 * 1024 ** 3
SLOTS = os.environ.get('SERA_SLOTS', 'D:/ai/tools/slots')
SLOTS_LIMIT = 4                          # busy processes on the whole machine, both sessions (16 logical CPUs)


def slots_limit():
    try:
        with open(os.path.join(SLOTS, 'limit.txt')) as f:
            return max(1, min(SLOTS_LIMIT, int(f.read().strip())))
    except Exception:
        return SLOTS_LIMIT


def _alive(pid):
    if sys.platform == 'win32':
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)          # query limited information
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        return bool(ok) and code.value == 259                              # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def take_slot(name, wait=True, pid=None):
    """Hold one machine-wide slot for process `pid` (default: this one): returns its path, or None if wait=False and
    none is free. Stale slots (their process is gone) are reclaimed first. Hot (GPU >= HOT) offers one slot fewer,
    critical none, so the whole machine backs off together (after the second crash it ran at 83-84 C with 4 busy)."""
    pid = pid or os.getpid()
    os.makedirs(SLOTS, exist_ok=True)
    while True:
        limit, t = slots_limit(), temperature()
        if t is not None and t >= HOT:                    # hot: one slot fewer for new work (holders finish theirs)
            limit -= 1
        if (t is not None and t >= CRITICAL) or on_battery():   # independent review C1: no new work on battery (the 22:02
            limit = 0                                           # crash began with the AC adapter dropping out)
        with _mutex() as m:                               # count and take in one step: never above the limit
            live, free = 0, None
            for i in range(SLOTS_LIMIT):                  # every live slot counts, even one above a lowered limit
                path = os.path.join(SLOTS, f'slot-{i}.lock')
                if not os.path.exists(path):
                    free = path if free is None else free
                    continue
                try:
                    with open(path) as f:
                        owner = int(f.read().split()[0])
                except Exception:
                    live += 1
                    continue
                if _alive(owner):
                    live += 1
                else:
                    free_slot(path)                       # its process is gone
                    free = path if free is None else free
            if live < limit and free is not None and m.owned():     # B H-4: still ours (not broken while paused)
                with open(free, 'w') as f:
                    f.write(f'{pid} {name} {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
                return free
        if not wait:
            return None
        time.sleep(10)


class _mutex:
    """A short exclusive section across processes (a lock file; one older than 60 s is from a dead process)."""

    def __enter__(self):
        self.path = os.path.join(SLOTS, 'mutex')
        self.token = f'{os.getpid()} {os.urandom(8).hex()}'           # unique even within one clock tick
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, self.token.encode())
                os.close(fd)
                return self
            except (FileExistsError, PermissionError):         # Windows: a mutex being deleted reads as denied
                try:
                    if time.time() - os.path.getmtime(self.path) > 60:
                        os.remove(self.path)
                except OSError:
                    pass
                time.sleep(0.05)

    def owned(self):
        try:
            with open(self.path) as f:
                return f.read() == self.token
        except OSError:
            return False

    def __exit__(self, *exc):
        # B H-4: a holder paused past 60 s has its mutex broken as stale; on resuming it must not delete another
        # process's live mutex, so it removes only its own (checked by token)
        if self.owned():
            try:
                os.remove(self.path)
            except OSError:
                pass


def kill_tree(pid):
    """Stop one process and its children, by that exact process id (never by name or pattern)."""
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True)
    else:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


def paused_ok(s, t):
    """True when paused work may resume: not hot or critical, and the GPU below HOT - RESUME_MARGIN."""
    return s in ('ok', 'cool') and (t is None or t < HOT - RESUME_MARGIN)


def _tree(pid):
    """pid and every descendant (one process listing)."""
    if sys.platform != 'win32':
        return [pid]
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command',
                              'Get-CimInstance Win32_Process | ForEach-Object { "$($_.ProcessId) $($_.ParentProcessId)" }'],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return [pid]
    kids = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            kids.setdefault(int(parts[1]), []).append(int(parts[0]))
    tree, todo = [], [pid]
    while todo:
        q = todo.pop()
        if q in tree:
            continue
        tree.append(q)
        todo += [k for k in kids.get(q, []) if k != q]
    return tree


def _nt(pids, fn):
    if sys.platform != 'win32':
        import signal
        for q in pids:
            try:
                os.kill(q, signal.SIGSTOP if fn == 'NtSuspendProcess' else signal.SIGCONT)
            except OSError:
                pass
        return
    import ctypes
    for q in pids:
        h = ctypes.windll.kernel32.OpenProcess(0x0800, False, q)          # PROCESS_SUSPEND_RESUME
        if h:
            getattr(ctypes.windll.ntdll, fn)(h)
            ctypes.windll.kernel32.CloseHandle(h)


def suspend_tree(pid):
    """Pause a process and its children where they stand (2026-09-25, the author: no lost progress to heat). By exact
    process id, never by name. Returns the ids paused, for resume_tree."""
    done = []
    for _ in range(10):                    # independent review (2): children spawned during the listing escape it, so suspend,
        new = [q for q in _tree(pid) if q not in done]     # list again, and repeat until no new process appears
        if not new:
            break
        _nt(new, 'NtSuspendProcess')
        done += new
    return done


def resume_tree(pids):
    _nt(pids, 'NtResumeProcess')


def free_slot(path):
    try:
        os.remove(path)
    except OSError:
        pass


def slots_in_use():
    try:
        return sorted(f for f in os.listdir(SLOTS) if f.endswith('.lock'))
    except OSError:
        return []


def _on_battery_raw():
    """True when the AC adapter is offline (Win32_Battery status 1 = discharging); None if unreadable."""
    if sys.platform != 'win32':
        return None
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command',
                              '(Get-CimInstance Win32_Battery | Select-Object -First 1).BatteryStatus'],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return int(out) == 1 if out else None
    except Exception:
        return None


SENSOR_TTL = {'temperature': 60, 'on_battery': 30, 'passive_limit': 60, 'gpu_hw_slowdown': 60}   # seconds
MAX_PAUSE = 6 * 3600             # a job paused this long by heat or battery is stopped after all
RESUME_MARGIN = 2                # resume paused work only below HOT - 2 (independent review (3): hysteresis to CRITICAL)


def _shared(name, read):
    """One reading per machine per SENSOR_TTL seconds, shared through SLOTS/sensors.json (2026-09-25). Each reading
    launches nvidia-smi or PowerShell, and every governor and every waiting job took its own every 10-30 s: that kept
    the idle GPU awake (P8, 8 W into the shared cooling path, 80 C with the CPU idle) and cost CPU itself."""
    path = os.path.join(SLOTS, 'sensors.json')
    now = time.time()
    try:
        with open(path) as f:
            v, at = json.load(f)[name]
        if 0 <= now - at <= SENSOR_TTL[name]:
            return v
    except Exception:
        pass
    try:
        os.makedirs(SLOTS, exist_ok=True)
        with _mutex():
            try:
                with open(path) as f:
                    cache = json.load(f)
            except Exception:
                cache = {}
            if name in cache and 0 <= time.time() - cache[name][1] <= SENSOR_TTL[name]:   # B H-5: another process
                return cache[name][0]                                                   # just read it
            v = read()
            cache[name] = [v, time.time()]
            tmp = f'{path}.{os.getpid()}.tmp'
            with open(tmp, 'w') as f:
                json.dump(cache, f)
            os.replace(tmp, path)
            return v
    except Exception:
        return read()


def temperature():
    return _shared('temperature', _temperature_raw)


def on_battery():
    """independent review of 9c744f8 (1): GetSystemPowerStatus, a microsecond call with no process spawned, so it is read fresh
    every time (an AC dropout is urgent). ACLineStatus 0 = offline (on battery), 1 = online, 255 = unknown."""
    if sys.platform == 'win32':
        try:
            import ctypes

            class SPS(ctypes.Structure):
                _fields_ = [('ACLineStatus', ctypes.c_ubyte), ('BatteryFlag', ctypes.c_ubyte),
                            ('BatteryLifePercent', ctypes.c_ubyte), ('SystemStatusFlag', ctypes.c_ubyte),
                            ('BatteryLifeTime', ctypes.c_ulong), ('BatteryFullLifeTime', ctypes.c_ulong)]
            s = SPS()
            if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s)):
                return None if s.ACLineStatus == 255 else s.ACLineStatus == 0
        except Exception:
            pass
    return _shared('on_battery', _on_battery_raw)


def passive_limit():
    return _shared('passive_limit', _passive_limit_raw)


def gpu_hw_slowdown():
    return _shared('gpu_hw_slowdown', _gpu_hw_slowdown_raw)


def _temperature_raw():
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return int(out.splitlines()[0])
    except Exception:
        return None


def _passive_limit_raw():
    """Lowest Windows thermal-zone passive limit in percent (100 = not throttling), or None."""
    if sys.platform != 'win32':
        return None
    try:
        out = subprocess.run(['powershell', '-NoProfile', '-Command',
                              '(Get-CimInstance Win32_PerfFormattedData_Counters_ThermalZoneInformation | '
                              'Measure-Object PercentPassiveLimit -Minimum).Minimum'],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return int(float(out))
    except Exception:
        return None


def _gpu_hw_slowdown_raw():
    """True when the GPU reports a hardware slowdown (0x8 HW slowdown, 0x40 HW thermal, 0x80 power brake)."""
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=clocks_throttle_reasons.active', '--format=csv,noheader'],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return bool(int(out.splitlines()[0], 16) & (0x8 | 0x40 | 0x80))
    except Exception:
        return False


def state():
    """('critical' | 'hot' | 'ok' | 'cool', gpu C, passive %).

    Corrected 2026-09-24 22:50: the earlier reading "87 C even with no job on it" was taken while CPU jobs ran (the GPU
    shares the CPU's cooling path); after the second crash, truly idle, it read 67 C. So it IS a load signal, and 90-91 C
    held for hours with the passive limit at 100% was already too hot: the thresholds were 91/94/96, now 78/84/88. The
    passive limit and GPU hardware slowdown stay as extra signals, and on battery all work pauses."""
    t, p = temperature(), passive_limit()
    if on_battery() or (t is not None and t >= CRITICAL) or (p is not None and p < 80) or gpu_hw_slowdown():
        return 'critical', t, p
    if (t is not None and t >= HOT) or (p is not None and p < 100):
        return 'hot', t, p
    if t is None and p is None:
        return 'ok', t, p                                        # sensors unreadable: hold, never add (fail safe)
    if (t is None or t <= COOL) and (p is None or p >= 100):
        return 'cool', t, p
    return 'ok', t, p


def rss(pid):
    """Resident memory of a process in bytes (Windows: working set via psapi), or 0 if unreadable."""
    if sys.platform != 'win32':
        try:
            with open(f'/proc/{pid}/statm') as f:
                return int(f.read().split()[1]) * os.sysconf('SC_PAGE_SIZE')
        except Exception:
            return 0
    import ctypes
    from ctypes import wintypes

    class PMC(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                    ('PeakWorkingSetSize', ctypes.c_size_t), ('WorkingSetSize', ctypes.c_size_t),
                    ('QuotaPeakPagedPoolUsage', ctypes.c_size_t), ('QuotaPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t), ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
                    ('PagefileUsage', ctypes.c_size_t), ('PeakPagefileUsage', ctypes.c_size_t)]
    h = ctypes.windll.kernel32.OpenProcess(0x1000 | 0x0010, False, pid)     # query limited info | vm read
    if not h:
        return 0
    try:
        c = PMC()
        c.cb = ctypes.sizeof(PMC)
        ok = ctypes.windll.psapi.GetProcessMemoryInfo(h, ctypes.byref(c), c.cb)
        return int(c.WorkingSetSize) if ok else 0
    finally:
        ctypes.windll.kernel32.CloseHandle(h)


def _lower_priority():
    try:
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)  # below normal
        else:
            os.nice(10)
    except Exception:
        pass


def _worker(job, todo, stop, done):
    os.environ.update(OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', NUMBA_NUM_THREADS='1')
    _lower_priority()
    while not stop.is_set():
        slot = take_slot(getattr(job, '__name__', 'unit'))                # machine-wide: wait for a free slot
        try:
            if stop.is_set():
                return
            try:
                unit = todo.get_nowait()
            except Exception:
                return
            job(unit)
            done.put(unit)
        finally:
            free_slot(slot)


def run_units(job, units, max_workers=3, log=print):
    """Run job(unit) for every unit, with 1..max_workers processes governed by temperature. job must be a top-level
    function (spawned processes import it) and must skip units already done."""
    todo, done = mp.Queue(), mp.Queue()
    for u in units:
        todo.put(u)
    total, finished = len(units), 0
    workers = []                                                     # (process, stop event)

    def add():
        stop = mp.Event()
        p = mp.Process(target=_worker, args=(job, todo, stop, done), daemon=True)
        p.start()
        workers.append((p, stop))

    add()
    started = time.monotonic()
    peak_mem = 0
    while finished < total:
        time.sleep(CHECK)
        while not done.empty():
            done.get()
            finished += 1
        workers[:] = [(p, s) for p, s in workers if p.is_alive()]
        s, t, p = state()
        if s == 'critical':
            # independent review C2: stop now, not after the unit. 2026-09-25 (the author: no lost progress): pause every worker
            # where it stands and resume it below HOT; only a pause longer than MAX_PAUSE stops them (units are
            # atomic, so then at most the units in progress are redone).
            log(f'governor: critical ({t} C, passive limit {p}%, battery {on_battery()}), pausing all work now')
            paused = [q for w, _ in workers for q in suspend_tree(w.pid)]
            t0 = time.monotonic()
            while not paused_ok(s, t) and time.monotonic() - t0 < MAX_PAUSE:
                time.sleep(60)
                s, t, p = state()
            if not paused_ok(s, t):
                log('governor: still too hot after MAX_PAUSE, stopping the paused workers')
                for w, stop in workers:
                    stop.set()
                    kill_tree(w.pid)
                workers.clear()
            else:
                resume_tree(paused)
                log(f'governor: resumed {len(paused)} paused processes at {t} C')
        if not workers and finished < total:
            add()
        elif s == 'hot' and len(workers) > 1:
            workers[-1][1].set()                                     # retire the newest after its current unit
        elif s == 'cool' and len(workers) < max_workers and finished + len(workers) < total:
            used = rss(os.getpid()) + sum(rss(w.pid) for w, _ in workers)
            per = used / (len(workers) + 1)
            if used + per <= MEMORY_BUDGET:
                add()
        peak_mem = max(peak_mem, rss(os.getpid()) + sum(rss(w.pid) for w, _ in workers))
        rate = finished / max(time.monotonic() - started, 1e-9) * 60
        log(f'governor: {finished}/{total} units, {len(workers)} workers, machine slots {len(slots_in_use())}/'
            f'{slots_limit()}, {t} C, passive {p}%, tree {peak_mem / 2**20:.0f} MiB peak, {rate:.1f} units/min')
    for p, s in workers:
        s.set()
