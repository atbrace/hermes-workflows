# Graph Report - tree  (2026-09-27)

## Corpus Check
- 96 files · ~130,967 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1150 nodes · 2283 edges · 70 communities (54 shown, 16 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 135 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- CurrentAttemptMetrics
- wfcommon.py
- sys
- test_fanout_expand.mjs
- plugin_api.py
- os
- efp
- jload
- subprocess
- test_fanout_item_goal.py
- run_agent_node
- test_prompt_workdir.py
- test_live_truth_ui.mjs
- __init__.py
- time
- test_register_surface.mjs
- test_failures_0923.py
- ref_node_fs
- act_amend
- test_canvas_wrap.mjs
- EngineNextCut
- pathlib
- shutil
- test_edge_routing.mjs
- test_session_strip.mjs
- LiveTruth
- test_node_panel.mjs
- 4. Contribute
- test_orphan_adopt_790c6ad.py
- _ping_route_once
- test_preflight_liveness_152be7f7.py
- test_metrics_missing_ui.mjs
- CardBackend
- Changelog
- test_tiers.py
- act_run
- test_deleted_cwd_resume_5c37b19.py
- test_card_frontend_contract.mjs
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- FakeHTTPError
- test_validate_0923.py
- test_sprint101w2_B2-retry.py
- _SV
- amend
- test_engine.py
- test_model_preflight_0924.py
- model_preflight
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- act_inbox
- Hermes Workflows
- test_failed_events_77.py
- test_prune_0923.py
- test_tier_report_0924.py
- test_v3_fixes.py
- child_metrics
- 3. Operate
- 1.0.2 — 2026-09-26 — the run watches itself
- manifest.json
- Integrated
- FakeProcess
- write_runner_exit
- Run
- Ctx
- fake

## God Nodes (most connected - your core abstractions)
1. `efp()` - 33 edges
2. `run_child()` - 28 edges
3. `jload()` - 28 edges
4. `_adopt_child()` - 21 edges
5. `main()` - 20 edges
6. `run_state()` - 20 edges
7. `NodePanel()` - 18 edges
8. `CurrentAttemptMetrics` - 18 edges
9. `loop()` - 18 edges
10. `EngineNextCut` - 16 edges

## Surprising Connections (you probably didn't know these)
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface)` --references--> `model_preflight()`  [INFERRED]
  CHANGELOG.md → __init__.py
- `Explorer V2: one node truth, two readers` --references--> `_view()`  [INFERRED]
  CHANGELOG.md → dashboard/plugin_api.py
- `Nodes and data` --references--> `build()`  [INFERRED]
  references/grammar.md → scripts/pack.py

## Import Cycles
- None detected.

## Communities (70 total, 16 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "wf.py"
Cohesion: 0.05
Nodes (65): concurrent_futures, fcntl, _adopt_child(), _AdoptedHandle, build_inputs(), _cancel_evidence(), _child_spoke(), child_work_dir() (+57 more)

### Community 2 - "CurrentAttemptMetrics"
Cohesion: 0.05
Nodes (35): Explorer V2: one node truth, two readers, Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is, Apply (source install only) (+27 more)

### Community 3 - "wfcommon.py"
Cohesion: 0.07
Nodes (39): shlex, amend_preview(), apply_graph_defaults(), current_attempt(), def_hash(), _defaults_errors(), _downstream(), gate_answer_valid() (+31 more)

### Community 4 - "sys"
Cohesion: 0.08
Nodes (15): importlib_util, json, sys, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes., v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run… (+7 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "plugin_api.py"
Cohesion: 0.10
Nodes (23): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+15 more)

### Community 7 - "os"
Cohesion: 0.10
Nodes (15): contextlib, copy, os, tempfile, Authoring door regressions; all state stays in this worktree, no…, Regression: launch a run in the tool's session; the payload carries a parser-…, Current-attempt heartbeat with real fake child identity; no provider access., Engine branch contracts, exercised by the actual runner and fake CLI (no… (+7 more)

### Community 8 - "efp"
Cohesion: 0.12
Nodes (27): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), finalize(), hermes_home() (+19 more)

### Community 9 - "jload"
Cohesion: 0.13
Nodes (26): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), Append mode: runner.log keeps crash diagnostics across respawns. Stamp wf.pid…, Strict: no silent normalization — ids double as directory names. (+18 more)

### Community 10 - "subprocess"
Cohesion: 0.08
Nodes (8): Serial bounded suite with durable per-case logs and atomic exit ledger. The…, subprocess, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 11 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 12 - "run_agent_node"
Cohesion: 0.09
Nodes (25): _bounded_retry(), _dangling_placeholders(), fmt_goal(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING… (+17 more)

### Community 13 - "test_prompt_workdir.py"
Cohesion: 0.11
Nodes (23): argparse, fnmatch, hashlib, Pattern, excluded(), load_guards(), main(), Path (+15 more)

### Community 14 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 15 - "__init__.py"
Cohesion: 0.16
Nodes (19): difflib, _alias_provider_pair(), handle(), model_tiers(), _output_pointer(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit… (+11 more)

### Community 16 - "time"
Cohesion: 0.10
Nodes (6): Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…, time

### Community 17 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 18 - "test_failures_0923.py"
Cohesion: 0.11
Nodes (6): sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time…, Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…

### Community 19 - "ref_node_fs"
Cohesion: 0.12
Nodes (12): ref_node_fs, ref_node_path, ref_node_url, code, { fanItems, fanCounts }, here, src, [first, second] (+4 more)

### Community 20 - "act_amend"
Cohesion: 0.12
Nodes (17): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _liveness_hint_suffix(), fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, The door only ever sees `graph` as a parsed object from the tool schema, but a… (+9 more)

### Community 21 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 23 - "pathlib"
Cohesion: 0.19
Nodes (13): pathlib, re, _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig(), check() (+5 more)

### Community 24 - "shutil"
Cohesion: 0.12
Nodes (7): shutil, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…, err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 25 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 26 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 28 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 29 - "4. Contribute"
Cohesion: 0.14
Nodes (14): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 4. Contribute, 4a. Map (+6 more)

### Community 30 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.15
Nodes (8): datetime, signal, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 31 - "_ping_route_once"
Cohesion: 0.14
Nodes (13): _import_call_llm(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the…, Server Retry-After, best-effort via core's parser. None when no header — NEVER… (+5 more)

### Community 32 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.21
Nodes (13): check(), contract(), fake_call_llm(), call_llm(), _fake_parse_retry_after(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.… (+5 more)

### Community 33 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 35 - "Changelog"
Cohesion: 0.17
Nodes (11): 0.9.0 — 2026-09-24, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind, 1.0.9 — 2026-09-27 — amend keeps committed routes only where they replay, Added (+3 more)

### Community 36 - "test_tiers.py"
Cohesion: 0.17
Nodes (5): importlib, Papercuts 2026-09-22 (owner feedback, sibling seat): 1. fan-out items[].goal…, v(), Ctx, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 37 - "act_run"
Cohesion: 0.23
Nodes (12): act_library(), act_run(), _card(), _hermes_bin(), _lib_path(), library_root(), Absolute launcher path — background runners do NOT inherit an interactive PATH., `/wf` — the library front door. `/wf` lists; `/wf <name> [note]` tells the… (+4 more)

### Community 39 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 40 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 41 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 42 - "FakeHTTPError"
Cohesion: 0.20
Nodes (8): Exception, EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 43 - "test_validate_0923.py"
Cohesion: 0.20
Nodes (6): glob, hermes_constants, plugin_api, v0.8.0 routing regression + v0.7.3 contracts: (1) literal ids that target a…, mkrun(), Lane B v0.7.6 contracts (Q2/Q3/Q5 + read model): (1) validate_graph_errors…

### Community 44 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 46 - "amend"
Cohesion: 0.25
Nodes (8): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, What you get, amend()

### Community 47 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 48 - "test_model_preflight_0924.py"
Cohesion: 0.29
Nodes (3): atexit, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…

### Community 49 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Reasoning levels the (provider, model) route accepts; the global set when the…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 52 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 53 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 54 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, _steer_event(), _steer_lines()

### Community 55 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 60 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 61 - "3. Operate"
Cohesion: 0.40
Nodes (5): 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3e. Reporting a finished run

### Community 62 - "1.0.2 — 2026-09-26 — the run watches itself"
Cohesion: 0.40
Nodes (5): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS

### Community 63 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 66 - "write_runner_exit"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

## Knowledge Gaps
- **182 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+177 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 596 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `label()` connect `plugin.js` to `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `amend()` connect `amend` to `test_amend_rebake_034849a2.py`, `CurrentAttemptMetrics`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `Changelog` connect `Changelog` to `1.0.2 — 2026-09-26 — the run watches itself`, `model_preflight`, `amend`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _182 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06538987688098495 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05179982440737489 - nodes in this community are weakly interconnected._
- **Should `CurrentAttemptMetrics` be split into smaller, more focused modules?**
  _Cohesion score 0.053763440860215055 - nodes in this community are weakly interconnected._