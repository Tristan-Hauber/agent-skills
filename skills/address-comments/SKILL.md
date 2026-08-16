---
name: address-comments
description: Evaluate selected GitHub comments, fix valid findings, and reply with verified evidence.
---

The main thread owns orchestration, evidence state, and GitHub mutations. Accept comment URLs/IDs from one issue or PR.

1. Run `$evaluate-github-comments` with any verified receipt; preserve comment IDs, authors, fingerprints, and all `Q#`/`P#`/`N#` dispositions.
2. Resolve questions from current target and linked context. If any remain, preserve `Please answer:`, post nothing, and resume by re-evaluating only affected/new/edited comments unless evidence invalidation requires more.
3. Revalidate against the current issue revision or PR head. Pass the receipt and only current fixer-ready findings to `$update-issue` or `$update-pr`; do not duplicate baseline retrieval or post completion replies after failure.
4. Verify the resulting state, refresh changed fingerprints, re-evaluate changed dispositions, then post one concise response per selected author covering fixes, questions, satisfied/obsolete/duplicate points, and rejected/optional suggestions with evidence. Never claim unverified work.

Do not reply to unrelated authors, mutate unrelated targets, or resolve threads unless requested. Stop on stale/unverifiable state, oscillation, or non-convergence. Do not stop at orientation or known remaining work.

Return target status, evaluation IDs, review receipt, fixer result, response links, exact questions, and blocker/-.
