#!/usr/bin/env python3
"""sys-tiismh: the seat background reaper — a workflow seat's answer is terminal.

Incident (2026-10-28): the core one-shot exit linger runs
wait_for_pending_completions BEFORE agent.close()'s kill_all, so a
notify_on_complete child's completion notice opened a post-answer turn on a
lane seat — duplicate receipts, dead turns, carrier re-drives.

The pair: wf.py stamps HERMES_WF_SEAT_BG_REAP=1 into the seat launch env
(scoped to the `--source workflow` seat spawn; the non-seat one-shot linger
#90879 is untouched), and this on_session_end observer kills the seat's own
task-scoped children with consume_output=True — the completion counts as
consumed, so the quiet drain loop (_drain_should_skip / drain_notifications)
finds nothing owned and the answer stays final.

Scope law:
  - Armed ONLY by the carrier env stamp; unset/0/"" is a no-op (gateway, door,
    interactive and Bot Mode sessions never see it, and a reap never raises).
  - Task-scoped: a subagent turn's on_session_end (different task_id) must not
    cut the parent seat's mid-turn background suite short.
  - Interrupted/failed turns skip the reap: core's own lifecycle kill
    (agent_close) still runs there and must not lose its completion notice.
  - persist_on_release children ARE killed: this source is not in
    _LIFECYCLE_KILL_SOURCES, so a seat deliberately leaves no surviving
    background daemons (no-daemon doctrine — the seat's answer is its end).
Fail-open everywhere: the reaper absent or broken must leave the plugin intact.
"""
import os

ENV = "HERMES_WF_SEAT_BG_REAP"
SOURCE = "seat_final_answer"


def reap(session_id=None, task_id=None, completed=None, failed=None,
         interrupted=None, **_):
    """on_session_end observer: reap this task's background children at the answer."""
    try:
        if os.environ.get(ENV, "") in ("", "0"):
            return None
        if failed or interrupted:
            return None
        from tools.process_registry import process_registry
        process_registry.kill_all(task_id, source=SOURCE, consume_output=True)
    except Exception:
        pass
    return None
