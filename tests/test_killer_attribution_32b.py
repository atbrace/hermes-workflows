#!/usr/bin/env python3
"""hw-32b: SIGTERM sender attribution — the runner records the kernel-provided
sender (siginfo.si_pid resolved to pid/cmd/uid) at signal time, appended as
fields to the est-6226 class constant. The class constant stays the verbatim
prefix (every pre-32b reader keeps matching); 'gateway restart' is still never
claimed — the record names the MEASURED sender process, not an interpretation.

Rows (Linux only; the signalfd leg is linux):
  A  a /bin/kill -TERM lands runner_exit.json whose reason keeps the class
     constant as prefix AND carries killer_pid=<int> killer_cmd containing the
     kill argv; the process still dies the default SIGTERM (rc -15 — the door's
     reaper semantics unchanged).
  B  a clean exit writes no SIGTERM runner_exit record (atexit path untouched).

Run: cd tests && python3 test_killer_attribution_32b.py
"""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

CLASS = "terminated: SIGTERM (external: source unknown)"

PROBE = """
import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import wf
wf._install_runner_term_cleanup({"_run": Path(sys.argv[2])})
print("READY", flush=True)
time.sleep(30)
"""

def run_probe(tmp):
    run = Path(tmp) / "run"
    run.mkdir()
    (run / "graph.json").write_text(json.dumps({"name": "kill32b", "nodes": []}))
    p = subprocess.Popen([sys.executable, "-c", PROBE, str(BUILD), str(run)],
                         stdout=subprocess.PIPE, text=True)
    assert p.stdout.readline().strip() == "READY", "probe never armed"
    return p, run

if sys.platform != "linux" or os.uname().machine not in ("x86_64", "aarch64"):
    print("SKIP (signalfd leg is linux x86_64/aarch64)")
    print("QH32B_OK"); sys.exit(0)

def _signalfd_alive():
    # Hosts may intercept signalfd (seccomp); the code degrades to the plain
    # est-6226 handler there, and the field rows degrade with it — the prefix
    # and rc semantics are asserted on EVERY host.
    import ctypes
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        libc.syscall.restype = ctypes.c_long
        m = (ctypes.c_char * 128)()
        import struct as _s
        _s.pack_into("@Q", m, 0, 1 << 14)
        fd = libc.syscall(ctypes.c_long(43), ctypes.c_int(-1), m, ctypes.c_size_t(128), ctypes.c_int(0))
        if fd >= 0:
            os.close(fd)
        return fd >= 0
    except OSError:
        return False

FIELDS = _signalfd_alive()

with tempfile.TemporaryDirectory() as tmp:
    p, run = run_probe(tmp)
    k = subprocess.run(["kill", "-TERM", str(p.pid)])   # /bin/kill: an identifiable sender
    rc = p.wait(timeout=15)
    rec = json.loads((run / "runner_exit.json").read_text())
    reason = rec.get("reason", "")
    check("A still dies the default SIGTERM (rc -15, door reaper unchanged)", rc == -15, f"rc={rc}")
    check("A class constant stays the verbatim prefix", reason.startswith(CLASS), reason[:160])
    check("A no interpretation word", "gateway restart" not in reason, reason)
    if FIELDS:
        check("A reason names a numeric killer_pid", any(
            t.startswith("killer_pid=") and t.split("=", 1)[1].lstrip("-").isdigit()
            for t in reason.split()), reason)
        check("A killer_cmd names the measured sender argv", "kill -TERM" in reason, reason)
        check("A killer_uid rides", "killer_uid=" in reason, reason)
    else:
        print("SKIP-FIELDS (signalfd unavailable on this host — fallback handler row only)")

with tempfile.TemporaryDirectory() as tmp:
    run2 = Path(tmp) / "run2"
    subprocess.run([sys.executable, "-c", PROBE.replace("time.sleep(30)", "time.sleep(0.2)"),
                    str(BUILD), str(run2)], stdout=subprocess.DEVNULL, timeout=20)
    check("B clean exit writes no SIGTERM runner_exit record (atexit path untouched)",
          not (run2 / "runner_exit.json").exists())

print("QH32B_" + ("OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
