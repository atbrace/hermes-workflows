# Graph Report - tree  (2026-09-28)

## Corpus Check
- 99 files · ~132,882 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 1171 nodes · 2325 edges · 75 communities (58 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 140 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- plugin_api.py
- wfcommon.py
- plugin-catalog: add `hermes-workflows` (community, automation)
- pathlib
- test_fanout_expand.mjs
- CurrentAttemptMetrics
- subprocess
- wf.py
- sys
- test_fanout_item_goal.py
- main
- jload
- test_lifecycle_next_cut_0923.py
- _adopt_child
- test_card_frontend_contract.mjs
- run_child
- test_live_truth_ui.mjs
- test_register_surface.mjs
- test_preflight_liveness_152be7f7.py
- __init__.py
- test_canvas_wrap.mjs
- efp
- run_agent_node
- json
- test_edge_routing.mjs
- test_session_strip.mjs
- importlib_util
- act_amend
- CardBackend
- EngineNextCut
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- Changelog
- test_orphan_adopt_790c6ad.py
- _ping_route_once
- _resolve_models
- test_deleted_cwd_resume_5c37b19.py
- test_metrics_missing_ui.mjs
- test_amend_rebake_034849a2.py
- test_node_facts.py
- Contributing to hermes-workflows
- test_fanout_ui.mjs
- _spawn_runner
- test_sprint101w2_B2-retry.py
- amend
- node_facts
- test_engine.py
- model_preflight
- test_failures_0923.py
- test_review_fixes.py
- test_sprint101w2_C3-fanout-gates.py
- test_sprint101w2_D2-steer-liveness.py
- test_status_next.py
- test_steer_live_40.py
- Manifest decisions (publish pass, 2026-09-24)
- act_inbox
- Hermes Workflows
- test_tiers.py
- test_v3_fixes.py
- child_metrics
- Run operations and read model
- test_papercuts_0922.py
- test_papercuts_0922b.py
- set_ping
- test_safe_root_workdir.py
- test_validator_caps.py
- manifest.json
- .states
- Integrated
- FakeProcess
- write_runner_exit
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
- `4. State location` --references--> `runs_root()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `4a. Map` --references--> `efp()`  [INFERRED]
  AGENTS.md → wfcommon.py
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface)` --references--> `model_preflight()`  [INFERRED]
  CHANGELOG.md → __init__.py

## Import Cycles
- None detected.

## Communities (75 total, 17 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.07
Nodes (85): ago(), api(), attemptNo(), bandRows(), box(), columnGroups(), ctxRest(), defaultTabFor() (+77 more)

### Community 1 - "plugin_api.py"
Cohesion: 0.05
Nodes (52): argparse, _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), Dashboard backend for hermes-workflows — thin projection of the SHARED read… (+44 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.06
Nodes (37): shlex, _active_spawn(), amend_preview(), apply_graph_defaults(), current_attempt(), _defaults_errors(), _downstream(), quote_json_parse_error() (+29 more)

### Community 3 - "plugin-catalog: add `hermes-workflows` (community, automation)"
Cohesion: 0.05
Nodes (39): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+31 more)

### Community 4 - "pathlib"
Cohesion: 0.10
Nodes (18): contextlib, copy, os, pathlib, tempfile, Authoring door regressions; all state stays in this worktree, no…, Regression: launch a run in the tool's session; the payload carries a parser-…, Current-attempt heartbeat with real fake child identity; no provider access. (+10 more)

### Community 5 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 6 - "CurrentAttemptMetrics"
Cohesion: 0.16
Nodes (9): Contributor checks (not ordinary user setup), File-authored graphs, Gates and branches, Graph grammar and authoring boundaries, Nodes and data, Run and handoff, Smallest working graph, Workflow authoring (1.0.11) (+1 more)

### Community 7 - "subprocess"
Cohesion: 0.08
Nodes (10): Serial bounded suite with durable per-case logs and atomic exit ledger. The…, shutil, subprocess, Item #77 (verb-roadmap/artifact-recovery): every node.failed EVENT must carry…, graph_check.py contract: committed graph ⇔ tree, both directions, plus the…, v0.7.3 `inputs:` node field: runner injects a `## Inputs` section (one labelled…, Sprint101 lane C2-prompt: #9 JSON contract derived from the node schema — when…, run_graph() (+2 more)

### Community 8 - "wf.py"
Cohesion: 0.10
Nodes (24): concurrent_futures, fcntl, build_inputs(), drain_inbox(), extract_json(), _inputs_block(), last_balanced_object(), _match_object() (+16 more)

### Community 9 - "sys"
Cohesion: 0.09
Nodes (15): glob, hermes_constants, plugin_api, sqlite3, sys, _fake_state_row(), Fake hermes chat for wf.py engine tests. Usage: fake_hermes.py chat --query-…, Register this child's --continue session title in state.db with n api calls —… (+7 more)

### Community 10 - "test_fanout_item_goal.py"
Cohesion: 0.20
Nodes (26): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+18 more)

### Community 11 - "main"
Cohesion: 0.12
Nodes (25): acquire_lock(), _bounded_retry(), emit(), finalize(), hermes_home(), log(), main(), consume_markers() (+17 more)

### Community 12 - "jload"
Cohesion: 0.15
Nodes (22): act_list(), act_release(), act_status(), act_steer(), act_stop(), act_wait(), Strict: no silent normalization — ids double as directory names., Explicit resume/watch verb. Read-only status/list never spawn; wait may resume… (+14 more)

### Community 13 - "test_lifecycle_next_cut_0923.py"
Cohesion: 0.08
Nodes (5): Lifecycle regressions: fresh exits, truthful steering, retry evidence, final…, sprint101 B1 — #3 typed error_class on every failure (closed set) and #7 stop…, Regression suite for signoff-v4 must-file items (v5). Each test must FAIL on…, P4 + P1 (blind-jury form, 2026-09-23): machine-answered gates and blocked_by.…, threading

### Community 14 - "_adopt_child"
Cohesion: 0.09
Nodes (22): _adopt_child(), _AdoptedHandle, _classify_rc_output(), _harvest_cancelled(), _harvest_death(), _kill_adopted(), _log_recent(), _proc_alive() (+14 more)

### Community 15 - "test_card_frontend_contract.mjs"
Cohesion: 0.11
Nodes (17): ref_node_assert, ref_node_crypto, ref_node_fs, ref_node_os, ref_node_url, macEvidence, parserSource, plugin (+9 more)

### Community 16 - "run_child"
Cohesion: 0.10
Nodes (22): _cancel_evidence(), _child_spoke(), child_work_dir(), derived_contract(), _first_message_s(), _next_spawn_no(), _node_file(), _note_turn_tier() (+14 more)

### Community 17 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 18 - "test_register_surface.mjs"
Cohesion: 0.11
Nodes (16): areas, ctx, { Edges, depthMap }, g, grab(), here, jsxPath, modPath (+8 more)

### Community 19 - "test_preflight_liveness_152be7f7.py"
Cohesion: 0.15
Nodes (16): Exception, check(), contract(), EscapeLineOnly, _fake_parse_retry_after(), FakeHTTPError, graph_two_routes(), HostileStr (+8 more)

### Community 20 - "__init__.py"
Cohesion: 0.22
Nodes (16): difflib, act_library(), act_run(), _card(), _hermes_bin(), _lib_path(), library_root(), model_tiers() (+8 more)

### Community 21 - "test_canvas_wrap.mjs"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 22 - "efp"
Cohesion: 0.16
Nodes (17): Drop a run dir, optionally pre-commit nodes/<id>.json records, run wf.py to…, run_graph(), make_run(), Create the run dir through the door with the runner spawn suppressed, then…, park_gate(), answer(), mirror(), Park on gate.wait in-process: timer (wait_s) and/or a fixed argv check re-run… (+9 more)

### Community 23 - "run_agent_node"
Cohesion: 0.15
Nodes (15): _dangling_placeholders(), fmt_goal(), Child session key: wf:<run>:<node>[:<i>]:<efp8>.<nonce>. The key is a LABEL for…, NEVER raises: any unexpected error is committed as a node failure so the wave…, Ordered unique '{NAME}' tokens that survived rendering and resolve to NOTHING…, Ordered unique item-field names a fan-out template interpolates: the supported…, run_agent_node(), _cancel_stragglers() (+7 more)

### Community 24 - "json"
Cohesion: 0.12
Nodes (4): json, Door-copy pins for the fan-out quorum blurb (fb 2f9653b1cc98a4e0) and its lane-…, Lane C1-defaults: #8 run-level `defaults:` wired at the door (validated + baked…, Regression suite for sign-off-v3 must-file items (v4): each test must FAIL on…

### Community 25 - "test_edge_routing.mjs"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 26 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 27 - "importlib_util"
Cohesion: 0.13
Nodes (6): importlib_util, Feedback #72: schemas may declare type "boolean". (1) validate_graph_errors…, on_skip:'prune' (2026-09-23): a false `when` on a prune gate commits `skipped`;…, mk_run(), Sprint-101 lane D-surface, item #15 (O1-trimmed, 1.1): the inline card is…, Hand-built committed run dir so act_wait/act_status need NO runner spawn.

### Community 28 - "act_amend"
Cohesion: 0.14
Nodes (15): act_amend(), act_save(), _coerce_graph(), _frozen_committed(), _input_graph(), _liveness_hint_suffix(), fb 034849a23af94418: ids whose committed bake an amend keeps verbatim — ONLY…, The door only ever sees `graph` as a parsed object from the tool schema, but a… (+7 more)

### Community 32 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 33 - "test_sprint101_A-door.py"
Cohesion: 0.15
Nodes (6): atexit, importlib, Ctx, FEEDBACK #43: model preflight at run/amend submit time, before the first wave.…, Ctx, SPRINT-101 Lane A-door: the door validates (model, provider, reasoning) from…

### Community 34 - "Changelog"
Cohesion: 0.14
Nodes (13): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — catalog maintainer review, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet, 1.0.6 — 2026-09-26 — suite ledger resets; fanout grammar named, 1.0.7 — 2026-09-27 — door quorum blurb matches the runner, 1.0.8 — 2026-09-27 — quorum cancels never fire blind (+5 more)

### Community 35 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.15
Nodes (8): datetime, signal, env_for(), put_rec(), 790c6ad — live-orphan adoption on a respawned runner. Forensic shape (waveA3):…, All per-item spawn records with a live pid, once every item is RUNNING., read_children(), start_runner()

### Community 36 - "_ping_route_once"
Cohesion: 0.14
Nodes (13): _import_call_llm(), _ping_note(), _ping_retry_after(), _ping_route_once(), _ping_status(), Call-time lazy core import (rule 7: stdlib at import time; host imports lazy…, Best-effort HTTP status of a ping failure: the SDK attribute first, then the…, Server Retry-After, best-effort via core's parser. None when no header — NEVER… (+5 more)

### Community 37 - "_resolve_models"
Cohesion: 0.21
Nodes (12): _alias_provider_pair(), (provider, model) the alias/tier TARGET names — 'provider/model'-prefixed seat…, Resolve tier keys in place and return (error, model_table, routes). Explicit…, Compatibility wrapper: resolve models and return the historical (error, table)…, The seat's `model:` block ({default, aliases}) — hermes_cli when importable,…, Names the seat itself resolves for -m: model aliases + the default model., resolve_models(), _resolve_models() (+4 more)

### Community 39 - "test_metrics_missing_ui.mjs"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 40 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (6): author(), commit_run(), Ctx, fb 034849a23af94418: an amend must not re-resolve already-committed nodes…, Commit a run the way act_run does (defaults + resolve) under the DEFAULT seat;…, seat()

### Community 41 - "test_node_facts.py"
Cohesion: 0.22
Nodes (5): asyncio, fastapi, call(), expect404(), O2 backend acceptance (L4): wfcommon.node_facts, the /runs/{id}/nodes/{nid}/log…

### Community 42 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 43 - "test_fanout_ui.mjs"
Cohesion: 0.20
Nodes (5): ref_node_path, code, { fanItems, fanCounts }, here, src

### Community 44 - "_spawn_runner"
Cohesion: 0.22
Nodes (9): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, handle(), Append mode: runner.log keeps crash diagnostics across respawns. Stamp wf.pid… (+1 more)

### Community 45 - "test_sprint101w2_B2-retry.py"
Cohesion: 0.22
Nodes (3): Sprint101 Lane B2-retry contracts (#5 bounded auto-retry, #4 harvest-on-death).…, Spawns for a run = child log files the runner wrote (logs/<node>.a<N>.log); the…, spawns_of()

### Community 46 - "amend"
Cohesion: 0.25
Nodes (8): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, What you get, amend()

### Community 47 - "node_facts"
Cohesion: 0.25
Nodes (8): 1.0.2 — 2026-09-26 — the run watches itself, Additions, Archify: no (verdict + evidence), SMIL for candy, Explorer V2: one node truth, two readers, Launching is showing (no agent control), WORKFLOWS beside SESSIONS | BOTS, node_facts(), Record facts for one node (fan-out item via `index`), plus its steer truth.…

### Community 48 - "test_engine.py"
Cohesion: 0.25
Nodes (3): answer(), Engine test: sequential, fanout, gate hold/release/resume, replay-skip,…, Stamp the gate answer with the CURRENT gate efp, like the door's release does.

### Community 49 - "model_preflight"
Cohesion: 0.29
Nodes (7): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), Reasoning levels the (provider, model) route accepts; the global set when the…, Nearest supported ladder level (weaker first — never an escalation), or None., Pure (no I/O): the FEEDBACK #43 model preflight, run at run/amend submit time…, _route_efforts()

### Community 55 - "test_steer_live_40.py"
Cohesion: 0.29
Nodes (3): mk(), B1 cooperative steer (feedback #13/#40) — the file protocol and cursor, proved…, Hand-built run dir with run.json meta pinning hermes_bin to the fake — WITHOUT…

### Community 56 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 57 - "act_inbox"
Cohesion: 0.33
Nodes (6): act_inbox(), Return (texts, n_pulled) for baked steering lines beyond this spawn's cursor,…, B1 (feedback #13/#40): the child's own pull of late steering. Runs IN THE CHILD…, #17: steer is only real if it lands in events.jsonl — the 45 real steers across…, _steer_event(), _steer_lines()

### Community 58 - "Hermes Workflows"
Cohesion: 0.33
Nodes (6): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase

### Community 61 - "child_metrics"
Cohesion: 0.33
Nodes (6): _attempt_api_calls(), api_calls for ONE dead attempt via the state.db join. Return an integer only…, Tool-progress evidence for the #5 bounded retry: True only when the dead…, _tool_progress(), child_metrics(), {skey: {tokens_in, tokens_out, cache_read, reasoning, api_calls, tool_calls,…

### Community 62 - "Run operations and read model"
Cohesion: 0.40
Nodes (4): Run operations and read model, Small, parent-gated escalation recipe (no new engine feature), blocked_by(), P1 (jury form): the NEAREST unfinished ancestors of a pending node, each with…

### Community 65 - "set_ping"
Cohesion: 0.40
Nodes (5): fake_call_llm(), call_llm(), _raise_import_error(), behavior=None restores the non-core host (import raises); dict stubs the…, set_ping()

### Community 66 - "test_safe_root_workdir.py"
Cohesion: 0.70
Nodes (4): check(), main(), fb 625a3241cfcc9dee — the child's advertised durable work dir is writable under…, run_graph()

### Community 67 - "test_validator_caps.py"
Cohesion: 0.40
Nodes (3): err_text(), fb-validator-duo (2026-09-26): the validator-cap duo + the manifest-clip pin.…, All rejection strings of a _validation_error payload, joined.

### Community 68 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 69 - ".states"
Cohesion: 0.67
Nodes (3): deps_ok(), dep_satisfied(), deps_ok()

### Community 72 - "write_runner_exit"
Cohesion: 0.50
Nodes (4): Write one verdict per runner process, tied to the graph snapshot it ran. An…, write_runner_exit(), graph_fingerprint(), Stable signature of the node definitions that a runner verdict describes.

## Knowledge Gaps
- **188 isolated node(s):** `api`, `hidden`, `Q`, `TERMINAL`, `$selRun` (+183 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 605 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Disclosure verification — clause-by-clause evidence` connect `_spawn_runner` to `plugin.js`, `plugin-catalog: add `hermes-workflows` (community, automation)`?**
  _High betweenness centrality (0.393) - this node is a cross-community bridge._
- **Why does `6. Desktop gate answer (maintainer ask #122099, teknium1)` connect `plugin.js` to `_spawn_runner`?**
  _High betweenness centrality (0.377) - this node is a cross-community bridge._
- **What connects `api`, `hidden`, `Q` to the rest of the system?**
  _188 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06511627906976744 - nodes in this community are weakly interconnected._
- **Should `plugin_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.054354178842782 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.058279370952821465 - nodes in this community are weakly interconnected._
- **Should `plugin-catalog: add `hermes-workflows` (community, automation)` be split into smaller, more focused modules?**
  _Cohesion score 0.04541062801932367 - nodes in this community are weakly interconnected._