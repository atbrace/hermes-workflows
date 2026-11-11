#!/usr/bin/env python3
"""hw-tia: the external-pack adoption recipe is shipped in references/operations.md.

Born from the haus-estate consolidation run 20261111-162224-wof-study-council:
every gap below was grep-verified absent from v1.4.7, so the pin is wording-
anchored (the council's gap-grep must go non-empty). Plain stdlib, no door, no
engine import: this pins the DOC, mirroring how test_portable_32 pins the
portable.md digests. Red without the section; green with it.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = (ROOT / "references" / "operations.md").read_text(encoding="utf-8")

ok = 0
def check(cond, msg, detail=""):
    global ok
    assert cond, msg + (f"  << {detail}" if detail else "")
    ok += 1; print("PASS", msg)

# the section, sliced from its heading to the next heading of any level
m = re.search(r"^#{2,3} Adopting an external pack\s*$", TEXT, re.M)
check(m is not None, "operations.md carries the 'Adopting an external pack' heading")
assert m is not None
section = TEXT[m.end():]
nxt = re.search(r"^#{2,3} ", section, re.M)
section = section[: nxt.start()] if nxt else section

def has(*words):
    s = section.lower()
    return all(w.lower() in s for w in words)

check(has("manifest", "source_digest") and has("not", "verify"),
      "gap 1: manifest digests are not provenance.source_digest — verify before save")
check(has("source="),
      "gap 2: the recipe says to always pass source= on the import save")
check(has("graph_path") and has("absolute"),
      "gap 3: graph_path must be absolute")
check(has("argv") and has("owning machine"),
      "gap 4: baked estate entrypoints (argv residency) validate only on the owning machine")
check(has("no import verb") and has("save") and has("inspect"),
      "gap 5: there is no import verb — save IS the import, library name: is the inspect")

# the bead's own title wording must be greppable in the shipped tree
check(re.search(r"adopting an external pack", TEXT, re.I | re.M) is not None,
      "gap-grep: 'adopting an external pack' is non-empty in the shipped tree")

print(f"\nOK {ok} checks")
