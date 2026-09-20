"""Independent Windows supervisor: exclusive lease, CPU affinity and 2 GiB job cap."""

import argparse
import ctypes as c
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.records import source_manifest, utc, write_json

LEASE = Path("D:/ai/projects/sera/runs/v3-batch-001/active.lock")
CAP = 2 * 1024 ** 3


class BasicLimit(c.Structure):
    _fields_ = [("user", c.c_int64), ("job_user", c.c_int64), ("flags", w.DWORD),
                ("min_ws", c.c_size_t), ("max_ws", c.c_size_t), ("processes", w.DWORD),
                ("affinity", c.c_size_t), ("priority", w.DWORD), ("scheduling", w.DWORD)]


class IoCounters(c.Structure):
    _fields_ = [(k, c.c_uint64) for k in ("read_ops", "write_ops", "other_ops", "read_bytes",
                                        "write_bytes", "other_bytes")]


class ExtendedLimit(c.Structure):
    _fields_ = [("basic", BasicLimit), ("io", IoCounters), ("process_cap", c.c_size_t),
                ("job_cap", c.c_size_t), ("peak_process", c.c_size_t), ("peak_job", c.c_size_t)]


class Accounting(c.Structure):
    _fields_ = [(k, c.c_int64) for k in ("user", "kernel", "period_user", "period_kernel")] + [
        (k, w.DWORD) for k in ("faults", "total_processes", "active_processes", "terminated")]


class ThreadEntry(c.Structure):
    _fields_ = [("size", w.DWORD), ("usage", w.DWORD), ("thread_id", w.DWORD),
                ("process_id", w.DWORD), ("base", w.LONG), ("delta", w.LONG), ("flags", w.DWORD)]


class Job:
    def __init__(self):
        self.k = c.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([c.c_void_p, w.LPCWSTR], w.HANDLE),
            "SetInformationJobObject": ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
            "QueryInformationJobObject": ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.c_void_p], w.BOOL),
            "GetCurrentProcess": ([], w.HANDLE),
            "GetProcessAffinityMask": ([w.HANDLE, c.POINTER(c.c_size_t), c.POINTER(c.c_size_t)], w.BOOL),
            "AssignProcessToJobObject": ([w.HANDLE, w.HANDLE], w.BOOL),
            "OpenProcess": ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
            "CloseHandle": ([w.HANDLE], w.BOOL),
            "CreateToolhelp32Snapshot": ([w.DWORD, w.DWORD], w.HANDLE),
            "Thread32First": ([w.HANDLE, c.POINTER(ThreadEntry)], w.BOOL),
            "Thread32Next": ([w.HANDLE, c.POINTER(ThreadEntry)], w.BOOL),
            "OpenThread": ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
            "ResumeThread": ([w.HANDLE], w.DWORD),
            "TerminateJobObject": ([w.HANDLE, w.UINT], w.BOOL),
            "SetThreadExecutionState": ([w.DWORD], w.DWORD),
        }
        for name, (args, result) in signatures.items():
            getattr(self.k, name).argtypes = args
            getattr(self.k, name).restype = result
        self.handle = self.k.CreateJobObjectW(None, None)
        self.check(self.handle)
        limits = ExtendedLimit()
        process_mask, system_mask = c.c_size_t(), c.c_size_t()
        self.check(self.k.GetProcessAffinityMask(self.k.GetCurrentProcess(), c.byref(process_mask),
                                                 c.byref(system_mask)))
        limits.basic.flags = 0x2000 | 0x200 | 0x10  # kill owned tree on close; job memory; affinity
        limits.basic.affinity = process_mask.value & -process_mask.value
        limits.job_cap = CAP
        self.check(self.k.SetInformationJobObject(self.handle, 9, c.byref(limits), c.sizeof(limits)))
        actual = self.sample()
        if actual["limit_bytes"] != CAP or actual["flags"] & 0x2210 != 0x2210:
            raise RuntimeError("Windows did not install the required resource limits")

    @staticmethod
    def check(result):
        if not result:
            raise c.WinError(c.get_last_error())
        return result

    def attach_and_resume(self, process):
        h = self.check(self.k.OpenProcess(0x101, False, process.pid))
        try:
            self.check(self.k.AssignProcessToJobObject(self.handle, h))
        finally:
            self.k.CloseHandle(h)
        snapshot = self.k.CreateToolhelp32Snapshot(4, 0)
        if snapshot == c.c_void_p(-1).value:
            raise c.WinError(c.get_last_error())
        resumed = 0
        try:
            entry = ThreadEntry()
            entry.size = c.sizeof(entry)
            more = self.k.Thread32First(snapshot, c.byref(entry))
            while more:
                if entry.process_id == process.pid:
                    thread = self.check(self.k.OpenThread(2, False, entry.thread_id))
                    try:
                        if self.k.ResumeThread(thread) == 0xffffffff:
                            raise c.WinError(c.get_last_error())
                        resumed += 1
                    finally:
                        self.k.CloseHandle(thread)
                more = self.k.Thread32Next(snapshot, c.byref(entry))
        finally:
            self.k.CloseHandle(snapshot)
        if not resumed:
            raise RuntimeError("No suspended worker thread was resumed")

    def sample(self):
        limits, account = ExtendedLimit(), Accounting()
        self.check(self.k.QueryInformationJobObject(self.handle, 9, c.byref(limits), c.sizeof(limits), None))
        self.check(self.k.QueryInformationJobObject(self.handle, 1, c.byref(account), c.sizeof(account), None))
        return {"limit_bytes": int(limits.job_cap), "flags": int(limits.basic.flags),
                "affinity": int(limits.basic.affinity), "peak_committed_bytes": int(limits.peak_job),
                "cpu_seconds": (account.user + account.kernel) / 1e7,
                "active_processes": int(account.active_processes),
                "total_processes": int(account.total_processes)}

    def close(self):
        self.k.CloseHandle(self.handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args()
    out = (ROOT / "runs" / options.attempt).resolve()
    if out.parent != ROOT / "runs" or out.exists():
        raise SystemExit("Use a fresh direct child of this lab's runs directory")
    out.mkdir(parents=True)
    owner = {"pid": os.getpid(), "token": uuid.uuid4().hex, "workstream": "sera-field",
             "created_utc": utc(), "output": str(out)}
    state = {"status": "STARTING", "started_utc": utc(), "sources": source_manifest(ROOT),
             "numerical_threads": 1, "memory_limit_bytes": CAP, "attempt": options.attempt,
             "command": options.command, "lease_acquired": False, "paid_compute": False}
    started = time.perf_counter()
    process = job = None
    returncode = 1
    try:
        with LEASE.open("x", encoding="utf-8") as handle:
            json.dump(owner, handle)
        state["lease_acquired"] = True
        job = Job()
        state["verified_limits_before_launch"] = job.sample()
        state["awake_requested"] = bool(job.k.SetThreadExecutionState(0x80000001))
        environment = {**os.environ, "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                       "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
                       "PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8",
                       "SERA_FIELD_SUPERVISED": owner["token"], "SERA_FIELD_ATTEMPT": str(out)}
        command = options.command[1:] if options.command[:1] == ["--"] else options.command
        with (out / "process.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen([sys.executable, "-X", "utf8", "-u", *command], cwd=ROOT,
                                       env=environment, stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=4)  # CREATE_SUSPENDED
            state["worker_pid"] = process.pid
            job.attach_and_resume(process)
            state["status"] = "RUNNING"
            while process.poll() is None:
                state["resources"] = job.sample()
                state["wall_seconds"] = time.perf_counter() - started
                write_json(out / "state.json", state)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
            returncode = process.returncode
            state["returncode"] = returncode
            state["status"] = "PASS" if returncode == 0 else "FAILED"
    except BaseException as error:
        state["status"] = "FAILED"
        state["error"] = f"{type(error).__name__}: {error}"
    finally:
        if process is not None and process.poll() is None:
            # Only the worker created by this invocation can be terminated here.
            process.kill()
            process.wait()
        if job is not None:
            state["resources"] = job.sample()
            job.k.SetThreadExecutionState(0x80000000)
            job.close()
        if state["lease_acquired"] and LEASE.exists():
            current = json.loads(LEASE.read_text())
            if current.get("token") == owner["token"] and current.get("pid") == owner["pid"]:
                LEASE.unlink()
                state["lease_released"] = True
            else:
                state["lease_released"] = False
        state["finished_utc"] = utc()
        state["wall_seconds"] = time.perf_counter() - started
        write_json(out / "state.json", state)
        with (ROOT / "runs" / "costs.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps({k: v for k, v in state.items() if k != "sources"}) + "\n")
    print(json.dumps({k: v for k, v in state.items() if k != "sources"}, indent=2))
    raise SystemExit(returncode)


if __name__ == "__main__":
    main()
