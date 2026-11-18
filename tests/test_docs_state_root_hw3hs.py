#!/usr/bin/env python3
"""hw-3hs: the per-key state-root / handoff-file law must be visible in the
shipped docs, not only inside the example inline-python blobs.

Symptom (bead hw-3hs): the law behind MW_STATE_ROOT / IR_STATE_ROOT — parallel
lanes must never share one global scratch (a six-false-clears field receipt);
path-binding belongs on the shelf launch — lived only in the machine-watch and
incident-response probe blobs, so the council's gap-grep over .md/.json found
zero hits. Acceptance: a grep from the bead's own wording goes non-empty on a
shipped doc. This pin runs exactly that grep; it fails red on the tree the
bead was filed against.

Run: python3 tests/test_docs_state_root_hw3hs.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The bead's own wording; each must be greppable in a shipped doc.
PHRASES = (
    "state root",        # deterministic per-key state roots
    "global scratch",    # parallel lanes must never share one
    "path-binding",      # belongs on the shelf launch
    "shelf launch",
    "handoff-file law",
)
DOC_FILES = (
    "references/example-tour.md",
    "examples/README.md",
)

fails = total = 0

def check(name, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL ") + name + (f" :: {detail[:200]}" if detail and not cond else ""),
          flush=True)
    if not cond:
        fails += 1

text = {f: (ROOT / f).read_text(encoding="utf-8").lower() for f in DOC_FILES}
for phrase in PHRASES:
    hits = [f for f, t in text.items() if phrase in t]
    check(f"gap-grep non-empty: {phrase!r}", bool(hits), "no shipped doc carries the phrase")

print(f"{'ALL PASS' if fails == 0 else 'FAILED'}: state-root law visible in docs ({total - fails}/{total})")
sys.exit(1 if fails else 0)
