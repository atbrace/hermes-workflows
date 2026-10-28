#!/usr/bin/env python3
"""#580 R9 (adversary blocker B4, atbrace PR): a NUL-prefixed README.md used to
flip the whole file to the binary skip in make_public's private-string audit —
the exported tree shipped forbidden lines after the NUL with "0 scrub hits"
while the bytes still decoded and rendered.

This file pins the cure as a REGRESSION, cloned from the tests/test_scrub_yml_
166b.py committee harness (same fixture-repo transport: build a minimal git
repo, run the exporter, judge exit code + exported tree). Honest state note:
the cure is ALREADY ON MAIN (scripts/make_public.py:143-148 — committee wf166
A1: a known-text suffix is ALWAYS audited, errors=replace makes the NUL inert;
the null-byte sniff skips only extensionless candidates). These legs are
therefore GREEN-ON-ARRIVAL; they exist so the #580 review class can never
re-open silently, not because this lane changed exporter code.

Law pinned:
  * README.md (a known .md suffix) with one NUL at offset 0/4096/8191 and a
    forbidden line after it -> export REFUSED before anything ships, naming
    README.md:LINE;
  * the poisoned README exports NOTHING (no partial tree);
  * control unchanged: a clean README.md still exports (audit, not ban).

Run: python3 tests/test_scrub_nul_readme_580.py
"""
import shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent
SCRIPT = BUILD / "scripts" / "make_public.py"
OUT_ROOT = BUILD / "home-nul-readme"
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + (f"  {detail}" if detail and not cond else ""))
    ok = ok and bool(cond)

FORBIDDEN_LINE = 'haus-marcus-opus-sol  # credential-shaped marker for the audit'

def run_export(files, tag):
    """Build a minimal git repo holding `files` {rel: bytes}, run make_public,
    return (exit code, stdout+stderr, exported tree dict rel->bytes or None).
    Cloned from tests/test_scrub_yml_166b.py (same fixture-ownership rules:
    the fixture carries its own scrub-list + guards so the repo's real guard
    line numbers never leak into a fixture verdict)."""
    src = OUT_ROOT / f"src-{tag}"; dst = OUT_ROOT / f"dst-{tag}"
    for d in (src, dst):
        shutil.rmtree(d, ignore_errors=True)
    src.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=src, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=src, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=src, check=True)
    (src / "README.md").write_text("# fixture\n")
    (src / "scripts").mkdir(exist_ok=True)
    (src / "scripts" / "scrub-list.txt").write_text("haus-marcus-opus-sol\n")
    (src / "scripts" / ".scrub-guards").write_text("scripts/scrub-list.txt\n")
    for rel, payload in files.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_bytes(payload)
    subprocess.run(["git", "add", "-A"], cwd=src, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=src, check=True)
    p = subprocess.run([sys.executable, str(SCRIPT), str(dst), "--repo", str(src)],
                       capture_output=True, text=True)
    exported = None
    if p.returncode == 0 and dst.exists():
        exported = {str(f.relative_to(dst)): f.read_bytes()
                    for f in dst.rglob("*") if f.is_file() and ".git" not in f.parts}
    return p.returncode, p.stdout + p.stderr, exported

# The exact adversary B4 repro shape: README.md, one NUL, forbidden line after.
# NUL@0 is the review's case; 4096/8191 mirror the yml-166b offset battery so
# a boundary-condition regression (sniff window) cannot return for .md either.
for off in (0, 4096, 8191):
    body = ("# probe\n" + "filler line\n" * 3 + FORBIDDEN_LINE + "\n")
    payload = body.encode()
    payload = payload[:off] + b"\0" + payload[off:]
    rc, out, exp = run_export({"README.md": payload}, f"nul{off}")
    check(f"README.md with NUL@{off} + forbidden line is REFUSED before export",
          rc != 0 and "README.md:5" in out, f"rc={rc} out={out[:160]}")
    check(f"NUL@{off}: refusal exports NOTHING (no partial tree)",
          exp is None, "exported a tree despite refusal")

rc, out, exp = run_export({"README.md": b"# probe\n" + (FORBIDDEN_LINE + "\n").encode()},
                          "plain-poison")
check("control: NUL-free poisoned README still refused (cure is not NUL-scoped)",
      rc != 0 and "README.md:2" in out, f"rc={rc} out={out[:160]}")

rc, out, exp = run_export({"README.md": "# clean probe\n".encode()}, "clean")
check("clean README.md still exports (audit, not ban)",
      rc == 0 and exp and "README.md" in exp, f"rc={rc} out={out[:160]}")

print("DONE test_scrub_nul_readme_580", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
