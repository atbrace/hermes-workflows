#!/usr/bin/env python3
"""hw-p2g (partial-gate-wedge): gate decisions must not queue behind an agent wave.

Verified defect (tip 5a2ab88, incident run 20261111-131651-ki-wave1): the gate pick
sits AFTER the agent-wave branch in the runner loop and ThreadPoolExecutor.map
blocks the whole loop for the wave's wall-clock duration, so a gate whose ancestor
already committed produces ZERO events while a sibling lane builds — the incident's
false-twin `when` skip waited 50 minutes for its wave boundary, and status showed
the deferred gate pending with no reason ("live and ready forever").

Laws this test locks:
  A1  a when-false gate skips at the wave BOUNDARY — the gate.skipped row lands
      BEFORE the sleeping sibling's node.finished (RED on base: it lands after);
  A2  a hold still lands AFTER the wave — the boundary drain must never park/hold
      across ready agents (the negative that keeps the wave un-stranded);
  B1  a deferred gate is VISIBLE: exactly one gate.deferred{node, by} event names
      the blocking wave, status nodes[<gate>].blocked_by carries that reason while
      the gate defers, and the reason is gone once the gate is next evaluated.
The untouched requires/blocked-by-partial law stays pinned by the neighbours
tests/test_partial_block_87.py and tests/test_partial_release_hw-sq1.py.

Run: env -u PYTHONPATH -u VIRTUAL_ENV HERMES_HOME=$(mktemp -d) \
     python3 tests/test_gate_wave_boundary_p2g.py
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
home = Path(tempfile.mkdtemp(prefix="wf-home-p2g-")).resolve()
os.environ["HERMES_HOME"] = str(home)
os.environ["WF_RUNS_ROOT"] = str(home / "workflows")  # est-2ek.1.762 pin
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

fake = str(HERE / "fake")
runs = home / "workflows"
runs.mkdir()
# Pin the spawn env: no HERMES_WF_* leakage from whatever harness runs this test.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("HERMES_WF_")}
ENV.update({"WF_ARGV_STABLE_ROOTS": str(home),
            "FAKE_LOG": str(home / "fake.log"),
            "FAKE_PROMPT_LOG": str(home / "prompts.log")})

ok = 0
def check(cond, msg):
    global ok
    assert cond, msg
    ok += 1
    print("PASS", msg)

# The incident's claim_plan shape: rc=1 with a valid fenced answer on the capture
# (DEADSEAT replays it), harvested to `done` by the producer's harvest_policy.
CAP = home / "claim_plan_capture.txt"
CAP.write_text("```json\n" + json.dumps({"verdict": "ship"}) + "\n```\n")

# Lane A: stub -> sleeper (an 8 s build, fake's SLEEP marker).
# Lane B: claim_plan -> two when twins. gate_dead (the FALSE twin) is DECLARED
# FIRST so the untouched est-1n7gx declaration-order pick reaches it first on
# base too — the only thing that may move is WHEN the decision is journaled.
nodes = [
    {"id": "stub", "type": "agent", "goal": "OK stub"},
    {"id": "sleeper", "type": "agent", "goal": "SLEEP 8 lane-A build",
     "after": ["stub"]},
    {"id": "claim_plan", "type": "agent", "goal": f"DEADSEAT {CAP} claim-plan lane-B",
     "schema": {"type": "object", "properties": {"verdict": {"type": "string"}},
                "required": ["verdict"]},
     "harvest_policy": "validate"},
    {"id": "gate_dead", "type": "gate", "after": ["claim_plan"],
     "when": "out.claim_plan.verdict != 'ship'", "on_skip": "prune"},
    {"id": "gate_ship", "type": "gate", "after": ["claim_plan"],
     "when": "out.claim_plan.verdict == 'ship'",
     "options": ["ship", "hold"], "default_option": "hold", "hold_timeout": 2},
]

run = runs / "20990101-000000-p2g"
(run / "nodes").mkdir(parents=True)
(run / "gates").mkdir()
(run / "graph.json").write_text(json.dumps({"name": "p2g", "nodes": nodes}))
(run / "run.json").write_text(json.dumps({
    "name": "p2g", "hermes_bin": fake, "concurrency": 4, "node_timeout": 60,
    "started": "2099-01-01T00:00:00+00:00"}))

proc = subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", run.name],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=ENV)

# B1 (mid-wave): once the wave actually defers the gate (the gate.deferred row),
# status must name WHY — the running wave — instead of reading pending-with-no-
# reason. A blocked_by still naming an unfinished ancestor predates the defer and
# doesn't count; the runner re-journals gate.deferred at the boundary after the
# ancestor commits, so poll from the defer row onward.
mid = None
def _defer_rows():
    try:
        return sum(1 for l in (run / "events.jsonl").read_text().splitlines()
                   if '"gate.deferred"' in l)
    except FileNotFoundError:
        return 0
t0 = time.time()
while time.time() - t0 < 60 and mid is None and proc.poll() is None:
    st = wfcommon.run_state(run) or {}
    gg = (st.get("nodes") or {}).get("gate_ship") or {}
    # Strict capture: the reason must NAME the blocking wave. A blocked_by still
    # carrying only the older ancestor projection predates the defer row's own
    # status read; accepting it once made this leg flake RED on a cold cache.
    _bb = gg.get("blocked_by") or []
    if _bb and _defer_rows() and any("sleeper" in str(b) for b in _bb):
        mid = _bb
    time.sleep(0.2)
proc.communicate(timeout=120)

evs = [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines()]
def rows(event, node):
    return [i for i, e in enumerate(evs)
            if e.get("event") == event and e.get("node") == node]

fin = rows("node.finished", "sleeper")
check(len(fin) == 1, "the sleeper finished exactly once")
skip = rows("gate.skipped", "gate_dead")
check(len(skip) == 1, "the false twin skipped exactly once")

# A1 — the boundary decision: the false twin skips WHILE the wave runs.
check(skip[0] < fin[0],
      "A1 gate.skipped(gate_dead) is journaled before node.finished(sleeper) — "
      f"skip row {skip[0]} vs finish row {fin[0]} (the incident window)")

# A2 — the hold stays behind the wave: the drain must not strand the ready wave.
held = rows("gate.held", "gate_ship")
check(len(held) == 1 and held[0] > fin[0],
      "A2 gate.held(gate_ship) lands after the wave ended — no hold across ready agents")

# B1 — the deferred reason: one gate.deferred naming the blocking wave, events AND status.
defr = [e for e in evs if e.get("event") == "gate.deferred"]
check(len(defr) == 1 and defr[0].get("node") == "gate_ship" and defr[0].get("by") == ["sleeper"],
      f"B1 exactly one gate.deferred node=gate_ship by=['sleeper'], got {defr}")
check(mid is not None and any("sleeper" in b for b in mid),
      f"B1 mid-wave status carries blocked_by naming the running wave, got {mid}")

final = wfcommon.run_state(run)
check(final["status"] == "done", f"run closes done over the auto-released hold: {final['status']}")
check("blocked_by" not in (final["nodes"].get("gate_ship") or {}),
      "B1 the deferred reason is gone once the gate was next evaluated")
check(final["nodes"]["gate_dead"]["status"] == "skipped", "the false twin committed skipped")
_crec = json.loads((run / "nodes" / "claim_plan.json").read_text())
check(_crec["status"] == "done"
      and (_crec.get("clamped") or {}).get("policy") == "validate",
      "the harvested (rc=1 + valid fence) claim_plan ancestor committed done")
spawns = (home / "fake.log").read_text().splitlines()
check(len(spawns) == 3, f"exactly three children spawned (no drain-side spawn), got {spawns}")

# --------------------------------------------------------------------------
# Scenario 2 — precedence pins (council round): the drain re-enters the prune
# cascade AFTER each commit (prune-first, the standing top-of-loop order), and
# an output precondition outranks the predicate. Victims commit the cascade
# fact `node.skipped all deps pruned` exactly as the base commit derives it —
# a gate that took its OWN decision one pass early would run a subtree the
# base prunes (gate.skipped + a skip record where node.skipped belongs).
nodes2 = [
    {"id": "stub", "type": "agent", "goal": "OK stub"},
    {"id": "sleeper", "type": "agent", "goal": "SLEEP 6 lane-A build", "after": ["stub"]},
    {"id": "plan", "type": "agent", "goal": "OK plan"},
    {"id": "g0", "type": "gate", "after": ["plan"],
     "when": "1 == 0", "on_skip": "prune"},
    {"id": "g1", "type": "gate", "after": ["g0"],
     "when": "out.g0.answer == 'x'"},                      # cascade victim
    {"id": "g2", "type": "agent", "goal": "OK g2 should never spawn",
     "after": ["g1"]},
    {"id": "rq", "type": "gate", "after": ["plan"], "requires": {"plan": ["nope"]},
     "when": "1 == 1"},                                    # precondition first
]
run2 = runs / "20990101-000001-p2g2"
(run2 / "nodes").mkdir(parents=True)
(run2 / "gates").mkdir()
(run2 / "graph.json").write_text(json.dumps({"name": "p2g2", "nodes": nodes2}))
(run2 / "run.json").write_text(json.dumps({
    "name": "p2g2", "hermes_bin": fake, "concurrency": 4, "node_timeout": 60,
    "started": "2099-01-01T00:00:00+00:00"}))
proc2 = subprocess.Popen([sys.executable, str(BUILD / "wf.py"), "run", run2.name],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=ENV)
proc2.communicate(timeout=120)
evs = [json.loads(l) for l in (run2 / "events.jsonl").read_text().splitlines()]
fin2 = rows("node.finished", "sleeper")[0]

check(rows("gate.skipped", "g0") and rows("gate.skipped", "g0")[0] < fin2,
      "S2 the false gate g0 skips at the boundary before the sleeper finishes")
_g1 = json.loads((run2 / "nodes" / "g1.json").read_text())
check(_g1["status"] == "skipped" and _g1.get("output", {}).get("skipped") == "all deps pruned",
      "S2 the cascade claims g1 with the prune fact, not a self-decided gate record")
check(not rows("node.started", "g2"),
      "S2 the pruned subtree never spawns (base prunes it; the drain may not run it)")
_f2 = rows("node.failed", "rq")
check(len(_f2) == 1 and _f2[0] < fin2,
      "S2 the requires-refusal fails the gate typed at the boundary, before the predicate's hold")
check(json.loads((run2 / "nodes" / "rq.json").read_text()).get("error_class") == "precondition",
      "S2 the refusal is typed precondition")

print(f"OK {ok} assertions passed")
