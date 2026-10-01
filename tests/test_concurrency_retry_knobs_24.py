#!/usr/bin/env python3
"""#24 knob family: launch-time concurrency validation/receipt + work-metered retry.

Before this fix the knobs were live-but-unreachable: wf.py read meta["concurrency"]
(default 4) and meta["item_concurrency"] (default 8) from run.json, but the door
validated neither — a graph-level `concurrency` key was REJECTED as an unknown graph
key and no run param carried it — so a wide fan-out could not be launched wider than
the baked default without hand-editing run.json. And a timeout death re-drove at the
IDENTICAL wall (node.timeout re-read from the same def every spawn), so a 2400 s hang
burned 2x2400 s of wall for zero result.

Part A (door, in-process, fake bin): graph-level keys accepted + validated with the
repo's reject shape; run/amend bakes the effective value + provenance into run.json;
a missing knob adds NO keys (key-set frozen for pre-existing run.json readers).
Part B (runner subprocess + fake hermes): concurrency.applied receipt with observed
width; loud mismatch receipt; legacy run.json (no knobs) still launches; work-metered
timeout retry (second spawn resumes, inherits ~remaining wall, emits dead_letter
exactly once, never a third spawn); a zero-ledger hang stays wall-only (2 spawns).

Run: python3 tests/test_concurrency_retry_knobs_24.py
"""
import importlib.util, json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE)
ROOT = BUILD.parent if BUILD.name == "tests" else BUILD
HOME = HERE / "home-knobs"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# ---------- part A: the door (in-process; HERMES_WF_HERMES_BIN keeps every spawn fake)
shutil.rmtree(HOME, ignore_errors=True)
os.environ["HERMES_HOME"] = str(HOME)
os.environ["HERMES_WF_HERMES_BIN"] = FAKE
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("hw", ROOT / "__init__.py")
hw = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(hw)

def call(**a):
    return json.loads(hw.handle(a))

def fields(res):
    return {e["field"] for e in (res.get("errors") or [])}

NARROW = {"name": "knob-a-narrow", "nodes": [{"id": "a", "type": "agent", "goal": "x"}]}

r = call(action="run", graph=dict(NARROW, concurrency=16), dry_run=True)
check("graph-level concurrency accepted at run", "error" not in r or "unknown graph key" not in r.get("error", ""), r)

r = call(action="save", graph=dict(NARROW, concurrency=16), name="knob-a-save")
check("graph-level concurrency accepted at save", "error" not in r, r)

r = call(action="save", graph=dict(NARROW, item_concurrency=12), name="knob-a-save-ic")
check("graph-level item_concurrency accepted at save", "error" not in r, r)

for bad, msg in ((0, "positive int"), ("abc", "positive int"), (2.5, "positive int")):
    r = call(action="save", graph=dict(NARROW, concurrency=bad), name=f"knob-a-bad-{bad}")
    check(f"concurrency {bad!r} rejected", r.get("error", "").startswith("graph invalid:")
          and any(msg in e["msg"] for e in (r.get("errors") or [])), r)

r = call(action="save", graph=dict(NARROW, concurrency=10000), name="knob-a-cap")
check("concurrency 10000 refused with cap named",
      "cap 4096" in json.dumps(r), r)

r = call(action="save", graph=dict(NARROW, retry={"mode": "nonsense"}), name="knob-a-retry-bad")
check("retry mode nonsense rejected",
      any("invalid retry.mode" in e["msg"] for e in (r.get("errors") or [])), r)

r = call(action="save", graph=dict(NARROW, retry={"not_a_key": 1}), name="knob-a-retry-keys")
check("retry unknown key rejected",
      any(e.get("field") == "retry" and "unknown key" in e["msg"] for e in (r.get("errors") or [])), r)

for good in ({"mode": "work-metered"}, {"mode": "wall"},
             {"mode": "work-metered", "resume_floor_s": 60}):
    r = call(action="save", graph=dict(NARROW, retry=good), name="knob-a-retry-" + good["mode"] + str(good.get("resume_floor_s", "")))
    check(f"retry {good} accepted", "error" not in r, r)

# a missing knob adds NOTHING: the legacy key set must not grow
def run_json_meta(rid):
    return json.loads((RUNS / rid / "run.json").read_text())

def wait_dead(rid, budget=15.0):
    t0 = time.time()
    while time.time() - t0 < budget:
        if not call(action="status", run_id=rid).get("runner_live"):
            return True
        time.sleep(0.2)
    return False

LEGACY = {"hermes_bin", "name", "started", "fp_rule_version", "owner"}
r = call(action="run", graph=NARROW)
rid = r.get("run_id"); check("bare run launches", bool(rid), r)
if rid:
    call(action="stop", run_id=rid); wait_dead(rid)
    keys = set(run_json_meta(rid))
    check("no knobs => no new run.json keys", keys <= LEGACY, str(sorted(keys - LEGACY)))

r = call(action="run", graph=dict(NARROW, concurrency=16, item_concurrency=12,
                                  retry={"mode": "work-metered", "resume_floor_s": 30}))
rid = r.get("run_id"); check("knobbed run launches", bool(rid), r)
if rid:
    call(action="stop", run_id=rid); wait_dead(rid)
    m = run_json_meta(rid)
    check("run.json carries requested values",
          m.get("concurrency") == 16 and m.get("item_concurrency") == 12
          and m.get("retry") == {"mode": "work-metered", "resume_floor_s": 30}, m)
    check("run.json carries author-vs-default provenance",
          (m.get("knobs_provenance") or {}).get("concurrency") == "author"
          and (m.get("knobs_provenance") or {}).get("retry") == "author", m)

# amend re-bakes: replace graph WITHOUT the knob -> value returns to default,
# provenance flips to default
nodes_v1 = NARROW["nodes"]
r = call(action="run", graph={"name": "knob-a-amend", "nodes": nodes_v1, "concurrency": 16})
rid = r.get("run_id")
if rid:
    call(action="stop", run_id=rid)
    am = call(action="amend", run_id=rid, graph={"name": "knob-a-amend", "nodes": nodes_v1})
    check("amend without knob accepted", am.get("ok"), am)
    m = run_json_meta(rid)
    check("amend re-bakes default + provenance",
          m.get("concurrency") == 4 and (m.get("knobs_provenance") or {}).get("concurrency") == "default", m)
else:
    check("amend lane run launched", False, r)

# ---------- part B: the runner (subprocess wf.py + fake children)
envb = dict(os.environ, HERMES_HOME=str(HOME), FAKE_LOG=str(HOME / "fake.log"))

def mk(run_id, nodes, meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "node_timeout": 30}; m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def wf(run_id, extra=None, timeout=180):
    env = dict(envb, **(extra or {}))
    p = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                       env=env, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip()

def events(r):
    try:
        return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
    except FileNotFoundError:
        return []

def rec_of(r, nid):
    return json.loads((r / "nodes" / f"{nid}.json").read_text())

def widths(r, nid):
    return [e["running"] for e in events(r) if e["event"] == "node.running_width" and e.get("node") == nid]

WAVE = {"name": "w", "nodes": [{"id": "w", "type": "agent",
                                "fanout": {"items": ["i1", "i2", "i3", "i4", "i5"], "goal": "SLEEP 0.6 {item}"}}]}

# B1: applied receipt + observed width, knob honored (no knob set today produces this)
r = mk("knob-b-width", WAVE["nodes"], {"item_concurrency": 2})
out = wf("knob-b-width")
check("width run completes", out.startswith("WORKFLOW_DONE"), out)
evs = [e for e in events(r) if e["event"] == "concurrency.applied"]
check("concurrency.applied emitted", len(evs) == 1, events(r))
if evs:
    e = evs[0]
    check("receipt carries requested/applied/knobs",
          e.get("requested", {}).get("item_concurrency") == 2
          and e.get("applied", {}).get("item_concurrency") == 2
          and e.get("knobs", {}).get("item_concurrency") == "author", e)
ws = widths(r, "w")
check("observed width honored the knob (max 2)", ws and max(ws) == 2, ws)

# B2: legacy run.json (no knob keys) -> receipt with defaults, run behavior unchanged
r = mk("knob-b-legacy", WAVE["nodes"], {})
out = wf("knob-b-legacy")
check("legacy run completes", out.startswith("WORKFLOW_DONE"), out)
evs = [e for e in events(r) if e["event"] == "concurrency.applied"]
check("legacy run still receipts", len(evs) == 1 and evs[0]["knobs"] == {}, evs)
check("legacy defaults applied", evs and evs[0]["applied"] == {"concurrency": 4, "item_concurrency": 8}, evs)

# B3: LOUD receipt when a graph asked wider than capacity
r = mk("knob-b-mismatch", [{"id": "m", "type": "agent", "goal": "x"}],
       {"concurrency": 4, "_requested": {"concurrency": 16, "knobs": {"concurrency": "author"}}})
out = wf("knob-b-mismatch", timeout=120)
evs = [e for e in events(r) if e["event"] == "concurrency.applied"]
check("mismatch receipt loud", evs and evs[0].get("mismatch") and
      evs[0].get("requested", {}).get("concurrency") == 16
      and evs[0].get("knobs", {}).get("concurrency") == "author", evs)
check("mismatch does not block the run", out.startswith("WORKFLOW_DONE"), out)

# B4: work-metered timeout, RESUMER FINISHES — hang child with ledger progress dies
# at the wall; the ONE resume spawn inherits the remaining wall and commits.
def attempt_walls(d):
    shutil.rmtree(d, ignore_errors=True)
    return d

BASE_ATTEMPTS = HOME / "attempts"
r = mk("knob-b-metered", [{"id": "h", "type": "agent", "goal": "RESUME hang"}],
       {"node_timeout": 4, "retry": {"mode": "work-metered", "resume_floor_s": 2}})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-metered")
t0 = time.time()
out = wf("knob-b-metered", extra={"FAKE_MODE": "work_metered", "FAKE_ATTEMPT_DIR": str(ad)})
wall = time.time() - t0
logs = sorted((r / "logs").glob("h.a*.log"))
walls = [float(x) for x in (ad / "walls.txt").read_text().split()] if (ad / "walls.txt").exists() else []
check("metered+finish: exactly two spawns", len(logs) == 2, str([p.name for p in logs]))
check("metered+finish: resume spawn gets the remaining wall, not the full fare",
      len(walls) == 2 and walls[0] == 4.0 and 0 < walls[1] < 4.0, str(walls))
check("metered+finish: no dead_letter (resume committed)",
      not [e for e in events(r) if e["event"] == "dead_letter"], events(r))
check("metered+finish: run completes on the resume", out.startswith("WORKFLOW_DONE"), out)
check("metered+finish: total wall bounded (fare + backoff + remaining, < identical-wall legacy)",
      wall < 4 + 5 + 2 + 3, f"wall={wall:.1f}s")

# B5: work-metered timeout, SECOND DEATH AT ANY WALL = dead-letter, never a third spawn
r = mk("knob-b-dead", [{"id": "h", "type": "agent", "goal": "RESUME hang"}],
       {"node_timeout": 4, "retry": {"mode": "work-metered", "resume_floor_s": 2}})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-dead")
t0 = time.time()
out = wf("knob-b-dead", extra={"FAKE_MODE": "work_metered_dead", "FAKE_ATTEMPT_DIR": str(ad)})
wall = time.time() - t0
logs = sorted((r / "logs").glob("h.a*.log"))
dl = next((e for e in events(r) if e["event"] == "dead_letter"), {})
check("second death: never a third spawn", len(logs) == 2, str([p.name for p in logs]))
check("second death: dead_letter once, residue classified",
      dl.get("residue") == "tool-ledger>0", dl)
check("second death: node failed honestly", rec_of(r, "h")["status"] == "failed", rec_of(r, "h"))
check("second death: bounded wall (fare + backoff + resume), not unbounded",
      wall < 4 + 5 + 2 + 3, f"wall={wall:.1f}s")

# B6: zero-ledger hang stays wall-only (identical to the legacy ladder, fail-closed)
r = mk("knob-b-zero", [{"id": "z", "type": "agent", "goal": "z"}],
       {"node_timeout": 4, "retry": {"mode": "work-metered", "resume_floor_s": 30}})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-zero")
out = wf("knob-b-zero", extra={"FAKE_MODE": "work_metered_zero", "FAKE_ATTEMPT_DIR": str(ad)})
logs = sorted((r / "logs").glob("z.a*.log"))
check("zero-ledger death never re-driven", len(logs) == 1, str([p.name for p in logs]))
check("no dead_letter for zero-ledger (fail-closed as before)",
      not [e for e in events(r) if e["event"] == "dead_letter"], events(r))

# B7: default mode unchanged — the legacy ladder re-drives at the IDENTICAL wall
r = mk("knob-b-legacy-retry", [{"id": "q", "type": "agent", "goal": "RESUME hang"}],
       {"node_timeout": 4})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-legacy-retry")
out = wf("knob-b-legacy-retry", extra={"FAKE_MODE": "work_metered", "FAKE_ATTEMPT_DIR": str(ad)})
walls = [float(x) for x in (ad / "walls.txt").read_text().split()] if (ad / "walls.txt").exists() else []
check("wall mode re-drives with the full wall again (no resume meter)",
      len(walls) >= 2 and walls[0] == walls[1] == 4.0, str(walls))
check("wall mode emits no dead_letter", not [e for e in events(r) if e["event"] == "dead_letter"], events(r))

print("TOTAL", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
