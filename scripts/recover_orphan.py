"""Archive precisely the reconciled dead lease. Never evict a live/ambiguous owner.

This one-time recovery is not called automatically by the numerical supervisor.
The Windows exclusive handle is held through identity/liveness checks and rename.
"""

import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEASE = Path("D:/ai/projects/sera/runs/v3-batch-001/active.lock")
EXPECTED = "0a59780ffe5487f66d4167567e83286aed092027629480eeb343f08cf9cb441a"


def main():
    kernel = c.WinDLL("kernel32", use_last_error=True)
    prototypes = {
        "CreateFileW": ([w.LPCWSTR, w.DWORD, w.DWORD, c.c_void_p, w.DWORD, w.DWORD, w.HANDLE], w.HANDLE),
        "ReadFile": ([w.HANDLE, c.c_void_p, w.DWORD, c.POINTER(w.DWORD), c.c_void_p], w.BOOL),
        "OpenProcess": ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
        "CloseHandle": ([w.HANDLE], w.BOOL),
        "SetFileInformationByHandle": ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
    }
    for name, (args, result) in prototypes.items():
        getattr(kernel, name).argtypes = args
        getattr(kernel, name).restype = result
    handle = kernel.CreateFileW(str(LEASE), 0x80000000 | 0x10000, 0, None, 3, 0x80, None)
    if handle == c.c_void_p(-1).value:
        raise c.WinError(c.get_last_error())
    try:
        buffer = c.create_string_buffer(4096)
        size = w.DWORD()
        if not kernel.ReadFile(handle, buffer, len(buffer), c.byref(size), None):
            raise c.WinError(c.get_last_error())
        data = buffer.raw[:size.value]
        if hashlib.sha256(data).hexdigest() != EXPECTED:
            raise RuntimeError("Lease changed; leave it intact")
        record = json.loads(data)
        c.set_last_error(0)
        owner = kernel.OpenProcess(0x1000, False, record["pid"])
        error = c.get_last_error()
        if owner:
            kernel.CloseHandle(owner)
            raise RuntimeError("Lease owner is live; leave it intact")
        if error != 87:  # ERROR_INVALID_PARAMETER for a nonexistent PID, not ACCESS_DENIED
            raise RuntimeError(f"Owner liveness is ambiguous: Windows error {error}")
        destination = str((ROOT / "local" / "archived-orphan-6c7a173f.lock").resolve())
        if Path(destination).exists():
            raise RuntimeError("Preserve the existing recovery archive")
        class Rename(c.Structure):
            _fields_ = [("replace", w.BOOL), ("root", w.HANDLE), ("length", w.DWORD),
                        ("name", w.WCHAR * len(destination))]
        rename = Rename()
        rename.replace = False
        rename.root = None
        rename.length = len(destination.encode("utf-16-le"))
        rename.name = destination
        if not kernel.SetFileInformationByHandle(handle, 3, c.byref(rename), c.sizeof(rename)):
            raise c.WinError(c.get_last_error())
        print(json.dumps({"archived": destination, "sha256": EXPECTED,
                          "owner_pid": record["pid"], "owner_absence_error": error,
                          "stopped_processes": [], "method": "exclusive-handle rename"}))
    finally:
        kernel.CloseHandle(handle)


if __name__ == "__main__":
    main()
