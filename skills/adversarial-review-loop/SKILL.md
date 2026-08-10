---
name: adversarial-review-loop
description: Review and fix one bounded change repeatedly until it is clean and validated.
---

Input: scope, requirements, validation, fixer workspace, optional verified receipt, `artifact_kind=auto|issue-draft|pr-description|documentation|other`, `checkpoint=commit|commit+push|save|none`. Main thread owns orchestration/evidence/checkpoints.

Evidence: verify fingerprints before reuse; cache evidence, not conclusions. Give child reviewers exact snippets/source IDs/fingerprints/open findings and expansion permission. Retrieve deltas before affected context; whole files/history only for interactions. Keep fragments near 1,000 tokens and below 10,000 unless unavoidable; full logs stay on disk.

Repeat until clean:

1. Use at most one `explorer` when useful. For code/config/resource scope, `$code-review` owns fresh review; otherwise `$artifact-review` owns fresh review with the supplied/inferred kind. If `auto` is not cheaply obvious from the named scope, use `other`; never guess a specialised lens. Never use the fixer as reviewer.
2. First cycle reviews the complete current state. After fixes, verify the prior receipt and review the fix delta, affected context/claims, and new/edited authoritative material. Reuse unchanged verified bytes, never old conclusions.
3. Run the selected lens with the verified packet; refresh only for domain-affecting deltas. Before `CLEAN`, require its `scope=final` review over the exact complete current code/artifact state, requirements, and authoritative context. Preserve child `P#`/`Q#`; prose-only artifacts never receive code/test lenses.
4. Resolve ambiguity from authoritative context. Render `P#` with evidence/fix/validation. Put unresolved decisions under `Please answer:` as direct `Q#` with context/options/recommendation; `Q#` stops mutation and same-session answers resume without `NEXT`.
5. Send findings to one `worker`, validate, checkpoint only as requested (`none` never commits), record fingerprint/delta, then fresh specialised review.
6. Stop `BLOCKED` on recurring unchanged findings, oscillation, reviewer conflict, unverifiable evidence, or non-convergence.

Do not stop at orientation or known remaining work. Return `CLEAN/BLOCKED | checkpoints/- | validation | review receipt | blocker/-`, plus findings/questions.
