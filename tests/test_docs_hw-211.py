"""hw-211: the join node shipped in 1.3.0 but references/ carried zero mentions
of it — peers paid agent-spawn tokens for every merge because the contract doc
never said the node exists. This test IS the bead's gap-grep: it requires a
join-node section in references/grammar.md and its terminal/any + failed-leg +
author-typo + zero-token semantics by name, and pins the documented reject-set
row against the shipped validator (wfcommon.JOIN_KEYS) so the section cannot
drift. Stdlib only, no spawn, no network; exit 0 = green.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
root = HERE.parent
os.environ.setdefault("HERMES_HOME", str(HERE / ".suite-home"))
sys.path.insert(0, str(root))
import wfcommon  # noqa: E402

grammar = (root / "references" / "grammar.md").read_text(encoding="utf-8")
fails = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + (f"  << {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(msg)


m = re.search(r"^## .*join.*$", grammar, re.M | re.I)
check(m is not None, "grammar.md carries a join-node section (gap-grep non-empty)")
sec = ""
if m:
    rest = grammar[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    sec = " ".join((rest[:nxt.start()] if nxt else rest).split())  # collapse line wraps: the contract is prose, not layout

check("zero tokens" in sec, "section says the join is a zero-token mechanic")
check('"terminal"' in sec and '"any"' in sec, "section documents the terminal/any modes")
check("precondition" in sec and "join parent failed" in sec,
      "section names the failed-leg loud fail (precondition / join parent failed)")
check("author typo" in sec and "no such path" in sec,
      "section names the author-typo fail (no such path in committed output)")
check("skipped" in sec and "tolerant" in sec, "section documents skipped-leg join tolerance")
check("1.3.0" in sec, "section records the shipped version")
_allowed = "unknown key; allowed: " + json.dumps(sorted(wfcommon.JOIN_KEYS))
check(_allowed in sec, "section quotes the door's reject-set row verbatim (JOIN_KEYS drift guard)",
      _allowed)

# behavioural pin: the documented closed set is the shipped one — a stray key
# on a join is refused at the door naming the node and field (validator only).
errs = wfcommon.validate_graph_errors([
    {"id": "a", "type": "agent", "goal": "x"},
    {"id": "j", "type": "join", "after": ["a"], "keys": {"v": "a.result"},
     "wait": "terminal", "when": "out.a.x == 1"}])
check(any(e.get("node") == "j" and e.get("field") == "when" for e in (errs or [])),
      "door still refuses join + when (closed set holds)", str(errs))

if fails:
    print(f"{len(fails)} FAILURES")
    sys.exit(1)
print("ALL PASS: hw-211 join-node docs")
