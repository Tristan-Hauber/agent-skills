---
name: pr-review
description: Verify that a PR is correct, in scope, adequately validated, and consistent with linked requirements.
---

Review only; do not edit. Tie findings to the remote head SHA. Accept optional verified receipt and `scope=auto|initial|delta|final` (`auto` default). After the review receipt is emitted, automatically run `$github-review-learnings` so settled review learnings are recorded without changing the review result.

1. Verify base/head ancestry, issue/comment/linked-source revisions, repo-instruction hashes, file blobs, checks, and prior cutoff. Initial review maps full base..head diff, comments/threads, rules/docs, and linked decisions. A descendant repeat starts with previous-head..current-head, changed blobs/symbols, and new/edited comments; base movement, force-push/non-ancestry, or unknown freshness invalidates affected evidence. For stacked PRs inspect child-head delta and discussion since any supplied or known review cutoff first; expand unchanged parents for cross-stack contracts, regressions, or uncertainty.
2. Retrieve stat/name-status before hunks, then bounded symbol context; whole files/history only when interactions require it. Target near 1,000 tokens per fragment; split/expand intentionally and never exceed 10,000 unless unavoidable. Keep logs outside context; inject status/failures.
3. Cache evidence, not conclusions. Prepare exact snippets/source IDs/fingerprints, requirements, and expansion permission for child and PR-specific review. Revalidate stale comments/findings.
4. For code/config/resource changes, run `$code-review` on the exact current diff and requirements with verified evidence; preserve its `P#`/`Q#` and receipt. For prose-only/docs-only diffs, run `$artifact-review kind=documentation` on the exact changed artifact/evidence. Separately check PR metadata, discussion, checks, linkage, and stacked/cross-stack correctness. Omit unrelated defects unless worsened/release-blocking.
5. Before `CLEAN`, `scope=final` requires fresh review of the exact complete current base..head diff through the applicable `$code-review` or `$artifact-review` lens, plus fresh PR-specific reasoning over requirements, metadata, discussion, and validation. Unchanged verified bytes may be reused, never old conclusions.

Render `P#` and direct `Q#` under `Please answer:`; never ask for `P#`, emit `NEXT`, or require another invocation. If explicitly requested, use a compact table without weakening P#/Q# evidence semantics.

Output `HEAD | <SHA>` plus findings/questions or `CLEAN`, and a receipt with base/head, source/cutoff fingerprints, inspected paths/ranges, validation, scope, and result IDs.
