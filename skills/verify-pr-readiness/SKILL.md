---
name: verify-pr-readiness
description: Read-only verification that a PR's exact current state is ready to merge.
---

Do not edit, checkout, push, approve, resolve, dismiss, merge, or mutate GitHub. Accept an optional verified review receipt.

1. Always refresh dynamic metadata: exact head/base, state/draft, mergeability, required checks, approvals/dismissal policy, unresolved threads, linked issues, and relevant source fingerprints. Reuse code/requirements evidence only after exact verification; fresh judgement does not require refetching identical bytes.
2. Always run a fresh `$pr-review scope=final` on the exact current head. Any `Q#`/`P#` means `NOT READY`; preserve exact lines and receipt.
3. Run `$evaluate-github-comments` for unresolved threads and new/edited comments since the receipt cutoff. Current `Q#`/`P#` block; `N#` is evidence.
4. Confirm checks passed on this head and matching command/config where applicable, approvals remain valid, conversations are non-blocking, PR is non-draft/mergeable, and base movement has not invalidated review/testing.
5. Confirm final diff/evidence satisfies linked issue criteria, metadata matches, and applicable tests/docs/migration/rollout/compatibility notes exist.
6. Use `BLOCKED` only when state is unknowable; `NOT READY` for known failures. Preserve `Please answer:` and same-session resumption.

Output `READY|NOT READY|BLOCKED | PR | head@SHA | base@SHA | review receipt | checks | approvals | threads | issue | metadata | blockers/-`, followed by exact questions.
