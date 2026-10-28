#!/usr/bin/env python3
"""sys-6uk25s: a launch against a lane whose incumbent run is blocked-by-failed
returns a terminal {blocked_by, reason} naming the failed node(s) and the
runner_exit verdict, and every identical re-invocation is refused via the
dedup marker — no silent new run (the 8x blind-retry burst, 2026-10-19).

Run: env -u WF_RUNS_ROOT -u HERMES_HOME python3 -m pytest tests/test_blocked_failfast_6uk25s.py -q
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wf_door_6uk25s", ROOT / "__init__.py")
door = importlib.util.module_from_spec(spec)
spec.loader.exec_module(door)
import wf_test_isolation
wf_test_isolation.install(door)

GRAPH = {"name": "failfast6uk25s", "nodes": [
    {"id": "seed", "type": "echo", "output": {"seed": 1}},
    {"id": "bad", "type": "agent", "goal": "FAILME please"},
    {"id": "join", "type": "echo", "after": ["seed", "bad"], "output": 2},
]}


class BlockedFailFast6uk25s(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="wf6uk25s-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "home").mkdir()
        self.runs = self.root / "runs"
        env = patch.dict(os.environ, {"WF_RUNS_ROOT": str(self.runs),
                                      "HERMES_HOME": str(self.root / "home"),
                                      "HERMES_WF_HERMES_BIN": str(ROOT / "tests" / "fake"),
                                      "FAKE_LOG": str(self.root / "fake.log")})
        env.start()
        self.addCleanup(env.stop)
        wf_test_isolation.install(door)  # settings.runs_root may outrank the env without this
        self.spawns = []
        spawn = patch.object(door, "_spawn_runner", side_effect=lambda r: self.spawns.append(r))
        spawn.start()
        self.addCleanup(spawn.stop)

    def _run_dirs(self):
        return sorted(p.name for p in self.runs.iterdir() if (p / "graph.json").exists())

    def test_blocked_lane_refuses_relaunch_with_attribution(self):
        key = "lane/failfast-6uk25s"
        first = door.act_run({"graph": GRAPH, "lane_key": key})
        self.assertIn("run_id", first)
        rid = first["run_id"]
        # Drive the REAL runner so the block state is the genuine one
        # (node recs + runner_exit.json), not a mock shape.
        run = subprocess.run([sys.executable, str(ROOT / "wf.py"), "run", rid],
                             env=os.environ.copy(), capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        lane_entry = json.loads(door._lane_paths(key)[0].read_text())
        self.assertEqual(lane_entry["run_id"], rid)
        st = door._lane_state(key, lane_entry)
        self.assertEqual(st["state"], "failed")
        self.assertEqual(st["failed_nodes"], ["bad"])
        self.assertFalse(st["unfinished"])

        # half 1: the relaunch is a terminal refusal naming the block.
        relaunch = door.act_run({"graph": GRAPH, "lane_key": key})
        self.assertIn("error", relaunch)
        self.assertIn("bad", relaunch["error"])
        self.assertTrue(relaunch["deduped"])
        self.assertEqual(relaunch["run_id"], rid)
        self.assertEqual(relaunch["reason"], "blocked by failed bad")
        self.assertIn("bad: failed", relaunch["blocked_by"])
        self.assertEqual(len(self.spawns), 1)  # only the original launch

        # half 2: a second identical invocation rides the same marker —
        # no silent new run, the lane entry never moves.
        second = door.act_run({"graph": GRAPH, "lane_key": key})
        self.assertEqual(second, relaunch)
        self.assertEqual(self._run_dirs(), [rid])
        self.assertEqual(json.loads(door._lane_paths(key)[0].read_text())["run_id"], rid)
        self.assertEqual(len(self.spawns), 1)

    def test_done_lane_still_relaunches_fresh(self):
        # The guard is 'failed' only: a done incumbent keeps re-run semantics.
        key = "lane/failfast-6uk25s-done"
        first = door.act_run({"graph": GRAPH, "lane_key": key})
        rid = first["run_id"]
        with patch.object(door, "run_state", return_value={"status": "done"}):
            again = door.act_run({"graph": GRAPH, "lane_key": key})
        self.assertNotEqual(again["run_id"], rid)
        self.assertNotIn("deduped", again)
        self.assertEqual(len(self.spawns), 2)


if __name__ == "__main__":
    unittest.main()
