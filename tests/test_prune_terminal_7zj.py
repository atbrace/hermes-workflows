"""prune is terminal (hw-7zj): a fan-out on a PRUNED arm must stay pruned even though
the items_from+after lockstep law forces a shared live ancestor (the classifier) into
its after list. LAW B ("one live dep keeps a join running") must not resurrect an arm
node via a dep that is an ANCESTOR of the pruned dep — the pruned gate already waits
on that ancestor, so it carries no independent signal. Joins with a genuinely live
sibling dep (not an ancestor of any pruned dep) keep running — that law is unchanged.

Collision class (wf/1): validate demands items_from head in the fan-out's OWN after;
prune_states prunes ONLY when ALL after deps are skipped; in a complementary when-gate
pair the batch fan-out keeps the done classifier as a live dep and spawns mid-hold on
the urgent arm — mutating the ledger the human was holding.

Runnable two ways (repo convention): `python3 tests/test_prune_terminal_7zj.py`
prints PASS/FAIL lines, exit 0 = green; pytest can also collect test_*.
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(PLUGIN))
import wfcommon  # noqa: E402

HOME = HERE / "home7zj"
RUNS = HOME / "workflows"
FAKE = HERE / "fake"
FAILS = []

def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)

# ---- pure derivation fixtures (no runner) ----
def agent(id, after=(), goal=None):
    return {"id": id, "type": "agent", "after": list(after), "timeout": 30,
            "goal": goal or 'JSON:{"ok": true}'}

def gate(id, after, when, on_fail=None):
    g = {"id": id, "type": "gate", "after": list(after), "wait": {"wait_s": 1},
         "when": when, "on_skip": "prune", "question": "?"}
    if on_fail:
        g["on_fail"] = on_fail
    return g

CLS = agent("classify", goal='JSON:{"items": ["b1", "b2"], "has_urgent": true}')
GATE = gate("route-batch", ["classify"], "out.classify.has_urgent != true")
FAN = {"id": "batch-run", "type": "agent", "after": ["route-batch", "classify"],
       "timeout": 30, "fanout": {"items_from": "classify.items", "goal": "go {item}"}}

# ---- 1. the collision itself: pruned gate + live ANCESTOR dep prunes the arm ----
nodes1 = [CLS, GATE, FAN]
st1b = {"classify": "done", "route-batch": "skipped", "batch-run": "pending"}
d1 = wfcommon.prune_states(nodes1, st1b)
check("fan-out on a pruned arm derives skipped (ancestor live dep does not resurrect)",
      st1b["batch-run"] == "skipped" and d1 == {"batch-run"}, str(st1b))

# ---- 2. cascade: a node downstream of that fan-out prunes too ----
nodes2 = nodes1 + [agent("report", ["batch-run"])]
st2 = {"classify": "done", "route-batch": "skipped", "batch-run": "pending", "report": "pending"}
wfcommon.prune_states(nodes2, st2)
check("prune cascades through the whole pruned arm",
      st2["batch-run"] == "skipped" and st2["report"] == "skipped", str(st2))

# ---- 3. join law UNCHANGED: a live SIBLING dep (not an ancestor of the pruned dep) runs ----
nodes3 = [CLS, GATE,
          agent("ship", ["classify"]),
          dict(FAN, after=["route-batch", "classify"]),
          agent("merge", ["batch-run", "ship"])]
st3 = {"classify": "done", "route-batch": "skipped", "ship": "done",
       "batch-run": "skipped", "merge": "pending"}
wfcommon.prune_states(nodes3, st3)
check("join with a live sibling dep still runs", st3["merge"] == "pending", str(st3))

# ---- 4. live dep that is NOT an ancestor of the pruned dep: no prune (conservative) ----
nodes4 = [CLS, GATE, agent("side"), dict(FAN, after=["route-batch", "classify", "side"])]
st4 = {"classify": "done", "route-batch": "skipped", "side": "done", "batch-run": "pending"}
wfcommon.prune_states(nodes4, st4)
check("independent live dep keeps the node running", st4["batch-run"] == "pending", str(st4))

# ---- 5. fallback exception (jam-h23) survives the precedence fix ----
nodes5 = [CLS, gate("route-batch", ["classify"], "x", on_fail="batch-run"), FAN]
st5 = {"classify": "done", "route-batch": "skipped", "batch-run": "pending"}
wfcommon.prune_states(nodes5, st5)
check("a skipped dep naming this node as on_fail still exempts it", st5["batch-run"] == "pending", str(st5))

# ---- runner fixtures ----
ENV = lambda r: {**os.environ, "HERMES_HOME": str(HOME), "WF_RUNS_ROOT": str(RUNS),
                 "WF_HERMES_BIN": str(FAKE), "FAKE_LOG": str(r / "fake.log"),
                 "PATH": f"{HERE}:{os.environ.get('PATH', '')}"}

def fresh(run_id, nodes):
    r = RUNS / run_id
    if r.exists():
        shutil.rmtree(r)
    for d in ("nodes", "gates", "logs"):
        (r / d).mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps({"name": "t", "nodes": nodes}))
    (r / "run.json").write_text(json.dumps({"name": "t", "hermes_bin": str(FAKE),
                                            "concurrency": 4,
                                            "started": "2026-10-21T00:00:00+00:00",
                                            "owner": "test"}))
    return r

def run_runner(r, timeout=180):
    return subprocess.run([sys.executable, str(PLUGIN / "wf.py"), "run", r.name],
                          env=ENV(r), capture_output=True, text=True, timeout=timeout)

def faked_graph():
    return [
        agent("classify", goal='JSON:{"items": ["b1", "b2"], "has_urgent": true}'),
        gate("route-urgent", ["classify"], "out.classify.has_urgent == true"),
        gate("route-batch", ["classify"], "out.classify.has_urgent != true"),
        {"id": "batch-run", "type": "agent", "after": ["route-batch", "classify"],
         "timeout": 30, "fanout": {"items_from": "classify.items", "goal": "go {item}"}},
        agent("escalate", ["route-urgent"]),
        agent("merge", ["batch-run", "escalate"]),
    ]

# ---- 6. real runner: urgent arm taken -> batch fan-out NEVER spawns ----
r = fresh("20990101-000000-7zj", faked_graph())
run_runner(r)
st = wfcommon.run_state(r)
S = {k: v["status"] for k, v in st["nodes"].items()}
spawned = any(x.name.startswith("batch-run") for x in (r / "logs").iterdir())
check("runner: pruned-arm fan-out commits skipped, zero spawns",
      S.get("batch-run") == "skipped" and not spawned, str(S) + f" spawned={spawned}")
check("runner: urgent arm runs", S.get("escalate") == "done" and S.get("route-urgent") == "done", str(S))
check("runner: merge runs with one live dep (skipped counts satisfied)", S.get("merge") == "done", str(S))
check("runner: run ends done", (st.get("runner_exit") or {}).get("reason") == "done", str(st.get("runner_exit")))
rec = json.loads((r / "nodes" / "batch-run.json").read_text())
byid = {n["id"]: n for n in faked_graph()}
check("skip record is efp-stamped (replay-skip law)", rec.get("efp") == wfcommon.efp(byid, byid["batch-run"]), str(rec.get("efp")))
ev = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
check("events: node.skipped names the pruned fan-out",
      any(e.get("event") == "node.skipped" and e.get("node") == "batch-run" for e in ev))

# ---- 7. re-drive with the committed skip fact: stays pruned, no respawn ----
n_fake_1 = len((r / "fake.log").read_text().splitlines()) if (r / "fake.log").exists() else 0
run_runner(r)
S2 = {k: v["status"] for k, v in wfcommon.run_state(r)["nodes"].items()}
n_fake_2 = len((r / "fake.log").read_text().splitlines()) if (r / "fake.log").exists() else 0
check("re-drive: fan-out stays skipped and nothing respawns",
      S2.get("batch-run") == "skipped" and n_fake_2 == n_fake_1, str(S2))

# ---- 8. mid-crash re-drive: kill the fan-out skip fact (crash before the cascade
#      commit) — the runner must RE-DERIVE the prune, not re-spawn the arm ----
(r / "nodes" / "batch-run.json").unlink()
run_runner(r)
st3r = wfcommon.run_state(r)
S3 = {k: v["status"] for k, v in st3r["nodes"].items()}
spawned3 = any(x.name.startswith("batch-run") for x in (r / "logs").iterdir())
n_fake_3 = len((r / "fake.log").read_text().splitlines()) if (r / "fake.log").exists() else 0
check("mid-crash re-drive: fan-out re-pruned from the gate fact, never spawned",
      S3.get("batch-run") == "skipped" and not spawned3 and n_fake_3 == n_fake_1, str(S3) + f" spawned={spawned3}")

print("RESULT:", "FAIL " + str(FAILS) if FAILS else "GREEN")
sys.exit(1 if FAILS else 0)
