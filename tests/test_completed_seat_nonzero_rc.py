#!/usr/bin/env python3
"""sys-bknard — a COMPLETED child seat that exits rc=1 (the hermes CLI exit
path, not a crash) must not land as `error_class=unknown` with the #102
dead-session CLI line quoted back as its verdict.

Field shape (receipt 20261107-143106-b2p-sysggxeiu, claim-plan a0, pinned
byte-for-byte below): the capture opens with 'Session ... found but has no
messages. Starting fresh.', carries the finished answer prose, and CLOSES with
a fenced json answer that PARSES but misses required schema keys. The #4
harvest correctly declined it (schema miss), the death landed `unknown`, and
the node.failed error text was pure startup noise — the actual defect (which
keys the answer missed) was nowhere. The CLI rc=1 attribution lives as a bead
comment on sys-bknard; this file pins the RUNNER-side law:

 A  parseable-but-schema-invalid fenced answer over rc=1:
    A1 typed answer_schema_invalid (closed-set member), terminal (ONE spawn:
       outside both retry ladders, exactly like `schema`);
    A2 the error names the validate() misses (missing required keys);
    A3 the error does NOT quote the dead-session noise line (#102 law);
    A4 nothing harvested: status failed, no output, no harvest.
 B  noise-only capture (no fence) over rc=1:
    B1 stays `unknown` — no new class is invented for a capture with no answer;
    B2 the error names the noise-only shape instead of quoting the noise line.
 C  schema-VALID fenced answer over rc=1 (noise included): the #4 harvest
    accept rule is byte-unchanged — partial + output, not answer_schema_invalid.

Style: PASS/FAIL lines + exit code (test_malformed_turn_541 house style); the
fake's DEADSEAT <path|NONE> mode replays a capture file and exits FAKE_RC.
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
HOME = HERE / "homeBKNARD"
RUNS = HOME / "workflows"
FAKE = str(HERE / "fake")
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(RUNS)   # est-2ek.1.762 pin: HERMES_HOME alone is not a sandbox
sys.path.insert(0, str(BUILD))
import wf as wfmod  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

# a0's real fenced answer (claim-plan node, receipt 20261107-143106-b2p-sysggxeiu,
# logs/claim-plan.a0.log — the ONLY fence in that capture), embedded verbatim
# except personal home paths scrubbed to '~' (test_personal_path_scrub_867 ships
# the tree; the schema-miss pin rides the KEYS, so the scrub is shape-neutral).
A0_BODY = r"""{"bead_id":"sys-ggxeiu","branch":"sys-ggxeiu","destructive":false,"fleet_touching":false,"hosts":["devbox"],"premise_evidence":"grep -rqiE 'api_server.{0,160}flat|flat.{0,160}api_server' ~/.hermes/profiles/homelab/skills -> exit 1 (gap live); anchor at plugin-hooks.md:42 (API_SERVER_KEY bearer line); live flat shape at profiles/homelab/config.yaml:374-379 platforms.api_server{enabled,host,port,key}, nested extra: form seen on jetstream in same file; git rev-parse in skills dir = not a repo and system-wide find shows exactly one copy of plugin-hooks.md — no repo tracks it, so the PR carries no diff and the fix is a direct profile-file edit","roles":[],"summary_plan":"Apply one line to ~/.hermes/profiles/homelab/skills/autonomous-ai-agents/hermes-agent/references/plugin-hooks.md next to the line-42 API_SERVER_KEY bearer bullet, stating that api_server requires flat keys (enabled/host/port/key directly under platforms.api_server, not the nested extra: map other platforms use). The file is under no git, so expect an empty worktree and no PR; close with close_class=verified plus the acceptance grep exit-0 as cite, and do not let the stat-only incident-analysis.md phantom redden exit-check.","tests_run":[],"verdict":"ready"}"""

# The receipt graph's claim-plan answer shape: the probe reported the a0 answer
# missing exactly ['premise_verdict', 'sha']; the pinned schema keeps those two
# required so the validate() errors in the error text are the same facts.
SCHEMA = {"type": "object", "required": ["verdict", "premise_verdict", "sha"],
          "properties": {"verdict": {"type": "string"},
                         "premise_verdict": {"type": "string"},
                         "sha": {"type": "string"}}}

def mk(run_id, goal, schema):
    r = RUNS / run_id
    shutil.rmtree(r, ignore_errors=True)
    (r / "nodes").mkdir(parents=True); (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": [
        {"id": "claim-plan", "type": "agent", "goal": goal, "schema": schema}]}))
    (r / "run.json").write_text(json.dumps(
        {"hermes_bin": FAKE, "concurrency": 1, "node_timeout": 30,
         "retry_backoff": [0.05, 0.05]}))
    return r

def wf(run_id, timeout=180):
    env = dict(os.environ, HERMES_HOME=str(HOME), FAKE_LOG=str(HOME / "fake.log"))
    return subprocess.run([sys.executable, str(BUILD / "wf.py"), "run", run_id],
                          env=env, capture_output=True, text=True, timeout=timeout).stdout.strip()

def rec_of(r):
    return json.loads((r / "nodes" / "claim-plan.json").read_text())

def spawns_of(run_id):
    return len(list((RUNS / run_id / "logs").glob("*.a*.log")))

def events(r):
    try:
        return [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
    except FileNotFoundError:
        return []

shutil.rmtree(HOME, ignore_errors=True)
HOME.mkdir(parents=True); RUNS.mkdir()
(HOME / "fake.log").write_text("")

# the a0 capture as the fake replays it (the fake prints the noise line itself):
# finished-work prose + the schema-missing fence. HOME is gitignored (tests/home*/).
CAP = HOME / "bknard_a0_capture.txt"
CAP.write_text("plan.json written to the run dir; intake complete for sys-ggxeiu.\n"
               "```json\n" + A0_BODY + "\n```\n")

# ================= A: parseable fence fails the schema over rc=1 =================
r = mk("bknard-schema", f"DEADSEAT {CAP} bknard-schema claim-plan", SCHEMA)
wf("bknard-schema")
rec = rec_of(r)
err = rec.get("error") or ""
check("A1 rc=1 + schema-missing fence types answer_schema_invalid (closed set)",
      rec.get("status") == "failed" and rec.get("error_class") == "answer_schema_invalid"
      and rec.get("error_class") in wfmod.ERROR_CLASSES, json.dumps(rec)[:240])
check("A2 error names the validate() misses (missing required premise_verdict, sha)",
      "missing required" in err and "premise_verdict" in err and "sha" in err, err[:240])
check("A3 error does not quote the dead-session noise line (#102 law)",
      "found but has no messages" not in err, err[:240])
check("A4 nothing harvested: failed, no output, no harvest",
      "output" not in rec and "harvest" not in rec, json.dumps(rec)[:240])
check("A5 terminal: exactly one spawn (outside both retry ladders, like `schema`)",
      spawns_of("bknard-schema") == 1, f"spawns={spawns_of('bknard-schema')}")
check("A5 node.failed event typed from the closed set",
      any(e.get("event") == "node.failed" and e.get("error_class") in wfmod.ERROR_CLASSES
          for e in events(r)), json.dumps(events(r))[-240:])

# ================= B: noise-only capture over rc=1 =================
r = mk("bknard-noise", "DEADSEAT NONE bknard-noise claim-plan", SCHEMA)
wf("bknard-noise")
rec = rec_of(r)
err = rec.get("error") or ""
check("B1 noise-only death keeps the pre-existing class (unknown — no answer, no new label)",
      rec.get("status") == "failed" and rec.get("error_class") == "unknown", json.dumps(rec)[:240])
check("B2 error names the noise-only shape instead of quoting the noise line",
      "dead-session noise" in err and "found but has no messages" not in err, err[:240])
check("B2 no re-drive over absent api-call evidence (receipt attempts=1 shape)",
      spawns_of("bknard-noise") == 1, f"spawns={spawns_of('bknard-noise')}")

# ================= C: schema-VALID fence over rc=1 — #4 accept rule unchanged =========
GOOD = HOME / "bknard_good_capture.txt"
GOOD.write_text("```json\n" + json.dumps({"verdict": "ready", "premise_verdict": "valid",
                                           "sha": "0" * 40}) + "\n```\n")
r = mk("bknard-valid", f"DEADSEAT {GOOD} bknard-valid claim-plan", SCHEMA)
wf("bknard-valid")
rec = rec_of(r)
check("C harvest-on-death still accepts a valid fence over rc=1 (partial, not retyped)",
      rec.get("status") == "partial" and rec.get("error_class") != "answer_schema_invalid"
      and (rec.get("output") or {}).get("verdict") == "ready", json.dumps(rec)[:240])

print("RESULT " + ("ok" if ok else "FAILED"))
sys.exit(0 if ok else 1)
