#!/usr/bin/env python3
"""hw-xr1: the shipped docs must state the machine-gate exec facts.

Gap (council-verified against shipped v1.4.7, three separate omissions in the
Gates-and-branches surface):

1. A `wait.until_argv` probe runs with cwd = the run dir and both run-identity
   env pins re-pinned to the owning run (wf.py `_aux_run` call, PR#243), yet
   the docs never said so — authors kept assuming a probe sees a neutral cwd.
2. The probe exec is a raw execve with NO tilde expansion: the door
   (`wfcommon.entrypoint_residency`) expands `~` for the residency check only,
   so a `~` ENTRYPOINT passes the door and dies at exec, and a `~` script
   OPERAND refuses at the door (operands must be absolute before expansion).
3. `hold_timeout`/`default_option` are inert on machine wait gates at runtime:
   `default_option` on a wait gate refuses at the door; `hold_timeout` on one
   feeds only the #475 hold-vs-wall admission; the wait gate's runtime ceiling
   is `wait.timeout_s`.

The phrases pinned below are the bead's own wording so the council's gap-grep
turns non-empty at next release. Run: python3 tests/test_docs_gate_exec_facts_xr1.py
"""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
grammar = (root / "references" / "grammar.md").read_text(encoding="utf-8")
skill = (root / "SKILL.md").read_text(encoding="utf-8")
door = (root / "__init__.py").read_text(encoding="utf-8")

failures = []


def pin(label, cond):
    print(("PASS" if cond else "FAIL") + ": " + label)
    if not cond:
        failures.append(label)


# grammar.md, Gates and branches: the three facts, in the bead's own words.
pin("grammar: probe cwd = the run dir", "cwd = the run dir" in grammar)
pin("grammar: run-identity env re-pin names both pins",
    "HERMES_WF_RUN_DIR" in grammar and "HERMES_WF_RUN_ID" in grammar)
pin("grammar: raw execve, no tilde expansion", "no tilde expansion" in grammar)
pin("grammar: ~ entrypoint passes door, dies at exec",
    "dies at exec" in grammar and "refuses at the door" in grammar)
pin("grammar: hold_timeout/default_option inert on wait gates",
    "inert on wait gates" in grammar)
pin("grammar: wait gate ceiling is wait.timeout_s", "timeout_s" in grammar)

# Mirror clauses ride the two other surfaces authors actually read.
pin("SKILL.md mirrors the wait-gate inertness", "inert on wait gates" in skill)
pin("door until_argv description mirrors cwd + tilde law",
    "cwd = the run dir" in door and "no tilde expansion" in door)

# Anti-rot: the retired tip must not come back.
pin("retired tip stays retired", "no run-dir exposure" not in (grammar + skill).lower())

sys.exit(1 if failures else 0)
