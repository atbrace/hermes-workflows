#!/usr/bin/env python3
"""Wake payload run-dir pointer: a failure wake must name where the logs live.

The wake text names runner.log/summary.md as FILENAMES but never carries the
run directory, so a woken seat on run.failed starts archaeology (globbing
runs-roots) before it can read the failure. The pointer facts already exist at
notify()'s point: the run Path, and the committed failed-node records'
log_path fields. Fix shape (peer-ratified): run.failed and run.done payloads
carry run_dir; run.failed additionally carries the failed-node log paths; the
authority-law template bodies stay verbatim.

Laws this pins:
  * POINTER: run.failed and run.done wake text (wire content AND the
    wake.jsonl probe row) contains the run directory path.
  * FAILED LOGS: run.failed wake text contains the committed failed node's
    log_path (node-rec facts only; efp law upheld via the shared reader).
  * AUTHORITY VERBATIM: the template body text is unchanged around the
    pointer fields.
  * SCOPE: gate.held payload carries no run-dir pointer (out of scope).

Direct notify() calls against real run dirs + the loopback sink the sibling
wake suites use. No provider, synthetic session ids.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
for _k in ("WF_WAKE_SINK_PORT", "API_SERVER_KEY", "API_SERVER_HOST", "API_SERVER_PORT",
           "WF_RUNS_ROOT"):
    os.environ.pop(_k, None)  # hermetic: no inherited endpoint may steal the wake
import wf  # noqa: E402

checks = 0
failures = 0


def check(label, cond, detail=""):
    global checks, failures
    checks += 1
    if cond:
        print(f"PASS {label}")
    else:
        failures += 1
        print(f"FAIL {label}: {detail}")


sinks = []


class _Sink(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(n)
        sinks.append({"idem": self.headers.get("Idempotency-Key", ""),
                      "body": json.loads(body.decode() or "{}")})
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *a):
        pass


srv = ThreadingHTTPServer(("127.0.0.1", 0), _Sink)
threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ["WF_WAKE_SINK_PORT"] = str(srv.server_address[1])

tmp = Path(tempfile.mkdtemp(prefix="wf-rundir-ptr-"))
OWNER = {"session_id": "a4t-session", "ui_session_id": "a4t-ui", "platform": "api_server"}
GRAPH = {"nodes": [{"id": "x", "type": "command", "cmd": "false", "needs": []}]}


def mk_run(run_id, graph=None):
    r = tmp / run_id
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "run.json").write_text(json.dumps(
        {"concurrency": 1, "node_timeout": 60, "owner": OWNER}))
    if graph is not None:
        (r / "graph.json").write_text(json.dumps(graph))
    return r


def ledger(r):
    p = r / "wake.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def content_of(post):
    return post["body"]["messages"][0]["content"]


try:
    # --- run.failed over a committed failed node record (efp-valid) ---
    r = mk_run("failed-1", GRAPH)
    byid = {n["id"]: n for n in GRAPH["nodes"]}
    child_log = r / "logs" / "x.a0.log"
    child_log.parent.mkdir()
    child_log.write_text("boom\n")
    (r / "nodes" / "x.json").write_text(json.dumps(
        {"status": "failed", "error": "fixture exit 1", "error_class": "exit",
         "log_path": str(child_log), "efp": wf.efp(byid, byid["x"])}))
    before = len(sinks)
    wf.notify(r, "run.failed", graph=GRAPH)
    posts = sinks[before:]
    rows = ledger(r)
    check("run.failed: exactly one POST", len(posts) == 1, str(posts))
    if posts:
        c = content_of(posts[0])
        check("run.failed: payload names the run dir", str(r) in c, c[:200])
        check("run.failed: payload names the failed-node log", str(child_log) in c, c[:200])
        check("run.failed: template body verbatim",
              "The workflow execution FAILED." in c, c[:200])
    check("run.failed: probe row carries the run dir",
          len(rows) == 1 and str(r) in rows[0].get("text", ""), str(rows))

    # --- run.done ---
    r2 = mk_run("done-1", GRAPH)
    before = len(sinks)
    wf.notify(r2, "run.done", graph=GRAPH)
    posts = sinks[before:]
    check("run.done: payload names the run dir",
          len(posts) == 1 and str(r2) in content_of(posts[0]),
          str(posts)[:200])

    # --- gate.held stays pointer-free (scope law) ---
    r3 = mk_run("held-1")
    before = len(sinks)
    wf.notify(r3, "gate.held", key="g1")
    posts = sinks[before:]
    check("gate.held: no run-dir pointer",
          len(posts) == 1 and str(r3) not in content_of(posts[0]),
          str(posts)[:200])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
    srv.shutdown()

print(f"\n{checks - failures}/{checks} checks passed")
sys.exit(1 if failures else 0)
