#!/usr/bin/env python3
"""Regression: the shelf census buckets husks and prints the fleet line.

A run dir past a grace whose runner_exit.json is absent and whose name is not
in the live-runner batch probe is a HUSK — the census must name it and print
one canonical counters block: {total, by_status, live_runners, husks,
gate_held}. Plain stdlib script; run: python3 tests/test_shelf_census_husk_hw0y7.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "shelf_census", ROOT / "scripts" / "shelf-census.py")
assert _spec and _spec.loader, "scripts/shelf-census.py must exist"
sc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sc)

ok = 0


def check(cond, msg):
    global ok
    assert cond, msg
    ok += 1
    print("PASS", msg)


def makedir(root, name, *, age=0.0, exit=None, held=None, answered=(), pid=None):
    d = root / name
    (d / "gates").mkdir(parents=True)
    (d / "run.json").write_text(json.dumps({"name": name}))
    if exit is not None:
        (d / "runner_exit.json").write_text(json.dumps({"reason": exit}))
    if held:
        (d / "gates" / (held + ".held.json")).write_text(json.dumps({"since": 1}))
    for gid in answered:
        (d / "gates" / (gid + ".json")).write_text(json.dumps({"answer": "x"}))
    if pid is not None:
        (d / "wf.pid").write_text(str(pid))
    if age:
        stamp = time.time() - age
        for p in list(d.rglob("*")) + [d]:
            if p.is_file():
                os.utime(p, (stamp, stamp))
        os.utime(d, (stamp, stamp))
    return str(d)


with tempfile.TemporaryDirectory() as td:
    wf = Path(td) / "workflows"
    wf.mkdir()
    done = makedir(wf, "r-done", age=7200, exit="done")
    failed = makedir(wf, "r-failed", age=7200, exit="crashed: boom")
    held = makedir(wf, "r-held", age=7200, held="approve")
    stale_held = makedir(wf, "r-stale-held", age=7200, held="approve", answered=("approve",))
    husk = makedir(wf, "r-husk", age=2 * 86400)
    fresh = makedir(wf, "r-fresh", age=60)
    live = makedir(wf, "r-live", age=7200, pid=os.getpid())

    probe = lambda dirs: {live} if live in list(dirs) else set()
    c = sc.run_status_census([done, failed, held, stale_held, husk, fresh, live],
                             grace_s=3600, probe=probe)
    for key in ("total", "by_status", "live_runners", "husks", "gate_held"):
        check(key in c, f"counters block carries {key}")
    check(c["total"] == 7, f"total counts every run dir (got {c['total']})")
    check(c["by_status"] == {"done": 1, "failed": 1, "gate_held": 1,
                             "husk": 2, "in_flight": 1, "live": 1},
          f"by_status buckets every class (got {c['by_status']})")
    check(c["live_runners"] == 1, "live_runners counts the probe-hit dir")
    check(c["gate_held"] == 1, "gate_held counts an unanswered hold marker only")
    check(c["husks"] == 2 and c["husk_dirs"] == sorted([husk, stale_held]),
          f"husks = past-grace + no exit record + not live (got {c['husk_dirs']})")

    out = Path(td) / "out.json"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "shelf-census.py"),
                        "--wf-root", str(wf), "--out", str(out),
                        "--husk-grace", "3600", "--no-refs"],
                       capture_output=True, text=True,
                       env=dict(os.environ, HERMES_HOME=td))
    check(r.returncode == 0, f"census exits 0 (rc={r.returncode}, stderr={r.stderr[-300:]})")
    written = json.loads(out.read_text())
    check("run_status" in written, "census artifact carries run_status")
    # E2E: no live pid/lock here, so r-live honestly subtracts as a husk too.
    check(written["run_status"]["husks"] == 3
          and written["run_status"]["live_runners"] == 0
          and written["run_status"]["total"] == 7,
          f"E2E counters subtract live-by-nothing (got {written['run_status']})")
    printed = json.loads(r.stdout.split("written:")[0])
    check("run_status" in printed, "the fleet line prints with the census summary")

    # The measured estate failure: one unchunked batch over ~1.5k dirs crosses
    # Linux's 128 KiB single-arg cap, the probe child dies, and fail-closed
    # busy books EVERY dead dir as live. Chunking must keep the truth.
    big = [makedir(wf, "r-big-%04d" % i, age=7200) for i in range(1500)]
    check(sc.live_runners(big) == set(),
          "1.5k-dir batch probe stays truthful over the argv cap")
    c2 = sc.run_status_census(big, grace_s=3600)
    check(c2["husks"] == 1500 and c2["live_runners"] == 0,
          f"the 1.5k husks subtract, not fail-closed (got {c2['by_status']})")

print(f"OK — {ok} checks")
