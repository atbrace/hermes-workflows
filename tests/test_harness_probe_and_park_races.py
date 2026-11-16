"""Guards for two test-harness races that flake CI.

1. tests/test_native_first_load_concurrency.py probes graph.lock inside every
   committer thread's deliver. flock on separate open file descriptions
   conflicts even inside one process, so two concurrent EX|NB probes collide:
   the loser raises BlockingIOError and the winner times out the delivery
   barrier. The probe must be shared (LOCK_SH|LOCK_NB) yet still refused while
   the product retains an exclusive graph.lock.
2. tests/11-lane-supervisor.py and tests/11-canary.py race a finite-sleep
   child against the kill: on a slow shard the child finishes first, the run
   reaches done, and the needs_resume assert dies with state=done/
   runner_live=False. The child must park on a WAIT file the harness releases
   only after the kill (unbounded park; the harnesses touch every release
   file in a finally), so it can never outrun it. Race 2's RED is forced,
   not raced: the fixture verb probe fails on any fixture that ignores WAIT,
   and the cycle test reports its settle window instead of passing vacuously
   around it. The cleanup path carries a forced failure too: a parked child
   whose release directory is deleted without release (the failed-assert
   teardown shape) must drain, never wait forever on a vanished path.
"""
import fcntl
import importlib.util
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

# Forced-failure proof for the harness cleanup path, run before any other
# section so nothing can mask it: a failed assert makes tempdir teardown
# delete a release file the parked child has not yet noticed, and a park
# that only honors the file waits forever on the vanished path. Park a child
# on a file that is never released, delete its directory, require a drain.
with tempfile.TemporaryDirectory(prefix='wf-drain-') as dtmp:
    trace = Path(dtmp) / '11-child-trace.jsonl'
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "tests/fixtures/11-fake-hermes.py"), 'chat'],
        stdin=subprocess.PIPE, text=True,
        # HERMES_WF_RUN_DIR must not leak in: when the suite runs inside a
        # workflow (gate probe, in-runner suite), the fixture would trace into
        # the OUTER run dir and this section would never see its own trace row.
        env={**{k: v for k, v in os.environ.items() if k != 'HERMES_WF_RUN_DIR'},
             'HERMES_HOME': dtmp}, stdout=subprocess.DEVNULL)
    try:
        proc.stdin.write(f'WAIT {dtmp}/release-lost\n')
        proc.stdin.close()
        end = time.monotonic() + 5
        while time.monotonic() < end and not trace.is_file():
            time.sleep(.01)
        assert trace.is_file(), 'the child fixture never started (no trace row)'
        time.sleep(.3)
        assert proc.poll() is None, (
            'drain proof is vacuous: the child fixture does not honor the '
            'WAIT verb (it exited early and would outrun the kill again)')
        shutil.rmtree(dtmp, ignore_errors=True)
        try:
            rc = proc.wait(5)
        except subprocess.TimeoutExpired:
            raise AssertionError(
                'parked child waits forever on a deleted release directory: '
                'a failed assert leaks an orphan spinning on a dead path')
        assert rc == 0, f'parked child drained rc={rc} after the release directory vanished'
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(5)
print('PASS parked child drains when the release directory vanishes; never waits forever')

# The carrier suite also executes its own concurrency test at import.
carrier_error = None
try:
    import test_native_first_load_concurrency as carrier
    probe = getattr(carrier, "probe_graph_lock", None)
except BaseException as exc:  # the carrier runs its whole test at import
    probe, carrier_error = None, exc
if probe is None:
    # Base shape: deliver inlines the probe as EX|NB on a fresh a+b open.
    def probe(run, mode=fcntl.LOCK_EX | fcntl.LOCK_NB, hold=None):
        with (run / "graph.lock").open("a+b") as lock:
            fcntl.flock(lock, mode)
            if hold is not None:
                hold()

with tempfile.TemporaryDirectory(prefix="wf-probe-race-") as tmp:
    run = Path(tmp)
    both_probing = threading.Barrier(2)
    failures = []

    def probe_once():
        try:
            probe(run, hold=lambda: both_probing.wait(3))
        except BaseException as exc:
            failures.append(exc)

    threads = [threading.Thread(target=probe_once) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(10)
    assert not failures, (failures if carrier_error is None
                          else f"carrier probe unavailable ({carrier_error!r}); "
                               f"synthetic base-shape probe failures: {failures}")
    with (run / "graph.lock").open("a+b") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        try:
            probe(run)
            raise AssertionError("probe granted while the product holds graph.lock exclusively")
        except BlockingIOError:
            pass
print("PASS concurrent probes coexist and the probe stays refused over a held exclusive graph.lock")


def until(pred, seconds=5):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if pred():
            return True
        time.sleep(.01)
    return False


def fixture_verb_probe():
    # Force race 2's RED instead of racing the wall clock the CI flake raced:
    # on a fixture that ignores the WAIT verb the child prints and exits in
    # milliseconds, so the 1 s liveness check fires every time.
    with tempfile.TemporaryDirectory(prefix='wf-verb-probe-') as vtmp:
        gate = Path(vtmp) / 'gate'
        proc = subprocess.Popen(
            [sys.executable, str(ROOT / 'tests/fixtures/11-fake-hermes.py'), 'chat'],
            stdin=subprocess.PIPE, text=True,
            env={**{k: v for k, v in os.environ.items() if k != 'HERMES_WF_RUN_DIR'},
                 'HERMES_HOME': vtmp}, stdout=subprocess.DEVNULL)
        try:
            proc.stdin.write(f'WAIT {gate}\n')
            proc.stdin.close()
            time.sleep(1)
            assert proc.poll() is None, (
                'race-2 harness is vacuous: the child fixture does not honor '
                'the WAIT verb (it exited early and would outrun the kill again)')
            gate.touch()
            assert proc.wait(5) == 0, 'parked child did not drain after release'
        finally:
            gate.touch()
            if proc.poll() is None:
                proc.kill()
                proc.wait(5)
fixture_verb_probe()
print('PASS the fixture WAIT verb parks the child until release, unbounded')

door_spec = importlib.util.spec_from_file_location('flake_door', ROOT / '__init__.py')
door = importlib.util.module_from_spec(door_spec)
door_spec.loader.exec_module(door)
import wf_test_isolation as _iso_flake
_iso_flake.install(door)
import wfcommon as common

with tempfile.TemporaryDirectory(prefix='wf-flake-wait-') as td:
    td = Path(td)
    runs = td / 'runs'
    runs.mkdir()
    rel = td / 'release-0'
    env = {**os.environ, 'HERMES_HOME': str(td), 'WF_RUNS_ROOT': str(runs),
           'HERMES_WF_HERMES_BIN': str(ROOT / 'tests/fixtures/11-fake-hermes.py')}
    with patch.dict(os.environ, env, clear=True):
        graph = {'name': 'flake-wait', 'nodes': [{'id': 'a', 'type': 'agent', 'goal': f'WAIT {rel}'}]}
        start = door.act_run({'graph': graph, 'lane_key': 'flake-wait/0'})
        assert 'run_id' in start, start
        rid = start['run_id']
        r = runs / rid
        assert until(lambda: common.runner_alive(r)), 'runner never live'
        live = door.act_status({'lane_key': 'flake-wait/0'})
        assert live['runner_live'] == common.runner_alive(r) == True, live
        # The CI shape, forced: give the child a 2 s window to reach done
        # before the kill, exactly as a slow shard lets a finite SLEEP win.
        # The outcome rides into the needs_resume failure below so a run that
        # reached done first can never let this test pass vacuously.
        settled = until(lambda: door.act_status({'lane_key': 'flake-wait/0'})['state'] == 'done', 2)
        try:
            os.kill(int((r / 'wf.pid').read_text()), signal.SIGKILL)
        except (FileNotFoundError, ProcessLookupError):
            pass  # the runner already exited clean: the CI shape itself
        try:
            assert until(lambda: not common.runner_alive(r)), 'kill failed'
            dead = door.act_status({'lane_key': 'flake-wait/0'})
            assert dead['needs_resume'], f'needs_resume lost (child reached done before the kill: settled={settled})'
            rel.touch()  # release the parked child only after the kill is proven
            door.act_wait({'run_id': rid, 'timeout': 5})
            assert until(lambda: door.act_status({'lane_key': 'flake-wait/0'})['state'] == 'done', 10), 'not resumed to done'
            assert (r / 'nodes' / 'a.json').is_file(), 'the parked node never committed even after release and resume'
        finally:
            rel.touch()
print("PASS parked child survives the kill, needs_resume holds, resume reaches done")
