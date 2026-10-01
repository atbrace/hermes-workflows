# Graph Report - tree  (2026-10-01)

## Corpus Check
- 183 files · ~254,351 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2070 nodes · 4138 edges · 122 communities (74 shown, 48 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- plugin.js
- wf.py
- wfcommon.py
- sys
- pathlib
- .meta
- test_lane_hygiene_preamble_8edcc9bf.py
- log
- time
- importlib_util
- subprocess
- test_fanout_expand.mjs
- jload
- lane_recover.py
- wf_dialect.py
- plugin_api.py
- test_11_ui_imports.mjs
- _Exporter
- DoorLib50
- runner_alive
- ref_node_fs
- test_sprint101w2_C3-fanout-gates.py
- run_agent_node
- __init__.py
- json
- Changelog
- efp
- test_silent_death_reaper_8.py
- .refuse
- act_run
- ref_node_fs
- test_live_truth_ui.mjs
- test_daemonize_8.py
- _ping_route_once
- test_pill_rail_expand.mjs
- test_tab_polish_48.mjs
- _Importer
- CurrentAttemptMetrics
- 3. Operate
- test_node_panel.mjs
- EngineNextCut
- _create_run
- Changelog
- __init__.py
- _bounded_retry
- AGENTS.md
- SKILL.md
- _input_graph
- test_pill_rail.mjs
- test_require_route_25.py
- PB87
- test_session_strip.mjs
- test_tool_bridge_settings_9c41e2b7.py
- amend
- Disclosure verification — clause-by-clause evidence
- LiveTruth
- test_node_panel.mjs
- test_sprint101_A-door.py
- Run operations and read model
- act_amend
- test_concurrency_retry_knobs_24.py
- FakeHTTPError
- test_require_route_25.py
- test_wfpid_owner_8.py
- _SV
- _Exporter
- test_engine.py
- test_route_efforts_b3c98b2a.py
- test_orphan_adopt_790c6ad.py
- act_save
- test_amend_rebake_034849a2.py
- Contributing to hermes-workflows
- ref_node_url
- graph_check.py
- TeamIntegration
- test_lane_recover_8edcc9bf.py
- FakeHTTPError
- ProvenanceCounters
- DialectRefusal
- test_sprint101w2_B2-retry.py
- _SV
- test_engine.py
- test_routing_routes.py
- test_run_dry_run.py
- model_preflight
- dep_satisfied
- suite.py
- CoreFaithfulCtx
- test_status_next.py
- test_steer_live_40.py
- _fake_parse_retry_after
- Manifest decisions (publish pass, 2026-09-24)
- _bind_run_context
- DoorLane
- Claim
- test_model_law_dad50be0.py
- 11-golden-solo.py
- 11-claim-wrapper.py
- test_papercuts_0922.py
- manifest.json
- dynamic-agent-count.js
- _LADDER
- Integrated
- Run
- .nfs00000000004dfe18000000a8
- date-now.js
- meta-nonliteral.js
- _mask
- args-iterable.js
- args-template.js
- audit-routes.js
- pipeline-glue-stage.js
- pipeline-length-template.js
- dialect/README.md
- sequential-awaits.js
- static-parallel.js
- two-stage-pipeline.js
- unknown-option.js
- while-loop.js

## God Nodes (most connected - your core abstractions)
1. `jload()` - 37 edges
2. `efp()` - 37 edges
3. `run_child()` - 33 edges
4. `DoorLib50` - 27 edges
5. `_Importer` - 27 edges
6. `_Exporter` - 26 edges
7. `log()` - 25 edges
8. `main()` - 24 edges
9. `loop()` - 24 edges
10. `run_state()` - 23 edges

## Surprising Connections (you probably didn't know these)
- `1. Detached runner` --references--> `_spawn_runner()`  [INFERRED]
  docs/catalog/disclosure-check.md → __init__.py
- `3.5 `log(message)`` --references--> `log()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `What the plugin gains` --references--> `_typed_error_class()`  [INFERRED]
  docs/patched-core.md → wf.py
- `7. Plain-JS rule, TypeScript, and loops` --references--> `loop()`  [INFERRED]
  references/anthropic-grammar.md → wf.py
- `Babysitting (read model, not ps)` --references--> `node_rec()`  [INFERRED]
  references/operator-playbook.md → wfcommon.py

## Import Cycles
- None detected.

## Communities (122 total, 48 thin omitted)

### Community 0 - "plugin.js"
Cohesion: 0.05
Nodes (99): 1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail, ago(), api(), attemptNo(), bandRows(), box(), BREATHE, columnGroups() (+91 more)

### Community 1 - "wf.py"
Cohesion: 0.04
Nodes (43): _adopt_child(), _AdoptedHandle, build_inputs(), _cancel_evidence(), _child_spoke(), child_work_dir(), _classify_rc_output(), derived_contract() (+35 more)

### Community 2 - "wfcommon.py"
Cohesion: 0.04
Nodes (43): 1.1.0 — 2026-09-28 — bot-team features: optional `profile` / `requires` / `lane_key` / runs-root / provenance, Owner settings: `runs_root` and `profile` (tool-bridge first-class, #41/#42), current_attempt(), effective_runs_root(), _env_ref_lookup(), _env_ref_var_name(), _expand_config_value(), _m() (+35 more)

### Community 3 - "sys"
Cohesion: 0.04
Nodes (4): rerr(), mk_run(), run_graph(), err_text()

### Community 4 - "pathlib"
Cohesion: 0.07
Nodes (5): Keeper, check(), refuses(), check(), main()

### Community 5 - ".meta"
Cohesion: 0.05
Nodes (37): 10. Permissions, invocation & resume (grammar-adjacent facts), 1.1 Canonical minimal example (verbatim, S1), 1. What a workflow script is, 2.1 Fields documented, 2.2 The static-read law (verbatim, S1 §"Edit a saved script"), 2.3 meta with phases (verbatim, from the Claude-generated cookbook script, S5), 2. The `meta` export block, 3.2 `parallel(tasks)` (+29 more)

### Community 6 - "test_lane_hygiene_preamble_8edcc9bf.py"
Cohesion: 0.08
Nodes (21): excluded(), load_guards(), main(), build(), collect_sources(), main(), _zip_info(), check() (+13 more)

### Community 7 - "log"
Cohesion: 0.08
Nodes (25): _acquire(), gate(), acquire_lock(), emit(), _fail_precondition(), finalize(), log(), main() (+17 more)

### Community 9 - "importlib_util"
Cohesion: 0.06
Nodes (5): main(), until(), fresh(), _v(), Weird

### Community 10 - "subprocess"
Cohesion: 0.06
Nodes (3): GoldenSolo, answer(), make_root()

### Community 11 - "test_fanout_expand.mjs"
Cohesion: 0.07
Nodes (28): badge0, badge1, badgeOf(), box(), calls, coll, { columnGroups: columnGroupsFn, bandRows: bandRowsFn }, def (+20 more)

### Community 12 - "jload"
Cohesion: 0.11
Nodes (19): _release_core(), fixture(), put(), test(), read_children(), state(), _active_spawn(), _active_spawns() (+11 more)

### Community 13 - "lane_recover.py"
Cohesion: 0.10
Nodes (16): apply_patch(), Bail, find_session(), _hermes_home(), journaled_calls(), main(), open_ro(), profile_db() (+8 more)

### Community 14 - "wf_dialect.py"
Cohesion: 0.08
Nodes (16): export_report(), _fmt_goal(), _has_tpl(), js_export(), js_import(), _main(), _match_close(), node_check() (+8 more)

### Community 15 - "plugin_api.py"
Cohesion: 0.10
Nodes (13): _events(), _fold_metrics(), get_node_log(), get_run(), _list_runs(), _node_log_tail(), release_gate(), _root() (+5 more)

### Community 16 - "test_11_ui_imports.mjs"
Cohesion: 0.08
Nodes (25): actual, baseShown, cardBaseline, codeOnly, dropNulls(), EDGE_TONE, $fanItem, FROZEN_BASELINE (+17 more)

### Community 17 - "_Exporter"
Cohesion: 0.14
Nodes (4): _Exporter, _js_literal(), _run_args(), _tpl_escape()

### Community 19 - "runner_alive"
Cohesion: 0.09
Nodes (17): act_release(), act_status(), act_steer(), act_stop(), act_wait(), _respawn_throttled(), _card(), _lane_key_error() (+9 more)

### Community 20 - "ref_node_fs"
Cohesion: 0.20
Nodes (19): _assert_no_fail_closed(), _assert_prompts_carry_own(), cards(), clean_items(), corrupt_items(), fan_graph(), fan_graph_bare(), idx_of() (+11 more)

### Community 22 - "run_agent_node"
Cohesion: 0.10
Nodes (15): _dangling_placeholders(), hermes_home(), _lane_gate(), _route_hold(), _route_home(), run_agent_node(), _cancel_stragglers(), one() (+7 more)

### Community 23 - "__init__.py"
Cohesion: 0.13
Nodes (13): _alias_provider_pair(), handle(), _model_policy_error(), model_tiers(), _owner_setting_read(), _owner_settings_error(), register(), resolve_models() (+5 more)

### Community 25 - "Changelog"
Cohesion: 0.08
Nodes (23): 0.9.0 — 2026-09-24, 1.0.10 — 2026-09-27 — child work dir is writable under HERMES_WRITE_SAFE_ROOT, 1.0.11 — 2026-09-27 — false when-gate defaults to prune (decorative-gate footgun closed), 1.0.16 — 2026-09-28, 1.0.17 — 2026-09-28, 1.0.2 — 2026-09-26 — the run watches itself, 1.0.3 — 2026-09-26 — the feedback fleet's four lane fixes, 1.0.4 — 2026-09-26 — manifest floor matches the fleet (+15 more)

### Community 26 - "efp"
Cohesion: 0.14
Nodes (16): File-authored graphs, Top-level provenance, Portable workflow files (publish = put the file on git), The js dialect seam (#33): `wf_dialect.py`, Walk-in example, nodes(), put(), run() (+8 more)

### Community 28 - ".refuse"
Cohesion: 0.14
Nodes (4): _const_name(), _control_kw(), _forbidden_label(), _line()

### Community 29 - "act_run"
Cohesion: 0.12
Nodes (13): act_library(), act_run(), _from_unknown_error(), _lane_entry(), _lane_paths(), _lib_path(), _lib_read(), _lib_rel_name() (+5 more)

### Community 30 - "ref_node_fs"
Cohesion: 0.11
Nodes (12): macEvidence, parserSource, plugin, root, temp, testsDir, tmp, [first, second] (+4 more)

### Community 31 - "test_live_truth_ui.mjs"
Cohesion: 0.10
Nodes (17): committed, def, detail, fanItems, isBusy, { ItemDetail }, liveDef, nodes (+9 more)

### Community 32 - "test_daemonize_8.py"
Cohesion: 0.13
Nodes (7): alive(), call(), descendants(), _kill(), proc_map(), registry_sweep(), settle()

### Community 33 - "_ping_route_once"
Cohesion: 0.11
Nodes (10): _import_call_llm(), _ping_note(), _ping_reachable(), _ping_retry_after(), _ping_route_once(), _ping_status(), _quota_refusal(), _route_liveness_ping() (+2 more)

### Community 34 - "test_pill_rail_expand.mjs"
Cohesion: 0.11
Nodes (17): clickables, clickIdx, closed, escBlock, escIdx, hasMini(), here, jsxPath (+9 more)

### Community 35 - "test_tab_polish_48.mjs"
Cohesion: 0.10
Nodes (15): CARD_STATES, findBy(), GATE, here, hookSeen, jsxPath, modPath, NODES (+7 more)

### Community 36 - "_Importer"
Cohesion: 0.21
Nodes (3): _Importer, _ordered(), _split_top()

### Community 38 - "3. Operate"
Cohesion: 0.11
Nodes (18): 1. What this is (30 seconds), 2. Install, 2a. Catalog install (stock Hermes), 2b. Remote desktop app, 2c. From a release zip, 2d. Optional: typed turn-cap deaths, 3. Operate, 3a. The loop (+10 more)

### Community 39 - "test_node_panel.mjs"
Cohesion: 0.12
Nodes (14): areas, { Edges, depthMap }, g, grab(), here, jsxPath, loadPlugin(), nodes (+6 more)

### Community 41 - "_create_run"
Cohesion: 0.13
Nodes (9): act_list(), _create_run(), _hermes_bin(), _identity_stamps(), _ready_pid(), runs_root(), _session_env(), _spawn_runner() (+1 more)

### Community 42 - "Changelog"
Cohesion: 0.13
Nodes (13): checkWrap(), cols, { depthMap, columnGroups, bandRows, Edges, CARD_W, MINI }, fan, layout(), many, mini, miniBody (+5 more)

### Community 43 - "__init__.py"
Cohesion: 0.13
Nodes (14): box(), def, fanDef, fanItemsFn, headButton(), here, jsx(), { NodeCard: RealNodeCard } (+6 more)

### Community 44 - "_bounded_retry"
Cohesion: 0.13
Nodes (9): _attempt_api_calls(), _bounded_retry(), _dead_letter(), _tc(), _metered_remaining(), _resume_preamble(), _retry_conf(), _tool_progress() (+1 more)

### Community 45 - "AGENTS.md"
Cohesion: 0.14
Nodes (12): Apply (source install only), Patched core: typed turn-cap deaths (optional), The patch, Verify, What the patch adds, What the plugin gains, Backend host, Desktop app machine (+4 more)

### Community 46 - "SKILL.md"
Cohesion: 0.13
Nodes (7): Node budgets, Contributor checks (not ordinary user setup), Babysitting (read model, not ps), Build-sprint lanes (parallel agent lanes on one repo), Ergonomics, Fleet children (audits, censuses, sweeps), Operator playbook (measured lessons; each one was paid for)

### Community 47 - "_input_graph"
Cohesion: 0.12
Nodes (9): act_inbox(), act_submit(), _coerce_graph(), _inline_graph_size_error(), _input_graph(), _slug(), _steer_lines(), _submit_dir() (+1 more)

### Community 49 - "test_require_route_25.py"
Cohesion: 0.13
Nodes (12): chain, check(), dead, { Edges, depthMap }, failed, nodes, omitted, page (+4 more)

### Community 51 - "test_session_strip.mjs"
Cohesion: 0.12
Nodes (14): empty, here, jsxPath, many, modPath, pm, pmUnknown, reactPath (+6 more)

### Community 52 - "test_tool_bridge_settings_9c41e2b7.py"
Cohesion: 0.17
Nodes (8): _blocker_home(), check(), parity_case(), parity_cfg(), parity_probe(), probe(), yaml_block(), yaml_settings()

### Community 53 - "amend"
Cohesion: 0.13
Nodes (15): 3d. Failures, resume, amend, 1.0.1 — 2026-09-25, Deaths become outcomes, Operator surface, The door validates from lists, The graph carries less, Concurrency and retry knobs (#100), Gates and branches (+7 more)

### Community 54 - "Disclosure verification — clause-by-clause evidence"
Cohesion: 0.13
Nodes (13): 1. Detached runner, 2. Agent-child argv and environment, 3. Machine gate `wait.until_argv`, 4. State location, 5. Network, cron, credentials — the corrected clause, Disclosure verification — clause-by-clause evidence, Catalog rules, checked at the pinned SHA, Disclosure (what the plugin actually does at runtime) (+5 more)

### Community 56 - "test_node_panel.mjs"
Cohesion: 0.16
Nodes (10): activeTabOf(), code, EDGE_TONE, here, jsx(), queries, render(), src (+2 more)

### Community 58 - "Run operations and read model"
Cohesion: 0.15
Nodes (14): For agents and contributors, Hermes Workflows, Install, License, Requirements, Two builds, one codebase, What you get, Lanes: in-flight dedupe for pollers (+6 more)

### Community 59 - "act_amend"
Cohesion: 0.15
Nodes (7): act_amend(), _frozen_committed(), _knob_bake(), _liveness_hint_suffix(), _profile_error(), _require_route_effective(), _route_enforcement()

### Community 60 - "test_concurrency_retry_knobs_24.py"
Cohesion: 0.18
Nodes (4): call(), events(), wait_dead(), widths()

### Community 61 - "FakeHTTPError"
Cohesion: 0.15
Nodes (10): findBy(), here, jsxPath, modPath, reactPath, sdkPath, src, textOf() (+2 more)

### Community 63 - "test_wfpid_owner_8.py"
Cohesion: 0.21
Nodes (6): alive(), cmdline(), _proc_pids(), runners_for(), wait_live(), wfpid_of()

### Community 65 - "_Exporter"
Cohesion: 0.18
Nodes (6): EDGE_TONE, $fanItem, { ItemChips }, src, texts(), walk()

### Community 66 - "test_engine.py"
Cohesion: 0.26
Nodes (7): check(), contract(), fake_call_llm(), graph_two_routes(), _raise_import_error(), set_ping(), submit_run()

### Community 67 - "test_route_efforts_b3c98b2a.py"
Cohesion: 0.18
Nodes (3): core(), Ctx, fake()

### Community 68 - "test_orphan_adopt_790c6ad.py"
Cohesion: 0.20
Nodes (3): env_for(), put_rec(), start_runner()

### Community 69 - "act_save"
Cohesion: 0.18
Nodes (6): act_save(), _concurrency_cap(), _knob_errors(), _model_names_valid(), _tags_error(), _validation_error()

### Community 70 - "test_amend_rebake_034849a2.py"
Cohesion: 0.24
Nodes (4): author(), commit_run(), Ctx, seat()

### Community 71 - "Contributing to hermes-workflows"
Cohesion: 0.20
Nodes (9): Before you push (mechanical gates), Contributing to hermes-workflows, For agents, Issues, License, Review checklist (the maintainer runs exactly this), What happens after you open the PR, What lands fast (+1 more)

### Community 72 - "ref_node_url"
Cohesion: 0.20
Nodes (4): code, { fanItems, fanCounts }, here, src

### Community 73 - "graph_check.py"
Cohesion: 0.40
Nodes (7): _ast(), _dump(), _edge_key(), main(), _norm(), normalize(), sig()

### Community 75 - "test_lane_recover_8edcc9bf.py"
Cohesion: 0.29
Nodes (5): check(), main(), run(), seed(), seed_review()

### Community 76 - "FakeHTTPError"
Cohesion: 0.20
Nodes (5): EscapeLineOnly, FakeHTTPError, HostileStr, KeyLeak, _quota_dead_429()

### Community 78 - "DialectRefusal"
Cohesion: 0.24
Nodes (3): DialectRefusal, _NonLiteral, _Refuse

### Community 82 - "test_routing_routes.py"
Cohesion: 0.32
Nodes (3): Ctx, fake_popen(), FakeProcess

### Community 84 - "model_preflight"
Cohesion: 0.29
Nodes (4): 1.0.5 — 2026-09-26 — preflight LIVENESS ping (warn-and-surface), model_preflight(), _nearest_effort(), _route_efforts()

### Community 85 - "dep_satisfied"
Cohesion: 0.33
Nodes (5): Unreleased, deps_ok(), blocked_by(), dep_satisfied(), deps_ok()

### Community 91 - "_fake_parse_retry_after"
Cohesion: 0.33
Nodes (3): _fake_parse_retry_after(), FRResult, Meta

### Community 92 - "Manifest decisions (publish pass, 2026-09-24)"
Cohesion: 0.33
Nodes (5): (a) requires_env semantics — VERDICT: user-provided env, prompted at install, Author, (b) capabilities block validation — VERDICT: catalog-side is metadata-only; manifest-side is registry-normalized, HERMES_WF_STEER_* decision — VERDICT: NOT in requires_env; requires_env: [], Manifest decisions (publish pass, 2026-09-24)

### Community 93 - "_bind_run_context"
Cohesion: 0.33
Nodes (3): _bind_run_context(), agent_ancestor(), render()

### Community 98 - "11-golden-solo.py"
Cohesion: 0.70
Nodes (3): capture(), main(), normalize()

### Community 99 - "11-claim-wrapper.py"
Cohesion: 0.60
Nodes (3): die(), replace(), write()

### Community 101 - "manifest.json"
Cohesion: 0.50
Nodes (3): api, tab, hidden

### Community 102 - "dynamic-agent-count.js"
Cohesion: 0.50
Nodes (3): byOwner, distinct, meta

## Knowledge Gaps
- **292 isolated node(s):** `.nfs00000000004dfe18000000a8 script`, `HOME`, `api`, `hidden`, `Q` (+287 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1048 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `1.1.1 — 2026-09-29 — runner correctness (cross-container liveness, ancestor gate answers), profile-home fix, lane-clean gate, portable files, pill rail` connect `plugin.js` to `wf.py`, `jload`, `runner_alive`, `__init__.py`, `Changelog`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `useValue()` connect `plugin.js` to `test_fanout_expand.mjs`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `label()` connect `plugin.js` to `.meta`, `ref_node_fs`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **What connects `.nfs00000000004dfe18000000a8 script`, `HOME`, `api` to the rest of the system?**
  _292 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `plugin.js` be split into smaller, more focused modules?**
  _Cohesion score 0.05319355464958261 - nodes in this community are weakly interconnected._
- **Should `wf.py` be split into smaller, more focused modules?**
  _Cohesion score 0.041666666666666664 - nodes in this community are weakly interconnected._
- **Should `wfcommon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04018987341772152 - nodes in this community are weakly interconnected._