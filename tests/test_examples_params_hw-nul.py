#!/usr/bin/env python3
"""hw-nul — the typed-params worked example must SHIP.

The #457 mechanism (top-level `params`, pin/tune, where/by) shipped undocumented
by example: a cold reader of examples/ found zero graph-level params blocks, so
the gap-grep from the bead is the acceptance law: `params` must go non-empty in
the shipped examples tree. Beyond presence, the pins below hold the example to
its teaching contract — it must pass the door's OWN params law (validate_graph_
full folds params_errors), carry at least one pin and one tune slot, exercise
both structural primitives (a `where` depth seam, a `by` verb-family patch),
appear on the examples map, and ride the pack include list (an unshipped example
is invisible to every install). Run directly: prints PASS lines, exits nonzero
on the first broken contract.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

GRAPH = ROOT / "examples" / "build" / "admission-lap.workflow.json"
DIA = (ROOT / "examples" / "diagrams").resolve()
ok = 0


def check(cond, msg, detail=""):
    global ok
    if not cond:
        print(f"FAIL {msg}" + (f"  << {detail}" if detail else ""))
        sys.exit(1)
    ok += 1
    print(f"PASS {msg}")


# --- the acceptance gap-grep: a shipped examples graph with a top-level params block
graphs = []
for dp, _, fs in (ROOT / "examples").walk():
    if DIA in Path(dp).resolve().parents or Path(dp).resolve() == DIA:
        continue  # derived artifacts (candidates, qa receipts) are not graphs
    for f in fs:
        p = Path(dp) / f
        if f.endswith(".json") and not f.endswith(".cards.json"):
            graphs.append(p)
carriers = [p for p in graphs
            if isinstance(json.loads(p.read_text(encoding="utf-8")).get("params"), dict)]
check(bool(carriers),
      "gap-grep: at least one shipped examples graph carries a top-level params block",
      f"{len(graphs)} graphs scanned, zero params blocks")

g = json.loads(GRAPH.read_text(encoding="utf-8"))
check(g.get("grammar") == "wf/1" and g.get("name") == "admission-lap",
      "admission-lap is a wf/1 graph named for its bead-row")

# the door's own law: the worked example must pass the validator the door uses
errs = wfcommon.validate_graph_full(g)
check(errs == [], "door validate_graph_full: zero defects", json.dumps(errs)[:400])
check(wfcommon.params_errors(g) == [], "params law clean (params_errors returns zero defects)")

p = g["params"]
kinds = {d.get("kind") for d in p.values()}
check("pin" in kinds and "tune" in kinds,
      "the example demonstrates BOTH kinds: a pin and a tune slot")
tune = {k: d for k, d in p.items() if d.get("kind") == "tune"}
check(all(isinstance(d.get("domain"), list) and d["domain"] for d in tune.values()),
      "every tune slot carries a non-empty domain")
nodes = {n["id"]: n for n in g["nodes"]}
wired = [n for n in nodes.values() if isinstance(n.get("where"), dict)]
patched = [n for n in nodes.values() if isinstance(n.get("by"), dict)]
check(bool(wired) and wired[0]["where"]["param"] in tune,
      "a `where` seam gates a declared tune slot (the depth ladder idiom)")
check(bool(wired) and all(v in tune[wired[0]["where"]["param"]]["domain"]
                          for v in wired[0]["where"]["in"]),
      "where.in lives inside the slot's domain (a dead gate is a typo)")
check(bool(patched) and set(patched[0]["by"]) <= set(tune),
      "a `by` patch switches on a declared tune slot (the verb-family idiom)")

# the dispatcher story: the LAUNCH brief is the zero-token echo carrying the
# effective bindings, and nothing downstream depends on the where-gated lane
# (removal cascade-prunes descendants — a dependent would vanish at the default)
brief = [n for n in nodes.values()
         if n.get("type") == "echo" and "{run." in json.dumps(n.get("output"))]
check(bool(brief), "the guard echo stamps the LAUNCH brief with the bound params")
gate_ids = {n["id"] for n in wired}
check(not any(gate_ids & set(n.get("after") or []) for n in nodes.values()),
      "no node hangs on the where-gated lane — pruning it at the default prunes nothing else")

# discoverable + shipped
readme = (ROOT / "examples" / "README.md").read_text(encoding="utf-8")
check("build/admission-lap.workflow.json" in readme,
      "the examples map carries the row (an unmapped example is invisible)")
check("admission-lap" in (ROOT / "scripts" / "pack.py").read_text(encoding="utf-8"),
      "pack.py ships the example (an unshipped example is invisible to every install)")

print(f"ALL PASS ({ok} hw-nul contracts)")
