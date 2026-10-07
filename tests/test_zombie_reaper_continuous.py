#!/usr/bin/env python3
"""Continuous zombie hygiene for the subreaper pool (receipts sys-fk7myz /
sys-1kt44m, devbox 2026-10-07: 8.8k adopted zombies — 7.6k of them `git` —
load average 39 on 20 cores; every healthy runner burned ~0.65 cores because
the poll walks that grow with the zombie pool run on a 0.25 s cadence).

The law this test locks:
  * _adopted_zombie_pids finds zombies parented to THIS process and EXCLUDES
    any pid in the tracked set — waitpid'ing a live Popen child out from under
    its polling thread makes subprocess report returncode 0: a FALSE GREEN
    seat verdict. Integrity, not hygiene.
  * _start_reaper launches a daemon thread named zombie-reaper; setting the
    stop event ends it (no thread leak after the run exits).
  * the reaper drains adopted zombies for real (a double-forked grandchild
    that exits is adopted while the subreaper is set; the pool must empty).
"""
import os, sys, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import wf  # noqa: E402

STUB = HERE / "stub_orphan_666_child.py"   # exits immediately: parent inherits a zombie
fails = []

def main() -> int:
    # 1) classification: tracked pids are NEVER returned, even as zombies.
    import subprocess
    p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    p.terminate(); p.wait()                # reaped by Popen: not a zombie anymore
    tracked = {p.pid}
    if p.pid in wf._adopted_zombie_pids(tracked):
        fails.append("tracked pid returned by _adopted_zombie_pids")

    # 2) a REAL adopted zombie: fork an intermediate that forks a grandchild and
    # exits; the grandchild (adopted by the subreaper = this process) exits ->
    # our zombie pool. Done IN-PROCESS: no nested-quoting hazard.
    if not wf._set_subreaper():
        print("SKIP: PR_SET_CHILD_SUBREAPER unavailable on this platform")
        return 0
    pid = os.fork()
    if pid == 0:
        try:
            g = os.fork()
            if g == 0:
                os._exit(0)               # grandchild: adopted by us, then dead
            os._exit(0)                   # intermediate dies too
        except Exception:
            os._exit(1)
    time.sleep(1.0)
    pool = wf._adopted_zombie_pids(set())
    if not pool:
        fails.append("no adopted zombie observed after double-fork exit (fixture may be racy; "
                     "check manually before trusting)")

    # 3) the reaper drains it and stops on the stop event.
    meta = {"_stop": threading.Event(), "_procs_lock": threading.Lock(), "_procs": {}}
    wf._start_reaper(meta)
    names = [t.name for t in threading.enumerate()]
    if "zombie-reaper" not in names:
        fails.append(f"reaper thread not started: {names}")
    deadline = time.time() + 10
    while time.time() < deadline and wf._adopted_zombie_pids(set()):
        time.sleep(0.5)
    if wf._adopted_zombie_pids(set()):
        fails.append("reaper did not drain the adopted zombie pool within 10s")
    meta["_stop"].set()
    time.sleep(1.5)
    if "zombie-reaper" in [t.name for t in threading.enumerate()]:
        fails.append("reaper thread survived the stop event")

    if fails:
        for f in fails:
            print("FAIL:", f)
        return 1
    print("zombie-reaper: classification excludes tracked Popen pids; daemon drains the "
          "adopted pool; stop event ends the thread")
    return 0

if __name__ == "__main__":
    sys.exit(main())
