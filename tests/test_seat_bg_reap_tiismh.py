#!/usr/bin/env python3
"""sys-tiismh done-check: a workflow seat reaps its background children AT the final answer.

Incident (2026-10-28, TW=2): lane seats that had already answered were re-opened by
notify_on_complete completion notices — the core one-shot exit linger runs
continue_quiet_notify_completions AFTER the answer and turns completions into
follow-up turns (duplicate receipts, dead turns, re-drives).

The fix is a pair: (1) the carrier stamps HERMES_WF_SEAT_BG_REAP=1 into every seat's
launch env (scoped to the `--source workflow` seat spawn, so the Bot Mode non-seat
linger #90879 is untouched); (2) the plugin's on_session_end observer (seat_bg_reap.py)
kills the seat's own background children with consume_output=True at turn end, so the
quiet drain loop finds nothing owned and the answer is terminal.

Assertions mirror the bead's acceptance:
  (a) the child process is gone after the answer;
  (b) no post-answer notice turn appears for the seat session (the completion is
      consumed — drain_notifications skips it, which is the ONLY way a completion
      becomes a follow-up turn on the quiet path).

Style (repo convention): stdlib-only; core-dependent assertions SKIP when hermes is
not importable (the carrier-side assertions always run).
"""
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, "/opt/hermes")
try:
    import tools.process_registry as pr_mod  # core registry (pip-installed hermes)
    HAVE_CORE = True
except Exception:
    pr_mod = None
    HAVE_CORE = False


def _load_reap_module():
    spec = importlib.util.spec_from_file_location(
        "_test_seat_bg_reap", ROOT / "seat_bg_reap.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_carrier_stamps_reap_env_on_seat_launch():
    """(1) The seat spawn env carries the reap flag, and delegation keeps it."""
    src = (ROOT / "wf.py").read_text(encoding="utf-8")
    anchor = src.index("HERMES_QUIET_TURN_REPORT_FILE=str(report_path)")
    env_block = src[anchor:anchor + 1600]
    assert "HERMES_WF_SEAT_BG_REAP" in env_block, (
        "carrier does not stamp the seat-reap flag into the seat launch env")
    # The flag must survive the routed (-p) env filter, which keeps only the
    # keep-set plus LC_* / HERMES_WF_* prefixes.
    assert 'k.startswith("HERMES_WF_")' in src, "routed env filter no longer keeps HERMES_WF_*"


def test_plugin_surface_registers_the_reaper():
    """(2) The reaper is on the hook surface (allow-list-gated loop registers it)."""
    src = (ROOT / "__init__.py").read_text(encoding="utf-8")
    surface = src[src.index("def _hook_surface()"):src.index("_CARD_HOOKS = (")]
    assert "_seat_bg_reap.reap" in surface, "reaper is not on _hook_surface()"
    assert "_seat_bg_reap = importlib.util.module_from_spec" in src, "seat_bg_reap.py not loaded"
    mod = _load_reap_module()
    assert mod.ENV == "HERMES_WF_SEAT_BG_REAP" and mod.SOURCE == "seat_final_answer"


def test_reap_is_gated_on_the_carrier_env(monkeypatch):
    """Off for every non-seat session: only the carrier's stamped env arms the reap."""
    mod = _load_reap_module()
    for off in (None, "0", ""):
        if off is None:
            monkeypatch.delenv(mod.ENV, raising=False)
        else:
            monkeypatch.setenv(mod.ENV, off)
        assert mod.reap(session_id="s", task_id="t") is None  # no-op, never raises


@pytest.mark.skipif(not HAVE_CORE, reason="hermes core not importable")
def test_child_gone_after_answer_and_no_notice_turn(tmp_path, monkeypatch):
    """(a)+(b) against the REAL registry: kill_all at the answer reaps the live child,
    and its completion is consumed — so the quiet drain loop gets no follow-up text."""
    mod = _load_reap_module()
    pr = pr_mod.process_registry
    # Isolate the singleton's durable side effects into the tmp hermes home.
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    monkeypatch.setattr(pr_mod, "CHECKPOINT_PATH", tmp_path / "processes.json")
    monkeypatch.setattr(pr_mod, "save_completed_result", lambda session: None)
    monkeypatch.setenv(mod.ENV, "1")

    child = subprocess.Popen(["sleep", "300"])
    task = "tiismh-seat-task"
    sess = pr_mod.ProcessSession(
        id="proc_tiismhtest0", command="sleep 300", task_id=task,
        cwd=str(tmp_path), started_at=time.time(),
        pid=child.pid, process=child, notify_on_complete=True)
    with pr._lock:
        pr._running[sess.id] = sess
    try:
        mod.reap(session_id="seat-session", task_id=task)
        # (a) the child is gone after the answer (SIGTERM, waiter reaps the zombie).
        assert child.wait(timeout=5) in (-15, -9, 143, 137)
        assert sess.exited and sess.termination_source == mod.SOURCE
        # (b) the completion is consumed: the quiet loop's drain skips it, so no
        # follow-up turn can re-open the seat.
        assert pr._drain_should_skip(sess.id) is True
        assert pr.drain_notifications(session_key=sess.session_key) == []
        # The post-answer linger finds nothing pending and returns immediately.
        assert sess._completion_event.wait(timeout=5)
        assert pr.wait_for_pending_completions(None, timeout=1)["waited"] == []
    finally:
        with pr._lock:
            pr._running.pop(sess.id, None)
            pr._finished.pop(sess.id, None)
            pr._completion_consumed.discard(sess.id)
        if child.poll() is None:
            child.kill()
            child.wait(timeout=5)


@pytest.mark.skipif(not HAVE_CORE, reason="hermes core not importable")
def test_task_scoped_reap_spares_a_foreign_task(tmp_path, monkeypatch):
    """The reap is task-scoped: a subagent turn's on_session_end (different task_id)
    must not cut the parent seat's mid-turn background suite short."""
    mod = _load_reap_module()
    pr = pr_mod.process_registry
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    monkeypatch.setattr(pr_mod, "CHECKPOINT_PATH", tmp_path / "processes.json")
    monkeypatch.setattr(pr_mod, "save_completed_result", lambda session: None)
    monkeypatch.setenv(mod.ENV, "1")

    child = subprocess.Popen(["sleep", "300"])
    sess = pr_mod.ProcessSession(
        id="proc_tiismhtest1", command="sleep 300", task_id="sa-other",
        cwd=str(tmp_path), started_at=time.time(),
        pid=child.pid, process=child, notify_on_complete=True)
    with pr._lock:
        pr._running[sess.id] = sess
    try:
        mod.reap(session_id="seat-session", task_id="tiismh-seat-task")
        assert child.poll() is None, "foreign-task child must survive the seat's reap"
    finally:
        with pr._lock:
            pr._running.pop(sess.id, None)
            pr._finished.pop(sess.id, None)
        child.kill()
        child.wait(timeout=5)


if __name__ == "__main__":  # script style, matching the repo convention
    # This file is pytest-shaped (def test_*), so under the merge-gate conftest a
    # bare relaunch would re-collect IT as a ScriptItem and re-run this block —
    # infinite ping-pong into the 90s wall. WF_PYTEST_NATIVE=1 makes the inner
    # run collect the test functions in-process (conftest's native escape hatch).
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-q"],
                             env=dict(os.environ, WF_PYTEST_NATIVE="1")))
