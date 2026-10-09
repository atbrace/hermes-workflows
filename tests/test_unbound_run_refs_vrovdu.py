#!/usr/bin/env python3
"""sys-vrovdu: the door must reject unbound {run.KEY} at launch AND on dry_run.

Measured 10-04 (haus counter C2, run 20261004-150243-bindability-probe-real):
a graph carrying {run.KEY} placeholders launched with NO run_context spawned
nodes with literal `{run.KEY}` text in their prompts, and dry_run:true passed
the same hole. Only the fan-out per-item re-interpolation braces-check existed.
Hermetic (sandboxed HOME + WF_RUNS_ROOT + resolver pin, fake runner spawn).
"""
import importlib.util, json, os, shutil, sys
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
HOME = Path(__file__).resolve().parent / "home_vrovdu"
shutil.rmtree(HOME, ignore_errors=True)
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
sys.path.insert(0, str(BUILD)); sys.path.insert(0, str(BUILD / "tests"))
spec = importlib.util.spec_from_file_location("vrovdu_door", str(BUILD / "__init__.py"))
hw = importlib.util.module_from_spec(spec); spec.loader.exec_module(hw)
import wf_test_isolation as _iso71; _iso71.install(hw)   # #71: pin settings.runs_root
spawns = []
hw._spawn_runner = lambda r: spawns.append(r)
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else " " + str(detail)))
    if not ok:
        failures.append(name)
def run(**extra):
    return json.loads(hw.handle({"action": "run", **extra}))
def dirs():
    w = HOME / "workflows"
    return sorted(p.name for p in w.iterdir()) if w.exists() else []

G = {"name": "vrovdu", "nodes": [
    {"id": "a", "type": "agent", "goal": "do {run.TOKEN}", "context": "for {run.TOKEN}"}]}

# 1. the bug itself: no run_context at all -> refuse, name the key, write nothing
before = (len(spawns), dirs())
r = run(graph=dict(G, name="v1"))
check("T1 no run_context refuses and names the key",
      "error" in r and "run.TOKEN" in r["error"] and "a" in r["error"], r)
check("T1b refusal wrote no run dir and spawned no runner",
      (len(spawns), dirs()) == before, dirs())

# 2. dry_run shares the gate (the bead's second half)
r = run(graph=dict(G, name="v2"), dry_run=True)
check("T2 dry_run refuses too", "error" in r and "run.TOKEN" in r.get("error", ""), r)
check("T2b dry_run refusal wrote nothing", (len(spawns), dirs()) == before, dirs())

# 3. seed binding is not an escape hatch: a seed never substitutes, so refs stay
r = run(graph=dict(G, name="v3"), run_context="a plain seed sentence")
check("T3 seed launch with dangling refs refuses", "error" in r, r)

# 4. a complete map binds the ref and launches exactly as before
before_ok = (len(spawns), dirs())
r = run(graph=dict(G, name="v4"), run_context={"TOKEN": "bound"})
check("T4 fully-bound launch still launches", bool(r.get("run_id")), r)
if r.get("run_id"):
    g = json.loads((HOME / "workflows" / r["run_id"] / "graph.json").read_text())
    n = next(x for x in g["nodes"] if x["id"] == "a")
    check("T4b bound prompts carry no placeholder",
          n["goal"] == "do bound" and "{run." not in json.dumps(g), n)
    hw.act_stop({"run_id": r["run_id"]})

# 5. a partial map refuses naming the MISSING key (pre-existing law, unchanged)
r = run(graph={"name": "v5", "nodes": [
    {"id": "a", "type": "agent", "goal": "{run.ONE} {run.TWO}"}]}, run_context={"ONE": "1"})
check("T5 partial map names the missing key", "missing key 'TWO'" in r.get("error", ""), r)

# 6. literal-free graphs are byte-unchanged (the golden-solo law)
r = run(graph={"name": "v6", "nodes": [{"id": "a", "type": "echo", "output": "plain"}]})
check("T6 literal-free graph unaffected", bool(r.get("run_id")), r)
if r.get("run_id"):
    hw.act_stop({"run_id": r["run_id"]})

# 7. every text surface is swept: echo output, gate options, fan-out goal, profile-free
for label, node in (("echo", {"id": "e", "type": "echo", "output": "v={run.T}"}),
                    ("gate options", {"id": "g", "type": "gate", "question": "q",
                                      "options": ["yes {run.T}"]}),
                    ("fanout goal", {"id": "f", "type": "agent",
                                     "fanout": {"items": [{"item": "1"}], "goal": "go {run.T}"}}),
                    ("gate argv", {"id": "w", "type": "gate", "question": "q",
                                   "wait": {"until_argv": ["true", "{run.T}"]}})):
    r = run(graph={"name": "v7-" + node["id"], "nodes": [node]})
    check(f"T7 {label} surface refuses an unbound ref",
          "error" in r and "run.T" in r.get("error", ""), r)

print("ALL PASS" if not failures else f"FAILURES PRESENT: {len(failures)}")
shutil.rmtree(HOME, ignore_errors=True)
sys.exit(bool(failures))
