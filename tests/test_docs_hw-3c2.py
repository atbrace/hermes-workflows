#!/usr/bin/env python3
"""hw-3c2: the death table. references/death-table.md carries EXACTLY one row
per already-typed error_class — signature -> where it surfaces -> the one
documented repair — and is reachable from the operator docs.

The council's gap (cross-estate consolidation run 20261111-162224, cross-estate
study thread, 2026-11-11): every typed class was documented, nowhere indexable
— the closed-set prose lives scattered across AGENTS.md §3d, operations.md and
the playbook, so an operator holding one error_class had no single row to read.
This pin is the doc half of that gap, the sibling of
tests/test_error_class_doc_sync.py (which pins the AGENTS.md pipe-list): the
table and wf.ERROR_CLASSES must agree exactly, both ways, one row per class,
every row a complete triple. A class added to the frozenset without a table
row, or an invented class in the table, fails the build.

Pure stdlib. Run: python3 tests/test_docs_hw-3c2.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import wf  # noqa: E402

fails = total = 0


def check(name, cond, detail=""):
    global fails, total
    total += 1
    print(("PASS " if cond else "FAIL " + name) + (f" :: {detail[:300]}" if detail and not cond else ""),
          flush=True)
    if not cond:
        fails += 1


TABLE = ROOT / "references" / "death-table.md"
check("references/death-table.md exists (the bead's gap-grep term: death table)",
      TABLE.is_file(), str(TABLE))
doc = TABLE.read_text(encoding="utf-8") if TABLE.is_file() else ""

check("the doc names itself the death table", "death table" in doc.lower())
check("the doc states its law: pure index over shipped behavior",
      "pure index over shipped behavior" in doc.lower())
check("the columns are the bead's triple",
      "signature" in doc.lower() and "where it surfaces" in doc.lower()
      and "documented repair" in doc.lower())

# the table proper: markdown rows whose first cell is a backticked class name
rows = []
for line in doc.splitlines():
    if not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 4 or cells[0].startswith("---") or set(cells[0]) <= set("-: "):
        continue
    if cells[0].strip("`") == "error_class":
        continue  # header row
    rows.append(cells)

classes = [c[0].strip("`") for c in rows]
check("every table row names a class in backticks",
      all(c[0].startswith("`") and c[0].endswith("`") for c in rows),
      f"bare-name rows: {[c[0] for c in rows if not c[0].startswith('`')]}")
check("no duplicate rows (one row per class)",
      len(classes) == len(set(classes)),
      f"dups: {sorted({c for c in classes if classes.count(c) > 1})}")
check("table set == ERROR_CLASSES (nothing typed missing, nothing invented)",
      set(classes) == set(wf.ERROR_CLASSES),
      f"in code, no row: {sorted(set(wf.ERROR_CLASSES) - set(classes))}; "
      f"row, not in code: {sorted(set(classes) - set(wf.ERROR_CLASSES))}")
check("every row is a complete triple (signature / surfaces / repair non-empty)",
      all(all(cell for cell in c[1:4]) for c in rows),
      f"short rows: {[c[0] for c in rows if not all(cell for cell in c[1:4])]!r}")

# reachability: an operator reading the operator docs must be routed here
for f in ("references/operations.md", "references/operator-playbook.md"):
    check(f"{f} links the death table",
          "death-table.md" in (ROOT / f).read_text(encoding="utf-8"))

print(f"TOTAL {total - fails} PASS {fails} FAIL", flush=True)
raise SystemExit(1 if fails else 0)
