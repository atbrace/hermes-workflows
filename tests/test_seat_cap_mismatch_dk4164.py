#!/usr/bin/env python3
"""sys-dk4164 — declared-vs-seeded seat cap must fail LOUD at admission.

Measured defect (fan-out lane b73cc5): the estate pool recorded .cap=4 before
a run declared max_seats: 8; _seat_pool_cap silently dropped the declaration
(the clamp only rides UNDER the recorded truth), the fan-out queued against 4
seats, and four lanes died at the queue horizon (seat_wait) instead of
admission ever saying so.

Fix contract (wf.py): AT ADMISSION (pool_seed present, the run_child graft
shape) a ceiling ABOVE the recorded .cap raises SeatCapError typed
"seat_cap_mismatch", naming the pool cap, the declared cap, and the .cap reset
path. The pool NEVER auto-raises: .cap keeps the recorded value (est-mg5o2
first-writer-wins). A ceiling UNDER or AT the pool cap still rides under it
(mg5o2 law intact); a read-only peek (seed=None, the seat.wait event path)
still reports the recorded truth without raising.

Dual-mode like test_error_classes_exhaustive_vb65.py: real pytest functions
run as a WF-GRAFT-6 subprocess item under tests/conftest.py (file-level
verdict), and standalone for scripts/suite.py.

Run: python -m pytest -q tests -k seat_cap_mismatch
 or: python3 tests/test_seat_cap_mismatch_dk4164.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wf


def _pool(tmp, cap):
    d = Path(tmp) / f".seats-{cap}"
    d.mkdir(parents=True)
    (d / ".cap").write_text(str(cap), encoding="utf-8")
    return d


def test_declared_cap_above_pool_cap_rejects_at_admission():
    # The bead's regression row: pool .cap=4, run declares max_seats: 8 —
    # the mismatch surfaces at admission, it is never silent.
    with tempfile.TemporaryDirectory() as tmp:
        d = _pool(tmp, 4)
        try:
            wf._seat_pool_cap(d, seed=4, ceiling=8)
        except wf.SeatCapError as e:
            msg = str(e)
            assert msg.startswith("seat_cap_mismatch"), msg
            assert "4" in msg and "8" in msg, msg
            assert str(d / ".cap") in msg, msg
            print("PASS declared-above-pool raises typed seat_cap_mismatch",
                  flush=True)
        else:
            raise AssertionError("declared cap above recorded .cap was silently clamped")
        assert (d / ".cap").read_text() == "4", ".cap must never auto-raise"
        print("PASS pool .cap untouched (no auto-raise)", flush=True)


def test_acquire_seam_raises_the_mismatch():
    # The production graft shape: the exact _seat_acquire kwargs run_child
    # passes at admission (caller cap, seed, ceiling).
    with tempfile.TemporaryDirectory() as tmp:
        d = _pool(tmp, 4)
        try:
            t = wf._seat_acquire(d, "dk4164", 8, 0.5, pool_seed=4, pool_ceiling=8)
        except wf.SeatCapError as e:
            assert "seat_cap_mismatch" in str(e), e
            print("PASS _seat_acquire raises the mismatch at the seam", flush=True)
        else:
            raise AssertionError(f"acquire returned {t!r}; mismatch was silent")


def test_ceiling_at_or_under_pool_still_rides_and_peeks_stay_quiet():
    with tempfile.TemporaryDirectory() as tmp:
        d = _pool(tmp, 8)
        assert wf._seat_pool_cap(d, seed=8, ceiling=4) == 4   # mg5o2 clamp law intact
        assert wf._seat_pool_cap(d, seed=8, ceiling=8) == 8   # equal is no mismatch
        assert wf._seat_pool_cap(d, ceiling=99) == 8          # read-only peek: truth, not fatal
        assert (d / ".cap").read_text() == "8"
        print("PASS ceiling under/equal rides; read-only peek never raises", flush=True)


if __name__ == "__main__":
    test_declared_cap_above_pool_cap_rejects_at_admission()
    test_acquire_seam_raises_the_mismatch()
    test_ceiling_at_or_under_pool_still_rides_and_peeks_stay_quiet()
    print("ALL PASS declared-vs-seeded cap (sys-dk4164)", flush=True)
