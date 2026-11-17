#!/usr/bin/env python3
"""Per-node call/token ceilings: the ledger gets a reader.

The telemetry sidecar (node_telemetry.py, est-wqml6) already records
api_calls/tool_calls/input_tokens per child, rewritten per event. This suite
proves the enforcement half: an agent node may declare max_api_calls /
max_input_tokens (validated at the door like the other numeric budget knobs);
the runner samples the sidecar at the poll seam it already has and, on a
ceiling EXCEEDED (observed > declared), kills the child tree, proves the death
and commits the node failed with the typed terminal class `ceiling_exceeded`
(outside both retry ladders, like budget_exhausted). The failure record names
which ceiling and the observed value; the read model reports the declared
shape where task_total_ceiling used to say "not_enforced".

Legs:
  M  closed set membership + the AGENTS 3d doc-sync (pinned separately).
  D  door: a declared ceiling validates; a malformed value is refused naming
     the key (green before and after: unknown-key rejection already names it).
  K  execution_clocks reports the declared shape; undeclared stays
     "not_enforced" byte-identical.
  E  end-to-end (fake child CEILING-EMIT climbs api_calls past the declared 3
     then lingers): node fails typed ceiling_exceeded, attempts==1, the record
     names max_api_calls + the observed count, tree_proof=dead, the fake pid is
     actually dead, the settle fold still joins+consumes the sidecar (the death
     carries `telemetry`, the dir stays bounded), and run_state accounting
     reports the declared shape.
  N1 the same CEILING-EMIT child WITHOUT declared ceilings completes done
     (green before and after: no neutering of normal runs).
  N2 declared-but-never-exceeded completes done with the declared shape on the
     record path (green after only).

Stdlib-only, serial, prints PASS/FAIL lines, exit 0 = green (repo contract).
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_HOME = tempfile.mkdtemp(prefix="wf-ceiling-home-")
os.environ["HERMES_HOME"] = _HOME
os.environ["WF_RUNS_ROOT"] = str(Path(_HOME) / "workflows")

import wf  # noqa: E402  (import-time: spec-loads wfcommon only; no spawn)
import wfcommon as WFC  # noqa: E402

door_spec = importlib.util.spec_from_file_location("wf_door_ceil", ROOT / "__init__.py")
door = importlib.util.module_from_spec(door_spec)
door_spec.loader.exec_module(door)
sys.path.insert(0, str(ROOT / "tests"))
import wf_test_isolation as _iso  # noqa: E402
_iso.install(door)

ok = True


def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"),
          flush=True)
    ok = ok and bool(cond)


# ---------- M: the closed set carries the new class ---------------------------
check("M1 ceiling_exceeded is in the closed ERROR_CLASSES set",
      "ceiling_exceeded" in wf.ERROR_CLASSES, sorted(wf.ERROR_CLASSES)[:6])
check("M2 ceiling_exceeded is terminal: outside the bounded retry whitelist",
      "ceiling_exceeded" not in wf._BOUNDED_RETRY_CLASSES)


# ---------- D: the door validates the knobs like the run_budget family --------
def door_errors(graph):
    res = door._validation_error(graph)
    if res is None:
        return ""
    return res.get("error", "") + " || " + " || ".join(
        f"{e.get('field')}: {e.get('msg')}" for e in res.get("errors", []))


g_ok = {"name": "ceil", "nodes": [{"id": "a", "type": "agent", "goal": "g",
                                   "max_api_calls": 3, "max_input_tokens": 100000}]}
check("D1 declared ceilings (non-negative ints) validate at the door",
      door_errors(g_ok) == "", door_errors(g_ok))
d_bad = door_errors({"name": "ceil", "nodes": [{"id": "a", "type": "agent", "goal": "g",
                                                "max_api_calls": "three"}]})
check("D2 max_api_calls='three' is refused naming the key",
      d_bad != "" and "max_api_calls" in d_bad, d_bad)
d_neg = door_errors({"name": "ceil", "nodes": [{"id": "a", "type": "agent", "goal": "g",
                                                "max_input_tokens": -1}]})
check("D3 max_input_tokens=-1 is refused naming the key",
      d_neg != "" and "max_input_tokens" in d_neg, d_neg)


# ---------- K: the accounting reports the declared shape ----------------------
clock_declared = WFC.execution_clocks({"id": "a", "max_api_calls": 3}, {"status": "done"},
                                      {}, time.time())
check("K1 a node with declared ceilings reports its declared shape",
      clock_declared["task_total_ceiling"] == {"max_api_calls": 3},
      str(clock_declared["task_total_ceiling"]))
clock_bare = WFC.execution_clocks({"id": "a"}, {"status": "done"}, {}, time.time())
check("K2 an undeclared node keeps task_total_ceiling='not_enforced' verbatim",
      clock_bare["task_total_ceiling"] == "not_enforced",
      str(clock_bare["task_total_ceiling"]))


# ---------- E/N: the end-to-end enforcement legs ------------------------------
def drive(goal, node_extra):
    """Run one solo-agent-node graph with the fake child; return (resp, run_dir, record, pids)."""
    home = Path(tempfile.mkdtemp(prefix="wf-ceiling-e2e-"))
    runs = home / "runs"
    runs.mkdir()
    fake = home / "fake-hermes"
    shutil.copy(ROOT / "tests" / "fake_hermes.py", fake)
    os.chmod(fake, 0o755)
    pidlog = home / "pids.log"
    env = {**os.environ, "HERMES_HOME": str(home), "WF_RUNS_ROOT": str(runs),
           "HERMES_WF_HERMES_BIN": str(fake), "FAKE_PID_LOG": str(pidlog)}
    env.pop("WORKFLOW_MAX_SEATS", None)
    with patch.dict(os.environ, env, clear=True):
        node = {"id": "a", "type": "agent", "goal": goal}
        node.update(node_extra)
        resp = door.act_run({"graph": {"name": "ceil", "nodes": [node]}})
        rec, run_dir = {}, None
        if isinstance(resp, dict) and resp.get("run_id"):
            run_dir = runs / resp["run_id"]
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                p = run_dir / "nodes" / "a.json"
                if p.is_file():
                    rec = json.loads(p.read_text())
                    if rec.get("status") in ("done", "partial", "failed"):
                        break
                time.sleep(0.25)
    pids = [int(x) for x in pidlog.read_text().split()] if pidlog.is_file() else []
    return resp, run_dir, rec, pids


def pid_dead(pid):
    try:
        os.kill(pid, 0)
        return False
    except ProcessLookupError:
        return True
    except PermissionError:
        return False


FAKE_TELE_4 = {"api_calls": 4, "tool_calls": 1, "input_tokens": 40,
               "output_tokens": 0, "total_tokens": 40}

# E: declared max_api_calls=3, the child climbs to 4 and lingers -> typed death.
resp, run_dir, rec, pids = drive("CEILING-EMIT API=4 SLEEP=30 STEP=0.3",
                                 {"max_api_calls": 3})
check("E1 the launch is accepted and produces a run",
      isinstance(resp, dict) and bool(run_dir), str(resp)[:200])
check("E2 the node commits failed with the typed terminal class",
      rec.get("status") == "failed" and rec.get("error_class") == "ceiling_exceeded",
      str({k: rec.get(k) for k in ("status", "error_class")}))
etxt = str(rec.get("error") or "")
check("E3 the failure names the ceiling and the observed count",
      "max_api_calls" in etxt and "4" in etxt, etxt)
check("E4 attempts==1 (terminal: neither ladder re-drove)", rec.get("attempts") == 1,
      str(rec.get("attempts")))
check("E5 the record carries the tree-death proof",
      rec.get("tree_proof") == "dead", str(rec.get("tree_proof")))
check("E6 the child process is actually dead",
      bool(pids) and all(pid_dead(p) for p in pids), str(pids))
check("E7 the settle fold still joins the sidecar onto the death record",
      rec.get("telemetry") == FAKE_TELE_4, str(rec.get("telemetry")))
if run_dir:
    tdir = run_dir / "telemetry"
    check("E8 the folded sidecar was consumed (no unbounded run-dir growth)",
          not tdir.exists() or not list(tdir.glob("*.json")),
          str(list(tdir.glob("*")) if tdir.exists() else []))
    st = WFC.run_state(run_dir) or {}
    check("E9 run accounting reports the declared ceiling shape",
          (st.get("accounting") or {}).get("task_total_ceiling") == {"a": {"max_api_calls": 3}},
          str((st.get("accounting") or {}).get("task_total_ceiling")))
    node_clock = ((st.get("nodes") or {}).get("a") or {}).get("clocks") or {}
    check("E10 the node clock reports the declared ceiling shape",
          node_clock.get("task_total_ceiling") == {"max_api_calls": 3},
          str(node_clock.get("task_total_ceiling")))
else:
    check("E8 the folded sidecar was consumed (no unbounded run-dir growth)", False, "no run")
    check("E9 run accounting reports the declared ceiling shape", False, "no run")
    check("E10 the node clock reports the declared ceiling shape", False, "no run")

# N1: the same runaway-shaped child WITHOUT declared ceilings is untouched.
resp, run_dir, rec, pids = drive("CEILING-EMIT API=9 SLEEP=1 STEP=0.05", {})
check("N1 no declared ceilings: the same child completes done, unaffected",
      isinstance(resp, dict) and bool(run_dir) and rec.get("status") == "done",
      str(resp)[:120] + str({k: rec.get(k) for k in ("status", "error_class")}))
if run_dir:
    st = WFC.run_state(run_dir) or {}
    check("N2 undeclared run keeps task_total_ceiling='not_enforced'",
          (st.get("accounting") or {}).get("task_total_ceiling") == "not_enforced",
          str((st.get("accounting") or {}).get("task_total_ceiling")))
else:
    check("N2 undeclared run keeps task_total_ceiling='not_enforced'", False, "no run")

# N3: declared but never exceeded -> the run completes normally.
resp, run_dir, rec, pids = drive("CEILING-EMIT API=2 SLEEP=1 STEP=0.05",
                                 {"max_api_calls": 99, "max_input_tokens": 1000000})
check("N3 declared-but-not-exceeded: completes done, telemetry intact",
      isinstance(resp, dict) and bool(run_dir) and rec.get("status") == "done"
      and rec.get("telemetry") == {"api_calls": 2, "tool_calls": 1, "input_tokens": 20,
                                   "output_tokens": 0, "total_tokens": 20},
      str(resp)[:120] + str({k: rec.get(k) for k in ("status", "error_class", "telemetry")}))

# E-fast (council leg 1): the exit race — a child that blows the ceiling and
# exits between polls must NOT commit done; the exit-instant final sample
# catches it. On the pre-fix code the loop breaks at rc before any sample and
# this leg commits done (RED).
resp, run_dir, rec, pids = drive("CEILING-EMIT API=4 SLEEP=0 STEP=0",
                                 {"max_api_calls": 3})
check("E-fast1 blow-the-ceiling-then-fast-exit commits typed, not done",
      isinstance(resp, dict) and bool(run_dir)
      and rec.get("status") == "failed" and rec.get("error_class") == "ceiling_exceeded",
      str(resp)[:120] + str({k: rec.get(k) for k in ("status", "error_class")}))
check("E-fast2 attempts==1 (terminal, no ladder)", rec.get("attempts") == 1,
      str(rec.get("attempts")))
check("E-fast3 the exit-race fold still joins the overshooting sidecar",
      rec.get("telemetry") == FAKE_TELE_4, str(rec.get("telemetry")))

# E-att (council leg 2): ceilings are PER ATTEMPT. The boundary is the fold
# itself: a later attempt's rewrite is ALL any judgment ever sees — attempt 1's
# counts are gone, so a re-drive gets a fresh ceiling and worst-case exposure
# is attempts x ceiling (both bounded). Deterministic module leg, no ladder
# acrobatics: rewrite the sidecar under one skey and fold once.
_nt_mod = wf._node_telemetry()
_att_run = Path(tempfile.mkdtemp(prefix="wf-ceiling-att-"))
_att_key = _nt_mod.node_key("a")
(_att_run / "telemetry").mkdir()
for _api in (2, 4):   # attempt 1 then attempt 2, same skey
    (_att_run / "telemetry" / (_att_key + ".json")).write_text(json.dumps(
        {"api_calls": _api, "tool_calls": 1, "input_tokens": 10 * _api,
         "output_tokens": 0, "total_tokens": 10 * _api}))
_folded = _nt_mod.fold_at_settle(_att_run, "a")
check("E-att1 the fold reports the LATEST attempt's counts only (per-attempt law)",
      _folded == {"api_calls": 4, "tool_calls": 1, "input_tokens": 40,
                  "output_tokens": 0, "total_tokens": 40}, str(_folded))
check("E-att2 ceiling judgment on the fold sees 4 vs declared 3 (hit), never a cumulative 6",
      _folded.get("api_calls", 0) == 4, str(_folded))
shutil.rmtree(_att_run, ignore_errors=True)

shutil.rmtree(_HOME, ignore_errors=True)
print("RESULT", "PASS" if ok else "FAIL", flush=True)
sys.exit(0 if ok else 1)
