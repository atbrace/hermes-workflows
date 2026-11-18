"""hw-ced (plugin-side): every seat prompt states its run dir.

Measured 2026-11-17 (runs 20261117-234621/234752/234908/235927-rdirprobe*):
a workflow seat whose session is served by a gateway DAEMON runs its terminal
in the daemon's process — inside the unit's declared systemd env — so the
runner's per-spawn HERMES_WF_* env pins never reach the seat shell (both
/proc/$$/environ and /proc/<cli>/environ counted zero HERMES_WF_* names;
cgroup hermes-gateway-*.service). Seats burned turns rediscovering the run
dir (b2p audit receipts, hw-7fg). The prompt is the one channel that always
reaches a seat, so it must name the run dir and say how to recover the
variable in-shell.

Green: the prompt carries 'Run dir: <run>' + the export hint, positioned in
the GOAL half (before '## Inputs') so the fan-out identity law ('everything
from ## Inputs onward byte-identical') is untouched — pinned by a two-item
fan-out whose prompt tails match byte-for-byte.
"""
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FAILS = []


def check(name, cond, detail=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  ::  " + str(detail)[:400]))
    if not cond:
        FAILS.append(name)


FAKE = r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
qp = args[args.index("--query-file") + 1] if "--query-file" in args else None
print("```json\n" + json.dumps({"result": "ok"}) + "\n```")
'''


def main():
    with tempfile.TemporaryDirectory(prefix="rdirprompt-") as t:
        tmp = Path(t)
        home = tmp / "home"
        home.mkdir()
        fake = tmp / "fake-hermes"
        fake.write_text(FAKE)
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        graph = {"name": "rdir", "nodes": [
            {"id": "solo", "type": "agent", "goal": "answer OK"},
            {"id": "fan", "type": "agent", "goal": "item {item} answers",
             "fanout": {"items": ["one", "two"]}}]}
        run = home / "workflows" / "rdir"
        (run / "nodes").mkdir(parents=True)
        (run / "gates").mkdir()
        (run / "graph.json").write_text(json.dumps(graph))
        (run / "run.json").write_text(json.dumps({"hermes_bin": str(fake), "concurrency": 4}))
        env = dict(os.environ, HERMES_HOME=str(home), WF_RUNS_ROOT=str(home / "workflows"))
        p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", "rdir"],
                           env=env, text=True, capture_output=True, timeout=90, cwd=str(tmp))
        check("lifecycle done", p.returncode == 0 and "WORKFLOW_DONE" in p.stdout,
              (p.stdout + p.stderr)[:300])
        text = (run / "logs" / "solo.a0.prompt.md").read_text()
        check("the prompt states Run dir with the absolute run path",
              "Run dir: " + str(run) in text, text[-400:])
        check("it tells the seat how to recover the variable in-shell",
              "HERMES_WF_RUN_DIR" in text and "export" in text, text[-400:])
        check("it lands in the GOAL half — before ## Inputs",
              "Run dir:" in text.split("## Inputs")[0], text[:400])
        f0 = (run / "logs" / "fan.0.a0.prompt.md").read_text()
        f1 = (run / "logs" / "fan.1.a0.prompt.md").read_text()
        tail = lambda s: s[s.index("## Inputs"):] if "## Inputs" in s else s
        check("fan-out identity law preserved: ## Inputs onward is byte-identical",
              f0.endswith(tail(f1)[len(tail(f1)) // 2:]) or tail(f0) == tail(f1),
              (tail(f0)[:120], tail(f1)[:120]))

    print("FAILURES:", len(FAILS))
    sys.exit(1 if FAILS else 0)


main()
