# GX Workflow Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Track the steps below and preserve each task's file ownership.

**Goal:** Implement the user-approved dialogue, routing, final-artifact quality and evaluation improvements and open a PR against main.

**Architecture:** One host-neutral decision contract controls waiting and approval reuse; task-specific workflows retain existing brand and evidence IDs. Quality belongs to an artifact version and observed conditions. A state-aware evaluation path stops guessing which question an answer belongs to; legacy scenarios remain explicitly legacy.

**Tech Stack:** Markdown agent skills, Python standard-library evaluation/tests, dependency-free browser observation JavaScript, local HTML fixtures.

**Spec:** [approved final proposal](../../research/2026-11-04-gx-workflow-final-improvement-proposal.md), including the Swarm Rebuild assessment linked there.

## Global Constraints

- User authorized implementation through PR in this chat; preserve this approval and do not reopen settled choices.
- Keep gx-design/gx-redesign entrypoints, BX/graphics/UI/video/Gemini/.pen/document paths, A/B/C review responsibilities, D/G/S/J/CH IDs and existing stack/brand priority.
- No third-party skill/code vendoring, hooks, mandatory React kit or new package dependency. Swarm Rebuild code has no confirmed reuse license.
- Questions have no arbitrary total cap; required unresolved intent blocks dependent work, optional preference does not become implied approval.
- Report missing evidence as unverified; tests of instructions or simulated runs are not real-model success measurements.
- Work only in this worktree. Do not edit the original checkout or other workers' files. Root coordinates integration; workers do not commit or push.

## Review Focus

- Empty/partial/cancelled/stale asynchronous replies must not unlock a required decision.
- A clear existing approval must not cause another brief/artifact/polish-scope question.
- Old skill text or score criteria must not contradict new audit-only/partial refinement routing.
- A final artifact change or missing required observation must invalidate affected approval claims.
- Eval completion, unexpected questions and incomplete runs must not consume unrelated answers or enter success averages.

## Task 1 — Interaction and routing contracts

**Owner:** interaction worker.
**Files:** HOST-COMPAT, BRIEF-INTERVIEW, DESIGN-TONE-ANCHOR, DESIGN-IT-TWICE, gx-design SKILL, gx-redesign SKILL/REDESIGN-INTERVIEW; tests/test_core_mode_interview.py and new tests/test_dialogue_contract.py only.
**Interface:** host decision record = id/value/status/source/scope-version/dependencies. Link quality/budget documents instead of copying their rules. Root owns README/site/version changes.

- [x] Add focused contract regression checks for resolved intent, scope reuse, waiting and contradictory old clauses; observe expected failures.
- [x] Implement decision/wait semantics, meaningful question wording, request-derived mode, targeted refinement and audit completion, explicit polish ID set.
- [x] Preserve full interviews for genuinely unresolved consequential intent and approved new-work direction selection.
- [x] Run owned tests and report intentional failures in legacy tests owned elsewhere.

## Task 2 — Final artifact and quality contracts

**Owner:** quality worker.
**Files:** PRODUCTION-HANDOFF, REVIEW-AXES, VISUAL-QUALITY, RUN-BUDGET, creative-production/review SKILL, agents/creative-producer.md; tests/test_evidence_based_design_audit.py and new tests/test_final_artifact_contract.py only.
**Interface:** host decision contract in HOST-COMPAT is authoritative; review record references artifact/version/hash/fixture/state/viewport/environment and affected A/B/C axes. Root supplies optional observation/example references.

- [x] Add checks for final-version review, required evidence, scoped Major and total budget; observe expected failures.
- [x] Reuse requested artifact route, separate actual UI/illustration/format per region, preserve prompt-only paths.
- [x] Require final artifact evidence, scope-required Critical/Major resolution, explicit exception/unverified states, impact-based re-review.
- [x] Use minimum one observation with changes only for findings; a single default three-cycle budget includes producer and review fixes.
- [x] Run owned tests and report integration needs.

## Task 3 — State-aware evaluations

**Owner:** evaluation worker.
**Files:** evals/**, tests/test_v012_modes_eval.py, new tests/test_eval_dialogue.py and fixtures under tests/fixtures only.
**Interface:** additive scenario dialogue/checkpoint format with explicit decision id/type/scope version; no auto-generated approval from an unmatched natural-language question. Preserve legacy schema with a visible limitation marker. All new behavior uses stdlib and mocked CLI events for deterministic tests.

- [x] Reproduce blind answer injection and metadata-only snapshot weakness in failing tests.
- [x] Implement matched checkpoint dispatch, completion stop, required wait/partial/unexpected state handling, questionless completion and incomplete stop reasons.
- [x] Hash file contents, retain observed file-change/command event evidence and state their visibility limits.
- [x] Separate dialogue and artifact quality dimensions from legacy procedure scores; incomplete runs must not count as successful averages.
- [x] Add the 21 proposal cases as reviewable scenario fixtures/checks. Distinguish automated harness cases from unexecuted real-model acceptance cases.
- [x] Run eval tests and dry-run commands without paid model invocation.

## Task 4 — Local observation/examples and public guidance

**Owner:** root.
**Files:** new skills/gx-design/scripts/observe-ui.js, two small local examples and usage guide, new observation tests, README, site/index.html copy only, plugin manifests/marketplace, version assertions and any integration tests not owned above.

- [x] Provide read-only bounded DOM/computed-style/repetition-candidate evidence collection in existing browser workflows; no extension install or visual overlay.
- [x] Provide list/filter and form/error contrast fixtures with meaningful worst-case data and comparison guidance; no fixed house style.
- [x] Explain optional Stageshow, Agentation and DialKit paths plus actual UI/illustration boundary and source-license limits in a short on-demand reference.
- [x] Update public workflow copy and both host manifests to 0.14.0; adjust outdated policy assertions to the approved semantics.
- [x] Run observation verification, local link checks, full unittest suite and evaluation dry-runs.

## Task 5 — Independent review and PR

- [x] Review worker changes against the approved proposal, then request a fresh whole-branch review.
- [x] Fix actionable review findings, rerun affected checks, and record honest validation limits in docs/research/2026-11-04-workflow-implementation-validation.md.
- [x] Inspect the final diff, commit Korean feature messages, push codex/gx-workflow-quality and open a PR against main.
- [x] Return the verified PR URL and concise implementation/testing summary. Do not merge or deploy.

## Additional approved steering — elapsed time / entry weight

The user additionally requested reducing long, heavy default execution while this implementation was active. Add core-by-default routing, progressive target-only discovery, unchanged-reference reuse, core recommendation1 plus comparison1 only if useful (explicit counts/full preserved), one orchestrator for small work, risk-based batched evidence, compact logs and runtime measurement. Required intent/wait/final criteria stay unchanged; no claimed wall-time speedup without matched real runs. Browser integration is opt-in so normal unit checks remain fast.

PR: https://github.com/bs-koo/gx-design/pull/18

## Follow-up hardening approved in chat

The user approved all findings and usability recommendations from the additional edge-case review. Update the existing PR; retain version 0.14.0 until this unreleased PR is merged.

- [x] Evaluation owner: reject escaping fixture/result paths before writes; terminate and await the complete process tree on timeout; preserve scored waiting/stopped outcomes separately from successful cost averages; preserve observed usage when later keys are absent. Add executable regression cases, including resume identity changes.
- [x] Observation owner: fix error descriptions through initial/invalid/recovered form states; expose effective opacity and preserve the capture budget for visible elements; bound browser connections and clean up child processes after failure or termination.
- [x] Workflow owner: reconcile brand preservation, partial-polish records, requested devices and actual candidate counts; clarify first versus repeated rejection, concise questions, independent task switching and available deliverables. Extend only missing dialogue acceptance cases.
- [x] Root: add an optional reviewed timing report for first useful turn and rework; distinguish CLI active time from human waiting and total elapsed time. No mandatory product-user instrumentation.
- [x] Root: run independent, isolated model forward checks for unanswered/partial/cancelled decisions, task switching and targeted fixes; record actual outcomes and limits without claiming a production benchmark.
- [x] Root: review changes, run the full deterministic and explicit Chrome suites, validate packaging and dry-runs, update validation evidence, commit and push to PR #18. Do not merge or deploy.

Ownership: evaluation worker owns evals/run_eval.py, evals/score.py, eval tests and the existing eval README; observation worker owns the example/observer/browser tests and observation reference; workflow worker owns skill Markdown except that reference and dialogue fixtures; root owns the optional benchmark module/tests, plans, evidence and PR integration. Shared files are coordinated before edits.

Independent code review additionally reproduced Python 3.10 junction traversal and normal CLI exits being misclassified as timeouts when a child inherited its output pipes. Both failed regression cases were added, fixed, and independently retested. The final Windows suite executes 178 tests, including 13 browser/transport tests, with no failures or skips. See the validation report for the five isolated model samples and the explicit platform/benchmark limits.
