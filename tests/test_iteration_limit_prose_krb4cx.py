#!/usr/bin/env python3
"""sys-989kek (krb4cx) — the CLI's iteration-limit PROSE classifies as
cap_exhausted so the existing bounded re-drive re-drives the node instead of
the card falling to hand-build as `unknown`.

Pins behavior, not spelling:
  (1) the verbatim krb4cx capture -> ('cap_exhausted', the cap line);
  (2) the typed -Q report path sees the same wording;
  (3) the 0923 law still holds: stdout prose naming `max_turns` alone is NOT
      promotable to a cap claim (report TEXT only).

Run: cd tests && python3 test_iteration_limit_prose_krb4cx.py
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wf  # noqa: E402

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

KRB4CX = ("Session x found but has no messages. Starting fresh.\n"
          "I reached the iteration limit and couldn't generate a summary.\n")
cls, marker = wf._classify_rc_output(KRB4CX)
check("krb4cx capture -> cap_exhausted", cls == "cap_exhausted",
      f"got {cls!r} marker={marker!r}")
check("marker is the cap line", bool(marker) and "iteration limit" in marker, repr(marker))

with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "report.json"
    p.write_text(json.dumps({"turn_exit_reason": "reached the iteration limit"}))
    tcls, _ = wf._typed_error_class(p)
check("typed report -> cap_exhausted", tcls == "cap_exhausted", repr(tcls))

cls2, _ = wf._classify_rc_output("Session found. max_turns noted in unrelated prose.\n")
check("max_turns prose stays unpromotable (0923 law)", cls2 == "unknown", f"got {cls2!r}")

# sys-989kek review: the gate must be the anchored cap SENTENCE only — legacy
# tokens in plain prose stay unpinnable, or a non-retryable 400 whose summary
# idles about limits gets masked into a re-drivable cap_exhausted.
cls3, _ = wf._classify_rc_output("Error code: 400 - invalid request\n"
                                 "Summary: I stayed well under the turn limit.\n")
check("legacy 'turn limit' prose does not mask provider_400 (0923 law)",
      cls3 == "provider_400", f"got {cls3!r}")
cls4, _ = wf._classify_rc_output("Plan: keep under the tool call limit of 40.\n"
                                 "Traceback (most recent call last):\nboom\n")
check("legacy 'tool call limit' prose stays unknown", cls4 == "unknown", f"got {cls4!r}")

sys.exit(0 if ok else 1)
