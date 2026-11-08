import sys, tempfile, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import wfcommon

# sys-wt3cck (hw-7bt): completion honesty. The honest fold lets a node that DIED
# read `done` — either the validate policy laundered a `partial` to done (the
# `clamped` stamp names the verdict it replaced) or an efp-valid `failed` carries
# a harvest answer that re-validates. Both stayed out of failed_nodes and let
# completed=True mask the death (live mask: run 20261103-171453-b2p-sysizvfq9,
# node push-pr). Fix law: run_state derives completed_over_dead_node from the
# SAME fold through the ONE predicate _died_but_harvested; a non-empty list
# forces completed=False (fail-closed: it can refuse green, never grant it).
# The key rides exactly where `completed` rides (est-3acn D7 verbatim-key-set law).

SCHEMA = {"type": "object"}

def _fixture(root):
    run = root / "run"; (run / "nodes").mkdir(parents=True)
    graph = {"id": "g", "title": "t", "defaults": {"seat": "s"}, "nodes": [
        {"id": "a", "task": "t", "seat": "s", "type": "echo", "output": {"ok": True}},
        {"id": "b", "task": "t", "seat": "s", "schema": SCHEMA,
         "depends_on": ["a"], "type": "echo", "output": {"ok": True}}]}
    (run / "graph.json").write_text(json.dumps(graph))
    (run / "run.json").write_text(json.dumps({"id": "g", "status": "done", "graph": graph}))
    (run / "runner_exit.json").write_text(json.dumps(
        {"reason": "done", "at": "x", "graph_fingerprint":
         wfcommon.graph_fingerprint(graph), "fp_rule_version":
         wfcommon.FP_RULE_VERSION}))
    byid = {n["id"]: n for n in graph["nodes"]}
    for nid in ("a", "b"):
        (run / "nodes" / f"{nid}.json").write_text(json.dumps(
            {"status": "done", "attempt": 1, "output": {"ok": True},
             "efp": wfcommon.efp(byid, byid[nid]),
             "fp_rule_version": wfcommon.FP_RULE_VERSION}))
    return run, byid

def _stamp(run, byid, rec):
    (run / "nodes" / "b.json").write_text(json.dumps(rec))

def test_clamped_death_refuses_green():
    # S1: the laundered arm — a record carrying the validate clamp reads done,
    # is not a failed_node, yet names the death and refuses completed.
    with tempfile.TemporaryDirectory() as td:
        run, byid = _fixture(pathlib.Path(td))
        _stamp(run, byid, {"status": "done", "attempt": 1, "output": {"ok": True},
                "error": "turn cap", "error_class": "cap_exhausted",
                "harvest": {"declared_status": "done"},
                "clamped": {"policy": "validate", "from_status": "partial",
                            "error_class": "cap_exhausted"},
                "efp": wfcommon.efp(byid, byid["b"]),
                "fp_rule_version": wfcommon.FP_RULE_VERSION})
        out = wfcommon.run_state(run)
        assert out["completed"] is False, out["completed"]
        assert out["completed_over_dead_node"] == ["b"], out
        assert out["failed_nodes"] == []

def test_honest_fold_death_refuses_green():
    # S2: the jam-aus arm — efp-valid `failed` whose harvest answer validates
    # folds to done for consumption yet must refuse run-level green.
    with tempfile.TemporaryDirectory() as td:
        run, byid = _fixture(pathlib.Path(td))
        _stamp(run, byid, {"status": "failed", "attempt": 1, "error": "boom",
                "error_class": "timeout",
                "harvest": {"declared_status": "done"}, "output": {"ok": True},
                "efp": wfcommon.efp(byid, byid["b"]),
                "fp_rule_version": wfcommon.FP_RULE_VERSION})
        out = wfcommon.run_state(run)
        assert out["completed"] is False, out["completed"]
        assert out["completed_over_dead_node"] == ["b"], out
        assert out["failed_nodes"] == []   # the fold still reads it done for edges

def test_clean_run_still_green_and_honest_absence():
    # S3: a clean terminal run keeps completed=True with the honest-empty list;
    # S4: no verdict stamped -> neither derived key rides (D7 verbatim law).
    with tempfile.TemporaryDirectory() as td:
        run, byid = _fixture(pathlib.Path(td))
        out = wfcommon.run_state(run)
        assert out["completed"] is True and out["completed_over_dead_node"] == []
        (run / "runner_exit.json").unlink()
        out = wfcommon.run_state(run)
        assert "completed" not in out and "completed_over_dead_node" not in out

def test_predicate_is_the_one_site():
    # S5: predicate units — a plain done is not a death; a failed WITHOUT a
    # validating harvest is not harvested (it rides failed_nodes instead).
    n = {"id": "b", "schema": SCHEMA}
    assert wfcommon._died_but_harvested(n, {"status": "done", "output": {}}) is False
    assert wfcommon._died_but_harvested(n, {"status": "done", "output": {},
                                            "clamped": {"policy": "validate"}}) is True
    assert wfcommon._died_but_harvested(n, {"status": "failed",
                                            "harvest": {"declared_status": "BLOCKED"},
                                            "output": {"ok": True}}) is False
    assert wfcommon._died_but_harvested(n, None) is False

if __name__ == "__main__":
    test_clamped_death_refuses_green()
    test_honest_fold_death_refuses_green()
    test_clean_run_still_green_and_honest_absence()
    test_predicate_is_the_one_site()
    print("sys-wt3cck: dead-node completion honesty green (4 checks)")
