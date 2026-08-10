---
name: issue-decomposition
description: Split a large issue into reviewed, independently deliverable child drafts with complete coverage.
---

Input: parent issue/draft plus `mode=propose|create` (`propose` default) and optional verified issue-review receipt. Do not modify code, branches, worktrees, labels, priority, milestones, assignees, or project state.

1. Verify/reuse unchanged parent, comment, linked-source, docs/rules, and terminology evidence; use at most one `explorer` for invalid/missing material. Resolve decisions before asking.
2. Split only into independently deliverable outcomes; keep one issue when tightly coupled and never split merely by file, layer, or implementation step.
3. Define children, dependencies, shared constraints, and parent completion criteria. Map every parent requirement; detect gaps, overlap, and cycles.
4. Draft standalone children with observable acceptance criteria, scope, dependencies, validation, and parent linkage. Add no speculative or hidden parent-only scope.
5. Run `$issue-review` on each child and the coverage matrix, passing shared verified evidence instead of rereading it. Fix `P#`, preserve direct `Q#` under `Please answer:`, resume from answers, and stop on oscillation.
6. `propose`: retain drafts and accept revise/reject/recheck. `create`: require `CLEAN`, verify parent revision, and obtain authority; unless already authorised, offer natural Approve/Revise/Reject/Recheck choices. Use stable `C#` children and `M#` parent edits; allow partial approval only without coverage loss. Create approved children in dependency order, establish links/checklist fallback, reconcile parent, verify coverage, then delete drafts.

Return `PROPOSED/CREATED/NOT_NEEDED/BLOCKED | parent | children/drafts | approved C#/M#/- | dependencies | coverage | review receipt | blocker/-`, followed by exact questions.
