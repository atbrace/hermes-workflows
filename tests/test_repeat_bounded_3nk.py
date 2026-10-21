#!/usr/bin/env python3
"""Bounded self-repeat on agent nodes: `repeat: {max, until?}`.

Pins the four halves of the contract:
  (1) admission — the validator accepts the shape and refuses malformed bounds
      BY NAME (missing/out-of-range max, non-agent or fan-out carrier, an
      `until` head that is not the node's own output);
  (2) the shared repeat law wfcommon.repeat_status over a committed record:
      'again' (gate open, budget left) / 'closed' / 'exhausted';
  (3) the commit stamp — save_node counts generations durably on the record,
      an amend resets the count, and non-repeat records stay byte-identical;
  (4) runner end-to-end via a counting fake agent: bound enforcement (the
      run hard-fails typed `repeat_exhausted` at the cap), replay-skip (a
      resume of a closed run spawns nothing; a resume of an exhausted run
      spawns nothing), and the previous output rides the next prompt.

Standalone script (no pytest):
  env -u WF_RUNS_ROOT -u HERMES_HOME python3 tests/test_repeat_bounded_3nk.py
"""
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_3nk", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
sys.path.insert(0, str(ROOT))
import wfcommon
import wf
import wf_test_isolation


def _nodes(repeat_val, carrier_type="agent", extra=None):
    n = {"id": "draft", "type": carrier_type, "after": ["seed"]}
    if carrier_type == "agent":
        n["goal"] = "draft it"
    if repeat_val is not None:
        n["repeat"] = repeat_val
    nodes = [{"id": "seed", "type": "echo", "output": {"s": 1}}, n]
    return nodes + (extra or [])


def _defs(nodes):
    return [d for d in wfcommon.validate_graph_errors(nodes)
            if "repeat" in str(d.get("field", "")) or "repeat" in str(d.get("msg", ""))]


def _rs(node, status="done", output=None, it=1):
    rec = {"status": status, "output": output, "repeat_iter": it}
    return wfcommon.repeat_status(node, rec)


class Admission3nk(unittest.TestCase):
    def test_wellformed_accepted(self):
        self.assertEqual(_defs(_nodes({"max": 3})), [])
        self.assertEqual(_defs(_nodes({"max": 3, "until": "out.draft.v >= 2"})), [])
        self.assertEqual(_defs(_nodes({"max": 1, "until": "not out.draft.ok and out.draft.v > 1"})), [])

    def test_missing_max_refused(self):
        self.assertTrue(_defs(_nodes({"until": "out.draft.v >= 2"})))

    def test_max_bounds(self):
        for bad in (0, 9, "3", True, 2.5, None):
            self.assertTrue(_defs(_nodes({"max": bad})), f"value {bad!r} accepted")

    def test_unknown_subkey_refused(self):
        self.assertTrue(_defs(_nodes({"max": 2, "every_s": 5})))

    def test_non_agent_carrier_refused(self):
        self.assertTrue(_defs(_nodes({"max": 2}, carrier_type="gate")))

    def test_fanout_carrier_refused(self):
        nodes = _nodes({"max": 2})
        nodes[1]["fanout"] = {"items": ["a"]}
        self.assertTrue(_defs(nodes))

    def test_malformed_until_refused(self):
        self.assertTrue(_defs(_nodes({"max": 2, "until": "out.draft.v >"})))
        self.assertTrue(_defs(_nodes({"max": 2, "until": 7})))

    def test_until_head_must_be_self(self):
        # ancestor heads are refused: the exit gate reads ONLY this node's own
        # committed output (that is what keeps the replay law pure per-record).
        self.assertTrue(_defs(_nodes({"max": 2, "until": "out.seed.s >= 1"})))
        self.assertTrue(_defs(_nodes({"max": 2, "until": "out.ghost.v == 1"})))


class RepeatLaw3nk(unittest.TestCase):
    NODE = {"id": "d", "type": "agent", "goal": "g", "repeat": {"max": 3}}
    UNTIL = {"id": "d", "type": "agent", "goal": "g",
             "repeat": {"max": 3, "until": "out.d.v >= 2"}}

    def test_no_repeat_closed(self):
        self.assertEqual(wfcommon.repeat_status({"id": "d", "type": "agent"}, {"status": "done"}),
                         "closed")

    def test_non_done_closed(self):
        rec = {"status": "failed", "output": None, "repeat_iter": 1}
        self.assertEqual(wfcommon.repeat_status(self.NODE, rec), "closed")
        rec_p = {"status": "partial", "output": {}, "repeat_iter": 1}
        self.assertEqual(wfcommon.repeat_status(self.NODE, rec_p), "closed")

    def test_fixed_count_loop_closes_at_max(self):
        # no until: the bound IS the exit law — closes done at max, never exhausts
        self.assertEqual(_rs(self.NODE, it=1), "again")
        self.assertEqual(_rs(self.NODE, it=2), "again")
        self.assertEqual(_rs(self.NODE, it=3), "closed")

    def test_until_gates(self):
        self.assertEqual(_rs(self.UNTIL, output={"v": 1}, it=1), "again")
        self.assertEqual(_rs(self.UNTIL, output={"v": 2}, it=1), "closed")

    def test_until_exhausted(self):
        self.assertEqual(_rs(self.UNTIL, output={"v": 1}, it=3), "exhausted")

    def test_until_value_error_fails_closed_to_done(self):
        # None >= 2 is a TypeError: a broken predicate must never launder the
        # node into pending forever — the commit stands.
        self.assertEqual(_rs(self.UNTIL, output={"v": None}, it=1), "closed")

    def test_missing_stamp_acts_as_first_iteration(self):
        rec = {"status": "done", "output": {"v": 1}}
        self.assertEqual(wfcommon.repeat_status(self.UNTIL, rec), "again")


class Stamp3nk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="wf3nk-stamp-")
        self.addCleanup(self.tmp.cleanup)
        self.run = Path(self.tmp.name)

    def _node(self, goal="g"):
        return {"id": "draft", "type": "agent", "goal": goal, "repeat": {"max": 2}}

    def test_nonrepeat_record_untouched(self):
        n = {"id": "plain", "type": "agent", "goal": "g"}
        wf.save_node(self.run, n, {"plain": n}, {"status": "done", "output": {"v": 1}, "ms": 0})
        rec = json.loads((self.run / "nodes" / "plain.json").read_text())
        self.assertNotIn("repeat_iter", rec)

    def test_stamp_increments_and_resets(self):
        n = self._node()
        byid = {"draft": n}
        wf.save_node(self.run, n, byid, {"status": "done", "output": {"v": 1}, "ms": 0})
        self.assertEqual(json.loads((self.run / "nodes" / "draft.json").read_text())["repeat_iter"], 1)
        wf.save_node(self.run, n, byid, {"status": "done", "output": {"v": 2}, "ms": 0})
        self.assertEqual(json.loads((self.run / "nodes" / "draft.json").read_text())["repeat_iter"], 2)
        # a failed commit also counts the generation (a dead attempt burned tokens)
        wf.save_node(self.run, n, byid, {"status": "failed", "error": "x", "ms": 0})
        self.assertEqual(json.loads((self.run / "nodes" / "draft.json").read_text())["repeat_iter"], 3)
        # an amend (def change) resets the count — old generations are stale
        n2 = self._node(goal="amended")
        wf.save_node(self.run, n2, {"draft": n2}, {"status": "done", "output": {"v": 1}, "ms": 0})
        self.assertEqual(json.loads((self.run / "nodes" / "draft.json").read_text())["repeat_iter"], 1)

    def test_node_rec_flips_open_gate_to_pending(self):
        n = {"id": "draft", "type": "agent", "goal": "g",
             "repeat": {"max": 3, "until": "out.draft.v >= 2"}}
        byid = {"draft": n}
        # gate open at iter 1 of 3: the done commit is NOT current — re-drive
        wf.save_node(self.run, n, byid, {"status": "done", "output": {"v": 1}, "ms": 0})
        self.assertEqual(wfcommon.node_rec(self.run, n, byid)[0], "pending")
        # gate satisfied: the done commit stands (replay-skip)
        wf.save_node(self.run, n, byid, {"status": "done", "output": {"v": 2}, "ms": 0})
        self.assertEqual(wfcommon.node_rec(self.run, n, byid)[0], "done")
        # gate open AT the bound: node_rec still reads done — the runner's
        # exhaustion pass (not the read law) turns it typed-failed
        n3 = {"id": "draft", "type": "agent", "goal": "g",
              "repeat": {"max": 3, "until": "out.draft.v >= 2"}}
        wf.save_node(self.run, n3, {"draft": n3}, {"status": "done", "output": {"v": 1}, "ms": 0})
        wf.save_node(self.run, n3, {"draft": n3}, {"status": "done", "output": {"v": 1}, "ms": 0})
        wf.save_node(self.run, n3, {"draft": n3}, {"status": "done", "output": {"v": 1}, "ms": 0})
        self.assertEqual(wfcommon.node_rec(self.run, n3, {"draft": n3})[0], "done")


class Runner3nk(unittest.TestCase):
    """End-to-end through the door + runner subprocess with a counting fake."""

    STUB = ("#!/usr/bin/env python3\n"
            "import sys, os, json\n"
            "args = sys.argv[1:]\n"
            "q = open(args[args.index('--query-file') + 1]).read() if '--query-file' in args else sys.stdin.read()\n"
            "c = os.environ['REPEAT_COUNT_FILE']\n"
            "n = 0\n"
            "if os.path.exists(c):\n"
            "    n = int(open(c).read() or '0')\n"
            "open(c, 'w').write(str(n + 1))\n"
            "if os.environ.get('REPEAT_PROMPT_LOG'):\n"
            "    open(os.environ['REPEAT_PROMPT_LOG'], 'a').write('\\n=====PROMPT=====\\n' + q + '\\n')\n"
            "print('```json\\n' + json.dumps({'v': n + 1}) + '\\n```')\n")

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="wf3nk-runner-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.runs = self.root / "runs"
        self.stub = self.root / "fake-agent"
        self.stub.write_text(self.STUB)
        self.stub.chmod(self.stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        self.count_file = self.root / "spawn.count"
        self.prompt_log = self.root / "prompts.log"
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.runs),
                                      "HERMES_HOME": str(self.home),
                                      "HERMES_WF_HERMES_BIN": str(self.stub),
                                      "REPEAT_COUNT_FILE": str(self.count_file),
                                      "REPEAT_PROMPT_LOG": str(self.prompt_log)})
        env.start()
        self.addCleanup(env.stop)
        wf_test_isolation.install(door)
        spawn = patch.object(door, "_spawn_runner")
        spawn.start()
        self.addCleanup(spawn.stop)

    def _spawns(self):
        try:
            return int(self.count_file.read_text() or "0")
        except FileNotFoundError:
            return 0

    def _drive(self, run_id):
        return subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", run_id],
                              env=os.environ.copy(), capture_output=True, text=True, timeout=180)

    def _graph(self, until, max_iters):
        return {"name": "repeat3nk", "nodes": [
            {"id": "draft", "type": "agent", "goal": "draft the thing",
             "repeat": {"max": max_iters, "until": until}},
            {"id": "pub", "type": "echo", "after": ["draft"], "output": {"shipped": True}},
        ]}

    def test_until_closes_run_completes(self):
        started = door._create_run({"graph": self._graph("out.draft.v >= 3", 5)},
                                   self._graph("out.draft.v >= 3", 5), None, {}, {}, [],
                                   concurrency_meta={})
        run_id = started["run_id"]
        out = self._drive(run_id)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), f"WORKFLOW_DONE {run_id}")
        self.assertEqual(self._spawns(), 3)  # generations 1,2 open the gate; 3 closes it
        rec = json.loads((self.runs / run_id / "nodes" / "draft.json").read_text())
        self.assertEqual(rec["status"], "done")
        self.assertEqual(rec["repeat_iter"], 3)
        self.assertEqual(rec["output"], {"v": 3})
        # the previous output rode the NEXT prompt
        prompts = self.prompt_log.read_text().split("=====PROMPT=====")
        self.assertEqual(len(prompts), 4)  # header + 3 prompts
        self.assertNotIn("Repeat pass", prompts[1])
        self.assertIn("## Repeat pass 2", prompts[2])
        self.assertIn('"v": 1', prompts[2])
        self.assertIn("## Repeat pass 3", prompts[3])
        # replay-skip law: a resume of the closed run spawns NOTHING new
        out2 = self._drive(run_id)
        self.assertEqual(out2.returncode, 0, out2.stderr)
        self.assertEqual(self._spawns(), 3)

    def test_bound_enforced_typed_failure_and_replay(self):
        started = door._create_run({"graph": self._graph("out.draft.v >= 99", 2)},
                                   self._graph("out.draft.v >= 99", 2), None, {}, {}, [],
                                   concurrency_meta={})
        run_id = started["run_id"]
        out = self._drive(run_id)
        self.assertEqual(self._spawns(), 2)  # never a third spawn — the bound is law
        self.assertEqual(out.stdout.strip(), f"WORKFLOW_FAILED {run_id} (draft)")
        r = self.runs / run_id
        rec = json.loads((r / "nodes" / "draft.json").read_text())
        self.assertEqual(rec["status"], "failed")
        self.assertEqual(rec["error_class"], "repeat_exhausted")
        events = [json.loads(l) for l in (r / "events.jsonl").read_text().splitlines()]
        self.assertTrue([e for e in events if e.get("event") == "node.repeat_exhausted"
                         and e.get("node") == "draft" and e.get("iters") == 2])
        # resume replays the typed failure: zero new spawns, same verdict
        out2 = self._drive(run_id)
        self.assertEqual(self._spawns(), 2)
        self.assertEqual(out2.stdout.strip(), f"WORKFLOW_FAILED {run_id} (draft)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
