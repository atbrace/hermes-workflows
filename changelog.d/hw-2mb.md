### Added
- `library` action accepts `check: true`: shelf-row digests are recomputed
  against the live shelf and drift is reported per row (a stored digest is a
  claim, not a fact). Validation keeps the strict boolean shape.
