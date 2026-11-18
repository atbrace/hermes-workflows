#!/usr/bin/env python3
"""hw-qh6: retry re-drives start seeded — the #130 inventory rides the schema-correction
and gate400 clamp re-drives, not just the ladder/park respawns.

Measured 2026-10-26: a re-drive that starts a fresh session redoes orientation from
zero (one re-drive burned 5.4M calls rebuilding a 4-call plan). #130 already ships the
machine '## Dead-attempt artifact inventory' preamble for the transient/bounded/park
respawns; the schema-correction re-drive and the gate400 clamp re-drive kept sending
'Redo the work' with no inventory. These rows pin the two seeded paths and the
resume_hint: false byte-identity promise.

  A schema-correction re-drive (attempt 1): its prompt carries the inventory header AND
    names the dead attempt's banked artifact; the run closes done off the seeded answer.
  B resume_hint: false on the same death: the retry prompt stays byte-identical to the
    pre-seed shape (no inventory) and the node fails exactly as before.

Run: cd tests && HOME=$PWD/homeqh6 python3 test_redrive_seed_qh6.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "homeqh6"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)
sys.path.insert(0, str(BUILD))

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

HEADER = "## Dead-attempt artifact inventory (machine preamble)"

def mk(run_id, nodes, **meta):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    m = {"hermes_bin": FAKE, "concurrency": 4, "node_timeout": 30,
         "retry_backoff": [0.05, 0.1]}; m.update(meta)
    (r / "run.json").write_text(json.dumps(m))
    return r

def wf(run_id, extra_env=None, timeout=180):
    env = dict(os.environ, HERMES_HOME=str(HOME), WF_RUNS_ROOT=str(RUNS),
               FAKE_LOG=str(HOME / "fake.log"), **(extra_env or {}))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def rec_of(r, nid):
    return json.loads((r / "nodes" / f"{nid}.json").read_text())

SCHEMA = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"]}

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
(HOME / "fake.log").write_text("")

# ---- A: the schema-correction re-drive starts seeded (auto-inventory: prior files exist) ----
r = mk("qh6-schema", [{"id": "a", "type": "agent", "goal": "tr qh6-schema",
                       "schema": SCHEMA, "resume_hint": True}])
out = wf("qh6-schema", {"FAKE_MODE": "seed_schema_qh6", "FAKE_API_CALLS": "0",
                        "FAKE_ATTEMPT_DIR": str(HOME / "att_schema")})
rec = rec_of(r, "a")
check("A seeded re-drive recovers to done ONLY off the inventory (fake gate)",
      rec["status"] == "done" and (rec.get("output") or {}).get("result") == "resumed-schema-qh6",
      str(rec)[:300])
p2 = r / "logs" / "a.a1.prompt.md"
prompt2 = p2.read_text() if p2.exists() else ""
check("A correction re-drive prompt carries the machine inventory header", HEADER in prompt2,
      prompt2[:160])
check("A inventory names the dead attempt's banked artifact", "qh6seed.md" in prompt2,
      prompt2[:160])
check("A correction wording keeps the don't-redo law",
      "Correct the answer schema without redoing finished work." in prompt2, prompt2[-200:])
check("A run closes done", out.startswith("WORKFLOW_DONE qh6-schema"), out[-160:])

# ---- B: resume_hint false — the retry prompt stays byte-identical to the pre-seed shape ----
r = mk("qh6-off", [{"id": "a", "type": "agent", "goal": "tr qh6-off",
                    "schema": SCHEMA, "resume_hint": False}])
out = wf("qh6-off", {"FAKE_MODE": "seed_schema_qh6", "FAKE_API_CALLS": "0",
                     "FAKE_ATTEMPT_DIR": str(HOME / "att_off")})
rec = rec_of(r, "a")
p2 = r / "logs" / "a.a1.prompt.md"
prompt2 = p2.read_text() if p2.exists() else ""
check("B resume_hint:false — no inventory bytes on the retry prompt", HEADER not in prompt2)
check("B and the node fails exactly as the pre-seed law (unseeded retry repeats the bad answer)",
      rec["status"] == "failed" and "result" in str(rec.get("error", "")), str(rec)[:250])
check("B prompt-side only: no resume_hint key in the record", "resume_hint" not in json.dumps(rec))

print("QH6_" + ("OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
