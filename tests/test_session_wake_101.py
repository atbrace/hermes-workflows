#!/usr/bin/env python3
"""Session-wake law: lifecycle TRANSITIONS reach the owner session stamp, exactly once.

The failure mode this pins: `run` stamps owner {session_id, ui_session_id, platform}
into run.json (the door's own comment: absent => "UI asks for manual resume"), the
runner then announces gate.held / run.done / run.failed by printing WORKFLOW_* lines
— and stdout is a file (`_spawn_runner` redirects it to runner.log). A tool-launched
run that holds a gate, finishes, or dies while nobody tails runner.log is invisible
to the session that launched it.

Law pinned here (transitions only — the stdout text itself is untouched):
  * one wake delivery per lifecycle transition (gate.held / run.done / run.failed)
    for a run whose run.json owner is stamped, recorded in <run>/wake.jsonl;
  * exactly ONE line per transition — a gate that parks in-process (hold_timeout)
    adds zero per-tick lines while it spins;
  * an owner-null run (tests, CLI) appends NOTHING, exactly like today's silent
    degradation — the WORKFLOW_* stdout vocabulary is identical either way;
  * the transition survives resume: held (process 1) + done (process 2) = 2 lines,
    never a re-notify of the same held.

The delivery surface is stubbed here via WF_WAKE_SINK_PORT (a localhost HTTP sink
records the wake POST; no gateway needed), so this test runs in CI unchanged —
the same stub env var the plugin's delivery path already honors.

RED on 224a9ea: `notify` does not exist — every wake.jsonl assertion below fails
(no file, no lines), stdout checks pass (they are the invariant, not the feature).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402  (gate answers must carry the current efp, like the door's)

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

FAKE = str(HERE / "fake")
OWNER = {"session_id": "wake-test-session", "ui_session_id": "wake-test-ui", "platform": "api_server"}

# ---- stubbed delivery sink: records every wake POST the fix makes ----
sinks = []

class _Sink(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(n)
        sinks.append({"path": self.path,
                      "session_header": self.headers.get("X-Hermes-Session-Id", ""),
                      "body": json.loads(body.decode() or "{}")})
        self.send_response(202)
        self.end_headers()
        self.wfile.write(b"{}")
    def log_message(self, *a):
        pass

_sink_srv = ThreadingHTTPServer(("127.0.0.1", 0), _Sink)
threading.Thread(target=_sink_srv.serve_forever, daemon=True).start()
SINK_PORT = _sink_srv.server_address[1]


tmp = Path(tempfile.mkdtemp(prefix="wf-wake-"))

def env():
    # HERMES_HOME scopes the runs root (wfcommon.runs_root); WF_WAKE_SINK_PORT stubs
    # the delivery endpoint the same way a gateway's api_server binds it.
    return dict(os.environ, HERMES_HOME=str(tmp), WF_WAKE_SINK_PORT=str(SINK_PORT),
                FAKE_LOG=str(tmp / "fake.log"))

(tmp / "fake.log").write_text("")
RUNS = tmp / "workflows"


def mk(run_id, nodes, owner):
    r = RUNS / run_id
    if r.exists():
        shutil.rmtree(r)
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": nodes}))
    meta = {"hermes_bin": FAKE, "concurrency": 1, "node_timeout": 60}
    if owner is not None:
        meta["owner"] = owner
    (r / "run.json").write_text(json.dumps(meta))
    return r


def drive(r, extra_env=None):
    """One runner process, stdout captured (the door's spawn redirects this to runner.log)."""
    e = env()
    e.update(extra_env or {})
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", r.name],
                          env=e, capture_output=True, text=True, timeout=90, cwd=str(ROOT))


def wakes(r):
    p = r / "wake.jsonl"
    try:
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    except FileNotFoundError:
        return []


def answer(r, gid, val):
    g = jg = json.loads((r / "graph.json").read_text())
    byid = {n["id"]: n for n in g["nodes"]}
    gate = byid[gid]
    (r / "gates" / f"{gid}.json").write_text(json.dumps(
        {"answer": val, "_def": wfcommon.efp(byid, gate), "fp_rule_version": wfcommon.FP_RULE_VERSION}))


def wait_for(fn, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        v = fn()
        if v:
            return v
        time.sleep(0.1)
    return None


try:
    # ---- 1. gate.held on an owner-stamped run fires EXACTLY ONE wake ----
    G_HOLD = [{"id": "n1", "type": "agent", "goal": "LIST: go"},
              {"id": "g1", "type": "gate", "after": ["n1"], "question": "ship?", "options": ["yes", "no"]}]
    r = mk("w1", G_HOLD, OWNER)
    out = drive(r).stdout.strip()
    check("stdout vocabulary intact (HELD)", out.startswith(f"WORKFLOW_HELD {r.name} g1"), out)
    w = wakes(r)
    check("gate.held fires exactly one wake", len(w) == 1 and w[0].get("event") == "gate.held", w)
    check("wake carries run_id + owner stamp",
          bool(w) and w[0].get("run_id") == r.name and w[0].get("owner") == OWNER, w)
    check("wake text names the run (nudge shape)", bool(w) and r.name in w[0].get("text", ""), w)
    check("sink saw the delivery", any(s["session_header"] == OWNER["session_id"] for s in sinks), str(sinks))

    # ---- 2. owner-null run fires ZERO wakes, stdout identical ----
    sinks.clear()
    r2 = mk("w2", G_HOLD, None)
    out2 = drive(r2).stdout.strip()
    check("owner-null stdout vocabulary intact", out2.startswith(f"WORKFLOW_HELD {r2.name} g1"), out2)
    check("owner-null fires zero wakes", wakes(r2) == [] and not (r2 / "wake.jsonl").exists(), wakes(r2))
    check("owner-null touches no delivery endpoint", sinks == [], sinks)

    # ---- 3. transition-only across resume: held (proc 1) + done (proc 2) = 2 lines ----
    G_FLOW = [{"id": "n1", "type": "agent", "goal": "LIST: go"},
              {"id": "g1", "type": "gate", "after": ["n1"], "question": "ship?", "options": ["yes", "no"]},
              {"id": "n2", "type": "agent", "after": ["g1"], "goal": "combine"}]
    r3 = mk("w3", G_FLOW, OWNER)
    out3 = drive(r3).stdout.strip()
    check("flow holds first", out3.startswith(f"WORKFLOW_HELD {r3.name} g1"), out3)
    check("held wake = 1 line", len(wakes(r3)) == 1, wakes(r3))
    answer(r3, "g1", "yes")
    out3b = drive(r3).stdout.strip()
    check("flow done after release", out3b.startswith(f"WORKFLOW_DONE {r3.name}"), out3b)
    w3 = wakes(r3)
    check("held+done = exactly 2 wakes (no held re-notify)",
          len(w3) == 2 and [e.get("event") for e in w3] == ["gate.held", "run.done"], w3)

    # ---- 4. run.failed fires one wake ----
    r4 = mk("w4", [{"id": "boom", "type": "agent", "goal": "FAILME"}], OWNER)
    out4 = drive(r4).stdout.strip()
    check("stdout vocabulary intact (FAILED)", out4.startswith(f"WORKFLOW_FAILED {r4.name}"), out4)
    w4 = wakes(r4)
    check("run.failed fires exactly one wake",
          len(w4) == 1 and w4[0].get("event") == "run.failed", w4)

    # ---- 5. park (hold_timeout) adds ZERO per-tick lines, then releases on the answer ----
    r5 = mk("w5", [{"id": "n1", "type": "agent", "goal": "LIST: go"},
                   {"id": "g1", "type": "gate", "after": ["n1"], "question": "ship?",
                    "options": ["yes", "no"], "hold_timeout": 600}], OWNER)
    n_turns_before = len((tmp / "fake.log").read_text().splitlines())
    e5 = env()
    p5 = subprocess.Popen([sys.executable, str(ROOT / "wf.py"), "run", r5.name],
                          env=e5, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, cwd=str(ROOT))
    t_park_start = time.time()
    w5a = wait_for(lambda: wakes(r5) or None, timeout=30)
    t_first_wake = time.time()
    check("parked hold wakes once", w5a is not None and len(wakes(r5)) == 1, w5a)
    time.sleep(2.0)   # >= 3 poll ticks of the park loop (0.5 s sleep)
    w5b = wakes(r5)
    check("zero per-tick wake lines while parked", len(w5b) == 1, w5b)
    answer(r5, "g1", "yes")
    out5 = p5.communicate(timeout=90)[0].strip()
    w5c = wakes(r5)
    check("park release -> done, 2 total wakes",
          len(w5c) == 2 and [e.get("event") for e in w5c] == ["gate.held", "run.done"], w5c)
    print(f"TIMING wake-latency-after-hold={t_first_wake - t_park_start:.2f}s "
          f"parked-window=2.0s ticks-skipped-without-extra-lines=true")
    n_turns_after = len((tmp / "fake.log").read_text().splitlines())
    check("park loop consumed zero extra agent turns",
          n_turns_after == n_turns_before + 1, f"before={n_turns_before} after={n_turns_after}")

    # ---- 6. delivery failure must not kill the runner (fail-open, loud) ----
    r6 = mk("w6", G_HOLD, OWNER)
    out6 = drive(r6, {"WF_WAKE_SINK_PORT": "1"}).stdout.strip()   # unroutable port
    check("dead sink keeps stdout + exit path intact",
          out6.startswith(f"WORKFLOW_HELD {r6.name} g1"), out6)
    w6 = wakes(r6)
    check("delivery failure recorded, not swallowed silently",
          bool(w6) and w6[0].get("delivered") is False, w6)

    # ---- 7. legacy/foreign owner shape (a bare string, not the dict stamp):
    #         degrade silently — never a crash, never a wake (R10 migration law) ----
    r7 = mk("w7", G_HOLD, "ignored")          # run.json owner: "some-string"
    out7 = drive(r7).stdout.strip()
    check("non-dict owner degrades silently", out7.startswith(f"WORKFLOW_HELD {r7.name} g1"), out7)
    check("non-dict owner writes no wake probe", not (r7 / "wake.jsonl").exists(), str(wakes(r7)))

    # ---- 8. a READ TIMEOUT is not a delivery: the event must stay retryable.
    #         Pinned in-process (notify() is pure stdlib): a sink that admits the
    #         connection then hangs past WAKE_TIMEOUT_S, so the client times out
    #         mid-read. A suppressed retry here means the owner NEVER learns the
    #         transition — the permanent-loss class. (F5) ----
    hang_done = threading.Event()

    class _Hang(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(n)
            hang_done.wait(30)                 # hang past the client's read window
            self.send_response(202)
            self.end_headers()
            self.wfile.write(b"{}")
        def log_message(self, *a):
            pass

    hang_srv = ThreadingHTTPServer(("127.0.0.1", 0), _Hang)
    threading.Thread(target=hang_srv.serve_forever, daemon=True).start()
    r8 = mk("w8", G_HOLD, OWNER)
    try:
        import wf as _wf
        _saved = _wf.WAKE_TIMEOUT_S
        _wf.WAKE_TIMEOUT_S = 0.5               # the constant is the whole contract
        try:
            e8 = env(); e8["WF_WAKE_SINK_PORT"] = str(hang_srv.server_address[1])
            os.environ["WF_WAKE_SINK_PORT"] = e8["WF_WAKE_SINK_PORT"]
            _wf.notify(r8, "gate.held", f"Workflow run {r8.name} is HELD at g1.", "held-def")
            w8a = wakes(r8)
            check("timeout attempt probe-records, delivered=false (retryable)",
                  len(w8a) == 1 and w8a[0].get("delivered") is False, w8a)
            hang_done.set()                    # release the stalled handler thread
            os.environ["WF_WAKE_SINK_PORT"] = str(SINK_PORT)   # fast sink now
            before = len(sinks)
            _wf.notify(r8, "gate.held", f"Workflow run {r8.name} is HELD at g1.", "held-def")
            w8b = wakes(r8)
            check("timeout does NOT suppress the retry: second attempt delivers",
                  len(w8b) == 2 and w8b[1].get("delivered") is True
                  and len(sinks) == before + 1, w8b)
            _wf.notify(r8, "gate.held", f"Workflow run {r8.name} is HELD at g1.", "held-def")
            check("a DELIVERED transition stays deduped (retry ends at success)",
                  len(wakes(r8)) == 2 and len(sinks) == before + 1, wakes(r8))
        finally:
            _wf.WAKE_TIMEOUT_S = _saved
    finally:
        hang_done.set()
        hang_srv.shutdown()

    # ---- 9. runner exception-CRASH (the write_runner_exit('crashed') net) pushes
    #         run.failed too: crash deaths emit no WORKFLOW_* stdout at all, so the
    #         probe+wake is the only non-polling signal the run died. Transition-only
    #         guard applies (event run.failed, key carries the crash reason). (F6) ----
    r9 = mk("w9", [{"id": "boom", "type": "agent", "goal": "LIST: go"}], OWNER)
    (r9 / "run.json").write_text(json.dumps(
        {"hermes_bin": FAKE, "concurrency": "abc", "node_timeout": 60, "owner": OWNER}))
        # concurrency:"abc" -> TypeError inside ThreadPoolExecutor, past acquire_lock:
        # the maintainer-verified crash trigger (tests/test_systemexit_stamp.py #3).
    out9 = drive(r9).stdout.strip()
    w9 = wakes(r9)
    check("crash wake fires exactly once",
          len(w9) == 1 and w9[0].get("event") == "run.failed"
          and "crashed" in w9[0].get("text", ""), w9)
    check("crash path stdout vocabulary unchanged (no new line)",
          "WORKFLOW_" not in out9, out9)
    check("crash still stamps runner_exit.json (net untouched)",
          (r9 / "runner_exit.json").exists()
          and "crashed" in json.loads((r9 / "runner_exit.json").read_text()).get("reason", ""),
          str((r9 / "runner_exit.json").read_text() if (r9 / "runner_exit.json").exists() else ""))
finally:
    _sink_srv.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)

print(f"TOTAL {checks} FAIL {failures}")
sys.exit(1 if failures else 0)
