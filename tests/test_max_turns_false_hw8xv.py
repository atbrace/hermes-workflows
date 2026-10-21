#!/usr/bin/env python3
"""hw-8xv: `max_turns: false` is an author-declared no-cap.

The runner spawns --max-turns only on truthiness, so a declared false was
already a working no-cap at spawn time; only the two numeric-bound validator
checks (node loop and defaults block) rejected it as a non-number. They admit
False now; every other bool, zero, negative, and over-cap number keeps its
existing rejection, and a declared false survives apply_graph_defaults
untouched (no preset or defaults fill over a declared key).
"""
import sys
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUILD))
import wfcommon  # noqa: E402

NODE = {"id": "a", "type": "agent", "goal": "g"}


def V(node):
    return wfcommon.validate_graph_errors([dict(NODE, **node)])


class MaxTurnsFalse(unittest.TestCase):
    def test_node_false_accepted(self):
        self.assertEqual(V({"max_turns": False}), [])

    def test_defaults_false_accepted(self):
        self.assertEqual(wfcommon._defaults_errors({"max_turns": False}), [])

    def test_true_still_rejected(self):
        for errs in (V({"max_turns": True}),
                     wfcommon._defaults_errors({"max_turns": True})):
            self.assertTrue(any(e["field"].endswith("max_turns") for e in errs), errs)

    def test_numbers_still_enforced(self):
        for bad in (0, -1, 201):
            self.assertTrue(V({"max_turns": bad}), bad)
        self.assertEqual(V({"max_turns": 100}), [])

    def test_timeout_false_still_rejected(self):
        # only max_turns has a no-cap meaning; timeout false stays a type error.
        self.assertTrue(V({"timeout": False}))
        self.assertTrue(wfcommon._defaults_errors({"timeout": False}))

    def test_declared_false_survives_defaults_merge(self):
        # per-node declared false is not overwritten by shape preset or defaults
        g = {"defaults": {"max_turns": 50},
             "nodes": [dict(NODE, max_turns=False, shape="recon")]}
        out = wfcommon.apply_graph_defaults(g)["nodes"][0]
        self.assertIs(out["max_turns"], False)
        # a defaults-level false fills a node that declares nothing
        g2 = {"defaults": {"max_turns": False}, "nodes": [dict(NODE)]}
        self.assertIs(wfcommon.apply_graph_defaults(g2)["nodes"][0]["max_turns"], False)


if __name__ == "__main__":
    unittest.main()
