# codex-github-workflow

Token-light Codex skills for diagnosing, reviewing, promoting, refining, implementing, fixing, and delivering GitHub work.

## Install

```bash
./install.sh --replace
```

Installs to `${CODEX_SKILLS_DIR:-~/.agents/skills}`. The installer validates the bundle before changing the destination.

## Recommended entry points

Start with the smallest workflow matching the current state. Review skills are read-only; fixers and delivery workflows mutate the named target only when explicitly invoked and authorised.

| Situation | Start with | Typical continuation |
|---|---|---|
| Fresh implementation-ready issue | `$deliver-issue <issue>` | Reviews, plans, implements, verifies, creates a PR, and fixes PR findings until review-ready. |
| Rough or incomplete issue | `$issue-refinement <issue>` | Inspect the local proposal; use `mode=update` only when ready to change GitHub. |
| Large issue with independent outcomes | `$issue-decomposition <issue>` | Inspect child drafts; use `mode=create` only when approved. |
| Review an issue without changing it | `$issue-review <issue>` | Post with `$post-github-feedback`, or update with `$update-issue` when authorised. |
| Diagnose an observed defect | `$diagnose-bug <symptom>` | Reproduces and localises the failing boundary; pass the verified `P#` to `$promote-to-issue`. |
| Deliver one bounded work item | `$deliver-work-item On branch <branch>, <item>` | Produces one reviewed, validated commit; no push or PR by default. |
| Create or reconcile a PR | `$create-or-update-pr ...` | Then run `$pr-review`. |
| Review someone else’s PR | `$pr-review <PR>` | Post findings with `$post-github-feedback`; do not mutate their branch without authority. |
| Review code/config/resource changes | `$code-review <diff/branch>` | Checks correctness, scope, design, warnings, localisation, and delegates test credibility. |
| Review changed tests specifically | `$test-review <diff/PR/tests>` | Checks claim fidelity, real boundaries, cohesion, redundancy, and scaffolding value. |
| Review and repair your own PR | `$pr-review <PR>` | `$update-pr`, then repeat review until `CLEAN`. |
| Evaluate issue or PR comments | `$evaluate-github-comments <target>` | Inspect dispositions or use `$address-comments`. |
| Turn a finding or discussion into an issue | `$promote-to-issue <source>` | Deduplicates, refines, reviews, and proposes creation; `mode=create` requires authority. |
| Address selected comments end to end | `$address-comments <comment URLs/IDs>` | Evaluates, fixes, verifies, and replies once per commenter. |
| Check immediately before merge | `$verify-pr-readiness <PR>` | Merge only when it returns `READY`; it never merges. |

### Fresh issue

```text
$deliver-issue <issue>

Possible stop:
- incomplete specification → $issue-refinement <issue>
- independent deliverables → $issue-decomposition <issue>
- unresolved decisions → answer the natural questions under `Please answer:` in the same session
```

### Requirement ownership

`issue-review` classifies material requirements and sources as `target-owned`, `inherited`, `dependency`, `downstream`, or `context`. Only target-owned and inherited requirements define the target's acceptance. Dependencies may block readiness, while downstream/context sources can constrain interfaces or expose risk without silently expanding scope. A missing-acceptance finding must trace ownership to the target or an applicable parent; related terminology or a downstream requirement is not enough. The same ownership ledger is reused by planning and delivery verification.

`deliver-issue` defaults to `issue_update=ask`:

- `ask` — show the exact proposed issue change once before recording material answers.
- `auto` — direct user answers may be recorded and reviewed automatically.
- `never` — never edit the issue; block when a durable semantic decision must be recorded.

A useful answer bundle is simply:

```text
Q1: <answer>
Q2: <answer>
```

No new skill invocation is required. The workflow re-fetches context and resumes automatically. Under `issue_update=ask`, if the decisions need to be recorded in the issue, it shows an exact, editable proposal before mutation. After an approved update verifies, delivery does not stop: it reruns `issue-review` from scratch, reconciles any retained branch commits against the revised issue, and continues automatically.



### Diagnose an observed defect

```text
$diagnose-bug <symptom, expected behaviour, environment, and available reproduction evidence>
```

The skill is read-only by default. It reproduces and minimises the failure, tests competing layer boundaries, and distinguishes symptom, proximate cause, likely root cause, confidence, and ruled-out hypotheses. Passing model tests exclude only the paths they exercise: UI symptoms are separately traced through presentation state, observation/binding, rendering, identity/lifecycle, threading, conditions, and event delivery. Each independently supported defect becomes its own `P#` for `$promote-to-issue`; unrelated causes are never bundled. Temporary probes require approval, isolation, disposable data/services, and cleanup.

### Promote a finding to an issue

```text
$promote-to-issue <P# finding, notes, or discussion/comment URL>
```

The default `mode=propose` verifies current evidence, searches open and recently closed issues and relevant PRs semantically, preserves safe source links, and returns either an existing-target disposition or an exact reviewed issue draft. Natural approval can create it; `mode=create` is explicit creation authority. Creation revalidates source fingerprints and repeats duplicate search to avoid races. Existing issues and originating threads are never changed implicitly.

### Review someone else’s PR

```text
$pr-review <PR>
→ inspect the P# findings and any Q# questions
→ $post-github-feedback <PR> <findings>
```

### Review and repair your own PR

```text
$pr-review <PR>
→ $update-pr <PR> <findings>
→ repeat until $pr-review returns CLEAN
→ human review and CI
→ $verify-pr-readiness <PR>
```

### Review tests directly

```text
$test-review <changed behaviour, tests, seams, or PR>
```

`test-review` is the narrow test-specific read-only review lens. It verifies that names/setup/assertions prove the same behaviour, important production decisions are not injected through test seams, tests remain falsifiable, independently failing contracts are separated, new scaffolding earns its cost, and new tests add semantic coverage rather than duplicate nearby tests. It searches changed/nearby coverage first rather than scanning the whole suite. Intentional overlap or unusual scaffolding should explain *why* only when naming/structure/docs do not already make the benefit clear.

## Question and finding contract

Reviews retain stable IDs but render them for humans rather than as pipe-delimited records.

```text
P1 [high] — Manual reordering breaks with interleaved Deleted slots.
- Evidence: iOS and macOS both map editor-visible positions onto a live-only move projection.
- Consequence: the wrong row can move, the operation can fail out of bounds, or hidden slots can be skipped.
- Required change: make editor reordering preserve retained Deleted slots, or deliberately disable it.
- Validation: cover Live/Deleted interleavings on both platforms.

Please answer:
- Q1 (for P1): How should Deleted setlist slots interact with manual reordering?
  - Options: disable reordering while Deleted slots exist; or define moves over the complete stored order while displaying Deleted slots in the editor.
  - Recommendation: use the complete stored order so retained slots remain stable.
```

## Issue-update proposal contract

When user answers must be recorded in an issue, the workflow distinguishes sourced requirements from new proposed rules:

```text
Already established:
- Restore Song and Remove from Setlist are in scope. Source: parent issue #338.

Proposed decisions requiring approval:
- M1: Viewer drops use the live projection and preserve hidden Deleted slots.
- M2: Editor moves use the complete retained order, including Deleted slots.

Please choose:
- Approve: apply all, or named, M# rules and continue.
- Revise: name an M# and give replacement wording or intent.
- Reject: leave the issue unchanged and remain blocked on that decision.
- Recheck: inspect the parent, linked items, relevant code, and documentation again before proposing revised rules.
```

Natural replies are accepted, for example: `looks good`, `approve M1 but revise M2`, `remove M3`, or `recheck the viewer-drop rule`. A materially revised proposal is shown once more before mutation; trivial copy edits should not create a repetitive confirmation loop.

An approved issue update is an internal workflow transition, not a delivery result:

```text
apply and verify issue update
→ re-fetch issue, comments, parent, links, and docs
→ rerun issue-review from scratch
→ reconcile existing commits against the revised contract
→ continue planning and implementation
```

The workflow must not stop at `Issue updated` or merely describe the next implementation when it can continue in the current session.

Comment evaluation may also emit:

```text
N# | comment source(s) | disposition | evidence
```

Rules:

- Before asking, search the current item, all relevant comments, parent, relationship-bearing linked issues/PRs, and pertinent project documentation.
- Never replace a direct `Q#` with a vague blocker topic.
- `P#` identifies a defect; `Q#` identifies a decision. Never ask the user to “answer P#”.
- Questions must be directly answerable and include context, concrete options when known, and a justified recommendation when useful.
- The question itself is the next step. Do not add a mechanical `NEXT` section or command syntax when the current workflow can resume from the answer.
- State a separate natural follow-on only when a new command, explicit mutation authority, or durable source-of-truth update is genuinely required.
- For a proposed issue edit, use stable `M#` IDs and offer approve, revise, reject, and recheck paths; never force an all-or-nothing magic reply.
- Material answers are recorded in the issue when authorised, then the complete issue review runs again before implementation. A parent delivery workflow must continue automatically after the update verifies.
- Findings are revalidated against the current issue revision or PR head before fixing or posting.

## Top-level workflows

- `deliver-issue`
- `deliver-work-item`
- `issue-refinement`
- `issue-decomposition`
- `verify-pr-readiness`
- `promote-to-issue`
- `diagnose-bug`

## Reusable bricks

- `plan-issue-work`
- `execute-reviewed-item`
- `adversarial-review-loop`
- `artifact-review`
- `code-review`
- `test-review`
- `verify-issue-delivery`
- `issue-review`
- `update-issue`
- `pr-review`
- `update-pr`
- `evaluate-github-comments`
- `address-comments`
- `post-github-feedback`
- `create-or-update-pr`

Every skill is explicit-only. Use `$skill-name`; no workflow in this catalogue may begin external writes through implicit matching.

## Specialised review lenses

The review stack is composed rather than monolithic:

```text
pr-review → code-review → test-review                 (code/config/resource diffs)
pr-review → artifact-review kind=documentation        (prose/docs-only diffs)
adversarial-review-loop → code-review → test-review   (code/config/resource scopes)
adversarial-review-loop → artifact-review             (typed prose artifacts)
```

`adversarial-review-loop` is now pure review/fix orchestration: specialised lenses own fresh judgement. `artifact-review` applies a shared evidence-fidelity/cohesion/rationale contract with typed `issue-draft`, `pr-description`, and `documentation` lenses; issue/PR callers pass the kind when already known. It consumes verified evidence rather than becoming another contextual GitHub traversal: `$issue-review` still owns full issue state, and `$pr-review` still owns PR metadata/discussion/stack correctness. `code-review` owns code-wide principles and final-net-diff scope hygiene; `test-review` owns test-specific claim fidelity, falsifiability, real production boundaries, cohesion, scaffolding value, and semantic duplicate coverage. Each child is refreshed only when its evidence domain changes, with fresh complete-state reasoning before final `CLEAN`.

Create a separate review skill when a sub-area has recurring failure modes **and** distinct evidence/retrieval needs. Otherwise keep the principle in the nearest common lens. Fidelity, cohesion, abstraction value, semantic redundancy, and durable rationale overlap across manifestations, but the evidence needed to judge code, tests, and prose differs; they therefore live in `code-review`, `test-review`, and `artifact-review` rather than a universal meta-skill. Scope hygiene stays inside `code-review` because it uses the same final diff and does not justify a separate pass.

Localisation, concurrency, security/privacy, migrations/data integrity, and API compatibility remain candidate lenses. Split one out only after repeated evidence shows the compact `code-review` rule is insufficient or a focused retrieval strategy can materially save context.

## Agent roles and token control

- Main thread: decisions, Git/GitHub mutation, integration, pushes, and cleanup.
- `explorer`: targeted read-only mapping; use at most one by default.
- `worker`: bounded implementation or draft fixing.
- Fresh high-reasoning `default`: independent read-only adversarial review.
- Parallelise only truly independent high-risk or read-heavy lanes; do not spawn agents for trivial work.
- Stop rather than loop indefinitely when findings recur unchanged, fixes oscillate, reviewers conflict, or validation cannot converge.

## Commit units, dependencies, and agent waves

Issue delivery separates three decisions that must not be conflated:

1. **Semantic commit units** — coherent repository states that can be reviewed and focusedly validated after their prerequisites. Tests/docs normally travel with the behaviour they establish.
2. **Dependency graph** — ordering between those units. Sequential units may touch the same files or symbols.
3. **Execution waves** — currently ready units that may run concurrently only when their active ownership is disjoint.

`plan-issue-work` derives them in that order. Parallelisability never decides whether work deserves one or several commits. A nontrivial issue planned as one item needs a substantive single-item rationale; shared files, shared subsystem, sequentiality, or inability to parallelise are not enough. Dependent workers/worktrees are started only after prerequisite commits integrate, from the new exact `HEAD`.

Each planned item still follows `execute-reviewed-item`: implement → strong review/fix → validation → one final commit. Findings found before that commit remain inside the item. If later implementation or review discovers an in-scope defect in an already established commit, delivery creates a new minimal fix item/commit rather than rewriting reviewed history by default. Coupled defects may share one fix item; commit count is an outcome, not a target.

## Input and evidence reuse

`deliver-issue` owns a small review-state manifest under the repository Git common directory. It records fingerprints, cutoffs, inspected locations, validation receipts, and review receipts—not source bodies or trusted conclusions. Reviewers verify fingerprints before reuse, fetch only changed/new/edited evidence between cycles, and still perform fresh final reasoning over the exact complete current diff/state before `CLEAN`.

Retrieval proceeds from metadata/stat/name-status to changed hunks and affected symbols; whole files, histories, or logs are expanded only when required. Evidence fragments target roughly 1,000 tokens, with deliberate splitting/expansion and a 10,000-token per-fragment hard guard unless no safe alternative exists. Full logs stay on disk. See [`INPUT-EFFICIENCY-REVIEW.md`](INPUT-EFFICIENCY-REVIEW.md). Dependency freshness follows the same rule: verify only readiness/acceptance-critical references metadata-first, and expand linked diffs only when bounded evidence cannot establish what shipped or a cross-item contract needs implementation detail. `code-review` judges the final net diff without loading intermediate commits merely to hunt partial-revert residue. `test-review` searches changed and nearby semantically related tests first; it never scans the full suite merely to look for duplicates. `artifact-review` reads the artifact first and expands only bounded source evidence needed for material claims; issue/PR drafts reuse the packet already assembled by their owning workflow rather than rereading linked graphs or diffs.

## Legacy local-skill consolidation

Earlier standalone local skills can be retired once their useful behaviour is represented here. Remove same-name skills from other Codex skill directories to avoid precedence ambiguity.

- old `code-review` → `code-review` (now includes changed lifecycle/retention/cleanup and source-anchor checks)
- old `issue-review` → `issue-review` (retains a bounded established-Swift-architecture check)
- `adversarial-review` → `code-review` / `pr-review` (explicit compact-table output remains available)
- `adversarial-auto-fixer` → `adversarial-review-loop` / `update-pr` / `deliver-work-item`
- `gh-address-comments` → `evaluate-github-comments` / `address-comments` (selected PR thread state is preserved; GraphQL is used only when flat comments are insufficient)
- `yeet` → `create-or-update-pr` / `deliver-work-item` (connector/API first, safe authenticated `gh` fallback, remote revalidation)
- `repository-workflow` → `deliver-work-item` / `execute-reviewed-item` (pre-existing dirt and one-logical-unit rules are explicit)

The catalogue intentionally keeps its no-`[codex]` PR-title rule.

## Runtime prompt budget

The validator caps the 22 runtime skill files at 6,245 words, `deliver-issue` at 500 words, the eight evidence-heavy review/diagnostic skills at 350 words, other skills at 280 words, and descriptions at 18 words. The current catalogue uses 6,197 words. The ceiling is roughly 5% above the reviewed baseline and remains a drift guard, not an optimisation target. `artifact-review`, `code-review`, `test-review`, `promote-to-issue`, and `diagnose-bug` are selectively loaded rather than universal prompt cost. See [`TOKEN-REVIEW.md`](TOKEN-REVIEW.md).

A skill reaching **90% of its cap** triggers a recorded keep/compress/split architecture decision; it does not automatically require splitting. Adding/removing a skill or changing the skill call graph requires a fresh catalogue architectural review before validation passes. See [`ARCHITECTURE-REVIEW.md`](ARCHITECTURE-REVIEW.md).

## Safety invariants

- Switch to and verify the intended branch before changes.
- Revalidate review findings against current state before fixing.
- Temporary worktrees and safely redundant temporary branches are closed on every exit.
- Export a recovery patch before removing a worktree with uncommitted changes.
- Retain and report branches containing unique unintegrated commits.
- `execute-reviewed-item` and `deliver-work-item` create exactly one commit only after all review cycles are clean and final validation passes.
- Generated or reconciled PR titles never use `[codex]` or another automation prefix.
- Existing human-authored issue/PR content is reconciled rather than blindly replaced.
- `verify-pr-readiness` always performs a fresh PR review against the exact current head.

## Validate

```bash
./validate.sh
```

The behavioural review is recorded in [`ADVERSARIAL-REVIEW.md`](ADVERSARIAL-REVIEW.md); prompt-size measurements are in [`TOKEN-REVIEW.md`](TOKEN-REVIEW.md), and the content-ingestion review is in [`INPUT-EFFICIENCY-REVIEW.md`](INPUT-EFFICIENCY-REVIEW.md).
