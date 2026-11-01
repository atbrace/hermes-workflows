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
      becomes a follow-up turn on the quiet path);
  (c) the reap is task-scoped: a foreign task_id (a subagent turn's on_session_end)
      must not cut the parent seat's mid-turn background suite short.

Style (repo convention): stdlib-only plain script; core-dependent assertions SKIP
when hermes is not importable (the carrier-side assertions always run).
Run:  python3 tests/test_seat_bg_reap_tiismh.py   (from the repo root)
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, "/opt/hermes")
try:
    import tools.process_registry as pr_mod  # core registry (pip-installed hermes)
    HAVE_CORE = True
except Exception:
    pr_mod = None
    HAVE_CORE = False

checks = 0
failures = 0
skips = 0


def check(name, ok, detail=""):
    global checks, failures
    checks += 1
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))
    failures += 0 if ok else 1


def skip(name, reason):
    global skips
    skips += 1
    print(f"SKIP {name} — {reason}")


def _load_reap_module():
    spec = importlib.util.spec_from_file_location(
        "_test_seat_bg_reap", ROOT / "seat_bg_reap.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _env(values):
    """Set/remove env entries (value None removes); returns the prior state."""
    prior = {}
    for k, v in values.items():
        prior[k] = os.environ.get(k)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    return prior


def _env_restore(prior):
    for k, v in prior.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def leg_carrier():
    """(1) The seat spawn env carries the reap flag, and delegation keeps it."""
    src = (ROOT / "wf.py").read_text(encoding="utf-8")
    anchor = src.index("HERMES_QUIET_TURN_REPORT_FILE=str(report_path)")
    env_block = src[anchor:anchor + 1600]
    check("(1) carrier stamps HERMES_WF_SEAT_BG_REAP into the seat launch env",
          "HERMES_WF_SEAT_BG_REAP" in env_block,
          "carrier does not stamp the seat-reap flag into the seat launch env")
    # The flag must survive the routed (-p) env filter, which keeps only the
    # keep-set plus LC_* / HERMES_WF_* prefixes.
    check("(1) routed env filter still keeps HERMES_WF_*",
          'k.startswith("HERMES_WF_")' in src,
          "routed env filter no longer keeps HERMES_WF_*")


def leg_plugin_surface():
    """(2) The reaper is on the hook surface (allow-list-gated loop registers it)."""
    src = (ROOT / "__init__.py").read_text(encoding="utf-8")
    surface = src[src.index("def _hook_surface()"):src.index("_CARD_HOOKS = (")]
    check("(2) reaper is on _hook_surface()", "_seat_bg_reap.reap" in surface,
          "reaper is not on _hook_surface()")
    check("(2) seat_bg_reap.py is loaded by the plugin",
          "_seat_bg_reap = importlib.util.module_from_spec" in src,
          "seat_bg_reap.py not loaded")
    mod = _load_reap_module()
    check("(2) reaper pins ENV/SOURCE constants",
          mod.ENV == "HERMES_WF_SEAT_BG_REAP" and mod.SOURCE == "seat_final_answer")


def leg_env_gate():
    """Off for every non-seat session: only the carrier's stamped env arms the reap."""
    mod = _load_reap_module()
    ok = True
    for off in (None, "0", ""):
        prior = _env({mod.ENV: off})
        try:
            ok = ok and mod.reap(session_id="s", task_id="t") is None  # no-op, never raises
        except Exception:
            ok = False
            _env_restore(prior)
            break
        _env_restore(prior)
    check("(3) reap is a no-op for unset/0/\"\" env, never raises", ok)


def _registry_leg(name, sess_id, reap_task, sess_task, expect_dead):
    """Shared driver for the two real-registry legs (child + singleton cleanup guaranteed)."""
    mod = _load_reap_module()
    pr = pr_mod.process_registry
    with tempfile.TemporaryDirectory() as tmp:
        # Isolate the singleton's durable side effects into the tmp hermes home.
        prior = _env({"HERMES_HOME": tmp, mod.ENV: "1"})
        prior_ck = pr_mod.CHECKPOINT_PATH
        prior_save = pr_mod.save_completed_result
        pr_mod.CHECKPOINT_PATH = Path(tmp) / "processes.json"
        pr_mod.save_completed_result = lambda session: None
        child = subprocess.Popen(["sleep", "300"])
        sess = pr_mod.ProcessSession(
            id=sess_id, command="sleep 300", task_id=sess_task,
            cwd=tmp, started_at=time.time(),
            pid=child.pid, process=child, notify_on_complete=True)
        try:
            with pr._lock:
                pr._running[sess.id] = sess
            mod.reap(session_id="seat-session", task_id=reap_task)
            if expect_dead:
                # (a) the child is gone after the answer (SIGTERM, waiter reaps the zombie).
                check(f"{name} (a) child gone at the answer",
                      child.wait(timeout=5) in (-15, -9, 143, 137))
                check(f"{name} termination_source is the reap",
                      bool(sess.exited and sess.termination_source == mod.SOURCE))
                # (b) the completion is consumed: the quiet loop's drain skips it, so no
                # follow-up turn can re-open the seat.
                check(f"{name} (b) drain skips the consumed completion",
                      pr._drain_should_skip(sess.id) is True
                      and pr.drain_notifications(session_key=sess.session_key) == [])
                # The post-answer linger finds nothing pending and returns immediately.
                check(f"{name} (b) linger waits on nothing",
                      sess._completion_event.wait(timeout=5)
                      and pr.wait_for_pending_completions(None, timeout=1)["waited"] == [])
            else:
                check(f"{name} (c) foreign-task child survives the seat's reap",
                      child.poll() is None,
                      "foreign-task child must survive the seat's reap")
        finally:
            with pr._lock:
                pr._running.pop(sess.id, None)
                pr._finished.pop(sess.id, None)
                pr._completion_consumed.discard(sess.id)
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)
            pr_mod.CHECKPOINT_PATH = prior_ck
            pr_mod.save_completed_result = prior_save
            _env_restore(prior)


def main():
    leg_carrier()
    leg_plugin_surface()
    leg_env_gate()
    if HAVE_CORE:
        _registry_leg("(4) reap at the answer —", "proc_tiismhtest0",
                      "tiismh-seat-task", "tiismh-seat-task", expect_dead=True)
        _registry_leg("(5) task-scoped reap —", "proc_tiismhtest1",
                      "tiismh-seat-task", "sa-other", expect_dead=False)
    else:
        skip("(4) reap at the answer (real registry)", "hermes core not importable")
        skip("(5) task-scoped reap (real registry)", "hermes core not importable")
    print(f"DONE seat_bg_reap_tiismh — {checks - failures}/{checks}"
          + (f" ({skips} SKIP)" if skips else ""))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
