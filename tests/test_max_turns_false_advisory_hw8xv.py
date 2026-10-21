#!/usr/bin/env python3
"""hw-8xv review follow-up: a declared max_turns false must not warn on the
door's validate path.

The shape-p95 advisory compares the resolved cap with `<` against the preset
budget; False compares as 0, so without the guard every graph legitimately
declaring max_turns false emits a bogus 'below p95 budget' warning that
contradicts the admitted feature. Pin: node-level and defaults-level false
validate ok with NO max_turns warning; the numeric advisory still fires.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

NODE = {"id": "lane", "type": "agent", "goal": "Inspect the lane"}


class MaxTurnsFalseNoAdvisory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="wf-8xv-advisory-")
        cls.home = Path(cls.tmp.name)
        cls.env = patch.dict(os.environ, {
            "HERMES_HOME": str(cls.home),
            "WF_RUNS_ROOT": str(cls.home / "runs"),
            "HERMES_WF_HERMES_BIN": str(ROOT / "tests" / "fake"),
        })
        cls.env.start()
        spec = importlib.util.spec_from_file_location("hw8xv_advisory_door", ROOT / "__init__.py")
        assert spec is not None and spec.loader is not None
        cls.door = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.door)
        import wf_test_isolation as _iso
        _iso.install(cls.door)

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        cls.tmp.cleanup()

    def validate(self, graph):
        return json.loads(self.door.handle({"action": "validate", "graph": graph}))

    def max_turns_warnings(self, result):
        return [w for w in result.get("warnings", [])
                if isinstance(w, dict) and w.get("field") == "max_turns"]

    def test_node_level_false_no_advisory(self):
        r = self.validate({"name": "8xv", "nodes": [dict(NODE, max_turns=False)]})
        self.assertIs(r.get("ok"), True, r)
        self.assertEqual(self.max_turns_warnings(r), [], r)

    def test_defaults_level_false_no_advisory(self):
        r = self.validate({"name": "8xv", "defaults": {"max_turns": False},
                           "nodes": [dict(NODE)]})
        self.assertIs(r.get("ok"), True, r)
        self.assertEqual(self.max_turns_warnings(r), [], r)

    def test_numeric_advisory_still_fires(self):
        budget = self.door._common.SHAPE_PRESETS["recon"]["max_turns"]
        r = self.validate({"name": "8xv", "nodes": [dict(NODE, shape="recon",
                                                         max_turns=budget - 1)]})
        self.assertIs(r.get("ok"), True, r)
        self.assertEqual(len(self.max_turns_warnings(r)), 1, r)


if __name__ == "__main__":
    unittest.main()
