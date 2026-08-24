---
name: mistake-analysis
description: Surface regressions, process slips, and agent execution mistakes from git history and the shared workflow-improvement store; recommend only.
---

Two evidence sources, one shared pipeline — does not replace the workflow-improvement pipeline's observer/evaluator/recommender stages (outside this catalogue), feeds them.

1. `scripts/regression_scan.py <repo> <days>` — read-only: revert commits, hotfix-shortly-after-merge candidates (same file touched again within 72h of a merge), repeated-subject signals. For each candidate not already in the store (checked by fingerprint), write it with `${CODEX_HOME:-$HOME/.codex}/workflow-improvement/store.py add`, `source=tool`, using the same record shape as the observer. Never assign cause or a remedy at this stage.
2. Query the shared store: `store.py list --status pending --limit 100`, and separately `--status accepted`. Group by `event` and `context.harness` (codex/claude/unset) into a compact digest: category, count, oldest unresolved, most recent.
3. Emit the digest, then note that evaluating and recommending on the new pending records is the next step, via the workflow-improvement pipeline's evaluator and recommender stages outside this catalogue — do not evaluate or recommend here.

For agent-prompting mistakes (vague or ignored instructions, unsupported claims): only report what an observer already captured in the store for that session; do not investigate transcripts to find new instances.
