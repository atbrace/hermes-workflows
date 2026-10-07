#!/usr/bin/env python3
"""sys-1w0hoy ask 1 — the suite owns its child env: an ambient PYTHONPATH
(agent-terminal / cron / hook leak) must NOT reach a test case. The leak has
been re-diagnosed every session (test_validate_0923, test_sprint101_A-door,
test_tool_bridge_settings, test_card_backend_080 import hermes_constants and
red-shift on whoever's PYTHONPATH happens to be set), so suite.py strips
PYTHONPATH for every case the same way it pins HERMES_HOME.
Hermetic: throwaway root of stub tests, run via sys.executable, same shape as
tests/test_suite_zero_discovery_112.py.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUITE = ROOT / "scripts" / "suite.py"
fails = 0
total = 0


def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))
    fails += 0 if ok else 1


def make_root(td, name, body):
    root = Path(td) / "root"
    (root / "tests").mkdir(parents=True)
    (root / "tests" / name).write_text(body)
    return root


PROBE = """import json, os, sys
out = os.environ["PROBE_OUT"]
rec = {"PYTHONPATH": os.environ.get("PYTHONPATH"),
       "HERMES_HOME": os.environ.get("HERMES_HOME")}
open(out, "w").write(json.dumps(rec))
"""

with tempfile.TemporaryDirectory(prefix="suite-pp-1w0hoy-") as td:
    td = Path(td)
    probe_out = td / "env.json"
    root = make_root(td, "test_env_probe.py", PROBE)

    # The suite itself is invoked WITH a poisoned PYTHONPATH, exactly as an
    # agent terminal would; PROBE_OUT tells the stub where to dump what the
    # child env actually carried.
    out = td / "out"
    r = subprocess.run([sys.executable, str(SUITE), str(root), str(out)],
                       capture_output=True, text=True, timeout=120,
                       env={**{k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
                            "PYTHONPATH": "/tmp/ambient-agent-leak",
                            "PROBE_OUT": str(probe_out)})
    check("stub exits 0 despite poisoned PYTHONPATH", r.returncode == 0,
          f"suite rc={r.returncode}")
    seen = None
    if probe_out.exists():
        seen = json.loads(probe_out.read_text())
    check("child saw NO PYTHONPATH (stripped, not inherited)",
          seen is not None and seen.get("PYTHONPATH") is None, str(seen))
    check("suite still pins HERMES_HOME for children (no regression)",
          seen is not None and str(seen.get("HERMES_HOME", "")).endswith("tests/.suite-home"),
          str(seen))

print(f"\n{'FAIL' if fails else 'OK'}: {total - fails}/{total} checks pass")
sys.exit(1 if fails else 0)
