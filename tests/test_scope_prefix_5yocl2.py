#!/usr/bin/env python3
"""sys-5yocl2: the daemonize hop is wrapped in a transient wf-<run_id>.scope.

Runners took the cgroup of whichever hermes-*.service launched them, so every
unit restart (the 6h swap-reclaim timer, gateway restarts) SIGTERM'd every
in-flight lane. _scope_prefix returns the systemd-run argv prefix; the gate is
(systemd-run on PATH) AND (user manager reachable — its private socket under
XDG_RUNTIME_DIR); otherwise [] and today's plain double-fork stands.

The gate branches are tested against a stub PATH and a sandboxed
XDG_RUNTIME_DIR (never the machine's real state); the LIVE probe (real
systemd-run into a real user manager, cgroup must end in wf-<rid>.scope) runs
only where the real gate holds and skips with NOTE elsewhere (CI runners have
no user manager).

Standalone, stdlib-only:
  PYTHONPATH=/opt/hermes /opt/hermes/.venv/bin/python tests/test_scope_prefix_5yocl2.py
"""
import importlib.util, os, select, shutil, socket, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("WF_TEST_BUILD") or HERE.parent)
scratch = HERE / "home-scopeprefix5yocl2"   # tests/home-*/ — ignored by .gitignore
if scratch.exists():
    shutil.rmtree(scratch)
home = scratch / "home"; home.mkdir(parents=True)
os.environ["HERMES_HOME"] = str(home)
os.environ["WF_RUNS_ROOT"] = str(home / "workflows")   # sandbox BOTH: never the estate shelf
sys.path.insert(0, str(BUILD))
spec = importlib.util.spec_from_file_location("hwsp", BUILD / "__init__.py")
hw = importlib.util.module_from_spec(spec); spec.loader.exec_module(hw)
import wf_test_isolation as _iso71; _iso71.install(hw)

_REAL_GATE = bool(shutil.which("systemd-run")) and hw._user_manager_reachable()
_ORIG_PATH, _ORIG_XRD = os.environ.get("PATH"), os.environ.get("XDG_RUNTIME_DIR")

ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL " ) + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and bool(cond)

def gate(stub_bin, xrd_with_socket):
    """Point PATH/XDG_RUNTIME_DIR at the sandboxed gate halves and ask the prefix."""
    os.environ["PATH"] = str(stub_bin)
    if xrd_with_socket is None:
        os.environ.pop("XDG_RUNTIME_DIR", None)
    else:
        os.environ["XDG_RUNTIME_DIR"] = str(xrd_with_socket)
    return hw._scope_prefix("20261113-120000-demo")

def mk_stub_bin():
    d = scratch / "bin"; d.mkdir(exist_ok=True)
    (d / "systemd-run").write_text("#!/bin/sh\nexit 0\n")
    (d / "systemd-run").chmod(0o755)
    return d

def mk_xrd(name, with_socket):
    # AF_UNIX names cap at ~107 chars: sockets live in a short /tmp sandbox,
    # never under the long tests/home-* tree.
    x = Path(tempfile.mkdtemp(prefix="wfscope5yocl2-", dir="/tmp")) / name
    (x / "systemd").mkdir(parents=True)
    if with_socket:
        s = socket.socket(socket.AF_UNIX); s.bind(str(x / "systemd" / "private")); s.close()
    return x

# T1 gate on -> exact prefix, unit pinned to the run id
_xrd = mk_xrd("xrd-ok", True)
p = gate(mk_stub_bin(), _xrd)
check("T1 gate-on prefix",
      p == ["systemd-run", "--user", "--scope", "--collect",
            "--unit=wf-20261113-120000-demo"], repr(p))
# T2 unit sanitisation: only unit-safe chars survive (run ids are [a-z0-9_-],
# but isalnum() admits unicode graph names — a raw '/' must never reach --unit)
os.environ["PATH"] = str(mk_stub_bin()); os.environ["XDG_RUNTIME_DIR"] = str(_xrd)
u = hw._scope_prefix("a/b c#d\u00e9")[-1]
check("T2 unit sanitised", u == "--unit=wf-a-b-c-d-", repr(u))
# T3 no systemd-run -> [] (today's hop)
check("T3 no systemd-run falls back", gate(str(scratch / "emptybin"), mk_xrd("xrd-nm", False)) == [])
# T4 systemd-run but no user manager (no private socket, then no XDG at all)
check("T4 no manager falls back", gate(mk_stub_bin(), mk_xrd("xrd-nm2", False)) == []
      and gate(mk_stub_bin(), None) == [])

if _ORIG_PATH is None:
    os.environ.pop("PATH", None)
else:
    os.environ["PATH"] = _ORIG_PATH
if _ORIG_XRD is None:
    os.environ.pop("XDG_RUNTIME_DIR", None)
else:
    os.environ["XDG_RUNTIME_DIR"] = _ORIG_XRD

# T5 LIVE: real systemd-run, real manager — the wrapped process must land in
# wf-<rid>.scope (proves bus, unit naming and cgroup placement end to end).
if _REAL_GATE:
    rid = time.strftime("20261113-%H%M%S-scope-probe")
    r = subprocess.run([*hw._scope_prefix(rid), sys.executable, "-c",
                        "print(open('/proc/self/cgroup').read())"],
                       capture_output=True, text=True, timeout=30)
    line = next((ln.split("::", 1)[1] for ln in r.stdout.splitlines() if ln.startswith("0::")), "")
    check("T5 live cgroup is the scope",
          r.returncode == 0 and line.endswith(f"wf-{rid}.scope"),
          f"rc={r.returncode} cgroup={line!r} err={r.stderr.strip()[:200]}")
else:
    print("NOTE live scope probe skipped (no real systemd-run/user manager here)")

# T6 LIVE: the REAL hop shape through the scope — systemd-run must hand the
# ready fd through (pass_fds) and the double-fork/setsid runner must survive
# its own transient parent AND systemd-run exiting: a scope that killed its
# cgroup at main-PID exit would silently murder every spawn (the trap T5 can't
# see, because T5's probe IS the main process).
if _REAL_GATE:
    tgt = scratch / "t6_runner.py"
    tgt.write_text(r'''
import os, time
fd = int(os.environ["HERMES_WF_READY_FD"])
cg = open("/proc/self/cgroup").read().strip()
os.write(fd, str(os.getpid()).encode() + b" " + cg.encode() + b"\n")
time.sleep(30)   # stay long enough to see whether systemd sweeps the cgroup
''')
    rid6 = time.strftime("%Y%m%d-%H%M%S-t6-probe")
    rd6, wd6 = os.pipe()
    p6 = subprocess.Popen([*hw._scope_prefix(rid6), sys.executable, "-c",
                           hw._DAEMON_INTERMEDIATE, str(tgt), rid6, str(wd6)],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          stdin=subprocess.DEVNULL, pass_fds=(wd6,),
                          start_new_session=True)
    os.close(wd6)
    try:
        ready6 = os.read(rd6, 256).split(b"\n")[0].split() if select.select([rd6], [], [], 10)[0] else []
    finally:
        os.close(rd6)
    p6.wait(timeout=10)
    runner6 = int(ready6[0]) if ready6 and ready6[0].isdigit() else None
    alive6 = False
    for _ in range(20):        # 5s past the transient: does systemd sweep the cgroup?
        time.sleep(0.25)
        alive6 = runner6 is not None and os.path.exists(f"/proc/{runner6}")
    check("T6 hop survives the scope: ready fd through systemd-run, runner still in scope",
          alive6 and len(ready6) > 1 and ready6[1].decode().endswith(f"wf-{rid6}.scope"),
          f"ready={ready6!r} alive={alive6}")
    if alive6 and runner6 is not None:
        os.kill(runner6, 15)   # the probe runner exits; no lingering children

shutil.rmtree(scratch, ignore_errors=True)
for d in Path("/tmp").glob("wfscope5yocl2-*"):   # the bound sockets live in here
    shutil.rmtree(d, ignore_errors=True)
sys.exit(0 if ok else 1)
