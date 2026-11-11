"""hw-bzl: the philosophy appendix ships in the pack and stays genericized.

Gap-grep from the bead wording: 'the ledger', numbers as shapes, husk/wedge
defined by their exact query, every law paired with a receipt the package
itself holds. Mechanics stay in the mechanics references.
"""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
doc = (root / "references" / "posture.md").read_text(encoding="utf-8")
assert len(doc.splitlines()) <= 30, f"appendix must stay <=30 lines, is {len(doc.splitlines())}"
low = doc.lower()
for word in ("the ledger", "husk", "wedge", "receipt", "shape"):
    assert word in low, f"gap-grep term missing: {word!r}"
assert not re.search(r"\bbds?\b", low), "appendix must say 'the ledger', never bd"
assert not re.search(r"\bbeads\b", low), "appendix must say 'the ledger', never beads"
assert "references/posture.md" in (root / "SKILL.md").read_text(), \
    "SKILL.md must point at the shipped appendix (docs/posture.md does not ride the ZIP pack)"
print("ALL PASS: posture appendix ships genericized (hw-bzl)")
