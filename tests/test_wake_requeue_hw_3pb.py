#!/usr/bin/env python3
"""hw-3pb: runtime_coordination_required is a TYPED refusal, and its bounded
requeue is one attempt past the lease window — a second refusal settles.

The ledger evidence (run 20261116-152922, wake.jsonl): session.resume refused
runtime_coordination_required (the owner chat's desktop backend holds the
session turn lease; TTL 300 s, renewed at turn start) and deliver() folded the
whole class into outcome=retry reason=transport_error. The runner wrote one
try-later row and exited, so a wake fired while the chat was active died
forever — even though the identical resume lands minutes after lease expiry.

Laws this pins:
  * TYPED: a resume refusal of runtime_coordination_required maps to
    reason=runtime_coordination, never the transport_error bucket
    (wake_native level), and the wake.jsonl row carries error_reason verbatim.
  * TOO-EARLY RE-DRIVE IS A NO-OP: inside WAKE_REQUEUE_AFTER_S a re-drive
    neither calls the adapter nor writes a row (an attempt cannot prove).
  * ONE BOUNDED RE-DRIVE: the first re-drive past the window calls the
    adapter again under the SAME instance id.
  * SECOND REFUSAL SETTLES: delivered=None + native_refused detail; every
    later re-drive costs zero rows and zero calls.
  * ARMED DRIVER: a first refusal arms the existing trailing-recheck marker
    (due = now + window) — no new daemon.
Direct notify() against a real run dir with a fake wake module; the
wake_native level drives the real module with a failing fake client.
"""
import json
import os
import shutil
import sys
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
for _k in ("WF_WAKE_SINK_PORT", "API_SERVER_KEY", "API_SERVER_HOST", "API_SERVER_PORT",
           "WF_RUNS_ROOT"):
    os.environ.pop(_k, None)
os.environ["HERMES_HOME"] = tempfile.mkdtemp(prefix="wf-3pb-home-")
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


class FakeWake:
    SCHEMA = "wake-native-admission/v1"

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def deliver(self, sid, text, tid, home):
        self.calls.append(tid)
        return self.outcomes[min(len(self.calls) - 1, len(self.outcomes) - 1)]


RETRY_RC = {"outcome": "retry", "reason": "runtime_coordination"}


def rows(run):
    return [json.loads(l) for l in (run / "wake.jsonl").read_text().splitlines() if l.strip()]


def backdate(run, secs):
    old = (datetime.now(timezone.utc) - timedelta(seconds=secs)).isoformat(timespec="seconds")
    rs = rows(run)
    rs[0]["ts"] = old
    with open(run / "wake.jsonl", "w") as f:
        for r in rs:
            f.write(json.dumps(r) + "\n")


run = Path(tempfile.mkdtemp(prefix="wf-3pb-")) / "run-3pb"
run.mkdir()
(run / "run.json").write_text(json.dumps(
    {"id": "run-3pb", "owner": {"session_id": "owner-chat", "platform": "local"}}))

fake = FakeWake([RETRY_RC])
wf._WAKE_NATIVE, wf._WAKE_NATIVE_TRIED = fake, True

verdict = wf.notify(run, "run.failed", key="t-requeue")
r1 = rows(run)
check("S1 first refusal records a typed try-later row",
      verdict == "undelivered" and len(r1) == 1 and fake.calls and
      r1[0].get("delivered") is False and r1[0].get("error_class") == "native_retry"
      and r1[0].get("error_reason") == "runtime_coordination", str(r1))
mk = wf._wake_marker_path(run, "run.failed")
st = json.loads(mk.read_text())
check("S1b first refusal arms the recheck marker at lease window + margin",
      st.get("pending") is True and
      300 <= st["due"] - st["fire_ts"] <= wf.WAKE_REQUEUE_AFTER_S + 5, str(st))

tid = r1[0]["id"]
verdict = wf.notify(run, "run.failed", key="t-requeue")
check("S2 too-early re-drive: no adapter call, no new row",
      verdict == "undelivered" and len(fake.calls) == 1 and len(rows(run)) == 1, str(rows(run)))

backdate(run, wf.WAKE_REQUEUE_AFTER_S + 40)
verdict = wf.notify(run, "run.failed", key="t-requeue")
r2 = rows(run)
check("S3 first re-drive past the window re-drives under the SAME identity",
      verdict == "undelivered" and len(fake.calls) == 2 and len(r2) == 2 and
      r2[1]["id"] == tid and r2[1].get("error_reason") == "runtime_coordination", str(r2))
check("S3b marker re-armed after the second refusal",
      json.loads(mk.read_text()).get("pending") is True)

verdict = wf.notify(run, "run.failed", key="t-requeue")
r3 = rows(run)
_, settled = wf._wake_ledger_read(run)
check("S4 second refusal settles: delivered=None, typed detail, budget spent",
      len(r3) == 3 and r3[2].get("delivered") is None
      and r3[2].get("error_class") == "native_refused" and tid in settled, str(r3))

verdict = wf.notify(run, "run.failed", key="t-requeue")
check("S5 settled instance: zero rows, zero calls",
      verdict == "delivered" and len(fake.calls) == 2 and len(rows(run)) == 3)

# wake_native level: the RPC code itself is typed, not the transport bucket
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("wn_3pb", ROOT / "wake_native.py")
wn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wn)


class Client:
    async def rpc(self, method, **params):
        raise RuntimeError("runtime_coordination_required: session writer lease live")


@asynccontextmanager
async def connect(endpoint):
    yield Client()


with patch.object(wn, "discover", return_value="ep"), patch.object(wn, "_connect", connect):
    out = wn.deliver("owner-chat", "wake", "tid-3pb", "/home")
check("S6 resume refusal is typed runtime_coordination, not transport_error",
      out == {"outcome": "retry", "reason": "runtime_coordination"}, str(out))

shutil.rmtree(run.parent, ignore_errors=True)
print(f"hw-3pb: {checks} checks, {failures} failures")
sys.exit(1 if failures else 0)
