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
receipt; loud mismatch receipt; a knob-free run emits NOTHING (ratified: zero
concurrency.applied / node.running_width events, no wall stamp, no spawn-wall env —
the legacy event stream stays byte-identical to the frozen capture) yet launches; work-metered
timeout retry (second spawn resumes, inherits ~remaining wall, emits dead_letter
exactly once, never a third spawn); a zero-ledger hang stays wall-only (2 spawns).

#580 take-over (review blockers B1-B3): the amend leg asserts the LAUNCH-FROZEN
knob law (grammar.md line 7 made code — an amend re-bakes nothing and answers
knobs_frozen), the door refuses a non-finite resume_floor_s (1e309/NaN), the
runner defends the same class at its own seam (a persisted non-finite floor
normalizes to the default, never an infinite spawn wall), and a shelved entry
carrying top-level retry INCLUDES like any other graph (shared-validator parity).

Run: python3 tests/test_concurrency_retry_knobs_24.py
"""
import importlib.util, json, math, os, shutil, subprocess, sys, time
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
# council r4 R3: a host WF_RUNS_ROOT would escape the sandbox. DROP it rather
# than point it: setting it makes the door stamp launch_root into a knob-free
# run.json, which the B-leg exact-keys check (correctly) forbids; with it
# unset the door resolves runs under HERMES_HOME (RUNS below).
os.environ.pop("WF_RUNS_ROOT", None)
os.environ["HERMES_WF_HERMES_BIN"] = FAKE
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("hw", ROOT / "__init__.py")
hw = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(hw)
# S3 (test_shelf_isolation_71): a bare env drop is not a sandbox — pin the door's
# settings.runs_root channel beside it, like every other in-process door writer.
import wf_test_isolation
wf_test_isolation.install(hw)

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

# #580 B3 (admission side): valid JSON numeric overflow is NOT a duration.
# 1e309 round-trips to +inf and NaN survives json — both must refuse at the
# door naming the field, so no inf ever reaches a spawn wall.
for bad_rf in (1e309, float("nan")):
    r = call(action="save", graph=dict(NARROW, retry={"mode": "work-metered",
                                                      "resume_floor_s": bad_rf}),
             name=f"knob-a-retry-nonfinite-{bad_rf}")
    check(f"retry resume_floor_s {bad_rf!r} refused (finite positive law)",
          any(e.get("field") == "retry.resume_floor_s" and "finite" in e["msg"]
              for e in (r.get("errors") or [])), r)

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

# est-2ek.1.166/ra-plan#125-1: EVERY run now stamps plugin_version (derived from
# plugin.yaml, never invented) — a sanctioned meta key, not a knob key.
LEGACY = {"hermes_bin", "name", "started", "fp_rule_version", "owner", "plugin_version"}
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
    # #100 item 4 (main ruling, rides the rebase): an over-default author ask
    # bakes DOWN to the default; the raw ask lands in _requested.
    check("run.json carries requested values",
          m.get("_requested", {}).get("concurrency") == 16
          and m.get("_requested", {}).get("item_concurrency") == 12
          and m.get("concurrency") == 4 and m.get("item_concurrency") == 8
          and m.get("retry") == {"mode": "work-metered", "resume_floor_s": 30}, m)
    check("run.json carries author-vs-default provenance",
          (m.get("knobs_provenance") or {}).get("concurrency") == "author"
          and (m.get("knobs_provenance") or {}).get("retry") == "author", m)

# #580 B1 (launch-frozen law — grammar.md line 7's promise made code): an amend
# NEVER re-bakes the knob family. The runner's hot-reload seam re-reads only
# graph.json at the wave boundary, so a re-baked run.json would disagree with
# the live scheduler until respawn; the launch-time bake and its provenance
# STAND, and the amend response names the frozen values (knobs_frozen).
nodes_v1 = NARROW["nodes"]
r = call(action="run", graph={"name": "knob-a-amend", "nodes": nodes_v1, "concurrency": 16})
rid = r.get("run_id")
if rid:
    call(action="stop", run_id=rid)
    am = call(action="amend", run_id=rid, graph={"name": "knob-a-amend", "nodes": nodes_v1})
    check("amend without knob accepted", am.get("ok"), am)
    m = run_json_meta(rid)
    check("amend keeps the launch-frozen bake (value and provenance unmoved)",
          m.get("concurrency") == 4 and m.get("_requested", {}).get("concurrency") == 16
          and (m.get("knobs_provenance") or {}).get("concurrency") == "author", m)
    check("amend response carries knobs_frozen naming the frozen bake",
          bool(am.get("knobs_frozen")) and am["knobs_frozen"].get("concurrency") == 4, am)
else:
    check("amend lane run launched", False, r)

# #580 B2 (shared-validator parity): the shelf is measured with the SAME full
# validator a submitted graph gets (validate_graph_full, no door-side extra
# keys) — a shelved graph carrying top-level `retry` must INCLUDE, not die
# `unknown graph key` at expansion while direct submission accepts it. The
# merged payload correctly drops child top-level keys (fusion projects the
# parent's); the leg pins ACCEPTANCE, not a child-baked knob.
r = call(action="run", graph={"name": "knob-a-include", "nodes": nodes_v1,
                              "include": [{"as": "klib", "use": "knob-a-retry-work-metered"}]})
check("included shelf entry carrying retry expands (no unknown-key refusal)",
      bool(r.get("run_id")) and "unknown graph key" not in json.dumps(r), r)
if r.get("run_id"):
    call(action="stop", run_id=r["run_id"]); wait_dead(r["run_id"])

# ---------- part B: the runner (subprocess wf.py + fake children)
# est-2ek.1.762 pin (lane arrival): the spawn legs carry the code-level
# WF_RUNS_ROOT pin to THIS test's own scratch runs root — exactly the dir the
# door already resolves under the pinned HERMES_HOME (line 54's pop), so child
# behaviour is unchanged; the in-process golden-solo leg (A) never sees this
# key and its zero-key contract (LEGACY above) stays intact.
envb = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS), FAKE_LOG=str(HOME / "fake.log"))

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

def attempt_walls(d):
    shutil.rmtree(d, ignore_errors=True)
    return d

BASE_ATTEMPTS = HOME / "attempts"

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

# B2: knob-free run (no knob keys in run.json) => NO receipts, per the ratified
# contract: the event stream of a knob-free run stays byte-identical to the
# frozen capture. Zero concurrency.applied, zero node.running_width; and for the
# death side, a knob-free timeout record carries no 'wall' key and the child's
# spawn env carries no HERMES_WF_SPAWN_WALL_S line (the fake records a wall line
# into walls.txt only when that env is actually set).
r = mk("knob-b-legacy", WAVE["nodes"], {})
out = wf("knob-b-legacy")
check("knob-free run completes", out.startswith("WORKFLOW_DONE"), out)
check("knob-free run: zero concurrency.applied events",
      not [e for e in events(r) if e["event"] == "concurrency.applied"], events(r))
check("knob-free run: zero node.running_width events",
      not [e for e in events(r) if e["event"] == "node.running_width"], events(r))
r = mk("knob-b-legacy-deaths", [{"id": "z", "type": "agent", "goal": "hang"}],
       {"node_timeout": 3})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-legacy-deaths")
wf("knob-b-legacy-deaths", extra={"FAKE_MODE": "hang", "FAKE_ATTEMPT_DIR": str(ad)}, timeout=120)
check("knob-free timeout death: no 'wall' key in the node record",
      "wall" not in rec_of(r, "z"), rec_of(r, "z"))
check("knob-free spawn: no HERMES_WF_SPAWN_WALL_S env line",
      not (ad / "walls.txt").exists(), (ad / "walls.txt").read_text() if (ad / "walls.txt").exists() else "")

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
# Retime per the repo's measured-floor precedent (#581/9bc5bcc and the
# park-walls 159c W-series): the components are exact — walls.txt fares
# [4, 2], backoff 5 s — the term the old bound omitted is the ~4 s host reap
# overhead between wall expiry and the runner noticing. Measured worst leg
# 15.7 s on this estate host (2026-10-27). Bound = fare + backoff + resume
# fare + reap overhead + 3 s margin.
check("metered+finish: total wall bounded (fare+backoff+resume+reap overhead+3s margin)",
      wall < 4 + 5 + 2 + 4 + 3, f"wall={wall:.1f}s")

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
check("second death: bounded wall (fare+backoff+resume+reap overhead+3s margin), not unbounded",
      wall < 4 + 5 + 2 + 4 + 3, f"wall={wall:.1f}s")

# B6: zero-ledger hang stays wall-only (identical to the legacy ladder, fail-closed)
r = mk("knob-b-zero", [{"id": "z", "type": "agent", "goal": "z"}],
       {"node_timeout": 4, "retry": {"mode": "work-metered", "resume_floor_s": 30}})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-zero")
out = wf("knob-b-zero", extra={"FAKE_MODE": "work_metered_zero", "FAKE_ATTEMPT_DIR": str(ad)})
logs = sorted((r / "logs").glob("z.a*.log"))
check("zero-ledger death never re-driven", len(logs) == 1, str([p.name for p in logs]))
check("no dead_letter for zero-ledger (fail-closed as before)",
      not [e for e in events(r) if e["event"] == "dead_letter"], events(r))

# B7: explicit wall mode — the legacy ladder re-drives at the IDENTICAL wall
# (the knob opted in, so the spawn env carries the wall the fake records)
r = mk("knob-b-legacy-retry", [{"id": "q", "type": "agent", "goal": "RESUME hang"}],
       {"node_timeout": 4, "retry": {"mode": "wall"}})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-legacy-retry")
out = wf("knob-b-legacy-retry", extra={"FAKE_MODE": "work_metered", "FAKE_ATTEMPT_DIR": str(ad)})
walls = [float(x) for x in (ad / "walls.txt").read_text().split()] if (ad / "walls.txt").exists() else []
check("wall mode re-drives with the full wall again (no resume meter)",
      len(walls) >= 2 and walls[0] == walls[1] == 4.0, str(walls))
check("wall mode emits no dead_letter", not [e for e in events(r) if e["event"] == "dead_letter"], events(r))

# B8 (#580 B3, runner seam): a persisted NON-FINITE resume floor — 1e309 is
# JSON-legal round-trip (writes Infinity) and lands in run.json from a
# pre-cure/hand-written byte, the door now refuses it at admission but the
# runner must not wear an author-inf wall either. _retry_conf normalizes the
# non-finite floor to the default 30 s: the second spawn gets a FINITE wall
# (<= the default floor), the run completes on it, never a third spawn.
r = mk("knob-b-overflow", [{"id": "h", "type": "agent", "goal": "RESUME hang"}],
       {"node_timeout": 4, "retry": {"mode": "work-metered", "resume_floor_s": 1e309}})
ad = attempt_walls(BASE_ATTEMPTS / "knob-b-overflow")
out = wf("knob-b-overflow", extra={"FAKE_MODE": "work_metered", "FAKE_ATTEMPT_DIR": str(ad)})
walls = [float(x) for x in (ad / "walls.txt").read_text().split()] if (ad / "walls.txt").exists() else []
logs = sorted((r / "logs").glob("h.a*.log"))
check("overflow floor: second spawn wall is FINITE (normalized, never inf)",
      len(walls) == 2 and math.isfinite(walls[1]) and walls[1] <= 30.0, str(walls))
check("overflow floor: run completes on the resume, never a third spawn",
      len(logs) == 2 and out.startswith("WORKFLOW_DONE"), out[:80])

print("TOTAL", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
