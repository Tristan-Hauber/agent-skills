---
name: create-or-update-pr
description: Create or reconcile a PR from the intended branch without overwriting human context.
---

Input: repository/issue, head, base, `mode=draft|ready`, and optional verified evidence/review receipt. The main thread owns branch, push, evidence state, and GitHub mutations. Do not merge or approve.

1. Use at most one `explorer` for nontrivial repo rules/template, linked context, existing PR, and evidence missing from the receipt. Verify fingerprints; prefer diff metadata and changed hunks before broader reads.
2. Resolve head/base/linkage. If unresolved, make no branch change and ask a direct `Q#` under `Please answer:`; same-session answers resume without `NEXT`.
3. Require a safe tree; switch to the intended head and verify attached `HEAD`. Never stash, discard, or force-push implicitly.
4. Draft from the exact current diff, reusing verified bytes rather than re-emitting them. Never use `[codex]` or another automation title prefix. Fill a new template; for an existing PR preserve relevant human/unknown sections and update only owned standard sections or `<!-- codex-workflow:<section>:start/end -->` regions unless empty, wholly tool-managed, or broader replacement is authorised.
5. Run `$adversarial-review-loop artifact_kind=pr-description checkpoint=save` with the evidence packet until accurate.
6. Push when needed; verify remote SHA and stop on divergence. Prefer GitHub connector/API for PR lookup/mutation; if unavailable/insufficient, fall back to authenticated `gh`. After ambiguous mutation results, re-fetch before fallback to avoid duplicate creation/update. Create/update, then verify head/base, linkage, metadata, state, and SHA. New PRs default draft; change existing draft/ready state only when authorised.
7. Delete the local draft after success; retain it on failure. Avoid worktrees; safely preserve and clean any created one.

Return `CREATED/UPDATED/BLOCKED | PR | head@SHA | base | state | checks | review receipt | cleanup | blocker/draft/-`, followed by exact questions.
