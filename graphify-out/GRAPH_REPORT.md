# Graph Report - tree  (2026-09-27)

## Corpus Check
- 97 files · ~132,329 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1174 nodes · 2321 edges · 73 communities (58 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 137 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wfcommon.py
- EngineNextCut
- os
- test_fanout_expand.mjs
- graph_check.py
- pathlib
- wf.py
- efp
- plugin_api.py
- time
- jload
- test_fanout_item_goal.py
- test_sprint101w2_C3-fanout-gates.py
- _adopt_child
- importlib_util
- test_live_truth_ui.mjs
- log
- __init__.py
- test_register_surface.mjs
- Changelog
- sys
- CurrentAttemptMetrics
- ref_node_fs
- run_child
- _ping_route_once
- test_canvas_wrap.mjs
- test_node_click_expand.mjs
- Run operations and read model
- test_edge_routing.mjs
- test_session_strip.mjs
- act_run
- LiveTruth
- test_node_panel.mjs
- AGENTS.md
- test_tiers.py
- test_metrics_missing_ui.mjs
- test_prompt_workdir.py
- CardBackend
- test_preflight_liveness_152be7f7.py
- test_orphan_adopt_790c6ad.py
- test_deleted_cwd_resume_5c37b19.py
- test_card_frontend_contract.mjs
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- test_sprint101w2_B2-retry.py
- act_save
- test_engine.py
- model_preflight
- plugin-catalog: add `hermes-workflows` (community, automation)
- test_sprint101w2_C1-defaults.py
- test_sprint101w2_D2-steer-liveness.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- Patched core: typed turn-cap deaths (optional)
- Exception
- act_inbox
- Manual installation — Hermes Workflows 0.9.0
- Hermes Workflows
- test_tier_report_0924.py
- test_v3_fixes.py
- child_metrics
- test_papercuts_0922.py
- test_validator_caps.py
- write_spawn_record
- manifest.json
- Integrated
- FakeHTTPError
- FakeProcess
- Run
- Ctx
- _output_pointer
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

## Communities (73 total, 15 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "wfcommon.py"
Cohesion: 0.05
Nodes (43): shlex, _active_spawn(), _active_spawns(), amend_preview(), apply_graph_defaults(), current_attempt(), _defaults_errors(), _downstream() (+35 more)

### Community 2 - "EngineNextCut"
Cohesion: 0.08
Nodes (23): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+15 more)

### Community 3 - "os"
Cohesion: 0.07
Nodes (13): os, Serial bounded suite with durable per-case logs and atomic exit ledger. The…, shutil, subprocess, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Papercuts 2026-09-22 round 2 (owner feedback drain, sibling seat): 3.… (+5 more)

### Community 4 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 5 - "graph_check.py"
Cohesion: 0.09
Nodes (28): argparse, fnmatch, hashlib, Pattern, re, _ast(), main(), _norm() (+20 more)

### Community 6 - "pathlib"
Cohesion: 0.10
Nodes (16): contextlib, copy, json, pathlib, tempfile, Authoring door regressions; all state stays in this worktree, no…, Regression: launch a run in the tool's session; the payload carries a parser-…, Current-attempt heartbeat with real fake child identity; no provider access. (+8 more)

### Community 7 - "wf.py"
Cohesion: 0.08
Nodes (29): concurrent_futures, fcntl, build_inputs(), _dangling_placeholders(), drain_inbox(), extract_json(), fmt_goal(), _inputs_block() (+21 more)

### Community 8 - "efp"
Cohesion: 0.11
Nodes (29): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, acquire_lock(), emit(), finalize(), main() (+21 more)

### Community 9 - "plugin_api.py"
Cohesion: 0.10
Nodes (23): asyncio, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+15 more)

### Community 10 - "time"
Cohesion: 0.08
Nodes (13): glob, hermes_constants, plugin_api, sqlite3, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —…, v0.7.6 Lane A contracts (Q1 + Q4 + Q8), real runner + tests/fake. Q1 spawn-time… (+5 more)

### Community 11 - "jload"
Cohesion: 0.13
Nodes (27): Explorer V2: one node truth, two readers, act_amend(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), Append mode: runner.log keeps crash diagnostics across respawns. Stamp wf.pid… (+19 more)

### Community 12 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 13 - "test_sprint101w2_C3-fanout-gates.py"
Cohesion: 0.08
Nodes (7): Ctx, Deterministic regressions for explicit workflow provider/model routing., answer(), sprint101 C3 — #12 fan-out ergonomics, #14 gate defaults. #12 fanout.goal…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 14 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _note_turn_tier(), _proc_alive() (+14 more)

### Community 15 - "importlib_util"
Cohesion: 0.10
Nodes (6): importlib_util, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, End-to-end test of the `workflow` tool door against fake hermes., on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, answer(), Regression suite from the mega-review fleet: each test is a mutant that USED to…

### Community 16 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 17 - "log"
Cohesion: 0.16
Nodes (20): _bounded_retry(), log(), now(), Q4 transient retry: re-spawn a failed child at most 2 more times (5 s, 20 s…, #5 bounded auto-retry, run ONCE after _transient_retry: a death whose…, Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique item-field names a fan-out template interpolates: the supported… (+12 more)

### Community 18 - "__init__.py"
Cohesion: 0.16
Nodes (19): difflib, _alias_provider_pair(), _frozen_committed(), handle(), model_tiers(), hermes-workflows plugin — the `workflow` tool: agent-owned graph runs. The…, fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat… (+11 more)

### Community 19 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 20 - "Changelog"
Cohesion: 0.11
Nodes (18): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner (+10 more)

### Community 21 - "sys"
Cohesion: 0.11
Nodes (8): sys, Stub hermes_bin for test_orphan_adopt_790c6ad — the live-orphan repro child.…, Library verbs + /wf command: save (from run_id / inline), library list, run…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn., mk(), A2 + A3 + O1 acceptance (L6): failed/partial nodes ship node_facts beside the…

### Community 23 - "ref_node_fs"
Cohesion: 0.12
Nodes (12): ref_node_fs, ref_node_path, ref_node_url, code, { fanItems, fanCounts }, here, src, [first, second] (+4 more)

### Community 24 - "run_child"
Cohesion: 0.12
Nodes (18): _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract(), _first_message_s(), hermes_home(), _next_spawn_no() (+10 more)

### Community 25 - "_ping_route_once"
Cohesion: 0.12
Nodes (16): _import_call_llm(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the…, Server Retry-After, best-effort via core's parser. None when no header — NEVER… (+8 more)

### Community 26 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 27 - "test_node_click_expand.mjs"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 28 - "Run operations and read model"
Cohesion: 0.12
Nodes (15): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, What you get, Run operations and read model (+7 more)

### Community 29 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 30 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 31 - "act_run"
Cohesion: 0.17
Nodes (15): act_library(), act_list(), act_run(), _card(), _hermes_bin(), _lib_path(), library_root(), _liveness_hint_suffix() (+7 more)

### Community 33 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 34 - "AGENTS.md"
Cohesion: 0.18
Nodes (6): Node budgets, Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data

### Community 35 - "test_tiers.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…, Ctx, Model tiers: node.model accepts a literal id OR a key of the owner's dict…

### Community 36 - "test_metrics_missing_ui.mjs"
Cohesion: 0.17
Nodes (7): ref_node_assert, EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 37 - "test_prompt_workdir.py"
Cohesion: 0.26
Nodes (11): stat, check(), home_and_fakes(), main(), mk_run(), L7 — A1 durable prompt file + A4 durable child work dir. A1: the prompt as sent…, step(), check() (+3 more)

### Community 39 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.23
Nodes (12): check(), contract(), fake_call_llm(), _fake_parse_retry_after(), graph_two_routes(), _raise_import_error(), FEEDBACK #152be7f7: preflight LIVENESS ping — warn-and-surface contract.…, a+b share openai/m-1 (distinct-route dedupe), c rides openai-codex/m-2, d is… (+4 more)

### Community 40 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.18
Nodes (6): datetime, signal, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, start_runner()

### Community 42 - "test_card_frontend_contract.mjs"
Cohesion: 0.18
Nodes (8): ref_node_crypto, ref_node_os, macEvidence, parserSource, plugin, root, temp, testsDir

### Community 43 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 44 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 45 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 46 - "act_save"
Cohesion: 0.25
Nodes (8): act_save(), _coerce_graph(), _input_graph(), The door only ever sees `graph` as a parsed object from the tool schema, but a…, Choose one explicitly supplied source; never discover files on the caller's…, Shelve a graph under a name: from an existing run (`run_id`) or an inline…, Return graph-level and node-level defects together, before any write/spawn., _validation_error()

### Community 47 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 48 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Reasoning levels the (provider, model) route accepts; the global set when the…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 49 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.29
Nodes (6): Catalog rules, checked at the pinned SHA, plugin-catalog: add `hermes-workflows` (community, automation), Relationship to a patched core, `requires_hermes: ">=0.21.4"` — measured, not guessed, Test evidence at the pin, What it is

### Community 52 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 53 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 54 - "Patched core: typed turn-cap deaths (optional)"
Cohesion: 0.33
Nodes (6): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains

### Community 55 - "Exception"
Cohesion: 0.33
Nodes (5): Exception, EscapeLineOnly, HostileStr, KeyLeak, No status attr — str() alone is the oneshot.py:322 escape line (regex path).

### Community 56 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, _steer_event(), _steer_lines()

### Community 57 - "Manual installation — Hermes Workflows 0.9.0"
Cohesion: 0.33
Nodes (6): Backend host, Desktop app machine, Manual installation — Hermes Workflows 0.9.0, Removal, Source-tree verification, Verify and unpack on each machine that needs a component

### Community 58 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 61 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 63 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 64 - "write_spawn_record"
Cohesion: 0.40
Nodes (5): _node_file(), B1 (feedback #13/#40): at spawn, copy every inbox line addressed to this node…, Q1 spawn-time record: written right after Popen succeeds, BEFORE the child is…, _steer_bake(), write_spawn_record()

### Community 65 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 67 - "FakeHTTPError"
Cohesion: 0.50
Nodes (3): FakeHTTPError, _quota_dead_429(), Openai-shaped error: status attr + response.headers carry Retry-After; str() is…

## Knowledge Gaps
- **194 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+189 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 611 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `label()` connect `plugin.js` to `test_card_frontend_contract.mjs`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `amend()` connect `Run operations and read model` to `test_amend_rebake_034849a2.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `What you get` connect `Run operations and read model` to `Hermes Workflows`, `EngineNextCut`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _194 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06538987688098495 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05297532656023222 - nodes in this community are weakly interconnected._
- **Should `EngineNextCut` be split into smaller, more focused modules?**
  _Cohesion score 0.07823613086770982 - nodes in this community are weakly interconnected._