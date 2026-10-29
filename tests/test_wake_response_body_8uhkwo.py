#!/usr/bin/env python3
"""sys-8uhkwo: a refused wake POST records the refusal REASON in wake.jsonl.

Law pinned here: when the wake endpoint answers non-2xx, the ledger row carries
rec["body"] — the gateway's refusal body, bounded to the first 512 bytes,
decoded errors="replace", bearer-redacted at the read site (the persist-time
loop in _wake_append covers only text/error). An empty or unreadable body
records NO body key: the row survives, fail-open law unchanged.

RED on 3b38a04: _wake_deliver stored only f"HTTP {status}" / f"HTTP {e.code}"
at both record sites and discarded the body — a 409 (mid-turn vs
TUI-not-wakeable) was undiagnosable from the ledger.

Script-style like its wake-suite siblings (fresh-process, exit code is the
verdict); ONE pytest-collectible def test so `pytest -k response_body` names a
real item instead of exiting 5 (conftest ScriptModule mode runs this file as a
subprocess; the __main__ block is the merge-gate contract).
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


tmp = Path(tempfile.mkdtemp(prefix="wf-wake-body-"))
RUNS = tmp / "workflows"
OWNER = {"session_id": "wake-body-session", "ui_session_id": "wake-body-ui",
         "platform": "api_server"}


def mk(run_id):
    r = RUNS / run_id
    (r / "nodes").mkdir(parents=True)
    (r / "gates").mkdir()
    (r / "graph.json").write_text(json.dumps({"name": run_id, "nodes": []}))
    (r / "run.json").write_text(json.dumps({"concurrency": 1, "owner": OWNER}))
    return r


def wakes(r):
    p = r / "wake.jsonl"
    try:
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    except FileNotFoundError:
        return []


_refused_body = {}


class _Refusal(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(n)
        self.send_response(_refused_body["code"])
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(_refused_body["body"])
    def log_message(self, *a):
        pass


def refused_notify(run_id, code, body):
    """One notify() against a sink that refuses with (code, body); returns the
    single wake.jsonl row (the attempt itself is what we pin)."""
    import wf as _wf
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Refusal)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        _refused_body.update({"code": code, "body": body})
        r = mk(run_id)
        saved = os.environ.get("WF_WAKE_SINK_PORT")
        os.environ["WF_WAKE_SINK_PORT"] = str(srv.server_address[1])
        try:
            _wf.notify(r, "gate.held", key=f"held-{run_id}")
        finally:
            if saved is None:
                os.environ.pop("WF_WAKE_SINK_PORT", None)
            else:
                os.environ["WF_WAKE_SINK_PORT"] = saved
        return r
    finally:
        srv.shutdown()


def _run_all():
    # ---- 1. a 409 with a JSON reason: the reason survives into the ledger ----
    r = refused_notify("b409", 409,
                       b'{"error":{"message":"session mid-turn; wake deferred"}}')
    w = wakes(r)
    check("409 row recorded undelivered", len(w) == 1 and w[0].get("delivered") is False, w)
    check("409 error field keeps the status", bool(w) and w[0].get("error") == "HTTP 409", w)
    check("409 refusal reason persisted in body",
          bool(w) and "mid-turn" in w[0].get("body", ""), str(w))

    # ---- 2. bearer shapes in the body are redacted before persist ----
    r = refused_notify("b500", 500,
                       b'refuse_reason: Authorization: Bearer SUPER-SECRET-CRED-42; retry')
    w = wakes(r)
    raw = (r / "wake.jsonl").read_text()
    check("500 refusal body persisted", bool(w) and "refuse_reason" in w[0].get("body", ""), str(w))
    check("bearer secret never persisted in wake probe",
          "SUPER-SECRET-CRED-42" not in raw, raw)

    # ---- 3. the body is bounded: first 512 bytes only ----
    r = refused_notify("bcap", 400, b"x" * 3000 + b"TAILMARKER")
    w = wakes(r)
    check("body bounded to first 512 bytes",
          bool(w) and w[0].get("body") == "x" * 512, str(w)[:200])

    # ---- 4. empty refusal body: row without body key, fail-open, no raise ----
    r = refused_notify("bnone", 502, b"")
    w = wakes(r)
    check("empty body records the row without a body key",
          len(w) == 1 and w[0].get("delivered") is False and "body" not in w[0], w)

    shutil.rmtree(tmp, ignore_errors=True)


def test_response_body_refusal_reason_recorded_redacted_and_bounded():
    _run_all()
    assert failures == 0, f"{failures} of {checks} checks failed (see PASS/FAIL lines)"


if __name__ == "__main__":
    _run_all()
    print(f"TOTAL {checks} FAIL {failures}")
    sys.exit(1 if failures else 0)
