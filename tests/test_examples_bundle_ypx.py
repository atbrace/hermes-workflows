#!/usr/bin/env python3
"""hw-ypx: the shipped bundle must carry a human atom, a decision-park starter
term, and a carrier-scale reference. The council's gap-grep (bead wording)
must go non-empty against the shipped tree, and both new graphs must pass the
door as authored. Stdlib-only; prints PASS/FAIL, exit 0 = green."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ok = True
_n = 0


def check(name, cond, detail=""):
    global ok, _n
    _n += 1
    if cond:
        print(f"PASS {name}")
    else:
        ok = False
        print(f"FAIL {name} :: {detail[:200]}")


ATOM = ROOT / "examples" / "basics" / "human-atom.json"
CARRIER = ROOT / "examples" / "ops" / "bead-to-prod.json"


def load(p):
    return json.loads(p.read_text())


def door_validate(path):
    return subprocess.run([sys.executable, str(ROOT / "wf.py"), "validate", str(path)],
                          cwd=ROOT, capture_output=True, text=True)


check("B1 basics/human-atom.json is bundled", ATOM.is_file(), str(ATOM))
check("B2 ops/bead-to-prod.json is bundled", CARRIER.is_file(), str(CARRIER))

if ATOM.is_file():
    r = door_validate(ATOM)
    check("B3 human-atom passes the door", r.returncode == 0, r.stdout + r.stderr)
    g = load(ATOM)
    gates = [n for n in g.get("nodes", []) if n.get("type") == "gate"]
    check("B4 the human atom carries a human gate", bool(gates), str(g))
    check("B5 post hold-vs-wall: a human decision gate holds, no wall "
          "(no hold_timeout on the gate)",
          all("hold_timeout" not in n for n in gates),
          str([n.get("id") for n in gates if "hold_timeout" in n]))
    check("B6 the decision-park starter names itself in its contract",
          "decision-park" in (g.get("description") or "").lower(),
          g.get("description", ""))

if CARRIER.is_file():
    r = door_validate(CARRIER)
    check("B7 bead-to-prod passes the door", r.returncode == 0, r.stdout + r.stderr)
    g = load(CARRIER)
    nodes = {n["id"]: n for n in g.get("nodes", [])}
    check("B8 the carrier publishes under a suite proof",
          any(n.get("publishes") for n in g["nodes"])
          and any(n.get("suite_proof") for n in g["nodes"]), str(list(nodes)))

# DIAGRAM LAW 3: both graphs ship their cards sidecar (the only hand-authored input).
for gpath in (ATOM, CARRIER):
    side = gpath.with_name(gpath.name[:-5] + ".cards.json")
    if gpath.is_file():
        check(f"B9 cards sidecar beside {gpath.name}", side.is_file(), str(side))
        if side.is_file():
            cards = load(side).get("cards", [])
            check(f"B10 exactly two cards for {gpath.name}", len(cards) == 2, str(len(cards)))

# The bead's own gap-grep: its wording finds the bundle in the shipped tree.
maptext = (ROOT / "examples" / "README.md").read_text()
for term in ("human-atom", "bead-to-prod", "decision-park"):
    hits = subprocess.run(
        ["grep", "-rli", term, str(ROOT / "examples")],
        capture_output=True, text=True).stdout.strip()
    check(f"B11 gap-grep '{term}' goes non-empty in examples/", bool(hits), hits)
check("B12 the human atom and the carrier are on the examples map",
      "human-atom.json" in maptext and "bead-to-prod.json" in maptext, "")

print(f"{'ALL PASS' if ok else 'FAILURES PRESENT'} ({_n} bundle contracts)")
sys.exit(0 if ok else 1)
