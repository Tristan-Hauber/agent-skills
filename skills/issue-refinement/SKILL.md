---
name: issue-refinement
description: Refine a rough issue into an implementation-ready specification without inventing scope.
---

Input: issue/draft plus `mode=propose|update` (`propose` default) and optional verified evidence/review receipt. Do not modify code, branches, worktrees, labels, priority, milestone, assignees, or project state.

1. Verify/reuse unchanged issue/comments, parent/linked items, docs/rules, current behaviour, tests, APIs/schemas, migrations, and terminology. Use at most one `explorer` for invalid/missing evidence.
2. Preserve intent and settled decisions. Resolve questions from context; distinguish product decisions from reversible implementation assumptions.
3. Draft only useful sections: problem, behaviour, scope, requirements, observable acceptance criteria, relevant edge/failure/compatibility/migration concerns, validation, docs, assumptions, and open questions; avoid boilerplate and implementation checklists.
4. Run `$issue-review` with the verified receipt; fix `P#` findings, preserve direct `Q#` under `Please answer:`, resume from answers, and on repeats retrieve only changed evidence before fresh reasoning. Continue until `CLEAN` or oscillation.
5. `propose`: retain the reviewed draft and accept revise/reject/recheck. `update`: require `CLEAN`, reconciled revision, and authority. Separate sourced requirements from stable `M#` changes and offer Approve/Revise/Reject/Recheck unless authorised. Update only the body, verify, refresh receipt, then delete the draft.

Return `REFINED/UPDATED/BLOCKED | target | draft/- | review receipt | approved M#/- | assumptions/- | ready=yes/no | blocker/-`, followed by exact questions.
