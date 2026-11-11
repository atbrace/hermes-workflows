#!/usr/bin/env python3
"""hw-3ft: the honest-partial recipe must live next to the close-out guidance.

Symptom (bead hw-3ft): when a late leg dies cap_exhausted, budgets.md — the
doc an author reaches — tells them to shrink work and write-first, then leaves
them with `blocked_by_partial_ancestor` descendants. The escape hatch
(`harvest_policy: "validate"` producer-side, `after_partial: true`
consumer-side) exists and is implemented, but only in references/grammar.md
and a buried SKILL.md bullet; the council's gap-grep over budgets.md came back
empty at v1.4.7. This test IS that gap-grep, plus the honesty pins: the doc
must name both release directions with the engine's real key spellings, in the
same section as the write-first/close-out guidance.

Run: python3 tests/test_docs_hw-3ft.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "references" / "budgets.md"
GRAMMAR = ROOT / "references" / "grammar.md"

fails = total = 0


def check(name, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL " + name) + (f" :: {detail[:300]}" if detail and not cond else ""),
          flush=True)
    if not cond:
        fails += 1


doc = DOC.read_text(encoding="utf-8")

# 1. THE GAP-GREP (the bead's own acceptance): non-empty at these tokens.
check("budgets.md names the honest-partial keys (council gap-grep non-empty)",
      re.search(r"after_partial|harvest_policy", doc) is not None,
      "no `after_partial` / `harvest_policy` token anywhere in budgets.md")

# 2. Both release directions: producer-side policy and consumer-side opt-in.
check("producer-side harvest_policy validate is named",
      re.search(r"harvest_policy[^\n]*validate", doc) is not None,
      "harvest_policy never tied to validate")
check("consumer-side after_partial true is named",
      re.search(r"after_partial[^\n]*true", doc, re.IGNORECASE) is not None,
      "after_partial never tied to true")

# 3. NEXT TO the close-out guidance: the recipe sits after the write-first
# paragraph in the same doc (the bead: "next to the close-out-hoist paragraph").
wf = doc.find("write-first")
first_key = min((doc.find(m) for m in ("harvest_policy", "after_partial") if doc.find(m) >= 0), default=-1)
check("the recipe sits after the write-first/close-out paragraph",
      wf >= 0 and first_key > wf,
      f"write-first at {wf}, first key mention at {first_key}")

# 4. Honesty pins: the doc uses the engine's real key spellings, the same
# tokens the grammar law carries (no paraphrase-only recipe).
grammar = GRAMMAR.read_text(encoding="utf-8")
check("keys match the sanctioned grammar.md spellings",
      all(t in doc and t in grammar for t in ("harvest_policy", "after_partial")),
      "doc/grammar key spelling drift")

# 5. The recipe tells the reader the death stays visible (the clamp's honest
# clause — a done record keeps error_class/error/harvest), so the release is
# honest, not an error swallow.
check("recipe says the death stays on the record",
      re.search(r"death.{0,80}record|record.{0,80}death", doc, re.IGNORECASE | re.DOTALL) is not None,
      "no honest-visibility clause")

print(f"{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
