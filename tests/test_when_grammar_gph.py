#!/usr/bin/env python3
"""hw-gph: the grammar doc must record the real `when` refusal text and the
bare-path truthiness law. The gap (cross-estate study council, 2026-11-11):
references/grammar.md described `when` in comparison-only terms, so a
hyphenated node id met a bare tokenizer message and truthiness looked
accidental. This test is the council's gap-grep pinned as code: it fails red
on a doc that omits either truth, and it pins both truths against the shipped
tokenizer so the doc can't drift from the grammar it describes.
"""
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

os.environ.setdefault("HERMES_HOME", tempfile.mkdtemp(prefix="wf-gph-doc-"))
sys.path.insert(0, str(ROOT))

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


doc = (ROOT / "references" / "grammar.md").read_text()
when_para = next((ln for ln in doc.splitlines() if "Bounded `when`" in ln), "")

# Truth 1: the real refusal text, named as a tokenizer raise, not a subtraction
# misparse (the bead's own gap-grep wording).
check("when paragraph records the refusal text", "bad char" in when_para,
      "grammar.md when paragraph carries no 'bad char' refusal text")
check("when paragraph names the no-subtraction law", "subtraction" in when_para,
      "paragraph does not state the hyphen is never a subtraction misparse")
# Truth 2: a bare path with no comparison is legal truthiness.
check("when paragraph records bare-path truthiness", "truthiness" in when_para,
      "paragraph does not state bare out.<node>.<path> is legal truthiness")

# Pin the doc's claims against the shipped tokenizer (stdlib-only import lane,
# same as the doc gap itself: docs must not describe behavior that isn't there).
import wfcommon  # noqa: E402

msg = wfcommon.when_expr_ok("out.router-node.verdict == 'go'")
check("hyphenated id refuses as bad char at the door (not a subtraction parse)",
      msg is not None and re.search(r"when: bad char '-' at \d+", msg), repr(msg))
check("bare path passes the door", wfcommon.when_expr_ok("out.router.verdict") is None)
check("bare path truthiness: truthy value -> True",
      wfcommon.when_true({"when": "out.router.verdict"}, {"router": {"verdict": "go"}}) is True)
check("bare path truthiness: empty string -> False",
      wfcommon.when_true({"when": "out.router.verdict"}, {"router": {"verdict": ""}}) is False)
check("bare path truthiness: missing path -> False",
      wfcommon.when_true({"when": "out.router.verdict"}, {"router": {}}) is False)

if FAILS:
    print(f"\n{len(FAILS)} check(s) FAILED")
    sys.exit(1)
print("\nall checks passed")
