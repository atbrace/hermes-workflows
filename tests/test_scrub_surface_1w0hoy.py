#!/usr/bin/env python3
"""sys-1w0hoy ask 3 — the publish scrub audit covers EVERY text file that
ships, not a suffix whitelist. Estate tokens in seat/label wording hide in
exactly the shapes the old AUDIT_SUFFIXES set skipped (.yml workflow labels,
.txt lists, extensionless fixtures), so the bounced-4-rounds class of leak
(`haus seat` passing the scrub) must fail the build HERE. Hermetic: throwaway
git repo, make_public.py driven with --repo like CI does.
"""
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MP = ROOT / "scripts" / "make_public.py"
PY = sys.executable
fails = 0
total = 0


def check(name, ok, detail=""):
    global fails, total
    total += 1
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail and not ok else ""))
    fails += 0 if ok else 1


def run_audit(repo, target):
    return subprocess.run([PY, str(MP), str(target), "--repo", str(repo)],
                          capture_output=True, text=True, timeout=120)


def make_repo(td):
    repo = Path(td) / "repo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "scripts").mkdir()
    (repo / "scripts" / ".scrub-guards").write_text("# empty allow-list\n")
    return repo


TOKEN = "haus-elec"  # matches the built-in \bhaus\b family without the exhaust false-positive

with tempfile.TemporaryDirectory(prefix="scrub-surface-1w0hoy-") as td:
    td = Path(td)

    # (a) a .yml label line carrying the estate token FAILS the audit.
    repo = make_repo(td)
    (repo / "graph.yml").write_text(f'seat:\n  label: "fast {TOKEN} seat"\n')
    (repo / "ok.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo, check=True)
    r = run_audit(repo, td / "out-a")
    check("estate token in .yml seat/label wording FAILS the publish audit",
          r.returncode == 1 and "graph.yml:2" in r.stderr, r.stdout[:120] + r.stderr[:200])

    # (b) extensionless and .txt files are audited too.
    repo2 = make_repo(td / "b")
    (repo2 / "fixture-bin-fake").write_text(f"spawn {TOKEN} now\n")
    (repo2 / "notes.txt").write_text(f"wording mentions {TOKEN}\n")
    subprocess.run(["git", "add", "-A"], cwd=repo2, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo2, check=True)
    r2 = run_audit(repo2, td / "out-b")
    check("estate token in extensionless/.txt files FAILS the audit",
          r2.returncode == 1 and "fixture-bin-fake:1" in r2.stderr and "notes.txt:1" in r2.stderr,
          r2.stderr[:250])

    # (c) a genuine binary (NUL-bearing) is copied, never grepped: no crash,
    # and its .py sibling keeps the audit honest.
    repo3 = make_repo(td / "c")
    (repo3 / "blob.png").write_bytes(b"\x89PNG\r\n\x1a\n\0" + TOKEN.encode() + b"\0more")
    (repo3 / "ok.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "-A"], cwd=repo3, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo3, check=True)
    r3 = run_audit(repo3, td / "out-c")
    check("NUL-bearing binary is copied without grep (clean rc, still shipped)",
          r3.returncode == 0 and (td / "out-c" / "blob.png").exists(),
          r3.stderr[:200])

    # (d) clean tree still publishes green (no over-blocking regression).
    repo4 = make_repo(td / "d")
    (repo4 / "ok.yml").write_text("seat:\n  label: \"fast seat\"\n")
    subprocess.run(["git", "add", "-A"], cwd=repo4, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo4, check=True)
    r4 = run_audit(repo4, td / "out-d")
    check("clean tree publishes green", r4.returncode == 0, r4.stderr[:200])

    # (e) real-repo contract: this repo's own tree passes the widened audit.
    r5 = run_audit(ROOT, td / "out-real")
    check("THIS repo passes the widened audit (0 scrub hits)",
          r5.returncode == 0, r5.stderr[:400])

print(f"\n{'FAIL' if fails else 'OK'}: {total - fails}/{total} checks pass")
sys.exit(1 if fails else 0)
