docs(operator): state the dispatch caps doctrine — guards mechanical, caps are meters (hw-sp9)

The cap machinery was documented piecemeal (owner clamp in grammar.md, RunBudget
and pool caps in operations.md) but no shipped section stated the doctrine:
guards mechanical, judgment only in graph seats; caps are per-subject interval /
per-tick / live-laps numbers — the cap is a meter, never the governor's opinion;
lanes are terminal on the subjects their guards watch. Added to
references/operator-playbook.md beside the seat-cap admission bullets, with a
pointer from the operations.md RunBudget section.
Tests: tests/test_dispatch_caps_hw-sp9.py (RED at base: all gap-grep tokens
absent; green after).
