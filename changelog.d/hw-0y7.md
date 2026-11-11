### Added
- `shelf-census`: husk bucket (run dirs past the retention grace that carry no
  terminal record — counted, subtracted from live, never fail-closed) and the
  canonical counters fleet line. Liveness moved to the one liveness law
  (`runner_lock_states` batch, chunked below the argv cap); the weaker
  pid-only fallback can now only ADD liveness, never subtract it.
