docs(budgets): the honest-partial recipe next to the close-out guidance

references/budgets.md — the doc an author reaches when a late leg dies
cap_exhausted and its descendants go blocked_by_partial_ancestor — warned that
a harvested partial blocks plain edges but never named the escape hatch that
is already implemented: harvest_policy:"validate" (producer-side: a
schema-valid, no-Remaining harvest commits done, the death kept on the record)
or after_partial:true (consumer-side: consume the harvest deliberately). The
recipe lived only in references/grammar.md and a buried SKILL.md bullet. One
paragraph added after the write-first/close-out paragraph; the council
gap-grep over budgets.md now goes non-empty (hw-3ft).

Tests: tests/test_docs_hw-3ft.py — the gap-grep itself, plus pins that the doc
names both release directions with the grammar.md spellings, sits after the
write-first paragraph, and keeps the honest-visibility clause.
