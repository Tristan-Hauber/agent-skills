---
name: quick-code-review
description: |
    Budget-aware code review for the current diff, a pull request, a branch, or a path.
    Prioritises concrete correctness defects, with bounded deeper checks at higher effort.
    Use for a focused review; use a dedicated security, architecture, or full code-review
    workflow when that is the primary request.
---

# quick-code-review

Requires `git`. A pull-request target or GitHub posting also requires an authenticated `gh` CLI.
The optional cost audit uses `jq` when available and reports when it cannot run.

The review's primary objective is to find actionable defects introduced by the target. Secondary
quality findings are allowed only when they are concrete, in scope, and worth a senior reviewer's
attention. Do not optimise for the number of findings.

## Invocation

Accept `low` (default), `medium`, or `high` as a trailing effort level.

Optional flags may appear anywhere:

- `--high-confidence` — report only findings scored 80 or higher.
- `--history` — add bounded history/context checks at `high`; otherwise history is not read.
- `--no-disposable-thread` — keep `high` entirely in the current thread.

Do not unconditionally delegate the whole skill. Review threads are disposable, so delegation is a
selective cost and coverage decision, not a context-preservation requirement.

| Effort | Core review | Additional coverage | Disposable work |
|---|---|---|---|
| `low` | Changed hunks plus necessary enclosing symbols | Obvious contract, state, branch, and CLAUDE.md failures | None |
| `medium` | Low review, then a second correctness pass | Branch/state, sibling implementations, tests, docs, and targeted simplification | None by default |
| `high` | Medium review with adversarial scenarios | Full bounded correctness challenge, architecture/CLAUDE.md reconciliation, optional history | One bounded correctness reviewer when justified |

## Step 0 — preflight and size gate

Run the repository's `scripts/preflight.sh` if present:

- `scripts/preflight.sh diff [<revision-range>] [<path-filter>]`
- `scripts/preflight.sh pr <number>`

Otherwise obtain the same facts with read-only Git/GitHub commands.

Resolve and record:

- target type and exact revision/base/head;
- current branch, worktree state, and whether staged and unstaged changes are both included;
- merge-base with the default branch when reviewing a branch or empty local diff;
- changed files and added/deleted line counts;
- excluded generated, lock, dependency, and project metadata files;
- large touched files (over 400 lines or roughly 16 KB for a remote PR);
- PR draft, closed, already-reviewed, and check status when applicable.

If the target is empty, report that and stop. If a `medium` or `high` review is flagged large,
report the measured scope and ask whether to proceed or use `low`; never silently pay for it.

For a PR, stop before review if it is closed, draft, or already has this reviewer's review/comment,
unless the user explicitly asks to re-review. Do not treat missing or incomplete CI as proof of a
code defect; report it as a validation limit.

## Step 1 — resolve the target and state

- No argument: review staged plus unstaged changes. If empty, review the current branch against its
  merge-base with the default branch.
- A number: treat it as a PR number; fetch its declared base, head, title, body, and diff.
- A branch: compare that branch with its merge-base with the default branch.
- A path: restrict the resolved diff to that path.

Before judging code, verify that the diff being read is the diff being reviewed. For a PR, refresh
the remote metadata or otherwise confirm the current head and base. Note local modifications that
are not part of the PR. Never invent a branch, ref, or default branch name.

## Step 2 — bounded context

List CLAUDE.md files at the repository root and in directories containing touched files. Read their
literal text at every effort level. Do not follow arbitrary references from them at low or medium.
At high, read one directly referenced architecture or layering document only when the changed scope
clearly falls under it.

Read only the context needed to judge a changed hunk:

- the enclosing function, method, type, view, or document section;
- definitions of directly called symbols when their contract determines correctness;
- the relevant test, protocol, model, or persistence boundary when the hunk crosses it;
- one or two sibling implementations when the change claims to generalise or mirror existing
  behaviour.

For a large file, extract the enclosing symbol or section with targeted searches. Do not page through
the whole file. Per touched file, use at most two additional targeted lookups beyond the first
enclosing-symbol extraction. A high-effort disposable reviewer has a total budget of roughly 15
tool calls, excluding the initial diff fetch.

## Step 3 — review passes

### Low: obvious correctness, cheaply

Read every changed hunk and check:

- both sides of every boolean gate, early return, fallback, and optional path;
- changed state transitions, ownership, persistence, cancellation, and lifecycle behaviour;
- empty, nil, duplicate, reordered, boundary, and repeated-use inputs where the hunk handles them;
- changed comments or documentation against the actual code contract;
- whether the diff satisfies literal CLAUDE.md requirements that apply to its files.

Use a confirm-first posture: report a defect only when the changed code and bounded context support
it. Do not search history, prior PRs, or unrelated code. Do not report speculative tests or broad
refactoring ideas.

### Medium: correctness first, then targeted compatibility checks

Run the low pass, then make one separate pass focused on correctness risks that are easy to miss by
reading a hunk once:

1. Construct small concrete inputs or interaction sequences for each changed branch. Evaluate
   predicates in both modes, including the off/default mode; compare empty and populated states.
2. Check the branch/state matrix: initial state, repeated action, cancellation, failure, retry,
   reorder, deletion, restoration, and concurrent or externally refreshed state when relevant.
3. Check sibling implementations and call sites for the same contract. Look for platform variants,
   alternate entry points, duplicated model/view logic, and old/new naming left by a rename.
4. Compare changed tests with the contract they claim to prove. Identify tests that pass while
   bypassing the changed path, assert only setup facts, or omit the branch that exposes the bug.
5. Check touched documentation, localisation, generated/manual parity, and referenced file paths
   only when the diff or CLAUDE.md makes them part of the change.

Then perform a short steelman-and-challenge pass for simplification and architecture. Report only
concrete problems: dead changed code, a clearly unnecessary abstraction, a new reimplementation of
an existing sibling mechanism, or state owned at the wrong layer. Do not report duplication merely
because two short expressions look alike; require a realistic maintenance or correctness consequence.

### High: adversarial correctness with bounded reinforcement

Run the medium pass, then actively attempt to disprove the change:

- enumerate changed branches and create a minimal breaking input for each plausible failure mode;
- test ordering, repeated invocation, partial data, empty data, platform variants, fallback paths,
  failure recovery, and lifecycle boundaries appropriate to the code;
- trace values across the changed boundary into the first consumer that can invalidate the contract;
- compare the implementation with its closest sibling and with the pre-change behaviour;
- check whether tests and comments provide an oracle that the implementation violates.

High is not permission to audit the entire repository. Do not chase unrelated pre-existing defects.

If the diff is non-trivial and `--no-disposable-thread` was not supplied, one fresh disposable review
thread may perform an independent adversarial correctness pass. Give it:

- the exact resolved target and base/head;
- changed-file list and large-file restrictions;
- the surrounding-context and tool-call budgets above;
- the instruction to report only concrete defects introduced by the diff;
- no preliminary findings or desired conclusions.

Do not delegate the preflight, target verification, consolidation, scoring, posting, or cost audit.
If the diff is small, already well covered, or the expected cost is disproportionate, keep the review
inline and record why the disposable pass was skipped.

With `--history`, a separate bounded history pass may inspect only the exact changed lines using
`git blame`, `git log --oneline -L`, and at most five recent relevant PRs. Count line-history results
before fetching patches; if more than eight commits touch the range, read only the most recent five.
Stop after two prior-PR queries with no relevant context. History may explain intent or reveal a
regression contract, but it must not turn pre-existing behaviour into a finding.

## Step 4 — consolidate and score

Consolidate overlapping findings from all passes before scoring. Score each surviving finding from
0–100 for confidence that it is real, introduced by the target, and worth surfacing:

- `0`: false positive or pre-existing; drop it.
- `25`: plausible but unverified, or a minor coverage/documentation gap.
- `50`: verified but minor or uncommon.
- `75`: verified and likely to occur, or explicitly required by applicable CLAUDE.md.
- `100`: directly confirmed and frequent or materially damaging.

Exclude before reporting:

- compiler, typechecker, formatter, or ordinary CI failures;
- unchanged lines and pre-existing defects;
- stylistic nits and speculative redesigns;
- duplication without a concrete maintenance, behavioural, or performance consequence;
- missing tests or documentation unless the omission creates a realistic defect or violates CLAUDE.md.

Security issues introduced by the diff are correctness findings, but this is not a substitute for a
dedicated security review. Keep findings sorted by confidence, include exact file and line locations,
the concrete triggering scenario, impact, and a focused fix direction.

By default report scores 25 and above so the user can see verified minor findings. With
`--high-confidence`, report only 80 and above. If there are more than 20 findings, report the
strongest 20 and state how many were omitted.

## Step 5 — report and cost audit

For `high`, record a timestamp immediately before starting any disposable or history reviewer. After
consolidation and scoring, run `scripts/audit-cost.sh <timestamp>` when available. Include the actual
total effective token figure when reported. If it prints `SKIPPED`, say that the audit was unavailable
without inventing a cost.

Call `ReportFindings` with the surviving findings, or an empty array when none survive. The report
must distinguish:

- findings;
- skipped non-substantive files;
- validation performed and its limits;
- disposable/history passes used or deliberately skipped;
- review cost, when measured.

## Step 6 — posting safeguards

Never post to GitHub unless the user explicitly asks. If posting is requested, show the exact proposed
comment and obtain explicit confirmation immediately before running `gh pr comment`. Do not combine
posting approval with approval for unrelated edits, commits, or fixes.
