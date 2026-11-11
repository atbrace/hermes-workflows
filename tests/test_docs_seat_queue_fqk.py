#!/usr/bin/env python3
"""The FIFO seat queue shipped in est-2ek.1.856/.857 must be DOCUMENTED.

Symptom: the queue landed with zero doc mentions. A 17-minute
starvation field report is exactly why operators deserve to see the mechanism:
markers under <seats>/queue/, the (enqueued, uuid) order key, the
0.5 s / 8 s / 20 s liveness windows, unreadable markers blocking admission,
and every external prune logged to <seats>/.pruned.jsonl.

The pin is two-sided: the doc must name each fact, and the numbers it names
must MATCH wf.py's constants, so the doc can neither be missing nor drift.

Run: python3 tests/test_docs_seat_queue_fqk.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "references" / "operations.md"
WF = ROOT / "wf.py"

fails = total = 0


def check(name, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL " + name) + (f" :: {detail[:300]}" if detail and not cond else ""),
          flush=True)
    if not cond:
        fails += 1


def section(text, heading):
    i = text.find(heading)
    if i < 0:
        return ""
    rest = text[i:]
    nxt = re.search(r"\n## (?!#)", rest[len(heading):])
    return rest[: len(heading) + nxt.start()] if nxt else rest


doc = DOC.read_text(encoding="utf-8")
sec = section(doc, "## Global agent-seat admission")
src = WF.read_text(encoding="utf-8")


def constant(name):
    m = re.search(rf"^{name} = ([0-9.]+)", src, re.M)
    return m.group(1) if m else None


hb, live, prune = (constant(k) for k in
                   ("SEAT_QUEUE_HB_S", "SEAT_QUEUE_LIVE_S", "SEAT_QUEUE_PRUNE_S"))

# The constants exist in code (the doc's source of truth).
for name, val in (("SEAT_QUEUE_HB_S", hb), ("SEAT_QUEUE_LIVE_S", live),
                  ("SEAT_QUEUE_PRUNE_S", prune)):
    check(f"wf.py still defines {name}", val is not None,
          "constant removed/renamed — update this test and the doc together")

# THE GAP: the docs must carry the queue, in the seat-admission section.
check("references/operations.md has a seat-queue section",
      "queue" in sec.lower() and "marker" in sec.lower(),
      "zero doc mentions of the FIFO seat queue markers")
check("the doc names the marker path <seats>/queue/", "queue/" in sec)
check("the doc names the order key (enqueued, uuid)", "(enqueued, uuid)" in sec)
check("the doc says FIFO/ordering gates admission, fairness only",
      "FIFO" in sec and "fairness" in sec,
      "must state markers gate FAIRNESS only, never capacity")
check("the doc says an unreadable marker BLOCKS admission",
      re.search(r"unreadable[^.]*block", sec, re.I) is not None,
      "'unreadable marker blocks admission' missing")
check("the doc names the prune ledger .pruned.jsonl", ".pruned.jsonl" in sec)
check("the doc names the ledger fields",
      all(k in sec for k in ("pruner", "reason")),
      "ledger row must name ts/pruner/kind/name/row snapshot/reason")

# The numbers must match the code, not folklore.
if hb and live and prune:
    check(f"doc names the heartbeat cadence {hb} s", re.search(rf"\b{re.escape(hb)}\b", sec) is not None)
    check(f"doc names the liveness window {live} s", re.search(rf"\b{re.escape(live)}\b", sec) is not None)
    check(f"doc names the prune window {prune} s", re.search(rf"\b{re.escape(prune)}\b", sec) is not None)

print(f"TOTAL {total - fails} PASS {fails} FAIL", flush=True)
raise SystemExit(1 if fails else 0)
