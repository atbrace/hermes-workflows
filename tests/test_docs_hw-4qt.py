#!/usr/bin/env python3
"""hw-4qt: the operator playbook must teach a stall SIGNATURE, not a hunch.

The old line read "growing idle + flat api_calls IS stalled" — that pair is
necessary evidence, not sufficient: a healthy long-reasoning seat writes nothing
until it answers, so the old rule kills live work on a hunch. The rule now says
so, and this test bites on the parts an operator actually greps for when a lane
looks wedged: the dropped sufficiency claim, the corroborating evidence (log
tail + process state), the `steer`/`stop` response vocabulary, and the pairing
law — every kill answered with a same-pass re-drive, so a mis-read never costs
the wave its work.

Run: python3 tests/test_docs_hw-4qt.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = (ROOT / "references" / "operator-playbook.md").read_text(encoding="utf-8")

fails = total = 0


def check(name, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL ") + name
          + (f" :: {detail[:300]}" if detail and not cond else ""),
          flush=True)
    if not cond:
        fails += 1


section = doc.split("## Babysitting", 1)[-1] if "## Babysitting" in doc else ""

# THE SYMPTOM: the sufficiency claim must be gone.
check("old sufficiency line retired", "stalled — `steer` it or `stop` + amend; don't wait it out" not in doc,
      "playbook still asserts idle+flat api_calls alone proves a stall")

# THE FIX: the fragments an operator greps for, in the Babysitting section.
for frag in ("necessary evidence, not sufficient",
             "log tail",
             "process state",
             "same-pass re-drive"):
    check(f"stall signature names {frag!r}", frag in section,
          "fragment missing from the Babysitting section (gap-grep would stay empty)")

# The response law survives: kill is still allowed, just corroborated and paired.
check("steer/stop response vocabulary retained", "`steer`" in section and "`stop`" in section,
      "the replacement must keep the action, not just the caveat")

print(f"TOTAL {total - fails} PASS {fails} FAIL", flush=True)
raise SystemExit(1 if fails else 0)
