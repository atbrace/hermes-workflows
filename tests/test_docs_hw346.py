#!/usr/bin/env python3
"""hw-346: the shipped docs must state the GATE-OUTPUT SHAPE LAW and name the
silent-success trap of arms routed on a gate field other than `.answer`.

Measured defect (haus-estate consolidation run 20261111-162224-wof-study-council):
arms routed on `out.<gate>.option` resolve MISSING paths to None (wfcommon
_when_atom dict.get, never an error), so no equality arm fires, BOTH arms prune,
and the run closes green with zero wake. Nothing in references/grammar.md or
SKILL.md carried the shape: a released gate commits `answer` under `.answer`; a
hold-timeout auto-release carries `_machine:"auto_release"` (the ONLY machine
read of default-vs-human); a pruned gate commits `{"gate": "skipped"}` and
carries no `answer` at all.

The pins bite on the section the gate author actually reads, and the
engine-sync guard reads the literals out of wf.py so doc and engine go red
together on drift either way (R6; precedent test_error_class_doc_sync.py).
The mutation probe re-runs every doc pin against a snapshot of the shipped
v1.4.7 Gates paragraph — the pre-fix text — proving the pins bite forever,
not just on this checkout (precedent test_grammar_hw-bgb.py).

Run: python3 tests/test_docs_hw346.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
grammar = (root / "references" / "grammar.md").read_text(encoding="utf-8")
skill = (root / "SKILL.md").read_text(encoding="utf-8")
wfs = (root / "wf.py").read_text(encoding="utf-8")

ok = True


def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and cond


# The section a gate author reads, sliced heading-to-heading.
m = re.search(r"^## Gates and branches.*?(?=^## )", grammar, re.M | re.S)
check("gates section exists", m is not None)
section = m.group(0) if m else ""

PINS = [
    ("answers under .answer", lambda s: "answer" in s and ".answer" in s),
    ("names the pruned-gate record", lambda s: re.search(r'\{\\?"gate\\?"\s*:\s*\\?"skipped', s) is not None),
    # The quoted VALUE literal: the shipped text already names the
    # gate.auto_released EVENT, so only `"auto_release"` as a committed value
    # is the gap the council grepped for.
    ("names _machine:\"auto_release\" as the default-vs-human read",
     lambda s: "_machine" in s and '"auto_release"' in s),
    ("names the trap (None resolves, both arms pruned, green, no wake)",
     lambda s: all(w in s for w in ("None", "prune", "green", "wake"))
     and re.search(r"silent", s) is not None),
]
for label, pin in PINS:
    check(f"grammar: {label}", pin(section))

# SKILL.md carries the law in one line (the front-door read is where the trap bites).
check("SKILL.md names .answer", ".answer" in skill)
check("SKILL.md names auto_release", "auto_release" in skill)

# Engine sync: the documented literals exist in the runner, so this pin goes
# red the day the engine changes the shape out from under the docs.
check("engine emits auto_release", '"auto_release"' in wfs)
check('engine emits {"gate": "skipped"}', '"gate": "skipped"' in wfs)
check("engine stamps _machine", '"_machine"' in wfs)

# Mutation probe: every doc pin must FAIL on the shipped v1.4.7 text (snapshot)
# — the pin is a law-check, not a tautology.
PREFIX_V147 = (
    "## Gates and branches\n\nA gate has `type:\"gate\"`, `after`, optional "
    "`question`/`options`, `when`, `on_skip`, `default_option`, `hold_timeout`. "
    "Human gates hold until release; with `hold_timeout` (s) the runner parks at "
    "zero tokens and, at expiry, releases with `default_option` (event "
    "`gate.auto_released`). Gate options are answer DATA.\n"
)
for label, pin in PINS:
    check(f"pin bites pre-fix text: {label}", not pin(PREFIX_V147))

print("ALL PASS: docs state the gate-output shape law and the silent-arm trap"
      if ok else "FAILURES")
sys.exit(0 if ok else 1)
