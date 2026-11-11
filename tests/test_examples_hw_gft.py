#!/usr/bin/env python3
"""hw-gft: the rubric-repair example must ship as a *tested* example.

Bead wording under pin: author -> BLIND rubric scoring of the committed artifact
-> exactly one repair of named findings -> frontier re-score -> second-disagreement
STOP RULE -> exactly one disposition, plus a tour entry. The pins, all re-derivable
from the shipped bytes:
 - the graph validates clean and carries exactly the admission-loop node set;
 - blindness is by construction: the rubric seat consumes ONLY the artifact path
   (never the author's narrative) and the re-score consumes ONLY the repaired
   artifact plus the original findings (never the repair's claims);
 - the loop is structural, not implied: exactly one repair node; its `when` is
   complementary to the first-pass admit arm; the re-score hangs behind the
   repair so a clean first pass cascade-prunes the whole repair arm;
 - the STOP rule is a machine `when` on the disagreement count, complementary
   pair (halt vs admit), and each arm ends in exactly one disposition echoed at
   zero token cost;
 - every `when` parses under the bounded grammar;
 - the cards sidecar drives the derived diagram (fresh bytes, DIAGRAM LAW);
 - the map README and the tested tour carry the entry;
 - on a clean seat the pinned capability class `council_a` refuses the launch
   BY NAME with the valid list (the blind-council contract).
"""
import importlib.util
import io
import contextlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wfcommon  # noqa: E402

GPATH = ROOT / "examples" / "build" / "rubric-repair.workflow.json"
CPATH = ROOT / "examples" / "build" / "rubric-repair.workflow.cards.json"

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, f"{msg}" + (f"  << {detail}" if detail else "")
    ok += 1
    print("PASS", msg)

g = json.loads(GPATH.read_text())
check(wfcommon.validate_graph_errors(g) == [], "graph validates clean",
      json.dumps(wfcommon.validate_graph_errors(g)))
nodes = {n["id"]: n for n in g["nodes"]}
check(set(nodes) == {"author", "rubric", "clear-gate", "admit-first-pass",
                     "repair", "rescore", "halt-gate", "stop",
                     "admit-gate", "accept"},
      "exactly the admission-loop node set", sorted(nodes))

# blind by construction: each scoring seat reads only what its schema needs
check(nodes["rubric"]["inputs"] == ["author.artifact"],
      "rubric seat is blind to the author's narrative (inputs pick the artifact path only)",
      json.dumps(nodes["rubric"].get("inputs")))
check(nodes["rescore"]["inputs"] == ["repair.artifact", "rubric.findings"],
      "re-score sees the repaired artifact + original findings, never the repair's claims",
      json.dumps(nodes["rescore"].get("inputs")))

# exactly one repair, gated by the first verdict; pair complementary
repairs = [n for n in g["nodes"] if n["id"] == "repair"]
check(len(repairs) == 1, "exactly one repair node exists")
check(nodes["repair"]["when"] == "out.rubric.verdict == 'findings'"
      and nodes["clear-gate"]["when"] == "out.rubric.verdict == 'pass'",
      "first-pass arms are a complementary pair carried by the arm heads themselves")
check(nodes["repair"].get("on_skip") == "prune"
      and nodes["clear-gate"].get("on_skip") == "prune",
      "both first-pass arms prune, never pass-through")
check(nodes["rescore"]["after"] == ["repair"],
      "re-score hangs behind the repair: a clean pass cascade-prunes the whole repair arm")

# second-disagreement STOP is a machine `when` on the disagreement count
HALT = "out.rescore.disagreements >= 2"
ADMIT = "out.rescore.disagreements < 2"
check(nodes["halt-gate"]["when"] == HALT and nodes["admit-gate"]["when"] == ADMIT,
      "halt vs admit is a complementary machine-`when` pair on the disagreement count")
check(nodes["halt-gate"]["type"] == "gate" and nodes["admit-gate"]["type"] == "gate"
      and "wait" in nodes["halt-gate"] and "wait" in nodes["admit-gate"],
      "the STOP rule is evaluated by machine gates (wait timers), no human hold")
check(all(n["on_skip"] == "prune" for n in (nodes["halt-gate"], nodes["admit-gate"])),
      "halt/admit arms prune on the untaken branch")

# exactly one disposition per arm, echoed at zero token cost
for did, parent in (("admit-first-pass", "clear-gate"), ("stop", "halt-gate"),
                    ("accept", "admit-gate")):
    d = nodes[did]
    check(d["type"] == "echo" and d["after"] == [parent],
          f"disposition {did!r} is an echo behind its arm head {parent!r}")
dispositions = [n for n in g["nodes"] if n["type"] == "echo"]
check(len(dispositions) == 3, "the graph carries exactly the three arm dispositions")

# bounded-grammar teeth on every branch predicate
for nid in ("clear-gate", "repair", "halt-gate", "admit-gate"):
    err = wfcommon.when_expr_ok(nodes[nid]["when"])
    check(err is None, f"when on {nid} parses under the bounded grammar", str(err))

# the schema carries the machine fields the when-predicates read
check("verdict" in nodes["rubric"]["schema"]["required"]
      and "findings" in nodes["rubric"]["schema"]["required"],
      "rubric schema requires verdict + findings (findings verbatim to the repair)")
check("disagreements" in nodes["rescore"]["schema"]["required"],
      "re-score schema requires the disagreements count the STOP rule reads")

# description is the full contract: named seeds + the capability-class law
desc = g["description"]
check("run_context" in desc and "artifact_spec" in desc and "rubric" in desc,
      "description names its run_context seeds")
check("council_a" in desc, "description documents the pinned capability class")
check(nodes["rescore"]["model"] == "council_a",
      "the frontier re-score is the pinned seat; the rest ride defaults")

# DIAGRAM LAW: the cards sidecar exists and the committed candidate is fresh
check(CPATH.is_file(), "cards sidecar authored beside the graph")
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "graph_diagram.py"),
                    "--check", str(GPATH.relative_to(ROOT))],
                   cwd=ROOT, capture_output=True, text=True)
check(r.returncode == 0, "derived diagram candidate is fresh (--check green)",
      (r.stdout + r.stderr)[:300])

# the map and the tour carry the entry
row = [ln for ln in (ROOT / "examples" / "README.md").read_text().splitlines()
       if "rubric-repair" in ln]
check(len(row) >= 1, "examples/README.md map row exists")
tour = (ROOT / "references" / "example-tour.md").read_text()
check("rubric-repair" in tour and "disagree" in tour.lower(),
      "references/example-tour.md carries the tour entry with the STOP rule")

# capability-class law, PINNED (blind-council precedent): on a clean seat the
# re-score pin refuses BY NAME with the valid list — never a silent downgrade.
_td = tempfile.mkdtemp()
os.environ["WF_RUNS_ROOT"] = _td + "/runs"
os.environ["HERMES_HOME"] = _td
_spec = importlib.util.spec_from_file_location("_rr_door", str(ROOT / "__init__.py"))
_rr = importlib.util.module_from_spec(_spec)
with contextlib.redirect_stderr(io.StringIO()):
    _spec.loader.exec_module(_rr)
import wf_test_isolation
wf_test_isolation.install(_rr)
with contextlib.redirect_stderr(io.StringIO()):
    _v = json.loads(_rr.handle({"action": "validate", "graph": g}))
check(_v.get("ok") is False and "council_a" in json.dumps(_v),
      "clean seat: unbound capability class refuses BY NAME with the valid list",
      json.dumps(_v)[:160])

print(f"test_examples_hw_gft: {ok} checks PASS")
