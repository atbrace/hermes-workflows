#!/usr/bin/env python3
"""hw-2mb: shelf provenance was WRITE-ONLY — `save` stamped source_digest once and
every later `library` read replayed the stored value verbatim, so a hand-edited,
partially-rewritten, or pre-#126 (unstamped) shelf entry was undetectable.
`library check:true` now recomputes each row's digest against the shelved bytes
and reports drifted/unstamped rows; WITHOUT the flag the response bytes are
unchanged (golden-bytes law). drift_check.py is checkout-version drift, NOT
shelf digests — this is the same seam, finished.
"""
import json, os, shutil, sys
from pathlib import Path
BUILD = Path(os.environ.get("WF_TEST_BUILD") or Path(__file__).parent)
if os.environ.get("WF_TEST_BUILD") and not (BUILD / "fake").exists():
    raise SystemExit("WF_TEST_BUILD names a tests/ dir (this test reads fixtures under it); got " + str(BUILD))

HOME = BUILD / "home_hw2mb"
os.environ["HERMES_HOME"] = str(HOME)
os.environ["WF_RUNS_ROOT"] = str(HOME / "workflows")
shutil.rmtree(HOME, ignore_errors=True)
sys.path.insert(0, str(BUILD))
import importlib.util
spec = importlib.util.spec_from_file_location("hw", str(BUILD.parent / "__init__.py"))
hw = importlib.util.module_from_spec(spec); spec.loader.exec_module(hw)
import wf_test_isolation as iso; iso.install(hw)
os.environ["HERMES_WF_HERMES_BIN"] = str(BUILD / "fake")
def call(**a): return json.loads(hw.handle(a))
ok = True
def check(label, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + label + ("" if cond or not detail else f"  {detail}"))
    ok = ok and cond

G = {"name": "Digest Demo", "nodes": [{"id": "a", "type": "agent", "goal": "go"}]}
SHELF = HOME / "workflows" / "library"

def rows_of(r): return {x["name"]: x for x in r.get("library", [])}

# T1 clean stamped save: digest_match true, nothing unstamped, no author_source.
call(action="save", graph=dict(G), name="clean")
r = call(action="library", check=True)
row = rows_of(r).get("clean", {})
check("T1 clean row digest_match true; unstamped []",
      row.get("digest_match") is True and r.get("unstamped") == [] and "author_source" not in row,
      json.dumps({"row": row, "unstamped": r.get("unstamped")}))

# T2 hand-edited shelf bytes (stored stamp left alone) -> drifted, NOT unstamped.
call(action="save", graph={"name": "Drifted", "nodes": [{"id": "a", "type": "agent", "goal": "go v1"}]},
     name="drifted")
p = SHELF / "drifted.json"
d = json.loads(p.read_text(encoding="utf-8"))
d["nodes"][0]["goal"] = "go v2 hand-edited"
p.write_text(json.dumps(d), encoding="utf-8")
r = call(action="library", check=True)
row = rows_of(r).get("drifted", {})
check("T2 hand-edited row digest_match false, not in unstamped",
      row.get("digest_match") is False and "drifted" not in (r.get("unstamped") or ["?"]),
      json.dumps({"row": row, "unstamped": r.get("unstamped")}))

# T3 pre-#126 bare entry (no provenance block at all) -> unstamped.
(SHELF / "legacy.json").write_text(json.dumps(dict(G, name="legacy")), encoding="utf-8")
r = call(action="library", check=True)
check("T3 unstamped entry named top-level, digest_match false",
      "legacy" in (r.get("unstamped") or []) and rows_of(r).get("legacy", {}).get("digest_match") is False,
      json.dumps({"unstamped": r.get("unstamped"), "row": rows_of(r).get("legacy")}))

# T4 author_source: resolvable file matching the shelf -> match; file moved -> drift.
src = HOME / "author.json"
src.write_text(json.dumps(dict(G, name="author-src")), encoding="utf-8")
call(action="save", graph=dict(G), name="authored", source=str(src))
r = call(action="library", check=True)
check("T4 resolvable author source matches",
      rows_of(r).get("authored", {}).get("author_source") == "match",
      json.dumps(rows_of(r).get("authored")))
src.write_text(json.dumps({"name": "author-src",
                           "nodes": [{"id": "a", "type": "agent", "goal": "moved"}]}), encoding="utf-8")
r = call(action="library", check=True)
check("T4b author file moved -> drift",
      rows_of(r).get("authored", {}).get("author_source") == "drift",
      json.dumps(rows_of(r).get("authored")))

# T5 source that is attribution prose/URL -> no author_source key, no crash.
call(action="save", graph=dict(G), name="prose-src", source="https://example.invalid/graph.json")
r = call(action="library", check=True)
check("T5 non-path source echoes no author_source",
      "author_source" not in rows_of(r).get("prose-src", {}),
      json.dumps(rows_of(r).get("prose-src")))

# T6 GOLDEN BYTES: without check, the tagless response is exactly the pre-change
# key set and rows carry no digest keys.
r6 = call(action="library")
check("T6 no-check response keeps golden bytes (keys == {library,hint}, no digest keys)",
      set(r6) == {"library", "hint"}
      and all("digest_match" not in x and "author_source" not in x for x in r6["library"]),
      json.dumps({"keys": sorted(r6),
                  "row_keys": sorted(rows_of(r6).get("clean", {}))}))

print("ALL PASS" if ok else "FAILURES PRESENT"); sys.exit(0 if ok else 1)
