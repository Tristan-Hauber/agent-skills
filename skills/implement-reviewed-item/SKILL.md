---
name: implement-reviewed-item
description: Implement one bounded item and produce a single reviewed, validated final commit.
---

The main thread owns orchestration, evidence state, and the sole final commit. Work only in the assigned workspace; inventory pre-existing dirt, never stage/overwrite it, and block on overlap; switch to its branch and verify attached `HEAD`. Treat the input as one semantic commit unit: if it contains multiple coherent commit units, stop for replanning rather than collapsing them to satisfy the one-commit contract. Exclude unrelated cleanup unless required/generated/inseparable.

1. Give one `worker` only the task, owned scope, dependency commits, acceptance checks, validation, workspace, and verified evidence packet. It expands context only when needed, implements fully, adds proportionate tests/docs, validates, and returns `READY` without committing.
2. Run `$adversarial-review-loop checkpoint=none` with that worker as fixer, the receipt, and fresh reviewers. Keep all work uncommitted; between cycles review fix deltas, then require a fresh final complete-state review. Findings discovered before commit are fixed within this item, never emitted as separate review-fix commits.
3. Resolve requirement questions from supplied issue/linked decisions/docs. If unresolved, stop without committing and preserve direct `Q#` under `Please answer:`; mention external recording only for a material undurable decision.
4. After final `CLEAN`, run required validation, record command/config/head receipts, then create exactly one focused commit. Verify commit and clean workspace; create no intermediate, recovery, or squash commits.
5. Stop `BLOCKED` on recurring findings, invalid evidence that cannot be refreshed, or unplanned dependencies; caller owns recovery.

Use an `explorer` only for a bounded lookup. Do not stop at orientation or known remaining work.

Return `ID | CLEAN/BLOCKED | commit SHA/- | validation | review receipt | blocker/-`, followed by exact questions.
