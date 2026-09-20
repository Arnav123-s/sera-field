"""One-time preservation of the verified, interrupted CONNECTED-002 lease.

No process is stopped. Both recorded PIDs must be nonexistent, not inaccessible.
An exclusive file handle protects identity checks and the non-replacing rename.
"""
import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEASE = Path('D:/ai/projects/sera/runs/v3-batch-001/active.lock')
EXPECTED = 'c3bb886fb352b67d9be8fa1c5840acae831b381c9121fec6c3ef5a85312b3275'
ARCHIVE = ROOT / 'local' / 'takeover-003' / 'interrupted-ag-lease.lock'


def main():
    k = c.WinDLL('kernel32', use_last_error=True)
    signatures = {
        'CreateFileW': ([w.LPCWSTR, w.DWORD, w.DWORD, c.c_void_p, w.DWORD, w.DWORD, w.HANDLE], w.HANDLE),
        'ReadFile': ([w.HANDLE, c.c_void_p, w.DWORD, c.POINTER(w.DWORD), c.c_void_p], w.BOOL),
        'OpenProcess': ([w.DWORD, w.BOOL, w.DWORD], w.HANDLE),
        'CloseHandle': ([w.HANDLE], w.BOOL),
        'SetFileInformationByHandle': ([w.HANDLE, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
    }
    for name, (args, result) in signatures.items():
        getattr(k, name).argtypes, getattr(k, name).restype = args, result
    handle = k.CreateFileW(str(LEASE), 0x80000000 | 0x10000, 0, None, 3, 0x80, None)
    if handle == c.c_void_p(-1).value:
        raise c.WinError(c.get_last_error())
    try:
        buffer, size = c.create_string_buffer(4096), w.DWORD()
        if not k.ReadFile(handle, buffer, len(buffer), c.byref(size), None):
            raise c.WinError(c.get_last_error())
        data = buffer.raw[:size.value]
        assert hashlib.sha256(data).hexdigest() == EXPECTED, 'Lease identity changed'
        lease = json.loads(data)
        state_path = Path(lease['output']) / 'state.json'
        state_bytes = state_path.read_bytes()
        state = json.loads(state_bytes)
        assert lease['pid'] == 14156 and state['worker_pid'] == 5504
        checks = {}
        for pid in (lease['pid'], state['worker_pid']):
            c.set_last_error(0)
            process = k.OpenProcess(0x1000, False, pid)
            error = c.get_last_error()
            if process:
                k.CloseHandle(process)
                raise RuntimeError(f'PID {pid} exists; leave lease intact')
            if error != 87:
                raise RuntimeError(f'PID {pid} ambiguous Windows status: {error}')
            checks[pid] = error
        ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        assert not ARCHIVE.exists(), 'Keep the earlier recovery record'
        (ARCHIVE.parent / 'ag-run-state-at-takeover.json').write_bytes(state_bytes)
        destination = str(ARCHIVE.resolve())
        class Rename(c.Structure):
            _fields_ = [('replace', w.BOOL), ('root', w.HANDLE), ('length', w.DWORD),
                        ('name', w.WCHAR * len(destination))]
        rename = Rename(False, None, len(destination.encode('utf-16-le')), destination)
        if not k.SetFileInformationByHandle(handle, 3, c.byref(rename), c.sizeof(rename)):
            raise c.WinError(c.get_last_error())
        receipt = {'lease_sha256': EXPECTED, 'archived': str(ARCHIVE),
                   'nonexistent_pids_windows_errors': checks, 'processes_stopped': [],
                   'preserved_run': lease['output'], 'cost_status': 'Last sample is a lower bound; supervisor interrupted',
                   'method': 'exclusive-handle identity check and non-replacing rename'}
        (ARCHIVE.parent / 'recovery.json').write_text(json.dumps(receipt, indent=2))
        print(json.dumps(receipt, indent=2))
    finally:
        k.CloseHandle(handle)


if __name__ == '__main__':
    main()
