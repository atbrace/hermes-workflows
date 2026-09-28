# Graph Report - tree  (2026-09-28)

## Corpus Check
- 104 files · ~137,254 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1208 nodes · 2413 edges · 81 communities (62 shown, 19 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 155 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- test_prompt_workdir.py
- pathlib
- test_fanout_expand.mjs
- log
- time
- jload
- test_fanout_item_goal.py
- os
- __init__.py
- test_card_frontend_contract.mjs
- test_sprint101w2_C3-fanout-gates.py
- test_live_truth_ui.mjs
- plugin_api.py
- subprocess
- test_register_surface.mjs
- test_preflight_liveness_152be7f7.py
- EngineNextCut
- CurrentAttemptMetrics
- _SV
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- act_run
- test_edge_routing.mjs
- test_session_strip.mjs
- Changelog
- CardBackend
- LiveTruth
- test_node_panel.mjs
- Hermes Workflows
- test_sprint101_A-door.py
- node_facts
- test_orphan_adopt_790c6ad.py
- validate_graph_errors
- json
- test_metrics_missing_ui.mjs
- _resolve_models
- sys
- test_deleted_cwd_resume_5c37b19.py
- test_amend_rebake_034849a2.py
- test
- test_node_facts.py
- Contributing to hermes-workflows
- act_save
- plugin-catalog: add `hermes-workflows` (community, automation)
- Disclosure verification — clause-by-clause evidence
- SKILL.md
- test_fanout_ui.mjs
- test_sprint101w2_B2-retry.py
- 3. Operate
- test_engine.py
- model_preflight
- test_lifecycle_next_cut_0923.py
- test_review_fixes.py
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- AGENTS.md
- 4. Contribute
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- act_inbox
- Manual installation — Hermes Workflows 1.0.11
- graph_check.py
- test_prune_0923.py
- test_tiers.py
- test_v3_fixes.py
- test_v5_fixes.py
- child_metrics
- 2. Install
- _bind_run_context
- test_papercuts_0922.py
- set_ping
- manifest.json
- Integrated
- FakeProcess
- _AdoptedHandle
- Run
- fake

## God Nodes (most connected - your core abstractions)
1. `efp()` - 31 edges
2. `jload()` - 29 edges
3. `run_child()` - 28 edges
4. `_adopt_child()` - 21 edges
5. `main()` - 21 edges
6. `run_state()` - 21 edges
7. `loop()` - 20 edges
8. `NodePanel()` - 18 edges
9. `CurrentAttemptMetrics` - 18 edges
10. `EngineNextCut` - 16 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `3a. The loop` --references--> `run()`  [INFERRED]
  AGENTS.md → tests/test_run_binding.py
- `Operator surface` --references--> `run()`  [INFERRED]
  CHANGELOG.md → tests/test_run_binding.py
- `Small, parent-gated escalation recipe (no new engine feature)` --references--> `run()`  [INFERRED]
  references/operations.md → tests/test_run_binding.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py

## Import Cycles
- None detected.

## Communities (81 total, 19 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (84): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+76 more)

### Community 1 - "wf.py"
Cohesion: 0.06
Nodes (57): concurrent_futures, fcntl, _adopt_child(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract() (+49 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.07
Nodes (48): shlex, Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), drain_inbox(), emit() (+40 more)

### Community 3 - "test_prompt_workdir.py"
Cohesion: 0.08
Nodes (32): argparse, fnmatch, hashlib, Pattern, excluded(), load_guards(), main(), Path (+24 more)

### Community 4 - "pathlib"
Cohesion: 0.09
Nodes (19): contextlib, copy, importlib_util, pathlib, tempfile, Authoring door regressions; all state stays in this worktree, no…, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, Regression: launch a run in the tool's session; the payload carries a parser-… (+11 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "log"
Cohesion: 0.09
Nodes (30): run(), _bounded_retry(), build_inputs(), _dangling_placeholders(), fmt_goal(), _inputs_block(), log(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s… (+22 more)

### Community 7 - "time"
Cohesion: 0.08
Nodes (15): glob, hermes_constants, plugin_api, re, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+7 more)

### Community 8 - "jload"
Cohesion: 0.13
Nodes (26): act_amend(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), ONE gate-answer path for tool and UI. Stale answers never block: the answer…, Append mode: runner.log keeps crash diagnostics across respawns. Stamp wf.pid… (+18 more)

### Community 9 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 10 - "os"
Cohesion: 0.10
Nodes (8): os, shutil, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Library verbs + /wf command: save (from run_id / inline), library list, run…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.…, 4052d57719653b1a: atomic library replay binding, no real runner., Item #76 (verb-roadmap/wait-payload): mid-run status/wait must NOT re-ship…

### Community 11 - "__init__.py"
Cohesion: 0.11
Nodes (21): difflib, _frozen_committed(), _import_call_llm(), _output_pointer(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status() (+13 more)

### Community 12 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_crypto, ref_node_fs, ref_node_os, ref_node_path, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 13 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.09
Nodes (7): Ctx, Deterministic regressions for explicit workflow provider/model routing., sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 14 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 15 - "plugin_api.py"
Cohesion: 0.18
Nodes (18): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read…, Load this plugin's sibling module without binding global ``wfcommon``. (+10 more)

### Community 16 - "subprocess"
Cohesion: 0.10
Nodes (5): Serial bounded suite with durable per-case logs and atomic exit ledger. The…, subprocess, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, Tier self-report (2026-09-24): a FAILED child's core -Q turn report tier is…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 17 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 18 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.15
Nodes (16): Exception, check(), contract(), EscapeLineOnly, _fake_parse_retry_after(), FakeHTTPError, graph_two_routes(), HostileStr (+8 more)

### Community 19 - "EngineNextCut"
Cohesion: 0.20
Nodes (4): Smallest working graph, Workflow authoring (1.0.11), EngineNextCut, deps_ok()

### Community 21 - "_SV"
Cohesion: 0.12
Nodes (11): Tiny recursive-descent evaluator: or > and > not > comparison > value. Values:…, Syntax-mode value: total-order sentinel so a PARSE-ONLY pass never raises on…, Parse-only check for validate_graph — VALUE-INDEPENDENT (sentinel operands), so…, _SV, _when_and(), _when_atom(), _when_cmp(), _when_expr() (+3 more)

### Community 22 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 23 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 24 - "act_run"
Cohesion: 0.16
Nodes (16): 4. State location, act_library(), act_list(), act_run(), _card(), _hermes_bin(), _lib_path(), library_root() (+8 more)

### Community 25 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 26 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 27 - "Changelog"
Cohesion: 0.13
Nodes (14): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+6 more)

### Community 30 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 31 - "Hermes Workflows"
Cohesion: 0.14
Nodes (14): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, For agents and contributors, Hermes Workflows (+6 more)

### Community 32 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 33 - "node_facts"
Cohesion: 0.14
Nodes (13): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS, Run operations and read model, Small, parent-gated escalation recipe (no new engine feature) (+5 more)

### Community 34 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.15
Nodes (8): datetime, signal, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 35 - "validate_graph_errors"
Cohesion: 0.15
Nodes (12): apply_graph_defaults(), _defaults_errors(), Bake run-level `defaults` + per-node `shape` presets into the agent node defs,…, Canonical reasoning set: ('none',) + hermes_constants.VALID_REASONING_EFFORTS.…, Return a LIST of {node, field, msg} — EVERY defect, not the first. Strict ids:…, gate.wait = {wait_s?, until_argv?, every_s?, timeout_s?}: a machine-answered…, Per-key rules for a graph-level `defaults:` block — the SAME checks a node key…, reasoning_levels() (+4 more)

### Community 36 - "json"
Cohesion: 0.15
Nodes (6): json, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn., mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 37 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 38 - "_resolve_models"
Cohesion: 0.21
Nodes (12): _alias_provider_pair(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., resolve_models(), _resolve_models() (+4 more)

### Community 39 - "sys"
Cohesion: 0.17
Nodes (5): sys, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, End-to-end test of the `workflow` tool door against fake hermes., Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph()

### Community 41 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 42 - "test"
Cohesion: 0.25
Nodes (10): fixture(), put(), 95d7010295d70102: versioned replay integrity across the budget-rule change., test(), Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes. (+2 more)

### Community 43 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 44 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 45 - "act_save"
Cohesion: 0.20
Nodes (10): act_save(), _coerce_graph(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, Shelve a graph under a name: from an existing run (`run_id`) or an inline…, Return graph-level and node-level defects together, before any write/spawn., _validation_error() (+2 more)

### Community 46 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.22
Nodes (7): Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime), plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence (re-run on the published pin before submitting), What it is

### Community 47 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.22
Nodes (9): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 5. Network, cron, credentials — the corrected clause, 6. Desktop gate answer (maintainer ask #122099, teknium1), Disclosure verification — clause-by-clause evidence, handle(), model_tiers() (+1 more)

### Community 48 - "SKILL.md"
Cohesion: 0.22
Nodes (6): Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Staleness and replay

### Community 49 - "test_fanout_ui.mjs"
Cohesion: 0.22
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 50 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 51 - "3. Operate"
Cohesion: 0.25
Nodes (8): 1. What this is (30 seconds), 3. Operate, 3a. The loop, 3b. Minimal graph, 3c. Fan-out, gates, branches, 3e. Reporting a finished run, 5. Where things live at runtime, AGENTS.md — front door for agents

### Community 52 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 53 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Reasoning levels the (provider, model) route accepts; the global set when the…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 58 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 60 - "4. Contribute"
Cohesion: 0.33
Nodes (6): 4. Contribute, 4a. Map, 4b′. Navigate with the knowledge graph, 4b. Run the checks, 4c. Rules, 4d. Release

### Community 61 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 62 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 63 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, _steer_event(), _steer_lines()

### Community 64 - "Manual installation — Hermes Workflows 1.0.11"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 1.0.11, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 65 - "graph_check.py"
Cohesion: 0.67
Nodes (5): _ast(), main(), _norm(), Graph drift gate: is the committed graphify-out/graph.json current for this…, sig()

### Community 70 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 71 - "2. Install"
Cohesion: 0.40
Nodes (5): 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths

### Community 72 - "_bind_run_context"
Cohesion: 0.40
Nodes (4): _bind_run_context(), agent_ancestor(), render(), Resolve a launch binding on a post-defaults copy, before persistence. Map…

### Community 74 - "set_ping"
Cohesion: 0.40
Nodes (5): fake_call_llm(), call_llm(), _raise_import_error(), behavior=None restores the non-core host (import raises); dict stubs the…, set_ping()

### Community 75 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

## Knowledge Gaps
- **197 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+192 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 623 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `Disclosure verification — clause-by-clause evidence` to `act_run`, `plugin-catalog: add `hermes-workflows` (community, automation)`?**
  _High betweenness centrality (0.390) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `Disclosure verification — clause-by-clause evidence` to `plugin.js`?**
  _High betweenness centrality (0.382) - this node is a cross-community bridge._
- **Why does `nudgeOwner()` connect `plugin.js` to `Disclosure verification — clause-by-clause evidence`?**
  _High betweenness centrality (0.380) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _197 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06638655462184874 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06412583182093164 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07215686274509804 - nodes in this community are weakly interconnected._