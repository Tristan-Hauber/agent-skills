---
name: pr-fixer
description: Fix validated PR findings and leave the PR updated, pushed, and ready for review.
---

The main thread owns Git lifecycle, evidence state, checkpoints, pushes, PR mutation, and cleanup. Input uses `$pr-review` head SHA, review receipt, and `Q#`/`P#` findings.

1. Resolve current head/base and verify the receipt. On descendant head drift, inspect the delta and affected context before a fresh review; on base movement, force-push/non-ancestry, edited authoritative sources, or unknown freshness, invalidate affected evidence and broaden retrieval. Mark stale/already-fixed findings.
2. Resolve questions from linked context. Preserve unresolved `Please answer:` blocks and stop before mutation.
3. Require a safe tree. Create/register a temporary branch/worktree from the PR head, switch to it, and verify attached `HEAD`; store title/body outside it.
4. Dependency-order current findings. Use one `worker`; per finding/coupled batch run `$adversarial-review-loop checkpoint=commit` with the evidence packet. Post-commit findings become new fix commits; do not amend/reset/rewrite reviewed commits by default. Integrate into the persistent head, validate, push normally, verify remote SHA, and refresh file/diff/validation fingerprints. Never force-push implicitly.
5. Use a fresh reviewer to reconcile title/body with pushed evidence; update and verify remotely.
6. On every exit export recovery patches, remove/prune the worktree, and delete its branch only after proving no unique work remains; retain/report unique work/drafts.

Stop on oscillation or unverifiable state. Do not stop at orientation or known remaining work.

Return `UPDATED/BLOCKED | PR | resolved/stale IDs | commits | validation | review receipt | cleanup | retained work/- | blocker/draft/-`, followed by exact questions.
