"""Dispatch caps doctrine doc-pins (hw-sp9): the council's gap-grep must go
non-empty in the shipped tree. Stdlib-only; exit 0 = green (repo test law)."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
playbook = (root / "references" / "operator-playbook.md").read_text(encoding="utf-8")
operations = (root / "references" / "operations.md").read_text(encoding="utf-8")

# The bead's own gap-grep tokens (bead hw-sp9 acceptance), case-insensitive.
shipped = (playbook + "\n" + operations).lower()
for token in ("cap is a meter", "governor", "per-subject interval", "per-tick", "live-laps"):
    assert token in shipped, f"gap-grep token missing from shipped docs: {token!r}"

# The doctrine itself lives in the operator playbook, named as a doctrine.
pb = playbook.lower()
assert "dispatch caps doctrine" in pb, "doctrine must be named in operator-playbook.md"
for phrase in ("guards mechanical", "judgment only in graph seats", "lanes are terminal"):
    assert phrase in pb, f"doctrine phrase missing from operator-playbook.md: {phrase!r}"

# operations.md points at the doctrine from the cap mechanics it documents.
ops = operations.lower()
assert "cap is a meter" in ops and "operator-playbook" in ops, \
    "operations.md must carry the meter-not-governor pointer to operator-playbook.md"

print("PASS: dispatch caps doctrine documented (hw-sp9)")
