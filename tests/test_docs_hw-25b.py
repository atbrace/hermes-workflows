#!/usr/bin/env python3
"""hw-25b: the caller-side self-wake guard law must ship in the docs.

Gap-grep law from the bead: the guard text is visible in the shipped tree and
findable by a grep in the bead's own wording. Pins references/operations.md
(the lane_key law section) and the SKILL.md lane_key bullet pointer.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILS = []


def check(label, ok):
    print(("PASS " if ok else "FAIL ") + label, flush=True)
    if not ok:
        FAILS.append(label)


ops = (ROOT / "references" / "operations.md").read_text()
skill = (ROOT / "SKILL.md").read_text()

# bead's own wording, verbatim
check("ops: subject-id + content-hash dedupe law",
      "subject-id" in ops
      and "content-hash over fields your own writes never touch" in ops)
check("ops: own-write self-fire consequence",
      "its own write re-fires it forever" in ops)
check("ops: append-only rows + hash-carrying comments",
      "append-only rows + hash-carrying comments" in ops)
check("ops: named as the self-wake guard",
      re.search(r"(?i)self-wake guard", ops) is not None)
# council gap-grep: guard wording must be greppable in shipped markdown
check("gap-grep: runner-side vs caller-side wording present",
      re.search(r"(?i)subject-id|own write|self-wake", ops) is not None)
# SKILL.md carries a pointer on the lane_key bullet
bullet = re.search(r"(?is)No double-dispatch.*?\[operations\]\(references/operations\.md\)",
                   skill)
check("skill: lane_key bullet mirrors the self-wake guard pointer",
      bullet is not None
      and re.search(r"(?i)self-wake guard", bullet.group(0)) is not None
      and "subject-id" in bullet.group(0))

print("test_docs_hw-25b:", "FAIL " + ", ".join(FAILS) if FAILS else "OK")
sys.exit(1 if FAILS else 0)
