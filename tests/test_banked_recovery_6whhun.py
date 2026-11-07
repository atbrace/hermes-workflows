#!/usr/bin/env python3
"""sys-6whhun banked-work recovery — scripts/lane_recover.py --banked <run-dir>.

The incident shape: a build seat commits (clean tree, branch ahead of main) and the
lane dies before push/PR. The work is banked in the git sense — safe on the branch,
invisible to the carrier — and the hand is a rebase->push->PR->ci-repair-chain.
--banked turns that hand into one audited command.

Law pinned here (stdlib-only; temp git repo + bare remote; PR/chain legs are
injectable commands):
  * SAME liveness law as --finalize: runner.lock held => refuse (exit 3), zero git
    moves — a live runner can run the chain itself;
  * the banked shape is verified fail-closed (exit 4 + reason in the receipt):
    dirty tree, HEAD off the lane branch, branch not ahead of origin/main, branch
    already on the remote, --pr-check-cmd exit 0 (open PR);
  * default is DRY-RUN: the plan lists fetch->rebase->push (+PR/chain legs when
    commands are given), nothing moves, the push leg carries no force flag;
  * --apply runs the legs and stops at the FIRST failure; a conflicting rebase is
    ABORTED (tree restored, no .git/rebase-* residue), never a force-push;
  * every invocation writes <run>/banked_receipt.json next to nodes/.

Plain script (the lane_recover harness idiom: non-zero exit on any FAIL) AND a
pytest module (def test_banked_* for `pytest -k banked`): the body is the check
list, both runners share it.
"""
import fcntl
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

SCRIPT = ROOT / "scripts" / "lane_recover.py"


def check(label, cond, detail=""):
    return (label, bool(cond), detail)


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=check)


def dead_pid():
    p = subprocess.Popen([sys.executable, "-c", "import sys; sys.exit(7)"])
    p.wait()
    return p.pid


def mk_lane(tmp, name="lane"):
    """Bare remote with main, plus a clone checked out on a one-commit lane branch
    sys-test (NOT pushed). Returns (remote, clone_path). Per-name dirs so several
    lanes coexist in one tmp."""
    remote = tmp / f"remote-{name}.git"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(remote)],
                   capture_output=True, check=True)
    seed = tmp / f"seed-{name}"
    subprocess.run(["git", "clone", str(remote), str(seed)], capture_output=True, check=True)
    git(seed, "config", "user.email", "lane@test")
    git(seed, "config", "user.name", "lane")
    (seed / "f.txt").write_text("base\n")
    git(seed, "add", ".")
    git(seed, "commit", "-m", "base")
    git(seed, "push", "origin", "main")
    lane = tmp / name
    subprocess.run(["git", "clone", str(remote), str(lane)], capture_output=True, check=True)
    git(lane, "config", "user.email", "lane@test")
    git(lane, "config", "user.name", "lane")
    git(lane, "checkout", "-b", "sys-test")
    (lane / "f.txt").write_text("banked work\n")
    git(lane, "add", ".")
    git(lane, "commit", "-m", "banked")
    return remote, lane


def mk_run(tmp, graph, name="run"):
    r = tmp / name
    (r / "nodes").mkdir(parents=True)
    (r / "graph.json").write_text(json.dumps(graph))
    (r / "wf.pid").write_text(str(dead_pid()) + "\n")   # dead pid = dead runner
    return r


def lane_graph(lane, branch="sys-test"):
    return {"name": "b2p-synthetic", "nodes": [
        {"id": "claim-plan", "type": "agent", "goal": "intake only."},
        {"id": "build", "type": "agent", "goal":
            f"Implementation seat. Work only in the prepared {lane} worktree on branch {branch}. "
            "Do not push."},
    ]}


def run_checks():
    spec = importlib.util.spec_from_file_location("lane_recover_banked", SCRIPT)
    lr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lr)

    results = []
    tmp = Path(tempfile.mkdtemp(prefix="banked-"))
    try:
        remote, lane = mk_lane(tmp)
        run = mk_run(tmp, lane_graph(lane))

        # ---- A: dry-run resolves repo+branch from the build goal; plan only.
        rc, rep = lr.recover_banked_work(run)
        results.append(check("A1 dry-run exits 0", rc == 0, f"rc={rc} reason={rep.get('reason')}"))
        results.append(check("A2 repo/branch resolved from the goal (trailing '.' stripped)",
                             rep.get("repo") == str(lane) and rep.get("branch") == "sys-test", rep))
        legs = [s["leg"] for s in rep.get("steps", [])]
        results.append(check("A3 plan legs are fetch/rebase/push in order",
                             legs == ["fetch", "rebase", "push"], legs))
        results.append(check("A4 the push leg is never a force-push",
                             all("-f" not in s["cmd"] and "--force" not in s["cmd"]
                                 for s in rep["steps"] if s["leg"] == "push"), rep["steps"]))
        results.append(check("A5 nothing moved: branch still absent from the remote",
                             not git(remote, "ls-remote", "--heads", ".", "refs/heads/sys-test",
                                     check=False).stdout.strip()))
        receipt = json.loads((run / "banked_receipt.json").read_text())
        results.append(check("A6 dry-run wrote the receipt beside nodes/",
                             receipt.get("mode") == "dry-run" and (run / "nodes").is_dir(), receipt))

        # ---- B: shape checks fail closed with a reason (exit 4).
        (lane / "dirty.txt").write_text("dirt\n")
        rc, rep = lr.recover_banked_work(run)
        results.append(check("B1 dirty tree => 4 + reason",
                             rc == 4 and "dirty" in rep.get("reason", ""), rep.get("reason")))
        (lane / "dirty.txt").unlink()

        git(lane, "checkout", "main")
        rc, rep = lr.recover_banked_work(run)
        results.append(check("B2 HEAD off the lane branch => 4",
                             rc == 4 and "lane branch" in rep.get("reason", ""), rep.get("reason")))
        git(lane, "checkout", "sys-test")

        git(lane, "branch", "sys-empty", "origin/main")
        git(lane, "checkout", "sys-empty")
        rc, rep = lr.recover_banked_work(run, repo=lane, branch="sys-empty")
        results.append(check("B3 branch not ahead of main => 4 (nothing banked)",
                             rc == 4 and "not ahead" in rep.get("reason", ""), rep.get("reason")))
        git(lane, "checkout", "sys-test")
        git(lane, "branch", "-D", "sys-empty")

        rc, rep = lr.recover_banked_work(run, pr_check_cmd="exit 0")
        results.append(check("B4 open PR (--pr-check-cmd exit 0) => 4",
                             rc == 4 and "open pr" in rep.get("reason", "").lower(),
                             rep.get("reason")))
        rc, rep = lr.recover_banked_work(run, pr_check_cmd="exit 1")
        results.append(check("B5 pr-check exit 1 reads as no PR => 0", rc == 0, rep.get("reason")))

        # ---- C: a live runner (runner.lock held) refuses, exit 3.
        hold = open(run / "runner.lock", "w")
        fcntl.flock(hold, fcntl.LOCK_EX)
        try:
            rc, rep = lr.recover_banked_work(run)
        finally:
            fcntl.flock(hold, fcntl.LOCK_UN)
            hold.close()
        results.append(check("C1 held runner.lock => 3, zero moves",
                             rc == 3 and "alive" in rep.get("reason", ""), rep.get("reason")))

        # ---- D: --apply runs the chain; injectable PR/chain legs receive the env.
        log = tmp / "pr.log"
        rc, rep = lr.recover_banked_work(
            run, apply=True,
            pr_cmd=f"sh -c 'echo $LANE_BRANCH $LANE_SHA >> {log}'",
            chain_cmd=f"sh -c 'echo CHAINED $LANE_BRANCH >> {log}'")
        results.append(check("D1 apply exits 0 recovered", rc == 0 and rep.get("status") == "recovered",
                             f"rc={rc} reason={rep.get('reason')}"))
        pushed = git(remote, "ls-remote", "--heads", ".", "refs/heads/sys-test",
                     check=False).stdout.strip()
        results.append(check("D2 the branch is on the remote (plain push)", bool(pushed), pushed))
        logged = log.read_text() if log.exists() else ""
        first = logged.splitlines()[0] if logged else ""
        parts = first.split()
        results.append(check("D3 PR leg saw branch+sha via LANE_* env",
                             parts[:1] == ["sys-test"] and len(parts[1:2][0] if len(parts) > 1 else "") == 40,
                             logged))
        results.append(check("D4 chain leg saw the branch via LANE_BRANCH env",
                             any(l == "CHAINED sys-test" for l in logged.splitlines()), logged))

        # re-run after the push: the shape is gone, the reason names it.
        rc, rep = lr.recover_banked_work(run)
        results.append(check("D5 pushed branch => 4 'already on origin'",
                             rc == 4 and "already on origin" in rep.get("reason", ""),
                             rep.get("reason")))

        # ---- E: rebase conflict on --apply aborts and restores the tree.
        remote2, lane2 = mk_lane(tmp, "lane2")
        seed2 = tmp / "seed-lane2"    # push a conflicting main move from the seed clone
        git(seed2, "checkout", "main")
        (seed2 / "f.txt").write_text("upstream moved\n")
        git(seed2, "commit", "-a", "-m", "moved")
        git(seed2, "push", "origin", "main")
        run2 = mk_run(tmp, lane_graph(lane2), name="run2")
        rc, rep = lr.recover_banked_work(run2, apply=True)
        results.append(check("E1 conflicting rebase => 5", rc == 5 and rep.get("failed_leg") == "rebase",
                             f"rc={rc} reason={rep.get('reason')}"))
        residue = list((Path(lane2) / ".git").glob("rebase-*"))
        results.append(check("E2 rebase aborted: no .git/rebase-* residue", not residue, residue))
        results.append(check("E3 tree restored clean, lane commit intact",
                             not git(lane2, "status", "--porcelain").stdout.strip()
                             and int(git(lane2, "rev-list", "--count", "origin/main..HEAD",
                                         check=False).stdout.strip() or 0) == 1,
                             git(lane2, "status", "--porcelain").stdout))

        # ---- F: repo/branch unresolvable (no goal phrase, no claim-plan output).
        run3 = mk_run(tmp, {"name": "x", "nodes": [{"id": "build", "type": "agent",
                                                   "goal": "no worktree phrase"}]}, name="run3")
        rc, rep = lr.recover_banked_work(run3)
        results.append(check("F1 unresolvable repo/branch => 2 with a name-flags reason",
                             rc == 2 and "--repo" in rep.get("reason", ""), rep.get("reason")))
        (run3 / "nodes" / "claim-plan.json").write_text(
            json.dumps({"status": "done", "output": {"branch": "sys-fallback"}}))
        git(lane, "checkout", "-b", "sys-fallback")   # same commit, still unpushed
        rc, rep = lr.recover_banked_work(run3, repo=lane)   # branch now from claim-plan
        results.append(check("F2 claim-plan output.branch is the branch fallback",
                             rc == 0 and rep.get("branch") == "sys-fallback", rep.get("reason")))

        # ---- G: receipt records a refusal too (audit trail is the whole point).
        results.append(check("G1 refusal receipt carries the reason",
                             json.loads((run3 / "banked_receipt.json").read_text())
                             .get("reason")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return results


def test_banked_recovery():
    bad = [r for r in run_checks() if not r[1]]
    for label, ok, detail in bad:
        print(f"FAIL {label}: {detail}")
    assert not bad, f"{len(bad)} banked-recovery check(s) failed"


if __name__ == "__main__":
    results = run_checks()
    fails = 0
    for label, ok, detail in results:
        print(("PASS " if ok else "FAIL ") + label + (f": {detail}" if not ok else ""))
        fails += not ok
    print(f"\n{len(results)} checks, {fails} failure(s)")
    sys.exit(1 if fails else 0)
