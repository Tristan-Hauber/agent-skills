---
name: deliver-issue
description: Deliver one issue through review, implementation, verification, and a review-ready PR.
---

Input: issue plus `issue_update=ask|auto|never` (`ask` default). The main thread owns decisions, Git/GitHub/evidence state, integration, pushes, and cleanup. Do not merge; respect concurrency.

Continuation gate: an explicit invocation requests execution, not a status report. Reconstruct current issue/repository/branch/commits/worktrees/validation/PR; prior summaries/blocker labels are advisory. Unwritten code, missing tests, and known next steps are work, not blockers. Continue while in-scope work remains without required decision, authority, external dependency, or non-convergence.

Evidence state: keep one atomic manifest with schema `1` under `$(git rev-parse --git-common-dir)/codex-workflow/<repo-id>/<issue-id>/review-state.json`. The main thread alone writes it; subagents return immutable receipts. Store fingerprints/cutoffs, inspected paths/ranges, validation/review receipts—not source bodies, secrets, commands to execute, or trusted conclusions. Before reuse verify issue/comment/linked-source revisions, repo-instruction and file blob hashes, base/head ancestry and diff, worktree diff, and validation command/config. Unknown metadata, edits, base movement, force-push, or mismatches invalidate affected evidence and require broader retrieval. After compaction reread only exact missing ranges. Retain the manifest through the issue/PR lifecycle and report its path.

1. Use at most one `explorer` for evidence absent/invalid in the manifest. Retrieve metadata/stat/name-status first, then changed hunks, symbols, comments after the cutoff, and failures. Require a safe tree; switch to the delivery branch and verify attached `HEAD` before edits.
2. Run `$issue-review` with the verified ledger/receipt; no planning while `Q#`/`P#` remains. Preserve the full `Please answer:` question block; never summarise it, ask the user to answer `P#`, or emit `NEXT`. After answers re-fetch changed context. When an issue edit is needed, separate `Already established:` sourced requirements from `M#` rules under `Proposed decisions requiring approval:`; under `Please choose:` allow natural Approve/Revise/Reject/Recheck. Partial approval is valid only when omitted rules are nonessential or separately resolved. `ask` requires approval; `auto` reviews then applies; `never` does not edit and blocks only when implementation depends on undocumented intent. Apply authorised rules through `$update-issue`. After `UPDATED`, verify remotely, re-fetch, and restart step 2 with a fresh review using verified unchanged evidence; the update is an internal transition, never terminal. Resolve findings or explicit waivers; stop on oscillation. Use `$issue-refinement` for structural incompleteness and `$issue-decomposition` for independent outcomes.
3. Run `$plan-issue-work` from the reviewed ledger. Reconcile any retained branch commits as complete, valid, incomplete, or invalidated; never discard them because review restarted.
4. Execute dependency-ready items. Isolate only concurrently disjoint work; never pre-create dependent worktrees. Start dependants after prerequisites integrate from exact new `HEAD`. Run `$execute-reviewed-item`, integrate clean commits stably, and update fingerprints. Later in-scope defects in committed items become minimal fix items; preserve/restart dependants from resulting `HEAD`; never rewrite reviewed history.
5. Prove reachability before cleanup; export recovery patches, remove/prune worktrees, delete only redundant branches, retain/report unique work.
6. Run `$verify-issue-delivery` with the receipt until clean.
7. Run `$create-or-update-pr mode=draft`, then `$pr-review` → `$update-pr` incrementally until a fresh final exact-head review is `CLEAN`; preserve questions.
8. Run `$create-or-update-pr mode=ready`; finish cleanup.

Return issue/PR status, commits, validation/checks, review-state path/receipt, cleanup, retained work, exact questions, and blockers. Apply the continuation gate before every return.
