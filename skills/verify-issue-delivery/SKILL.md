---
name: verify-issue-delivery
description: Recheck an integrated branch against the issue, fix every delivery gap, and repeat until clean.
---

The main thread owns Git/evidence state, integration, and cleanup. Accept a verified issue decision/ownership ledger/review receipt. Require a safe tree; switch to the integrated branch and verify attached `HEAD`.

Evidence discipline: initial cycle verifies current issue/comments/parent/linked/docs, base, complete diff, rules, and worktree fingerprint. After fixes inspect only the descendant delta, changed blobs/symbol context, affected requirements, and new/edited sources. Base movement, non-ancestry, unknown freshness, or mismatches invalidate affected evidence. Cache exact evidence, not conclusions. Soft-cap each injected fragment near 1,000 tokens; split/expand intentionally and never exceed 10,000 unless no safe alternative exists. Keep logs on disk and inject concise results/failures.

Repeat:

1. Use at most one `explorer` for missing/invalid requirement-to-code/test evidence.
2. Give a fresh high-reasoning read-only reviewer the requirements ledger, exact hunks/snippets/fingerprints, prior open gaps, and permission to expand. Check every `target-owned`/`inherited` requirement; never redefine the issue to fit implementation. Dependencies may block readiness but their deliverables are not target acceptance; `downstream`/`context` do not expand scope unless explicitly assigned to the target. For guards/predicates verify risk-proportionate falsifiable coverage of allowed and disallowed paths. For localisation verify every touched key or documented fallback in every supported locale plus neighbouring/glossary consistency, preserving regional variants.
3. Preserve direct `Q#` under `Please answer:`; same-session answers resume.
4. Output `P#` gaps. If none, run final validation and a fresh final review over the exact complete base..head diff and current requirements; unchanged verified bytes may be reused. Only then return `CLEAN`.
5. Convert gaps into minimal items. If a gap corrects an already committed item, make a new minimal fix item/commit; do not amend/reset/rewrite reviewed commits by default. Group only coupled gaps. Isolate only disjoint work; run `$implement-reviewed-item` with the packet, integrate stably, update fingerprints, and revalidate.
6. Prove reachability, export recovery patches, remove/prune worktrees, delete redundant branches, and retain/report unique work.
7. Stop on recurring/oscillating findings or unverifiable evidence.

Return `CLEAN/BLOCKED | commits | validation | review receipt | cleanup | retained work/- | blocker/-`, followed by exact questions.
