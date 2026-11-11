docs(gates): state the machine-gate exec facts — probe cwd/env, raw execve, inert hold keys

Three omissions in the Gates-and-branches surface (hw-xr1, council gap-grep
against shipped v1.4.7): a `wait.until_argv` probe runs with cwd = the run dir
with both run-identity env pins re-pinned to the owning run (PR#243) — the
probe may read the run dir; the probe exec is a raw execve with no tilde
expansion, so a `~` entrypoint passes the door's residency check (expanded for
validation only) and dies at exec, and a `~` script operand refuses at the door
— write absolute paths; and `hold_timeout`/`default_option` are inert on
machine wait gates — `default_option` refuses at the door, `hold_timeout` feeds
only the #475 hold-vs-wall admission, and the runtime ceiling is
`wait.timeout_s`. The retired "no run-dir exposure" tip stays retired.
Mirrored into SKILL.md and the door's `until_argv` description.

Tests: tests/test_docs_gate_exec_facts_xr1.py (red without the doc lines;
Pins the bead's own wording so the council's gap-grep turns non-empty).
