#!/usr/bin/env python3
"""hw-zqq gap-grep pin: the five event-admission laws must be greppable in the
shipped tree (docs/event-admission.md), linked from the README, recorded in the
CHANGELOG's Unreleased section, and in scripts/pack.py's release include list.
The bead's acceptance is literally "a grep from the bead's own wording finds it"
— this script is that grep, so the council's gap-grep cannot silently go empty
again (laws first shipped in #225, deleted without replacement by #470).
Stdlib-only; prints PASS/FAIL; exit 0 green.
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "event-admission.md"

# (label, needle) — needles are the bead's own wording, lowercase-compared.
LAW_GREPS = [
    ("law1 triggers-never-truth", "triggers, never truth"),
    ("law2 session-is-the-pipe", "session is the pipe"),
    ("law3 accelerator", "accelerator"),
    ("law3 dead-man", "dead-man"),
    ("law4 emit-equals-consume", "emit==consume"),
    ("law4 shared eligibility predicate", "shared eligibility predicate"),
    ("law5 three codes", "three answers"),
    ("law5 deferred exit 3", "exit 3"),
    ("law5 no ledger write", "ledger write"),
    ("law5 permanent silence", "silence"),
]

results = []


def check(label, ok, detail=""):
    results.append((label, ok))
    print(f"{'PASS' if ok else 'FAIL'} {label}{' — ' + detail if detail else ''}")


def main():
    if not DOC.is_file():
        check("doc-shipped: docs/event-admission.md exists", False, "file absent")
        # Everything downstream depends on the file; keep the red legible.
        for label, needle in LAW_GREPS:
            check(label, False, "doc absent")
    else:
        check("doc-shipped: docs/event-admission.md exists", True)
        text = DOC.read_text(encoding="utf-8").lower()
        for label, needle in LAW_GREPS:
            check(label, needle in text, f"needle {needle!r}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("readme-link", "event-admission.md" in readme)

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased = re.search(r"(?ms)^## Unreleased$(.*?)(?=^## )", changelog)
    check("changelog-unreleased",
          bool(unreleased) and "event-admission" in unreleased.group(1))

    # Pack-surface law (scripts/pack.py, the no-wholesale include list): an
    # unshipped doc is invisible to every ZIP install — the acceptance is the
    # SHIPPED tree, not just the repo tree.
    spec = importlib.util.spec_from_file_location("pack_pin", ROOT / "scripts" / "pack.py")
    assert spec and spec.loader
    pack = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pack)
    check("pack-surface: docs/event-admission.md is in the release include list",
          "docs/event-admission.md" in pack.INCLUDE_FILES)

    failed = [label for label, ok in results if not ok]
    if failed:
        print(f"FAIL {len(failed)} of {len(results)} checks red")
        return 1
    print(f"PASS all {len(results)} checks green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
